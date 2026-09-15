#!/usr/bin/env python3
"""Download and verify only the selected AerialVG evaluation images."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image
from huggingface_hub import hf_hub_download

REPO_ID = "IPEC-COMMUNITY/AerialVG"


def load_items(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_image(path: Path, expected_width: int, expected_height: int) -> None:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.width != expected_width or image.height != expected_height:
            raise ValueError(f"dimension mismatch for {path.name}: {image.size} != {(expected_width, expected_height)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = root / "aerialvg/evaluation90/aerialvg_test_90.jsonl"
    image_dir = root / "aerialvg/evaluation90/images"
    image_dir.mkdir(parents=True, exist_ok=True)
    success = 0
    failed: list[str] = []
    for item in load_items(manifest):
        filename = item["filename"]
        destination = image_dir / filename
        try:
            if not destination.is_file():
                cached = hf_hub_download(repo_id=REPO_ID, repo_type="dataset", filename=f"images/{filename}")
                shutil.copy2(cached, destination)
            verify_image(destination, int(item["width"]), int(item["height"]))
            success += 1
        except Exception as error:
            failed.append(f"{filename}: {error}")
    print(f"Success: {success}")
    print(f"Failed: {len(failed)}")
    for error in failed:
        print(f"- {error}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
