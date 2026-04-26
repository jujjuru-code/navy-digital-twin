-- =============================================================================
-- NAVY SAILOR DIGITAL TWIN - DATABASE SCHEMA (POC)
-- =============================================================================
-- Implements the 7-domain logical data model for the Sailor Digital Twin.
-- All synthetic data; no PII. Designed to mirror real Navy source systems
-- (NSIPS, TFMMS, NTMPS, MRRS, etc.) for eventual production migration.
--
-- Domain mapping:
--   Personnel       -> sailor, fitrep
--   Manpower        -> billet, command, assignment
--   Training        -> nec, qualification
--   Pay             -> pay_record
--   Medical         -> medical_status
--   Education       -> education_record
--   Recruiting      -> accession
--   Cross-cutting   -> personnel_event (audit/event spine)
-- =============================================================================

PRAGMA foreign_keys = ON;

-- =============================================================================
-- REFERENCE TABLES (lookup data)
-- =============================================================================

CREATE TABLE IF NOT EXISTS rate (
    rate_code        TEXT PRIMARY KEY,    -- e.g., 'MM', 'CTN', 'HM'
    rate_name        TEXT NOT NULL,        -- e.g., 'Machinist''s Mate'
    community        TEXT NOT NULL,        -- e.g., 'Engineering', 'Cyber', 'Medical'
    is_critical      INTEGER NOT NULL DEFAULT 0  -- 1 = on critical NEC/rating list
);

CREATE TABLE IF NOT EXISTS nec (
    nec_code         TEXT PRIMARY KEY,    -- e.g., '3354', '0000'
    nec_title        TEXT NOT NULL,
    related_rate     TEXT,
    is_critical      INTEGER NOT NULL DEFAULT 0,
    typical_currency_months  INTEGER,    -- how often re-qual is needed
    FOREIGN KEY (related_rate) REFERENCES rate(rate_code)
);

CREATE TABLE IF NOT EXISTS command (
    command_id       TEXT PRIMARY KEY,    -- UIC equivalent
    command_name     TEXT NOT NULL,
    command_type     TEXT NOT NULL,       -- 'Sea', 'Shore', 'Overseas'
    homeport         TEXT,
    region           TEXT,                -- e.g., 'Norfolk', 'San Diego'
    fleet            TEXT                 -- e.g., 'Atlantic', 'Pacific', 'CNRC'
);

-- =============================================================================
-- DOMAIN 1: PERSONNEL (CORE SAILOR ENTITY)
-- =============================================================================
-- Source system equivalent: NSIPS
-- Holds identity + current state. History lives in child tables.
-- =============================================================================

CREATE TABLE IF NOT EXISTS sailor (
    dod_id              TEXT PRIMARY KEY,         -- 10-digit synthetic ID
    rate_code           TEXT NOT NULL,
    paygrade            TEXT NOT NULL,            -- E1-E9
    primary_nec         TEXT,
    secondary_nec       TEXT,
    enlistment_date     DATE NOT NULL,
    eaos                DATE NOT NULL,            -- End of Active Obligated Service
    years_of_service    REAL NOT NULL,
    time_in_rate_months INTEGER NOT NULL,
    -- Demographics relevant to retention modeling (no PII)
    age                 INTEGER NOT NULL,
    gender              TEXT,                     -- 'M', 'F', 'X'
    marital_status      TEXT,                     -- 'Single', 'Married', 'Divorced'
    num_dependents      INTEGER NOT NULL DEFAULT 0,
    has_efm             INTEGER NOT NULL DEFAULT 0,  -- Exceptional Family Member
    -- Current assignment snapshot (denormalized for query performance)
    current_command_id  TEXT,
    current_billet_id   TEXT,
    -- Status flags
    status              TEXT NOT NULL DEFAULT 'Active',  -- Active, Separated, Retired
    separation_date     DATE,
    separation_reason   TEXT,                     -- For training the retention model
    FOREIGN KEY (rate_code) REFERENCES rate(rate_code),
    FOREIGN KEY (primary_nec) REFERENCES nec(nec_code),
    FOREIGN KEY (current_command_id) REFERENCES command(command_id)
);

CREATE INDEX IF NOT EXISTS idx_sailor_status ON sailor(status);
CREATE INDEX IF NOT EXISTS idx_sailor_paygrade ON sailor(paygrade);
CREATE INDEX IF NOT EXISTS idx_sailor_eaos ON sailor(eaos);
CREATE INDEX IF NOT EXISTS idx_sailor_command ON sailor(current_command_id);

-- =============================================================================
-- DOMAIN 1 (cont.): FITREP / EVAL HISTORY
-- =============================================================================
-- Source system equivalent: NSIPS BUPERS Online
-- =============================================================================

CREATE TABLE IF NOT EXISTS fitrep (
    fitrep_id           TEXT PRIMARY KEY,
    dod_id              TEXT NOT NULL,
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    paygrade_at_eval    TEXT NOT NULL,
    -- 5-trait avg (Mil Bearing, Adaptability, Teamwork, Mission, Leadership)
    trait_avg           REAL NOT NULL,           -- 1.0 - 5.0
    -- Promotion recommendation: SP=Significant Problems, P=Progressing,
    -- PP=Promotable, MP=Must Promote, EP=Early Promote
    promotion_recommendation TEXT NOT NULL,
    summary_group_size  INTEGER,                 -- For competitive context
    summary_group_avg   REAL,
    is_competitive      INTEGER NOT NULL DEFAULT 1,  -- 0 = concurrent/special
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id)
);

CREATE INDEX IF NOT EXISTS idx_fitrep_sailor ON fitrep(dod_id);
CREATE INDEX IF NOT EXISTS idx_fitrep_period ON fitrep(period_end);

-- =============================================================================
-- DOMAIN 2: MANPOWER (BILLETS + ASSIGNMENTS)
-- =============================================================================
-- Source system equivalents: TFMMS (billets), NSIPS/MAPP (assignments)
-- =============================================================================

CREATE TABLE IF NOT EXISTS billet (
    billet_id           TEXT PRIMARY KEY,         -- BIN equivalent
    command_id          TEXT NOT NULL,
    rate_required       TEXT NOT NULL,
    paygrade_required   TEXT NOT NULL,
    nec_required        TEXT,                     -- Primary NEC requirement
    nec_required_secondary TEXT,
    sea_shore           TEXT NOT NULL,            -- 'Sea', 'Shore'
    is_critical         INTEGER NOT NULL DEFAULT 0,
    is_filled           INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (command_id) REFERENCES command(command_id),
    FOREIGN KEY (rate_required) REFERENCES rate(rate_code),
    FOREIGN KEY (nec_required) REFERENCES nec(nec_code)
);

CREATE INDEX IF NOT EXISTS idx_billet_command ON billet(command_id);
CREATE INDEX IF NOT EXISTS idx_billet_filled ON billet(is_filled);
CREATE INDEX IF NOT EXISTS idx_billet_critical ON billet(is_critical);

CREATE TABLE IF NOT EXISTS assignment (
    assignment_id       TEXT PRIMARY KEY,
    dod_id              TEXT NOT NULL,
    billet_id           TEXT NOT NULL,
    command_id          TEXT NOT NULL,            -- Denormalized for fast queries
    report_date         DATE NOT NULL,
    detach_date         DATE,                     -- NULL = current assignment
    sea_shore           TEXT NOT NULL,
    tour_type           TEXT,                     -- 'Standard', 'Extended', 'Short'
    is_current          INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id),
    FOREIGN KEY (billet_id) REFERENCES billet(billet_id),
    FOREIGN KEY (command_id) REFERENCES command(command_id)
);

CREATE INDEX IF NOT EXISTS idx_assignment_sailor ON assignment(dod_id);
CREATE INDEX IF NOT EXISTS idx_assignment_billet ON assignment(billet_id);
CREATE INDEX IF NOT EXISTS idx_assignment_current ON assignment(is_current);

-- =============================================================================
-- DOMAIN 3: TRAINING (QUALIFICATIONS, NECs, PQS)
-- =============================================================================
-- Source system equivalents: NTMPS, FLTMPS, CeTARS
-- =============================================================================

CREATE TABLE IF NOT EXISTS qualification (
    qual_id             TEXT PRIMARY KEY,
    dod_id              TEXT NOT NULL,
    qual_type           TEXT NOT NULL,            -- 'NEC', 'PQS', 'Watch', 'School'
    qual_code           TEXT NOT NULL,            -- e.g., NEC code or PQS identifier
    qual_title          TEXT NOT NULL,
    date_earned         DATE NOT NULL,
    currency_expires    DATE,                     -- NULL if no currency requirement
    is_current          INTEGER NOT NULL DEFAULT 1,
    granting_command    TEXT,
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id),
    FOREIGN KEY (granting_command) REFERENCES command(command_id)
);

CREATE INDEX IF NOT EXISTS idx_qual_sailor ON qualification(dod_id);
CREATE INDEX IF NOT EXISTS idx_qual_type ON qualification(qual_type);
CREATE INDEX IF NOT EXISTS idx_qual_currency ON qualification(is_current);

CREATE TABLE IF NOT EXISTS advancement_exam (
    exam_id             TEXT PRIMARY KEY,
    dod_id              TEXT NOT NULL,
    exam_cycle          TEXT NOT NULL,            -- e.g., '2025-Cycle-1'
    target_paygrade     TEXT NOT NULL,
    standard_score      INTEGER,                  -- 0-100
    passed              INTEGER NOT NULL DEFAULT 0,
    advanced            INTEGER NOT NULL DEFAULT 0,
    exam_date           DATE NOT NULL,
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id)
);

CREATE INDEX IF NOT EXISTS idx_exam_sailor ON advancement_exam(dod_id);

-- =============================================================================
-- DOMAIN 4: PAY
-- =============================================================================
-- Source system equivalents: DJMS, DFAS
-- For POC we hold the latest pay snapshot per Sailor.
-- =============================================================================

CREATE TABLE IF NOT EXISTS pay_record (
    dod_id              TEXT PRIMARY KEY,
    base_pay_monthly    REAL NOT NULL,
    bah_monthly         REAL NOT NULL DEFAULT 0,
    bas_monthly         REAL NOT NULL DEFAULT 0,
    sea_pay_monthly     REAL NOT NULL DEFAULT 0,
    special_pay_monthly REAL NOT NULL DEFAULT 0,  -- Hazardous, dive, sub, flight
    -- Selective Reenlistment Bonus
    srb_zone            TEXT,                     -- 'A', 'B', 'C', NULL
    srb_multiplier      REAL,                     -- e.g., 1.5, 4.0, 6.0
    srb_eligible_until  DATE,                     -- Window closing date
    last_updated        DATE NOT NULL,
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id)
);

CREATE INDEX IF NOT EXISTS idx_pay_srb_zone ON pay_record(srb_zone);

-- =============================================================================
-- DOMAIN 5: MEDICAL READINESS
-- =============================================================================
-- Source system equivalents: MRRS / BUMED
-- =============================================================================

CREATE TABLE IF NOT EXISTS medical_status (
    dod_id              TEXT PRIMARY KEY,
    pha_date            DATE,                     -- Periodic Health Assessment
    pha_due_date        DATE,
    dental_class        INTEGER,                  -- 1 (best) - 4 (non-deployable)
    immunizations_current INTEGER NOT NULL DEFAULT 1,
    is_deployable       INTEGER NOT NULL DEFAULT 1,
    deployment_limit_until DATE,                  -- If non-deployable, when?
    deployment_limit_reason TEXT,
    last_updated        DATE NOT NULL,
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id)
);

CREATE INDEX IF NOT EXISTS idx_medical_deployable ON medical_status(is_deployable);

-- =============================================================================
-- DOMAIN 6: EDUCATION
-- =============================================================================
-- Source system equivalents: Navy College / NPDB
-- =============================================================================

CREATE TABLE IF NOT EXISTS education_record (
    education_id        TEXT PRIMARY KEY,
    dod_id              TEXT NOT NULL,
    degree_level        TEXT NOT NULL,            -- 'HS', 'Some College', 'AA', 'BA', 'MA', 'PhD'
    school_name         TEXT,
    completion_date     DATE,
    used_tuition_assistance INTEGER NOT NULL DEFAULT 0,
    is_completed        INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id)
);

CREATE INDEX IF NOT EXISTS idx_education_sailor ON education_record(dod_id);

-- =============================================================================
-- DOMAIN 7: RECRUITING / ACCESSION
-- =============================================================================
-- Source system equivalents: CIRIMS, PRIDE
-- One row per Sailor — captures point-of-entry data.
-- =============================================================================

CREATE TABLE IF NOT EXISTS accession (
    dod_id              TEXT PRIMARY KEY,
    asvab_afqt          INTEGER NOT NULL,         -- 0-99 percentile
    asvab_gs            INTEGER,                  -- Subtests
    asvab_ar            INTEGER,
    asvab_mk            INTEGER,
    asvab_el            INTEGER,                  -- Electronics line score
    asvab_mc            INTEGER,                  -- Mechanical
    accession_source    TEXT NOT NULL,            -- 'Active', 'Reserve', 'Prior Service'
    enlistment_program  TEXT,                     -- 'GENDET', 'Nuke', 'AECF', 'Cyber', etc.
    contract_term_years INTEGER NOT NULL,
    accession_date      DATE NOT NULL,
    boot_camp_grad_date DATE,
    a_school_grade      REAL,                     -- GPA equivalent
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id)
);

-- =============================================================================
-- CROSS-CUTTING: PERSONNEL EVENT STREAM
-- =============================================================================
-- Spine of event-driven architecture per the Digital Twin vision.
-- Every meaningful change in any domain produces a row here.
-- For POC, populated alongside synthetic data; in production, fed by source
-- systems via Jupiter / orchestration layer.
-- =============================================================================

CREATE TABLE IF NOT EXISTS personnel_event (
    event_id            TEXT PRIMARY KEY,
    dod_id              TEXT NOT NULL,
    event_type          TEXT NOT NULL,            -- See enum below
    event_subtype       TEXT,
    event_date          DATE NOT NULL,
    source_system       TEXT NOT NULL,            -- 'NSIPS', 'TFMMS', 'NTMPS', etc.
    event_payload       TEXT,                     -- JSON blob with details
    FOREIGN KEY (dod_id) REFERENCES sailor(dod_id)
);

-- Event types (for reference, not enforced):
--   ACCESSION, ADVANCEMENT, REENLISTMENT, SEPARATION, RETIREMENT,
--   PCS_ORDERS, REPORT_ABOARD, DETACH, NEC_AWARDED, NEC_REVOKED,
--   QUAL_EARNED, FITREP_SUBMITTED, EXAM_TAKEN, SCHOOL_COMPLETED,
--   PHA_COMPLETED, MEDICAL_STATUS_CHANGE, SRB_ELIGIBLE, SRB_PAID

CREATE INDEX IF NOT EXISTS idx_event_sailor ON personnel_event(dod_id);
CREATE INDEX IF NOT EXISTS idx_event_type ON personnel_event(event_type);
CREATE INDEX IF NOT EXISTS idx_event_date ON personnel_event(event_date);

-- =============================================================================
-- ANALYTICS VIEWS (FEATURE LAYER FOUNDATION)
-- =============================================================================
-- Pre-computed views that scenario models build on top of.
-- These are the "features" referenced in the data architecture doc.
-- =============================================================================

-- Active Sailor base view (excludes separated/retired)
CREATE VIEW IF NOT EXISTS v_active_sailor AS
SELECT
    s.*,
    r.rate_name,
    r.community,
    r.is_critical AS rate_is_critical,
    c.command_name,
    c.command_type,
    c.region,
    c.fleet,
    -- Months until EAOS (negative if past)
    CAST((julianday(s.eaos) - julianday('now')) / 30.0 AS INTEGER) AS months_to_eaos
FROM sailor s
JOIN rate r ON s.rate_code = r.rate_code
LEFT JOIN command c ON s.current_command_id = c.command_id
WHERE s.status = 'Active';

-- Sea/shore tour history
CREATE VIEW IF NOT EXISTS v_sailor_tour_history AS
SELECT
    a.dod_id,
    COUNT(*) AS total_tours,
    SUM(CASE WHEN a.sea_shore = 'Sea' THEN 1 ELSE 0 END) AS sea_tours,
    SUM(CASE WHEN a.sea_shore = 'Shore' THEN 1 ELSE 0 END) AS shore_tours
FROM assignment a
GROUP BY a.dod_id;

-- FITREP trend (last 3 evals)
CREATE VIEW IF NOT EXISTS v_sailor_fitrep_recent AS
SELECT
    f.dod_id,
    COUNT(*) AS num_recent_fitreps,
    AVG(f.trait_avg) AS recent_trait_avg,
    SUM(CASE WHEN f.promotion_recommendation IN ('EP', 'MP') THEN 1 ELSE 0 END)
        AS ep_mp_count,
    MAX(f.period_end) AS last_fitrep_date
FROM fitrep f
WHERE f.fitrep_id IN (
    SELECT fitrep_id FROM fitrep f2
    WHERE f2.dod_id = f.dod_id
    ORDER BY f2.period_end DESC LIMIT 3
)
GROUP BY f.dod_id;
