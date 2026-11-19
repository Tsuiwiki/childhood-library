#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only asset inventory for Childhood Library.

Generates docs/reports/asset-inventory.md and .json.
Never modifies, moves or deletes any media file.

Usage (from repository root):
    python scripts/asset_inventory.py
"""
from __future__ import annotations

import hashlib
import json
import wave
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMOS = ROOT / "design-demos"
AUDIO_DIR = DEMOS / "audio"
REPORT_DIR = ROOT / "docs" / "reports"

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".oga", ".opus", ".aac", ".webm", ".mp4"}
SCAN_EXTS = AUDIO_EXTS | {".png", ".jpg", ".jpeg", ".webp", ".svg", ".musicxml", ".json", ".html", ".py", ".md"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def duration_seconds(path: Path):
    """Best-effort duration probe; returns None when no decoder is available."""
    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as w:
                rate = w.getframerate()
                return round(w.getnframes() / float(rate), 2) if rate else None
        except Exception:
            pass
    try:
        import av  # optional dependency (PyAV)

        with av.open(str(path)) as container:
            if container.duration:
                return round(container.duration / 1_000_000, 2)
            for stream in container.streams.audio:
                if stream.duration and stream.time_base:
                    return round(float(stream.duration * stream.time_base), 2)
    except Exception:
        pass
    return None


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    samples = load_json(AUDIO_DIR / "samples.json")
    official = load_json(AUDIO_DIR / "official-recordings.json")
    collection = load_json(AUDIO_DIR / "public-recording-collection.json")
    world = load_json(DEMOS / "world-materials.json")
    specialties = load_json(DEMOS / "specialties.json")

    refs = []
    for row in samples:
        if row.get("file"):
            refs.append(row["file"])
        for variant in row.get("variants", []):
            if variant.get("file"):
                refs.append(variant["file"])
    ref_names = sorted({Path(r).name for r in refs})

    audio_files = sorted(
        p for p in AUDIO_DIR.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    )
    actual_names = {p.name for p in audio_files}

    missing = sorted(set(ref_names) - actual_names)
    orphans = sorted(actual_names - set(ref_names))
    no_type = [r.get("id") for r in samples if not r.get("sampleType")]
    type_counts = Counter(r.get("sampleType") or "MISSING" for r in samples)

    type_by_name = {}
    for row in samples:
        for f in [row.get("file")] + [v.get("file") for v in row.get("variants", [])]:
            if f:
                type_by_name.setdefault(Path(f).name, row.get("sampleType") or "MISSING")

    audio_rows = []
    for p in audio_files:
        audio_rows.append(
            {
                "file": p.name,
                "path": rel(p),
                "ext": p.suffix.lower(),
                "bytes": p.stat().st_size,
                "sha256": sha256(p),
                "duration_seconds": duration_seconds(p),
                "referenced": p.name in ref_names,
                "sampleType": type_by_name.get(p.name),
            }
        )

    ext_counts = Counter()
    for p in DEMOS.rglob("*"):
        if p.is_file() and p.suffix.lower() in SCAN_EXTS and "__pycache__" not in p.parts:
            ext_counts[p.suffix.lower()] += 1

    summary = {
        "generatedOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scope": "local design-demos working tree (GitHub main excludes binary media via .gitignore)",
        "mode": "read-only; no media file was modified, moved or deleted",
        "sampleEntries": len(samples),
        "recordingVersions": len(refs),
        "uniqueAudioReferences": len(ref_names),
        "actualAudioFiles": len(audio_files),
        "missingReferences": len(missing),
        "orphanFiles": len(orphans),
        "entriesWithoutSampleType": len(no_type),
        "sampleTypeCounts": dict(sorted(type_counts.items())),
        "officialPreviews": len(official),
        "researchCollectionFiles": collection.get("fileCount"),
        "researchCollectionMappings": collection.get("workMappingCount"),
        "worldMaterials": len(world),
        "worldAudioPending": sum(1 for m in world if m.get("audioStatus") == "待采集"),
        "catalogWorks": len(specialties.get("works", [])),
        "extensionCounts": dict(sorted(ext_counts.items())),
    }

    payload = {
        "summary": summary,
        "audio": audio_rows,
        "missingReferences": missing,
        "orphanFiles": orphans,
        "entriesWithoutSampleType": no_type,
    }
    (REPORT_DIR / "asset-inventory.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# 资产与媒体完整性清单",
        "",
        f"- 生成时间：{summary['generatedOn']}",
        f"- 范围：{summary['scope']}",
        f"- 方式：{summary['mode']}",
        "- 生成脚本：`scripts/asset_inventory.py`（可重复执行，输出本文件与同名 `.json`）",
        "",
        "> 本清单只记录**本地工作区**资产。GitHub `main` 通过 `.gitignore` 排除全部二进制媒体，"
        "`design-demos/audio/` 在公开仓库中只有 JSON 清单。配置引用 ≠ 实际媒体文件；"
        "实际媒体文件 ≠ 已获公开播放、下载或分发授权。",
        "",
        "## 1. 汇总",
        "",
        "| 指标 | 数值 |",
        "| --- | ---: |",
    ]
    for key, label in [
        ("sampleEntries", "试听配置条目"),
        ("recordingVersions", "录音版本（含 variants）"),
        ("uniqueAudioReferences", "唯一音频文件名引用"),
        ("actualAudioFiles", "本地真实音频文件"),
        ("missingReferences", "引用缺失文件"),
        ("orphanFiles", "未被引用孤儿文件"),
        ("entriesWithoutSampleType", "缺少 sampleType 的条目"),
        ("officialPreviews", "官方短时预览配置"),
        ("researchCollectionFiles", "内部研究采集登记文件"),
        ("researchCollectionMappings", "采集记录作品映射"),
        ("worldMaterials", "世界经典资料卡"),
        ("worldAudioPending", "世界经典音频待采集"),
        ("catalogWorks", "作品发现目录条目"),
    ]:
        lines.append(f"| {label} | {summary[key]} |")

    lines += [
        "",
        "**资源类型分布**："
        + "、".join(f"`{k}` {v}" for k, v in summary["sampleTypeCounts"].items())
        + "。",
        "",
        "**文件类型分布**（`design-demos/` 递归，不含 `__pycache__`）："
        + "、".join(f"`{k}` {v}" for k, v in summary["extensionCounts"].items())
        + "。",
        "",
        "## 2. 基线断言",
        "",
        "| 断言 | 期望 | 实测 | 结果 |",
        "| --- | ---: | ---: | --- |",
    ]
    checks = [
        ("唯一音频引用", 62, summary["uniqueAudioReferences"]),
        ("本地真实音频文件", 85, summary["actualAudioFiles"]),
        ("引用缺失文件", 0, summary["missingReferences"]),
        ("孤儿文件", 23, summary["orphanFiles"]),
        ("缺少 sampleType", 3, summary["entriesWithoutSampleType"]),
        ("世界经典音频待采集", 47, summary["worldAudioPending"]),
    ]
    for label, expected, actual in checks:
        lines.append(f"| {label} | {expected} | {actual} | {'PASS' if actual == expected else 'CHECK'} |")

    lines += [
        "",
        "> 期望值来自 Phase 0 审计基线；若后续采集导致数字变化，应同步更新本报告、"
        "`DEVELOPMENT_STATUS.md` 与 `DATA_MIGRATION_PLAN.md`，不要静默漂移。",
        "",
        "## 3. 引用中的音频文件（含校验和）",
        "",
        "| 文件 | 类型 | 大小 (KB) | 时长 (s) | SHA-256 (前 12 位) |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for r in audio_rows:
        if not r["referenced"]:
            continue
        dur = "-" if r["duration_seconds"] is None else f"{r['duration_seconds']:.2f}"
        lines.append(
            f"| `{r['file']}` | {r['sampleType']} | {r['bytes'] / 1024:.1f} | {dur} | `{r['sha256'][:12]}` |"
        )

    lines += [
        "",
        "完整 SHA-256、字节数、时长与路径见 `asset-inventory.json`。时长为尽力探测："
        "WAV 使用标准库读取，其余格式在 PyAV 可用时探测；无解码器时记 `-`，不猜测。",
        "",
        "## 4. 孤儿文件（未被任何试听配置引用）",
        "",
        "| 文件 | 大小 (KB) | SHA-256 (前 12 位) |",
        "| --- | ---: | --- |",
    ]
    by_name = {r["file"]: r for r in audio_rows}
    for name in orphans:
        r = by_name[name]
        lines.append(f"| `{name}` | {r['bytes'] / 1024:.1f} | `{r['sha256'][:12]}` |")

    lines += [
        "",
        "> 孤儿文件在迁移报告中单列，由人工判断归档或淘汰，**不自动删除**。",
        "",
        "## 5. 数据完整性缺口",
        "",
        f"- 缺少 `sampleType` 的条目：{', '.join(f'`{i}`' for i in no_type) or '无'}。"
        "迁移前须按 `MUSIC_LIBRARY_IMPLEMENTATION_PLAN.md` §6 的五类资源补齐，不得猜测。",
        f"- 引用缺失文件：{len(missing)} 个" + (f"（{', '.join(missing)}）" if missing else "。"),
        "- 27 个 `internal` 研究录音保持「权利待核验」，只登记在研究层；"
        "21 个 `generated` 是程序合成示范音，页面标注「非原曲」。",
        "- 47 条世界经典音频全部「真实录音待采集」，不硬配合成音冒充原曲。",
        "",
        "## 6. 与迁移的关系",
        "",
        "本清单是 `DATA_MIGRATION_PLAN.md` §5 完整性校验的输入：导入后须复核数量、关联、"
        "孤儿、重复、权利分布与发布门禁；媒体文件按 `import_batch_id` 登记，只增不删，可按批次回滚。",
        "",
    ]
    (REPORT_DIR / "asset-inventory.md").write_text("\n".join(lines), encoding="utf-8")

    print("asset inventory written:", REPORT_DIR / "asset-inventory.md")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for label, expected, actual in checks:
        if actual != expected:
            print(f"BASELINE CHECK: {label} expected {expected}, got {actual}")


if __name__ == "__main__":
    main()
