# -*- coding: utf-8 -*-
"""只读探针：抓取学习强国公开专辑页的动态接口，输出曲目与全部可用音频地址。

v2 修正：不同专辑的音频档位并不都是 192 kbps（「陪你读童谣」只有 64 kbps 单档），
旧版写死 192 会把有效音频误报为空。这里保留 audio_storage_infos 全档位，并把
原始 audios 结构一并输出，便于人工核验后再决定是否采集。

不下载、不剪辑、不写采集清单；结果写入 probe-xuexi-result.json。
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probe-xuexi-result.json"

ALBUMS = [
    ("中华儿歌珍藏集(一)", "https://article.xuexi.cn/articles/audio/share/index.html?art_id=7617192199319184014&type=album"),
    ("陪你读童谣(一)", "https://article.xuexi.cn/articles/audio/share/index.html?art_id=17735598666313749703&type=album"),
]

TARGET_TITLES = {
    "数鸭子", "小蜜蜂", "卖报歌", "种瓜", "小小螺丝帽", "在老师身边",
    "我们在大地上栽种鲜花", "外婆的澎湖湾", "虫儿飞", "一园青菜成了精",
    "月亮走我也走", "摇篮曲", "小毛驴", "童年",
}


def decode(payload):
    response = payload.get("response", payload)
    return json.loads(base64.b64decode(response["data"]))


def cards_of(data):
    """从接口响应里找出曲目卡片，兼容多层嵌套。"""
    found = []

    def walk(node, depth=0):
        if depth > 8:
            return
        if isinstance(node, dict):
            if "audios" in node or "audio_storage_infos" in node or "article_title" in node:
                found.append(node)
            for value in node.values():
                walk(value, depth + 1)
        elif isinstance(node, list):
            for value in node:
                walk(value, depth + 1)

    walk(data)
    seen = set()
    result = []
    for card in found:
        key = card.get("id") or card.get("article_title") or json.dumps(card, ensure_ascii=False)[:80]
        if key in seen:
            continue
        seen.add(key)
        result.append(card)
    return result


def audio_choices(card):
    """列出一张卡片里所有可用的音频档位（含未标 bitrate 的情况）。"""
    choices = []
    for audio in card.get("audios") or []:
        for item in audio.get("audio_storage_infos") or []:
            if item.get("url"):
                choices.append({
                    "bitrate": item.get("bitrate"),
                    "url": item["url"],
                    "format": item.get("format") or item.get("file_type") or "",
                    "bytes": item.get("size") or item.get("file_size") or "",
                })
    return choices


def main():
    output = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, url in ALBUMS:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            captured = []

            def on_response(resp):
                if any(k in resp.url for k in ("getSubsetsMain", "getArticleMain", "getAlbum", "getAudio")):
                    try:
                        captured.append((resp.url, resp.json()))
                    except Exception:
                        pass

            page.on("response", on_response)
            try:
                page.goto(url, wait_until="load", timeout=60000)
                page.wait_for_timeout(4000)
            except Exception as exc:
                print(name, "LOAD_ERROR", str(exc)[:160])
            entries = []
            related_ids = set()
            api_keys = []
            for api_url, payload in captured:
                try:
                    data = decode(payload)
                except Exception:
                    continue
                raw = json.dumps(data, ensure_ascii=False)
                related_ids.update(re.findall(r"(?<!\d)\d{16,20}(?!\d)", raw))
                api_keys.append({
                    "api": api_url.split("?")[0].rsplit("/", 1)[-1],
                    "topKeys": sorted(data.keys())[:20] if isinstance(data, dict) else [],
                })
                cards = (data.get("data") or {}).get("sub_cards") or []
                if not cards:
                    cards = cards_of(data)
                for card in cards:
                    choices = audio_choices(card)
                    entries.append({
                        "api": api_url.split("?")[0].rsplit("/", 1)[-1],
                        "id": card.get("id") or card.get("item_id") or "",
                        "title": card.get("article_title") or card.get("title") or "",
                        "performers": card.get("performers") or "",
                        "desc": str(card.get("desc") or "")[:160],
                        "duration": card.get("play_length") or "",
                        "audioChoices": choices,
                        "audiosRaw": card.get("audios") or [],
                    })
            # 去重（同一个 card 可能被多个接口重复吐出）
            unique = {}
            for entry in entries:
                key = entry["id"] or entry["title"]
                if key not in unique or len(entry["audioChoices"]) > len(unique[key]["audioChoices"]):
                    unique[key] = entry
            entries = list(unique.values())
            series = []
            for href in page.eval_on_selector_all("a", "els => els.map(e => e.href)"):
                if "article.xuexi.cn" in href and ("album" in href or "art_id" in href):
                    series.append(href)
            output[name] = {
                "url": url,
                "pageTitle": page.title(),
                "apiResponses": len(captured),
                "apiKeys": api_keys,
                "entries": entries,
                "relatedArtIds": sorted(related_ids),
                "seriesLinks": sorted(set(series))[:30],
                "targetHits": [
                    {"title": e["title"], "id": e["id"], "audioChoices": e["audioChoices"]}
                    for e in entries if e["title"] in TARGET_TITLES
                ],
            }
            found = sum(1 for e in entries if e["audioChoices"])
            print(name, "entries=", len(entries), "withAudio=", found,
                  "apis=", len(captured), "targets=", len(output[name]["targetHits"]))
            page.close()
        browser.close()
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("saved", OUT.name)


if __name__ == "__main__":
    main()
