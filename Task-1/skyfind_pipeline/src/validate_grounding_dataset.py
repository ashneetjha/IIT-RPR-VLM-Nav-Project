import json
from pathlib import Path

DATA_DIR = Path("data")

FILES = [
    "grounding_train.jsonl",
    "grounding_validation.jsonl",
    "grounding_test.jsonl",
    "grounding_train_aug.jsonl"
]

REPORT_FILE = DATA_DIR / "validation_report.txt"


def validate_file(file_path):

    total_records = 0
    valid_records = 0
    invalid_records = 0

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line_num, line in enumerate(f, start=1):

            total_records += 1

            try:

                record = json.loads(line)

                image_id = record.get(
                    "image_id"
                )

                bbox = record.get(
                    "bbox"
                )

                expression = record.get(
                    "expression"
                )

                if not image_id:
                    invalid_records += 1
                    continue

                if not isinstance(
                    bbox,
                    list
                ):
                    invalid_records += 1
                    continue

                if len(bbox) != 4:
                    invalid_records += 1
                    continue

                if not isinstance(
                    expression,
                    str
                ):
                    invalid_records += 1
                    continue

                if not expression.strip():
                    invalid_records += 1
                    continue

                valid_records += 1

            except Exception:

                invalid_records += 1

    return {
        "file": file_path.name,
        "total": total_records,
        "valid": valid_records,
        "invalid": invalid_records
    }


if __name__ == "__main__":

    results = []

    total_records = 0
    total_valid = 0
    total_invalid = 0

    for filename in FILES:

        file_path = DATA_DIR / filename

        if not file_path.exists():

            print(
                f"[WARNING] Missing file: {filename}"
            )

            continue

        result = validate_file(
            file_path
        )

        results.append(result)

        total_records += result["total"]
        total_valid += result["valid"]
        total_invalid += result["invalid"]

        print(
            f"[OK] {filename}"
        )

        print(
            f"Records : {result['total']:,}"
        )

        print(
            f"Valid   : {result['valid']:,}"
        )

        print(
            f"Invalid : {result['invalid']:,}\n"
        )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as report:

        report.write(
            "GROUNDING DATASET VALIDATION REPORT\n"
        )

        report.write(
            "=" * 50 + "\n\n"
        )

        for result in results:

            report.write(
                f"{result['file']}\n"
            )

            report.write(
                f"Total Records : {result['total']:,}\n"
            )

            report.write(
                f"Valid Records : {result['valid']:,}\n"
            )

            report.write(
                f"Invalid Records : {result['invalid']:,}\n\n"
            )

        report.write(
            "=" * 50 + "\n"
        )

        report.write(
            f"TOTAL RECORDS : {total_records:,}\n"
        )

        report.write(
            f"VALID RECORDS : {total_valid:,}\n"
        )

        report.write(
            f"INVALID RECORDS : {total_invalid:,}\n"
        )

    print("\n================================")
    print("VALIDATION COMPLETE")
    print("================================")
    print(f"Total Records : {total_records:,}")
    print(f"Valid Records : {total_valid:,}")
    print(f"Invalid       : {total_invalid:,}")
    print(f"Report        : {REPORT_FILE}")