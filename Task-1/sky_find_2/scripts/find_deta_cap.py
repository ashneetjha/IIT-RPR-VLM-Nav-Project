from datasets import load_dataset

dataset = load_dataset(
    "ZhanYang-nwpu/UAVIT-1M",
    split="train",
    streaming=True
)

for sample in dataset:

    text = sample["conversations"][0]["value"]

    if "[deta_cap]" in text:

        print(sample)
        break