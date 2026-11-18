import hashlib
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"
OUT = ROOT / "shots-audio"
SAMPLES = json.loads((AUDIO_DIR / "samples.json").read_text(encoding="utf-8"))
OFFICIAL_IDS = {item["id"] for item in json.loads((AUDIO_DIR / "official-recordings.json").read_text(encoding="utf-8"))}


def assert_no_horizontal_overflow(page, label: str) -> None:
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"{label}: horizontal overflow"


def wait_until_ready(page) -> None:
    page.wait_for_function("document.body.dataset.audioReady === 'true'")


def recording_versions(sample):
    return [sample, *sample.get("variants", [])]


def play_sample(page, work_id: str, filename: str | None = None) -> None:
    sample = next(item for item in SAMPLES if item["id"] == work_id)
    versions = recording_versions(sample)
    recording = next(item for item in versions if item["file"] == filename) if filename else sample
    card = page.locator(f'.work-card[data-work-id="{work_id}"]')
    expect(card).to_have_count(1)
    if filename is None and work_id not in OFFICIAL_IDS:
        card.locator(".audio-action").click()
    else:
        card.locator(".detail-button:not(.audio-action)").click()
        expect(page.locator("#work-dialog")).to_be_visible()
        if len(versions) > 1:
            page.locator("#sample-version").select_option(str(versions.index(recording)))
        page.locator("#sample-audio-play").click()
        page.keyboard.press("Escape")
        expect(page.locator("#work-dialog")).to_be_hidden()
    expect(page.locator("#audio-player")).to_be_visible()
    page.wait_for_function(
        """() => {
          const audio = document.getElementById('audio-element');
          return audio.readyState >= 2 && audio.duration > 1 && !audio.paused;
        }"""
    )
    expect(page.locator("#player-error")).to_be_hidden()
    expected_kicker = "内部经典录音" if recording.get("sampleType") == "internal" else "原创播放示范 · 非原曲" if recording.get("sampleType") == "generated" else "开放许可 / 原创示范"
    expect(page.locator("#player-kicker")).to_contain_text(expected_kicker)


def main() -> None:
    for sample in SAMPLES:
        for recording in recording_versions(sample):
            audio_path = AUDIO_DIR / recording["file"]
            payload = audio_path.read_bytes()
            assert len(payload) == recording["bytes"], f"Size mismatch: {recording['file']}"
            assert hashlib.sha256(payload).hexdigest() == recording["sha256"], f"SHA256 mismatch: {recording['file']}"

    OUT.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        console_errors = []
        page_errors = []
        network_requests = []
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("request", lambda request: network_requests.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        try:
            page.goto((ROOT / "works.html").as_uri(), wait_until="load")
            wait_until_ready(page)
            expect(page.locator("#sample-audio-count")).to_have_text(str(len(SAMPLES)))
            expect(page.locator("#internal-audio-count")).to_have_text("0")
            assert not page.locator("#audio-element").get_attribute("src"), "Samples must not autoplay or preload a src"

            page.locator("#show-samples").click()
            expect(page.locator("#show-samples")).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#filtered-count")).to_have_text(str(len(SAMPLES)))
            expect(page.locator(".work-card")).to_have_count(min(9, len(SAMPLES)))
            actual_ids = page.locator(".work-card").evaluate_all("cards => cards.map(card => card.dataset.workId).sort()")
            assert actual_ids == sorted(sample["id"] for sample in SAMPLES)[:9]
            assert_no_horizontal_overflow(page, "1440x900 sample catalogue")

            for index, sample in enumerate(SAMPLES):
                versions = recording_versions(sample)
                page.locator("#catalogue-search").fill(sample["id"])
                card = page.locator(f'.work-card[data-work-id="{sample["id"]}"]')
                if sample["id"] in OFFICIAL_IDS:
                    expect(card.locator(".official-marker")).to_contain_text("官方发行录音")
                else:
                    expect(card.locator(".sample-marker")).to_contain_text(sample["license"])
                card.locator(".detail-button:not(.audio-action)").click()
                expect(page.locator("#sample-audio-panel")).to_be_visible()
                expect(page.locator("#sample-version option")).to_have_count(len(versions))
                expect(page.locator("#sample-version-field")).to_be_visible() if len(versions) > 1 else expect(page.locator("#sample-version-field")).to_be_hidden()
                for version_index, recording in enumerate(versions):
                    if len(versions) > 1:
                        page.locator("#sample-version").select_option(str(version_index))
                    expected_title = "内部经典录音 · 权利待核验" if recording.get("sampleType") == "internal" else "原创播放示范 · 非原曲" if recording.get("sampleType") == "generated" else "开放许可 / 原创示范"
                    expect(page.locator("#sample-audio-title")).to_have_text(expected_title)
                    expect(page.locator("#sample-audio-meta")).to_contain_text(recording["author"])
                    expect(page.locator("#sample-audio-meta")).to_contain_text(recording["license"])
                    expect(page.locator("#sample-source-link")).to_have_attribute("href", recording["sourcePage"])
                    expect(page.locator("#sample-license-link")).to_have_attribute("href", recording["licenseUrl"])
                    expect(page.locator("#sample-audio-panel")).to_have_attribute("data-selected-file", recording["file"])
                page.keyboard.press("Escape")
                expect(page.locator("#work-dialog")).to_be_hidden()

                for recording in versions:
                    play_sample(page, sample["id"], recording["file"])
                    duration = page.locator("#audio-element").evaluate("audio => audio.duration")
                    assert 1 < duration < 300, f"Unexpected decoded duration for {sample['id']} {recording['file']}: {duration}"
                    if recording.get("durationSeconds"):
                        assert abs(duration - recording["durationSeconds"]) < 0.2, f"Duration metadata mismatch: {recording['file']}"
                    source = page.locator("#audio-element").get_attribute("src")
                    assert source == f"audio/{recording['file']}" or source.endswith(f"/audio/{recording['file']}"), f"Unexpected sample source: {source}"
                    if index == 0 and recording["file"] == sample["file"]:
                        page.locator("#results-title").evaluate("element => element.scrollIntoView()")
                        page.screenshot(path=str(OUT / "open-samples-desktop.png"))
                    page.locator("#audio-player-close").click()
                    expect(page.locator("#audio-player")).to_be_hidden()
                    assert not page.locator("#audio-element").get_attribute("src")

            page.set_viewport_size({"width": 375, "height": 812})
            page.locator("#catalogue-search").fill(SAMPLES[0]["id"])
            play_sample(page, SAMPLES[0]["id"])
            assert_no_horizontal_overflow(page, "375x812 sample player")
            spacing = page.evaluate(
                """() => ({
                  padding: parseFloat(getComputedStyle(document.body).paddingBottom),
                  playerHeight: document.getElementById('audio-player').getBoundingClientRect().height
                })"""
            )
            assert spacing["padding"] >= spacing["playerHeight"], "Mobile body padding must clear the sample player"
            page.locator("#results-title").evaluate("element => element.scrollIntoView()")
            page.screenshot(path=str(OUT / "open-samples-mobile.png"))

            assert not console_errors, f"Console errors: {console_errors}"
            assert not page_errors, f"Page errors: {page_errors}"
            assert not network_requests, f"Unexpected external requests: {network_requests}"
            version_count = sum(len(recording_versions(sample)) for sample in SAMPLES)
            print(
                f"PASS validate_samples.py: {len(SAMPLES)} work entries / {version_count} MP3/WAV/M4A/FLAC/MP4-audio versions decoded and played; "
                "SHA256, duration, version selector, attribution/source/license links, desktop/mobile layout, no console/page/external-network errors"
            )
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
