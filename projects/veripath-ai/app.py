from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from src.assistant import respond
from src.experience_v4 import profile_completeness, next_action
from src.taxonomy import family_names, load_taxonomy, related_paths
from src.universal_engine import recommend

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='VeriPath AI', page_icon='✦', layout='wide')

@st.cache_data
def load_catalogue():
    return pd.read_csv(ROOT / 'data' / 'programme_catalogue_universal.csv')

CAT = load_catalogue()
TAX = load_taxonomy()

if 'results' not in st.session_state:
    st.session_state.results = None
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'profile' not in st.session_state:
    st.session_state.profile = {
        'background': 'Software Engineering student',
        'gpa': 0.0,
        'gpa_scale': 4.0,
        'skills': [],
        'interests': [],
        'career_goal': '',
        'preferred_domains': [],
        'preferred_countries': [],
        'budget': 12000.0,
        'language': 'English',
    }

st.markdown('''
<style>
.stApp{background:#070b11;color:#f5f7fb}.block-container{max-width:1250px;padding-top:2rem}
h1,h2,h3{letter-spacing:-.04em}.vp{padding:2rem;border:1px solid #263145;border-radius:24px;background:linear-gradient(145deg,#101826,#0a1019)}
.small{color:#9cabc1}.pill{display:inline-block;padding:.25rem .55rem;border:1px solid #33445f;border-radius:999px;margin:.1rem}
</style>
''', unsafe_allow_html=True)

st.markdown('<div class="vp"><div class="small">VERIPATH AI // STUDY UNIVERSE</div><h1>Profile → discover → compare → decide.</h1><p>Decision support for international study exploration without pretending a compatibility score is an admission probability.</p></div>', unsafe_allow_html=True)

st.subheader('1. Build your decision profile')
p = st.session_state.profile
p['background'] = st.text_input('Academic background', p.get('background',''))
p['interests'] = [x.strip() for x in st.text_input('Interests (comma separated)', ', '.join(p.get('interests',[]))).split(',') if x.strip()]
p['skills'] = [x.strip() for x in st.text_input('Skills (comma separated)', ', '.join(p.get('skills',[]))).split(',') if x.strip()]
p['career_goal'] = st.text_input('Career direction', p.get('career_goal',''))
p['preferred_domains'] = st.multiselect('Study families', family_names(TAX), default=[x for x in p.get('preferred_domains',[]) if x in family_names(TAX)])
p['preferred_countries'] = st.multiselect('Preferred countries', sorted(CAT.country.unique()), default=[x for x in p.get('preferred_countries',[]) if x in set(CAT.country)])
p['budget'] = st.number_input('Annual tuition budget (€)', 0, 100000, int(p.get('budget',12000)), 500)
st.caption(f"Profile completeness: {profile_completeness(p):.0%}")

if p['interests']:
    paths = related_paths(p['interests'], TAX)
    if paths:
        st.markdown('Related study paths: ' + ' '.join(f'<span class="pill">{x}</span>' for x in paths), unsafe_allow_html=True)

st.subheader('2. Generate transparent matches')
if st.button('Generate recommendations', type='primary'):
    st.session_state.results = recommend(p, CAT, top_k=8, diversity=.30)

results = st.session_state.results
if results is not None and len(results):
    for _, row in results.iterrows():
        with st.container(border=True):
            c1,c2 = st.columns([4,1])
            with c1:
                st.markdown(f"### {row['title']}")
                st.write(f"{row['institution']} · {row['country']} · {row['family']}")
                st.write(' '.join(row.get('why',[])) or 'Ranked from the current profile and decision weights.')
                unknowns = row.get('unknowns',[])
                if unknowns:
                    st.caption('Still verify: ' + ', '.join(map(str,unknowns)))
            with c2:
                st.metric('Compatibility', f"{row['compatibility_score']:.1f}/100")
                st.caption('Not an admission probability')
                if st.button('Shortlist', key=f"short-{row['programme_id']}") and row['programme_id'] not in st.session_state.shortlist:
                    st.session_state.shortlist.append(row['programme_id'])

section, action, reason = next_action(p, results, st.session_state.shortlist)
st.info(f"Next action → {section}: {action} {reason}")

st.subheader('3. VeriPath Copilot')
question = st.text_input('Ask about your current options', placeholder='Why is the first result recommended?')
if question:
    response = respond(question, p, results, st.session_state.shortlist)
    st.write(response['text'])

st.divider()
st.caption('SOURCE-MIRROR NOTE: this GitHub version uses a small synthetic_demo catalogue for a runnable example. The original saved V4.02 release contains the full universal catalogue, taxonomy, evaluation assets and global video background. Real programme facts must be verified against official university sources.')
