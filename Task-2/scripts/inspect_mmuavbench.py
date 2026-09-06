#!/usr/bin/env python3
"""Inspect official MM-UAVBench task JSONs without downloading media."""
import csv, json, urllib.request
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; REPORTS=ROOT/'reports'
BASE='https://huggingface.co/datasets/daisq/MM-UAVBench/resolve/main/tasks/'
TASKS=['Air_Ground_Collaborative_Planning','Class_Agnostic_Counting','Cross_Object_Reasoning','Environment_State_Classification','Event_Prediction','Event_Tracing','Event_Understanding','Ground_Target_Planning','Intent_Analysis_and_Prediction','Orientation_Classification','Referring_Expression_Counting','Scene_Analysis_and_Prediction','Scene_Attribute_Understanding','Scene_Classification','Scene_Damage_Assessment','Swarm_Collaborative_Planning','Target_Backtracking','Temporal_Ordering','Urban_OCR']
def get(task):
    with urllib.request.urlopen(BASE+task+'.json', timeout=60) as r: return json.load(r)
def main():
  REPORTS.mkdir(exist_ok=True); inventory=[]; buckets={x:[] for x in ('VERIFIED','REVIEW_REQUIRED','REJECTED')}
  for task in TASKS:
    records=get(task); entity_types=Counter(); points=regions=boxes4=0; review_count=0
    for rec in records:
      ents=rec.get('target_entities',[]); q=rec.get('question',''); has4=False
      for e in ents:
        typ=e.get('entity_type','missing'); entity_types[typ]+=1; b=e.get('bbox',[])
        if len(b)==2: points+=1
        if typ=='region': regions+=1
        if len(b)==4: boxes4+=1; has4=True
      # A literal grounding-box prompt is a candidate only: it does not identify a
      # target bbox in machine-readable form, so never elevate it to VERIFIED.
      status='REVIEW_REQUIRED' if has4 and 'grounding box' in q.lower() else 'REJECTED'
      reason = ('The question names a grounding box but no source field maps that text to a specific bbox.' if status=='REVIEW_REQUIRED' else ('No four-coordinate bbox exists.' if not has4 else 'Boxes condition a multiple-choice question; no explicit text-to-target-bbox mapping is supplied.'))
      compact={'source_dataset':'MM-UAVBench','source_task':task,'source_id':rec.get('question_id'),'validation_status':status,'reason':reason,'question':q,'image_resources':rec.get('metadata',{}).get('data_resources',[]),'target_entities':ents}
      buckets[status].append(compact); review_count += status=='REVIEW_REQUIRED'
    sample=records[0] if records else {}
    inventory.append({'task_name':task,'record_count':len(records),'fields_present':'|'.join(sample.keys()),'target_entity_types':json.dumps(dict(entity_types),sort_keys=True),'point_annotations':points,'region_annotations':regions,'four_coordinate_boxes':boxes4,'text_field':'question','image_resource_field':'metadata.data_resources','source_id_field':'question_id','review_required_records':review_count,'sample_record':json.dumps(sample,ensure_ascii=False)})
  for status, recs in buckets.items():
    with (REPORTS/f"mmuav_grounding_{status.lower()}.jsonl").open('w') as f:
      for r in recs: f.write(json.dumps(r,ensure_ascii=False)+'\n')
  with (REPORTS/'mmuav_task_inventory.json').open('w') as f: json.dump(inventory,f,ensure_ascii=False,indent=2)
  cols=list(inventory[0]);
  with (REPORTS/'mmuav_task_inventory.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(inventory)
  total=sum(x['record_count'] for x in inventory); four=sum(x['four_coordinate_boxes'] for x in inventory)
  md=['# MM-UAVBench official task inventory','',f'Official source: `{BASE[:-6]}`. Inspected {len(inventory)} task JSON files / **{total}** records; no image or video media was downloaded.','',f'The records are benchmark MCQs. They contain **{four}** four-coordinate entity boxes, but the source does not provide an explicit referring-expression → target-bbox supervision field. Therefore VERIFIED count is **0**.','', '| Task | Records | 4-coordinate boxes | Points | Regions | Review required |','|---|---:|---:|---:|---:|---:|']
  md += [f"| {x['task_name']} | {x['record_count']} | {x['four_coordinate_boxes']} | {x['point_annotations']} | {x['region_annotations']} | {x['review_required_records']} |" for x in inventory]
  md += ['', 'Only records whose question literally mentions a “grounding box” are retained as REVIEW_REQUIRED candidates. They still require manual/experimental confirmation because no machine-readable link identifies which entity bbox is that box. All other records are REJECTED for the intended image+expression+bbox training representation.']
  (REPORTS/'mmuav_task_inventory.md').write_text('\n'.join(md)+'\n')
  print(json.dumps({'records':total, **{k:len(v) for k,v in buckets.items()}},indent=2))
if __name__=='__main__': main()
