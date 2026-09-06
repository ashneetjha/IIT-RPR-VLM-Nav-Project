from datasets import load_dataset

TARGET = "Semantic_151.jpg"

dataset = load_dataset(
    "kunyu241/SkyFind",
    split="train",
    streaming=True
)

for idx, record in enumerate(dataset):

    if record["fileName"] == TARGET:

        print("\nFOUND")
        print(f"Image: {TARGET}")
        print(f"Index: {idx}")
        break