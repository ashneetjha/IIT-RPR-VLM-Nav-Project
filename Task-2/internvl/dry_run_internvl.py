#!/usr/bin/env python3
"""Validate unified records and report the exact chat payload shape; never trains."""
import argparse,json
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',default='../outputs/unified_grounding_verified.jsonl');p.add_argument('--media-root',default='');p.add_argument('--limit',type=int,default=5);a=p.parse_args()
 valid=[]; bad=[]; src=Path(a.input)
 for n,line in enumerate(src.read_text().splitlines() if src.exists() else []):
  if n>=a.limit: break
  try:
   r=json.loads(line); b=r['bbox']; assert r['expression'].strip() and len(b)==4 and all(isinstance(x,(int,float)) for x in b)
   path=Path(a.media_root)/r['image_id'] if a.media_root else None
   valid.append({'source_id':r['source_id'],'image':str(path) if path else r['image_id'],'image_exists':path.exists() if path else None,'model_payload':{'image':'<image path>','conversations':[{'from':'human','value':'<image>\\n'+r['expression']},{'from':'gpt','value':'REPLACE_WITH_TEAM_BBOX_SERIALIZATION'}]}})
  except Exception as e: bad.append({'line':n+1,'error':str(e)})
 report=['# InternVL dry run','',f'- Samples tested: **{len(valid)+len(bad)}**','- Valid samples: **%d**; invalid samples: **%d**.'%(len(valid),len(bad)), '- Model/config status: no team checkpoint/configuration supplied; model was not instantiated.', '- Image loading: not attempted for empty VERIFIED input; provide `--media-root` on the server.', '- Bbox/text validation: schema requires four numeric coordinates and non-empty text.', '- Readiness: **BLOCKED — no VERIFIED grounding records and team checkpoint/training parameters are pending.**','', '## Payload shape', '```json',json.dumps(valid[:1],indent=2),'```']
 out=Path('../reports/internvl_dry_run.md');out.parent.mkdir(exist_ok=True);out.write_text('\n'.join(report)+'\n');print('\n'.join(report[:8]))
if __name__=='__main__':main()
