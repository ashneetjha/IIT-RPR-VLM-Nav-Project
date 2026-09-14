#!/usr/bin/env python3
"""Validate the generated AerialVG Phase 1 shortlist artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / "aerialvg/annotation/vg_test_odvg.jsonl"
    jsonl_path = root / "aerialvg/shortlist/aerialvg_test_shortlist.jsonl"
    csv_path = root / "aerialvg/shortlist/aerialvg_test_shortlist.csv"
    manual_path = root / "aerialvg/shortlist/manual_verification.md"
    report_path = root / "reports/AERIALVG_PHASE1_REPORT.md"
    source_records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    source_names = {record.get("filename") for record in source_records}
    shortlist = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    csv_rows = list(csv.DictReader(csv_path.open(encoding="utf-8", newline="")))
    errors: list[str] = []
    names = [record.get("filename") for record in shortlist]
    if len(names) != len(set(names)):
        errors.append("duplicate filenames in JSONL")
    if len(csv_rows) != len(shortlist):
        errors.append("CSV row count does not match JSONL shortlist count")
    if len({row.get("filename") for row in csv_rows}) != len(csv_rows):
        errors.append("duplicate filenames in CSV")
    if {row.get("filename") for row in csv_rows} != set(names):
        errors.append("CSV filenames do not exactly match shortlisted filenames")
    if not set(names).issubset(source_names):
        errors.append("shortlisted filename is absent from source")
    required_categories = {"long_caption", "short_caption", "complex_relational"}
    if {record.get("selection_category") for record in shortlist} != required_categories:
        errors.append("categories are missing or unexpected")
    for record in shortlist:
        grounding = record.get("grounding", {})
        if not isinstance(grounding.get("caption"), str) or not grounding["caption"]:
            errors.append(f"missing caption: {record.get('filename')}")
        regions = grounding.get("regions")
        if not isinstance(regions, list) or not regions or any("bbox" not in region for region in regions):
            errors.append(f"missing bbox/region data: {record.get('filename')}")
        if record.get("manual_verification_status") != "PENDING":
            errors.append(f"manual status is not PENDING: {record.get('filename')}")
    for row in csv_rows:
        if row.get("manual_verification_status") != "PENDING":
            errors.append(f"CSV manual status is not PENDING: {row.get('filename')}")
    for path in (csv_path, manual_path, report_path):
        if not path.exists():
            errors.append(f"missing output: {path.relative_to(root)}")
    if errors:
        print("Validation: FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Validation: PASS")
    print(f"Source records: {len(source_records)}")
    print(f"Shortlist: {len(shortlist)}")
    print(f"Unique filenames: {len(set(names))}")


if __name__ == "__main__":
    main()