# Task 2 — UAV123 and MM-UAVBench Investigation

Task 2 investigates UAV datasets suitable for multimodal visual grounding and subsequent InternVL training.

## UAV123

Completed work:

- Obtained the UAV123 10 FPS dataset.
- Inspected annotation and image organization.
- Investigated sequence-to-frame mapping using `configSeqs.m`.
- Verified annotation rows contain four values: `x, y, width, height`.
- Verified `group1_2` contains 395 annotations corresponding to frames 445–839.
- Visually validated the bounding box against the corresponding image.
- Investigated UAV123 tracking attributes and annotation semantics.

## Current UAV123 Finding

UAV123 provides tracking bounding-box annotations and sequence information. Native natural-language referring expressions were not established from the inspected annotation files.

Therefore, expressions should not be fabricated merely to force UAV123 into a grounding schema.

## MM-UAVBench

Current dataset source:

https://huggingface.co/datasets/daisq/MM-UAVBench

The dataset is being investigated for grounding-relevant image, language, and region/bounding-box annotations.

## Validation Evidence

Bounding-box validation:

`scripts/check_uav123_bbox.py`

Visual output:

`outputs/uav123_group1_2_frame445_bbox.jpg`

## Next Stage

- Identify grounding-relevant MM-UAVBench annotations.
- Normalize valid image + expression/command + bounding-box samples.
- Prepare the unified representation for InternVL.
- Validate the InternVL training pipeline before server execution.
