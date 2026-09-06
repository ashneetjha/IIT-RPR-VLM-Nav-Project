# UAVIT-1M Conversion Results

## Dataset

UAVIT-1M

Source:

https://huggingface.co/datasets/ZhanYang-nwpu/UAVIT-1M

---

## Conversion Objective

Convert UAVIT-1M dataset records into Qwen3-VL training format.

---

## Processing Strategy

- Hugging Face Streaming
- Direct JSONL Generation
- No Dataset Download
- Qwen3-VL Compatible Format

---

## Runtime Statistics

| Metric | Value |
|----------|----------|
| Records Processed | 1,240,666 |
| Errors | 0 |
| Runtime | 10.13 Minutes |

---

## Validation Procedure

1. Dataset schema inspection
2. Task-type discovery
3. Conversation structure analysis
4. 1K sample conversion
5. 10K sample conversion
6. Full dataset conversion
7. Output verification

---

## Task Categories Found

- img_cls
- img_cap
- deta_cap
- deta_cls
- count

---

## Generated Artifacts

```text
uavit_qwen_full.jsonl
conversion_report.txt
uavit_analysis.txt
```

---

## Conclusion

The entire UAVIT-1M dataset was successfully transformed into Qwen3-VL training format using a streaming conversion pipeline.

All records were processed successfully with zero conversion errors.