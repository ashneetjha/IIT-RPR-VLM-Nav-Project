# IIT-RPR-VLM-Nav-Project

## UAV Vision-Language Model Research and Real-Time Navigation

Research repository for UAV Vision-Language Model (VLM) data infrastructure, visual grounding, and multimodal training preparation conducted as part of the IIT Ropar research project.

## Pipeline

```text
UAV Dataset Discovery
        ↓
Dataset Inspection
        ↓
Data Conversion / Annotation Restructuring
        ↓
Visual Grounding Validation
        ↓
UAV123 / MM-UAVBench Investigation
        ↓
Unified Grounding Representation
        ↓
InternVL Training Preparation
Task 1

Task 1 covers:

UAVIT-1M data inspection and conversion
Qwen3-VL-compatible multimodal data preparation
SkyFind referring-expression grounding
Bounding-box and expression extraction
Grounding JSONL generation
Dataset validation and statistics

See Task-1/.

Task 2

Task 2 covers:

UAV123 dataset acquisition and structural investigation
Sequence/frame mapping
Bounding-box format verification
Visual bounding-box validation
UAV123 annotation/attribute investigation
MM-UAVBench dataset investigation

See Task-2/.

Current Grounding Target

The intended unified grounding sample is:

Image + Language Expression/Command + Bounding Box

The repository intentionally excludes large raw datasets, local virtual environments, model checkpoints, and other machine-specific files.

Research Progress
Completed
UAVIT-1M data infrastructure and conversion
SkyFind grounding restructuring
UAV123 acquisition and annotation validation
UAV123 frame/bounding-box correspondence validation
Initial MM-UAVBench investigation
In Progress
MM-UAVBench grounding-subset identification
Cross-dataset normalization
InternVL training-data preparation
InternVL training-script validation
