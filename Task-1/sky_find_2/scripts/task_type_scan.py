from datasets import load_dataset
import re

dataset = load_dataset(
    "ZhanYang-nwpu/UAVIT-1M",
    split="train",
    streaming=True
)

task_types = set()

for i, sample in enumerate(dataset):

    text = sample["conversations"][0]["value"]

    matches = re.findall(r"\[(.*?)\]", text)

    for m in matches:
        task_types.add(m)

    if i % 10000 == 0:
        print(f"Checked {i} samples")

    if i >= 100000:
        break

print("\nTASK TYPES FOUND:")
for t in sorted(task_types):
    print(t)