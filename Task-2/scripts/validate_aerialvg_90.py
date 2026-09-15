#!/usr/bin/env python3
"""Validate the reproducible AerialVG 90-image evaluation set."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image

CATEGORIES = ("long_caption", "short_caption", "complex_relational")
PHASE1_FILES = (
    "aerialvg/shortlist/aerialvg_test_shortlist.jsonl",
    "aerialvg/shortlist/aerialvg_test_shortlist.csv",
    "aerialvg/shortlist/image_availability.csv",
    "aerialvg/shortlist/manual_verification.md",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_output(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / "aerialvg/annotation/vg_test_odvg.jsonl"
    output = root / "aerialvg/evaluation90"
    jsonl_path = output / "aerialvg_test_90.jsonl"
    csv_path = output / "aerialvg_test_90.csv"
    availability_path = output / "image_availability.csv"
    image_dir = output / "images"
    errors: list[str] = []

    required_paths = [source, jsonl_path, csv_path, availability_path, output / "evaluation_selection_report.md"]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(root)}")
    if not image_dir.is_dir():
        errors.append("missing evaluation image directory")

    source_records: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    csv_rows: list[dict[str, str]] = []
    availability_rows: list[dict[str, str]] = []
    if source.is_file():
        try:
            source_records = load_jsonl(source)
        except Exception as error:
            errors.append(f"source JSONL is unreadable: {error}")
    if jsonl_path.is_file():
        try:
            records = load_jsonl(jsonl_path)
        except Exception as error:
            errors.append(f"evaluation JSONL is invalid: {error}")
    if csv_path.is_file():
        try:
            with csv_path.open(encoding="utf-8", newline="") as handle:
                csv_rows = list(csv.DictReader(handle))
        except Exception as error:
            errors.append(f"evaluation CSV is invalid: {error}")
    if availability_path.is_file():
        try:
            with availability_path.open(encoding="utf-8", newline="") as handle:
                availability_rows = list(csv.DictReader(handle))
        except Exception as error:
            errors.append(f"availability CSV is invalid: {error}")

    source_names = {record.get("filename") for record in source_records}
    source_by_name: dict[str, list[dict[str, Any]]] = {}
    for source_record in source_records:
        source_by_name.setdefault(source_record.get("filename"), []).append(source_record)
    names = [record.get("filename") for record in records]
    name_set = set(names)
    if len(source_records) != 4723:
        errors.append(f"source record count is {len(source_records)}, expected 4723")
    if len(records) != 90:
        errors.append(f"evaluation record count is {len(records)}, expected 90")
    if len(name_set) != 90:
        errors.append(f"evaluation unique filename count is {len(name_set)}, expected 90")
    if Counter(record.get("selection_category") for record in records) != Counter({category: 30 for category in CATEGORIES}):
        errors.append("category counts are not exactly 30/30/30")
    if not name_set.issubset(source_names):
        errors.append("evaluation contains filename absent from source annotation")
    csv_names = {row.get("filename") for row in csv_rows}
    availability_names = {row.get("filename") for row in availability_rows}
    if csv_names != name_set or len(csv_rows) != len(records):
        errors.append("evaluation CSV filenames do not exactly match JSONL")
    if availability_names != name_set or len(availability_rows) != len(records):
        errors.append("availability CSV filenames do not exactly match JSONL")

    for record in records:
        filename = record.get("filename")
        if not isinstance(record.get("caption"), str) or not record["caption"].strip():
            errors.append(f"missing caption: {filename}")
        if not isinstance(record.get("target"), str) or not record["target"].strip():
            errors.append(f"missing target: {filename}")
        bbox = record.get("target_bbox")
        if not isinstance(bbox, list) or len(bbox) != 4 or any(not isinstance(value, (int, float)) for value in bbox):
            errors.append(f"invalid target bbox: {filename}")
        if not isinstance(record.get("regions"), list) or not record["regions"]:
            errors.append(f"missing regions: {filename}")
        source_matches = source_by_name.get(filename, [])
        if source_matches:
            if not any(
                record.get("caption") == source_record.get("grounding", {}).get("caption")
                and record.get("regions") == source_record.get("grounding", {}).get("regions", [])
                and record.get("target") == source_record.get("grounding", {}).get("regions", [{}])[0].get("phrase")
                and record.get("target_bbox") == source_record.get("grounding", {}).get("regions", [{}])[0].get("bbox")
                for source_record in source_matches
            ):
                errors.append(f"manifest annotation differs from all source records: {filename}")
        image_path = image_dir / str(filename)
        if not image_path.is_file():
            errors.append(f"missing image: {filename}")
            continue
        try:
            with Image.open(image_path) as image:
                image.verify()
            with Image.open(image_path) as image:
                actual_size = (image.width, image.height)
            expected_size = (record.get("width"), record.get("height"))
            if actual_size != expected_size:
                errors.append(f"image dimensions mismatch: {filename}: {actual_size} != {expected_size}")
        except Exception as error:
            errors.append(f"image cannot be opened: {filename}: {error}")

    for row in availability_rows:
        filename = row.get("filename")
        expected_path = f"aerialvg/evaluation90/images/{filename}"
        if row.get("local_image_found") != "true" or row.get("local_image_path") != expected_path:
            errors.append(f"availability does not confirm local image: {filename}")
        if row.get("status") not in {"VERIFIED", "PENDING"}:
            errors.append(f"invalid availability status: {filename}")

    csv_by_name = {row.get("filename"): row for row in csv_rows}
    for record in records:
        row = csv_by_name.get(record.get("filename"))
        if row is None:
            continue
        if row.get("selection_category") != record.get("selection_category"):
            errors.append(f"CSV category differs from JSONL: {record.get('filename')}")
        if row.get("manual_verification_status") != record.get("manual_verification_status"):
            errors.append(f"CSV status differs from JSONL: {record.get('filename')}")

    phase1 = root / "aerialvg/shortlist/aerialvg_test_shortlist.jsonl"
    if not phase1.is_file():
        errors.append("missing Phase 1 shortlist")
    else:
        phase1_records = load_jsonl(phase1)
        phase1_names = {record["filename"] for record in phase1_records}
        if not phase1_names.issubset(name_set):
            errors.append("not all Phase 1 filenames were reused")
        for filename in phase1_names:
            original = root / "aerialvg/images" / filename
            evaluation = image_dir / filename
            if not original.is_file() or not evaluation.is_file():
                errors.append(f"Phase 1 image is not preserved: {filename}")
            elif sha256(original) != sha256(evaluation):
                errors.append(f"Phase 1 image differs in evaluation copy: {filename}")
        phase1_statuses = {record.get("manual_verification_status") for record in phase1_records}
        if phase1_statuses != {"VERIFIED"}:
            errors.append("Phase 1 shortlist no longer has all VERIFIED statuses")

    tracked_diff = git_output(root, "diff", "--name-only", "HEAD")
    for changed in tracked_diff.splitlines():
        if "annotation/vg_test_odvg.jsonl" in changed:
            errors.append("source annotation is modified")
        if any(token in changed.lower() for token in ("uav123", "uavit", "uav-1m", "uav-1", "uav-3")):
            errors.append(f"unrelated UAV file is modified: {changed}")

    if errors:
        print("Validation: FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    counts = Counter(record["selection_category"] for record in records)
    verified = sum(record.get("manual_verification_status") == "VERIFIED" for record in records)
    pending = sum(record.get("manual_verification_status") == "PENDING" for record in records)
    reused = sum(record.get("reused_phase1") is True for record in records)
    print("Validation: PASS")
    print(f"Source records: {len(source_records)}")
    print(f"Final images: {len(records)}")
    print(f"Unique filenames: {len(name_set)}")
    print(f"Long captions: {counts['long_caption']}")
    print(f"Short captions: {counts['short_caption']}")
    print(f"Complex relational: {counts['complex_relational']}")
    print(f"Reused verified Phase-1 images: {reused}")
    print(f"Verified: {verified}")
    print(f"Pending: {pending}")


if __name__ == "__main__":
    main()
