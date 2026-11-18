# -*- coding: utf-8 -*-
"""三馆与研究层回归：链接完整性、统一导航、五维状态、目录筛选、详情回链、移动端、控制台。"""
from __future__ import annotations

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "library-content.json").read_text(encoding="utf-8"))
SPECIALTIES = json.loads((ROOT / "specialties.json").read_text(encoding="utf-8"))

SPEC_KEYS = [
    "childhood", "nature", "play", "lullaby",
    "classical", "world", "forgotten", "original",
]
PAGES = [
    "dir-3.html", "music.html", "story.html", "poetry.html",
    "research.html", "works.html",
] + [f"specialty-{key}.html" for key in SPEC_KEYS]
SPECIALTY_PAGES = [f"specialty-{key}.html" for key in SPEC_KEYS]
NAV_HREFS = ["dir-3.html", "story.html", "music.html", "poetry.html", "research.html", "works.html"]


def check_data():
    records = DATA["records"]
    assert len(records) == 160, f"expected 160 research records, got {len(records)}"
    assert DATA["stats"]["story"]["total"] == 100
    assert DATA["stats"]["poetry"]["total"] == 60
    assert DATA["stats"]["story"]["topics"] == 15, "15 editorial topics, not 15 works"
    assert DATA["stats"]["poetry"]["assets"] == 12, "12 version/asset clues, not 12 works"
    assert sum(1 for g in DATA["groups"] if g["hall"] == "story") == 9
    assert sum(1 for g in DATA["groups"] if g["hall"] == "poetry") == 10
    fields = ["researchStatus", "rightsStatus", "qualityStatus", "accessMethod", "publicationStatus"]
    ids = set()
    for r in records:
        assert r["id"] not in ids, f"duplicate id {r['id']}"
        ids.add(r["id"])
        for f in fields:
            assert r.get(f), f"{r['id']} missing {f}"
        assert r["sourceUrl"], f"{r['id']} missing source clue"
        assert r["rightsStatus"] != "verified", f"{r['id']} rights verified without evidence archive"
        assert r["publicationStatus"] == "draft", f"{r['id']} is not a research draft"
        assert r["qualityStatus"] == "unreviewed", f"{r['id']} quality not reviewed yet"
    assert len(DATA["statusModel"]) == 5
    return len(records)


def check_links():
    broken = []
    total = 0
    for f in sorted(ROOT.glob("*.html")):
        for href in re.findall(r'href="([^"]+)"', f.read_text(encoding="utf-8")):
            if href.startswith(("#", "http", "mailto:", "data:", "javascript:")):
                continue
            clean = href.split("#")[0].split("?")[0]
            if not clean or "'" in clean or "+" in clean:
                continue
            total += 1
            if not (ROOT / clean).resolve().exists():
                broken.append((f.name, href))
    assert not broken, f"broken local links: {broken}"
    return total


def new_page(browser, errors, viewport=None):
    page = browser.new_page(viewport=viewport or {"width": 1440, "height": 900})
    page.on("console", lambda msg, box=errors: box.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc, box=errors: box.append(str(exc)))
    return page


def main():
    record_count = check_data()
    link_count = check_links()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1) 全站统一导航 + 全站地图 + 控制台 / 溢出
        for name in PAGES:
            errors = []
            page = new_page(browser, errors)
            page.goto((ROOT / name).as_uri(), wait_until="load")
            page.wait_for_timeout(120)
            assert page.locator(".desktop-nav a").count() == 6, f"{name}: desktop nav"
            for href in NAV_HREFS:
                assert page.locator(f'.desktop-nav a[href="{href}"]').count() == 1, f"{name}: nav {href}"
            assert page.locator(".lib-map .lib-hall").count() == 4, f"{name}: three halls + research"
            assert page.locator(".lib-specs a").count() == 8, f"{name}: eight specialty links"
            assert page.locator('.lib-map a[href="../docs/PROJECT_PRINCIPLES.md"]').count() == 1, f"{name}: principles link"
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{name}: desktop overflow"
            assert not errors, f"{name}: console errors {errors}"
            page.close()

        # 2) 八个专题页横向串联
        for name in SPECIALTY_PAGES:
            errors = []
            page = new_page(browser, errors)
            page.goto((ROOT / name).as_uri(), wait_until="load")
            assert page.locator(".lib-peer-list a").count() == 8, f"{name}: peer list"
            assert page.locator('.lib-peer-list a[aria-current="page"]').count() == 1, f"{name}: current peer"
            assert page.locator(".lib-peer-ends a").count() == 2, f"{name}: prev/next"
            assert page.locator('.crumb a[href="music.html"]').count() >= 1, f"{name}: back to music hall"
            assert not errors, f"{name}: console errors {errors}"
            page.close()

        # 3) 故事馆目录与筛选
        errors = []
        page = new_page(browser, errors)
        page.goto((ROOT / "story.html").as_uri(), wait_until="load")
        assert page.locator(".rec-card").count() == 100, "story records"
        assert page.locator("[data-group-section]").count() == 9, "story groups"
        assert "100 / 100" in page.locator("#hall-visible").inner_text()
        page.locator("#hall-search").fill("女娲")
        page.wait_for_timeout(80)
        assert page.locator(".rec-card:visible").count() == 2, "search 女娲"
        assert "2 / 100" in page.locator("#hall-visible").inner_text()
        page.locator("#hall-search").fill("")
        page.locator("#hall-group").select_option("myth")
        page.wait_for_timeout(80)
        assert page.locator(".rec-card:visible").count() == 15, "myth group filter"
        assert page.locator("[data-group-section]:visible").count() == 1, "other groups hidden"
        page.locator("#hall-group").select_option("all")
        page.wait_for_timeout(80)
        assert page.locator(".rec-card:visible").count() == 100, "reset filter"
        first = page.locator(".rec-card").first
        first.locator("summary").click()
        status_keys = first.locator(".status-list dt").all_inner_texts()
        assert status_keys == [
            "research_status", "rights_status", "quality_status", "access_method", "publication_status",
        ], f"five-dimension status list: {status_keys}"
        assert "权利待核验" in first.inner_text(), "rights pending label"
        assert not errors, f"story.html: console errors {errors}"
        page.close()

        # 4) 古诗词馆
        errors = []
        page = new_page(browser, errors)
        page.goto((ROOT / "poetry.html").as_uri(), wait_until="load")
        assert page.locator(".rec-card").count() == 60, "poetry records"
        assert page.locator("[data-group-section]").count() == 10, "poetry groups"
        assert "60 / 60" in page.locator("#hall-visible").inner_text()
        assert "版本 / 资产线索" in page.locator(".rec-card").nth(48).inner_text(), "asset-layer card"
        assert not errors, f"poetry.html: console errors {errors}"
        page.close()

        # 5) 研究资源库
        errors = []
        page = new_page(browser, errors)
        page.goto((ROOT / "research.html").as_uri(), wait_until="load")
        assert page.locator(".layer").count() == 2, "research / library layers"
        model_rows = page.locator("#model tbody tr").count()
        assert model_rows == 5, f"five-dimension model table: {model_rows}"
        assert page.locator(".dash-cell").count() == 8, "dashboard cells"
        assert page.locator(".flow li").count() == 8, "workflow steps"
        assert page.locator("#sources-title").count() == 1, "source clues"
        dash_text = page.locator("#dashboard").inner_text()
        # 统计随每轮真实录音替换变化，期望值一律由数据文件实时计算，避免写死数字造成假失败
        from collections import Counter
        samples = json.loads((ROOT / "audio" / "samples.json").read_text(encoding="utf-8"))
        collection = json.loads((ROOT / "audio" / "public-recording-collection.json").read_text(encoding="utf-8"))
        versions = sum(1 + len(s.get("variants", [])) for s in samples)
        types = Counter(s.get("sampleType", "open") for s in samples)
        generated_count = types.get("generated", 0)
        for expected in (
            "105", "100 + 60",
            f"{len(samples)} / {versions}",
            f"{collection['fileCount']} / {collection['workMappingCount']}",
            f"{types.get('internal', 0)} / {generated_count} / {types.get('open', 0)}",
        ):
            assert expected in dash_text, f"dashboard missing {expected}"
        boundary_text = page.locator("#boundary").inner_text()
        assert str(generated_count) in boundary_text and "非原曲" in boundary_text, "generated audio boundary"
        assert "DATA_MODEL.md" in boundary_text, "data model divergence note"
        replacement_text = page.locator("#replacement").inner_text()
        assert page.locator("#replacement tbody tr").count() == 3, "replacement clue groups"
        assert f"剩余 {generated_count} 首" in replacement_text, "replacement progress heading"
        assert "找不到的不硬配" in replacement_text, "no-substitution rule"
        # 世界经典 47 条资料卡全补齐，但音频一律「待采集」，不得硬配合成音
        world_records = json.loads((ROOT / "world-materials.json").read_text(encoding="utf-8"))
        world_clues = json.loads((ROOT / "world-audio-clues.json").read_text(encoding="utf-8"))
        assert len(world_records) == 47, "47 world material records"
        assert all(r["audioStatus"] == "待采集" and r["hasAudio"] is False for r in world_records), "world audio pending"
        assert all((ROOT / r["cover"]).is_file() for r in world_records), "world cover files"
        chinese_materials = json.loads((ROOT / "china-materials.json").read_text(encoding="utf-8"))
        assert str(len(chinese_materials) + len(world_records)) in dash_text, "total material cards on dashboard"
        world_text = page.locator("#world-pending").inner_text()
        assert f"{len(world_records)} 条已补齐" in world_text, "world material completion heading"
        assert "真实录音待采集" in world_text and "找不到的不硬配" in world_text, "world no-substitution rule"
        assert page.locator("#world-pending tbody tr").count() == len(world_clues["verifiedCandidates"]), "world audio clue rows"
        assert not errors, f"research.html: console errors {errors}"
        page.close()

        # 6) 作品详情 -> 所属专题反向回链
        sample_id = next(
            w["id"] for w in SPECIALTIES["works"] if w.get("specialties")
        )
        expected_keys = next(
            w["specialties"] for w in SPECIALTIES["works"] if w["id"] == sample_id
        )
        errors = []
        page = new_page(browser, errors)
        page.goto((ROOT / "works.html").as_uri() + f"#work-{sample_id}", wait_until="load")
        page.wait_for_timeout(180)
        nav = page.locator("#work-spec-links")
        assert nav.count() == 1, "work spec links container"
        assert nav.get_attribute("hidden") is None, f"{sample_id}: spec links should show"
        links = page.locator("#work-spec-link-list a")
        assert links.count() == len(expected_keys), f"{sample_id}: specialty link count"
        for key in expected_keys:
            assert page.locator(f'#work-spec-link-list a[href="specialty-{key}.html"]').count() == 1
        page.evaluate("location.hash = ''")
        page.wait_for_timeout(120)
        assert nav.get_attribute("hidden") is not None, "cleared hash hides spec links"
        assert not errors, f"works.html: console errors {errors}"
        page.close()

        # 7) 移动端
        for name in ("dir-3.html", "music.html", "story.html", "poetry.html", "research.html", "works.html", "specialty-childhood.html"):
            errors = []
            page = new_page(browser, errors, {"width": 375, "height": 812})
            page.goto((ROOT / name).as_uri(), wait_until="load")
            page.wait_for_timeout(120)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{name}: mobile overflow"
            menu = page.locator("#menu-toggle:visible").first
            menu.click()
            assert menu.get_attribute("aria-expanded") == "true", f"{name}: mobile menu"
            assert page.locator('.mobile-nav a[href="research.html"]:visible').count() == 1, f"{name}: mobile nav"
            assert not errors, f"{name}: mobile console errors {errors}"
            page.close()

        browser.close()

    print(json.dumps({
        "result": "PASS",
        "records": record_count,
        "localLinksChecked": link_count,
        "pagesChecked": len(PAGES),
        "specialtyPages": len(SPECIALTY_PAGES),
        "checks": "data model, local links, unified nav, site map, specialty peers, hall filters, five-dimension status, research dashboard, work->spec back links, mobile, console",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
