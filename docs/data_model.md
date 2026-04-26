# Sailor Digital Twin — Data Model & Domain Architecture

**Document purpose.** This is the design specification for the Sailor Digital Twin data foundation. It codifies the seven core domains of the MyNavy HR enterprise as a single, authoritative logical model, identifies the source system of record for each attribute, and defines the feature layers that power scenario-specific analytics.

This document is the bridge between the strategic vision in *The Digital Twin* briefing and the actual implementation. Engineers building the production system should be able to read this document and know what to build; leadership reviewing it should be able to see how the abstraction maps to concrete deliverables.

## 1. Architectural principles

The data model is built on five non-negotiable principles drawn from the Digital Twin vision:

1. **One Sailor, one identity.** Every Sailor — Active, Reserve, Civilian — has exactly one record in the authoritative `sailor` entity, keyed by DoD ID. Every other piece of data in every domain joins back to this single key. This is the architectural answer to "the absence of a single, authoritative representation of the Sailor across the enterprise."

2. **Federation, not replication.** The Digital Twin does not own the data; it federates across the source systems of record. NSIPS still owns personnel data. TFMMS still owns billets. NTMPS still owns training. The Digital Twin organizes, exposes, and adjudicates — but the source systems remain the authoritative origins.

3. **Event-driven by design.** Every meaningful change in any domain produces a row in `personnel_event`. This is the audit trail, the replay log, and the basis for downstream notifications. State at any point in time can be reconstructed from the event stream.

4. **Identity is current state; history lives in child tables.** The `sailor` entity holds *what is true now* (current rank, current command, current EAOS). All historical data — past assignments, past FITREPs, past quals — lives in child tables with a foreign key back to Sailor. This separation is what makes the model performant for both real-time queries and historical analysis.

5. **Schema mirrors source systems.** Field names, value sets, and semantics in this model deliberately echo NSIPS, TFMMS, NTMPS, MRRS, and DJMS. This is so production migration is a configuration exercise, not a re-architecture.

## 2. The seven core domains

Each domain has a primary system of record in production, an entity (or set of entities) in the data model, and a defined update cadence.

### Domain 1: Personnel

**Source of record:** NSIPS (Navy Standard Integrated Personnel System), with FITREP data from NSIPS BUPERS Online.

**Entities:**
- `sailor` — the central identity entity. Holds current paygrade, rate, primary/secondary NEC, EAOS, demographics, and current assignment snapshot.
- `fitrep` — performance evaluation history. One row per evaluation period.

**Update cadence:** Near-real-time for personnel changes; per-evaluation-cycle for FITREPs.

**Known data quality issues to plan for:** Rank/rate lag during advancement cycles (NSIPS often shows the previous paygrade for several days post-cycle). Historical FITREPs older than ~10 years may require OCR ingestion from archived paper records.

### Domain 2: Manpower

**Source of record:** TFMMS (Total Force Manpower Management System) for billets; NSIPS / MAPP for assignments.

**Entities:**
- `command` — every command (UIC) in the Navy, with type (Sea/Shore/Overseas), homeport, region, and fleet.
- `billet` — every authorized position. A billet has a rate requirement, paygrade requirement, optional NEC requirement, sea/shore designation, and a critical flag.
- `assignment` — a Sailor's tour at a billet. Multiple historical rows per Sailor; one current row.

**Update cadence:** Monthly for billet authorizations (TFMMS); real-time at PCS for assignments (NSIPS/MAPP).

**Critical design decision:** Billet and assignment are separate entities. A *billet* is a slot that needs to be filled (e.g., MM1 with NEC 3354 on USS Bainbridge); an *assignment* is a Sailor filling that billet for a specific period. Same billet → many assignments over time; same Sailor → many assignments through career. Mixing these is one of the most common modeling mistakes in HR systems and breaks downstream analytics.

### Domain 3: Training

**Source of record:** NTMPS (Navy Training Management Planning System), FLTMPS (Fleet Training Management Planning System), CeTARS (Corporate enterprise Training Activity Resource System).

**Entities:**
- `qualification` — every qualification a Sailor has earned. Includes NECs, PQS items, watch quals, and school completions. Each row has a date earned, optional currency expiration, and a current/lapsed flag.
- `advancement_exam` — past advancement examination history with standard scores.
- `nec` (reference) — catalog of NEC codes with criticality flags and typical currency intervals.

**Update cadence:** Daily batch from training systems.

**Known data quality issues:** Currency expiration dates are often missing in the source — many quals were created without explicit expiration tracking. The Digital Twin should compute expected currency from `nec.typical_currency_months` when source dates are NULL.

### Domain 4: Pay

**Source of record:** DJMS (Defense Joint Military Pay System) flowing through DFAS; SRB eligibility historically scattered across NSIPS, Career Management Systems, and downstream computations.

**Entities:**
- `pay_record` — current pay snapshot per Sailor: base pay, BAH, BAS, sea pay, special pays, and SRB zone/multiplier/window.

**Update cadence:** Bi-weekly from DJMS for pay; SRB updates are event-driven on contract events.

**Critical issue this domain solves:** SRB eligibility calculations historically had multiple sources of truth, contributing to erroneous payments and missed retention opportunities. The Digital Twin makes the authoritative SRB record visible and auditable. This aligns with the briefing's "N16 and N10 are coordinating with DFAS on Total Force Pay modernization" initiative.

### Domain 5: Medical Readiness

**Source of record:** MRRS (Medical Readiness Reporting System); BUMED systems for clinical detail.

**Entities:**
- `medical_status` — current readiness picture per Sailor: PHA date and due date, dental class, immunization currency, deployable status, and any deployment-limiting condition.

**Update cadence:** Daily.

**What this enables:** The Medical Readiness Trajectory scenario — predicting which Sailors will go non-deployable in the next 6–12 months based on PHA periodicity, dental class drift, and immunization expirations. This was identified as a future scenario in the kickoff conversation.

### Domain 6: Education

**Source of record:** Navy College / NPDB.

**Entities:**
- `education_record` — completed and in-progress education credentials beyond initial accession (degrees, schools, tuition assistance usage).

**Update cadence:** Quarterly.

**Known data quality issues:** TA-funded course completions often lag actual completion by 60–90 days due to grade-reporting delays from civilian institutions.

### Domain 7: Recruiting / Accession

**Source of record:** CIRIMS (Centralized Recruit Information Management System), PRIDE.

**Entities:**
- `accession` — point-of-entry record per Sailor: ASVAB scores (AFQT and subtests), accession source, enlistment program, contract term, boot camp grad date, A-school performance.

**Update cadence:** Captured at accession; rarely updated thereafter.

**What this enables:** The Accession-to-First-Tour-Success scenario — connecting recruiting profile to A-school performance to first command outcomes, to inform both recruiting strategy and initial detailing.

## 3. Cross-cutting: the personnel event stream

The `personnel_event` table is the spine of the event-driven architecture. It is not a domain in itself; it is a cross-cutting audit and orchestration layer.

Every meaningful change in any domain produces an event row containing:
- The DoD ID of the affected Sailor
- An event type (ACCESSION, ADVANCEMENT, REPORT_ABOARD, NEC_AWARDED, FITREP_SUBMITTED, etc.)
- A timestamp
- The source system that generated the event
- A JSON payload with event-specific details

This table is what makes the twin auditable. State at any historical point can be reconstructed by replaying events. Downstream consumers (notifications, dashboards, ML feature pipelines) subscribe to event streams rather than polling the source tables.

In production, this layer is fed by Jupiter's orchestration capability and the Mulesoft/Snowflake HR Data Exchange shown on Slide 12 of the briefing.

## 4. Feature layers — turning data into scenarios

The raw schema gives us federated data. The *feature layer* is what turns that data into scenario-specific signals. Features are computed views or pre-aggregated tables that scenario models consume directly.

### Retention Risk feature layer

| Feature | Computation | Source domains |
|---|---|---|
| `months_to_eaos` | EAOS date − today | Personnel |
| `srb_eligibility_status` | SRB zone, multiplier, days until window closes | Pay |
| `tours_at_sea_consecutive` | Count of back-to-back sea tours | Manpower |
| `geographic_stability_score` | Number of moves in last 6 yrs, distance moved | Manpower |
| `promotion_velocity_pct_peer` | Time-in-rate vs. peer cohort median | Personnel + FITREP |
| `fitrep_trait_trend` | Slope of trait scores over last 3 FITREPs | Personnel |
| `nec_currency_status` | % of held NECs currently current | Training |
| `medical_deployable` | Current deployable status | Medical |
| `dependents_complexity` | Family size, EFM enrollment | Personnel |
| `nec_criticality` | Is the NEC on the critical-NEC list | Personnel + Training |

Output: a multi-dimensional risk score categorizing Sailors by primary risk driver (Compensation / Career Stagnation / Quality of Life / Engagement) with recommended interventions tied to actual programs.

### Promotion Readiness feature layer

| Feature | Computation | Source domains |
|---|---|---|
| `tir_eligibility_status` | Time-in-rate vs. minimum required for next paygrade | Personnel |
| `tis_eligibility_status` | Time-in-service vs. minimum | Personnel |
| `pqs_completion_pct` | Required PQS for next paygrade — % complete | Training |
| `nec_completion_required` | NECs required vs. held for next-paygrade billets | Training + Manpower |
| `exam_score_history` | Past advancement exam standard scores | Training |
| `fitrep_promote_recommendation_rate` | EP/MP rate over last 3 FITREPs | Personnel |
| `peer_competitiveness_pct` | Composite score percentile within peer group | Computed |

Output: readiness tier (Highly Competitive / Competitive / Approaching / Needs Development), a list of specific gaps, and a prioritized action plan.

### Reuse across scenarios

The five scenarios identified — Retention, Promotion, Detailing, Medical Readiness, Accession-to-First-Tour — share substantial feature overlap. Building the data model to support all five from day one means features computed for one scenario become inputs to others:

| Feature | Retention | Promotion | Detailing | Medical | Accession |
|---|---|---|---|---|---|
| Time-in-rate | × | × | × |  |  |
| FITREP history | × | × | × |  |  |
| NEC currency | × | × | × |  |  |
| Sea/shore tour history | × |  | × |  |  |
| Medical deployability | × |  | × | × |  |
| Family/EFM | × |  | × |  |  |
| ASVAB scores |  |  |  |  | × |
| Peer cohort comparison | × | × |  |  | × |

This is why investing in the data model first — before building any single scenario — pays dividends. The same feature pipeline serves multiple analytics.

## 5. Source-system migration path

The POC runs on synthetic data in SQLite for portability and PII safety. The production system targets Jupiter / Advana with feeds from the source systems below.

| Domain | POC source (synthetic) | Production source | Update cadence |
|---|---|---|---|
| Personnel | `generate_data.py` | NSIPS | Near-real-time |
| Manpower (billets) | `generate_data.py` | TFMMS | Monthly |
| Manpower (assignments) | `generate_data.py` | NSIPS / MAPP | Real-time at PCS |
| Training | `generate_data.py` | NTMPS / FLTMPS / CeTARS | Daily batch |
| Pay | `generate_data.py` | DJMS / DFAS | Bi-weekly |
| Medical | `generate_data.py` | MRRS / BUMED | Daily |
| Education | `generate_data.py` | Navy College / NPDB | Quarterly |
| Recruiting | `generate_data.py` | CIRIMS / PRIDE | At accession |

The schema field names mirror the production sources, so migration is primarily a configuration of data pipelines into the existing schema, not a re-design.

## 6. What this design does NOT include (yet)

Items deliberately deferred for the POC scope:

- **Reserve and Civilian populations.** POC is Active Duty enlisted only. Adding Reserve and Civilian requires extending `sailor` with status discriminator and adding source-system mappings (RESCAS for Reserve, DCPDS for Civilian).
- **Officer detailing logic.** The model accommodates officers schematically but the POC scope is enlisted. Officer-specific entities (designators, subspecialties, AQDs) would extend the schema.
- **Real-time event streaming.** The POC populates `personnel_event` synchronously alongside data generation. Production needs Kafka / Snowflake Streams or equivalent.
- **Granular pay history.** The POC holds the latest pay snapshot. Production needs a temporal pay model with effective-dated rows.
- **Command climate / survey data.** Referenced in the retention feature layer but not yet in the schema. Would require ingestion from DEOCS or similar surveys.

These are all natural extensions of the current model, not redesigns.
