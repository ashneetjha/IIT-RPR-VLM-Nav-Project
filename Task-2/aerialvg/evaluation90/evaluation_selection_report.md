# AerialVG 90-Image Evaluation Selection

- Source file: `aerialvg/annotation/vg_test_odvg.jsonl`
- Source record count: 4723
- Final evaluation count: 90
- Category counts: long_caption=30, short_caption=30, complex_relational=30
- Reused Phase 1 count: 30
- Newly added count: 60
- Selection criteria: long captions are at least 100 characters; short captions are at most 75 characters; complex relational records have at least 3 regions, at least 2 explicit relations, or at least 3 spatial relation words.
- Duplicate prevention: filenames and normalized captions are unique globally.
- Caption normalization: lowercase captions with non-word runs replaced by spaces.
- Selection is deterministic and reuses all valid Phase 1 records before category-specific ranking fills the quotas.
- Download source: `IPEC-COMMUNITY/AerialVG`, `images/<filename>`.
- Local image count: 90/90
- VERIFIED count: 30
- PENDING count: 60

Grounding DINO not started.

GLIP not started.

This is the 90-image evaluation preparation stage.
