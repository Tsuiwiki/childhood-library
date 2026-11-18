from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
FILES = [ROOT / f"dir-{i}.html" for i in range(1, 4)]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for file in FILES:
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(file.as_uri(), wait_until="load")
        page.wait_for_timeout(900)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "desktop overflow"

        if file.name == "dir-3.html":
            assert page.locator(".collection-tab").count() == 4, "all/story/music/poetry entries"
            assert page.locator(".tab-story").inner_text().find("故事馆") >= 0
            assert page.locator(".tab-music").inner_text().find("音乐馆") >= 0
            assert page.locator(".tab-poetry").inner_text().find("古诗词馆") >= 0
            assert page.locator('a[href="music.html"]').count() >= 1, "music hall link"
            assert page.locator("audio").count() == 0, "no audio on homepage"
        else:
            page.locator("#tab-poetry").click()
            assert page.locator('[data-search]:visible').count() == 2, "poetry filter"
            search = page.locator('input[type="search"]:visible')
            search.fill("李白")
            page.wait_for_timeout(100)
            assert page.locator('[data-search]:visible').count() == 1, "search filter"
            search.fill("不存在的原型条目")
            page.wait_for_timeout(100)
            assert page.locator('[data-search]:visible').count() == 0, "empty result"
            search.fill("")
            page.locator("#tab-all").click()
            assert page.locator('[data-search]:visible').count() == 4, "reset filter"

            card = page.locator('[data-search]:visible').first
            trigger = card.locator("button").first if card.locator("button").count() else card
            trigger.click()
            assert page.locator("dialog").is_visible(), "dialog opens"
            page.keyboard.press("Escape")
            assert not page.locator("dialog").is_visible(), "dialog closes with Escape"

        page.set_viewport_size({"width": 375, "height": 812})
        page.reload(wait_until="load")
        page.wait_for_timeout(500)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "mobile overflow"
        menu = page.locator("#menu-toggle:visible, .menu-button:visible").first
        menu.click()
        assert menu.get_attribute("aria-expanded") == "true", "mobile menu opens"
        assert not errors, f"console errors: {errors}"
        checks = "three-library entries, music link" if file.name == "dir-3.html" else "filters, search, empty/reset, dialog, Escape"
        print(f"PASS {file.name}: {checks}, mobile menu, overflow, console")
        page.close()
    browser.close()
