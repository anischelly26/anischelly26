from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable

ROOT=Path(__file__).resolve().parents[1]
TAXONOMY_PATH=ROOT/'data'/'study_taxonomy.json'

def load_taxonomy(path:Path=TAXONOMY_PATH)->dict:
    return json.loads(path.read_text(encoding='utf-8'))

def family_names(tax:dict|None=None)->list[str]:
    tax=tax or load_taxonomy(); return [x['name'] for x in tax['families']]

def all_subfields(tax:dict|None=None)->list[str]:
    tax=tax or load_taxonomy(); return [s['name'] for f in tax['families'] for s in f['subfields']]

def search_taxonomy(query:str,tax:dict|None=None)->list[dict]:
    tax=tax or load_taxonomy(); q=query.strip().lower(); out=[]
    for f in tax['families']:
        subs=[s['name'] for s in f['subfields'] if q in s['name'].lower()] if q else [s['name'] for s in f['subfields']]
        if q in f['name'].lower() or subs: out.append({'family':f['name'],'subfields':subs})
    return out

def related_paths(interests:Iterable[str],tax:dict|None=None)->list[str]:
    tax=tax or load_taxonomy(); bridges=tax.get('bridges',{}); words=' '.join(interests).lower(); found=[]
    for k,vals in bridges.items():
        if k.lower() in words: found.extend(vals)
    for f in tax['families']:
        for s in f['subfields']:
            if any(tok in s['name'].lower() for tok in words.split() if len(tok)>4): found.append(s['name'])
    return list(dict.fromkeys(found))[:12]
