#!/usr/bin/env python3
"""Validate the static data contract before publishing the model."""
from __future__ import annotations
import json
import re
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=(ROOT/'data'/'observations.js').read_text(encoding='utf-8')
PROVENANCE=json.loads((ROOT/'data'/'provenance.json').read_text(encoding='utf-8'))

def values(key: str) -> list[float]:
    m=re.search(rf'{key}:\[(.*?)\]',DATA,re.S)
    if not m: raise SystemExit(f'missing {key}')
    return [float(x) for x in m.group(1).split(',') if x.strip()]

obs=values('OBS')
last=values('OBS_LAST_DATE')
assert len(obs)>=12 and all(v>0 for v in obs), 'prices must be positive'
assert len(last)==3, 'last date must have year/month/day'
last_date=date(*map(int,last))
meta=date.fromisoformat(PROVENANCE['last_observation']['date'])
assert last_date==meta, 'data bundle and provenance disagree about the last date'
assert obs[-1]==PROVENANCE['last_observation']['value_usd'], 'last value disagrees with provenance'
assert PROVENANCE['last_observation']['kind'] in {'monthly_close','provisional_spot'}
print(f'ok: {len(obs)} observations through {last_date.isoformat()} ({PROVENANCE["last_observation"]["kind"]})')
