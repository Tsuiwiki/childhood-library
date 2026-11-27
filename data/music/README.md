# Music data

This is the normalized, machine-readable music dataset. Existing source files remain in place during this first consolidation pass.

## Files and current counts

- `works.json`: 105 indexed works from `design-demos/specialties.json`.
- `recordings.json`: 230 references: 62 prototype sample records, 27 public recording collection records, 5 official preview links, and 136 external audio/video/album/archive links.
- `lyrics.json`: 61 lyric/version records: 14 references into the legacy sample file plus 47 source-attributed traditional nursery-rhyme text records.
- `scores.json`: 14 score/material references.

## Data rules

- `workId` / `workIds` links each material or recording reference to a work.
- Different recordings and regional/textual variants remain separate records.
- External links are navigation references, not locally stored audio and not proof of playback availability.
- Generated demos and instrumental renderings are not authentic recordings of the named traditional song.
- Legacy lyrics are referenced in place rather than duplicated here; the original source file remains unchanged.
- The `publicDomainClaim` field records the source dataset's classification only. Verify the specific text/version and applicable jurisdiction before public use; it says nothing about recordings or arrangements.
- `file`, `displayAsset`, and `sourceAsset` are preserved references. Their presence does not guarantee a file exists at that path or is publicly distributable.
- Rights statements are retained from source records. Public accessibility is not automatic redistribution permission.
- Any `reviewFlags` / `mappingStatus` must be resolved before treating a recording as definitively linked to a work.

## Source snapshot

Normalized from:
- `design-demos/specialties.json`
- `design-demos/audio/samples.json`
- `design-demos/audio/public-recording-collection.json`
- `design-demos/audio/official-recordings.json`
- `design-demos/world-lyrics-sources.json`
- `web/src/research/audioLinks.ts`

This is a data consolidation, not a claim that all entries are fully verified or ready for public release.
