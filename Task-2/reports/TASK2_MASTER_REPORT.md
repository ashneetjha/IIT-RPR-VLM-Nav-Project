# Task 2 master report — grounding audit and InternVL preparation

## Executive summary

The local UAV123 10fps release was audited read-only and official MM-UAVBench task JSONs were inspected without downloading media. Neither source currently yields a scientifically verified image + referring expression/command + target bounding-box training set: UAV123 has boxes but no native language expressions; MM-UAVBench is a 19-task multiple-choice benchmark whose boxes are question context rather than an explicit text-to-target-bbox label. No training was launched.

| Work item | Status | Evidence |
|---|---|---|
| UAV123 acquisition and audit | COMPLETE | `uav123_audit.json`, `uav123_audit.md` |
| MM-UAVBench task inspection | COMPLETE | task inventory and classified JSONL files |
| Verified grounding extraction | COMPLETE (zero verified) | `mmuav_grounding_verified.jsonl` |
| Unified schema and status-preserving build | COMPLETE | `schema/`, `build_unified_grounding.py` |
| InternVL prep and dry-run | COMPLETE / BLOCKED for training | `internvl/`, `internvl_dry_run.md` |
| Server validation / training | PENDING TEAM INPUT | checkpoint, release, parameter and server access absent |

## UAV123

The local release has 123 annotation files, 37,607 annotation rows, 37,885 image files and 91 physical image folders. All annotation rows have four fields; 853 rows contain NaN values (and are consequently invalid for direct box conversion). Native box format is `x,y,width,height`; canonical conversion is `[x, y, x+w, y+h]`. `group1_2` has 395 rows and maps to `group1/000445.jpg`–`000839.jpg`. The `att/` files are tracking attributes, not language. **No native referring-expression/text-command field was found.** See `uav123_audit.md`.

## MM-UAVBench source and inventory

Official sources inspected: Hugging Face `daisq/MM-UAVBench` task JSONs and the supporting `AI9Stars/MM-UAVBench` code. The official release has 19 task files and 5,702 records. The inventory reports fields, entity types, points, regions, four-coordinate boxes, resources and a sample per task.

There are 2,073 records with at least one four-coordinate box (2,043 rejected as MCQ box-context records and 30 retained as REVIEW_REQUIRED source records containing a literal “grounding box” prompt). The latter expand to 88 entity-level candidate rows. **VERIFIED image+text+bbox records: 0.** These candidates must not be used for fine-tuning until the source establishes an exact expression-to-entity association.

## Unified schema

`schema/unified_grounding_schema.json` fixes bbox order as `[x1,y1,x2,y2]` and distinguishes `VERIFIED` from `REVIEW_REQUIRED`. Points are excluded; no width/height was invented. The builder preserves only the source question for review candidates and records their non-ground-truth status.

## InternVL preparation

The existing Task 1 Qwen work was inspected: its converter emits role/content messages while SkyFind restructuring uses image ID, bbox and expression. The official OpenGVLab/InternVL `internvl_chat` loader was inspected; it accepts image paths plus ShareGPT-style `conversations` and `<image>` tokens. The preparation layer follows this structure but intentionally requires the team to choose bbox textual serialization, exact InternVL release/checkpoint, data root, launcher, and training parameters. The validator exposes all missing fields. Dry-run completed safely with zero VERIFIED inputs and did not instantiate a model or train.

## Missing external inputs

1. Team-approved InternVL release/checkout and compatible checkpoint.
2. Team-approved bbox output serialization and task prompting policy.
3. Server media root, writable output directory, launcher/GPU allocation, and training hyperparameters.
4. A verified source for text-to-target-bbox labels for UAV123/MM-UAVBench, or approval of a separately reviewed annotation protocol.

## Remaining work and recommended next action

Populate and review `internvl/config_template.yaml` with the team, then validate it on the GPU server. Do not train the 88 MM-UAVBench review candidates as ground truth.
