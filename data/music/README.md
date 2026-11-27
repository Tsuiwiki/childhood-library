# Music data

This directory is the normalized, machine-readable music dataset for Childhood Library.

## Files

- `works.json`: 105 indexed works from the existing specialty catalogue. A catalogue entry is not proof that audio, lyrics, scores, or rights are complete.
- `recordings.json`: recording/version references consolidated from prototype samples, the public recording collection, and official preview links.
- `lyrics.json`: 14 lyric/version records extracted from the existing sample materials.
- `scores.json`: 14 score/material records extracted from the existing sample materials.

## Data rules

- `workId` / `workIds` links recordings, lyrics, and scores to a work.
- Different recordings and regional/textual variants remain separate records.
- A generated demo or instrumental rendering is not labelled as an authentic recording of the traditional song.
- `file`, `displayAsset`, and `sourceAsset` are preserved references from the old dataset; their presence does not guarantee that a file exists at that path or is publicly distributable.
- Rights statements are copied from source records. Publicly reachable media is not automatically licensed for redistribution.
- Existing files under `design-demos/` remain untouched during this first normalization pass. Do not delete them until application references and local media inventories have been checked.

## Source snapshot

Normalized from:
- `design-demos/specialties.json`
- `design-demos/audio/samples.json`
- `design-demos/audio/public-recording-collection.json`
- `design-demos/audio/official-recordings.json`

This is a data consolidation, not a claim that all entries are fully verified or ready for public release.
