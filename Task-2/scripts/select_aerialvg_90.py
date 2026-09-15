#!/usr/bin/env python3
"""Create a deterministic 90-image AerialVG evaluation manifest."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

SPATIAL_RE = re.compile(
    r"\b(left|right|top|bottom|front|behind|above|below|under|over|inside|"
    r"near|next to|beside|between|overlapping|in front of)\b",
    re.IGNORECASE,
)
CATEGORIES = ("long_caption", "short_caption", "complex_relational")
TARGETS = {"long_caption": 30, "short_caption": 30, "complex_relational": 30}
LONG_MIN = 100
SHORT_MAX = 75


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def normalized_caption(caption: str) -> str:
    return re.sub(r"\W+", " ", caption.lower()).strip()


def relation_value(region: dict[str, Any]) -> str:
    value = region.get("realation") or region.get("relation", "")
    return value.strip() if isinstance(value, str) else ""


def analyze(record: dict[str, Any]) -> dict[str, int | float]:
    grounding = record["grounding"]
    caption = grounding["caption"]
    regions = grounding.get("regions", [])
    relations = [relation_value(region) for region in regions]
    relations = [relation for relation in relations if relation]
    return {
        "caption_length": len(caption),
        "region_count": len(regions),
        "relation_count": len(relations),
        "spatial_count": len(SPATIAL_RE.findall(caption)),
        "complexity_score": round(
            min(len(caption), 220) / 20
            + len(regions) * 4
            + len(relations) * 5
            + len(SPATIAL_RE.findall(caption)) * 2,
            3,
        ),
    }


def target_region(record: dict[str, Any]) -> dict[str, Any]:
    regions = record.get("grounding", {}).get("regions", [])
    if not regions or relation_value(regions[0]):
        raise ValueError(f"target region cannot be inferred: {record.get('filename')}")
    target = regions[0]
    if not target.get("phrase") or not isinstance(target.get("bbox"), list):
        raise ValueError(f"target data is incomplete: {record.get('filename')}")
    return target


def candidate_indices(records: list[dict[str, Any]]) -> dict[str, list[int]]:
    analyses = [analyze(record) for record in records]
    candidates = {category: [] for category in CATEGORIES}
    for index, info in enumerate(analyses):
        if info["caption_length"] >= LONG_MIN:
            candidates["long_caption"].append(index)
        if info["caption_length"] <= SHORT_MAX:
            candidates["short_caption"].append(index)
        if info["region_count"] >= 3 or info["relation_count"] >= 2 or info["spatial_count"] >= 3:
            candidates["complex_relational"].append(index)
    candidates["long_caption"].sort(
        key=lambda index: (
            -analyses[index]["caption_length"],
            -analyses[index]["region_count"],
            -analyses[index]["relation_count"],
            records[index]["filename"],
            normalized_caption(records[index]["grounding"]["caption"]),
            index,
        )
    )
    candidates["short_caption"].sort(
        key=lambda index: (
            analyses[index]["caption_length"],
            -analyses[index]["region_count"],
            -analyses[index]["spatial_count"],
            records[index]["filename"],
            normalized_caption(records[index]["grounding"]["caption"]),
            index,
        )
    )
    candidates["complex_relational"].sort(
        key=lambda index: (
            -analyses[index]["region_count"],
            -analyses[index]["relation_count"],
            -analyses[index]["spatial_count"],
            -analyses[index]["caption_length"],
            records[index]["filename"],
            normalized_caption(records[index]["grounding"]["caption"]),
            index,
        )
    )
    return candidates


def select(records: list[dict[str, Any]], existing_path: Path) -> list[dict[str, Any]]:
    by_filename = {record["filename"]: record for record in records}
    existing = load_jsonl(existing_path)
    selected: list[dict[str, Any]] = []
    used_files: set[str] = set()
    used_captions: set[str] = set()
    counts = Counter()
    for item in existing:
        filename = item.get("filename")
        category = item.get("selection_category")
        if filename not in by_filename or category not in TARGETS or filename in used_files:
            continue
        record = by_filename[filename]
        caption_key = normalized_caption(record["grounding"]["caption"])
        if caption_key in used_captions:
            continue
        target_region(record)
        selected.append({"record": record, "category": category, "reused_phase1": True})
        used_files.add(filename)
        used_captions.add(caption_key)
        counts[category] += 1
    candidates = candidate_indices(records)
    for category in CATEGORIES:
        for index in candidates[category]:
            if counts[category] >= TARGETS[category]:
                break
            record = records[index]
            filename = record["filename"]
            caption_key = normalized_caption(record["grounding"]["caption"])
            if filename in used_files or caption_key in used_captions:
                continue
            target_region(record)
            selected.append({"record": record, "category": category, "reused_phase1": False})
            used_files.add(filename)
            used_captions.add(caption_key)
            counts[category] += 1
        if counts[category] != TARGETS[category]:
            raise RuntimeError(f"Could not select {TARGETS[category]} {category} records")
    if len(selected) != 90 or len(used_files) != 90:
        raise RuntimeError("selection did not produce 90 unique records")
    return selected


def manifest_item(item: dict[str, Any], rank: int, verified_names: set[str]) -> dict[str, Any]:
    record = item["record"]
    grounding = record["grounding"]
    target = target_region(record)
    relations = [
        {"phrase": region.get("phrase", ""), "relation": relation_value(region), "bbox": region.get("bbox")}
        for region in grounding.get("regions", [])[1:]
        if relation_value(region)
    ]
    return {
        "filename": record["filename"],
        "selection_rank": rank,
        "selection_category": item["category"],
        "caption": grounding["caption"],
        "target": target["phrase"],
        "target_bbox": target["bbox"],
        "relations": relations,
        "regions": grounding.get("regions", []),
        "width": record["width"],
        "height": record["height"],
        "manual_verification_status": "VERIFIED" if record["filename"] in verified_names else "PENDING",
        "reused_phase1": item["reused_phase1"],
    }


def write_outputs(selected: list[dict[str, Any]], root: Path, verified_names: set[str]) -> None:
    output = root / "aerialvg/evaluation90"
    image_dir = output / "images"
    output.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)
    items = [manifest_item(item, rank, verified_names) for rank, item in enumerate(selected, 1)]
    jsonl_path = output / "aerialvg_test_90.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    csv_path = output / "aerialvg_test_90.csv"
    fields = ["filename", "selection_category", "caption", "target", "target_bbox", "relation_summary", "width", "height", "local_image_path", "manual_verification_status"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for item in items:
            writer.writerow({
                "filename": item["filename"],
                "selection_category": item["selection_category"],
                "caption": item["caption"],
                "target": item["target"],
                "target_bbox": json.dumps(item["target_bbox"]),
                "relation_summary": "; ".join(relation["relation"] for relation in item["relations"]),
                "width": item["width"],
                "height": item["height"],
                "local_image_path": f"aerialvg/evaluation90/images/{item['filename']}",
                "manual_verification_status": item["manual_verification_status"],
            })
    availability = output / "image_availability.csv"
    with availability.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["filename", "local_image_found", "local_image_path", "width", "height", "status"], lineterminator="\n")
        writer.writeheader()
        for item in items:
            path = image_dir / item["filename"]
            writer.writerow({
                "filename": item["filename"],
                "local_image_found": str(path.is_file()).lower(),
                "local_image_path": f"aerialvg/evaluation90/images/{item['filename']}",
                "width": item["width"],
                "height": item["height"],
                "status": "VERIFIED" if item["manual_verification_status"] == "VERIFIED" else "PENDING",
            })
    counts = Counter(item["selection_category"] for item in items)
    reused = sum(item["reused_phase1"] for item in items)
    report = output / "evaluation_selection_report.md"
    report.write_text(
        "# AerialVG 90-Image Evaluation Selection\n\n"
        f"- Source file: `aerialvg/annotation/vg_test_odvg.jsonl`\n"
        f"- Source record count: 4723\n- Final evaluation count: {len(items)}\n"
        f"- Category counts: long_caption={counts['long_caption']}, short_caption={counts['short_caption']}, complex_relational={counts['complex_relational']}\n"
        f"- Reused Phase 1 count: {reused}\n- Newly added count: {len(items) - reused}\n"
        "- Selection criteria: long captions are at least 100 characters; short captions are at most 75 characters; complex relational records have at least 3 regions, at least 2 explicit relations, or at least 3 spatial relation words.\n"
        "- Duplicate prevention: filenames and normalized captions are unique globally.\n"
        "- Caption normalization: lowercase captions with non-word runs replaced by spaces.\n"
        "- Selection is deterministic and reuses all valid Phase 1 records before category-specific ranking fills the quotas.\n"
        "- Download source: `IPEC-COMMUNITY/AerialVG`, `images/<filename>`.\n"
        f"- Local image count: {sum((image_dir / item['filename']).is_file() for item in items)}/{len(items)}\n"
        f"- VERIFIED count: {sum(item['manual_verification_status'] == 'VERIFIED' for item in items)}\n"
        f"- PENDING count: {sum(item['manual_verification_status'] == 'PENDING' for item in items)}\n\n"
        "Grounding DINO not started.\n\nGLIP not started.\n\nThis is the 90-image evaluation preparation stage.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / "aerialvg/annotation/vg_test_odvg.jsonl"
    existing = root / "aerialvg/shortlist/aerialvg_test_shortlist.jsonl"
    existing_records = load_jsonl(existing)
    verified_names = {item["filename"] for item in existing_records if item.get("manual_verification_status") == "VERIFIED"}
    selected = select(load_jsonl(source), existing)
    write_outputs(selected, root, verified_names)
    print(f"Selected {len(selected)} records: " + ", ".join(f"{key}={value}" for key, value in Counter(item['category'] for item in selected).items()))


if __name__ == "__main__":
    main()
