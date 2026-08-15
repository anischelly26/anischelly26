# VeriPath AI V4.02 — Study-Abroad Discovery & Decision Support

VeriPath is an AI-assisted international-study discovery and decision-support system. It is designed to help a student go from a vague profile to a structured set of study options **without turning a recommendation score into a fake admission probability**.

## Product journey

```text
Student profile
      ↓
Explore academic universe
      ↓
Transparent recommendations
      ↓
Known checks + unknowns + affordability + data quality
      ↓
Shortlist / compare
      ↓
Decision tasks
      ↓
Grounded VeriPath Copilot
```

## Core ideas in the saved V4.02 release

- Data-driven academic taxonomy spanning many study families and subfields
- Guided student profile and cross-disciplinary discovery
- Compatibility scoring from interests, domain, career direction, country, affordability and data quality
- **Known requirements and unknown requirements shown separately**
- Diversity-aware reranking so one academic family does not dominate every result
- Shortlist, comparison and decision-planning workflows
- Grounded deterministic assistant that refuses to invent missing admissions facts
- Evaluation tooling for ranking quality and recommendation behaviour
- Explicit separation between verified/seed data and `synthetic_demo` discovery records
- V4 experience with the bundled video acting as a fixed full-application background

## Scientific / product honesty

**Compatibility ≠ admission probability.**

VeriPath does not claim that a 75/100 compatibility score means a 75% chance of admission. Known evidence, affordability, data quality and missing information are kept visible as separate decision dimensions.

Synthetic records are labelled as demo/discovery records. They are **not real university offerings**, and real programme requirements must be verified against official university sources before applying.

## Run this GitHub source mirror

```bash
pip install -r requirements.txt
streamlit run app.py
```

The GitHub mirror includes a small `synthetic_demo` catalogue and taxonomy so the recommendation engine and decision experience can be explored immediately.

## Main source components

```text
app.py                         # runnable Streamlit source-mirror experience
src/universal_engine.py        # compatibility + transparent decision signals
src/taxonomy.py                # academic-family/subfield discovery
src/experience_v4.py           # journey/progress/next-action logic
src/assistant.py               # grounded decision copilot
data/                          # lightweight demo catalogue + taxonomy
```

## Original release vs GitHub mirror

The latest exact saved artifact currently available is **`VeriPath_AI_V402_Global_Background_Fixed.zip`**. The original release contains the complete universal catalogue/taxonomy, evaluation assets, documentation, tests and the global MP4 background.

This GitHub folder is a readable/runnable source mirror rather than a byte-for-byte copy of every large/binary release asset. See [`../SOURCE_RELEASES.md`](../SOURCE_RELEASES.md) for the original archive name and SHA-256 hash.

A later V4.03 build was produced during development, but its exact ZIP is not currently present in the saved file library, so V4.02 is **not** being relabelled as V4.03 here.

---

**Anis Chelly // AI × Software Engineering // EdTech & Decision Support**
