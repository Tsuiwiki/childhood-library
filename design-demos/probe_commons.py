# -*- coding: utf-8 -*-
"""只读探针：为 world 47 首检索 Wikimedia Commons 开放许可音频候选。

只查询公开 API 与许可证元数据，不下载、不写采集清单。
结果写入 probe-commons-result.json，供人工核验后决定是否采集。

v2 修正：Wikimedia 的 OGG 音频 mime 是 application/ogg（不是 audio/ogg），
旧版按 mime.startswith("audio/") 过滤会把全部有效候选误删；
改为按扩展名判定音频，并并发检索以缩短耗时。

v3 修正：本机共享出口 IP 被 Wikimedia 限流（api.php 返回 403 Too Many Reqs，
upload.wikimedia.org 返回 429），旧版 api() 会静默吞掉异常并返回 {}，
导致「0 / 47」被误读成「没有开放许可音频」。现在先做一次可达性探测，
被限流时写明原因与已核验线索，不再输出误导性的 0 结果。
"""
from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probe-commons-result.json"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "ChildhoodLibraryResearch/0.1 (local prototype; non-commercial)"}

AUDIO_EXT = {".ogg", ".oga", ".mp3", ".wav", ".flac", ".m4a", ".opus", ".webm"}
ALLOWED_LICENSE = ("public domain", "pd-", "cc0", "cc by", "cc-by", "cc by-sa", "cc-by-sa")


def target_works():
    spec = json.loads((ROOT / "specialties.json").read_text(encoding="utf-8"))
    samples = json.loads((ROOT / "audio" / "samples.json").read_text(encoding="utf-8"))
    have = {s["id"] for s in samples}
    return [w for w in spec["works"] if w["id"] not in have]


def strip_html(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", str(value)))).strip()


def api(params, retries=2):
    for attempt in range(retries + 1):
        try:
            response = requests.get(API, params={**params, "format": "json"}, headers=HEADERS, timeout=40)
            response.raise_for_status()
            return response.json()
        except Exception:
            if attempt == retries:
                return {}
            time.sleep(1.0)
    return {}


def search_files(title):
    plain = re.sub(r"['’()（）]", " ", title).strip()
    queries = [f"{plain} audio", f'intitle:"{title}"']
    names = []
    for query in queries:
        data = api({
            "action": "query", "list": "search", "srsearch": query,
            "srnamespace": 6, "srlimit": 20,
        })
        names.extend(item["title"] for item in data.get("query", {}).get("search", []))
    return sorted({n for n in names if Path(n).suffix.lower() in AUDIO_EXT})[:24]


def imageinfo_batch(chunk):
    data = api({
        "action": "query", "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime|mediatype",
        "titles": "|".join(chunk),
    })
    rows = {}
    for page in data.get("query", {}).get("pages", {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        if not info:
            continue
        meta = info.get("extmetadata") or {}

        def field(key):
            return strip_html((meta.get(key) or {}).get("value"))

        license_name = field("LicenseShortName")
        rows[page["title"]] = {
            "file": page["title"],
            "mime": info.get("mime", ""),
            "bytes": info.get("size", 0),
            "url": re.sub(r"\?utm_.*$", "", info.get("url", "")),
            "descriptionUrl": info.get("descriptionurl", ""),
            "license": license_name,
            "licenseUrl": (meta.get("LicenseUrl") or {}).get("value", ""),
            "usageTerms": field("UsageTerms"),
            "artist": field("Artist") or field("Credit"),
            "description": field("ImageDescription")[:300],
            "date": field("DateTimeOriginal"),
            "allowed": any(token in license_name.lower() for token in ALLOWED_LICENSE),
            "audioExt": Path(page["title"]).suffix.lower() in AUDIO_EXT,
        }
    return rows


def imageinfo(titles):
    result = {}
    chunks = [titles[i:i + 20] for i in range(0, len(titles), 20)]
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(imageinfo_batch, chunk) for chunk in chunks]
        for future in as_completed(futures):
            result.update(future.result())
    return result


def probe_reachability():
    """单次请求判断 Commons API 是否可达；返回 (ok, status_code, detail)。"""
    params = {
        "action": "query", "list": "search", "srsearch": "Baa, Baa, Black Sheep",
        "srnamespace": 6, "srlimit": 1, "format": "json",
    }
    try:
        response = requests.get(API, params=params, headers=HEADERS, timeout=25)
    except Exception as exc:
        return False, 0, f"请求异常：{type(exc).__name__}: {str(exc)[:160]}"
    if response.status_code != 200:
        return False, response.status_code, (
            f"HTTP {response.status_code}；"
            "Wikimedia 边缘缓存对共享出口 IP 限流（403 Too Many Reqs / 429）。"
        )
    try:
        response.json()
    except Exception:
        return False, response.status_code, "HTTP 200 但响应不是 JSON"
    return True, 200, "Commons API 可达"


def blocked_result(status_code, detail, works):
    clues_path = ROOT / "world-audio-clues.json"
    clues = json.loads(clues_path.read_text(encoding="utf-8")) if clues_path.exists() else {}
    return {
        "status": "blocked_by_wikimedia_rate_limit",
        "api": API,
        "httpStatus": status_code,
        "detail": detail,
        "note": (
            "0 候选不等于 Commons 没有开放许可音频。本轮通过 WebFetch 通道核验到的候选"
            "见 verifiedCandidates；它们多为器乐片段、MIDI、同名异曲或现代专辑录音，"
            "且本地无法下载二进制媒体，因此 47 首一律标「音频待采集」。"
        ),
        "worksChecked": len(works),
        "worksWithUsableAudio": None,
        "verifiedCandidates": clues.get("verifiedCandidates", []),
        "checkedOn": "2026-11-18",
    }


def main():
    works = target_works()
    reachable, status_code, detail = probe_reachability()
    if not reachable:
        OUT.write_text(
            json.dumps(blocked_result(status_code, detail, works), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"BLOCKED Commons API: {detail}")
        print("saved", OUT.name, "status=blocked_by_wikimedia_rate_limit, works=", len(works))
        return
    found = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(search_files, w["title"]): w for w in works}
        for future in as_completed(futures):
            work = futures[future]
            try:
                found[work["id"]] = future.result()
            except Exception as exc:
                found[work["id"]] = []
                print("SEARCH_ERROR", work["id"], str(exc)[:100])
    all_files = sorted({name for names in found.values() for name in names})
    print("candidate files:", len(all_files))
    infos = imageinfo(all_files)
    output = {}
    for index, work in enumerate(works, 1):
        records = [infos[name] for name in found[work["id"]] if name in infos and infos[name]["audioExt"]]
        records.sort(key=lambda r: (not r["allowed"], -r["bytes"]))
        usable = [r["file"] for r in records if r["allowed"]][:4]
        output[work["id"]] = {
            "id": work["id"], "title": work["title"], "type": work.get("type", ""),
            "candidates": records[:8], "usable": usable,
        }
        print(f"{index:2}/{len(works)} {work['id']} {work['title'][:34]:34} audio={len(records)} usable={len(usable)}")
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("saved", OUT.name, "works with usable audio =",
          sum(1 for v in output.values() if v["usable"]), "/", len(output))


if __name__ == "__main__":
    main()
