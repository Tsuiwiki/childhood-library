# -*- coding: utf-8 -*-
"""生成世界经典 47 条资料卡与原创 SVG 封面。

数据来源：
- world-lyrics-sources.json：四组逐曲核验的公版歌词 / 来源 / 权利结论
- specialties.json：105 条发现目录
- audio/samples.json：已有本地录音（用于判定哪些作品缺音频）

口径（用户选择「真实录音优先」）：
- 资料卡 47 条全补：封面、已核验歌词、来源、权利状态、研究线索
- 歌词查不到就留空并在说明里写清原因，不凭记忆补写、不扩写
- 没有可考证旋律就不生成五线谱，不伪造谱面
- 找不到可靠真实录音的播放位统一标「待采集」，不硬配合成音冒充原曲
- 47 首均为「研究／元数据层」资料卡，不因补齐资料卡而改变权利状态

本脚本只生成本地原创封面与元数据，不下载、不复制任何第三方音频或图片。
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "song-assets"
RAW = ROOT / "_world_lyrics_raw.json"
SOURCES = ROOT / "world-lyrics-sources.json"
SPECIALTIES = ROOT / "specialties.json"
SAMPLES = ROOT / "audio" / "samples.json"
MATERIALS_OUT = ROOT / "world-materials.json"
CLUES_OUT = ROOT / "world-audio-clues.json"

# 已通过 Commons API（WebFetch 通道）实际核验到的开放许可候选。
# 本地出口 IP 被 Wikimedia 403 / 429 限流，upload.wikimedia.org 无法下载；
# 且多条命中是同名异曲、器乐片段或 MIDI 数据，按口径均不接入作品播放。
AUDIO_CLUES = {
    "EN-T04": (
        "已核验 Commons 文件元数据：File:Baa, Baa, Blacksheep.ogg → CC BY-SA 3.0，"
        "作者 CambridgeBayWeather，23.95 秒，application/ogg，文件说明为「Tune for "
        "Baa, Baa, Blacksheep」的曲调演奏而非人声演唱；本地采集受源站 429 限制未完成。"
    ),
    "EN-T15": (
        "Commons 搜索命中 File:Old McDonald Had a Farm.ogg（CC BY-SA 3.0 片段），"
        "但文件标题拼写 McDonald 与目录条目 MacDonald 不一致，需逐项比对版本后才能判断，"
        "未核验前不接入。"
    ),
    "EN-T22": (
        "Commons 命中 File:Yankee Doodle (choral).ogg（Public Domain Mark 1.0）、"
        "File:Yankee Doodle - Concert Band - United States Air Force Heritage of America "
        "Band.mp3（美国联邦政府作品）；同批结果里另有多首 1910–1917 年同名异曲录音"
        "（When Yankee Doodle Marches Thro' Berlin 等），必须严格排除。"
    ),
    "EN-M08": (
        "Commons 命中 File:Simple Gifts - Miriam Bowen.ogg 与 File:Simple Gifts - "
        "Pendyrus Choir-cory Band.ogg（CC BY-SA 3.0，署名 Sain (Recordiau) Cyf.）、"
        "File:Simple Gifts (2017) - Concert Band - United States Air Force Band.mp3"
        "（美国联邦政府作品）；均未完成逐项身份与授权复核。"
    ),
    "EN-M01": (
        "Commons 仅命中 File:Hush, Little Baby.mid（CC0 的 MIDI 数据），不是可播放的真实录音，"
        "按「真实录音优先」口径不接入。"
    ),
}

# 词曲作者：只填可核验的具名信息，其余一律标注为传统 / 作者不详。
CREATORS = {
    "EN-T25": "Brewster M. Higley 词 · Daniel E. Kelley 曲（1870 年代，版权史有争议）",
    "EN-T27": "Stephen Foster 词曲（1848）",
    "EN-M04": "Johannes Brahms 曲（Op. 49 No. 4）；德文传统歌词与后世英译需分别核验",
    "EN-M05": "Thomas Dekker 原词（1603 剧作）；旋律与后世填词版本需分别核验",
    "EN-M06": "威尔士传统曲调《Ar Hyd y Nos》；英文填词版本需分别核验",
    "EN-M08": "Joseph Brackett 词曲（1848，Shaker 传统）",
    "EN-M19": "专辑 / 曲目专题（Pete Seeger 等演唱条目），不是独立单曲",
    "EN-M20": "专辑 / 曲目专题（Woody Guthrie 等），不是独立单曲；含现代版权作品",
    "EN-M12": "拉美传统儿歌《La rana》； Smithsonian Folkways 具体录音版本权利待核验",
    "EN-M14": "美国国会图书馆民俗录音条目；表演者与版本权利待核验",
    "EN-M15": "美国原住民传统蝙蝠歌；具体采集版本权利待核验",
    "EN-M17": "传统锯木歌；具体采集版本权利待核验",
    "EN-M18": "希腊传统儿歌《To mikro potamaki》；具体录音版本权利待核验",
}
DEFAULT_CREATOR = "传统歌谣 · 词曲作者不详（具体版本待核验）"

PALETTES = [
    {"accent": "#e64a38", "scene": "#dfe8fb", "shape": "#2858b8", "detail": "#f1bd32", "green": "#739348"},
    {"accent": "#2858b8", "scene": "#f7e6c8", "shape": "#e64a38", "detail": "#739348", "green": "#f1bd32"},
    {"accent": "#739348", "scene": "#e8eef7", "shape": "#8b5e3c", "detail": "#e64a38", "green": "#f1bd32"},
    {"accent": "#f1bd32", "scene": "#e4f0e2", "shape": "#2858b8", "detail": "#e64a38", "green": "#739348"},
    {"accent": "#8b5e3c", "scene": "#f5e2d8", "shape": "#739348", "detail": "#2858b8", "green": "#f1bd32"},
    {"accent": "#2858b8", "scene": "#f3ecd2", "shape": "#e64a38", "detail": "#f1bd32", "green": "#739348"},
]

MOTIF_NAMES = [
    "星月", "山丘与太阳", "波浪与小船", "绵羊与羊毛",
    "钟面", "蛛网", "小火车与铁轨", "树与飞鸟",
    "花草", "游鱼", "小桥", "音符",
]

INK = "#191917"


def motif_svg(kind: int, p: dict) -> str:
    """在 translate(48,332) 之后的 704x176 画布里画一幅原创剪贴簿小景。"""
    a, s, b, d, g = p["accent"], p["scene"], p["shape"], p["detail"], p["green"]
    frame = (
        f'<rect x="0" y="0" width="704" height="176" fill="{s}" '
        f'stroke="{INK}" stroke-width="6"/>'
    )
    sw = f'stroke="{INK}" stroke-width="5"'
    scenes = {
        0: f'''<circle cx="560" cy="62" r="46" fill="{d}" {sw}/>
<circle cx="580" cy="44" r="40" fill="{s}"/>
<path d="M70 116 l9 20 22 3 -16 15 4 22 -19-11 -19 11 4-22 -16-15 22-3z" fill="{b}" {sw}/>
<path d="M230 60 l7 16 18 2 -13 13 3 18 -15-9 -16 9 3-18 -13-13 18-2z" fill="{d}" {sw}/>
<path d="M380 116 l6 14 15 2 -11 11 3 15 -13-8 -13 8 3-15 -11-11 15-2z" fill="{g}" {sw}/>''',
        1: f'''<circle cx="590" cy="48" r="34" fill="{d}" {sw}/>
<path d="M0 150 Q170 62 330 150 T704 128 L704 176 L0 176 Z" fill="{g}" {sw}/>
<path d="M0 160 Q190 104 380 160 T704 146 L704 176 L0 176 Z" fill="{b}" {sw}/>
<path d="M120 118 l0 -42 M104 92 l16 -18 16 18" fill="none" {sw}/>''',
        2: f'''<path d="M0 118 Q88 92 176 118 T352 118 T528 118 T704 118 L704 176 L0 176 Z" fill="{b}" {sw}/>
<path d="M0 146 Q88 120 176 146 T352 146 T528 146 T704 146" fill="none" stroke="{d}" stroke-width="7"/>
<path d="M262 74 L442 74 L408 116 L296 116 Z" fill="{d}" {sw}/>
<path d="M350 74 L350 20 L412 62 L350 62 Z" fill="{a}" {sw}/>''',
        3: f'''<ellipse cx="250" cy="112" rx="118" ry="52" fill="{d}" {sw}/>
<circle cx="152" cy="94" r="30" fill="{d}" {sw}/>
<circle cx="196" cy="70" r="30" fill="{d}" {sw}/>
<circle cx="248" cy="66" r="30" fill="{d}" {sw}/>
<circle cx="300" cy="74" r="30" fill="{d}" {sw}/>
<ellipse cx="372" cy="86" rx="34" ry="28" fill="{b}" {sw}/>
<path d="M196 150 L196 168 M300 150 L300 168" {sw}/>
<circle cx="372" cy="80" r="5" fill="{INK}"/>''',
        4: f'''<circle cx="352" cy="88" r="72" fill="{d}" {sw}/>
<circle cx="352" cy="88" r="60" fill="#fffaf0" {sw}/>
<path d="M352 88 L352 44 M352 88 L392 100" fill="none" {sw}/>
<circle cx="352" cy="88" r="7" fill="{a}"/>
<path d="M352 20 L352 32 M352 144 L352 156 M284 88 L296 88 M408 88 L420 88" {sw}/>''',
        5: f'''<circle cx="352" cy="88" r="76" fill="none" {sw}/>
<path d="M352 12 L352 164 M276 88 L428 88 M298 34 L406 142 M406 34 L298 142" fill="none" stroke="{b}" stroke-width="4"/>
<circle cx="352" cy="88" r="52" fill="none" {sw}/>
<circle cx="352" cy="88" r="28" fill="none" {sw}/>
<circle cx="352" cy="88" r="12" fill="{a}" {sw}/>''',
        6: f'''<path d="M0 148 L704 148" {sw}/>
<path d="M0 164 L704 164" stroke="{b}" stroke-width="4"/>
<rect x="180" y="62" width="230" height="76" rx="10" fill="{a}" {sw}/>
<rect x="410" y="42" width="76" height="96" rx="8" fill="{b}" {sw}/>
<rect x="226" y="78" width="60" height="40" fill="{d}" {sw}/>
<rect x="300" y="78" width="60" height="40" fill="{d}" {sw}/>
<circle cx="230" cy="146" r="22" fill="{INK}"/><circle cx="360" cy="146" r="22" fill="{INK}"/>
<circle cx="450" cy="146" r="18" fill="{INK}"/>''',
        7: f'''<path d="M120 176 L120 66" {sw}/>
<circle cx="120" cy="62" r="52" fill="{g}" {sw}/>
<circle cx="86" cy="46" r="32" fill="{g}" {sw}/>
<circle cx="156" cy="46" r="32" fill="{g}" {sw}/>
<path d="M460 70 q22 -22 44 0 q22 -22 44 0" fill="none" {sw}/>
<path d="M560 120 q18 -18 36 0 q18 -18 36 0" fill="none" {sw}/>
<path d="M260 150 q30 -34 60 0" fill="none" stroke="{b}" stroke-width="6"/>''',
        8: f'''<path d="M0 148 Q176 118 352 148 T704 142 L704 176 L0 176 Z" fill="{g}" {sw}/>
<path d="M180 148 L180 74 M320 148 L320 60 M470 148 L470 82" {sw}/>
<circle cx="180" cy="66" r="20" fill="{a}" {sw}/>
<circle cx="320" cy="52" r="22" fill="{d}" {sw}/>
<circle cx="470" cy="74" r="20" fill="{b}" {sw}/>
<circle cx="180" cy="66" r="7" fill="{d}"/><circle cx="320" cy="52" r="7" fill="{a}"/>
<circle cx="470" cy="74" r="7" fill="{d}"/>''',
        9: f'''<path d="M0 120 Q88 92 176 120 T352 120 T528 120 T704 120" fill="none" stroke="{b}" stroke-width="6"/>
<path d="M240 88 Q330 26 430 88 Q330 150 240 88 Z" fill="{a}" {sw}/>
<path d="M430 88 L488 50 L488 126 Z" fill="{d}" {sw}/>
<circle cx="286" cy="80" r="7" fill="{INK}"/>
<path d="M330 44 q20 -22 40 0" fill="none" {sw}/>''',
        10: f'''<path d="M0 148 L704 148" {sw}/>
<path d="M120 148 Q352 -6 584 148" fill="none" stroke="{a}" stroke-width="14"/>
<path d="M120 148 Q352 26 584 148" fill="none" {sw}/>
<path d="M232 104 L232 148 M352 74 L352 148 M472 104 L472 148" {sw}/>
<path d="M0 166 Q176 146 352 166 T704 160" fill="none" stroke="{b}" stroke-width="6"/>''',
        11: f'''<path d="M0 148 Q176 118 352 148 T704 140" fill="none" stroke="{g}" stroke-width="7"/>
<ellipse cx="220" cy="120" rx="26" ry="18" fill="{a}" {sw} transform="rotate(-20 220 120)"/>
<path d="M242 120 L242 40 L286 52 L242 64" fill="none" {sw}/>
<ellipse cx="430" cy="106" rx="26" ry="18" fill="{b}" {sw} transform="rotate(-20 430 106)"/>
<path d="M452 106 L452 26" {sw}/>
<path d="M452 26 Q492 34 492 62" fill="none" {sw}/>
<circle cx="560" cy="66" r="14" fill="{d}" {sw}/>''',
    }
    return f'<g transform="translate(48,332)">{frame}{scenes[kind]}</g>'


def wrap_title(title: str, width: int = 24) -> list[str]:
    words = title.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if current and len(trial) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines[:3] or [title]


def cover_svg(work_id: str, title: str, chinese_title: str, motif: int, p: dict) -> str:
    display = re.sub(r"（[^）]*）", "", title).strip() or title
    lines = wrap_title(display)
    size = 38 if max(len(line) for line in lines) <= 24 else 31
    line_height = 46 if size == 38 else 40
    top = 142
    title_text = "".join(
        f'<text x="64" y="{top + i * line_height}" class="cover-title" '
        f'font-size="{size}">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    cn_y = top + len(lines) * line_height + 24
    esc = html.escape
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img" aria-labelledby="title desc">
  <title id="title">{esc(work_id)} — {esc(display)}</title>
  <desc id="desc">童年书房剪贴簿风格原创封面：{esc(MOTIF_NAMES[motif])}小景，配中英双语标题</desc>
  <defs>
    <pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">
      <circle cx="3" cy="3" r="1.8" fill="{INK}" opacity=".22"/>
    </pattern>
  </defs>
  <rect width="800" height="600" fill="#f4eddc"/>
  <rect width="800" height="600" fill="url(#dots)"/>
  <rect x="18" y="18" width="764" height="564" fill="none" stroke="{INK}" stroke-width="8"/>
  <rect x="42" y="42" width="14" height="96" fill="{p['accent']}" stroke="{INK}" stroke-width="4"/>
  <rect x="548" y="48" width="184" height="52" fill="#fffaf0" stroke="{INK}" stroke-width="4" transform="rotate(3 640 74)"/>
  <text x="640" y="83" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="900" fill="{INK}">{esc(work_id)}</text>
  <g fill="{INK}" font-family="Georgia, 'Noto Serif CJK SC', serif" font-weight="900" letter-spacing="-1">{title_text}</g>
  <text x="64" y="{cn_y}" font-family="'Noto Serif CJK SC', 'Songti SC', SimSun, serif" font-size="23" font-weight="700" fill="{p['shape']}">{esc(chinese_title)}</text>
  {motif_svg(motif, p)}
  <rect x="48" y="520" width="704" height="38" fill="#fffaf0" stroke="{INK}" stroke-width="4"/>
  <text x="64" y="546" font-family="Arial, 'Microsoft YaHei', sans-serif" font-size="20" font-weight="800" fill="{INK}">童年书房 · 世界经典童谣 · 原创封面</text>
</svg>
'''


def rights_status(public_domain) -> str:
    if public_domain is True:
        return "传统歌词公版；具体现代改编、译词与录音权利另行核验"
    if public_domain is False:
        return "含现代版权作品或专辑，权利待核验"
    return "权利状态未知，按待核验处理"


def main() -> None:
    # 首次运行把 Agent 原始输出规范化为可复核的数据文件，然后删除临时文件。
    if RAW.exists():
        rows = json.loads(RAW.read_text(encoding="utf-8"))
        SOURCES.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        RAW.unlink()
    else:
        rows = json.loads(SOURCES.read_text(encoding="utf-8"))

    spec = json.loads(SPECIALTIES.read_text(encoding="utf-8"))
    works = {w["id"]: w for w in spec["works"]}
    samples = json.loads(SAMPLES.read_text(encoding="utf-8"))
    have_audio = {s["id"] for s in samples}
    target_ids = {w["id"] for w in spec["works"] if w["id"] not in have_audio}
    row_by_id = {r["id"]: r for r in rows}
    if set(row_by_id) != target_ids:
        missing = sorted(target_ids - set(row_by_id))
        stale = sorted(set(row_by_id) - target_ids)
        raise ValueError(f"Lyric source coverage mismatch: missing={missing}, stale={stale}")
    if any(wid in have_audio for wid in row_by_id):
        raise ValueError("A world material record would overwrite an existing audio work")

    ASSETS.mkdir(parents=True, exist_ok=True)
    materials = []
    for work_id in sorted(target_ids):
        row = row_by_id[work_id]
        work = works[work_id]
        digest = int(hashlib.sha256(work_id.encode("utf-8")).hexdigest(), 16)
        motif = digest % len(MOTIF_NAMES)
        palette = PALETTES[(digest // len(MOTIF_NAMES)) % len(PALETTES)]
        title = row["title"]
        chinese = row.get("chineseTitle") or ""
        cover = f"song-assets/{work_id}-cover.svg"
        (ASSETS / f"{work_id}-cover.svg").write_text(
            cover_svg(work_id, title, chinese, motif, palette), encoding="utf-8"
        )
        lyrics = row.get("lyrics") or []
        lyrics_title = (row.get("lyricsTitle") or "").strip() or "传统歌词（来源页逐行照录）"
        lyrics_note = re.sub(r"^\s*lyrics=null[。.]?\s*", "", row.get("lyricsNote") or "").strip()
        if not lyrics:
            lyrics_title = "歌词待采集 · 权威来源未刊全文"
            if not lyrics_note:
                lyrics_note = "所查权威来源未刊出可逐行照录的歌词全文；按口径不凭记忆补写、不推测、不扩写。"
        else:
            if not lyrics_note:
                lyrics_note = "歌词按所列来源页逐行照录，保留原标点；未凭记忆补写或改写。"
        public_domain = row.get("publicDomain", "unknown")
        availability = (
            "歌词 / 谱面 / 真实录音待采集" if not lyrics
            else "歌词已核验 · 真实录音待采集"
        )
        materials.append({
            "id": work_id,
            "title": title,
            "chineseTitle": chinese,
            "creator": CREATORS.get(work_id, DEFAULT_CREATOR),
            "cover": cover,
            "coverAlt": f"《{title}》原创封面：{MOTIF_NAMES[motif]}剪贴簿小景，配「{chinese}」中英双语标题",
            "completion": "materials_only",
            "availability": availability,
            "hasAudio": False,
            "audioStatus": "待采集",
            "status": "metadata_verified",
            "rightsStatus": rights_status(public_domain),
            "researchStatus": "lyrics_verified" if lyrics else "source_only",
            "lyricsTitle": lyrics_title,
            "lyrics": lyrics,
            "lyricsNote": lyrics_note,
            "score": None,
            "scoreSource": None,
            "scoreTitle": None,
            "scoreNote": None,
            "sourceTitle": row.get("sourceTitle") or "",
            "sourceUrl": row.get("sourceUrl") or "",
            "publicDomain": public_domain,
            "extraNotes": row.get("extraNotes") or "",
            "audioClue": AUDIO_CLUES.get(work_id, ""),
        })

    MATERIALS_OUT.write_text(
        json.dumps(materials, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    clues = {
        "note": (
            "47 首世界经典均未接入第三方音频。用户口径为「真实录音优先」："
            "逐首核验开放许可 / 公开机构真实录音，找不到的播放位标「待采集」，"
            "不硬配程序合成音冒充原曲。"
        ),
        "probe": {
            "script": "probe_commons.py",
            "result": "blocked_by_wikimedia_rate_limit",
            "detail": (
                "本地出口 IP 访问 commons.wikimedia.org / en.wikipedia.org / api.wikimedia.org "
                "的 API 均返回 HTTP 403 Too Many Reqs；upload.wikimedia.org 返回 HTTP 429。"
                "WebFetch 通道可读取 Commons API 元数据，但无法下载二进制音频，"
                "且浏览器内置预览只加载本地文件，故本轮未采集任何第三方音频。"
            ),
            "checkedOn": "2026-11-18",
        },
        "verifiedCandidates": [
            {"id": wid, "note": AUDIO_CLUES[wid]} for wid in sorted(AUDIO_CLUES)
        ],
        "conclusion": (
            "已核验的候选多为器乐片段、MIDI 数据、同名异曲或专辑录音，"
            "不能作为目标作品的可播放真实录音；须逐项完成版本、表演者与授权复核后再决定。"
        ),
    }
    CLUES_OUT.write_text(
        json.dumps(clues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "worldMaterials": len(materials),
        "covers": len(list(ASSETS.glob("EN-*-cover.svg"))),
        "withLyrics": sum(1 for m in materials if m["lyrics"]),
        "lyricsPending": sum(1 for m in materials if not m["lyrics"]),
        "audioPending": sum(1 for m in materials if m["audioStatus"] == "待采集"),
        "verifiedAudioClues": len(clues["verifiedCandidates"]),
        "materialsFile": MATERIALS_OUT.name,
        "cluesFile": CLUES_OUT.name,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
