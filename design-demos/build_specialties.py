# -*- coding: utf-8 -*-
"""按规划 §2.1 八个专题，对 105 首发现目录做策展归类，生成专题候选清单 JSON。"""
import json
import re
from pathlib import Path

import build_works

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT.parent / "docs" / "CLASSIC_SONGS_CATALOG.md"
OUT = ROOT / "specialties.json"

SECTIONS = {
    "3": ("CN", "中国传统童谣与民间歌谣", "中国"),
    "4": ("CN", "中国经典创作儿歌", "中国"),
    "5": ("EN", "英语传统童谣与民间歌曲", "英语地区"),
    "6": ("EN", "英语摇篮曲与多元文化曲目", "多地区"),
}

SPECIALTIES = {
    "childhood": "童年的歌",
    "nature": "大自然的歌",
    "play": "游戏与伙伴",
    "lullaby": "月亮与摇篮曲",
    "classical": "古典音乐的童年",
    "world": "世界的童谣",
    "forgotten": "被遗忘的童谣",
    "original": "新芽原创",
}


def clean(v):
    return re.sub(r"\s+", " ", v.replace("<br>", " ")).strip()


def classify(work_id, work_type, note, section_num):
    text = f"{work_type} {note}"
    tags = set()
    # 摇篮曲
    if any(k in text for k in ["摇篮", "安睡", "安抚", "Lullaby", "lullaby", "Pretty Little Horses"]):
        tags.add("lullaby")
    # 古典
    if any(k in text for k in ["古典", "Brahms", "Shaker", "Golden Slumbers", "Lavender"]):
        tags.add("classical")
    # 游戏与伙伴（游戏/数数/问答/拍手等，去掉泛化的"歌"字）
    if any(k in text for k in ["游戏", "拍手", "数数", "问答", "轮唱", "绕口令", "互动", "动作", "手指", "叠句", "节奏"]):
        tags.add("play")
    # 自然
    if any(k in text for k in ["自然", "动物", "植物", "田园", "海洋", "春天", "季节", "草原", "风雨", "花草", "虫", "鸟", "鱼"]):
        tags.add("nature")
    # 被遗忘的童谣（地方方言、口传、历史采录）
    if any(k in text for k in ["北京童谣", "绍兴童谣", "闽南", "地方", "历史童谣", "口传", "民间童谣", "方言", "异文", "采录"]):
        tags.add("forgotten")
    # 世界的童谣（多语言、民族）
    if section_num in ("5", "6"):
        tags.add("world")
    if any(k in text for k in ["西语", "加勒比", "希腊", "威尔士", "Seminole", "非裔", "波多黎各", "民族"]):
        tags.add("world")
    # 童年的歌（中国创作儿歌）
    if section_num == "4":
        tags.add("childhood")
    # 若没有任何专题命中，归入 childhood 或 world 兜底
    if not tags:
        tags.add("childhood" if section_num in ("3", "4") else "world")
    return sorted(tags)


def main():
    entries = {}
    for work in build_works.parse_catalog():
        section_num = "5" if work["group"] == "english" else ("3" if "传统" in work["groupName"] else "4")
        tags = classify(work["id"], work["type"], work["note"], section_num)
        entries[work["id"]] = {
            "id": work["id"],
            "title": work["title"],
            "type": work["type"],
            "note": work["note"],
            "region": work["region"],
            "specialties": tags,
        }
    result = {"specialties": SPECIALTIES, "works": list(entries.values())}
    stats = {k: 0 for k in SPECIALTIES}
    for work in entries.values():
        for tag in work["specialties"]:
            if tag in stats:
                stats[tag] += 1
    result["stats"] = stats
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"total": len(entries), "stats": stats}, ensure_ascii=False))


if __name__ == "__main__":
    main()
