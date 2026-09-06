import json
from pathlib import Path


def save_json(data, filepath):

    filepath = Path(filepath)

    filepath.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"[INFO] Saved {len(data):,} records -> {filepath}"
    )


def load_json(filepath):

    filepath = Path(filepath)

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)