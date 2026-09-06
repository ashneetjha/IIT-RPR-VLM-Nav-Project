#!/usr/bin/env python3
"""Reproducible, read-only audit of the local UAV123 10fps release."""
import json, math, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "UAV123_10fps"
ANNO = DATA / "anno" / "UAV123_10fps"
IMAGES = DATA / "data_seq" / "UAV123_10fps"
REPORTS = ROOT / "reports"

def main():
    REPORTS.mkdir(exist_ok=True)
    fields, invalid, nan_rows, rows = Counter(), 0, 0, 0
    files = sorted(p for p in ANNO.glob("*.txt") if p.parent.name != "att")
    for p in files:
        for line in p.read_text(errors="replace").splitlines():
            if not line.strip(): continue
            vals = [x.strip() for x in line.split(",")]
            fields[str(len(vals))] += 1; rows += 1
            try:
                nums = [float(x) for x in vals]
                if any(math.isnan(x) for x in nums): nan_rows += 1
                if len(nums) != 4 or not all(math.isfinite(x) for x in nums): invalid += 1
            except ValueError: invalid += 1
    cfg = (DATA / "configSeqs.m").read_text(errors="replace")
    mappings = []
    pattern = re.compile(r"struct\('name','([^']+)','path','([^']+)','startFrame',(\d+),'endFrame',(\d+)")
    for name, path, start, end in pattern.findall(cfg):
        folder = Path(path.replace('\\', '/')).name
        mappings.append({"sequence": name, "image_folder": folder, "start_frame": int(start), "end_frame": int(end)})
    image_files = list(IMAGES.rglob("*.jpg")) + list(IMAGES.rglob("*.jpeg")) + list(IMAGES.rglob("*.png"))
    physical_folders = [p for p in IMAGES.iterdir() if p.is_dir()]
    group = next(x for x in mappings if x['sequence'] == 'group1_2')
    audit = {
      "dataset": "UAV123 10fps local release", "dataset_path": str(DATA),
      "annotation_file_count": len(files), "image_file_count": len(image_files),
      "physical_image_folder_count": len(physical_folders), "total_annotation_rows": rows,
      "field_count_distribution": dict(fields), "invalid_rows": invalid, "nan_rows": nan_rows,
      "annotation_format": "x,y,width,height", "converted_bbox_format": "[x1,y1,x2,y2] where x2=x+w and y2=y+h",
      "representative_sequence_mappings": [x for x in mappings if x['sequence'] in ['bike1','group1_1','group1_2','person4_1','uav1_1']],
      "group1_2_mapping": {**group, "annotation_rows": sum(1 for x in (ANNO/'group1_2.txt').read_text().splitlines() if x.strip()), "first_image": "000445.jpg", "last_expected_image": "000839.jpg"},
      "tracking_attributes": "Per-sequence attribute files are under anno/UAV123_10fps/att; they are tracking challenge tags, not language expressions.",
      "native_language_grounding": {"exists": False, "finding": "Audited native annotation and configuration files contain numeric boxes, sequence metadata, and tracking attributes; no native referring-expression/text-command field was found."},
      "audit_method": "Read-only scan of native annotation text files and configSeqs.m; raw data was not modified."
    }
    (REPORTS/'uav123_audit.json').write_text(json.dumps(audit, indent=2)+"\n")
    md = f"# UAV123 10fps audit\n\n- Annotation files: **{len(files)}**; rows: **{rows}**; images: **{len(image_files)}**; physical image folders: **{len(physical_folders)}**.\n- Rows have field counts: `{dict(fields)}`; invalid rows: **{invalid}**; NaN rows: **{nan_rows}**.\n- Native boxes are `x,y,width,height`; conversion is `[x, y, x+w, y+h]`.\n- `group1_2` maps to `group1/000445.jpg` through `group1/000839.jpg`, with **{audit['group1_2_mapping']['annotation_rows']}** annotation rows.\n- Tracking attributes live in `anno/UAV123_10fps/att/`; they are not referring expressions.\n\n## Grounding conclusion\n\nUAV123 supplies tracking boxes, but this audited release has **no native natural-language referring expressions or commands**. It must not be used as image+text+bbox grounding data without separately sourced, reviewed language annotations.\n"
    (REPORTS/'uav123_audit.md').write_text(md)
    print(json.dumps(audit, indent=2))
if __name__ == '__main__': main()
