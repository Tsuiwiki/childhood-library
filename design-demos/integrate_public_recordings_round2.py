# -*- coding: utf-8 -*-
"""把第二轮采集的真实录音接入 audio/samples.json。

规则：
- 只替换原本 sampleType=generated 的 8 个作品，主录音来自 role=primary 的记录；
- role=variant 的记录追加到 variants，保留版本选择能力，不覆盖主版本；
- 沿用原有 materials（封面 / 封面说明），不伪造歌词或五线谱；
- 精确标注诵读 / 表演 / 改编版本，不把非歌曲演唱录音写成「原唱」；
- 幂等：可重复运行，按文件名去重。
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from integrate_public_recordings import COLLECTION_PATH, POLICY_PAGE, SAMPLES_PATH, duration_label

CODEC_NAMES = {"mp3float": "MP3", "mp3": "MP3", "aac": "AAC", "flac": "FLAC"}


def downloaded_format(record):
    codec = CODEC_NAMES.get(record["codec"], record["codec"])
    channel = "双声道" if record["channels"] == 2 else "单声道"
    rate = f"{record['sampleRate'] / 1000:g} kHz"
    if record["file"].endswith(".m4a"):
        return f"M4A 容器 / {codec} 原声音轨，{rate} {channel}；未重新编码"
    return f"{codec}，{rate} {channel}；本地未剪辑或转码"


def make_sample(record, work_id, materials, collected_on):
    author = record["author"]
    delivery = f"{record['collectionMethod']}。演唱、编曲与录音版本以来源页为准。"
    if record.get("versionNote"):
        delivery += " " + record["versionNote"]
    sample = {
        "id": work_id,
        "file": record["file"],
        "workTitle": record["title"],
        "sourceTitle": record["sourceTitle"],
        "kind": record["kind"],
        "sampleType": "internal",
        "versionLabel": f"{author} · {record['sourceTitle']}",
        "durationLabel": duration_label(record["durationSeconds"]),
        "durationSeconds": record["durationSeconds"],
        "author": author,
        "attribution": f"{author} · {record['sourceTitle']}",
        "sourcePage": record["sourcePage"],
        "downloadedFile": record["mediaUrl"],
        "downloadedFormat": downloaded_format(record),
        "deliveryNote": delivery,
        "license": "内部研究 · 权利待核验",
        "licenseUrl": POLICY_PAGE,
        "licenseNote": "公开页面可试听不等于开放再发布许可；此文件仅进入内部研究与原型库，词曲、表演及录音权利须另行核验。",
        "retrievedOn": collected_on,
        "bytes": record["bytes"],
        "sha256": record["sha256"],
        "changes": record["collectionMethod"],
        "materials": materials,
    }
    if record.get("sourceTrackId"):
        sample["sourceTrackId"] = record["sourceTrackId"]
    if record.get("versionNote"):
        sample["versionNote"] = record["versionNote"]
    return sample


def as_variant(sample):
    variant = dict(sample)
    variant.pop("id", None)
    variant.pop("materials", None)
    return variant


def main():
    samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    collection = json.loads(COLLECTION_PATH.read_text(encoding="utf-8"))
    collected_on = collection["collectedOn"]
    round2 = [r for r in collection["records"] if r.get("round") == 2]
    if not round2:
        raise ValueError("No round-2 collection records found")

    by_id = {s["id"]: s for s in samples}
    by_work = {}
    for record in round2:
        for work_id in record["ids"]:
            by_work.setdefault(work_id, []).append(record)

    for work_id, records in by_work.items():
        existing = by_id.get(work_id)
        if existing is None:
            raise ValueError(f"Unknown work ID in round-2 collection: {work_id}")
        if existing.get("sampleType") != "generated":
            # 幂等重跑：已被替换过，只补 variant
            if not any(r["role"] == "variant" for r in records):
                continue
        else:
            primaries = [r for r in records if r["role"] == "primary"]
            if len(primaries) != 1:
                raise ValueError(f"Expected exactly one primary for {work_id}, got {len(primaries)}")
            primary = make_sample(primaries[0], work_id, existing["materials"], collected_on)
            by_id[work_id] = primary
        primary = by_id[work_id]
        variants = [v for v in primary.get("variants", []) if v["file"] not in {r["file"] for r in records if r["role"] == "variant"}]
        for record in records:
            if record["role"] != "variant":
                continue
            variants.append(as_variant(make_sample(record, work_id, primary["materials"], collected_on)))
        if variants:
            primary["variants"] = variants
        else:
            primary.pop("variants", None)

    updated = [by_id[s["id"]] for s in samples]
    if len(updated) != 58:
        raise ValueError(f"Expected 58 work entries, got {len(updated)}")
    # 所有采集记录都必须能在 samples 的主录音或 variants 里找到
    referenced = {(s["id"], s["file"]) for s in updated}
    referenced |= {(s["id"], v["file"]) for s in updated for v in s.get("variants", [])}
    expected = {(work_id, r["file"]) for r in collection["records"] for work_id in r["ids"]}
    missing = expected - referenced
    if missing:
        raise ValueError(f"Collection records not wired into samples: {sorted(missing)}")
    counts = Counter(s.get("sampleType", "open") for s in updated)
    versions = sum(1 + len(s.get("variants", [])) for s in updated)
    SAMPLES_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "samples": len(updated),
        "versions": versions,
        "counts": dict(counts),
        "round2Works": len(by_work),
        "round2Files": len(round2),
        "collectionFiles": collection["fileCount"],
        "collectionMappings": collection["workMappingCount"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
