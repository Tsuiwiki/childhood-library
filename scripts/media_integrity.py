#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only media integrity / backup-manifest check (T-07, M0).

Compares the flat media directory against docs/reports/asset-inventory.json,
reports checksum drift, missing files and unexpected extra files. It NEVER
modifies, moves or deletes anything; unexpected files are listed for a human.

Usage (from repository root):
    python scripts/media_integrity.py
    python scripts/media_integrity.py --root var/media --json
Exit code 0 = all manifest entries verified; 1 = at least one problem.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.media.integrity import verify_manifest  # noqa: E402

DEFAULT_MANIFEST = ROOT / "docs" / "reports" / "asset-inventory.json"
DEFAULT_ROOT = ROOT / "var" / "media"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()

    root = args.root if args.root.is_absolute() else (ROOT / args.root).resolve()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected = {row["file"]: row["sha256"] for row in payload["audio"]}

    results = verify_manifest(root, expected)
    failures = [item for item in results if not item.ok]

    present = {p.name for p in root.iterdir() if p.is_file()} if root.is_dir() else set()
    extras = sorted(present - set(expected))

    summary = {
        "mode": "read-only",
        "root": str(root),
        "manifest": str(args.manifest),
        "manifest_entries": len(expected),
        "checked": len(results),
        "verified": len(results) - len(failures),
        "failed": len(failures),
        "unexpected_files": extras,
        "failures": [item.as_dict() for item in failures],
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("media integrity (read-only)")
        print("  root:              %s" % root)
        print("  manifest entries:  %d" % len(expected))
        print("  verified:          %d" % (len(results) - len(failures)))
        print("  failed:            %d" % len(failures))
        print("  unexpected files:  %d" % len(extras))
        for name in extras:
            print("    extra: %s (NOT deleted)" % name)
        for item in failures:
            print("    FAIL %s: %s" % (item.object_key, item.message))
        print("  note: extra/orphan files are reported, never removed automatically")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
