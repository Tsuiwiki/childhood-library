# -*- coding: utf-8 -*-
"""从模板 + specialties.json 生成八个专题独立页。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "specialty-template.html"
DATA = ROOT / "specialties.json"

# 规划 §2.1 八专题的定义
SPEC_DEFS = {
    "childhood": {
        "no": "01", "name": "童年的歌", "key": "童年的歌",
        "desc": "中国经典儿童歌曲、校园歌曲与童年记忆，是几代人共同的听觉底色。这里收录旋律舒展、歌词有画面的创作儿歌与校园歌。",
        "scope": "中国经典儿童歌曲、校园歌曲、童年记忆",
        "focus": "区分儿童歌曲、校园歌曲与成人怀旧作品",
        "accent": "#e64a38",
    },
    "nature": {
        "no": "02", "name": "大自然的歌", "key": "大自然的歌",
        "desc": "春夏秋冬、花草树木、鸟兽虫鱼与河流海洋。自然观察与画面感，是这类作品最珍贵的部分。",
        "scope": "春夏秋冬、花草树木、鸟兽、河流海洋",
        "focus": "自然观察、画面感与旋律舒展度",
        "accent": "#739348",
    },
    "play": {
        "no": "03", "name": "游戏与伙伴", "key": "游戏与伙伴",
        "desc": "游戏歌、拍手歌、数数歌、问答歌。在语言与身体的互动里，藏着最自然的童趣。",
        "scope": "游戏歌、拍手歌、数数歌、问答歌",
        "focus": "互动性、语言趣味与传统玩法",
        "accent": "#f1bd32",
    },
    "lullaby": {
        "no": "04", "name": "月亮与摇篮曲", "key": "月亮与摇篮曲",
        "desc": "中国及世界各地的摇篮曲与安睡音乐。温柔、克制，适合陪伴，不承诺任何助眠效果。",
        "scope": "中国及世界各地摇篮曲、安睡音乐",
        "focus": "温柔、克制、适合陪伴，不承诺助眠效果",
        "accent": "#2858b8",
    },
    "classical": {
        "no": "05", "name": "古典音乐的童年", "key": "古典音乐的童年",
        "desc": "儿童古典作品、适龄器乐小品与音乐故事。引导聆听，而非把作品简化成训练工具。",
        "scope": "儿童古典作品、适龄器乐小品、音乐故事",
        "focus": "引导聆听，不把作品简化成训练工具",
        "accent": "#8b5e3c",
    },
    "world": {
        "no": "06", "name": "世界的童谣", "key": "世界的童谣",
        "desc": "多语言童谣、地方儿童歌曲与民族音乐。保留原语言与文化背景，听见不同地域的童年。",
        "scope": "多语言童谣、地方儿童歌曲、民族音乐",
        "focus": "保留原语言、文化背景和地域版本",
        "accent": "#2858b8",
    },
    "forgotten": {
        "no": "07", "name": "被遗忘的童谣", "key": "被遗忘的童谣",
        "desc": "地方方言、口传童谣与历史采录。记录传承人、采录地点、异文与语境，留住正在远去的声音。",
        "scope": "地方方言、口传童谣、历史采录",
        "focus": "记录传承人、采录地点、异文和语境",
        "accent": "#8b5e3c",
    },
    "original": {
        "no": "08", "name": "新芽原创", "key": "新芽原创",
        "desc": "当代原创儿童音乐。尊重儿童视角、创作质量与明确授权，给真正的新作品留出空间。",
        "scope": "当代原创儿童音乐",
        "focus": "尊重儿童视角、创作质量与明确授权",
        "accent": "#739348",
    },
}


def card_html(w):
    status = "候选 · 待核验"
    note = (w.get("note") or "").strip()
    note_html = f'<p class="note">{note}</p>' if note else ""
    return (
        f'<a class="work-card" href="works.html#work-{w["id"]}">'
        f'<span class="id">{w["id"]}</span>'
        f'<h3>{w["title"]}</h3>'
        f'<span class="type">{w["type"]} · {w["region"]}</span>'
        f'{note_html}'
        f'<span class="status">{status}</span>'
        f'</a>'
    )


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    works = data["works"]
    template = TEMPLATE.read_text(encoding="utf-8")
    stats = data["stats"]
    for key, spec in SPEC_DEFS.items():
        # 该专题的候选
        matches = [w for w in works if key in w["specialties"]]
        matches.sort(key=lambda w: w["id"])
        if matches:
            cards = "\n".join(card_html(w) for w in matches)
        else:
            cards = (
                '<div class="empty">'
                '<p>本专题为「新芽原创」，面向当代原创儿童音乐。</p>'
                '<p>当前候选作品待通过编辑评审与可追溯授权后逐首入库，暂无已登记曲目。</p>'
                '</div>'
            )
        html = template
        for token, value in {
            "__SPECIALTY_NAME__": spec["name"],
            "__SPECIALTY_NO__": spec["no"],
            "__SPECIALTY_KEY__": spec["key"],
            "__SPECIALTY_DESC__": spec["desc"],
            "__SPECIALTY_SCOPE__": spec["scope"],
            "__SPECIALTY_FOCUS__": spec["focus"],
            "__ACCENT__": spec["accent"],
            "__WORKS_COUNT__": str(len(matches)),
            "__WORKS_CARDS__": cards,
        }.items():
            html = html.replace(token, value)
        out = ROOT / f"specialty-{key}.html"
        out.write_text(html, encoding="utf-8")
        print(f"{key}: {len(matches)} 首 -> {out.name}")


if __name__ == "__main__":
    main()
