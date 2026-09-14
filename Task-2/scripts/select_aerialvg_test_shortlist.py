#!/usr/bin/env python3
"""Create a deterministic, annotation-only AerialVG Phase 1 shortlist."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


SPATIAL_RE = re.compile(
    r"\b(left|right|top|bottom|front|behind|above|below|under|over|inside|"
    r"near|next to|beside|between|overlapping|in front of)\b",
    re.IGNORECASE,
)
DEFAULT_SOURCE = Path("aerialvg/annotation/vg_test_odvg.jsonl")
SHORT_MAX = 75
LONG_MIN = 100
QUOTA = 10


def load_records(source: Path) -> list[dict[str, Any]]:
    with source.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def analyze(record: dict[str, Any]) -> dict[str, Any]:
    grounding = record["grounding"]
    caption = grounding["caption"]
    regions = grounding["regions"]
    relations = [
        region.get("realation", "").strip()
        for region in regions
        if isinstance(region.get("realation", ""), str)
        and region.get("realation", "").strip()
    ]
    spatial_words = SPATIAL_RE.findall(caption)
    region_count = len(regions)
    relation_count = len(relations)
    spatial_count = len(spatial_words)
    # This score is for stable ranking, not a claim of semantic truth.
    complexity_score = (
        min(len(caption), 220) / 20.0
        + region_count * 4
        + relation_count * 5
        + spatial_count * 2
    )
    return {
        "caption_length": len(caption),
        "region_count": region_count,
        "relation_count": relation_count,
        "spatial_count": spatial_count,
        "complexity_score": round(complexity_score, 3),
    }


def normalized_caption(caption: str) -> str:
    return re.sub(r"\W+", " ", caption.lower()).strip()


def category_candidates(
    records: list[dict[str, Any]], analyses: dict[int, dict[str, Any]]
) -> dict[str, list[int]]:
    categories: dict[str, list[int]] = {"long_caption": [], "short_caption": [], "complex_relational": []}
    for index, record in enumerate(records):
        info = analyses[index]
        if info["caption_length"] >= LONG_MIN:
            categories["long_caption"].append(index)
        if info["caption_length"] <= SHORT_MAX:
            categories["short_caption"].append(index)
        if (
            info["region_count"] >= 3
            or info["relation_count"] >= 2
            or info["spatial_count"] >= 3
        ):
            categories["complex_relational"].append(index)

    categories["long_caption"].sort(
        key=lambda i: (
            -analyses[i]["caption_length"],
            -analyses[i]["region_count"],
            -analyses[i]["relation_count"],
            records[i]["filename"],
            normalized_caption(records[i]["grounding"]["caption"]),
            i,
        )
    )
    categories["short_caption"].sort(
        key=lambda i: (
            analyses[i]["caption_length"],
            -analyses[i]["region_count"],
            -analyses[i]["spatial_count"],
            records[i]["filename"],
            normalized_caption(records[i]["grounding"]["caption"]),
            i,
        )
    )
    categories["complex_relational"].sort(
        key=lambda i: (
            -analyses[i]["region_count"],
            -analyses[i]["relation_count"],
            -analyses[i]["spatial_count"],
            -analyses[i]["caption_length"],
            records[i]["filename"],
            normalized_caption(records[i]["grounding"]["caption"]),
            i,
        )
    )
    return categories


def choose_shortlist(
    records: list[dict[str, Any]], analyses: dict[int, dict[str, Any]]
) -> list[dict[str, Any]]:
    categories = category_candidates(records, analyses)
    chosen: list[dict[str, Any]] = []
    used_files: set[str] = set()
    used_captions: set[str] = set()
    for category in ("long_caption", "short_caption", "complex_relational"):
        selected = 0
        for index in categories[category]:
            record = records[index]
            filename = record["filename"]
            caption_key = normalized_caption(record["grounding"]["caption"])
            if filename in used_files or caption_key in used_captions:
                continue
            chosen.append(
                {
                    "record": record,
                    "analysis": analyses[index],
                    "selection_category": category,
                }
            )
            used_files.add(filename)
            used_captions.add(caption_key)
            selected += 1
            if selected == QUOTA:
                break
        if selected != QUOTA:
            raise RuntimeError(f"Could not find {QUOTA} unique records for {category}")
    return chosen


def target_region(record: dict[str, Any]) -> dict[str, Any] | None:
    regions = record["grounding"].get("regions", [])
    if not regions:
        return None
    first = regions[0]
    # In this annotation schema the first region is the target when it has no
    # relation; later regions carry the anchor relation(s).
    if not first.get("realation", ""):
        return first
    return None


def write_outputs(
    selected: list[dict[str, Any]], source: Path, root: Path
) -> tuple[Path, Path, Path, Path, Path]:
    output_dir = root / "aerialvg" / "shortlist"
    reports_dir = root / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "aerialvg_test_shortlist.jsonl"
    csv_path = output_dir / "aerialvg_test_shortlist.csv"
    manual_path = output_dir / "manual_verification.md"
    availability_path = output_dir / "image_availability.csv"
    report_path = reports_dir / "AERIALVG_PHASE1_REPORT.md"
    summary_path = reports_dir / "AERIALVG_PHASE1_SUMMARY.txt"

    for rank, item in enumerate(selected, start=1):
        item["selection_rank"] = rank
        item["manual_verification_status"] = "PENDING"
        item["record"].update(
            {
                "selection_rank": rank,
                "selection_category": item["selection_category"],
                **item["analysis"],
                "manual_verification_status": "PENDING",
            }
        )
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for item in selected:
            handle.write(json.dumps(item["record"], ensure_ascii=False) + "\n")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "rank", "filename", "selection_category", "caption_length", "caption",
            "region_count", "relation_count", "target_phrase", "target_bbox",
            "manual_verification_status",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in selected:
            record = item["record"]
            target = target_region(record)
            writer.writerow(
                {
                    "rank": item["selection_rank"],
                    "filename": record["filename"],
                    "selection_category": item["selection_category"],
                    "caption_length": item["analysis"]["caption_length"],
                    "caption": record["grounding"]["caption"],
                    "region_count": item["analysis"]["region_count"],
                    "relation_count": item["analysis"]["relation_count"],
                    "target_phrase": target.get("phrase", "") if target else "",
                    "target_bbox": json.dumps(target["bbox"]) if target else "",
                    "manual_verification_status": "PENDING",
                }
            )

    with manual_path.open("w", encoding="utf-8") as handle:
        handle.write("# AerialVG Test Shortlist Manual Verification\n\n")
        handle.write("All entries are annotation-based candidates. No image was visually inspected by this script.\n\n")
        for item in selected:
            record = item["record"]
            target = target_region(record)
            relations = [
                region.get("realation", "")
                for region in record["grounding"]["regions"]
                if region.get("realation", "")
            ]
            expected = "; ".join(relations) if relations else "No explicit anchor relation"
            handle.write(f"## {item['selection_rank']}. {record['filename']}\n\n")
            handle.write(f"- Caption: {record['grounding']['caption']}\n")
            handle.write(f"- Category: {item['selection_category']}\n")
            handle.write(f"- Target: {target.get('phrase', '') if target else 'Not inferred from schema'}\n")
            handle.write(f"- Expected relationship: {expected}\n")
            handle.write(f"- Expected target bbox: {json.dumps(target['bbox']) if target else 'Not inferred from schema'}\n")
            handle.write("- Verification status: PENDING\n- Notes: \n\n")

    with availability_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["filename", "local_image_found", "local_path", "manual_verification_status"])
        writer.writeheader()
        for item in selected:
            filename = item["record"]["filename"]
            matches = list(root.rglob(filename))
            writer.writerow(
                {
                    "filename": filename,
                    "local_image_found": str(bool(matches)).lower(),
                    "local_path": str(matches[0].relative_to(root)) if matches else "",
                    "manual_verification_status": "PENDING",
                }
            )

    counts = Counter(item["selection_category"] for item in selected)
    source_records = len(load_records(source))
    schema = (
        "Top-level `filename`, `height`, `width`, `grounding`; `grounding` contains "
        "`caption` and `regions`; each region contains `bbox`, `phrase`, and, for "
        "anchor regions, `realation` (dataset spelling)."
    )
    report = f"""# AerialVG Phase 1 Report

- Date: {date.today().isoformat()}
- Source file: `{source.relative_to(root)}`
- Total records: {source_records}
- Shortlist size: {len(selected)} unique filenames
- Counts: long_caption={counts['long_caption']}, short_caption={counts['short_caption']}, complex_relational={counts['complex_relational']}

## Schema discovered

{schema} No source records were modified.

## Filtering methodology

All {source_records} JSONL records were parsed. Caption character length, region count (entity proxy), explicit non-empty `realation` count, and case-insensitive spatial-word count were calculated. Long candidates have length >= {LONG_MIN}; short candidates have length <= {SHORT_MAX}; complex relational candidates have at least 3 regions, at least 2 explicit relations, or at least 3 spatial relation words. Ranking is deterministic and category-specific: long favors length, short favors genuinely short captions while retaining region/spatial signal, and complex favors regions, relations, spatial language, then length.

Ten candidates were selected per category. A global filename set and normalized-caption set prevent duplicate filenames and trivial repeated captions. The source order was not used as the selection criterion.

## Target, anchor, and relation interpretation

The first region is summarized as the Target only when it has no `realation` field/value, matching the observed schema pattern in which later regions carry anchor relationships. All regions remain preserved in the shortlist JSONL. CSV and the manual checklist summarize the first region only when this interpretation is supported; no target was invented otherwise.

## Completed and not completed

Completed: annotation parsing, deterministic candidate filtering, a 30-image candidate shortlist, CSV/JSONL export, manual-verification checklist, local image availability check, and structural validation.

Not completed: visual inspection, manual verification, downloading images, model evaluation, Grounding DINO, and GLIP. This is an LLM-assisted annotation shortlist only, not a visually verified result.

## Exact next step

Obtain the selected image files through the approved dataset access process, open each image, compare the caption and all target/anchor relationships against the annotation, then update only the manual checklist/status fields after human review.

## Reproducibility

```bash
python3 scripts/select_aerialvg_test_shortlist.py
python3 scripts/validate_aerialvg_shortlist.py
```
"""
    report_path.write_text(report, encoding="utf-8")
    summary_path.write_text(
        f"Source: {source.relative_to(root)}\n"
        f"Total test records: {source_records}\n"
        f"Shortlist size: {len(selected)}\n"
        f"Category counts: long={counts['long_caption']}, short={counts['short_caption']}, complex={counts['complex_relational']}\n"
        "Status: Candidate shortlist created; manual visual verification pending\n"
        "Next action: Obtain and inspect selected images manually; do not run Grounding DINO/GLIP yet.\n",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, manual_path, availability_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    source = args.source if args.source.is_absolute() else root / args.source
    records = load_records(source)
    analyses = {index: analyze(record) for index, record in enumerate(records)}
    selected = choose_shortlist(records, analyses)
    write_outputs(selected, source, root)
    counts = Counter(item["selection_category"] for item in selected)
    print("AERIAL VG PHASE 1")
    print("-----------------")
    print(f"Source records: {len(records)}")
    print(f"Shortlist: {len(selected)}")
    print(f"Long captions: {counts['long_caption']}")
    print(f"Short captions: {counts['short_caption']}")
    print(f"Complex relational: {counts['complex_relational']}")
    print(f"Unique filenames: {len({item['record']['filename'] for item in selected})}")
    print("Validation: run validate_aerialvg_shortlist.py")


if __name__ == "__main__":
    main()