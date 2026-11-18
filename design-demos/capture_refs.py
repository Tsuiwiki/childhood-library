from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "refs"
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page.goto("https://www.booktrust.org.uk", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(5000)
    try:
        page.get_by_text("I Accept Cookies", exact=True).first.click(force=True)
    except Exception:
        pass
    page.wait_for_timeout(1000)
    page.keyboard.press("Escape")
    for selector in ["button[aria-label='Close']", "button[title='Close']", ".modal-close", ".close"]:
        try:
            for button in page.locator(selector).all():
                if button.is_visible():
                    button.click(force=True)
        except Exception:
            pass
    page.wait_for_timeout(2000)
    page.screenshot(path=str(OUT / "booktrust-clean.png"), full_page=False)
    browser.close()
