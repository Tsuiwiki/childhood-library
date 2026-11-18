import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"
SAMPLES_PATH = AUDIO_DIR / "samples.json"
COLLECTION_PATH = AUDIO_DIR / "public-recording-collection.json"
POLICY_PAGE = "../docs/COPYRIGHT_POLICY.md"


def duration_label(seconds):
    total = round(seconds)
    minutes, remaining = divmod(total, 60)
    return f"约 {minutes} 分 {remaining} 秒" if minutes else f"约 {remaining} 秒"


def version_label(record):
    labels = {
        "CN-C03-xuexi-chorus.mp3": "学习强国专辑合唱版 · 杨宁领唱 / 广州市少年艺术中心合唱团",
        "CN-C02-gxzf.flac": "中央乐团合唱团 · 广西公开音频版",
        "CN-C02-xuexi-chorus.m4a": "上海菁英少年合唱团 · 学习强国视频原声版",
    }
    return labels.get(record["file"], f"{record['author']} · {record['sourceTitle']}")


def make_sample(record, work_id, materials):
    author = "杨宁（领唱）、广州市少年艺术中心合唱团" if record["file"] == "CN-C03-xuexi-chorus.mp3" else record["author"]
    codec_names = {"mp3float": "MP3", "aac": "AAC", "flac": "FLAC"}
    codec = codec_names.get(record["codec"], record["codec"])
    extension = Path(record["file"]).suffix.lower()
    if record["file"] == "CN-C02-gxzf.flac":
        downloaded_format = f"来源扩展名为 .mp3，实际为 {codec}，{record['sampleRate'] / 1000:g} kHz {'双声道' if record['channels'] == 2 else '单声道'}；本地仅按实际编码改用 .flac 扩展名"
    elif extension == ".m4a":
        downloaded_format = f"M4A 容器 / {codec} 原声音轨，{record['sampleRate'] / 1000:g} kHz {'双声道' if record['channels'] == 2 else '单声道'}；未重新编码"
    else:
        downloaded_format = f"{codec}，{record['sampleRate'] / 1000:g} kHz {'双声道' if record['channels'] == 2 else '单声道'}；本地未剪辑或转码"
    sample = {
        "id": work_id,
        "file": record["file"],
        "workTitle": record["title"],
        "sourceTitle": record["sourceTitle"],
        "kind": record["kind"],
        "sampleType": "internal",
        "versionLabel": version_label(record),
        "durationLabel": duration_label(record["durationSeconds"]),
        "durationSeconds": record["durationSeconds"],
        "author": author,
        "attribution": f"{author} · {record['sourceTitle']}",
        "sourcePage": record["sourcePage"],
        "downloadedFile": record["mediaUrl"],
        "downloadedFormat": downloaded_format,
        "deliveryNote": f"{record['collectionMethod']}。演唱、编曲与录音版本以下来源页为准。",
        "license": "内部研究 · 权利待核验",
        "licenseUrl": POLICY_PAGE,
        "licenseNote": "公开页面可试听不等于开放再发布许可；此文件仅进入内部研究与原型库，词曲、表演及录音权利须另行核验。",
        "retrievedOn": record["collectedOn"],
        "bytes": record["bytes"],
        "sha256": record["sha256"],
        "changes": record["collectionMethod"],
        "materials": materials,
    }
    if record.get("sourceTrackId"):
        sample["sourceTrackId"] = record["sourceTrackId"]
    return sample


def main():
    samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    collection = json.loads(COLLECTION_PATH.read_text(encoding="utf-8"))
    collected_on = collection["collectedOn"]
    by_id = {sample["id"]: sample for sample in samples}
    records_by_id = {}
    for record in collection["records"]:
        record = {**record, "collectedOn": collected_on}
        for work_id in record["ids"]:
            records_by_id.setdefault(work_id, []).append(record)

    if set(records_by_id) != {
        "CN-C02", "CN-C03", "CN-C04", "CN-C05", "CN-C06", "CN-C07", "CN-C09",
        "CN-C11", "CN-C12", "CN-C13", "CN-C14", "CN-C15", "CN-C16", "CN-C17", "CN-C18", "CN-C19",
    }:
        raise ValueError("Unexpected collection work IDs")

    for work_id, records in records_by_id.items():
        existing = by_id[work_id]
        materials = existing["materials"]
        if work_id == "CN-C03":
            existing["versionLabel"] = "1957 电影《护士日记》片段 · 王丹凤"
            new_variant = make_sample(records[0], work_id, materials)
            new_variant.pop("id")
            new_variant.pop("materials")
            variants = [item for item in existing.get("variants", []) if item["file"] != new_variant["file"]]
            variants.append(new_variant)
            existing["variants"] = variants
            continue
        ordered = sorted(records, key=lambda record: 0 if record["file"] == "CN-C02-gxzf.flac" else 1)
        primary = make_sample(ordered[0], work_id, materials)
        variants = []
        for record in ordered[1:]:
            variant = make_sample(record, work_id, materials)
            variant.pop("id")
            variant.pop("materials")
            variants.append(variant)
        if variants:
            primary["variants"] = variants
        by_id[work_id] = primary

    updated = [by_id[sample["id"]] for sample in samples]
    if len(updated) != 58:
        raise ValueError(f"Expected 58 work entries, got {len(updated)}")
    referenced = [(sample["id"], sample["file"]) for sample in updated]
    referenced += [(sample["id"], variant["file"]) for sample in updated for variant in sample.get("variants", [])]
    expected = {(work_id, record["file"]) for record in collection["records"] for work_id in record["ids"]}
    if not expected.issubset(set(referenced)):
        raise ValueError(f"Missing mappings: {sorted(expected - set(referenced))}")
    counts = Counter(sample.get("sampleType", "open") for sample in updated)
    if counts != Counter({"generated": 29, "internal": 18, "open": 11}):
        raise ValueError(f"Unexpected sample counts: {counts}")
    SAMPLES_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"samples": len(updated), "counts": counts, "newFiles": collection["fileCount"], "newMappings": collection["workMappingCount"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
