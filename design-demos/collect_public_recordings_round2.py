# -*- coding: utf-8 -*-
"""第二轮真实录音采集：把只读探针核验过的公开来源接入内部研究库。

与 collect_public_recordings.py（第一轮，16 个文件）分开执行，互不覆盖。
来源限定：
- 央视网「独立单曲页」：整期节目页含多个曲目，一律排除；
- 学习强国公开专辑页音频：通过动态接口取真实地址，带来源页上下文保存。

精确标注版本性质：《数鸭子》为童谣诵读、《一园青菜成了精》为童谣表演，
均不是「歌曲原唱」，不得写成目标作品原曲录音。

输出：追加记录到 audio/public-recording-collection.json（标记 round=2），
并更新 fileCount / workMappingCount。可重复运行，已存在的文件按 SHA-256 复用。
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from collect_public_recordings import (
    AUDIO_DIR,
    MANIFEST,
    POLICY_PAGE,
    download,
    extract_audio,
    file_metadata,
)

ROOT = Path(__file__).resolve().parent
CCTV_PROBE = ROOT / "probe-cctv-result.json"
XUEXI_PROBE = ROOT / "probe-xuexi-result.json"
STREAM_PROBE = ROOT / "probe-streams-result.json"

XUEXI_ALBUM_PAGE = "https://article.xuexi.cn/articles/audio/share/index.html?art_id=17735598666313749703&type=album"

VIDEO_METHOD = "从公开视频提取第一路原声音轨；去除视频流，音频直接封装为 M4A，未重新编码"
AUDIO_METHOD = "带来源页上下文保存公开专辑页内完整音频；本地未剪辑或转码"

# label 必须与 probe_cctv.py 的 PAGES 名称一致
CASES = [
    {
        "label": "卖报歌-大手牵小手", "ids": ["CN-C20"], "title": "卖报歌",
        "file": "CN-C20-cctv.m4a", "author": "总台央广少年广播70-80年代团员合唱团",
        "sourceTitle": "央视网《大手牵小手》：卖报歌",
        "kind": "公开视频原声音轨 · 童声合唱", "role": "primary",
    },
    {
        "label": "小毛驴-回声嘹亮", "ids": ["CN-N03"], "title": "小毛驴",
        "file": "CN-N03-cctv.m4a", "author": "老皮匠乐队",
        "sourceTitle": "央视网《回声嘹亮》：儿歌《小毛驴》",
        "kind": "公开视频原声音轨 · 乐队改编演唱", "role": "primary",
        "versionNote": "来源页为乐队改编演唱版本，不是传统儿歌的历史原版录音。",
    },
    {
        "label": "小小螺丝帽-宝贝亮相吧", "ids": ["CN-C21"], "title": "小小螺丝帽",
        "file": "CN-C21-cctv.m4a", "author": "鲁彦皓",
        "sourceTitle": "央视网《宝贝亮相吧》：歌曲《小小螺丝帽》",
        "kind": "公开视频原声音轨 · 少儿演唱", "role": "primary",
    },
    {
        "label": "外婆的澎湖湾-回声嘹亮", "ids": ["CN-C08"], "title": "外婆的澎湖湾",
        "file": "CN-C08-cctv-hsl.m4a", "author": "张楚怡",
        "sourceTitle": "央视网《回声嘹亮》：歌曲《外婆的澎湖湾》",
        "kind": "公开视频原声音轨 · 演唱版本", "role": "primary",
    },
    {
        "label": "外婆的澎湖湾-民歌中国", "ids": ["CN-C08"], "title": "外婆的澎湖湾",
        "file": "CN-C08-cctv-mgzg.m4a", "author": "任贤齐",
        "sourceTitle": "央视网《民歌·中国》：歌曲《外婆的澎湖湾》",
        "kind": "公开视频原声音轨 · 演唱版本", "role": "variant",
    },
    {
        "label": "虫儿飞-大手牵小手", "ids": ["CN-N05"], "title": "虫儿飞",
        "file": "CN-N05-cctv-dqsx.m4a", "author": "赵蕾",
        "sourceTitle": "央视网《大手牵小手》：歌曲《虫儿飞》",
        "kind": "公开视频原声音轨 · 少儿演唱", "role": "primary",
    },
    {
        "label": "虫儿飞-精彩音乐汇", "ids": ["CN-N05"], "title": "虫儿飞",
        "file": "CN-N05-cctv-jcyyh.m4a", "author": "麦麦",
        "sourceTitle": "央视网《精彩音乐汇》：歌曲《虫儿飞》",
        "kind": "公开视频原声音轨 · 演唱版本", "role": "variant",
    },
    {
        "label": "童年-快乐大巴", "ids": ["CN-N02"], "title": "童年",
        "file": "CN-N02-cctv-kldb.m4a", "author": "刘昱星",
        "sourceTitle": "央视网《快乐大巴》：歌曲《童年》",
        "kind": "公开视频原声音轨 · 少儿演唱", "role": "primary",
    },
    {
        "label": "童年-精彩音乐汇", "ids": ["CN-N02"], "title": "童年",
        "file": "CN-N02-cctv-jcyyh.m4a", "author": "周觅",
        "sourceTitle": "央视网《精彩音乐汇》：歌曲《童年》",
        "kind": "公开视频原声音轨 · 演唱版本", "role": "variant",
    },
    {
        "label": "一园青菜成了精-七巧板", "ids": ["CN-T12"], "title": "一园青菜成了精",
        "file": "CN-T12-cctv.m4a", "author": "刘瀚元家庭",
        "sourceTitle": "央视网《七巧板》：《一园青菜成了精》",
        "kind": "公开视频原声音轨 · 童谣表演与念诵", "role": "primary",
        "versionNote": "来源页是童谣表演 / 念诵，不是有固定曲谱的歌曲演唱录音；作为该童谣的真实口头演绎版本登记。",
    },
]

XUEQI_CASE = {
    "label": "学习强国 陪你读童谣(一) · 数鸭子", "ids": ["CN-N01"], "title": "数鸭子",
    "file": "CN-N01-xuexi.mp3", "author": "刘雪姣",
    "sourceTitle": "学习强国《陪你读童谣（一）》：数鸭子",
    "kind": "公开专辑音频 · 童谣诵读（非歌曲演唱）", "role": "primary",
    "versionNote": "来源专辑为「陪你读童谣」诵读系列，此音频是童谣念读，不是《数鸭子》歌曲演唱版本；不得标作原唱。",
}


def stream_url(label: str) -> str:
    """从只读探测结果里取已验证可解码的媒体地址，不在采集脚本里硬编码 URL。"""
    results = json.loads(STREAM_PROBE.read_text(encoding="utf-8"))
    for item in results:
        if item["label"] == label and item.get("ok"):
            return item["url"]
    raise ValueError(f"No verified stream for {label}")


def source_page(label: str) -> str:
    cctv = json.loads(CCTV_PROBE.read_text(encoding="utf-8"))
    if label in cctv:
        return cctv[label]["url"]
    return XUEXI_ALBUM_PAGE


def build_records():
    cases = CASES + [XUEQI_CASE]
    records = []
    for case in cases:
        output = AUDIO_DIR / case["file"]
        url = stream_url(case["label"])
        page = source_page(case["label"])
        if case["file"].endswith(".mp3"):
            download(url, output, XUEXI_ALBUM_PAGE)
            method = AUDIO_METHOD
        else:
            extract_audio(url, output, page)
            method = VIDEO_METHOD
        record = {
            "ids": case["ids"],
            "title": case["title"],
            "file": case["file"],
            "sourcePage": page,
            "mediaUrl": url,
            "author": case["author"],
            "sourceTitle": case["sourceTitle"],
            "kind": case["kind"],
            "collectionMethod": method,
            "role": case["role"],
            "round": 2,
            **file_metadata(output),
        }
        if case.get("versionNote"):
            record["versionNote"] = case["versionNote"]
        if case["label"] == XUEQI_CASE["label"]:
            record["sourceTrackId"] = "13891788958395814906"
        records.append(record)
        print("OK", case["file"], record["durationSeconds"], "s", record["bytes"], "bytes")
    return records


def main():
    AUDIO_DIR.mkdir(exist_ok=True)
    collection = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = [r for r in collection["records"] if r.get("round") != 2]
    for record in existing:
        record.setdefault("round", 1)
    fresh = build_records()
    records = existing + fresh
    collection["records"] = records
    collection["fileCount"] = len(records)
    collection["workMappingCount"] = sum(len(r["ids"]) for r in records)
    collection["collectedOn"] = date.today().isoformat()
    collection["rounds"] = [
        {"round": 1, "files": len(existing), "usage": "学习强国专辑、政府/高校公开音频、公开视频原声音轨"},
        {"round": 2, "files": len(fresh), "usage": "央视网独立单曲页 + 学习强国陪你读童谣专辑"},
    ]
    collection["licenseUrl"] = POLICY_PAGE
    MANIFEST.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "files": len(records),
        "mappings": collection["workMappingCount"],
        "round2Files": len(fresh),
        "round2Works": len({i for r in fresh for i in r["ids"]}),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
