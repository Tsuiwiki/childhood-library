import base64
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import av
import imageio_ffmpeg
import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"
MANIFEST = AUDIO_DIR / "public-recording-collection.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ALBUM_PAGE = "https://article.xuexi.cn/articles/audio/share/index.html?art_id=7617192199319184014&type=album"
POLICY_PAGE = "../docs/COPYRIGHT_POLICY.md"

ALBUM_TRACKS = {
    "小燕子": ("CN-C03-xuexi-chorus.mp3", ["CN-C03"]),
    "丢手绢": ("CN-C14-xuexi.mp3", ["CN-C14"]),
    "拔萝卜": ("CN-C13-xuexi.mp3", ["CN-C13"]),
    "一分钱": ("CN-C06-xuexi.mp3", ["CN-C06"]),
    "读书郎": ("CN-C07-xuexi.mp3", ["CN-C07"]),
    "找朋友": ("CN-C19-xuexi.mp3", ["CN-C19"]),
    "小鸭子": ("CN-C15-xuexi.mp3", ["CN-C15"]),
    "娃哈哈": ("CN-C17-xuexi.mp3", ["CN-C17"]),
    "嘀哩，嘀哩": ("CN-C04-CN-C16-xuexi.mp3", ["CN-C04", "CN-C16"]),
}

VIDEO_SOURCES = [
    {
        "ids": ["CN-C02"],
        "title": "我们的田野",
        "file": "CN-C02-xuexi-chorus.m4a",
        "sourcePage": "https://article.xuexi.cn/articles/index.html?art_id=571012350271693813",
        "mediaUrl": "https://boot-video.xuexi.cn/video/1004/p/1a8e8a60e593fbc8f08517d335ef834e-c5cea7f043e34956a5ed063c23b25bd5-3.mp4",
        "author": "上海菁英少年合唱团",
        "sourceTitle": "学习强国《每日一曲｜我们的田野》",
        "kind": "公开视频原声音轨 · 童声合唱",
    },
    {
        "ids": ["CN-C12"],
        "title": "快乐的节日",
        "file": "CN-C12-xuexi-galaxy.m4a",
        "sourcePage": "https://article.xuexi.cn/articles/index.html?art_id=10967841520155694097",
        "mediaUrl": "https://boot-video.xuexi.cn/video/1004/p/479e9788d5365320fd0d539f711a81cd-589b181c38c54c99a2705cc749fee22d-1.mp4",
        "author": "中央电视台银河少年电视艺术团等",
        "sourceTitle": "学习强国《每日一曲｜快乐的节日》",
        "kind": "公开视频原声音轨 · 童声合唱",
    },
    {
        "ids": ["CN-C11"],
        "title": "听妈妈讲那过去的事情",
        "file": "CN-C11-xuexi.m4a",
        "sourcePage": "https://article.xuexi.cn/articles/index.html?art_id=12345317585299113386",
        "mediaUrl": "https://boot-video.xuexi.cn/video/1005/p/5264b1f7e135fa5df52577d1910b4829-da3d4ba314d2412d83a2d6d877bc4d87-2.mp4",
        "author": "学习强国来源页所列演出版本",
        "sourceTitle": "学习强国《每日一曲｜听妈妈讲那过去的事情》",
        "kind": "公开视频原声音轨",
    },
    {
        "ids": ["CN-C18"],
        "title": "我爱北京天安门",
        "file": "CN-C18-hbwy.m4a",
        "sourcePage": "https://hbwy.org.cn/c/2021/10/20/45911.shtml",
        "mediaUrl": "https://hbwy.org.cn/upload/resources/video/2023/12/25/55336.mp4",
        "author": "北京铁路职工子弟第五小学等八校学生",
        "sourceTitle": "湖北文艺网《我爱北京天安门》",
        "kind": "公开视频原声音轨 · 历史童声合唱",
    },
    {
        "ids": ["CN-C05"],
        "title": "采蘑菇的小姑娘",
        "file": "CN-C05-cctv.m4a",
        "sourcePage": "https://tv.cctv.com/2020/01/28/VIDEk2uuabNzEz4nRD1FVL4m200128.shtml",
        "mediaUrl": "https://dh5wswx02.v.cntv.cn/asp/h5e/hls/main/0303000a/3/default/1d6db5e85f8842a4b184f5d9a1cdbb78/main.m3u8?maxbr=2048&contentid=15120519184043",
        "author": "唐蜜、王宸汐",
        "sourceTitle": "央视网《童声唱》：采蘑菇的小姑娘",
        "kind": "公开视频原声音轨 · 童声表演",
    },
    {
        "ids": ["CN-C09"],
        "title": "小螺号",
        "file": "CN-C09-cctv.m4a",
        "sourcePage": "https://tv.cctv.com/2022/08/26/VIDEHuad5HoEUXAvWoSD0IDD220826.shtml",
        "mediaUrl": "https://dh5wswx02.v.cntv.cn/asp/h5e/hls/main/0303000a/3/default/cd2e7c8287144e868e5ff4d2bfda740b/main.m3u8?maxbr=2048&contentid=15120519184043",
        "author": "张伊蔓",
        "sourceTitle": "央视网《童声唱》：小螺号",
        "kind": "公开视频原声音轨 · 童声独唱",
    },
]


def decode_response_data(payload):
    response = payload.get("response", payload)
    return json.loads(base64.b64decode(response["data"]))


def probe(path):
    with av.open(str(path)) as container:
        audio_streams = [stream for stream in container.streams if stream.type == "audio"]
        if not audio_streams:
            raise ValueError(f"No audio stream: {path}")
        duration = float(container.duration / av.time_base) if container.duration else 0
        if duration <= 1:
            raise ValueError(f"Invalid decoded duration: {path}: {duration}")
        stream = audio_streams[0]
        return {
            "durationSeconds": round(duration, 3),
            "codec": stream.codec_context.name,
            "sampleRate": stream.codec_context.sample_rate,
            "channels": stream.codec_context.channels,
        }


def file_metadata(path):
    payload = path.read_bytes()
    return {
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        **probe(path),
    }


def download(url, output, referer):
    if output.exists():
        file_metadata(output)
        print(f"EXISTS {output.name}")
        return
    partial = output.with_suffix(output.suffix + ".part")
    headers = {"User-Agent": USER_AGENT, "Referer": referer}
    with requests.get(url, headers=headers, stream=True, timeout=120) as response:
        response.raise_for_status()
        with partial.open("wb") as handle:
            for chunk in response.iter_content(1024 * 256):
                if chunk:
                    handle.write(chunk)
    file_metadata(partial)
    partial.replace(output)
    print(f"SAVED {output.name}")


def extract_audio(url, output, referer):
    if output.exists():
        file_metadata(output)
        print(f"EXISTS {output.name}")
        return
    partial = output.with_name(output.stem + ".part" + output.suffix)
    headers = f"Referer: {referer}\r\nUser-Agent: {USER_AGENT}\r\n"
    command = [
        FFMPEG, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-headers", headers, "-i", url, "-map", "0:a:0", "-vn",
        "-c:a", "copy", "-movflags", "+faststart", "-f", "ipod", str(partial),
    ]
    try:
        subprocess.run(command, check=True, timeout=300)
        file_metadata(partial)
        partial.replace(output)
    finally:
        if partial.exists():
            partial.unlink()
    print(f"EXTRACTED {output.name}")


def collect_album():
    records = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            with page.expect_response(lambda response: "getSubsetsMain" in response.url, timeout=90000) as info:
                page.goto(ALBUM_PAGE, wait_until="domcontentloaded", timeout=90000)
            data = decode_response_data(info.value.json())
            cards = data["data"]["sub_cards"]
            by_title = {card["title"]: card for card in cards}
            missing = set(ALBUM_TRACKS) - set(by_title)
            if missing:
                raise ValueError(f"Album tracks missing: {sorted(missing)}")
            for title, (filename, ids) in ALBUM_TRACKS.items():
                card = by_title[title]
                audio = card["audios"][0]
                storage = next(item for item in audio["audio_storage_infos"] if item["bitrate"] == 192)
                output = AUDIO_DIR / filename
                download(storage["url"], output, ALBUM_PAGE)
                records.append({
                    "ids": ids,
                    "title": title,
                    "file": filename,
                    "sourcePage": ALBUM_PAGE,
                    "mediaUrl": storage["url"],
                    "author": card.get("performers") or "中国唱片集团有限公司来源版本",
                    "sourceTitle": "学习强国《中华儿歌珍藏集（一）》",
                    "kind": "专辑完整录音 · 192 kbps MP3",
                    "collectionMethod": "带来源页上下文保存公开页面内完整录音；本地未剪辑或转码",
                    "sourceTrackId": card["id"],
                    **file_metadata(output),
                })
        finally:
            browser.close()
    return records


def main():
    AUDIO_DIR.mkdir(exist_ok=True)
    records = collect_album()
    guangxi_page = "https://gdb.gxzf.gov.cn/ztjj_46964/lsztgd_46974/2021_99999/dsxxjy_97384/hsgqdjc_36974/t8911623.shtml"
    guangxi_url = urljoin(guangxi_page, "./W020210519351515425016.mp3")
    guangxi_output = AUDIO_DIR / "CN-C02-gxzf.flac"
    download(guangxi_url, guangxi_output, guangxi_page)
    records.append({
        "ids": ["CN-C02"],
        "title": "我们的田野",
        "file": guangxi_output.name,
        "sourcePage": guangxi_page,
        "mediaUrl": guangxi_url,
        "author": "中央乐团合唱团",
        "sourceTitle": "广西壮族自治区国防动员办公室《我们的田野》",
        "kind": "公开页面独立完整音频",
        "collectionMethod": "保存来源页公开音频；来源扩展名为 MP3，实际编码按探测结果记录；本地未剪辑或转码",
        **file_metadata(guangxi_output),
    })
    for source in VIDEO_SOURCES:
        output = AUDIO_DIR / source["file"]
        extract_audio(source["mediaUrl"], output, source["sourcePage"])
        records.append({
            **{key: value for key, value in source.items() if key != "mediaUrl"},
            "mediaUrl": source["mediaUrl"],
            "collectionMethod": "从公开视频提取第一路原声音轨；去除视频流，音频直接封装为 M4A，未重新编码",
            **file_metadata(output),
        })
    payload = {
        "collectedOn": date.today().isoformat(),
        "usage": "内部研究与原型播放；公开再发布权利待核验",
        "licenseUrl": POLICY_PAGE,
        "fileCount": len(records),
        "workMappingCount": sum(len(record["ids"]) for record in records),
        "records": records,
    }
    if len(records) != 16 or payload["workMappingCount"] != 17:
        raise ValueError("Expected 16 media files and 17 work mappings")
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": str(MANIFEST),
        "files": len(records),
        "mappings": payload["workMappingCount"],
        "durations": {record["file"]: record["durationSeconds"] for record in records},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
