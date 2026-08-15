from __future__ import annotations
from typing import Any
import re
import pandas as pd

DEFAULT_WEIGHTS={'semantic':.40,'domain':.18,'career':.15,'country':.08,'affordability':.10,'data_quality':.09}

def _tokens(x:Any)->set[str]:
    return set(re.findall(r"[a-z0-9]+",str(x).lower()))

def _sim(a:Any,b:Any)->float:
    A,B=_tokens(a),_tokens(b)
    return len(A&B)/max(1,len(A|B))

def score_program(profile:dict,row:dict,weights:dict|None=None)->dict:
    w=weights or DEFAULT_WEIGHTS
    user_text=' '.join(map(str, profile.get('skills',[])+profile.get('interests',[])+[profile.get('career_goal',''),profile.get('background','')]))
    program_text=' '.join(map(str,[row.get('title',''),row.get('family',''),row.get('subfield',''),row.get('description',''),row.get('keywords','')]))
    semantic=_sim(user_text,program_text)
    domains=profile.get('preferred_domains',[])
    domain=max([_sim(d,row.get('family','')) for d in domains] or [0.4])
    career=_sim(profile.get('career_goal',''),program_text)
    countries=profile.get('preferred_countries',[])
    country=1.0 if not countries else (1.0 if str(row.get('country','')) in countries else 0.35)
    fee=float(row.get('tuition_eur',0) or 0); budget=float(profile.get('budget',0) or 0)
    affordability=.55 if not fee or not budget else (1.0 if fee<=budget else max(0.0,1-(fee-budget)/max(budget,1)))
    dq=float(row.get('data_quality',.6) or .6)
    parts={'semantic':semantic,'domain':domain,'career':career,'country':country,'affordability':affordability,'data_quality':dq}
    compatibility=100*sum(parts[k]*w[k] for k in w)
    known=[]; unknown=[]
    if row.get('min_gpa') not in ('',None):
        try:
            normalized=float(profile.get('gpa',0))/max(float(profile.get('gpa_scale',4)),1)
            req=float(row['min_gpa'])/max(float(row.get('gpa_scale',4) or 4),1)
            known.append(('Academic threshold','meets' if normalized>=req else 'does_not_meet'))
        except Exception: unknown.append('Academic threshold')
    else: unknown.append('Academic threshold')
    if row.get('language_requirement') not in ('',None): known.append(('Language','verify_evidence'))
    else: unknown.append('Language requirement')
    if fee: known.append(('Affordability','within_budget' if (not budget or fee<=budget) else 'over_budget'))
    else: unknown.append('Tuition')
    why=[]
    if semantic>.12: why.append('Your interests and skills overlap with the programme theme.')
    if domain>.45: why.append('It aligns with one of your preferred study domains.')
    if career>.08: why.append('The programme language connects with your stated career direction.')
    why_not=[]
    if countries and country<1: why_not.append('It is outside your preferred country list.')
    if affordability<.5: why_not.append('Known tuition is above your stated budget.')
    improve=[]
    if any(v=='does_not_meet' for _,v in known): improve.append('Strengthen or document academic prerequisites before applying.')
    if any(k=='Language' for k,_ in known): improve.append('Verify and prepare accepted language-test evidence.')
    if not improve: improve.append('Validate official entry requirements and strengthen programme-specific evidence.')
    return {**row,**{f'{k}_score':round(v*100,1) for k,v in parts.items()},'compatibility_score':round(compatibility,1),'known_checks':known,'unknowns':unknown,'why':why,'why_not':why_not,'improve':improve}

def recommend(profile:dict,catalogue:pd.DataFrame,weights:dict|None=None,top_k:int=20,diversity:float=.25)->pd.DataFrame:
    rows=[score_program(profile,r.to_dict(),weights) for _,r in catalogue.iterrows()]
    ranked=sorted(rows,key=lambda x:x['compatibility_score'],reverse=True)
    if diversity>0:
        selected=[]; counts={}
        for r in ranked:
            fam=r.get('family','Unknown'); penalty=counts.get(fam,0)*diversity*7
            r['_rerank']=r['compatibility_score']-penalty
        for r in sorted(ranked,key=lambda x:x['_rerank'],reverse=True):
            selected.append(r); counts[r.get('family','Unknown')]=counts.get(r.get('family','Unknown'),0)+1
            if len(selected)>=top_k: break
        ranked=selected
    return pd.DataFrame(ranked[:top_k]).drop(columns=['_rerank'],errors='ignore')
