from datasets import load_dataset
import json
from tqdm import tqdm
import time
import os

print("Loading UAVIT-1M...")

dataset = load_dataset(
    "ZhanYang-nwpu/UAVIT-1M",
    split="train",
    streaming=True
)

os.makedirs("output", exist_ok=True)
os.makedirs("logs", exist_ok=True)

output_file = "output/uavit_qwen_full.jsonl"
report_file = "output/conversion_report.txt"
progress_file = "logs/progress.txt"
error_file = "logs/errors.log"

count = 0
errors = 0

start_time = time.time()

with open(output_file, "w", encoding="utf-8") as fout, \
     open(error_file, "w", encoding="utf-8") as ferr:

    for sample in tqdm(dataset, desc="Converting"):

        try:

            image_path = sample.get("image", "")
            conversations = sample.get("conversations", [])

            if len(conversations) < 2:
                continue

            human_msg = ""
            assistant_msg = ""

            for msg in conversations:

                role = msg.get("from", "")
                value = msg.get("value", "")

                if role == "human":
                    human_msg = value

                elif role == "gpt":
                    assistant_msg = value

            if not human_msg or not assistant_msg:
                continue

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
                                "text": human_msg.replace("<image>\n", "").strip()
                            }
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": assistant_msg.strip()
                            }
                        ]
                    }
                ]
            }

            fout.write(
                json.dumps(
                    qwen_record,
                    ensure_ascii=False
                ) + "\n"
            )

            count += 1

            if count % 50000 == 0:

                elapsed = (time.time() - start_time) / 60

                print(
                    f"\nProcessed {count:,} "
                    f"| Errors: {errors} "
                    f"| Runtime: {elapsed:.2f} min"
                )

                fout.flush()

                with open(progress_file, "w") as p:
                    p.write(str(count))

        except Exception as e:

            errors += 1

            ferr.write(f"{count}: {str(e)}\n")

            if errors <= 20:
                print(f"ERROR: {e}")

end_time = time.time()

runtime_minutes = (end_time - start_time) / 60

with open(report_file, "w", encoding="utf-8") as report:

    report.write(
        f"Dataset: UAVIT-1M\n"
        f"Output Format: Qwen3-VL JSONL\n\n"
        f"Converted Records: {count}\n"
        f"Errors: {errors}\n"
        f"Runtime (minutes): {runtime_minutes:.2f}\n"
        f"Output File: {output_file}\n"
    )

print("\n==============================")
print("CONVERSION COMPLETE")
print("==============================")
print(f"Records Converted : {count:,}")
print(f"Errors            : {errors}")
print(f"Runtime           : {runtime_minutes:.2f} minutes")
print(f"Output            : {output_file}")
print(f"Report            : {report_file}")
print(f"Error Log         : {error_file}")