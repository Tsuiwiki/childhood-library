# -*- coding: utf-8 -*-
"""只读探测：验证候选媒体地址确实可解码且含音频流，不保存任何媒体文件。

输入：probe-cctv-result.json（央视单曲页推导的 HLS）+ probe-xuexi-result.json（专辑音频）
输出：probe-streams-result.json，供采集脚本筛掉不可用地址。
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probe-streams-result.json"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

CCTV = json.loads((ROOT / "probe-cctv-result.json").read_text(encoding="utf-8"))
XUEXI = json.loads((ROOT / "probe-xuexi-result.json").read_text(encoding="utf-8"))

TARGETS = []


def add(work_id, label, url, source_page, referer=None):
    TARGETS.append({
        "workId": work_id,
        "label": label,
        "url": url,
        "sourcePage": source_page,
        "referer": referer or source_page,
    })


for name, page in CCTV.items():
    for stream in page.get("streams", []):
        add(page["workId"], name, stream["mainUrl"], page["url"])

for album, payload in XUEXI.items():
    for hit in payload.get("targetHits", []):
        for choice in hit.get("audioChoices", []):
            ids = {
                "数鸭子": "CN-N01",
                "小蜜蜂": "CN-T06",
            }
            if hit["title"] in ids:
                add(ids[hit["title"]], f"学习强国 {album} · {hit['title']}",
                    choice["url"], payload["url"])


def probe(target):
    headers = f"Referer: {target['referer']}\r\nUser-Agent: Mozilla/5.0\r\n"
    command = [
        FFMPEG, "-hide_banner", "-nostdin",
        "-headers", headers,
        "-i", target["url"],
        "-t", "2", "-f", "null", "-",
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=90,
            encoding="utf-8", errors="replace",
        )
        text = (completed.stderr or "") + (completed.stdout or "")
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": "timeout"}
    audio = re.findall(r"Audio:\s*([^\n]+)", text)
    duration = re.findall(r"Duration:\s*([^,]+)", text)
    ok = bool(audio) and "Invalid" not in text and not re.search(r"Failed to|Error opening|403 Forbidden|404 Not Found", text)
    return {
        "ok": ok,
        "audio": audio[:2],
        "duration": duration[:1],
        "reason": "" if ok else text.strip()[-300:],
    }


def main():
    results = []
    for target in TARGETS:
        info = probe(target)
        results.append({**target, **info})
        print(("OK  " if info["ok"] else "FAIL"), target["workId"], target["label"],
              (info.get("audio") or [""])[0][:70])
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("saved", OUT.name, "ok=", sum(1 for r in results if r["ok"]), "/", len(results))


if __name__ == "__main__":
    main()
