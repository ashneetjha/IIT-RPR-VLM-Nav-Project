from datasets import load_dataset

dataset = load_dataset(
    "ZhanYang-nwpu/UAVIT-1M",
    split="train",
    streaming=True
)

max_len = 0

for i, sample in enumerate(dataset):

    conv_len = len(sample["conversations"])

    if conv_len > max_len:
        max_len = conv_len
        print(f"New max: {max_len}")

    if i >= 100000:
        break

print("\nMaximum conversation length:", max_len)