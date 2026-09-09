#!/usr/bin/env python3
"""Replace the latest point in data/observations.js with a dated observation.

Example:
  python3 tools/update_observation.py --date 2026-09-30 --price 81234 --kind monthly_close
"""
from __future__ import annotations
import argparse, json, re
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
bundle=ROOT/'data'/'observations.js'; provenance=ROOT/'data'/'provenance.json'
p=argparse.ArgumentParser();p.add_argument('--date',required=True);p.add_argument('--price',type=float,required=True);p.add_argument('--kind',choices=('monthly_close','provisional_spot'),required=True);a=p.parse_args()
dt=date.fromisoformat(a.date)
if a.price<=0: raise SystemExit('price must be positive')
text=bundle.read_text(encoding='utf-8')
text=re.sub(r'OBS_LAST_DATE:\[\d+,\d+,\d+\]',f'OBS_LAST_DATE:[{dt.year},{dt.month},{dt.day}]',text)
text=re.sub(r'OBS_LAST_PROVISIONAL:(?:true|false)',f'OBS_LAST_PROVISIONAL:{str(a.kind=="provisional_spot").lower()}',text)
text=re.sub(r'(OBS:\[.*),[^,\]]+(\],\s*\n\s*OBS_LAST_DATE:)',lambda m:f'{m.group(1)},{a.price:g}{m.group(2)}',text,flags=re.S)
bundle.write_text(text,encoding='utf-8')
meta=json.loads(provenance.read_text(encoding='utf-8'))
meta['last_observation']={'date':a.date,'value_usd':a.price,'kind':a.kind}
provenance.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated; now run tools/validate_data.py and the audit tests')
