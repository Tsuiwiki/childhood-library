from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
PAGE_URL = (ROOT / "works.html").as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.goto(PAGE_URL, wait_until="load")
    page.wait_for_function("document.body.dataset.audioReady === 'true'")

    assert page.locator("#total-count").inner_text() == "105"
    assert page.locator("#filtered-count").inner_text() == "105"
    assert page.locator("#china-count").inner_text() == "55"
    assert page.locator("#sample-audio-count").inner_text() == "58"
    assert page.locator("#official-audio-count").inner_text() == "5"
    assert page.locator("#official-audio-frame").count() == 0
    assert page.locator(".work-card").count() == 9
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "desktop overflow"

    page.get_by_role("button", name="下一页").click()
    assert "第 2 / 12 页" in page.locator("#results-status").inner_text()
    assert page.locator(".work-card").count() == 9

    search = page.locator("#catalogue-search")
    search.fill("让我们荡起双桨")
    assert page.locator("#filtered-count").inner_text() == "1"
    assert page.locator(".work-card h3").inner_text() == "让我们荡起双桨"
    page.locator(".detail-button:not(.audio-action)").click()
    assert page.locator("dialog").is_visible()
    assert page.locator("#dialog-id").inner_text() == "CN-C01"
    source = page.locator("#dialog-source a")
    assert source.count() == 1
    assert source.get_attribute("target") == "_blank"
    assert "noopener" in source.get_attribute("rel")
    page.keyboard.press("Escape")
    assert not page.locator("dialog").is_visible()

    page.locator("#clear-search").click()
    page.locator("#group-filter").select_option("nursery")
    assert page.locator("#filtered-count").inner_text() == "55"
    page.locator("#status-filter").select_option("rights_pending")
    assert page.locator("#filtered-count").inner_text() == "26"
    page.locator("#reset-filters").click()
    assert page.locator("#filtered-count").inner_text() == "105"

    search.fill("绝对不存在的儿歌编号")
    assert page.locator("#no-results").is_visible()
    assert page.locator(".work-card").count() == 0
    page.locator("#empty-reset").click()
    assert page.locator("#filtered-count").inner_text() == "105"

    page.locator("#group-filter").select_option("english")
    assert page.locator("#filtered-count").inner_text() == "50"
    page.locator("#sort-order").select_option("title")
    assert page.locator(".work-card").count() == 9
    page.locator("#reset-filters").click()

    page.goto(f"{PAGE_URL}#work-CN-C29", wait_until="load")
    page.wait_for_function("document.body.dataset.audioReady === 'true'")
    assert page.locator("dialog").is_visible()
    assert page.locator("#dialog-id").inner_text() == "CN-C29"
    assert page.locator("#song-materials").is_visible()
    assert page.locator("#song-lyrics p").count() == 7
    assert page.locator("#score-sheet").is_visible()
    page.keyboard.press("Escape")
    assert not page.locator("dialog").is_visible()

    # 世界经典 47 条资料卡：封面、已核验歌词、来源与「音频待采集」全部可见；
    # 47 张原创 SVG 封面必须能在浏览器里解码，不能只是文件存在。
    import json
    world = json.loads((ROOT / "world-materials.json").read_text(encoding="utf-8"))
    assert len(world) == 47, "47 world material records"
    assert all((ROOT / m["cover"]).is_file() for m in world), "world cover files exist"
    assert all(m["audioStatus"] == "待采集" and m["hasAudio"] is False for m in world), "world audio pending"
    assert all(m["score"] is None and m["scoreSource"] is None for m in world), "no fabricated scores"
    assert all(m["sourceUrl"].startswith("https://") for m in world), "verified HTTPS sources"
    cover_results = page.evaluate("""async (paths) => Promise.all(paths.map(p => new Promise(resolve => {
      const img = new Image();
      img.onload = () => resolve([p, img.naturalWidth > 0]);
      img.onerror = () => resolve([p, false]);
      img.src = p;
    })))""", [m["cover"] for m in world])
    assert all(ok for _, ok in cover_results), f"broken world covers: {[p for p, ok in cover_results if not ok]}"

    first = next(m for m in world if m["id"] == "EN-T04")
    page.goto(f"{PAGE_URL}#work-EN-T04", wait_until="load")
    page.wait_for_function("document.body.dataset.audioReady === 'true'")
    assert page.locator("dialog").is_visible()
    assert page.locator("#dialog-id").inner_text() == "EN-T04"
    assert page.locator("#song-materials").is_visible()
    assert page.locator("#song-cover").get_attribute("src") == first["cover"]
    assert page.locator("#song-lyrics p").count() == len(first["lyrics"])
    assert page.locator("#score-sheet").is_hidden(), "no score without verified melody"
    assert page.locator("#material-sources").is_visible(), "source / rights panel"
    assert page.locator("#material-source-list a").get_attribute("href") == first["sourceUrl"]
    assert "待采集" in page.locator("#dialog-rights").inner_text()
    page.keyboard.press("Escape")

    # 权威来源未刊全文的条目：歌词留白并写明原因，不凭记忆补写
    pending = next(m for m in world if not m["lyrics"])
    page.goto(f"{PAGE_URL}#work-{pending['id']}", wait_until="load")
    page.wait_for_function("document.body.dataset.audioReady === 'true'")
    assert page.locator("#song-lyrics p").count() == 1
    assert "待采集" in page.locator("#song-lyrics p").inner_text()
    assert page.locator("#material-sources").is_visible()
    page.keyboard.press("Escape")

    page.goto(PAGE_URL, wait_until="load")
    page.wait_for_function("document.body.dataset.audioReady === 'true'")
    page.locator("#catalogue-search").fill("Baa, Baa, Black Sheep")
    assert "待采集" in " ".join(page.locator('.work-card[data-work-id="EN-T04"] .audio-marker').all_text_contents())
    assert page.locator('.work-card[data-work-id="EN-T04"] .sample-card-cover').count() == 1
    page.locator("#reset-filters").click()

    for work_id, primary_file, variant_file, author in (
        ("CN-C02", "CN-C02-gxzf.flac", "CN-C02-xuexi-chorus.m4a", "上海菁英少年合唱团"),
        ("CN-C03", "CN-C03-original.mp4", "CN-C03-xuexi-chorus.mp3", "杨宁"),
    ):
        version_page = browser.new_page(viewport={"width": 1440, "height": 900})
        version_page.goto(f"{PAGE_URL}#work-{work_id}", wait_until="load")
        version_page.wait_for_function("document.body.dataset.audioReady === 'true'")
        assert version_page.locator("dialog").is_visible()
        assert version_page.locator("#song-materials").is_visible()
        assert version_page.locator("#song-cover").get_attribute("src") == f"song-assets/{work_id}-cover.svg"
        assert version_page.locator("#sample-version option").count() == 2
        assert version_page.locator("#sample-audio-panel").get_attribute("data-selected-file") == primary_file
        version_page.locator("#sample-version").select_option("1")
        version_page.wait_for_function(f"document.getElementById('sample-audio-panel').dataset.selectedFile === '{variant_file}'")
        assert author in version_page.locator("#sample-audio-meta").inner_text()
        version_page.keyboard.press("Escape")
        assert not version_page.locator("dialog").is_visible()
        version_page.close()

    page.set_viewport_size({"width": 375, "height": 812})
    page.goto(PAGE_URL, wait_until="load")
    page.wait_for_function("document.body.dataset.audioReady === 'true'")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "mobile overflow"
    assert page.locator(".work-card").count() == 9
    menu = page.locator("#menu-toggle")
    menu.click()
    assert menu.get_attribute("aria-expanded") == "true"
    assert page.locator("#mobile-nav").is_visible()
    page.keyboard.press("Escape")
    assert menu.get_attribute("aria-expanded") == "false"

    assert page.locator("audio").count() == 2
    assert not page.locator("#audio-element").get_attribute("src"), "no local audio is bundled or loaded by default"
    assert not page.locator("#official-audio-element").get_attribute("src"), "no official audio is requested by default"
    assert not errors, f"console errors: {errors}"
    import json
    samples = json.loads((ROOT / "audio" / "samples.json").read_text(encoding="utf-8"))
    versions = sum(1 + len(s.get("variants", [])) for s in samples)
    print(f"PASS works.html: 105 entries, {55 + len(world)} material records (55 Chinese / {len(world)} world), {len(world)} covers decoded, {len(world)} audio slots marked pending, {len(samples)} local work entries / {versions} recording versions, 5 official recordings, multi-version selector, pagination, filters, deep links, partial materials, mobile, console")
    page.close()

    home = browser.new_page(viewport={"width": 1440, "height": 900})
    home.goto((ROOT / "dir-3.html").as_uri(), wait_until="load")
    home.locator(".header-cta").click()
    home.wait_for_load_state("load")
    assert home.url.endswith("/works.html")
    assert home.locator("#total-count").inner_text() == "105"
    print("PASS dir-3.html: header CTA opens works.html")
    home.close()
    browser.close()
