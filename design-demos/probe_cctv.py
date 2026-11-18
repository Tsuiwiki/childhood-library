# -*- coding: utf-8 -*-
"""只读探针：打开央视网公开单曲视频页，抓 HLS guid 并推导可提取音轨的 main.m3u8。

只接受「独立单曲页」：整期节目页含多个曲目，不能直接当作某一首作品的原声。
输出 probe-cctv-result.json 供人工核验与后续采集；不下载、不剪辑。
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probe-cctv-result.json"

# (作品 ID, 页面标识, 公开单曲页 URL)
PAGES = [
    ("CN-C20", "卖报歌-大手牵小手", "https://tv.cctv.com/v/v1/VIDExSfFIKK3Fmoyx84K4FHl220606.html"),
    ("CN-N03", "小毛驴-回声嘹亮", "https://tv.cntv.cn/video/C11356/f110df6245dc4bcca52c1205cd76c5a0"),
    ("CN-C21", "小小螺丝帽-宝贝亮相吧", "https://tv.cctv.com/v/v2/VIDEreA9pWmeIZ7Ehlx9Fa64210314.html"),
    ("CN-C08", "外婆的澎湖湾-回声嘹亮", "https://tv.cctv.com/2014/06/28/VIDE1403959879035109.shtml"),
    ("CN-C08", "外婆的澎湖湾-民歌中国", "https://tv.cctv.com/2018/11/28/VIDEleQytPNFhXoSzx7F1Ahl181128.shtml"),
    ("CN-N05", "虫儿飞-大手牵小手", "https://tv.cctv.cn/2019/10/16/VIDExGznIy4bpUu1j8wsX4pD191016.shtml"),
    ("CN-N05", "虫儿飞-精彩音乐汇", "https://tv.cctv.com/2019/03/18/VIDEBTQh3QtxHe0f4lUqVjBu190318.shtml"),
    ("CN-N02", "童年-快乐大巴", "https://tv.cctv.cn/2018/09/22/VIDEgSZ1eNOUpujo720kdGFe180922.shtml"),
    ("CN-N02", "童年-精彩音乐汇", "https://tv.cctv.com/2023/07/19/VIDE4nJ9pjWogBYb7od9Ghd2230719.shtml"),
    ("CN-T12", "一园青菜成了精-七巧板", "https://tv.cctv.com/v/v1/VIDEEUPGaW9KNkr8KvsAZNBn210626.html"),
]

HLS_RE = re.compile(
    r"https?://([^/]+)/asp/h5e/hls/(?:main|\d+)/0303000a/3/default/([0-9a-f]{32})/"
)
GUID_RE = re.compile(r"[0-9a-f]{32}")
CONTENT_ID = "15120519184043"


def main():
    result = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for work_id, name, url in PAGES:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            media = set()

            def on_request(req):
                u = req.url
                if ".m3u8" in u or ".mp4" in u:
                    media.add(u)

            page.on("request", on_request)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4500)
            except Exception as exc:
                print(name, "LOAD_ERROR", str(exc)[:120])
            try:
                page_title = page.title()
                body = page.content()
            except Exception:
                page_title, body = "", ""
            hosts = {}
            for media_url in media:
                match = HLS_RE.search(media_url)
                if match:
                    host, guid = match.group(1), match.group(2)
                    hosts.setdefault((host, guid), set()).add(media_url)
            streams = []
            for (host, guid), urls in hosts.items():
                streams.append({
                    "host": host,
                    "guid": guid,
                    "mainUrl": (
                        f"https://{host}/asp/h5e/hls/main/0303000a/3/default/"
                        f"{guid}/main.m3u8?maxbr=2048&contentid={CONTENT_ID}"
                    ),
                    "observedUrls": sorted(urls)[:5],
                })
            # 备用：页面里单独出现的 guid，但没有完整 HLS 路径
            loose_guids = sorted(set(GUID_RE.findall(body)))
            result[name] = {
                "workId": work_id,
                "url": url,
                "host": urlparse(url).netloc,
                "title": page_title,
                "streams": streams,
                "looseGuids": [g for g in loose_guids if g not in {s["guid"] for s in streams}][:10],
                "mediaCount": len(media),
            }
            print(work_id, name, "streams=", len(streams), "media=", len(media))
            page.close()
        browser.close()
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("saved", OUT.name)


if __name__ == "__main__":
    main()
