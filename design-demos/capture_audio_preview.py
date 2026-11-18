import os
import wave
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "shots-audio"
OUT.mkdir(exist_ok=True)
TEST_WAV = OUT / "CN-C01.wav"

with wave.open(str(TEST_WAV), "wb") as stream:
    stream.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
    stream.writeframes(b"\0\0" * 8000)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto((ROOT / "works.html").as_uri(), wait_until="load")
        page.locator("#audio-batch-input").set_input_files(str(TEST_WAV))
        page.wait_for_function("document.getElementById('internal-audio-count').textContent === '1'")
        page.locator('.work-card[data-work-id="CN-C01"] [data-audio-play]').click()
        page.locator("#results-title").evaluate("(e) => e.scrollIntoView()")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "audio-player-desktop.png"))
        page.set_viewport_size({"width": 375, "height": 812})
        page.locator("#results-title").evaluate("(e) => e.scrollIntoView()")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "audio-player-mobile.png"))
        browser.close()
finally:
    if TEST_WAV.exists():
        os.unlink(TEST_WAV)
