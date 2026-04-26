# Navy Sailor Digital Twin — POC

A laptop-based proof of concept demonstrating the Sailor Digital Twin vision: a single, authoritative, event-driven view of a Sailor's career lifecycle, federated across the seven core MyNavy HR data domains.

This POC uses **fully synthetic data** for 5,000 Active Duty enlisted Sailors. No PII. No real DoD systems are touched.

## Two scenarios demonstrated

1. **Retention Risk** — identify Sailors at risk of leaving, categorized by risk type (Compensation, Career Stagnation, Quality of Life, Engagement), with recommended interventions.
2. **Promotion Readiness** — identify advancement-ready Sailors and surface the specific, actionable gaps blocking those who aren't.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│             Streamlit Dashboard (app.py)                │
│   Enterprise Overview · Retention · Promotion · Profile │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│         Scenario Logic (Python: feature engineering     │
│         + scoring rules; will become ML models in       │
│         production)                                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database (navy_dt.db)               │
│   sailor · billet · assignment · qualification ·        │
│   fitrep · pay · medical · education · accession ·      │
│   personnel_event (audit/event spine)                   │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────┐
│        Synthetic Data Generator (generate_data.py)      │
│        Mirrors NSIPS, TFMMS, NTMPS, MRRS, etc.          │
└─────────────────────────────────────────────────────────┘
```

The schema and scenario logic mirror real Navy source systems. When migrating to Jupiter/Advana in production, the scenario logic stays unchanged — only the data source swaps in.

## Quickstart

Requires Python 3.10+.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data (creates data/navy_dt.db)
cd src
python generate_data.py

# 3. Launch the Streamlit dashboard
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

## Project structure

```
navy_digital_twin/
├── README.md
├── requirements.txt
├── src/
│   ├── schema.sql          # SQLite DDL — the 7 domains as tables + views
│   ├── generate_data.py    # Synthetic data generator
│   └── app.py              # Streamlit dashboard
├── data/
│   └── navy_dt.db          # Generated database (gitignored if shared)
└── docs/
    └── data_model.md       # Domain architecture & data model design doc
```

## Configuration

Re-generate data with different parameters:

```bash
python generate_data.py --sailors 5000 --seed 42 --db-path ../data/navy_dt.db
```

The fixed seed makes runs reproducible — useful for demo consistency.

## Design notes

- **Why SQLite?** Single file, no server, fully portable. A teammate can git-clone this repo, run it, and have a working demo in 30 seconds. When we move to Jupiter, the schema migrates almost as-is to a real warehouse.
- **Why rule-based scoring instead of ML?** For a POC, transparent rules are auditable, debuggable, and demoable to leadership. In production, we'd replace the scoring functions with gradient-boosted models trained on historical separation/advancement outcomes — but the feature engineering layer stays identical.
- **Why an event stream?** The Digital Twin vision calls for an "event-driven, auditable" representation. The `personnel_event` table is the spine of that — every meaningful change in any domain produces a row. This is what enables time-travel queries and audit trails in production.

## Synthetic data — embedded patterns

The generator deliberately produces realistic patterns the models can learn from:

- ~20% of Sailors are "fast trackers" with stronger FITREPs and faster promotion velocity.
- ~25% are placed within the EAOS retention decision window (0–18 months).
- Critical-rate Sailors (Cyber, Nuclear, Submarine) get higher ASVAB scores and more SRB eligibility.
- ~12% are non-deployable due to medical/dental issues.
- ~80% billet fill rate, with deliberate critical-NEC gaps to simulate the "home grow" scenario.
- Marriage rates, dependents, and EFM enrollment scale with years of service.
