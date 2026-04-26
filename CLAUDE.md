# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate the SQLite database (must be run before launching the app)
cd src
python generate_data.py

# Optional flags for data generation
python generate_data.py --sailors 5000 --seed 42 --db-path ../data/navy_dt.db

# Launch the Streamlit dashboard
streamlit run src/app.py
# Dashboard accessible at http://localhost:8501
```

There is no test suite — this is a POC; all verification is done manually via the Streamlit UI.

## Architecture

This is a Navy Sailor Digital Twin POC: a single authoritative view of a Sailor's career lifecycle across seven MyNavy HR domains, using 5,000 fully synthetic Sailors (no PII). The entire stack is self-contained — no external services required.

**Data flow:**
1. `generate_data.py` creates a synthetic SQLite database (`data/navy_dt.db`)
2. `app.py` queries the database and computes scenario scores
3. Streamlit renders four interactive pages: Enterprise Overview, Retention Risk, Promotion Readiness, Sailor Profile

**Key files:**
- `src/schema.sql` — complete DDL: 17 tables + 3 analytical views across 7 domains
- `src/generate_data.py` — `SailorDataGenerator` class (~755 lines); deterministic seed 42 by default; embeds realistic distribution patterns (fast-trackers, retention windows, critical-rate bonuses, medical non-deployability, billet fill gaps)
- `src/app.py` — Streamlit UI (~624 lines); `@st.cache_resource` for DB connection, `@st.cache_data` for query results; two core scoring functions

**Database design principles (from `docs/data_model.md`):**
- `sailor` table is the *current-state* identity record keyed on `dod_id` (universal key across all domains)
- `personnel_event` is the event spine — every domain change produces an audit event; designed for Kafka/Snowflake Streams migration
- Child tables hold history; analytical views (`v_active_sailor`, `v_sailor_tour_history`, `v_sailor_fitrep_recent`) are the primary query surfaces
- Schema field names intentionally mirror real Navy source systems: NSIPS, TFMMS, NTMPS, MRRS, DJMS, Navy College, CIRIMS — for easy Jupiter/Advana migration

**Scenario scoring logic (both in `src/app.py`):**
- `compute_retention_risk()` (lines 118–211): 4 weighted dimensions (Compensation, Career Stagnation, QoL, Engagement), each 0–25 pts, total 0–100
- `compute_promotion_readiness()` (lines 269–321): 5 weighted components (TIR, FITREP, exam, NEC, PQS), score 0–100 → tier (Highly Competitive / Competitive / Approaching / Needs Development)
- Both functions receive a pandas DataFrame row and return a score + gap analysis dict; designed to be swapped for ML models without touching the data layer

**Seven domains covered by the schema:**
1. Personnel — `sailor`, `fitrep`
2. Manpower — `billet`, `command`, `assignment`
3. Training — `qualification`, `advancement_exam`
4. Pay — `pay_record`
5. Medical — `medical_status`
6. Education — `education_record`
7. Recruiting — `accession`

**Synthetic data patterns (intentionally embedded for realistic demos):**
- ~20% fast-trackers with stronger evals
- ~25% Sailors within EAOS retention window (0–18 months)
- Critical rates (Cyber, Nuclear, Submarine) receive higher ASVAB scores and SRB eligibility
- ~12% non-deployable (medical/dental)
- ~80% billet fill rate with deliberate critical-NEC gaps
