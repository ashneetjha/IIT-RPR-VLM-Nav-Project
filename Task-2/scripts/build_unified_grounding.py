#!/usr/bin/env python3
"""Build only status-preserving unified records from MM-UAVBench inspection output."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'reports'; O=ROOT/'outputs'
def lines(p):
  if not p.exists(): return []
  return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def main():
  O.mkdir(exist_ok=True); stats={}
  for status, source in [('VERIFIED','mmuav_grounding_verified.jsonl'),('REVIEW_REQUIRED','mmuav_grounding_review_required.jsonl')]:
    out=[]
    for r in lines(R/source):
      # Preserve only 4-coordinate entity candidates. Text is the source question,
      # explicitly flagged REVIEW_REQUIRED because association remains unproven.
      for n,e in enumerate(r.get('target_entities', [])):
        b=e.get('bbox',[])
        if len(b)!=4: continue
        image=(r.get('image_resources') or [{}])[0].get('path','')
        out.append({'image_id':image,'expression':r['question'],'bbox':b,'source_dataset':'MM-UAVBench','source_task':r['source_task'],'source_id':f"{r['source_id']}:{n}",'validation_status':status,'derivation_note':'REVIEW_REQUIRED: source question/entity association is not established.' if status!='VERIFIED' else ''})
    p=O/f"unified_grounding_{status.lower()}.jsonl"; p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in out)); stats[status.lower()]=len(out)
  rejected=lines(R/'mmuav_grounding_rejected.jsonl'); reasons=Counter(x['reason'] for x in rejected)
  summary={'per_dataset':{'UAV123':{'input_count':0,'verified_count':0,'review_required_count':0,'rejected_count':0,'rejection_reasons':{'native_language_expression_absent':'UAV123 audit: boxes only; no expression records emitted'}},'MM-UAVBench':{'input_count':sum(len(lines(R/f'mmuav_grounding_{x}.jsonl')) for x in ['verified','review_required','rejected']),'verified_count':stats['verified'],'review_required_count':stats['review_required'],'rejected_count':len(rejected),'rejection_reasons':dict(reasons)}}}
  (R/'unified_grounding_stats.json').write_text(json.dumps(summary,indent=2)+'\n')
  (R/'unified_grounding_stats.md').write_text('# Unified grounding statistics\n\nMM-UAVBench VERIFIED records: **0**. REVIEW_REQUIRED entity candidates: **%d**. These candidates preserve the source question but are not training ground truth. UAV123 emits zero records because the native release lacks language expressions.\n' % stats['review_required'])
  print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
