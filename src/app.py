"""
Navy Sailor Digital Twin - Streamlit Demo Dashboard
====================================================

Interactive demonstration of the Sailor Digital Twin POC. Three views:
  1. Enterprise Overview - the "scale of the data" picture
  2. Retention Risk - identify Sailors at risk of leaving
  3. Promotion Readiness - identify and coach advancement candidates

Run with:
    streamlit run app.py
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

# =============================================================================
# CONFIG
# =============================================================================

DB_PATH = Path(__file__).parent.parent / "data" / "navy_dt.db"

st.set_page_config(
    page_title="Sailor Digital Twin POC",
    page_icon="⚓",
    layout="wide",
)

# =============================================================================
# DATA ACCESS
# =============================================================================

@st.cache_resource
def get_connection():
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

@st.cache_data
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)

# =============================================================================
# SCENARIO 1: RETENTION RISK
# =============================================================================
# Computes a multi-dimensional retention risk score per Sailor.
# Categories: Career Stagnation, Quality of Life, Compensation, Engagement, Mission Fit
# =============================================================================

RETENTION_RISK_SQL = """
WITH tour_history AS (
    SELECT dod_id,
           COUNT(*) AS total_tours,
           SUM(CASE WHEN sea_shore = 'Sea' THEN 1 ELSE 0 END) AS sea_tours
    FROM assignment
    GROUP BY dod_id
),
fitrep_recent AS (
    SELECT dod_id,
           AVG(trait_avg) AS recent_trait_avg,
           SUM(CASE WHEN promotion_recommendation IN ('EP','MP') THEN 1 ELSE 0 END) AS ep_mp_count,
           COUNT(*) AS num_recent_fitreps
    FROM (
        SELECT f.*,
               ROW_NUMBER() OVER (PARTITION BY dod_id ORDER BY period_end DESC) AS rn
        FROM fitrep f
    ) ranked
    WHERE rn <= 3
    GROUP BY dod_id
),
nec_currency AS (
    SELECT dod_id,
           SUM(CASE WHEN qual_type = 'NEC' AND is_current = 1 THEN 1 ELSE 0 END) AS current_necs,
           SUM(CASE WHEN qual_type = 'NEC' THEN 1 ELSE 0 END) AS total_necs
    FROM qualification
    GROUP BY dod_id
)
SELECT
    s.dod_id,
    s.paygrade,
    s.rate_code,
    r.rate_name,
    r.community,
    r.is_critical AS rate_is_critical,
    s.years_of_service,
    s.time_in_rate_months,
    s.eaos,
    CAST((julianday(s.eaos) - julianday('now')) / 30.0 AS INTEGER) AS months_to_eaos,
    s.num_dependents,
    s.has_efm,
    c.command_name,
    c.command_type,
    c.region,
    th.sea_tours,
    th.total_tours,
    fr.recent_trait_avg,
    fr.ep_mp_count,
    fr.num_recent_fitreps,
    nc.current_necs,
    nc.total_necs,
    pr.srb_zone,
    pr.srb_multiplier,
    ms.is_deployable
FROM sailor s
JOIN rate r ON s.rate_code = r.rate_code
LEFT JOIN command c ON s.current_command_id = c.command_id
LEFT JOIN tour_history th ON s.dod_id = th.dod_id
LEFT JOIN fitrep_recent fr ON s.dod_id = fr.dod_id
LEFT JOIN nec_currency nc ON s.dod_id = nc.dod_id
LEFT JOIN pay_record pr ON s.dod_id = pr.dod_id
LEFT JOIN medical_status ms ON s.dod_id = ms.dod_id
WHERE s.status = 'Active'
"""


def compute_retention_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute multi-dimensional retention risk score.

    This is a transparent, rule-based scoring system for the POC. In production,
    we'd replace this with a trained ML model (gradient boosted trees on historical
    separation outcomes), but the rule-based version is auditable and demoable.

    Each dimension contributes 0-25 points; total risk = 0-100.
    """
    df = df.copy()

    # --- Compensation risk (0-25) ---
    # In SRB window with no SRB activity = compensation gap
    df["risk_compensation"] = 0
    in_eaos_window = df["months_to_eaos"].between(0, 18)
    df.loc[in_eaos_window & df["srb_zone"].isnull(), "risk_compensation"] += 10
    df.loc[in_eaos_window & df["srb_zone"].notnull() & (df["srb_multiplier"] < 2.0), "risk_compensation"] += 5
    # Sailors with dependents and no special pay = compensation pressure
    df.loc[df["num_dependents"] >= 2, "risk_compensation"] += 5
    df.loc[df["has_efm"] == 1, "risk_compensation"] += 5

    # --- Career stagnation risk (0-25) ---
    df["risk_stagnation"] = 0
    # High time-in-rate at lower paygrades signals stagnation
    pg_tir_threshold = {"E4": 36, "E5": 60, "E6": 72, "E7": 84}
    for pg, threshold in pg_tir_threshold.items():
        mask = (df["paygrade"] == pg) & (df["time_in_rate_months"] > threshold)
        df.loc[mask, "risk_stagnation"] += 15
    # Few EP/MP recommendations
    df.loc[df["ep_mp_count"].fillna(0) == 0, "risk_stagnation"] += 5
    df.loc[df["recent_trait_avg"].fillna(5) < 3.5, "risk_stagnation"] += 5

    # --- Quality of life risk (0-25) ---
    df["risk_qol"] = 0
    # Heavy sea time
    df.loc[df["sea_tours"].fillna(0) >= 3, "risk_qol"] += 10
    df.loc[df["sea_tours"].fillna(0) >= 4, "risk_qol"] += 5
    # Currently on sea duty AND has dependents
    df.loc[(df["command_type"] == "Sea") & (df["num_dependents"] >= 2), "risk_qol"] += 5
    # EFM enrollment adds QoL stress
    df.loc[df["has_efm"] == 1, "risk_qol"] += 5

    # --- Engagement / performance risk (0-25) ---
    df["risk_engagement"] = 0
    df.loc[df["recent_trait_avg"].fillna(5) < 3.5, "risk_engagement"] += 10
    df.loc[df["recent_trait_avg"].fillna(5) < 3.0, "risk_engagement"] += 5
    df.loc[df["is_deployable"] == 0, "risk_engagement"] += 5
    # No current NEC despite having earned one in the past
    has_lapsed_nec = (df["total_necs"].fillna(0) > 0) & (df["current_necs"].fillna(0) == 0)
    df.loc[has_lapsed_nec, "risk_engagement"] += 5

    # --- Total ---
    df["total_risk"] = (
        df["risk_compensation"] + df["risk_stagnation"]
        + df["risk_qol"] + df["risk_engagement"]
    )

    # Risk tier
    def tier(score):
        if score >= 50:
            return "High"
        if score >= 30:
            return "Medium"
        if score >= 15:
            return "Low"
        return "Minimal"
    df["risk_tier"] = df["total_risk"].apply(tier)

    # Critical Sailor flag (boost priority for critical-rate Sailors at risk)
    df["is_critical_retention"] = (
        (df["rate_is_critical"] == 1) & (df["total_risk"] >= 30)
    ).astype(int)

    # Recommended action
    def recommend(row):
        if row["risk_compensation"] >= 10 and row["months_to_eaos"] <= 12:
            return "SRB / re-enlistment conversation"
        if row["risk_stagnation"] >= 15:
            return "Career counseling, school request, NEC roadmap"
        if row["risk_qol"] >= 15:
            return "Geographic stability discussion, shore tour priority"
        if row["risk_engagement"] >= 15:
            return "Performance improvement plan, mentorship pairing"
        return "Routine retention check-in"
    df["recommended_action"] = df.apply(recommend, axis=1)

    # Primary risk driver
    risk_cols = ["risk_compensation", "risk_stagnation", "risk_qol", "risk_engagement"]
    risk_labels = {"risk_compensation": "Compensation", "risk_stagnation": "Career Stagnation",
                   "risk_qol": "Quality of Life", "risk_engagement": "Engagement"}
    df["primary_driver"] = df[risk_cols].idxmax(axis=1).map(risk_labels)

    return df

# =============================================================================
# SCENARIO 2: PROMOTION READINESS
# =============================================================================

PROMOTION_SQL = """
WITH fitrep_summary AS (
    SELECT dod_id,
           AVG(trait_avg) AS career_trait_avg,
           SUM(CASE WHEN promotion_recommendation IN ('EP','MP') THEN 1 ELSE 0 END) AS ep_mp_career,
           COUNT(*) AS total_fitreps
    FROM fitrep
    GROUP BY dod_id
),
exam_recent AS (
    SELECT dod_id, MAX(standard_score) AS best_recent_score
    FROM advancement_exam
    GROUP BY dod_id
),
qual_counts AS (
    SELECT dod_id,
           SUM(CASE WHEN qual_type = 'PQS' THEN 1 ELSE 0 END) AS pqs_count,
           SUM(CASE WHEN qual_type = 'NEC' AND is_current = 1 THEN 1 ELSE 0 END) AS current_necs
    FROM qualification
    GROUP BY dod_id
)
SELECT
    s.dod_id,
    s.paygrade,
    s.rate_code,
    r.rate_name,
    r.community,
    s.years_of_service,
    s.time_in_rate_months,
    s.primary_nec,
    c.command_name,
    c.command_type,
    fs.career_trait_avg,
    fs.ep_mp_career,
    fs.total_fitreps,
    er.best_recent_score,
    qc.pqs_count,
    qc.current_necs
FROM sailor s
JOIN rate r ON s.rate_code = r.rate_code
LEFT JOIN command c ON s.current_command_id = c.command_id
LEFT JOIN fitrep_summary fs ON s.dod_id = fs.dod_id
LEFT JOIN exam_recent er ON s.dod_id = er.dod_id
LEFT JOIN qual_counts qc ON s.dod_id = qc.dod_id
WHERE s.status = 'Active'
  AND s.paygrade IN ('E3','E4','E5','E6','E7')
"""

PAYGRADE_TIR_MIN = {"E3": 9, "E4": 12, "E5": 36, "E6": 36, "E7": 36}
NEXT_PG = {"E3": "E4", "E4": "E5", "E5": "E6", "E6": "E7", "E7": "E8"}


def compute_promotion_readiness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute promotion readiness score (0-100) plus a list of gaps to close.
    """
    df = df.copy()
    df["next_paygrade"] = df["paygrade"].map(NEXT_PG)
    df["tir_required"] = df["paygrade"].map(PAYGRADE_TIR_MIN)

    # Eligibility components
    df["tir_eligible"] = df["time_in_rate_months"] >= df["tir_required"]
    df["fitrep_strong"] = df["career_trait_avg"].fillna(0) >= 3.7
    df["exam_strong"] = df["best_recent_score"].fillna(0) >= 50
    df["has_current_nec"] = df["current_necs"].fillna(0) >= 1
    df["pqs_sufficient"] = df["pqs_count"].fillna(0) >= 2

    # Readiness score: weighted sum
    df["readiness_score"] = (
        df["tir_eligible"].astype(int) * 25
        + df["fitrep_strong"].astype(int) * 25
        + df["exam_strong"].astype(int) * 20
        + df["has_current_nec"].astype(int) * 15
        + df["pqs_sufficient"].astype(int) * 15
    )

    def tier(score):
        if score >= 80:
            return "Highly Competitive"
        if score >= 60:
            return "Competitive"
        if score >= 40:
            return "Approaching"
        return "Needs Development"
    df["readiness_tier"] = df["readiness_score"].apply(tier)

    # Gap list (what's blocking)
    def gaps(row):
        items = []
        if not row["tir_eligible"]:
            months_short = int(row["tir_required"] - row["time_in_rate_months"])
            items.append(f"Time-in-rate: need {months_short} more months")
        if not row["fitrep_strong"]:
            items.append("Improve FITREP trait average (target ≥ 3.7)")
        if not row["exam_strong"]:
            items.append("Score 50+ on advancement exam")
        if not row["has_current_nec"]:
            items.append("Earn or refresh primary NEC")
        if not row["pqs_sufficient"]:
            items.append("Complete additional PQS qualifications")
        return items if items else ["All criteria met — package ready"]
    df["gaps"] = df.apply(gaps, axis=1)
    df["gap_count"] = df["gaps"].apply(len)

    return df

# =============================================================================
# UI
# =============================================================================

st.sidebar.title("⚓ Sailor Digital Twin")
st.sidebar.caption("MyNavy HR — POC Demo")
page = st.sidebar.radio(
    "Navigate",
    ["Enterprise Overview", "Retention Risk", "Promotion Readiness", "Sailor Profile"],
)
st.sidebar.divider()
st.sidebar.caption("Data: 5,000 synthetic Active Duty enlisted Sailors")
st.sidebar.caption("All data is synthetic. No PII.")

# -----------------------------------------------------------------------------
# PAGE: ENTERPRISE OVERVIEW
# -----------------------------------------------------------------------------
if page == "Enterprise Overview":
    st.title("Enterprise Overview")
    st.caption("The Sailor Digital Twin: one authoritative view across 7 domains.")

    total_sailors = query("SELECT COUNT(*) as c FROM sailor WHERE status = 'Active'").iloc[0]["c"]
    total_billets = query("SELECT COUNT(*) as c FROM billet WHERE billet_id NOT LIKE 'BIN-HIST-%'").iloc[0]["c"]
    filled_billets = query("SELECT SUM(is_filled) as c FROM billet WHERE billet_id NOT LIKE 'BIN-HIST-%'").iloc[0]["c"]
    total_events = query("SELECT COUNT(*) as c FROM personnel_event").iloc[0]["c"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Sailors", f"{total_sailors:,}")
    c2.metric("Billets", f"{total_billets:,}")
    c3.metric("Billet Fill Rate", f"{filled_billets/total_billets*100:.1f}%")
    c4.metric("Personnel Events", f"{total_events:,}")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Paygrade distribution")
        pg_df = query("""
            SELECT paygrade, COUNT(*) AS sailors
            FROM sailor WHERE status = 'Active'
            GROUP BY paygrade ORDER BY paygrade
        """)
        st.bar_chart(pg_df.set_index("paygrade"))

    with col_r:
        st.subheader("Sailors by community")
        comm_df = query("""
            SELECT r.community, COUNT(*) AS sailors
            FROM sailor s JOIN rate r ON s.rate_code = r.rate_code
            WHERE s.status = 'Active'
            GROUP BY r.community ORDER BY sailors DESC
        """)
        st.bar_chart(comm_df.set_index("community"))

    st.subheader("Domain coverage")
    coverage = pd.DataFrame([
        {"Domain": "Personnel",  "Records": query("SELECT COUNT(*) c FROM sailor").iloc[0]["c"], "Source System (Production)": "NSIPS"},
        {"Domain": "Manpower (billets)",   "Records": query("SELECT COUNT(*) c FROM billet").iloc[0]["c"], "Source System (Production)": "TFMMS"},
        {"Domain": "Manpower (assignments)","Records": query("SELECT COUNT(*) c FROM assignment").iloc[0]["c"], "Source System (Production)": "NSIPS / MAPP"},
        {"Domain": "Training (quals/NECs)", "Records": query("SELECT COUNT(*) c FROM qualification").iloc[0]["c"], "Source System (Production)": "NTMPS / FLTMPS"},
        {"Domain": "FITREPs",     "Records": query("SELECT COUNT(*) c FROM fitrep").iloc[0]["c"], "Source System (Production)": "NSIPS BUPERS Online"},
        {"Domain": "Pay",          "Records": query("SELECT COUNT(*) c FROM pay_record").iloc[0]["c"], "Source System (Production)": "DJMS / DFAS"},
        {"Domain": "Medical Readiness", "Records": query("SELECT COUNT(*) c FROM medical_status").iloc[0]["c"], "Source System (Production)": "MRRS / BUMED"},
        {"Domain": "Education",    "Records": query("SELECT COUNT(*) c FROM education_record").iloc[0]["c"], "Source System (Production)": "Navy College"},
        {"Domain": "Recruiting",   "Records": query("SELECT COUNT(*) c FROM accession").iloc[0]["c"], "Source System (Production)": "CIRIMS / PRIDE"},
        {"Domain": "Personnel Events", "Records": query("SELECT COUNT(*) c FROM personnel_event").iloc[0]["c"], "Source System (Production)": "Cross-cutting (orchestration layer)"},
    ])
    st.dataframe(coverage, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# PAGE: RETENTION RISK
# -----------------------------------------------------------------------------
elif page == "Retention Risk":
    st.title("Retention Risk")
    st.caption("Identify Sailors at risk of leaving — categorized by risk type, with recommended interventions.")

    raw = query(RETENTION_RISK_SQL)
    risk = compute_retention_risk(raw)

    # Top-line metrics
    high_risk = (risk["risk_tier"] == "High").sum()
    med_risk = (risk["risk_tier"] == "Medium").sum()
    critical_at_risk = risk["is_critical_retention"].sum()
    in_window = (risk["months_to_eaos"].between(0, 18)).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("High Risk", f"{high_risk:,}", delta_color="inverse")
    c2.metric("Medium Risk", f"{med_risk:,}", delta_color="inverse")
    c3.metric("Critical-Rate at Risk", f"{critical_at_risk:,}",
              help="Critical NEC/community Sailors with risk score ≥ 30")
    c4.metric("In EAOS Window (≤ 18 mo)", f"{in_window:,}")

    st.divider()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        tier_filter = st.multiselect("Risk tier", ["High", "Medium", "Low", "Minimal"], default=["High", "Medium"])
    with col_f2:
        community_filter = st.multiselect(
            "Community",
            sorted(risk["community"].dropna().unique()),
            default=[]
        )
    with col_f3:
        critical_only = st.checkbox("Critical-rate Sailors only")

    filtered = risk[risk["risk_tier"].isin(tier_filter)]
    if community_filter:
        filtered = filtered[filtered["community"].isin(community_filter)]
    if critical_only:
        filtered = filtered[filtered["rate_is_critical"] == 1]

    st.subheader(f"Risk drivers — {len(filtered):,} Sailors")
    col_l, col_r = st.columns(2)
    with col_l:
        driver_counts = filtered["primary_driver"].value_counts()
        st.bar_chart(driver_counts)
        st.caption("Primary risk driver distribution")
    with col_r:
        action_counts = filtered["recommended_action"].value_counts()
        st.bar_chart(action_counts)
        st.caption("Recommended action distribution")

    st.subheader("Sailor list")
    display = filtered.sort_values("total_risk", ascending=False).head(200).copy()
    display = display[[
        "dod_id", "paygrade", "rate_code", "community", "command_name",
        "months_to_eaos", "total_risk", "risk_tier", "primary_driver",
        "srb_zone", "recommended_action"
    ]].rename(columns={
        "dod_id": "DoD ID", "paygrade": "PG", "rate_code": "Rate",
        "community": "Community", "command_name": "Command",
        "months_to_eaos": "Mo to EAOS", "total_risk": "Risk Score",
        "risk_tier": "Tier", "primary_driver": "Primary Driver",
        "srb_zone": "SRB Zone", "recommended_action": "Recommended Action"
    })
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.caption("Showing top 200 by risk score. Click any DoD ID in Sailor Profile page for detail.")

# -----------------------------------------------------------------------------
# PAGE: PROMOTION READINESS
# -----------------------------------------------------------------------------
elif page == "Promotion Readiness":
    st.title("Promotion Readiness")
    st.caption("Identify advancement-ready Sailors and the specific gaps blocking those who aren't.")

    raw = query(PROMOTION_SQL)
    prom = compute_promotion_readiness(raw)

    highly = (prom["readiness_tier"] == "Highly Competitive").sum()
    comp = (prom["readiness_tier"] == "Competitive").sum()
    approaching = (prom["readiness_tier"] == "Approaching").sum()
    needs_dev = (prom["readiness_tier"] == "Needs Development").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Highly Competitive", f"{highly:,}")
    c2.metric("Competitive", f"{comp:,}")
    c3.metric("Approaching", f"{approaching:,}")
    c4.metric("Needs Development", f"{needs_dev:,}")

    st.divider()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        target_pg = st.selectbox("Target paygrade", ["All"] + ["E4", "E5", "E6", "E7", "E8"])
    with col_f2:
        community_filter = st.multiselect(
            "Community",
            sorted(prom["community"].dropna().unique()),
            default=[]
        )

    filtered = prom.copy()
    if target_pg != "All":
        filtered = filtered[filtered["next_paygrade"] == target_pg]
    if community_filter:
        filtered = filtered[filtered["community"].isin(community_filter)]

    st.subheader(f"Readiness distribution — {len(filtered):,} Sailors")
    tier_order = ["Highly Competitive", "Competitive", "Approaching", "Needs Development"]
    tier_counts = filtered["readiness_tier"].value_counts().reindex(tier_order, fill_value=0)
    st.bar_chart(tier_counts)

    # Detail view
    view_mode = st.radio("View", ["Top advancement candidates", "Sailors with closeable gaps"], horizontal=True)

    if view_mode == "Top advancement candidates":
        display = filtered[filtered["readiness_score"] >= 80].sort_values("readiness_score", ascending=False).head(100).copy()
        display = display[[
            "dod_id", "paygrade", "next_paygrade", "rate_code", "community",
            "command_name", "readiness_score", "career_trait_avg", "best_recent_score"
        ]].rename(columns={
            "dod_id": "DoD ID", "paygrade": "PG", "next_paygrade": "→",
            "rate_code": "Rate", "community": "Community", "command_name": "Command",
            "readiness_score": "Score", "career_trait_avg": "FITREP Avg",
            "best_recent_score": "Best Exam Score"
        })
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        # Sailors with 1-2 gaps - "almost there"
        closeable = filtered[(filtered["readiness_score"] >= 50) & (filtered["readiness_score"] < 80)].sort_values("readiness_score", ascending=False).head(100).copy()
        closeable["gaps_text"] = closeable["gaps"].apply(lambda lst: " | ".join(lst))
        display = closeable[[
            "dod_id", "paygrade", "next_paygrade", "rate_code", "command_name",
            "readiness_score", "gap_count", "gaps_text"
        ]].rename(columns={
            "dod_id": "DoD ID", "paygrade": "PG", "next_paygrade": "→",
            "rate_code": "Rate", "command_name": "Command",
            "readiness_score": "Score", "gap_count": "# Gaps",
            "gaps_text": "Gaps to Close"
        })
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.caption("These Sailors are close to competitive — targeted action could move them up.")

# -----------------------------------------------------------------------------
# PAGE: SAILOR PROFILE
# -----------------------------------------------------------------------------
elif page == "Sailor Profile":
    st.title("Sailor Digital Twin — Individual Profile")
    st.caption("The full picture of one Sailor, federated across all 7 domains.")

    dod_id = st.text_input("DoD ID", placeholder="e.g., 9990000123")

    if not dod_id:
        # Sample picker
        sample = query("SELECT dod_id FROM sailor WHERE status = 'Active' ORDER BY RANDOM() LIMIT 5")
        st.caption("Try one of these random DoD IDs:")
        cols = st.columns(5)
        for i, sid in enumerate(sample["dod_id"]):
            if cols[i].button(sid):
                dod_id = sid
                st.rerun()

    if dod_id:
        sailor = query("SELECT * FROM v_active_sailor WHERE dod_id = ?", (dod_id,))
        if sailor.empty:
            st.error(f"No active Sailor found with DoD ID {dod_id}")
        else:
            s = sailor.iloc[0]
            st.header(f"{s['rate_code']}{s['paygrade'][1]} — {s['rate_name']}")
            st.caption(f"DoD ID {s['dod_id']} · {s['command_name']} · {s['region']}")

            # Top metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Paygrade", s["paygrade"])
            c2.metric("Years of Service", f"{s['years_of_service']:.1f}")
            c3.metric("Months to EAOS", int(s["months_to_eaos"]))
            c4.metric("TIR (months)", s["time_in_rate_months"])

            st.divider()

            # Domain panels
            tab_p, tab_t, tab_f, tab_pay, tab_m, tab_a = st.tabs([
                "Personnel", "Training", "FITREPs", "Pay", "Medical", "Assignments"
            ])

            with tab_p:
                cols = ["age", "gender", "marital_status", "num_dependents", "has_efm",
                        "enlistment_date", "eaos", "primary_nec"]
                st.dataframe(sailor[cols].T.rename(columns={sailor.index[0]: "Value"}), use_container_width=True)

            with tab_t:
                quals = query("SELECT qual_type, qual_code, qual_title, date_earned, currency_expires, is_current FROM qualification WHERE dod_id = ? ORDER BY date_earned DESC", (dod_id,))
                st.dataframe(quals, use_container_width=True, hide_index=True)
                exams = query("SELECT exam_cycle, target_paygrade, standard_score, passed, advanced FROM advancement_exam WHERE dod_id = ? ORDER BY exam_date DESC", (dod_id,))
                if not exams.empty:
                    st.markdown("**Advancement exams:**")
                    st.dataframe(exams, use_container_width=True, hide_index=True)

            with tab_f:
                fitreps = query("SELECT period_start, period_end, paygrade_at_eval, trait_avg, promotion_recommendation FROM fitrep WHERE dod_id = ? ORDER BY period_end DESC", (dod_id,))
                st.dataframe(fitreps, use_container_width=True, hide_index=True)

            with tab_pay:
                pay = query("SELECT * FROM pay_record WHERE dod_id = ?", (dod_id,))
                if not pay.empty:
                    p = pay.iloc[0]
                    pay_display = pay.drop(columns=["dod_id"]).T.rename(columns={pay.index[0]: "Value"})
                    st.dataframe(pay_display, use_container_width=True)

            with tab_m:
                med = query("SELECT * FROM medical_status WHERE dod_id = ?", (dod_id,))
                if not med.empty:
                    med_display = med.drop(columns=["dod_id"]).T.rename(columns={med.index[0]: "Value"})
                    st.dataframe(med_display, use_container_width=True)

            with tab_a:
                assigns = query("""
                    SELECT a.report_date, a.detach_date, c.command_name, a.sea_shore, a.is_current
                    FROM assignment a JOIN command c ON a.command_id = c.command_id
                    WHERE a.dod_id = ? ORDER BY a.report_date DESC
                """, (dod_id,))
                st.dataframe(assigns, use_container_width=True, hide_index=True)

            # Personnel events timeline
            st.divider()
            st.subheader("Personnel event stream")
            st.caption("Audit trail of all changes to this Sailor's record — the spine of the event-driven Digital Twin.")
            events = query("SELECT event_date, event_type, source_system, event_payload FROM personnel_event WHERE dod_id = ? ORDER BY event_date DESC LIMIT 50", (dod_id,))
            st.dataframe(events, use_container_width=True, hide_index=True)
