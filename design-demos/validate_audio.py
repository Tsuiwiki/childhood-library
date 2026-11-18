import importlib.util
import shutil
import struct
import tempfile
import wave
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent


def build_template_copy(destination: Path) -> None:
    """Build a temporary copy without writing works.html."""
    spec = importlib.util.spec_from_file_location("build_works_for_audio_test", ROOT / "build_works.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    html, entries, _samples, _official_recordings, _materials = module.build_html()
    if len(entries) != 105:
        raise AssertionError(f"Expected 105 catalogue entries, got {len(entries)}")
    destination.write_text(html, encoding="utf-8")


def make_test_wav(path: Path) -> None:
    """Generate one second of silence for media testing; this is not a song."""
    sample_rate = 22050
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(struct.pack("<h", 0) * sample_rate)


def wait_until_ready(page) -> None:
    page.wait_for_function("document.body.dataset.audioReady === 'true'")
    expect(page.locator("#import-audio")).to_be_enabled()


def open_detail(page, work_id: str) -> None:
    if page.locator("#work-dialog").is_visible() and page.locator("#dialog-id").inner_text() == work_id:
        return
    page.locator("#catalogue-search").fill(work_id)
    card = page.locator(f'.work-card[data-work-id="{work_id}"]')
    expect(card).to_have_count(1)
    card.locator(".detail-button:not(.audio-action)").click()
    expect(page.locator("#work-dialog")).to_be_visible()
    expect(page.locator("#dialog-id")).to_have_text(work_id)


def assert_no_horizontal_overflow(page, label: str) -> None:
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"{label}: horizontal overflow"


def run_audio_test(page, temp_dir: Path) -> None:
    single = temp_dir / "single-local-test.wav"
    replacement = temp_dir / "replacement-local-test.wav"
    batch_cn = temp_dir / "CN-C01.wav"
    batch_en = temp_dir / "EN-T01-test.wav"
    unmatched = temp_dir / "UNKNOWN-01.wav"
    for path in (single, replacement, batch_cn, batch_en, unmatched):
        make_test_wav(path)

    page.goto((temp_dir / "works-audio-test.html").as_uri(), wait_until="load")
    wait_until_ready(page)
    expect(page.locator("#total-count")).to_have_text("105")
    expect(page.locator("#internal-audio-count")).to_have_text("0")
    assert page.locator("body").get_attribute("data-audio-storage") == "indexeddb"
    assert_no_horizontal_overflow(page, "1440x900")

    # Add through the detail panel; CN-C01 also has a bundled sample, so its card button plays that sample.
    open_detail(page, "CN-C01")
    page.locator("#detail-audio-input").set_input_files(str(single))
    expect(page.locator("#internal-audio-count")).to_have_text("1")
    expect(page.locator("#detail-audio-file")).to_contain_text(single.name)
    expect(page.locator("#detail-audio-file")).to_contain_text("KB")
    page.keyboard.press("Escape")
    expect(page.locator("#work-dialog")).to_be_hidden()

    # IndexedDB state and derived UI survive a full reload.
    page.reload(wait_until="load")
    wait_until_ready(page)
    expect(page.locator("#internal-audio-count")).to_have_text("1")
    expect(page.locator('.work-card[data-work-id="CN-C01"] .audio-marker')).to_have_text("内部本地音频")

    # A user click creates a Blob URL and the native audio element enters play state.
    open_detail(page, "CN-C01")
    page.evaluate("""
      () => {
        window.__audioPlayEvents = 0;
        document.getElementById('audio-element').addEventListener(
          'play', () => { window.__audioPlayEvents += 1; }, { once: true }
        );
      }
    """)
    page.locator("#detail-audio-play").click()
    expect(page.locator("#audio-player")).to_be_visible()
    page.wait_for_function("""
      () => {
        const audio = document.getElementById('audio-element');
        return audio.src.startsWith('blob:') && window.__audioPlayEvents > 0;
      }
    """)
    page.keyboard.press("Escape")
    expect(page.locator("#work-dialog")).to_be_hidden()
    page.locator("#audio-player-close").click()
    expect(page.locator("#audio-player")).to_be_hidden()
    assert page.locator("#audio-element").get_attribute("src") is None
    assert page.evaluate("document.getElementById('audio-element').paused")

    # Replacement updates the displayed filename without changing the work count.
    open_detail(page, "CN-C01")
    page.locator("#detail-audio-input").set_input_files(str(replacement))
    expect(page.locator("#detail-audio-file")).to_contain_text(replacement.name)
    expect(page.locator("#detail-audio-file")).not_to_contain_text(single.name)
    expect(page.locator("#internal-audio-count")).to_have_text("1")

    page.locator("#detail-audio-remove").click()
    expect(page.locator("#internal-audio-count")).to_have_text("0")
    expect(page.locator("#detail-audio-file")).to_have_text("尚未添加本地音频")
    page.keyboard.press("Escape")
    expect(page.locator("#work-dialog")).to_be_hidden()

    # Batch import matches IDs at filename starts, including a suffix before extension.
    page.locator("#audio-batch-input").set_input_files([str(batch_cn), str(batch_en)])
    expect(page.locator("#internal-audio-count")).to_have_text("2")
    expect(page.locator("#audio-import-status")).to_contain_text("导入成功 2")
    expect(page.locator("#audio-import-status")).to_contain_text("无匹配 0")
    page.locator("#catalogue-search").fill("EN-T01")
    expect(page.locator('.work-card[data-work-id="EN-T01"] .audio-marker')).to_be_visible()

    page.locator("#audio-batch-input").set_input_files(str(unmatched))
    expect(page.locator("#audio-import-status")).to_contain_text("无匹配 1")
    expect(page.locator("#internal-audio-count")).to_have_text("2")

    unsupported = temp_dir / "CN-C01-notes.txt"
    unsupported.write_text("not audio", encoding="utf-8")
    page.locator("#audio-batch-input").set_input_files(str(unsupported))
    expect(page.locator("#audio-import-status")).to_contain_text("格式不支持 1")
    expect(page.locator("#internal-audio-count")).to_have_text("2")

    # Persistence and the open fixed player both fit the mobile viewport.
    page.set_viewport_size({"width": 375, "height": 812})
    page.reload(wait_until="load")
    wait_until_ready(page)
    expect(page.locator("#internal-audio-count")).to_have_text("2")
    assert_no_horizontal_overflow(page, "375x812")
    page.locator("#catalogue-search").fill("CN-C01")
    page.locator('.work-card[data-work-id="CN-C01"] .audio-action').click()
    expect(page.locator("#audio-player")).to_be_visible()
    page.wait_for_function("document.getElementById('audio-element').src.startsWith('blob:')")
    assert_no_horizontal_overflow(page, "375x812 with player")
    spacing = page.evaluate("""
      () => ({
        padding: parseFloat(getComputedStyle(document.body).paddingBottom),
        playerHeight: document.getElementById('audio-player').getBoundingClientRect().height
      })
    """)
    assert spacing["padding"] >= spacing["playerHeight"], "Mobile body padding must clear the fixed player"
    page.keyboard.press("Escape")
    expect(page.locator("#audio-player")).to_be_hidden()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="childhood-library-audio-test-") as temporary:
        temp_dir = Path(temporary)
        build_template_copy(temp_dir / "works-audio-test.html")
        shutil.copytree(ROOT / "audio", temp_dir / "audio")
        shutil.copytree(ROOT / "song-assets", temp_dir / "song-assets")
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
                run_audio_test(page, temp_dir)
                assert not console_errors, f"Console errors: {console_errors}"
                assert not page_errors, f"Page errors: {page_errors}"
                assert not network_requests, f"Unexpected network requests: {network_requests}"
                print(
                    "PASS validate_audio.py: add, IndexedDB reload, Blob playback, replace, remove, "
                    "batch ID matching, unmatched/unsupported feedback, 1440x900, 375x812, no console/page/network errors"
                )
            finally:
                context.close()
                browser.close()
    print("Temporary build copy and one-second test WAV files removed; no test audio was delivered.")


if __name__ == "__main__":
    main()
