#!/usr/bin/env python3
"""Convert verified unified records to OpenGVLab InternVL chat records.

The official dataset loader accepts `image` plus ShareGPT-style `conversations`.
The bbox textual serialization is a team decision, so this tool refuses placeholders.
"""
import argparse, json
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument('--input',default='../outputs/unified_grounding_verified.jsonl'); p.add_argument('--output',default='../outputs/internvl_grounding.jsonl'); p.add_argument('--bbox-template',required=True,help='Python format, e.g. "[x1={x1}, y1={y1}, x2={x2}, y2={y2}]"')
 a=p.parse_args();
 if 'REPLACE_WITH' in a.bbox_template: raise SystemExit('bbox template is a required team decision')
 src=Path(a.input); out=Path(a.output); out.parent.mkdir(exist_ok=True); count=0
 with out.open('w') as f:
  for line in src.read_text().splitlines() if src.exists() else []:
   r=json.loads(line); x1,y1,x2,y2=r['bbox']; target=a.bbox_template.format(x1=x1,y1=y1,x2=x2,y2=y2)
   ex={'id':r['source_id'],'image':r['image_id'],'conversations':[{'from':'human','value':'<image>\n'+r['expression']},{'from':'gpt','value':target}]}
   f.write(json.dumps(ex,ensure_ascii=False)+'\n'); count+=1
 print(f'Wrote {count} InternVL records to {out}')
if __name__=='__main__': main()
