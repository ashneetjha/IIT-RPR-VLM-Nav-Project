import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data")

FILES = [
    "grounding_train.jsonl",
    "grounding_validation.jsonl",
    "grounding_test.jsonl",
    "grounding_train_aug.jsonl"
]

REPORT_FILE = DATA_DIR / "dataset_statistics.txt"


def process_file(file_path):

    image_sample_count = defaultdict(int)

    total_samples = 0

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            record = json.loads(line)

            image_id = record["image_id"]

            image_sample_count[image_id] += 1

            total_samples += 1

    unique_images = len(image_sample_count)

    avg_samples = (
        total_samples / unique_images
        if unique_images
        else 0
    )

    min_samples = (
        min(image_sample_count.values())
        if image_sample_count
        else 0
    )

    max_samples = (
        max(image_sample_count.values())
        if image_sample_count
        else 0
    )

    return {
        "file": file_path.name,
        "images": unique_images,
        "samples": total_samples,
        "avg": avg_samples,
        "min": min_samples,
        "max": max_samples
    }


if __name__ == "__main__":

    results = []

    total_images = 0
    total_samples = 0

    for filename in FILES:

        file_path = DATA_DIR / filename

        if not file_path.exists():

            print(
                f"[WARNING] Missing: {filename}"
            )

            continue

        result = process_file(file_path)

        results.append(result)

        total_images += result["images"]
        total_samples += result["samples"]

        print("\n" + "=" * 50)
        print(result["file"])
        print("=" * 50)

        print(
            f"Images              : {result['images']:,}"
        )

        print(
            f"Grounding Samples   : {result['samples']:,}"
        )

        print(
            f"Avg Samples/Image   : {result['avg']:.2f}"
        )

        print(
            f"Min Samples/Image   : {result['min']}"
        )

        print(
            f"Max Samples/Image   : {result['max']}"
        )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as report:

        report.write(
            "SKYFIND DATASET STATISTICS\n"
        )

        report.write(
            "=" * 60 + "\n\n"
        )

        for result in results:

            report.write(
                f"{result['file']}\n"
            )

            report.write(
                f"Images: {result['images']:,}\n"
            )

            report.write(
                f"Grounding Samples: {result['samples']:,}\n"
            )

            report.write(
                f"Average Samples/Image: {result['avg']:.2f}\n"
            )

            report.write(
                f"Min Samples/Image: {result['min']}\n"
            )

            report.write(
                f"Max Samples/Image: {result['max']}\n\n"
            )

        report.write(
            "=" * 60 + "\n"
        )

        report.write(
            f"TOTAL IMAGES : {total_images:,}\n"
        )

        report.write(
            f"TOTAL SAMPLES : {total_samples:,}\n"
        )

    print("\n" + "=" * 60)
    print("STATISTICS GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total Images  : {total_images:,}")
    print(f"Total Samples : {total_samples:,}")
    print(f"Report        : {REPORT_FILE}")