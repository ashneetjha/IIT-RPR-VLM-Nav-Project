# MM-UAVBench official task inventory

Official source: `https://huggingface.co/datasets/daisq/MM-UAVBench/resolve/main/`. Inspected 19 task JSON files / **5702** records; no image or video media was downloaded.

The records are benchmark MCQs. They contain **5548** four-coordinate entity boxes, but the source does not provide an explicit referring-expression → target-bbox supervision field. Therefore VERIFIED count is **0**.

| Task | Records | 4-coordinate boxes | Points | Regions | Review required |
|---|---:|---:|---:|---:|---:|
| Air_Ground_Collaborative_Planning | 208 | 602 | 111 | 134 | 30 |
| Class_Agnostic_Counting | 330 | 0 | 0 | 0 | 0 |
| Cross_Object_Reasoning | 172 | 352 | 0 | 0 | 0 |
| Environment_State_Classification | 323 | 0 | 0 | 0 | 0 |
| Event_Prediction | 247 | 0 | 0 | 0 | 0 |
| Event_Tracing | 243 | 0 | 0 | 0 | 0 |
| Event_Understanding | 301 | 0 | 0 | 0 | 0 |
| Ground_Target_Planning | 325 | 1 | 1566 | 1 | 0 |
| Intent_Analysis_and_Prediction | 310 | 1615 | 0 | 0 | 0 |
| Orientation_Classification | 739 | 739 | 0 | 0 | 0 |
| Referring_Expression_Counting | 350 | 0 | 0 | 0 | 0 |
| Scene_Analysis_and_Prediction | 207 | 0 | 0 | 0 | 0 |
| Scene_Attribute_Understanding | 277 | 180 | 0 | 180 | 0 |
| Scene_Classification | 239 | 165 | 0 | 165 | 0 |
| Scene_Damage_Assessment | 350 | 0 | 0 | 0 | 0 |
| Swarm_Collaborative_Planning | 293 | 1528 | 0 | 1241 | 0 |
| Target_Backtracking | 118 | 366 | 0 | 0 | 0 |
| Temporal_Ordering | 350 | 0 | 0 | 0 | 0 |
| Urban_OCR | 320 | 0 | 0 | 0 | 0 |

Only records whose question literally mentions a “grounding box” are retained as REVIEW_REQUIRED candidates. They still require manual/experimental confirmation because no machine-readable link identifies which entity bbox is that box. All other records are REJECTED for the intended image+expression+bbox training representation.
