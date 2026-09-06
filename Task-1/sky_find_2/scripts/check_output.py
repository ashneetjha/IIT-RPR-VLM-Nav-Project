import json

with open(
    "output/uavit_qwen_1k.jsonl",
    "r",
    encoding="utf-8"
) as f:

    for i, line in enumerate(f):

        obj = json.loads(line)

        print(f"\n===== RECORD {i+1} =====")
        print(json.dumps(obj, indent=2, ensure_ascii=False))

        if i == 2:
            break