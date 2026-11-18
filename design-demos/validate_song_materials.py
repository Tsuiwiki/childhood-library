import json
from collections import Counter
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent
SAMPLES = json.loads((ROOT / "audio" / "samples.json").read_text(encoding="utf-8"))
FULL_SAMPLES = [sample for sample in SAMPLES if sample.get("sampleType") != "generated" and sample["materials"].get("score")]
OUT = ROOT / "shots-songs"
EXPECTED = {
    "EN-T01": {"measures": 12, "divisions": 4, "notes": "C4 C4 G4 G4 A4 A4 G4 F4 F4 E4 E4 D4 D4 C4 G4 G4 F4 F4 E4 E4 D4 G4 G4 F4 F4 E4 E4 D4 C4 C4 G4 G4 A4 A4 G4 F4 F4 E4 E4 D4 D4 C4"},
    "EN-T02": {"measures": 8, "divisions": 4, "notes": "E4 D4 C4 D4 E4 E4 E4 D4 D4 D4 E4 G4 G4 E4 D4 C4 D4 E4 E4 E4 E4 D4 D4 E4 D4 C4"},
    "EN-T03": {"measures": 4, "divisions": 12, "notes": "C4 C4 C4 D4 E4 E4 D4 E4 F4 G4 C5 C5 C5 G4 G4 G4 E4 E4 E4 C4 C4 C4 G4 F4 E4 D4 C4"},
    "CN-T01": {"measures": 8, "divisions": 4, "notes": "E4 G4 A4 G4 E4 D4 E4 G4 A4 C5 A4 G4 E4 D4 E4 G4 A4 C5 A4 G4 E4 D4 E4 G4 E4 D4 E4 C4"},
    "CN-C28": {"measures": 10, "divisions": 4, "notes": "C4 E4 G4 E4 F4 A4 G4 E4 G4 A4 G4 E4 D4 C4 G4 A4 C5 A4 G4 E4 D4 E4 G4 A4 G4 E4 D4 E4 D4 E4 G4 E4 D4 E4 C4"},
    "CN-C26": {"measures": 8, "divisions": 4, "notes": "G4 G4 A4 G4 E4 E4 D4 G4 A4 C5 A4 G4 E4 D4 E4 E4 G4 A4 G4 E4 D4 C4 D4 E4 G4 E4 D4 C4"},
    "CN-C01": {"measures": 12, "divisions": 4, "notes": "A4 C5 D5 E5 G5 E5 C5 D5 C5 A4 C5 A4 C5 D5 E5 G5 G5 A5 G5 E5 D5 E5 E5 G5 A5 G5 E5 D5 C5 D5 E5 G5 E5 D5 C5 D5 E5 C5 A4 D5 E5 C5"},
    "CN-C03": {"measures": 12, "divisions": 4, "notes": "E4 G4 C5 A4 G4 E4 G4 E4 A4 C5 G4 C5 E5 D5 D5 C5 D5 C5 A4 C5 G4 E4 E4 G4 A4 C5 A4 G4 E4 G4 A4 C5 D5 E5 D5 C5 D5 C5 A4 G4 E4 D4 C4"},
    "CN-C10": {"measures": 16, "divisions": 4, "notes": "A3 A3 C4 D4 E4 G4 E4 D4 D4 D4 E4 G4 G4 E4 A3 A3 C4 D4 E4 G4 E4 D4 D4 D4 E4 G4 G4 A4 C5 C5 C5 C5 C5 C5 B4 C5 C5 C5 C5 D5 D5 C5 C5 C5 C5 C5 C5 C5 B4 D5 D5 D5 E5 D5 C5 A4"},
}


def normalized_lyrics(value: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9\u3400-\u9fff]", value)).casefold()


def validate_source_files() -> None:
    for sample in FULL_SAMPLES:
        work_id = sample["id"]
        materials = sample["materials"]
        svg_roots = {}
        for key in ("cover", "score"):
            root = ET.parse(ROOT / materials[key]).getroot()
            assert root.tag.endswith("svg"), f"Not SVG: {materials[key]}"
            svg_roots[key] = root
        score_root = ET.parse(ROOT / materials["scoreSource"]).getroot()
        measures = score_root.findall("./part/measure")
        expected = EXPECTED.get(work_id) or sample.get("engraving")
        assert expected, f"Missing engraving expectation: {work_id}"
        assert len(measures) == expected["measures"]
        pitches = []
        verses = {}
        lyric_counts = Counter()
        for measure in measures:
            notes = measure.findall("note")
            durations = sum(int(note.findtext("duration")) for note in notes)
            assert durations == expected["divisions"] * 4, f"Bad measure duration: {work_id} bar {measure.attrib['number']}"
            for note in notes:
                pitches.append(f"{note.findtext('pitch/step')}{note.findtext('pitch/octave')}")
                for lyric in note.findall("lyric"):
                    number = lyric.attrib["number"]
                    text = lyric.findtext("text")
                    assert text and lyric.findtext("syllabic") in {"single", "begin", "middle", "end"}
                    verses.setdefault(number, []).append(text)
                    lyric_counts[text] += 1
        expected_pitches = expected["notes"].split()
        pitch_cursor = 0
        for pitch in pitches:
            if pitch_cursor < len(expected_pitches) and pitch == expected_pitches[pitch_cursor]:
                pitch_cursor += 1
        assert pitch_cursor == len(expected_pitches), f"Original pitch sequence is not preserved: {work_id}"
        assert verses, f"No engraved lyrics: {work_id}"
        engraved = "".join("".join(verses[number]) for number in sorted(verses, key=int))
        assert normalized_lyrics(engraved) == normalized_lyrics("".join(materials["lyrics"])), f"MusicXML does not contain the complete lyrics: {work_id}"
        svg_counts = Counter(text.strip() for text in svg_roots["score"].itertext() if text.strip())
        missing_svg_lyrics = {
            text: count - svg_counts[text]
            for text, count in lyric_counts.items()
            if svg_counts[text] < count
        }
        assert not missing_svg_lyrics, f"SVG score is missing rendered lyrics: {work_id}: {missing_svg_lyrics}"


def assert_no_horizontal_overflow(page, label: str) -> None:
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"{label}: page overflow"
    dialog_fits = page.evaluate(
        "document.getElementById('work-dialog').scrollWidth <= document.getElementById('work-dialog').clientWidth + 1"
    )
    assert dialog_fits, f"{label}: dialog overflow"


def open_materials(page, work_id: str) -> None:
    page.locator("#catalogue-search").fill(work_id)
    card = page.locator(f'.work-card[data-work-id="{work_id}"]')
    card.locator(".detail-button:not(.audio-action)").click()
    expect(page.locator("#work-dialog")).to_be_visible()
    expect(page.locator("#song-materials")).to_be_visible()
    page.wait_for_function(
        "document.getElementById('song-cover').naturalWidth > 0 && document.getElementById('song-score').naturalWidth > 0"
    )


def main() -> None:
    validate_source_files()
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        console_errors = []
        page_errors = []
        external_requests = []
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("request", lambda request: external_requests.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        try:
            page.goto((ROOT / "works.html").as_uri(), wait_until="load")
            page.wait_for_function("document.body.dataset.audioReady === 'true'")
            page.locator("#show-samples").click()
            expect(page.locator(".sample-card-cover")).to_have_count(min(9, len(SAMPLES)))
            expect(page.locator("#sample-audio-count")).to_have_text(str(len(SAMPLES)))
            page.wait_for_function("Array.from(document.querySelectorAll('.sample-card-cover')).every(image => image.complete && image.naturalWidth > 0)")
            card_ratios = page.locator(".sample-card-cover").evaluate_all("images => images.map(image => { const rect = image.getBoundingClientRect(); return rect.width / rect.height; })")
            assert all(1.28 < ratio < 1.38 for ratio in card_ratios), f"Card covers are cropped or stretched: {card_ratios}"
            assert_no_horizontal_overflow(page, "desktop cards")

            for sample in FULL_SAMPLES:
                work_id = sample["id"]
                materials = sample["materials"]
                open_materials(page, work_id)
                assert "dialog-with-materials" in (page.locator("#work-dialog").get_attribute("class") or "")
                expect(page.locator("#lyrics-title")).to_have_text(materials["lyricsTitle"])
                expect(page.locator("#song-lyrics p")).to_have_count(len(materials["lyrics"]))
                assert page.locator("#song-lyrics p").all_text_contents() == materials["lyrics"]
                expect(page.locator("#lyrics-note")).to_have_text(materials["lyricsNote"])
                expect(page.locator("#score-title")).to_have_text(materials["scoreTitle"])
                expect(page.locator("#score-note")).to_contain_text("完整歌词已嵌入 MusicXML")
                expect(page.locator("#song-cover")).to_have_attribute("alt", materials["coverAlt"])
                cover_ratio = page.locator("#song-cover").evaluate("image => { const rect = image.getBoundingClientRect(); return rect.width / rect.height; }")
                assert 1.28 < cover_ratio < 1.38, f"Detail cover is cropped or stretched: {work_id} ratio {cover_ratio}"
                assert page.locator("#song-cover").get_attribute("src") == materials["cover"]
                assert page.locator("#song-score").get_attribute("src") == materials["score"]
                for selector, key in (("#cover-download", "cover"), ("#score-svg-download", "score"), ("#score-source-download", "scoreSource")):
                    link = page.locator(selector)
                    assert link.get_attribute("href") == materials[key]
                    assert link.get_attribute("download") is not None
                assert_no_horizontal_overflow(page, f"desktop {work_id}")
                page.locator("#song-materials").evaluate("element => element.scrollIntoView({block: 'start'})")
                page.screenshot(path=str(OUT / f"{work_id}-materials-desktop.png"))
                page.locator("#score-scroll").evaluate("element => element.scrollIntoView({block: 'center'})")
                page.screenshot(path=str(OUT / f"{work_id}-score-desktop.png"))
                page.keyboard.press("Escape")
                expect(page.locator("#work-dialog")).to_be_hidden()

            page.set_viewport_size({"width": 375, "height": 812})
            for sample in FULL_SAMPLES:
                work_id = sample["id"]
                open_materials(page, work_id)
                assert_no_horizontal_overflow(page, f"mobile {work_id}")
                scrolling = page.evaluate(
                    """() => {
                      const region = document.getElementById('score-scroll');
                      const before = region.scrollLeft;
                      region.scrollLeft = 160;
                      return {canScroll: region.scrollWidth > region.clientWidth, before, after: region.scrollLeft};
                    }"""
                )
                assert scrolling["canScroll"] and scrolling["after"] > 0, f"Score region cannot scroll: {work_id}"
                page.locator("#song-materials").evaluate("element => element.scrollIntoView({block: 'start'})")
                page.screenshot(path=str(OUT / f"{work_id}-materials-mobile.png"))
                page.locator("#score-scroll").evaluate("element => { element.scrollLeft = 0; element.scrollIntoView({block: 'center'}); }")
                page.screenshot(path=str(OUT / f"{work_id}-score-mobile.png"))
                page.keyboard.press("Escape")

            page.locator("#show-samples").click()
            page.locator("#catalogue-search").fill("CN-C02")
            page.locator('.work-card[data-work-id="CN-C02"] .detail-button:not(.audio-action)').click()
            expect(page.locator("#song-materials")).to_be_visible()
            expect(page.locator("#score-sheet")).to_be_hidden()
            assert "dialog-with-materials" in (page.locator("#work-dialog").get_attribute("class") or "")
            page.keyboard.press("Escape")

            assert not console_errors, f"Console errors: {console_errors}"
            assert not page_errors, f"Page errors: {page_errors}"
            assert not external_requests, f"Unexpected external requests: {external_requests}"
            print(f"PASS validate_song_materials.py: {len(FULL_SAMPLES)} covers, {len(FULL_SAMPLES)} MusicXML sources, {len(FULL_SAMPLES)} engraved scores; original pitch sequences and durations; complete multi-verse lyrics embedded in MusicXML and rendered in SVG; downloads; desktop/mobile scrolling; non-sample fallback; no console/page/external-network errors")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
