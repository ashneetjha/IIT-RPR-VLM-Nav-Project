from datasets import load_dataset, Image
from pathlib import Path
import json
import time

from config import (
    DATASET_NAME,
    DATA_DIR,
    LOG_DIR,
    LOG_INTERVAL
)


def get_last_processed_image(output_file):

    if not output_file.exists():
        return None

    try:

        with open(
            output_file,
            "rb"
        ) as f:

            f.seek(0, 2)

            file_size = f.tell()

            buffer = b""
            block_size = 4096

            while file_size > 0:

                read_size = min(
                    block_size,
                    file_size
                )

                file_size -= read_size

                f.seek(file_size)

                buffer = (
                    f.read(read_size)
                    + buffer
                )

                lines = buffer.splitlines()

                if len(lines) > 1:

                    last_line = lines[-1]

                    record = json.loads(
                        last_line.decode(
                            "utf-8"
                        )
                    )

                    return record.get(
                        "image_id"
                    )

    except Exception:

        return None

    return None


def process_train_split():

    split_name = "train"

    output_file = (
        DATA_DIR /
        "grounding_train.jsonl"
    )

    report_file = (
        DATA_DIR /
        "report_train.txt"
    )

    error_file = (
        LOG_DIR /
        "errors_train.log"
    )

    resume_after_image = (
        get_last_processed_image(
            output_file
        )
    )

    print("\n" + "=" * 70)
    print(
        "[INFO] SKYFIND GROUNDING DATASET GENERATION"
    )
    print("=" * 70)
    print(
        f"[INFO] Dataset : {DATASET_NAME}"
    )
    print(
        f"[INFO] Split   : {split_name}"
    )
    print(
        f"[INFO] Output  : {output_file}"
    )

    if resume_after_image:

        print(
            f"[INFO] Resume From : "
            f"{resume_after_image}"
        )

    else:

        print(
            "[INFO] Fresh Run"
        )

    print("=" * 70)

    start_time = time.time()

    dataset = load_dataset(
        DATASET_NAME,
        split=split_name,
        streaming=True
    )

    dataset = dataset.cast_column(
        "image",
        Image(decode=False)
    )

    image_count = 0
    annotation_count = 0
    sample_count = 0
    error_count = 0

    resume_mode = (
        resume_after_image
        is not None
    )

    with open(
        output_file,
        "a",
        encoding="utf-8"
    ) as outfile, open(
        error_file,
        "a",
        encoding="utf-8"
    ) as errlog:

        for record in dataset:

            try:

                image_id = record.get(
                    "fileName"
                )

                if not image_id:
                    continue

                # --------------------------------
                # AUTO RESUME
                # --------------------------------

                if resume_mode:

                    if (
                        image_id
                        ==
                        resume_after_image
                    ):

                        resume_mode = False

                        print(
                            f"[INFO] Resume point found: "
                            f"{image_id}"
                        )

                        continue

                    else:

                        continue

                # --------------------------------

                image_count += 1

                annotations = record.get(
                    "annotations",
                    []
                )

                for ann in annotations:

                    try:

                        annotation_count += 1

                        bbox = ann.get(
                            "bbox"
                        )

                        expressions = ann.get(
                            "expressions",
                            []
                        )

                        if not bbox:
                            continue

                        if len(bbox) != 4:
                            continue

                        if not expressions:
                            continue

                        for expression in expressions:

                            expression = (
                                expression.strip()
                            )

                            if not expression:
                                continue

                            output_record = {
                                "image_id": image_id,
                                "bbox": bbox,
                                "expression": expression
                            }

                            outfile.write(
                                json.dumps(
                                    output_record,
                                    ensure_ascii=False
                                )
                                + "\n"
                            )

                            sample_count += 1

                            if (
                                sample_count %
                                LOG_INTERVAL
                                ==
                                0
                            ):

                                runtime = (
                                    time.time()
                                    -
                                    start_time
                                ) / 60

                                print(
                                    f"[INFO] Samples: {sample_count:,} | "
                                    f"Images: {image_count:,} | "
                                    f"Annotations: {annotation_count:,} | "
                                    f"Errors: {error_count:,} | "
                                    f"Runtime: {runtime:.2f} min"
                                )

                                outfile.flush()

                    except Exception as ann_error:

                        error_count += 1

                        errlog.write(
                            f"Annotation Error | "
                            f"Image={image_id} | "
                            f"{str(ann_error)}\n"
                        )

            except Exception as img_error:

                error_count += 1

                errlog.write(
                    f"Image Error | "
                    f"{str(img_error)}\n"
                )

    runtime_minutes = (
        time.time()
        -
        start_time
    ) / 60

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as report:

        report.write(
            f"Dataset: {DATASET_NAME}\n"
            f"Split: {split_name}\n\n"
            f"Images Processed: {image_count:,}\n"
            f"Annotations Seen: {annotation_count:,}\n"
            f"Grounding Samples Added: {sample_count:,}\n"
            f"Errors: {error_count:,}\n"
            f"Runtime (minutes): {runtime_minutes:.2f}\n"
            f"Output File: {output_file}\n"
            f"Error Log: {error_file}\n"
        )

    print("\n" + "=" * 70)
    print("TASK 1 COMPLETED")
    print("=" * 70)
    print(
        f"Images Processed  : {image_count:,}"
    )
    print(
        f"Annotations Seen  : {annotation_count:,}"
    )
    print(
        f"Grounding Samples : {sample_count:,}"
    )
    print(
        f"Errors            : {error_count:,}"
    )
    print(
        f"Runtime           : {runtime_minutes:.2f} min"
    )
    print(
        f"Output            : {output_file}"
    )
    print(
        f"Report            : {report_file}"
    )
    print(
        f"Error Log         : {error_file}"
    )
    print("=" * 70)


if __name__ == "__main__":
    process_train_split()