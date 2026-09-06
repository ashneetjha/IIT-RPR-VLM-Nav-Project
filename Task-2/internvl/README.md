# InternVL preparation

Reviewed target: the current official [OpenGVLab/InternVL](https://github.com/OpenGVLab/InternVL) `internvl_chat` training loader. Its meta file names an annotation JSON/JSONL file and root; each image example uses `image` and ShareGPT-style `conversations` entries (`from` / `value`), with `<image>` in the human value. This preparation layer follows that loader shape. It does **not** claim a particular InternVL release/checkpoint: the team-provided choice remains required.

Transformation (only for VERIFIED input):

```text
unified record [image_id, expression, bbox]
  -> validated normalized record [x1,y1,x2,y2]
  -> {"image": image_id,
      "conversations": [{"from":"human","value":"<image>\n" + expression},
                        {"from":"gpt","value": bbox_target_template(...)}]}
```

InternVL accepts assistant text but does not prescribe a project bbox serialization. `bbox_target_template` is therefore deliberately a required team decision; the converter refuses a placeholder. REVIEW_REQUIRED candidates are excluded from training conversion.

From this directory:

```bash
python validate_internvl_config.py --config config_template.yaml
python prepare_internvl_dataset.py --bbox-template '[x1={x1}, y1={y1}, x2={x2}, y2={y2}]'
python dry_run_internvl.py --media-root /server/mmuavbench
```
