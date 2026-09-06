# UAV123 10fps audit

- Annotation files: **123**; rows: **37607**; images: **37885**; physical image folders: **91**.
- Rows have field counts: `{'4': 37607}`; invalid rows: **853**; NaN rows: **853**.
- Native boxes are `x,y,width,height`; conversion is `[x, y, x+w, y+h]`.
- `group1_2` maps to `group1/000445.jpg` through `group1/000839.jpg`, with **395** annotation rows.
- Tracking attributes live in `anno/UAV123_10fps/att/`; they are not referring expressions.

## Grounding conclusion

UAV123 supplies tracking boxes, but this audited release has **no native natural-language referring expressions or commands**. It must not be used as image+text+bbox grounding data without separately sourced, reviewed language annotations.
