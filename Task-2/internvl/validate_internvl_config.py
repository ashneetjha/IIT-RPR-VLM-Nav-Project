#!/usr/bin/env python3
"""Lightweight preflight validator; no model checkpoint is loaded."""
import argparse, os
from pathlib import Path
REQUIRED=('internvl_repo','checkpoint','data_root','output_dir','bbox_target_template','max_dynamic_patch','per_device_train_batch_size','gradient_accumulation_steps','learning_rate','num_train_epochs','launcher')
def parse(path):
 d={}
 for line in Path(path).read_text().splitlines():
  if ':' in line and not line.lstrip().startswith('#'):
   k,v=line.split(':',1); d[k.strip()]=v.strip()
 return d
def main():
 a=argparse.ArgumentParser();a.add_argument('--config',default='config_template.yaml');x=a.parse_args(); d=parse(x.config); missing=[k for k in REQUIRED if not d.get(k) or 'REPLACE_WITH' in d[k]]
 print('CONFIG:',Path(x.config).resolve()); print('missing team parameters:', ', '.join(missing) if missing else 'none')
 for k in ('internvl_repo','checkpoint','data_root','output_dir'):
  v=d.get(k,''); print(f'{k}: {v} ({"exists" if v and "REPLACE_WITH" not in v and os.path.exists(v) else "not locally resolvable"})')
 raise SystemExit(2 if missing else 0)
if __name__=='__main__': main()
