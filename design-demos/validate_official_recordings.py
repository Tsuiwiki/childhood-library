import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent
RECORDINGS = json.loads((ROOT / "audio" / "official-recordings.json").read_text(encoding="utf-8"))
OUT = ROOT / "shots-official-audio"


def wait_for_official_metadata(page) -> None:
    page.wait_for_function(
        """() => {
          const audio = document.getElementById('official-audio-element');
          return audio.readyState >= 1 && audio.duration > 25 && audio.duration < 31 && audio.paused;
        }""",
        timeout=45000,
    )
    expect(page.locator("#official-audio-element")).to_be_visible()
    expect(page.locator("#official-audio-status")).to_contain_text("再次点击")


def wait_for_official_playback(page) -> None:
    page.wait_for_function(
        """() => {
          const audio = document.getElementById('official-audio-element');
          return audio.readyState >= 2 && audio.duration > 25 && audio.duration < 31 && !audio.paused;
        }""",
        timeout=45000,
    )
    expect(page.locator("#official-audio-element")).to_be_visible()
    expect(page.locator("#official-audio-status")).to_contain_text("正在播放官方 30 秒原录音")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        external_requests = []
        page_errors = []
        page.on("request", lambda request: external_requests.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        statuses = {}
        durations = {}
        try:
            page.goto((ROOT / "works.html").as_uri(), wait_until="load")
            page.wait_for_function("document.body.dataset.audioReady === 'true'")
            expect(page.locator("#official-audio-count")).to_have_text(str(len(RECORDINGS)))
            expect(page.locator("#official-audio-frame")).to_have_count(0)
            assert not page.locator("#official-audio-element").get_attribute("src")
            assert not external_requests, f"Official audio must not load by default: {external_requests}"

            for index, recording in enumerate(RECORDINGS):
                print(f"Checking {recording['id']} {recording['trackTitle']}", flush=True)
                page.locator("#catalogue-search").fill(recording["id"])
                card = page.locator(f'.work-card[data-work-id="{recording["id"]}"]')
                expect(card.locator(".official-marker")).to_contain_text("官方发行录音")
                card.locator(".audio-action").click()
                expect(page.locator("#work-dialog")).to_be_visible()
                expect(page.locator("#official-audio-panel")).to_be_visible()
                expect(page.locator("#official-audio-description")).to_contain_text(recording["trackTitle"])
                expect(page.locator("#official-audio-description")).to_contain_text(recording["versionNote"])
                expect(page.locator("#official-source-link")).to_have_attribute("href", recording["sourcePage"])
                assert not any(url.startswith(recording["apiUrl"]) for url in external_requests), f"Opening details must not request this recording: {recording['id']}"

                with page.expect_response(
                    lambda response, url=recording["apiUrl"]: response.url.startswith(url),
                    timeout=45000,
                ) as response_info:
                    page.locator("#official-audio-load").click()
                response = response_info.value
                statuses[recording["id"]] = response.status
                assert response.status < 400, f"API HTTP error for {recording['id']}: {response.status}"
                wait_for_official_metadata(page)
                page.locator("#official-audio-load").click()
                wait_for_official_playback(page)
                duration = page.locator("#official-audio-element").evaluate("audio => audio.duration")
                durations[recording["id"]] = round(duration, 3)
                source = page.locator("#official-audio-element").get_attribute("src")
                assert source.startswith("https://cdnt-preview.dzcdn.net/"), f"Unexpected official preview source: {source}"
                expect(page.locator("#official-audio-status")).to_contain_text("正在播放官方 30 秒原录音")
                if index == 0:
                    page.screenshot(path=str(OUT / "official-recording-desktop.png"), full_page=True)
                page.keyboard.press("Escape")
                expect(page.locator("#work-dialog")).to_be_hidden()
                page.wait_for_function("!document.getElementById('official-audio-element').getAttribute('src')")

            page.set_viewport_size({"width": 375, "height": 812})
            page.locator("#catalogue-search").fill("CN-C19")
            page.locator('.work-card[data-work-id="CN-C19"] .audio-action').click()
            expect(page.locator("#official-audio-panel")).to_be_visible()
            page.locator("#official-audio-load").click()
            wait_for_official_metadata(page)
            page.locator("#official-audio-load").click()
            wait_for_official_playback(page)
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "mobile official recording panel overflow"
            page.screenshot(path=str(OUT / "official-recording-mobile.png"), full_page=True)
            page.keyboard.press("Escape")
            page.wait_for_function("!document.getElementById('official-audio-element').getAttribute('src')")
            assert not page_errors, f"Page errors: {page_errors}"
            print(
                f"PASS validate_official_recordings.py: {len(RECORDINGS)} official Deezer previews decoded and played; "
                f"click-to-request only, exact track identity, API statuses {statuses}; decoded durations {durations}; "
                "official HTTPS preview hosts, source/version/limits, close cleanup, desktop/mobile"
            )
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
