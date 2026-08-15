# VeriPath AI V3.0 — Study Universe

VeriPath V3 is a universal study-discovery and decision-support platform. It is deliberately broader than an engineering/AI recommender and is designed so the academic taxonomy can expand without application-code changes.

## What changed

- Data-driven taxonomy spanning 50+ academic families and hundreds of subfields.
- New **Explore the World of Study** experience with search and cross-disciplinary bridges.
- Guided five-step profile builder with profile import/export and diverse personas.
- Routed product experience: Welcome, Profile, Explore, Discover, Programme Detail, Shortlist, Compare, Scenario Lab, Application Readiness, Assistant, Data Health, Evaluation Lab, Methodology.
- Genuine layered motion/parallax-style hero component with reduced-motion accessibility support.
- Recommendation logic that keeps **compatibility, known checks, affordability, data quality and uncertainty separate**.
- Diversity-aware reranking and cross-disciplinary discovery.
- Grounded deterministic VeriPath Assistant that refuses to invent unknown admissions facts.
- Synthetic trainable-weight pipeline with profile-level split to prevent leakage.
- Evaluation support for Precision@K, Recall@K, HitRate@K, MRR, MAP and NDCG@K; coverage/diversity/novelty hooks documented.
- Explicit separation of real/verified-seed and synthetic discovery data.

## Scientific honesty

A compatibility score is **not an admission probability**.

Synthetic programme records exist only to demonstrate universal discovery breadth. They are labelled `synthetic_demo` and are not real university offerings. Real programme facts must be verified against official sources before decisions.

## Run on Windows

Double-click `START_VERIPATH.bat`.

## Manual run

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Train the lightweight ranking weights

```bash
python train_ranker.py
```

## Run the synthetic evaluation benchmark

```bash
python run_benchmark_v300.py
```

## Run tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

See `docs/` for architecture, taxonomy, governance, ranking, design, audit and roadmap notes.

## V3.2 Journey Rebuild

This build focuses on three pain points:
- a clearer guided journey so users do not feel lost,
- a more context-aware copilot with multi-turn memory,
- richer visuals including illustrative university cards and a stronger landing experience.

### Honest note on images
Because live web retrieval is disabled in the build environment, the university images in this release are generated illustrative institution cards, not downloaded official campus photos. They are meant to improve clarity and visual hierarchy without pretending to be official assets.

## V4.01 Video Background Update
The Home hero now uses the bundled `assets/hero-background.mp4` as its live background, with readability overlays and cursor-reactive depth layers.

## V4.02 Global Background Update

The uploaded video now acts as a fixed full-application background. Home placement was rebuilt so the main journey cards are visible and consistently composed instead of appearing below a boxed video hero. See `docs/RELEASE_NOTES_V402.md` for details.
