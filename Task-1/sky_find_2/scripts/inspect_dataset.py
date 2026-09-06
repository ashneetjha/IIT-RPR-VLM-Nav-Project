from datasets import load_dataset

dataset = load_dataset(
    "ZhanYang-nwpu/UAVIT-1M",
    split="train",
    streaming=True
)

for i, sample in enumerate(dataset):

    print("\n====================")
    print(f"Sample {i+1}")
    print("====================")

    print("ID:")
    print(sample["id"])

    print("\nIMAGE:")
    print(sample["image"])

    print("\nCONVERSATIONS:")
    print(sample["conversations"])

    if i == 9:
        break