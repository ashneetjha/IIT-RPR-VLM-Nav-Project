# SkyFind Dataset Engineering Pipeline

A modular research-oriented preprocessing pipeline for the SkyFind UAV Vision-Language dataset.

This project was developed as part of the UAV/VLM multimodal research workflow for aerial scene understanding, referring expression grounding, and future multimodal instruction tuning pipelines.

---

# Project Overview

The pipeline performs:

- Unified annotation extraction from the SkyFind dataset
- Structured JSON generation
- Semantic preservation of annotations
- Dynamic image streaming from Hugging Face
- PyTorch-compatible multimodal dataloader preparation
- Lightweight preprocessing validation

The implementation follows the discussed architecture requirements:
- single consolidated JSON
- no per-image JSON fragmentation
- scalable preprocessing workflow
- future fine-tuning compatibility

---

# Features

## Unified Annotation Pipeline
- Extracts:
  - file names
  - bounding boxes
  - referring expressions
- Preserves complete semantic information
- Stores all annotations in one centralized JSON file

## Streaming-Based Dataset Access
- Avoids downloading the full 157GB dataset
- Dynamically streams images from Hugging Face
- Lightweight and scalable

## Modular PyTorch DataLoader
- IterableDataset-based architecture
- Dynamic image loading
- Multimodal batch preparation
- Future-ready for VLM fine-tuning workflows

## Clean Research Engineering Structure
- Modular source organization
- Config-driven execution
- Reusable utility functions
- Minimal and scalable architecture

---

# Folder Structure

```text
skyfind_pipeline/
│
├── data/
│   └── unified_annotations_sample.json
│
├── src/
│   ├── config.py
│   ├── utils.py
│   ├── extract_annotations.py
│   └── dataloader.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── test_pipeline.py