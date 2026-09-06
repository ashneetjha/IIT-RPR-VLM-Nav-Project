# UAVIT-1M → Qwen3-VL Training Format Conversion

## Overview

This project implements a scalable data conversion pipeline for transforming the UAVIT-1M vision-language dataset from its native Hugging Face schema into the training format required by Qwen3-VL.

The implementation uses Hugging Face streaming to process the dataset directly from the Hub without downloading the original dataset locally.

---

## Objective

Convert all records from the UAVIT-1M dataset into Qwen3-VL compatible JSONL format while:

- Avoiding local dataset downloads
- Supporting large-scale datasets efficiently
- Preserving image-text relationships
- Maintaining compatibility with Qwen3-VL fine-tuning pipelines
- Generating output in JSONL format for efficient downstream training

---

## Dataset Information

Dataset:

```
ZhanYang-nwpu/UAVIT-1M
```

Source:

Hugging Face Hub

Dataset Size:

```
1,240,666 samples
```

Dataset Format:

```json
{
    "id": "...",
    "image": "...",
    "conversations": [
        {
            "from": "human",
            "value": "<image> ..."
        },
        {
            "from": "gpt",
            "value": "..."
        }
    ]
}
```

---

## Task Analysis

During dataset inspection, the following task categories were identified:

| Task Type | Description |
|------------|------------|
| img_cls | Image Classification |
| deta_cap | Detailed Captioning |
| img_cap | Image Captioning |
| deta_cls | Detailed Classification |
| count | Counting Tasks |

Conversation structure was found to be:

```
Human → GPT
```

Maximum conversation length observed:

```
2 messages
```

---

## Conversion Strategy

The pipeline performs the following steps:

1. Stream records directly from Hugging Face.
2. Read image path information.
3. Extract human prompt.
4. Extract GPT response.
5. Convert to Qwen3-VL message format.
6. Write output as JSONL.

No original dataset files are downloaded locally.

---

## Input Format

Example UAVIT-1M record:

```json
{
    "id": "Harvesting/Tra_Harvesting_047_080.jpg",
    "image": "ERA/train/Harvesting/Tra_Harvesting_047_080.jpg",
    "conversations": [
        {
            "from": "human",
            "value": "<image>\n[img_cls] Classify the image..."
        },
        {
            "from": "gpt",
            "value": "harvesting"
        }
    ]
}
```

---

## Output Format

Example Qwen3-VL record:

```json
{
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": "ERA/train/Harvesting/Tra_Harvesting_047_080.jpg"
                },
                {
                    "type": "text",
                    "text": "[img_cls] Classify the image..."
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "harvesting"
                }
            ]
        }
    ]
}
```

---

## Project Structure

```
sky_find_2/
│
├── output/
│   ├── uavit_qwen_full.jsonl
│   ├── conversion_report.txt
│
├── logs/
│   ├── progress.txt
│   ├── errors.log
│
├── samples/
│   ├── schema_notes.txt
│
├── scripts/
│   ├── inspect_dataset.py
│   ├── task_type_scan.py
│   ├── dataset_stats.py
│   ├── conversation_stats.py
│   ├── convert_uavit_to_qwen.py
│   └── check_output.py
│
└── README.md
```

---

## Execution

Install dependencies:

```bash
pip install datasets tqdm
```

Run conversion:

```bash
python scripts/convert_uavit_to_qwen.py
```

---

## Results

Conversion completed successfully.

| Metric | Value |
|----------|----------|
| Records Processed | 1,240,666 |
| Errors | 0 |
| Runtime | 10.13 Minutes |
| Output Format | JSONL |
| Dataset Download | Not Required |
| Streaming Enabled | Yes |

---

## Generated Files

### Dataset Output

```
output/uavit_qwen_full.jsonl
```

Contains all converted Qwen3-VL training records.

### Conversion Report

```
output/conversion_report.txt
```

Contains runtime and processing statistics.

### Error Log

```
logs/errors.log
```

Records any conversion failures.

---

## Key Features

- Hugging Face streaming support
- Zero dataset download requirement
- Large-scale dataset processing
- Qwen3-VL compatible output
- JSONL generation
- Error tracking
- Progress monitoring
- Reproducible pipeline

---

## Future Work

- Direct integration with Qwen3-VL training pipeline
- Dynamic image loading from Hugging Face
- Dataset sharding for distributed training
- Multi-GPU fine-tuning support
- Integration with Qwen3-VL processors and trainers

---

## Status

Completed.

Successfully converted the entire UAVIT-1M dataset into Qwen3-VL compatible JSONL format with zero conversion errors.