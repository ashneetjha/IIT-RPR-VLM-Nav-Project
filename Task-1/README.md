# Task 1 — UAV VLM Data Infrastructure

Task 1 focused on UAV dataset investigation, multimodal data conversion, and visual-grounding data restructuring.

## UAVIT-1M

The `sky_find_2` pipeline:

- Streams UAVIT-1M from Hugging Face.
- Inspects dataset structure and task types.
- Converts records into a Qwen3-VL-compatible JSONL format.
- Produces dataset statistics and conversion reports.

Main script:

`sky_find_2/scripts/convert_uavit_to_qwen.py`

## SkyFind

The `skyfind_pipeline` project processes referring-expression grounding data.

It extracts:

- image identifiers
- bounding boxes
- referring expressions

and creates grounding records in the form:

```json
{
  "image_id": "...",
  "bbox": [x1, y1, x2, y2],
  "expression": "..."
}

The processing follows the one-object-per-grounding-sample principle.

Main scripts:

src/task1_grounding_restructure.py
src/validate_grounding_dataset.py
src/dataset_statistics.py
Status

Task 1 contains the completed dataset-processing and grounding-restructuring work used as the foundation for the subsequent UAV123/MM-UAVBench and InternVL investigation.
