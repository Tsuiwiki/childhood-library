import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT.parent / "docs" / "CLASSIC_SONGS_CATALOG.md"
TEMPLATE = ROOT / "works-template.html"
OUTPUT = ROOT / "works.html"
SAMPLES = ROOT / "audio" / "samples.json"
OFFICIAL_RECORDINGS = ROOT / "audio" / "official-recordings.json"
MATERIALS = ROOT / "china-materials.json"
WORLD_MATERIALS = ROOT / "world-materials.json"

SECTIONS = {
    "3": ("nursery", "中国传统童谣与民间歌谣", "中国"),
    "4": ("nursery", "中国经典创作儿歌", "中国"),
    "5": ("english", "英语传统童谣与民间歌曲", "英语地区"),
    "6": ("english", "英语摇篮曲与多元文化曲目", "多地区"),
}
STATUS_LABELS = {
    "candidate": "候选 · 待核验",
    "source_found": "已发现来源 · 权利待核验",
    "metadata_verified": "元数据已核实",
    "rights_pending": "权利待核验",
    "link_only": "仅保留外链",
    "authorized": "已获授权",
    "rejected": "不收录",
}
CREATORS = {
    "CN-C01": "乔羽词 · 刘炽曲",
    "CN-C02": "管桦词 · 张文纲曲",
    "CN-C03": "王路、王云阶词 · 王云阶曲",
    "CN-C10": "王健词 · 谷建芬曲",
    "CN-N01": "王嘉桢词 · 胡小环曲",
    "CN-N02": "罗大佑词曲",
    "CN-N03": "林重冏词曲",
    "CN-N04": "李少白词 · 朱青曲（潇湘童谣版）",
    "CN-N05": "林夕词 · 陈光荣曲",
}

NEW_WORKS = [
    {
        "id": "CN-N01", "title": "数鸭子", "type": "创作儿歌 / 数数",
        "note": "1983 年创作；按具体词曲与录音版本核验，不因广泛传唱视为公版。",
        "sourceTitle": "首批种子库候选清单 §1.8", "sourceUrl": "", "status": "candidate",
    },
    {
        "id": "CN-N02", "title": "童年", "type": "校园与童年 / 成人怀旧",
        "note": "罗大佑写给成人的怀旧作品；保留其创作定位，不包装成幼儿儿歌。",
        "sourceTitle": "首批种子库候选清单 §1.8", "sourceUrl": "", "status": "rights_pending",
    },
    {
        "id": "CN-N03", "title": "小毛驴", "type": "创作儿歌 / 动物",
        "note": "1960 年创作，念唱结合；词曲与具体录音权利仍需分别核验。",
        "sourceTitle": "首批种子库候选清单 §1.8", "sourceUrl": "", "status": "candidate",
    },
    {
        "id": "CN-N04", "title": "月亮走我也走（潇湘童谣版）", "type": "童谣风格 / 地方",
        "note": "李少白词、朱青曲的潇湘童谣版本；与同名成人送别歌严格分开建档。",
        "sourceTitle": "首批种子库候选清单 §1.8", "sourceUrl": "", "status": "candidate",
    },
    {
        "id": "CN-N05", "title": "虫儿飞", "type": "电影插曲 / 童谣风格",
        "note": "1998 年电影插曲；标注原作语境与适龄审核，不仅凭童谣风格归为幼儿歌曲。",
        "sourceTitle": "首批种子库候选清单 §1.8", "sourceUrl": "", "status": "rights_pending",
    },
]


def clean(value):
    return re.sub(r"\s+", " ", value.replace("<br>", " ")).strip()


def theme_for(work_id, work_type, note):
    text = f"{work_type} {note}"
    rules = [
        ("摇篮与安抚", ["摇篮", "安抚"]),
        ("游戏与互动", ["游戏", "互动", "轮唱", "拍手", "动作", "手指"]),
        ("自然与动物", ["自然", "动物", "植物", "田园", "海洋", "春天", "季节", "草原"]),
        ("叙事与想象", ["叙事", "荒诞", "想象"]),
        ("语言与认知", ["数数", "知识", "语言", "绕口令", "问答", "数字", "字母"]),
        ("家庭与生活", ["家庭", "生活", "校园", "劳动", "学习", "历史", "城市", "友谊", "节日", "民族"]),
    ]
    for theme, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return theme
    return "文化与民谣"


def world_creator_map():
    """世界经典资料卡里已核验的词曲作者，用于填充作品目录的「创作」字段。"""
    if not WORLD_MATERIALS.exists():
        return {}
    records = json.loads(WORLD_MATERIALS.read_text(encoding="utf-8"))
    return {record["id"]: record["creator"] for record in records}


def parse_catalog():
    entries = []
    world_creators = world_creator_map()
    section = None
    for raw_line in CATALOG.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^## (\d+)\.", raw_line)
        if heading:
            section = SECTIONS.get(heading.group(1))
            continue
        if not section or not re.match(r"^\| (?:CN|EN)-", raw_line):
            continue
        cells = [clean(cell) for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) != 6:
            raise ValueError(f"Unexpected catalog row: {raw_line}")
        work_id, title, work_type, note, source_cell, status = cells
        source_match = re.search(r"\[([^]]+)]\(([^)]+)\)", source_cell)
        source_title = source_match.group(1) if source_match else source_cell
        source_url = source_match.group(2) if source_match else ""
        group, group_name, region = section
        entries.append({
            "id": work_id,
            "title": title,
            "type": work_type,
            "note": note,
            "group": group,
            "groupName": group_name,
            "region": region,
            "theme": theme_for(work_id, work_type, note),
            "creator": (
                CREATORS.get(work_id)
                or world_creators.get(work_id)
                or ("传统歌谣 · 词曲作者不详（具体版本待核验）" if work_id.startswith("EN-") else "创作者与具体版本待核验")
            ),
            "status": status,
            "statusLabel": STATUS_LABELS.get(status, status),
            "sourceTitle": source_title,
            "sourceUrl": source_url,
        })
    for item in NEW_WORKS:
        entries.append({
            **item,
            "group": "nursery",
            "groupName": "中国经典补录",
            "region": "中国",
            "theme": theme_for(item["id"], item["type"], item["note"]),
            "creator": CREATORS[item["id"]],
            "statusLabel": STATUS_LABELS[item["status"]],
        })
    return entries


def load_samples(entries):
    if not SAMPLES.exists():
        return []
    samples = json.loads(SAMPLES.read_text(encoding="utf-8"))
    work_ids = {entry["id"] for entry in entries}
    sample_ids = set()
    required = {"id", "file", "kind", "durationLabel", "author", "attribution", "sourcePage", "license", "licenseUrl", "deliveryNote", "bytes", "sha256", "materials"}
    recording_required = required - {"id", "materials"}

    def validate_recording(record, work_id):
        missing = recording_required - set(record)
        if missing:
            raise ValueError(f"Recording metadata missing {sorted(missing)}: {work_id} {record.get('file')}")
        sample_type = record.get("sampleType", "open")
        if sample_type not in {"open", "internal", "generated"}:
            raise ValueError(f"Unknown sample type for {work_id}: {sample_type}")
        if Path(record["file"]).name != record["file"]:
            raise ValueError(f"Sample file must be a plain filename: {record['file']}")
        audio_path = SAMPLES.parent / record["file"]
        if not audio_path.is_file() or audio_path.stat().st_size == 0:
            raise ValueError(f"Sample audio is missing or empty: {audio_path}")
        payload = audio_path.read_bytes()
        if len(payload) != record["bytes"]:
            raise ValueError(f"Sample size does not match manifest: {record['file']}")
        if hashlib.sha256(payload).hexdigest() != record["sha256"]:
            raise ValueError(f"Sample SHA256 does not match manifest: {record['file']}")
        return sample_type

    for sample in samples:
        if {"id", "materials"} - set(sample):
            raise ValueError(f"Sample work ID or materials missing: {sample.get('file')}")
        if sample["id"] not in work_ids:
            raise ValueError(f"Sample references an unknown work ID: {sample['id']}")
        if sample["id"] in sample_ids:
            raise ValueError(f"Duplicate sample work ID: {sample['id']}")
        sample_type = validate_recording(sample, sample["id"])
        variants = sample.get("variants", [])
        if not isinstance(variants, list):
            raise ValueError(f"Sample variants must be a list for {sample['id']}")
        variant_files = set()
        for variant in variants:
            validate_recording(variant, sample["id"])
            if variant["file"] == sample["file"] or variant["file"] in variant_files:
                raise ValueError(f"Duplicate recording version for {sample['id']}: {variant['file']}")
            variant_files.add(variant["file"])
        materials = sample["materials"]
        full_materials = {"cover", "coverAlt", "score", "scoreSource", "scoreTitle", "scoreNote", "lyricsTitle", "lyrics", "lyricsNote"}
        has_full_material_fields = materials.get("lyrics") is not None or materials.get("score") is not None
        material_required = full_materials if sample_type == "open" or (sample_type == "internal" and has_full_material_fields) else {"cover", "coverAlt"}
        if material_required - set(materials):
            raise ValueError(f"Song materials incomplete for {sample['id']}")
        if "lyrics" in materials and (not materials["lyrics"] or not all(isinstance(line, str) and line.strip() for line in materials["lyrics"])):
            raise ValueError(f"Lyrics must be a non-empty list of lines for {sample['id']}")
        for key in ("cover", "score", "scoreSource"):
            value = materials.get(key)
            if value is None:
                continue
            relative_path = Path(value)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise ValueError(f"Unsafe song material path for {sample['id']}: {value}")
            if not (ROOT / relative_path).is_file():
                raise ValueError(f"Missing song material for {sample['id']}: {value}")
        sample_ids.add(sample["id"])
    return samples


def load_official_recordings(entries):
    if not OFFICIAL_RECORDINGS.exists():
        return []
    records = json.loads(OFFICIAL_RECORDINGS.read_text(encoding="utf-8"))
    work_ids = {entry["id"] for entry in entries}
    record_ids = set()
    required = {
        "id", "workTitle", "trackTitle", "artist", "album", "label", "releaseDate",
        "durationLabel", "versionNote", "provider", "providerTrackId", "sourcePage",
        "apiUrl", "artistSourcePage", "termsPage", "accessNote",
        "rightsNote", "reviewStatus", "checkedOn",
    }
    for record in records:
        missing = required - set(record)
        if missing:
            raise ValueError(f"Official recording metadata missing {sorted(missing)}: {record.get('id')}")
        work_id = record["id"]
        if work_id not in work_ids or work_id in record_ids:
            raise ValueError(f"Unknown or duplicate official recording work ID: {work_id}")
        if record["provider"] != "Deezer" or record["reviewStatus"] != "reviewed_click_to_load":
            raise ValueError(f"Official recording is not reviewed for click-to-load: {work_id}")
        track_id = record["providerTrackId"]
        if not track_id.isdigit():
            raise ValueError(f"Invalid Deezer track ID: {work_id}")
        if record["sourcePage"] != f"https://www.deezer.com/en/track/{track_id}":
            raise ValueError(f"Official recording source URL mismatch: {work_id}")
        if record["apiUrl"] != f"https://api.deezer.com/track/{track_id}":
            raise ValueError(f"Official recording API URL mismatch: {work_id}")
        for key in ("artistSourcePage", "termsPage"):
            if not record[key].startswith("https://"):
                raise ValueError(f"Official recording policy URL must use HTTPS: {work_id} {key}")
        record_ids.add(work_id)
    if len(records) != 5:
        raise ValueError(f"Expected 5 reviewed official recordings, got {len(records)}")
    return records


def check_material_paths(record, label):
    """校验资料卡里的相对路径，避免绝对路径或越界路径。"""
    for key in ("cover", "score", "scoreSource"):
        value = record.get(key)
        if value is None:
            continue
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or not (ROOT / path).is_file():
            raise ValueError(f"Missing or unsafe {label} material path for {record['id']}: {value}")


def load_materials(entries):
    """合并中国 55 条 + 世界经典 47 条资料卡，共 102 条覆盖全部 105 条作品。

    世界经典资料卡按「真实录音优先」口径生成：歌词 / 来源 / 权利状态已逐曲核验，
    但无可靠真实录音，因此没有音频、没有谱面，播放位统一标「待采集」。
    """
    work_ids = {entry["id"] for entry in entries}
    chinese = json.loads(MATERIALS.read_text(encoding="utf-8")) if MATERIALS.exists() else []
    world = json.loads(WORLD_MATERIALS.read_text(encoding="utf-8")) if WORLD_MATERIALS.exists() else []
    record_ids = set()

    for record in chinese:
        required = {"id", "cover", "coverAlt", "completion", "lyrics", "lyricsTitle", "lyricsNote", "score", "scoreSource"}
        missing = required - set(record)
        if missing:
            raise ValueError(f"Chinese material metadata missing {sorted(missing)}: {record.get('id')}")
        if record["id"] not in work_ids or not record["id"].startswith("CN-"):
            raise ValueError(f"Material references an unknown or non-Chinese work: {record['id']}")
        if record["id"] in record_ids:
            raise ValueError(f"Duplicate material work ID: {record['id']}")
        check_material_paths(record, "Chinese")
        if not isinstance(record["lyrics"], list):
            raise ValueError(f"Lyrics must be a list for {record['id']}")
        record_ids.add(record["id"])
    if len(chinese) != 55:
        raise ValueError(f"Expected 55 Chinese material records, got {len(chinese)}")

    world_required = {
        "id", "title", "chineseTitle", "creator", "cover", "coverAlt", "completion",
        "availability", "hasAudio", "audioStatus", "status", "rightsStatus", "researchStatus",
        "lyricsTitle", "lyrics", "lyricsNote", "score", "scoreSource", "scoreTitle", "scoreNote",
        "sourceTitle", "sourceUrl", "publicDomain", "extraNotes", "audioClue",
    }
    for record in world:
        missing = world_required - set(record)
        if missing:
            raise ValueError(f"World material metadata missing {sorted(missing)}: {record.get('id')}")
        if record["id"] not in work_ids or not record["id"].startswith("EN-"):
            raise ValueError(f"Material references an unknown or non-English work: {record['id']}")
        if record["id"] in record_ids:
            raise ValueError(f"Duplicate material work ID: {record['id']}")
        check_material_paths(record, "world")
        if not isinstance(record["lyrics"], list) or not all(isinstance(line, str) and line.strip() for line in record["lyrics"]):
            raise ValueError(f"Lyrics must be a list of non-empty lines for {record['id']}")
        if record["hasAudio"] is not False or record["audioStatus"] != "待采集":
            raise ValueError(f"World material must mark audio as pending: {record['id']}")
        if record["score"] is not None or record["scoreSource"] is not None:
            raise ValueError(f"World material must not fabricate a score: {record['id']}")
        if not record["sourceUrl"].startswith("https://"):
            raise ValueError(f"World material source URL must be HTTPS: {record['id']}")
        if record["publicDomain"] not in (True, False, "unknown"):
            raise ValueError(f"Invalid publicDomain value: {record['id']}")
        record_ids.add(record["id"])
    if len(world) != 47:
        raise ValueError(f"Expected 47 world material records, got {len(world)}")
    return chinese + world


def build_html():
    entries = parse_catalog()
    if len(entries) != 105:
        raise ValueError(f"Catalog extraction incomplete or unexpected: {len(entries)} entries")
    ids = [entry["id"] for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate work IDs in catalog")
    samples = load_samples(entries)
    official_recordings = load_official_recordings(entries)
    materials = load_materials(entries)
    template = TEMPLATE.read_text(encoding="utf-8")
    placeholders = ("__WORKS_DATA__", "__SAMPLES_DATA__", "__OFFICIAL_RECORDINGS_DATA__", "__MATERIALS_DATA__")
    if any(template.count(token) != 1 for token in placeholders):
        raise ValueError("Template must contain exactly one works, samples, official recordings and materials placeholder")
    payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    sample_payload = json.dumps(samples, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    official_payload = json.dumps(official_recordings, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    material_payload = json.dumps(materials, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace("__WORKS_DATA__", payload).replace("__SAMPLES_DATA__", sample_payload).replace("__OFFICIAL_RECORDINGS_DATA__", official_payload).replace("__MATERIALS_DATA__", material_payload)
    return html, entries, samples, official_recordings, materials


def main():
    html, entries, samples, official_recordings, materials = build_html()
    OUTPUT.write_text(html, encoding="utf-8")
    counts = {}
    for entry in entries:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    print(json.dumps({
        "output": str(OUTPUT),
        "total": len(entries),
        "chinese": sum(entry["group"] == "nursery" for entry in entries),
        "samples": len(samples),
        "officialRecordings": len(official_recordings),
        "chineseMaterials": sum(m["id"].startswith("CN-") for m in materials),
        "worldMaterials": sum(m["id"].startswith("EN-") for m in materials),
        "materialCoverage": len(materials),
        "audioPending": sum(m.get("audioStatus") == "待采集" for m in materials),
        "statusCounts": counts,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
