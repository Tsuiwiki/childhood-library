from array import array
from collections import Counter
import hashlib
import html
import json
import math
from pathlib import Path
import wave

import verovio

import build_song_assets as base
import build_works

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "song-assets"
OUT.mkdir(exist_ok=True)
AUDIO = ROOT / "audio"
AUDIO.mkdir(exist_ok=True)

CHINA_IDS = [
    "CN-C01", "CN-C02", "CN-C03", "CN-C10", "CN-C11", "CN-C12", "CN-C06", "CN-C07",
    "CN-C15", "CN-C19", "CN-C20", "CN-C18", "CN-C21", "CN-C23", "CN-C24",
    "CN-T01", "CN-T02", "CN-T03", "CN-T04", "CN-T05", "CN-T07", "CN-T08", "CN-T09",
    "CN-T10", "CN-T12", "CN-C27", "CN-C28", "CN-C29",
    "CN-C08", "CN-C04", "CN-C16", "CN-C05", "CN-C13", "CN-C14",
    "CN-C09", "CN-C22", "CN-T06", "CN-T15",
    "CN-C25", "CN-C26", "CN-C17", "CN-T14",
    "CN-T11", "CN-T13", "CN-T16", "CN-T17", "CN-T18", "CN-T19", "CN-T20", "CN-C30",
    "CN-N01", "CN-N02", "CN-N03", "CN-N04", "CN-N05",
]
TOPIC_IDS = {"CN-T11", "CN-T20", "CN-C30"}

NEW_EXAMPLES = {
    "CN-T02": {
        "versionTitle": "摇啊摇，摇到外婆桥（上海嘉定短版）",
        "region": "上海嘉定",
        "lines": ["摇啊摇，摇到外婆桥，", "外婆叫我好宝宝。", "糖一包，果一包，", "外婆买条鱼来烧。"],
        "sourceTitle": "上海市嘉定区人民政府《曲艺文化走进古镇校园：从“青黄不接”到“处处繁花”》",
        "sourcePage": "https://www.jiading.gov.cn/mspd/shgj/content_879799",
        "lyricsNote": "采用嘉定区政府页面所列沪语童谣短文本；不与其他上海异文、同名电影或现代录音混同。传统文本可核对不等于来源网页或表演录音可自由转载。",
        "tempo": 82, "motif": "金色月亮、蓝色水波与摇向外婆桥的小船",
    },
    "CN-T05": {
        "versionTitle": "拍手歌（江苏海州方言游戏歌版）",
        "region": "江苏海州",
        "lines": [
            "你拍一我拍一，一个小孩哭叽叽。", "你拍二我拍二，二个小孩挑荠菜。",
            "你拍三我拍三，三个小孩吃饼干。", "你拍四我拍四，四个小孩吃洋柿。",
            "你拍五我拍五，五个小孩打边鼓。", "你拍六我拍六，六个小孩吃涮羊肉。",
            "你拍七我拍七，七个小孩坐飞机。", "你拍八我拍八，八个小孩笑哈哈。",
            "你拍九我拍九，九个小孩推牌九。", "你拍十我拍十，十个小孩打到蒋介石。",
        ],
        "sourceTitle": "今日海州《【美丽海州】海州方言童谣，你还记得几首？》",
        "sourcePage": "http://mp.weixin.qq.com/s?__biz=MzA5MDEzNTA4OA==&mid=402106063&idx=1&sn=bb8a7a3338983109d1bbc6f6d9bc119b&chksm=03fe5bbfad39edd87931d845ea0f212acbd8fe57ed8cc16387cd1b05861c3238465b8f9e038b#rd",
        "lyricsNote": "按海州区官方新媒体所录民间口头文学版本照录，保留“二个”“洋柿”等方言用字。末句含特定历史时期措辞，作为民俗史料展示，不改为现代宣传文本，也不采用同名现代创作。",
        "tempo": 104, "motif": "拍手游戏、数字卡片与红色节奏块",
    },
    "CN-C25": {
        "versionTitle": "小白兔白又白（河南睢县采录本）",
        "region": "河南睢县",
        "lines": ["小白兔，白又白，", "两个耳朵竖起来，", "爱吃萝卜爱吃菜，", "蹦蹦跳跳真可爱。"],
        "sourceTitle": "河南党史方志网《自然界事物歌》",
        "sourcePage": "http://www.hndsfz.cn/szfzg/2023/03-23/51733.html",
        "lyricsNote": "采用河南党史方志网所载睢县采录本，原文为“两个耳朵”，不替换成其他流行版本；原页列采录地与采录人，未据此推定录音或整理稿授权。",
        "tempo": 96, "motif": "绿色草地上的白兔、胡萝卜与蓝色天空",
    },
    "CN-C27": {
        "versionTitle": "拉大锯，扯大锯（辽宁朝阳童谣版）",
        "region": "辽宁朝阳",
        "lines": ["拉大锯，扯大锯，", "老家门口唱大戏。", "接闺女带女婿，", "小外甥也要去，", "去了没水喝，给个缸底喝，", "去了没地住，和小猪一被窝。"],
        "sourceTitle": "央视新闻、中国之声《声音里的中国丨地处辽宁，为什么朝阳的东北味儿不浓？》转载页",
        "sourcePage": "http://mp.weixin.qq.com/s?__biz=MzA4MzA1NzExNA==&mid=2650593603&idx=4&sn=1b92f9089a99c2fe374e58ed83c005fa&chksm=87f439f6b083b0e0bc34a337b16726688e1d3c90956894675fdd23e84a922992aa095b97423f#rd",
        "lyricsNote": "按权威报道所引朝阳童谣分段照录；报道未署词作者、采集人及采录年代，因此不称为唯一标准本，配套节目音频未被使用。",
        "tempo": 100, "motif": "红色戏台、绿色锯木动作与乡村大戏",
    },
    "CN-C29": {
        "versionTitle": "数蛤蟆（四川经典童谣首段）",
        "region": "四川",
        "lines": ["一只蛤蟆一张嘴，", "两只眼睛四条腿，", "扑通一声跳下水，", "蛤蟆不吃水，", "太平年，", "荷儿梅子兮，", "水上飘。"],
        "sourceTitle": "北京日报客户端、国家大剧院《从音画到史诗｜交响合唱〈炎黄风情〉即将世界首演》",
        "sourcePage": "https://peking.bjd.com.cn/content/s6909584ee4b0221b9bef1a80.html",
        "lyricsNote": "采用国家大剧院稿件所引四川经典童谣首段，保留“水上飘”等原文；后续数量递增段不由规则推演补写，现代合唱、编曲与演出录音不在此示范中。",
        "tempo": 92, "motif": "绿色荷塘、跳跃的蛤蟆与蓝色水波",
    },
}

ACCENTS = ["#e64a38", "#2858b8", "#739348", "#f1bd32"]


def title_lines(title):
    title = title.replace("（", "\n（", 1) if "（" in title else title
    lines = title.split("\n", 1)
    if len(lines) == 1 and len(title) > 9:
        lines = [title[:6], title[6:]]
    return lines[:2]


def motif_for(entry):
    text = f"{entry['title']} {entry['type']}"
    if any(word in text for word in ["摇篮", "月亮", "月光", "夜"]):
        return "moon"
    if any(word in text for word in ["动物", "兔", "鼠", "鸭", "蛤蟆", "燕", "蜂", "鸟", "驴"]):
        return "animal"
    if any(word in text for word in ["海", "水", "船", "桥", "澎湖湾", "螺号"]):
        return "water"
    if any(word in text for word in ["游戏", "拍手", "数数", "问答", "互动", "手绢", "朋友"]):
        return "play"
    if any(word in text for word in ["自然", "田园", "春天", "花", "瓜", "田野", "蘑菇", "树"]):
        return "nature"
    if any(word in text for word in ["学习", "校园", "读书", "老师", "历史", "叙事"]):
        return "book"
    return "music"


def motif_art(kind, accent):
    common = 'stroke="#191917" stroke-width="7" stroke-linejoin="round"'
    if kind == "moon":
        return f'''<rect x="360" y="150" width="370" height="330" fill="#2858b8" {common}/><circle cx="620" cy="250" r="70" fill="#f1bd32" {common}/><path d="M392 400 Q470 350 548 402 T716 390 L716 466 L392 466 Z" fill="{accent}" {common}/><path d="M420 230 l10 22 24 3-18 16 5 24-21-12-21 12 5-24-18-16 24-3z" fill="#fffaf0" {common}/>'''
    if kind == "animal":
        return f'''<path d="M80 430 Q240 360 400 426 T730 404 L730 492 L80 492 Z" fill="#739348" {common}/><ellipse cx="520" cy="342" rx="116" ry="92" fill="#fffaf0" {common}/><circle cx="418" cy="292" r="62" fill="#fffaf0" {common}/><path d="M390 242 Q360 142 402 140 Q438 176 424 244 M434 238 Q442 142 482 154 Q500 194 458 254" fill="{accent}" {common}/><circle cx="400" cy="290" r="7" fill="#191917"/><path d="M386 320 Q410 338 434 316" fill="none" {common}/><path d="M600 316 Q682 272 680 350 Q664 408 610 386" fill="{accent}" {common}/>'''
    if kind == "water":
        return f'''<rect x="56" y="174" width="680" height="310" fill="#2858b8" {common}/><circle cx="648" cy="218" r="46" fill="#f1bd32" {common}/><path d="M70 344 Q138 308 206 346 T342 342 T478 340 T614 338 T730 334 M70 424 Q138 388 206 426 T342 422 T478 420 T614 418 T730 414" fill="none" stroke="#fffaf0" stroke-width="14"/><path d="M226 334 L514 318 L458 424 L292 438 Z" fill="{accent}" {common}/><path d="M360 320 L360 196 L492 300 Z" fill="#fffaf0" {common}/>'''
    if kind == "play":
        return f'''<circle cx="530" cy="316" r="128" fill="{accent}" {common}/><path d="M416 254 Q530 300 644 252 M424 382 Q530 334 638 386 M530 188 V444" fill="none" {common}/><path d="M96 210 L290 190 L302 252 L106 270 Z" fill="#2858b8" {common}/><path d="M126 330 h52 v52 h-52z M196 300 h52 v52 h-52z M126 400 h52 v52 h-52z" fill="#f1bd32" {common}/>'''
    if kind == "nature":
        return f'''<circle cx="640" cy="208" r="54" fill="#f1bd32" {common}/><path d="M60 440 Q190 290 340 424 Q480 260 736 420 L736 494 L60 494 Z" fill="#739348" {common}/><path d="M504 430 V290" fill="none" {common}/><path d="M504 328 Q426 272 414 342 Q458 374 504 350 M504 366 Q582 306 596 378 Q550 410 504 390" fill="{accent}" {common}/><circle cx="504" cy="264" r="52" fill="{accent}" {common}/><circle cx="504" cy="264" r="20" fill="#f1bd32" {common}/>'''
    if kind == "book":
        return f'''<path d="M96 206 Q202 168 306 216 V450 Q202 402 96 442 Z M306 216 Q412 168 518 206 V442 Q412 402 306 450 Z" fill="#fffaf0" {common}/><path d="M306 216 V450 M126 254 Q204 232 274 258 M126 300 Q204 278 274 304 M340 258 Q410 232 488 254 M340 304 Q410 278 488 300" fill="none" {common}/><path d="M548 194 L694 172 L714 406 L568 428 Z" fill="{accent}" {common}/><path d="M580 244 L672 228 M586 292 L678 276 M592 340 L684 324" stroke="#fffaf0" stroke-width="10"/>'''
    return f'''<rect x="360" y="150" width="370" height="330" fill="{accent}" {common}/><path d="M450 206 V372 Q396 338 382 382 Q382 432 450 400 V254 L566 224 V340 Q512 306 498 350 Q498 400 566 368 V184 Z" fill="#fffaf0" {common}/><path d="M94 220 L284 194 L300 428 L110 454 Z" fill="#2858b8" {common}/><circle cx="194" cy="318" r="64" fill="#f1bd32" {common}/><path d="M160 334 Q194 366 230 330" fill="none" {common}/>'''


def generic_cover(entry):
    work_id = entry["id"]
    accent = ACCENTS[sum(ord(char) for char in work_id) % len(ACCENTS)]
    kind = motif_for(entry)
    lines = title_lines(entry["title"])
    title = "".join(f'<text x="54" y="{96 + index * 50}" class="cover-title">{html.escape(line)}</text>' for index, line in enumerate(lines))
    modern = entry["status"] == "rights_pending" or work_id.startswith("CN-N")
    category = "现代创作 · 权利待核验" if modern else "传统/地方童谣 · 版本核验"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img" aria-labelledby="title desc">
  <title id="title">{html.escape(work_id)} — {html.escape(entry['title'])}</title>
  <desc id="desc">童年书房原创主题封面，{html.escape(entry['type'])}</desc>
  <defs><pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.8" fill="#191917" opacity=".22"/></pattern></defs>
  <rect width="800" height="600" fill="#f4eddc"/><rect width="800" height="600" fill="url(#dots)"/>
  <rect x="18" y="18" width="764" height="564" fill="none" stroke="#191917" stroke-width="8"/>
  <rect x="42" y="42" width="14" height="116" fill="{accent}" stroke="#191917" stroke-width="4"/>
  <rect x="548" y="48" width="184" height="52" fill="#fffaf0" stroke="#191917" stroke-width="4" transform="rotate(3 640 74)"/>
  <text x="640" y="83" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="900" fill="#191917">{html.escape(work_id)}</text>
  <g fill="#191917" font-family="Georgia, 'Noto Serif CJK SC', 'Songti SC', SimSun, serif" font-size="42" font-weight="900">{title}</g>
  {motif_art(kind, accent)}
  <rect x="48" y="520" width="704" height="38" fill="#fffaf0" stroke="#191917" stroke-width="4"/>
  <text x="64" y="546" font-family="Arial, 'Microsoft YaHei', sans-serif" font-size="19" font-weight="800" fill="#191917">童年书房 · {category} · 原创封面</text>
</svg>'''


def build_all_covers(entries):
    for entry in entries:
        if entry["id"] not in CHINA_IDS:
            continue
        path = OUT / f"{entry['id']}-cover.svg"
        if path.exists():
            continue
        path.write_text(generic_cover(entry), encoding="utf-8")


def make_melody(track_index, line_count):
    scale = [("C", 4), ("D", 4), ("E", 4), ("G", 4), ("A", 4), ("C", 5), ("A", 4), ("G", 4), ("E", 4), ("D", 4)]
    measures = []
    original_notes = []
    for line_index in range(line_count):
        line_notes = []
        for note_index in range(8):
            pitch = scale[(track_index * 2 + line_index * 3 + note_index) % len(scale)]
            line_notes.append((pitch, 4, "quarter"))
            original_notes.append(f"{pitch[0]}{pitch[1]}")
        measures.extend([line_notes[:4], line_notes[4:]])
    return measures, " ".join(original_notes)


def synthesize_audio(work_id, measures, divisions, tempo):
    sample_rate = 22050
    seconds_per_beat = 60 / tempo
    lead_in = 0.25
    total_seconds = lead_in + len(measures) * 4 * seconds_per_beat + 0.8
    samples = array("f", [0.0]) * int(total_seconds * sample_rate)
    beat_cursor = 0.0
    for measure_index, measure in enumerate(measures):
        bass = ("C", 3) if measure_index % 4 in {0, 1, 3} else ("G", 3)
        base.add_tone(samples, sample_rate, lead_in + beat_cursor * seconds_per_beat, 3.7 * seconds_per_beat, base.pitch_frequency(bass), 0.045, 0.3)
        for pitch, duration, _note_type, *_rest in measure:
            beats = duration / divisions
            start = lead_in + beat_cursor * seconds_per_beat
            base.add_tone(samples, sample_rate, start, beats * seconds_per_beat * 0.92, base.pitch_frequency(pitch), 0.22)
            beat_cursor += beats
    peak = max(abs(value) for value in samples) or 1.0
    scale = 0.82 / peak
    pcm = array("h", (int(max(-1.0, min(1.0, value * scale)) * 32767) for value in samples))
    path = AUDIO / f"{work_id}.wav"
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())
    return path


def build_new_examples(entries):
    by_id = {entry["id"]: entry for entry in entries}
    toolkit = verovio.toolkit()
    toolkit.setOptions({
        "pageWidth": 2200, "pageHeight": 2800, "scale": 45,
        "adjustPageHeight": True, "breaks": "encoded", "header": "none", "footer": "none",
        "pageMarginTop": 60, "pageMarginBottom": 60, "pageMarginLeft": 60, "pageMarginRight": 60,
    })
    new_samples = []
    for track_index, (work_id, data) in enumerate(NEW_EXAMPLES.items()):
        entry = by_id[work_id]
        lines = data["lines"]
        layouts = [{
            "language": "zh",
            "lines": [(line, index * 2 + 1, index * 2 + 2) for index, line in enumerate(lines)],
        }]
        measures, original_notes = make_melody(track_index, len(lines))
        breaks = {index for index in range(5, len(measures) + 1, 4)}
        divisions = 4
        prepared = base.prepare_lyric_measures(measures, divisions, layouts)
        title = f"{data['versionTitle']} — 原创器乐示范，非传统旋律记谱"
        score_source = base.build_musicxml(work_id, title, prepared, divisions, breaks, "童年书房原创示范")
        if not toolkit.loadFile(str(score_source)):
            raise RuntimeError(f"Verovio could not load {score_source}")
        if toolkit.getPageCount() != 1:
            raise RuntimeError(f"Expected one-page score for {work_id}")
        score_path = OUT / f"{work_id}-score.svg"
        score_path.write_text(toolkit.renderToSVG(1), encoding="utf-8")
        audio_path = synthesize_audio(work_id, prepared, divisions, data["tempo"])
        payload = audio_path.read_bytes()
        new_samples.append({
            "id": work_id,
            "file": audio_path.name,
            "workTitle": data["versionTitle"],
            "sourceTitle": data["sourceTitle"],
            "kind": "原创器乐示范（无人声）",
            "sampleType": "open",
            "durationLabel": f"约 {round(len(payload) / 2 / 22050)} 秒",
            "author": "童年书房原型",
            "attribution": "童年书房原型 · 程序合成器乐",
            "sourcePage": data["sourcePage"],
            "generatedFormat": "WAV，22,050 Hz，16-bit 单声道 PCM",
            "deliveryNote": "本地生成的原创器乐示范；无人声，不是地方传统唱腔的采录、复原或原曲旋律。",
            "license": "CC0 1.0",
            "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
            "licenseNote": "新生成的示范音频、封面与简化谱以 CC0 1.0 提供；传统歌词版本与出处单独标明，该许可不延伸至来源网页。",
            "retrievedOn": "2026-11-18",
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "changes": "由 build_china_library.py 从与 MusicXML 相同的原创音符数据生成，未使用外部录音样本。",
            "engraving": {"measures": len(measures), "divisions": divisions, "notes": original_notes},
            "materials": {
                "cover": f"song-assets/{work_id}-cover.svg",
                "coverAlt": f"《{entry['title']}》原创封面：{data['motif']}",
                "score": f"song-assets/{work_id}-score.svg",
                "scoreSource": f"song-assets/{work_id}-score.musicxml",
                "scoreTitle": f"原创示范旋律 · C 大调 · 4/4 · {len(measures)} 小节",
                "scoreNote": "与示范音频使用同一原创音符数据；仅用于展示歌词与谱面联动，不表示该地方童谣的传统旋律或唱腔。",
                "scoreReferences": [],
                "lyricsTitle": f"传统歌词参考 · {data['region']}版本（音频为器乐）",
                "lyrics": lines,
                "lyricsNote": data["lyricsNote"],
            },
        })
    return new_samples


def build_audio_only_examples(entries, existing_samples):
    """Give every remaining Chinese record a clearly labelled original playback demo.

    These are interface demonstrations, not transcriptions or substitutes for the
    referenced songs. No protected melody, lyrics or external recording is used.
    """
    by_id = {entry["id"]: entry for entry in entries}
    existing_ids = {sample["id"] for sample in existing_samples}
    generated = []
    for track_index, work_id in enumerate(CHINA_IDS):
        if work_id in existing_ids:
            continue
        entry = by_id[work_id]
        measures, _notes = make_melody(track_index + 17, 2)
        audio_path = synthesize_audio(work_id, measures, 4, 92 + track_index % 5 * 6)
        payload = audio_path.read_bytes()
        generated.append({
            "id": work_id,
            "file": audio_path.name,
            "workTitle": f"{entry['title']} · 原创播放示范（非原曲）",
            "sourceTitle": "童年书房原创播放示范规则",
            "kind": "原创氛围音型（非原曲旋律、无人声）",
            "sampleType": "generated",
            "durationLabel": f"约 {round(len(payload) / 2 / 22050)} 秒",
            "author": "童年书房原型",
            "attribution": "童年书房原型 · 程序合成音频",
            "sourcePage": "../docs/COPYRIGHT_POLICY.md",
            "generatedFormat": "WAV，22,050 Hz，16-bit 单声道 PCM",
            "deliveryNote": "仅用于验证资料卡的音频播放交互；不是该作品的旋律、歌曲录音、传统唱腔或替代版本。",
            "license": "CC0 1.0",
            "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
            "licenseNote": "CC0 仅覆盖本次新生成的原创音频文件，不延伸至目录所指向的歌曲词曲、歌词、谱面、表演或录音。",
            "retrievedOn": "2026-11-18",
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "changes": "由 build_china_library.py 生成全新音型，未引用外部录音或目标歌曲旋律。",
            "materials": {
                "cover": f"song-assets/{work_id}-cover.svg",
                "coverAlt": f"《{entry['title']}》原创主题封面",
            },
        })
    return generated


def merge_samples(new_samples):
    path = ROOT / "audio" / "samples.json"
    existing = json.loads(path.read_text(encoding="utf-8"))
    by_id = {sample["id"]: sample for sample in existing}
    for sample in new_samples:
        by_id[sample["id"]] = sample
    samples = sorted(by_id.values(), key=lambda sample: sample["id"])
    path.write_text(json.dumps(samples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return samples


def write_material_manifest(entries, samples):
    sample_by_id = {sample["id"]: sample for sample in samples}
    records = []
    for work_id in CHINA_IDS:
        entry = next(item for item in entries if item["id"] == work_id)
        sample = sample_by_id.get(work_id)
        if sample and sample.get("sampleType") != "generated":
            record = dict(sample["materials"])
            record.update({
                "id": work_id,
                "completion": "full_internal" if sample.get("sampleType") == "internal" else "full_open",
                "availability": "完整资料 · 内部权利待核验" if sample.get("sampleType") == "internal" else "完整资料 · 原创示范",
                "hasAudio": True,
            })
        else:
            is_topic = work_id in TOPIC_IDS
            record = {
                "id": work_id,
                "cover": f"song-assets/{work_id}-cover.svg",
                "coverAlt": f"《{entry['title']}》原创主题封面",
                "score": None,
                "scoreSource": None,
                "scoreTitle": "五线谱待版本核验",
                "scoreNote": "尚未确认可使用的具体旋律与改编版本，不生成冒充原曲的谱面。",
                "lyricsTitle": "版本专题 · 待拆分单曲" if is_topic else "歌词与版本待核验",
                "lyrics": [],
                "lyricsNote": "这是版本或分类专题，须先拆分为有明确地区、文本与采录来源的单曲。" if is_topic else "当前仅展示作品元数据与原创封面；受保护文本不收录全文，传统版本也须先确认具体来源。",
                "completion": "topic" if is_topic else "metadata_only",
                "availability": "版本专题" if is_topic else "资料卡 · 权利待核验",
                "hasAudio": False,
            }
        if sample and sample.get("sampleType") == "generated":
            record.update({
                "hasAudio": True,
                "audioKind": "generated",
                "availability": "原创播放示范 · 非原曲",
            })
        record["title"] = entry["title"]
        record["creator"] = entry["creator"]
        record["status"] = entry["status"]
        records.append(record)
    path = ROOT / "china-materials.json"
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return records


def main():
    entries = build_works.parse_catalog()
    by_id = {entry["id"] for entry in entries}
    missing = set(CHINA_IDS) - by_id
    if missing:
        raise ValueError(f"Missing Chinese catalog entries: {sorted(missing)}")
    build_all_covers(entries)
    new_samples = build_new_examples(entries)
    samples = merge_samples(new_samples)
    generated_samples = build_audio_only_examples(entries, samples)
    samples = merge_samples(generated_samples)
    records = write_material_manifest(entries, samples)
    counts = Counter(record["completion"] for record in records)
    print(json.dumps({
        "chineseWorks": len(records), "covers": len(records),
        "newOpenExamples": len(new_samples), "newAudioOnlyDemos": len(generated_samples),
        "chineseWithAudio": sum(record["hasAudio"] for record in records),
        "completionCounts": counts, "totalSamples": len(samples),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
