# scripts/dataset_stats.py

from datasets import load_dataset
from collections import Counter
import re

dataset = load_dataset(
    "ZhanYang-nwpu/UAVIT-1M",
    split="train",
    streaming=True
)

counter = Counter()

for i, sample in enumerate(dataset):

    text = sample["conversations"][0]["value"]

    tags = re.findall(r"\[(.*?)\]", text)

    for tag in tags:
        counter[tag] += 1

    if i % 50000 == 0:
        print(i)

    if i >= 200000:
        break

print("\nTASK DISTRIBUTION")
for k, v in counter.items():
    print(k, v)