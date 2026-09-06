from datasets import load_dataset
import json

dataset = load_dataset(
    "ZhanYang-nwpu/UAVIT-1M",
    split="train",
    streaming=True
)

sample = next(iter(dataset))

image_path = sample["image"]

human_msg = sample["conversations"][0]["value"]
assistant_msg = sample["conversations"][1]["value"]

qwen_record = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image_path
                },
                {
                    "type": "text",
                    "text": human_msg.replace("<image>\n", "")
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": assistant_msg
                }
            ]
        }
    ]
}

print(json.dumps(qwen_record, indent=2))