# Task 2 — grounding audit and InternVL preparation

Task 2 investigates UAV datasets for multimodal visual grounding and subsequent InternVL training. Raw data remains outside this repository and is never modified by the included tooling.

## UAV123

Completed, reproducible work:

- Obtained the UAV123 10 FPS dataset.
- Inspected annotation and image organization.
- Investigated sequence-to-frame mapping using `configSeqs.m`.
- Verified annotation rows contain four values: `x, y, width, height`.
- Verified `group1_2` contains 395 annotations corresponding to frames 445–839.
- Visually validated the bounding box against the corresponding image.
- Investigated UAV123 tracking attributes and annotation semantics.
- Generated a read-only audit: 123 annotation files, 37,607 rows, 37,885 images, and 91 physical image folders.

## Current UAV123 Finding

UAV123 provides tracking bounding-box annotations and sequence information. Native natural-language referring expressions were not established from the inspected annotation files.

Therefore, expressions should not be fabricated merely to force UAV123 into a grounding schema.

## MM-UAVBench

Current dataset source:

https://huggingface.co/datasets/daisq/MM-UAVBench

Official task JSONs have been inspected without downloading media: 19 tasks / 5,702 records. The release is a multiple-choice benchmark; its available boxes do not establish image + referring-expression + target-bbox supervision. VERIFIED records: **0**. Thirty source records (88 entity-level box candidates) are retained only as `REVIEW_REQUIRED`.

## Validation Evidence

Bounding-box validation:

`scripts/check_uav123_bbox.py`

Visual output:

`outputs/uav123_group1_2_frame445_bbox.jpg`

## Next Stage

- Review `reports/TASK2_MASTER_REPORT.md` and the task inventory.
- Obtain team-approved InternVL release/checkpoint, bbox serialization, server paths, launcher, and training parameters.
- Validate on the GPU server before training. Do not train `REVIEW_REQUIRED` candidates as ground truth.

## Reproduce

```bash
python3 scripts/audit_uav123.py
python3 scripts/inspect_mmuavbench.py
python3 scripts/build_unified_grounding.py
(cd internvl && python3 validate_internvl_config.py)
(cd internvl && python3 dry_run_internvl.py)
```
