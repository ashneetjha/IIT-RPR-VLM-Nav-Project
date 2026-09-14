# AerialVG Phase 1 Report

- Date: 2026-09-15
- Source file: `aerialvg/annotation/vg_test_odvg.jsonl`
- Total records: 4723
- Shortlist size: 30 unique filenames
- Counts: long_caption=10, short_caption=10, complex_relational=10

## Schema discovered

Top-level `filename`, `height`, `width`, `grounding`; `grounding` contains `caption` and `regions`; each region contains `bbox`, `phrase`, and, for anchor regions, `realation` (dataset spelling). No source records were modified.

## Filtering methodology

All 4723 JSONL records were parsed. Caption character length, region count (entity proxy), explicit non-empty `realation` count, and case-insensitive spatial-word count were calculated. Long candidates have length >= 100; short candidates have length <= 75; complex relational candidates have at least 3 regions, at least 2 explicit relations, or at least 3 spatial relation words. Ranking is deterministic and category-specific: long favors length, short favors genuinely short captions while retaining region/spatial signal, and complex favors regions, relations, spatial language, then length.

Ten candidates were selected per category. A global filename set and normalized-caption set prevent duplicate filenames and trivial repeated captions. The source order was not used as the selection criterion.

## Target, anchor, and relation interpretation

The first region is summarized as the Target only when it has no `realation` field/value, matching the observed schema pattern in which later regions carry anchor relationships. All regions remain preserved in the shortlist JSONL. CSV and the manual checklist summarize the first region only when this interpretation is supported; no target was invented otherwise.

## Completed and not completed

Completed: annotation parsing, deterministic candidate filtering, a 30-image candidate shortlist, CSV/JSONL export, manual-verification checklist, local image availability check, and structural validation.

Not completed: visual inspection, manual verification, downloading images, model evaluation, Grounding DINO, and GLIP. This is an LLM-assisted annotation shortlist only, not a visually verified result.

## Exact next step

Obtain the selected image files through the approved dataset access process, open each image, compare the caption and all target/anchor relationships against the annotation, then update only the manual checklist/status fields after human review.

## Reproducibility

```bash
python3 scripts/select_aerialvg_test_shortlist.py
python3 scripts/validate_aerialvg_shortlist.py
```
