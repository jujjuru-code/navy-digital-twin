"""
Navy Sailor Digital Twin — Streamlit Demo Dashboard
====================================================
MyNavy HR POC  |  Themed to U.S. Navy Design Guide
Navy Black #08262C | Navy Blue #003B4F | Teal Blue #088199
Gray #C6CCD0 | Yellow #E8B00F | White #FFFFFF | Red #B30003
Fonts: Roboto (body) + Roboto Slab (headings)

Run with:  streamlit run app.py
"""

import sqlite3
from pathlib import Path
import io
import json

import pandas as pd
import plotly.express as px
import streamlit as st

# =============================================================================
# PAGE CONFIG
# =============================================================================
DB_PATH = Path(__file__).parent.parent / "data" / "navy_dt.db"

st.set_page_config(
    page_title="MyNavy HR — Sailor Digital Twin",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# NAVY DESIGN GUIDE — CUSTOM CSS
# =============================================================================
NAVY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Slab:wght@400;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stText {
    font-family: 'Roboto', sans-serif !important;
    color: #08262C;
}
h1, h2, h3, h4 {
    font-family: 'Roboto Slab', serif !important;
    color: #003B4F !important;
}
h1 { font-size: 32px !important; font-weight: 700 !important; }
h2 { font-size: 24px !important; font-weight: 700 !important; }
h3 { font-size: 20px !important; font-weight: 700 !important; }

[data-testid="stSidebar"] {
    background-color: #003B4F !important;
    border-right: 4px solid #088199;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] hr { border-color: #088199 !important; opacity: 0.6; }

[data-testid="stMetric"] {
    background-color: #F4F8FA !important;
    border-left: 4px solid #088199 !important;
    border-radius: 4px !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stMetricLabel"] {
    color: #003B4F !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"] {
    color: #08262C !important;
    font-family: 'Roboto Slab', serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}

hr { border-color: #C6CCD0 !important; opacity: 1 !important; }

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    border-bottom: 2px solid #C6CCD0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #003B4F !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    border-bottom: 3px solid transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #088199 !important;
    border-bottom: 3px solid #088199 !important;
    font-weight: 700 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #C6CCD0 !important;
    border-radius: 4px !important;
}

[data-testid="stButton"] button {
    background-color: #003B4F !important;
    color: #FFFFFF !important;
    font-weight: 500 !important;
    border: none !important;
    border-radius: 3px !important;
}
[data-testid="stButton"] button:hover { background-color: #088199 !important; }

[data-testid="stDownloadButton"] button {
    background-color: #E8B00F !important;
    color: #08262C !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 3px !important;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: #4A6570 !important;
    font-size: 12px !important;
}

/* ── Page header banner ── */
.page-header {
    background: linear-gradient(135deg, #003B4F 0%, #08262C 100%);
    color: #fff;
    padding: 1.2rem 1.5rem;
    border-radius: 6px;
    border-left: 6px solid #E8B00F;
    margin-bottom: 1.5rem;
}
.page-header h1 { color: #fff !important; margin: 0 !important; font-size: 26px !important; }
.page-header p { color: #C6CCD0 !important; margin: 0.3rem 0 0 0 !important; font-size: 13px !important; }

/* ── Section labels ── */
.section-label {
    color: #088199 !important;
    font-family: 'Roboto Slab', serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    border-bottom: 2px solid #088199;
    padding-bottom: 4px;
    margin-bottom: 12px;
    margin-top: 8px;
}

/* ── KPI note ── */
.kpi-note {
    background: #EEF6F8;
    border-left: 3px solid #088199;
    padding: 0.5rem 0.8rem;
    border-radius: 0 4px 4px 0;
    font-size: 13px;
    color: #003B4F;
    margin: 0.5rem 0 1rem 0;
}

/* ── Sailor hero card ── */
.sailor-card {
    background: linear-gradient(135deg, #003B4F, #08262C);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    color: white;
    border-left: 6px solid #E8B00F;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.sailor-card h2 { color: #fff !important; margin: 0 0 0.3rem 0 !important; font-size: 22px !important; }
.sailor-card .sub { color: #C6CCD0; font-size: 13px; }
.sailor-card .readiness {
    text-align: right;
}
.sailor-card .readiness-pct {
    font-family: 'Roboto Slab', serif;
    font-size: 32px;
    font-weight: 700;
    color: #E8B00F;
}
.sailor-card .readiness-label { font-size: 11px; color: #C6CCD0; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── Digital Twin Snapshot ── */
.dt-snapshot {
    background: #F4F8FA;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    border: 1px solid #C6CCD0;
}
.dt-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.35rem 0;
    border-bottom: 1px solid #E8EEF0;
    font-size: 13px;
}
.dt-row:last-child { border-bottom: none; }
.dt-label { color: #4A6570; font-weight: 500; }
.dt-val-green { color: #1a7a4a; font-weight: 600; }
.dt-val-red { color: #B30003; font-weight: 600; }
.dt-val-yellow { color: #9B7200; font-weight: 600; }
.dt-val-gray { color: #6B7C83; font-weight: 600; }
.dt-dot-green::before { content: "●"; color: #1a7a4a; margin-right: 5px; }
.dt-dot-red::before { content: "●"; color: #B30003; margin-right: 5px; }
.dt-dot-yellow::before { content: "●"; color: #E8B00F; margin-right: 5px; }
.dt-dot-gray::before { content: "●"; color: #C6CCD0; margin-right: 5px; }

/* ── Lifecycle timeline ── */
.lifecycle-wrap {
    background: #F4F8FA;
    border-radius: 6px;
    border: 1px solid #C6CCD0;
    padding: 1rem 1.5rem;
    overflow-x: auto;
}
.lifecycle-track {
    display: flex;
    align-items: center;
    gap: 0;
    min-width: 600px;
}
.lc-stage {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}
.lc-stage:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 16px;
    right: -50%;
    width: 100%;
    height: 2px;
    background: #C6CCD0;
    z-index: 0;
}
.lc-stage.completed::after { background: #088199; }
.lc-stage.active::after { background: linear-gradient(90deg, #088199, #C6CCD0); }
.lc-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #C6CCD0;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    z-index: 1;
    position: relative;
    border: 3px solid white;
    box-shadow: 0 0 0 2px #C6CCD0;
}
.lc-stage.completed .lc-circle {
    background: #088199;
    box-shadow: 0 0 0 2px #088199;
}
.lc-stage.active .lc-circle {
    background: #E8B00F;
    box-shadow: 0 0 0 3px #E8B00F;
    width: 36px;
    height: 36px;
    font-size: 14px;
}
.lc-label {
    margin-top: 6px;
    font-size: 10px;
    text-align: center;
    color: #6B7C83;
    font-family: 'Roboto', sans-serif;
    max-width: 70px;
    line-height: 1.3;
}
.lc-stage.active .lc-label {
    color: #003B4F;
    font-weight: 700;
    font-size: 11px;
}
.lc-sublabel {
    font-size: 9px;
    color: #088199;
    font-weight: 600;
    text-align: center;
    margin-top: 2px;
}

/* ── Workflow cards ── */
.wf-card {
    background: white;
    border: 1px solid #C6CCD0;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 5px solid #088199;
}
.wf-card.urgent { border-left-color: #B30003; }
.wf-card.warning { border-left-color: #E8B00F; }
.wf-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.6rem;
}
.wf-title { font-weight: 700; font-size: 14px; color: #003B4F; }
.wf-badge {
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 3px;
    white-space: nowrap;
}
.wf-badge-green { background: #d4edda; color: #1a7a4a; }
.wf-badge-red { background: #fde8e8; color: #B30003; }
.wf-badge-yellow { background: #fff3cd; color: #9B7200; }
.wf-meta { font-size: 12px; color: #4A6570; display: flex; gap: 1.5rem; flex-wrap: wrap; }
.wf-meta span { display: flex; align-items: center; gap: 4px; }

/* ── AI action cards ── */
.ai-card {
    background: white;
    border: 1px solid #C6CCD0;
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
    border-left: 5px solid #088199;
}
.ai-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.4rem;
}
.ai-title { font-weight: 700; font-size: 14px; color: #003B4F; }
.ai-conf-high { background: #d4edda; color: #1a7a4a; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 3px; }
.ai-conf-med  { background: #fff3cd; color: #9B7200; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 3px; }
.ai-rationale { font-size: 12px; color: #4A6570; margin-bottom: 0.4rem; }
.ai-meta { font-size: 11px; color: #6B7C83; }
.ai-disclaimer {
    background: #F4F8FA;
    border: 1px solid #C6CCD0;
    border-radius: 4px;
    padding: 0.6rem 0.8rem;
    font-size: 11px;
    color: #4A6570;
    margin-top: 1rem;
    text-align: center;
}

/* ── Provenance rows ── */
.prov-card {
    background: white;
    border: 1px solid #C6CCD0;
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.8rem;
}
.prov-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}
.prov-field { font-weight: 700; font-size: 14px; color: #003B4F; }
.prov-verified { background: #d4edda; color: #1a7a4a; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 3px; }
.prov-pending  { background: #fff3cd; color: #9B7200; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 3px; }
.prov-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.4rem;
    font-size: 12px;
}
.prov-item-label { color: #6B7C83; }
.prov-item-value { color: #08262C; font-weight: 500; }

/* ── Entitlement rows ── */
.ent-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #E8EEF0;
    font-size: 14px;
}
.ent-row:last-child { border-bottom: none; }
.ent-name { color: #003B4F; }
.ent-amount { font-family: 'Roboto Slab', serif; font-weight: 700; color: #08262C; }
.ent-badge { font-size: 11px; padding: 1px 6px; border-radius: 3px; margin-left: 6px; }
.ent-active { background: #d4edda; color: #1a7a4a; }
.ent-alert  { background: #fde8e8; color: #B30003; }
.pay-alert {
    background: #FFF8E1;
    border: 1px solid #E8B00F;
    border-left: 4px solid #E8B00F;
    border-radius: 4px;
    padding: 0.6rem 0.8rem;
    font-size: 12px;
    color: #9B7200;
    margin: 0.5rem 0;
}
</style>
"""
st.markdown(NAVY_CSS, unsafe_allow_html=True)

# =============================================================================
# DATA ACCESS
# =============================================================================
@st.cache_resource
def get_connection():
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

@st.cache_data(ttl=300)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)

def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-header"><h1>⚓ {title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )

def section(label: str) -> None:
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


# =============================================================================
# HELPER: READINESS INDICATOR
# =============================================================================
def compute_readiness_indicator(dod_id: str) -> tuple:
    """Return (score 0-100, label, color). Based on 4 domains x 25 pts each."""
    score = 0
    breakdown = {}

    med = query("SELECT is_deployable, dental_class FROM medical_status WHERE dod_id=?", (dod_id,))
    if not med.empty:
        m = med.iloc[0]
        pts = 25 if (m["is_deployable"] == 1 and m["dental_class"] <= 2) else (15 if m["is_deployable"] == 1 else 0)
    else:
        pts = 0
    score += pts
    breakdown["Medical"] = pts

    nec_curr = query("SELECT COUNT(*) as n FROM qualification WHERE dod_id=? AND qual_type='NEC' AND is_current=1", (dod_id,)).iloc[0]["n"]
    nec_tot  = query("SELECT COUNT(*) as n FROM qualification WHERE dod_id=? AND qual_type='NEC'", (dod_id,)).iloc[0]["n"]
    pts = 25 if nec_curr >= 1 else (10 if nec_tot > 0 else 15)
    score += pts
    breakdown["Training"] = pts

    fitrep = query(
        "SELECT AVG(trait_avg) as avg FROM (SELECT trait_avg FROM fitrep WHERE dod_id=? ORDER BY period_end DESC LIMIT 3)",
        (dod_id,),
    ).iloc[0]["avg"]
    pts = 25 if (fitrep and fitrep >= 3.7) else (15 if (fitrep and fitrep >= 3.0) else 5)
    score += pts
    breakdown["Performance"] = pts

    s = query("SELECT months_to_eaos FROM v_active_sailor WHERE dod_id=?", (dod_id,))
    if not s.empty:
        mos = s.iloc[0]["months_to_eaos"]
        pts = 25 if mos > 24 else (15 if mos > 12 else (5 if mos > 0 else 0))
    else:
        pts = 0
    score += pts
    breakdown["Service"] = pts

    score = min(100, score)
    label = "Mission Ready" if score >= 85 else ("Conditionally Ready" if score >= 65 else ("Limited Readiness" if score >= 40 else "Non-Mission Ready"))
    color = "#1a7a4a" if score >= 85 else ("#E8B00F" if score >= 65 else ("#B30003"))
    return score, label, color, breakdown


# =============================================================================
# HELPER: LIFECYCLE STAGE
# =============================================================================
LIFECYCLE_STAGES = [
    ("Recruit",     "🎯"),
    ("Accessions",  "📋"),
    ("Training",    "🎓"),
    ("Assignment",  "🚢"),
    ("Advancement", "⬆️"),
    ("PCS",         "📦"),
    ("Sep / Ret",   "🏅"),
]

def derive_lifecycle_stage(s: pd.Series) -> tuple:
    """Return (current_index 0-6, sublabel). s is a row from v_active_sailor."""
    yos    = float(s.get("years_of_service", 0))
    pg     = str(s.get("paygrade", "E1"))
    mos    = int(s.get("months_to_eaos", 99))
    ctype  = str(s.get("command_type", ""))

    if yos < 0.5:                       idx, sub = 0, "Boot Camp"
    elif yos < 1.5:                     idx, sub = 1, "In-Processing"
    elif yos < 3.0:                     idx, sub = 2, "A-School / C-School"
    elif mos <= 18:                     idx, sub = 5, f"EAOS in {mos} mo"
    elif pg in ("E7", "E8", "E9"):      idx, sub = 4, f"Senior Enlisted"
    elif ctype == "Sea":                idx, sub = 3, "Sea Duty"
    elif ctype == "Shore":              idx, sub = 3, "Shore Duty"
    elif ctype == "Overseas":           idx, sub = 3, "Overseas Duty"
    else:                               idx, sub = 3, "Assignment"
    return idx, sub

def render_lifecycle_html(current_idx: int, sub_label: str) -> str:
    stages_html = ""
    for i, (name, icon) in enumerate(LIFECYCLE_STAGES):
        if i < current_idx:
            cls, num = "completed", "✓"
        elif i == current_idx:
            cls, num = "active", icon
        else:
            cls, num = "", str(i + 1)
        sub = f'<div class="lc-sublabel">{sub_label}</div>' if i == current_idx else ""
        stages_html += (
            f'<div class="lc-stage {cls}">'
            f'<div class="lc-circle">{num}</div>'
            f'<div class="lc-label">{name}</div>'
            f'{sub}'
            f'</div>'
        )
    return f'<div class="lifecycle-wrap"><div class="lifecycle-track">{stages_html}</div></div>'


# =============================================================================
# HELPER: DIGITAL TWIN SNAPSHOT
# =============================================================================
def get_dt_snapshot(dod_id: str, s: pd.Series) -> list:
    """Return list of (label, value, color) for the 8-field status panel."""
    rows = []

    # Personnel Status
    rows.append(("Personnel Status", "Active Duty", "green"))

    # Pay Status
    pay = query("SELECT srb_zone, srb_eligible_until FROM pay_record WHERE dod_id=?", (dod_id,))
    if pay.empty:
        rows.append(("Pay Status", "Record Missing", "red"))
    else:
        rows.append(("Pay Status", "Current", "green"))

    # Orders Status
    asgn = query("SELECT is_current FROM assignment WHERE dod_id=? AND is_current=1 LIMIT 1", (dod_id,))
    rows.append(("Orders Status", "Permanent Duty" if not asgn.empty else "Awaiting Orders", "green" if not asgn.empty else "yellow"))

    # Medical Readiness
    med = query("SELECT is_deployable, dental_class FROM medical_status WHERE dod_id=?", (dod_id,))
    if med.empty:
        rows.append(("Medical Readiness", "PHA Required", "yellow"))
    elif med.iloc[0]["is_deployable"] == 0:
        rows.append(("Medical Readiness", "Non-Deployable", "red"))
    elif med.iloc[0]["dental_class"] and med.iloc[0]["dental_class"] > 2:
        rows.append(("Medical Readiness", "Dental Action Required", "yellow"))
    else:
        rows.append(("Medical Readiness", "Qualified", "green"))

    # Training Readiness
    lapsed = query("SELECT COUNT(*) as n FROM qualification WHERE dod_id=? AND qual_type='NEC' AND is_current=0", (dod_id,)).iloc[0]["n"]
    curr   = query("SELECT COUNT(*) as n FROM qualification WHERE dod_id=? AND qual_type='NEC' AND is_current=1", (dod_id,)).iloc[0]["n"]
    if lapsed > 0:
        rows.append(("Training Readiness", f"Action Required ({lapsed} lapsed)", "red"))
    elif curr == 0:
        rows.append(("Training Readiness", "No NECs on Record", "yellow"))
    else:
        rows.append(("Training Readiness", "Current", "green"))

    # Security Clearance (simulated — production would query DISS/JABS)
    community = str(s.get("community", ""))
    clearance = "TS/SCI - Active" if community in ("Cyber", "Intelligence") else "Secret - Active"
    rows.append(("Security Clearance", clearance, "green"))

    # Family/Dependency
    efm  = int(s.get("has_efm", 0))
    deps = int(s.get("num_dependents", 0))
    if efm:
        rows.append(("Family/Dependency", "EFM Enrolled", "yellow"))
    elif deps > 0:
        rows.append(("Family/Dependency", f"{deps} Dependent(s) on Record", "green"))
    else:
        rows.append(("Family/Dependency", "No Dependents", "gray"))

    # PCS Window
    mos = int(s.get("months_to_eaos", 99))
    if mos <= 0:
        rows.append(("PCS Window", "EAOS Passed", "red"))
    elif mos <= 18:
        rows.append(("PCS Window", "Window Active Now", "yellow"))
    else:
        approx = max(0, mos - 18)
        rows.append(("PCS Window", f"Opens in ~{approx} months", "gray"))

    return rows

def render_dt_snapshot(rows: list) -> str:
    html = '<div class="dt-snapshot">'
    for label, value, color in rows:
        html += (
            f'<div class="dt-row">'
            f'<span class="dt-label">{label}</span>'
            f'<span class="dt-dot-{color} dt-val-{color}">{value}</span>'
            f'</div>'
        )
    html += '</div>'
    return html


# =============================================================================
# HELPER: AI-ASSISTED NEXT BEST ACTIONS
# =============================================================================
def generate_ai_actions(dod_id: str, s: pd.Series) -> list:
    actions = []
    mos     = int(s.get("months_to_eaos", 99))
    pg      = str(s.get("paygrade", "E1"))
    rate    = str(s.get("rate_code", ""))
    comm    = str(s.get("community", ""))

    pay  = query("SELECT srb_zone, srb_multiplier FROM pay_record WHERE dod_id=?", (dod_id,))
    med  = query("SELECT is_deployable FROM medical_status WHERE dod_id=?", (dod_id,))
    lapsed = query(
        "SELECT qual_title FROM qualification WHERE dod_id=? AND qual_type='NEC' AND is_current=0 LIMIT 2",
        (dod_id,),
    )
    fitrep = query(
        "SELECT AVG(trait_avg) as avg FROM (SELECT trait_avg FROM fitrep WHERE dod_id=? ORDER BY period_end DESC LIMIT 3)",
        (dod_id,),
    ).iloc[0]["avg"]

    # 1. SRB / reenlistment
    if 0 <= mos <= 18:
        if not pay.empty and pay.iloc[0]["srb_zone"]:
            srb_z = pay.iloc[0]["srb_zone"]
            mult  = pay.iloc[0]["srb_multiplier"]
            actions.append({
                "title":    f"Route SRB Zone {srb_z} package to command approver",
                "rationale": f"Sailor is {mos} months from EAOS and eligible for SRB x{mult:.1f}. Package verified — all requirements met, pending command signature.",
                "confidence": "High", "conf_cls": "ai-conf-high",
                "policy":   "MILPERSMAN 1160-120",
                "systems":  "NSIPS · DFAS · BUPERS",
                "type":     "Re-enlistment",
            })
        else:
            actions.append({
                "title":    "Schedule mandatory retention counseling",
                "rationale": f"Sailor is {mos} months from EAOS. Retention counseling session required per OPNAVINST 1160.8B before EAOS -12 months.",
                "confidence": "High", "conf_cls": "ai-conf-high",
                "policy":   "OPNAVINST 1160.8B",
                "systems":  "NSIPS",
                "type":     "Retention",
            })

    # 2. Training cert
    if not lapsed.empty:
        nec_names = " / ".join(lapsed["qual_title"].tolist())
        actions.append({
            "title":    "Notify Sailor of expired NEC certification",
            "rationale": f"Lapsed NEC(s): {nec_names}. Currency expiration impacts deployment readiness and advancement eligibility.",
            "confidence": "High", "conf_cls": "ai-conf-high",
            "policy":   "NAVEDTRA 43467",
            "systems":  "NTMPS · FLTMPS · NSIPS",
            "type":     "Training",
        })

    # 3. PCS window vs. open billets
    if 12 <= mos <= 30:
        actions.append({
            "title":    f"Compare PCS window against open {rate} billet inventory",
            "rationale": f"PCS window opens in ~{max(0, mos - 18)} months. Cross-reference now to identify top-match billets before orders are cut.",
            "confidence": "Medium", "conf_cls": "ai-conf-med",
            "policy":   "MILPERSMAN 1306-100",
            "systems":  "TOPS · CMS-ID · TFMMS",
            "type":     "Detailing",
        })

    # 4. Medical readiness
    if not med.empty and med.iloc[0]["is_deployable"] == 0:
        actions.append({
            "title":    "Initiate medical readiness review and disposition",
            "rationale": "Sailor is currently non-deployable. Medical disposition required before next scheduled deployment window.",
            "confidence": "High", "conf_cls": "ai-conf-high",
            "policy":   "MANMED P-117",
            "systems":  "MRRS · BUMED · NSIPS",
            "type":     "Medical",
        })

    # 5. FITREP performance
    if fitrep and fitrep < 3.5:
        actions.append({
            "title":    "Schedule performance counseling with LPO/LCPO",
            "rationale": f"Recent FITREP trait average ({fitrep:.2f}) is below the competitive threshold (3.7). Early intervention improves advancement outcomes.",
            "confidence": "Medium", "conf_cls": "ai-conf-med",
            "policy":   "BUPERSINST 1610.10F",
            "systems":  "NSIPS BUPERS Online",
            "type":     "Performance",
        })

    # 6. Always: generate case summary
    actions.append({
        "title":    "Generate case summary with supporting evidence",
        "rationale": "Consolidated provenance data verified across all 7 authoritative sources. Full audit trail available for download.",
        "confidence": "High", "conf_cls": "ai-conf-high",
        "policy":   "MyNavy HR Data Governance Policy v2.1",
        "systems":  "All connected source systems",
        "type":     "Documentation",
    })

    return actions[:5]

def render_ai_card(action: dict, idx: int) -> str:
    conf_badge = f'<span class="{action["conf_cls"]}">{action["confidence"]} Confidence</span>'
    return (
        f'<div class="ai-card">'
        f'<div class="ai-card-header"><span class="ai-title">{action["title"]}</span>{conf_badge}</div>'
        f'<div class="ai-rationale">{action["rationale"]}</div>'
        f'<div class="ai-meta">📋 {action["policy"]} &nbsp;|&nbsp; 🔗 {action["systems"]} &nbsp;|&nbsp; 🏷️ {action["type"]}</div>'
        f'</div>'
    )


# =============================================================================
# RETENTION RISK SQL + SCORING
# =============================================================================
RETENTION_RISK_SQL = """
WITH tour_history AS (
    SELECT dod_id,
           COUNT(*) AS total_tours,
           SUM(CASE WHEN sea_shore='Sea' THEN 1 ELSE 0 END) AS sea_tours
    FROM assignment GROUP BY dod_id
),
fitrep_recent AS (
    SELECT dod_id,
           AVG(trait_avg) AS recent_trait_avg,
           SUM(CASE WHEN promotion_recommendation IN ('EP','MP') THEN 1 ELSE 0 END) AS ep_mp_count,
           COUNT(*) AS num_recent_fitreps
    FROM (SELECT f.*, ROW_NUMBER() OVER (PARTITION BY dod_id ORDER BY period_end DESC) AS rn FROM fitrep f) ranked
    WHERE rn <= 3 GROUP BY dod_id
),
nec_currency AS (
    SELECT dod_id,
           SUM(CASE WHEN qual_type='NEC' AND is_current=1 THEN 1 ELSE 0 END) AS current_necs,
           SUM(CASE WHEN qual_type='NEC' THEN 1 ELSE 0 END) AS total_necs
    FROM qualification GROUP BY dod_id
)
SELECT s.dod_id, s.paygrade, s.rate_code,
    r.rate_name, r.community, r.is_critical AS rate_is_critical,
    s.years_of_service, s.time_in_rate_months, s.eaos,
    CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INTEGER) AS months_to_eaos,
    s.num_dependents, s.has_efm,
    c.command_name, c.command_type, c.region,
    th.sea_tours, th.total_tours,
    fr.recent_trait_avg, fr.ep_mp_count, fr.num_recent_fitreps,
    nc.current_necs, nc.total_necs,
    pr.srb_zone, pr.srb_multiplier, ms.is_deployable
FROM sailor s
JOIN rate r ON s.rate_code=r.rate_code
LEFT JOIN command c ON s.current_command_id=c.command_id
LEFT JOIN tour_history th ON s.dod_id=th.dod_id
LEFT JOIN fitrep_recent fr ON s.dod_id=fr.dod_id
LEFT JOIN nec_currency nc ON s.dod_id=nc.dod_id
LEFT JOIN pay_record pr ON s.dod_id=pr.dod_id
LEFT JOIN medical_status ms ON s.dod_id=ms.dod_id
WHERE s.status='Active'
"""

def compute_retention_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["risk_compensation"] = 0
    in_win = df["months_to_eaos"].between(0, 18)
    df.loc[in_win & df["srb_zone"].isnull(), "risk_compensation"] += 10
    df.loc[in_win & df["srb_zone"].notnull() & (df["srb_multiplier"] < 2.0), "risk_compensation"] += 5
    df.loc[df["num_dependents"] >= 2, "risk_compensation"] += 5
    df.loc[df["has_efm"] == 1, "risk_compensation"] += 5

    df["risk_stagnation"] = 0
    for pg, thr in {"E4": 36, "E5": 60, "E6": 72, "E7": 84}.items():
        df.loc[(df["paygrade"] == pg) & (df["time_in_rate_months"] > thr), "risk_stagnation"] += 15
    df.loc[df["ep_mp_count"].fillna(0) == 0, "risk_stagnation"] += 5
    df.loc[df["recent_trait_avg"].fillna(5) < 3.5, "risk_stagnation"] += 5

    df["risk_qol"] = 0
    df.loc[df["sea_tours"].fillna(0) >= 3, "risk_qol"] += 10
    df.loc[df["sea_tours"].fillna(0) >= 4, "risk_qol"] += 5
    df.loc[(df["command_type"] == "Sea") & (df["num_dependents"] >= 2), "risk_qol"] += 5
    df.loc[df["has_efm"] == 1, "risk_qol"] += 5

    df["risk_engagement"] = 0
    df.loc[df["recent_trait_avg"].fillna(5) < 3.5, "risk_engagement"] += 10
    df.loc[df["recent_trait_avg"].fillna(5) < 3.0, "risk_engagement"] += 5
    df.loc[df["is_deployable"] == 0, "risk_engagement"] += 5
    df.loc[(df["total_necs"].fillna(0) > 0) & (df["current_necs"].fillna(0) == 0), "risk_engagement"] += 5

    df["total_risk"] = df["risk_compensation"] + df["risk_stagnation"] + df["risk_qol"] + df["risk_engagement"]
    df["risk_tier"] = df["total_risk"].apply(lambda s: "High" if s >= 50 else ("Medium" if s >= 30 else ("Low" if s >= 15 else "Minimal")))
    df["is_critical_retention"] = ((df["rate_is_critical"] == 1) & (df["total_risk"] >= 30)).astype(int)

    def rec(r):
        if r["risk_compensation"] >= 10 and r["months_to_eaos"] <= 12: return "SRB / re-enlistment conversation"
        if r["risk_stagnation"] >= 15: return "Career counseling, school request, NEC roadmap"
        if r["risk_qol"] >= 15: return "Geographic stability discussion, shore tour priority"
        if r["risk_engagement"] >= 15: return "Performance improvement plan, mentorship pairing"
        return "Routine retention check-in"
    df["recommended_action"] = df.apply(rec, axis=1)

    labels = {"risk_compensation": "Compensation", "risk_stagnation": "Career Stagnation",
              "risk_qol": "Quality of Life", "risk_engagement": "Engagement"}
    df["primary_driver"] = df[list(labels.keys())].idxmax(axis=1).map(labels)
    return df


# =============================================================================
# PROMOTION READINESS SQL + SCORING
# =============================================================================
PROMOTION_SQL = """
WITH fitrep_summary AS (
    SELECT dod_id, AVG(trait_avg) AS career_trait_avg,
           SUM(CASE WHEN promotion_recommendation IN ('EP','MP') THEN 1 ELSE 0 END) AS ep_mp_career,
           COUNT(*) AS total_fitreps
    FROM fitrep GROUP BY dod_id
),
exam_recent AS (SELECT dod_id, MAX(standard_score) AS best_recent_score FROM advancement_exam GROUP BY dod_id),
qual_counts AS (
    SELECT dod_id,
           SUM(CASE WHEN qual_type='PQS' THEN 1 ELSE 0 END) AS pqs_count,
           SUM(CASE WHEN qual_type='NEC' AND is_current=1 THEN 1 ELSE 0 END) AS current_necs
    FROM qualification GROUP BY dod_id
)
SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name, r.community,
    s.years_of_service, s.time_in_rate_months, s.primary_nec,
    c.command_name, c.command_type,
    fs.career_trait_avg, fs.ep_mp_career, fs.total_fitreps,
    er.best_recent_score, qc.pqs_count, qc.current_necs
FROM sailor s
JOIN rate r ON s.rate_code=r.rate_code
LEFT JOIN command c ON s.current_command_id=c.command_id
LEFT JOIN fitrep_summary fs ON s.dod_id=fs.dod_id
LEFT JOIN exam_recent er ON s.dod_id=er.dod_id
LEFT JOIN qual_counts qc ON s.dod_id=qc.dod_id
WHERE s.status='Active' AND s.paygrade IN ('E3','E4','E5','E6','E7')
"""

PAYGRADE_TIR_MIN = {"E3": 9, "E4": 12, "E5": 36, "E6": 36, "E7": 36}
NEXT_PG = {"E3": "E4", "E4": "E5", "E5": "E6", "E6": "E7", "E7": "E8"}

def compute_promotion_readiness(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["next_paygrade"] = df["paygrade"].map(NEXT_PG)
    df["tir_required"]  = df["paygrade"].map(PAYGRADE_TIR_MIN)
    df["tir_eligible"]  = df["time_in_rate_months"] >= df["tir_required"]
    df["fitrep_strong"] = df["career_trait_avg"].fillna(0) >= 3.7
    df["exam_strong"]   = df["best_recent_score"].fillna(0) >= 50
    df["has_current_nec"] = df["current_necs"].fillna(0) >= 1
    df["pqs_sufficient"]  = df["pqs_count"].fillna(0) >= 2
    df["readiness_score"] = (df["tir_eligible"].astype(int)*25 + df["fitrep_strong"].astype(int)*25
        + df["exam_strong"].astype(int)*20 + df["has_current_nec"].astype(int)*15 + df["pqs_sufficient"].astype(int)*15)
    df["readiness_tier"] = df["readiness_score"].apply(
        lambda s: "Highly Competitive" if s >= 80 else ("Competitive" if s >= 60 else ("Approaching" if s >= 40 else "Needs Development")))
    def gaps(row):
        items = []
        if not row["tir_eligible"]: items.append(f"TIR: need {int(row['tir_required']-row['time_in_rate_months'])} more months")
        if not row["fitrep_strong"]: items.append("Improve FITREP avg (target >= 3.7)")
        if not row["exam_strong"]: items.append("Score 50+ on advancement exam")
        if not row["has_current_nec"]: items.append("Earn or refresh primary NEC")
        if not row["pqs_sufficient"]: items.append("Complete additional PQS quals")
        return items if items else ["All criteria met"]
    df["gaps"]      = df.apply(gaps, axis=1)
    df["gap_count"] = df["gaps"].apply(len)
    return df


# =============================================================================
# BILLET MATCH SQL + SCORING
# =============================================================================
BILLET_MATCH_SQL = """
SELECT b.billet_id, b.command_id,
    c.command_name, c.command_type, c.homeport, c.region, c.fleet,
    r.rate_name, r.community AS rate_community, r.is_critical AS rate_is_critical,
    b.rate_required, b.paygrade_required, b.nec_required,
    n.nec_title AS nec_required_title, b.sea_shore, b.is_critical AS billet_is_critical
FROM billet b
JOIN command c  ON b.command_id=c.command_id
JOIN rate r     ON b.rate_required=r.rate_code
LEFT JOIN nec n ON b.nec_required=n.nec_code
WHERE b.is_filled=0 AND b.billet_id NOT LIKE 'BIN-HIST-%'
ORDER BY b.is_critical DESC, c.command_name
"""

SAILOR_POOL_SQL = """
SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name, r.community, r.is_critical AS rate_is_critical,
    s.years_of_service, s.time_in_rate_months, s.primary_nec, s.eaos,
    CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INTEGER) AS months_to_eaos,
    s.num_dependents, s.has_efm, s.current_command_id,
    c.command_name, c.command_type, c.region, c.homeport,
    ms.is_deployable, th.sea_tours, th.shore_tours
FROM sailor s
JOIN rate r ON s.rate_code=r.rate_code
LEFT JOIN command c ON s.current_command_id=c.command_id
LEFT JOIN medical_status ms ON s.dod_id=ms.dod_id
LEFT JOIN v_sailor_tour_history th ON s.dod_id=th.dod_id
WHERE s.status='Active'
"""

def compute_billet_match(sailors_df: pd.DataFrame, billet: pd.Series) -> pd.DataFrame:
    df = sailors_df[(sailors_df["rate_code"] == billet["rate_required"]) &
                    (sailors_df["paygrade"] == billet["paygrade_required"])].copy()
    if df.empty: return df
    nec_req = billet["nec_required"]
    df["match_nec"] = df["primary_nec"].apply(lambda n: 30 if n == nec_req else 0) if pd.notna(nec_req) else 15
    df["match_rotation"] = 0
    if billet["sea_shore"] == "Sea":
        df.loc[df["command_type"] == "Shore", "match_rotation"] = 25
        df.loc[df["command_type"] == "Sea",   "match_rotation"] = 5
    else:
        df.loc[df["command_type"] == "Sea",   "match_rotation"] = 25
        df.loc[df["command_type"] == "Shore", "match_rotation"] = 5
    df["match_dwell"] = 0
    df.loc[df["months_to_eaos"] >= 36, "match_dwell"] = 25
    df.loc[(df["months_to_eaos"] >= 24) & (df["months_to_eaos"] < 36), "match_dwell"] = 15
    df.loc[(df["months_to_eaos"] >= 12) & (df["months_to_eaos"] < 24), "match_dwell"] = 5
    df["match_deployable"] = 20
    if billet["sea_shore"] == "Sea": df.loc[df["is_deployable"] == 0, "match_deployable"] = 0
    df["match_score"] = df["match_nec"] + df["match_rotation"] + df["match_dwell"] + df["match_deployable"]
    df["match_tier"] = df["match_score"].apply(
        lambda s: "Excellent" if s >= 80 else ("Good" if s >= 60 else ("Marginal" if s >= 40 else "Poor")))
    return df.sort_values("match_score", ascending=False)


# =============================================================================
# DEMO PERSONAS
# =============================================================================
DEMO_PERSONAS = {
    "sailor": {
        "dod_id":       "9990001593",
        "name":         "MM(N)2 Rivera",
        "full_title":   "MM(N)2(SW) Rivera, USN",
        "rank_rate":    "Petty Officer Second Class",
        "description":  "Machinist's Mate Nuclear (E5)",
        "unit":         "NAVSTA Pearl Harbor",
        "command_id":   "N00012",
        "icon":         "⚙️",
        "color":        "#088199",
    },
    "commander": {
        "dod_id":       None,
        "name":         "CAPT Martinez",
        "full_title":   "CAPT J.L. Martinez, USN",
        "rank_rate":    "Captain, United States Navy",
        "description":  "Commanding Officer",
        "unit":         "USS GERALD R FORD CVN-78",
        "command_id":   "N00001",
        "icon":         "⚓",
        "color":        "#003B4F",
    },
    "detailer": {
        "dod_id":       None,
        "name":         "YN1 Torres",
        "full_title":   "YN1(SW) Torres, USN",
        "rank_rate":    "Petty Officer First Class",
        "description":  "PERS-43 Detailer, Surface Warfare",
        "unit":         "Naval Personnel Command",
        "command_id":   None,
        "icon":         "📋",
        "color":        "#E8B00F",
    },
}

# =============================================================================
# SESSION STATE DEFAULTS
# =============================================================================
for _key, _val in {
    "logged_in":      False,
    "role":           None,
    "demo_name":      None,
    "demo_dod":       None,
    "demo_command_id":None,
    "demo_unit":      None,
    "demo_icon":      "⚓",
    "demo_color":     "#003B4F",
    "profile_dod":    None,
    "current_page":   None,
    "launchpad_dod":  None,
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val

# =============================================================================
# LOGIN SCREEN
# =============================================================================
if not st.session_state["logged_in"]:
    st.markdown("""
    <style>
    /* ── Hide Streamlit chrome ── */
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* ── Full-page hero background ── */
    [data-testid="stAppViewContainer"] {
        background-image:
            linear-gradient(180deg,
                rgba(4,20,28,0.42) 0%,
                rgba(0,42,58,0.32) 55%,
                rgba(4,20,28,0.50) 100%),
            url("data:image/jpeg;base64,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");
        background-size: cover;
        background-position: center 40%;
        background-attachment: fixed;
    }
    [data-testid="stMain"] > div {
        background: transparent;
    }
    .block-container {
        background: transparent;
        padding-top: 0 !important;
        padding-bottom: 1rem !important;
        max-width: 980px !important;
    }

    /* ── Logo banner ── */
    .login-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg,
            rgba(0,30,42,0.92) 0%,
            rgba(8,38,44,0.88) 100%);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 10px 28px;
        border-radius: 0 0 10px 10px;
        border-bottom: 2px solid rgba(8,129,153,0.5);
        margin-bottom: 10px;
    }

    /* ── Hero title area ── */
    .login-hero-title {
        text-align: center;
        padding: 14px 1rem 10px;
    }
    .login-hero-title {
        background: rgba(2,12,18,0.82);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 16px 40px 14px;
        display: inline-block;
        margin: 0 auto 6px;
        border: 1px solid rgba(8,129,153,0.50);
        box-shadow: 0 4px 24px rgba(0,0,0,0.6);
    }
    .hero-heading {
        font-family: 'Roboto Slab', Georgia, serif;
        font-size: 2.6rem;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: .05em;
        text-shadow:
            2px 2px 0 rgba(0,0,0,0.9),
            0 4px 24px rgba(0,0,0,1),
            0 0 50px rgba(0,0,0,0.95);
        margin: 0 0 8px;
        line-height: 1.1;
    }
    .hero-subtext {
        color: rgba(210,230,240,0.95);
        font-size: 0.90rem;
        margin: 0;
        letter-spacing: .04em;
    }

    /* ── Persona cards — glassmorphism ── */
    .persona-card {
        background: rgba(255,255,255,0.10);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 16px;
        padding: 20px 16px 14px;
        text-align: center;
        transition: all .22s ease;
        cursor: pointer;
    }
    .persona-card:hover {
        background: rgba(255,255,255,0.18);
        border-color: rgba(8,129,153,0.85);
        box-shadow: 0 8px 32px rgba(8,129,153,0.30);
        transform: translateY(-3px);
    }
    .persona-icon { font-size: 2.4rem; margin-bottom: 8px; }
    .persona-role  { font-size: 17px; font-weight: 800; color: #FFFFFF; margin-bottom: 3px; text-shadow: 0 1px 4px rgba(0,0,0,.5); }
    .persona-name  { font-size: 14px; font-weight: 600; color: rgba(220,235,240,0.95); margin-bottom: 4px; }
    .persona-desc  { font-size: 11px; color: rgba(180,210,220,0.85); margin-bottom: 4px; line-height: 1.45; }
    .persona-unit  { font-size: 10px; color: #5BC8DA; font-weight: 700; letter-spacing: .04em; }

    /* ── Divider ── */
    .login-divider {
        text-align: center;
        color: rgba(255,255,255,0.40);
        font-size: 11px;
        letter-spacing: .12em;
        margin: 2px auto 10px;
        text-transform: uppercase;
    }

    /* ── Streamlit buttons on dark bg ── */
    .stButton > button {
        background: rgba(8,129,153,0.75) !important;
        border: 1px solid rgba(8,129,153,0.9) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(4px);
        transition: all .2s;
    }
    .stButton > button:hover {
        background: rgba(8,129,153,0.95) !important;
        box-shadow: 0 4px 16px rgba(8,129,153,0.4) !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

    # Banner with base64-embedded SVG logos (zero external dependencies)
    _IBM_B64  = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNjAgODgiIHdpZHRoPSIxMzAiIGhlaWdodD0iNDQiPgogIDxkZWZzPgogICAgPGNsaXBQYXRoIGlkPSJpYm1fY2xpcCI+CiAgICAgIDx0ZXh0IHg9IjQiIHk9Ijc0IgogICAgICAgICAgICBmb250LWZhbWlseT0iQXJpYWwgQmxhY2ssSGVsdmV0aWNhIE5ldWUsc2Fucy1zZXJpZiIKICAgICAgICAgICAgZm9udC1zaXplPSI3NiIgZm9udC13ZWlnaHQ9IjkwMCIgbGV0dGVyLXNwYWNpbmc9IjYiPklCTTwvdGV4dD4KICAgIDwvY2xpcFBhdGg+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIyNjAiIGhlaWdodD0iODgiIGZpbGw9IndoaXRlIi8+CiAgPHJlY3Qgd2lkdGg9IjI2MCIgaGVpZ2h0PSI4OCIgZmlsbD0iIzFGNzBDMSIgY2xpcC1wYXRoPSJ1cmwoI2libV9jbGlwKSIvPgogIDxyZWN0IHg9IjAiIHdpZHRoPSIyNjAiIHk9IjIyIiAgIGhlaWdodD0iNS41IiBmaWxsPSJ3aGl0ZSIgY2xpcC1wYXRoPSJ1cmwoI2libV9jbGlwKSIvPgogIDxyZWN0IHg9IjAiIHdpZHRoPSIyNjAiIHk9IjMwLjUiIGhlaWdodD0iNS41IiBmaWxsPSJ3aGl0ZSIgY2xpcC1wYXRoPSJ1cmwoI2libV9jbGlwKSIvPgogIDxyZWN0IHg9IjAiIHdpZHRoPSIyNjAiIHk9IjM5IiAgIGhlaWdodD0iNS41IiBmaWxsPSJ3aGl0ZSIgY2xpcC1wYXRoPSJ1cmwoI2libV9jbGlwKSIvPgogIDxyZWN0IHg9IjAiIHdpZHRoPSIyNjAiIHk9IjQ3LjUiIGhlaWdodD0iNS41IiBmaWxsPSJ3aGl0ZSIgY2xpcC1wYXRoPSJ1cmwoI2libV9jbGlwKSIvPgogIDxyZWN0IHg9IjAiIHdpZHRoPSIyNjAiIHk9IjU2IiAgIGhlaWdodD0iNS41IiBmaWxsPSJ3aGl0ZSIgY2xpcC1wYXRoPSJ1cmwoI2libV9jbGlwKSIvPgogIDxyZWN0IHg9IjAiIHdpZHRoPSIyNjAiIHk9IjY0LjUiIGhlaWdodD0iNS41IiBmaWxsPSJ3aGl0ZSIgY2xpcC1wYXRoPSJ1cmwoI2libV9jbGlwKSIvPgo8L3N2Zz4="
    _MNHR_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMjAwIiB3aWR0aD0iODgiIGhlaWdodD0iODgiPgogIDxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjMTExMTExIi8+CiAgPHJlY3QgeD0iNjciIHk9IjAiIHdpZHRoPSI2NiIgaGVpZ2h0PSIxNTUiIGZpbGw9IiNDODk2MEEiLz4KICA8Y2xpcFBhdGggaWQ9ImxwIj48cmVjdCB4PSIwIiB5PSIwIiB3aWR0aD0iNjciIGhlaWdodD0iMTU1Ii8+PC9jbGlwUGF0aD4KICA8ZyBjbGlwLXBhdGg9InVybCgjbHApIiBvcGFjaXR5PSIwLjQ1Ij4KICAgIDxsaW5lIHgxPSItMjAiIHkxPSIyMDAiIHgyPSIxMjAiIHkyPSItNDAiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iOSIvPgogICAgPGxpbmUgeDE9Ii00MCIgeTE9IjIwMCIgeDI9IjEwMCIgeTI9Ii00MCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSI5Ii8+CiAgICA8bGluZSB4MT0iLTYwIiB5MT0iMjAwIiB4Mj0iODAiICB5Mj0iLTQwIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjkiLz4KICAgIDxsaW5lIHgxPSIwIiAgIHkxPSIyMDAiIHgyPSIxNDAiIHkyPSItNDAiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iOSIvPgogICAgPGxpbmUgeDE9IjIwIiAgeTE9IjIwMCIgeDI9IjE2MCIgeTI9Ii00MCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSI5Ii8+CiAgICA8bGluZSB4MT0iNDAiICB5MT0iMjAwIiB4Mj0iMTgwIiB5Mj0iLTQwIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjkiLz4KICA8L2c+CiAgPHBvbHlnb24gcG9pbnRzPSIzMi4wMCwyOC4wMCAzNC40NywzNC42MCA0MS41MSwzNC45MSAzNS45OSwzOS4zMCAzNy44OCw0Ni4wOSAzMi4wMCw0Mi4yMCAyNi4xMiw0Ni4wOSAyOC4wMSwzOS4zMCAyMi40OSwzNC45MSAyOS41MywzNC42MCIgZmlsbD0iI0ZGRkZGRiIvPgogIDxyZWN0IHg9IjEzMyIgeT0iMTYiICB3aWR0aD0iNjciIGhlaWdodD0iMTgiIGZpbGw9IiNDODk2MEEiLz4KICA8cmVjdCB4PSIxMzMiIHk9IjQ0IiAgd2lkdGg9IjY3IiBoZWlnaHQ9IjE4IiBmaWxsPSIjQzg5NjBBIi8+CiAgPHJlY3QgeD0iMTMzIiB5PSI3MiIgIHdpZHRoPSI2NyIgaGVpZ2h0PSIxOCIgZmlsbD0iI0M4OTYwQSIvPgogIDxyZWN0IHg9IjEzMyIgeT0iMTAwIiB3aWR0aD0iNjciIGhlaWdodD0iMTgiIGZpbGw9IiNDODk2MEEiLz4KICA8cG9seWdvbiBwb2ludHM9IjE2OC4wMCwyMi4wMCAxNzAuNDcsMjguNjAgMTc3LjUxLDI4LjkxIDE3MS45OSwzMy4zMCAxNzMuODgsNDAuMDkgMTY4LjAwLDM2LjIwIDE2Mi4xMiw0MC4wOSAxNjQuMDEsMzMuMzAgMTU4LjQ5LDI4LjkxIDE2NS41MywyOC42MCIgZmlsbD0iI0ZGRkZGRiIvPgogIDxjaXJjbGUgY3g9IjEwMCIgY3k9IjUwIiByPSIxMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMTExMTExIiBzdHJva2Utd2lkdGg9IjQuNSIvPgogIDxsaW5lIHgxPSIxMDAiIHkxPSI2MCIgeDI9IjEwMCIgeTI9IjEwOCIgc3Ryb2tlPSIjMTExMTExIiBzdHJva2Utd2lkdGg9IjQuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgPGxpbmUgeDE9IjgyIiB5MT0iNzYiIHgyPSIxMTgiIHkyPSI3NiIgc3Ryb2tlPSIjMTExMTExIiBzdHJva2Utd2lkdGg9IjQuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgPHBhdGggZD0iTTgyLDc2IFE3Miw3NiA3Miw5MCBRNzIsMTAyIDg0LDEwMiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMTExMTExIiBzdHJva2Utd2lkdGg9IjQuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgPHBhdGggZD0iTTExOCw3NiBRMTI4LDc2IDEyOCw5MCBRMTI4LDEwMiAxMTYsMTAyIiBmaWxsPSJub25lIiBzdHJva2U9IiMxMTExMTEiIHN0cm9rZS13aWR0aD0iNC41IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICA8bGluZSB4MT0iODQiIHkxPSIxMDIiIHgyPSI5MiIgeTI9IjEwMiIgc3Ryb2tlPSIjMTExMTExIiBzdHJva2Utd2lkdGg9IjQuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgPGxpbmUgeDE9IjExNiIgeTE9IjEwMiIgeDI9IjEwOCIgeTI9IjEwMiIgc3Ryb2tlPSIjMTExMTExIiBzdHJva2Utd2lkdGg9IjQuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+CiAgPHJlY3QgeD0iMCIgeT0iMTU1IiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjQ1IiBmaWxsPSIjMTExMTExIi8+CiAgPHRleHQgeD0iMTAwIiB5PSIxNzciIGZvbnQtZmFtaWx5PSJBcmlhbCxIZWx2ZXRpY2Esc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOSIgZm9udC13ZWlnaHQ9IjkwMCIKICAgICAgICB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjRkZGRkZGIiBsZXR0ZXItc3BhY2luZz0iMC41Ij4KICAgIDx0c3BhbiBmb250LXdlaWdodD0iMzAwIiBmb250LXN0eWxlPSJpdGFsaWMiPk15PC90c3Bhbj48dHNwYW4gZm9udC13ZWlnaHQ9IjkwMCI+TkFWWTwvdHNwYW4+PHRzcGFuIGZpbGw9IiNDODk2MEEiPkhSPC90c3Bhbj4KICA8L3RleHQ+CiAgPHRleHQgeD0iMTAwIiB5PSIxOTEiIGZvbnQtZmFtaWx5PSJBcmlhbCxIZWx2ZXRpY2Esc2Fucy1zZXJpZiIgZm9udC1zaXplPSI5IiBmb250LXdlaWdodD0iNTAwIgogICAgICAgIGxldHRlci1zcGFjaW5nPSIxLjIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IiNDOEM4QzgiPlNFUlZJTkcgU0FJTE9SUyAyNC83PC90ZXh0Pgo8L3N2Zz4="
    st.markdown(f"""
    <div class="login-banner">
        <img src="data:image/svg+xml;base64,{_MNHR_B64}"
             alt="MyNavy HR" title="MyNavy HR"
             style="height:72px;width:auto;border-radius:6px;"/>
        <div style="flex:1;text-align:center;padding:0 16px;">
            <div style="font-size:1.05rem;font-weight:700;color:#FFFFFF;letter-spacing:.06em;
                        text-shadow:0 1px 6px rgba(0,0,0,.6);">SAILOR DIGITAL TWIN</div>
            <div style="font-size:0.72rem;color:#88C8D8;margin-top:2px;letter-spacing:.05em;">
                MyNavy HR &nbsp;·&nbsp; Developed by IBM &nbsp;·&nbsp; POC Demo
            </div>
        </div>
        <img src="data:image/svg+xml;base64,{_IBM_B64}"
             alt="IBM" title="IBM"
             style="height:38px;width:auto;background:white;padding:4px 10px;border-radius:5px;"/>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('''
    <div style="text-align:center;">
      <div class="login-hero-title">
        <div class="hero-heading">⚓&nbsp; Sailor Digital Twin</div>
        <div class="hero-subtext">MyNavy HR Intelligence Platform &nbsp;·&nbsp; All data is synthetic &nbsp;·&nbsp; No PII</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="login-divider">— Select your role to enter the demo —</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        p = DEMO_PERSONAS["sailor"]
        st.markdown(f"""
        <div class="persona-card">
            <div class="persona-icon">{p['icon']}</div>
            <div class="persona-role">Sailor</div>
            <div class="persona-name">{p['name']}</div>
            <div class="persona-desc">{p['description']}</div>
            <div class="persona-unit">{p['unit']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Login as {p['name']}", key="login_sailor", use_container_width=True):
            st.session_state.update({
                "logged_in": True, "role": "sailor",
                "demo_name": p["name"], "demo_full_title": p["full_title"],
                "demo_dod": p["dod_id"], "demo_command_id": p["command_id"],
                "demo_unit": p["unit"], "demo_icon": p["icon"], "demo_color": p["color"],
                "current_page": "My Digital Twin",
            })
            st.rerun()

    with col2:
        p = DEMO_PERSONAS["commander"]
        st.markdown(f"""
        <div class="persona-card">
            <div class="persona-icon">{p['icon']}</div>
            <div class="persona-role">Commander</div>
            <div class="persona-name">{p['name']}</div>
            <div class="persona-desc">{p['description']}</div>
            <div class="persona-unit">{p['unit']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Login as {p['name']}", key="login_commander", use_container_width=True):
            st.session_state.update({
                "logged_in": True, "role": "commander",
                "demo_name": p["name"], "demo_full_title": p["full_title"],
                "demo_dod": p["dod_id"], "demo_command_id": p["command_id"],
                "demo_unit": p["unit"], "demo_icon": p["icon"], "demo_color": p["color"],
                "current_page": "Command Dashboard",
            })
            st.rerun()

    with col3:
        p = DEMO_PERSONAS["detailer"]
        st.markdown(f"""
        <div class="persona-card">
            <div class="persona-icon">{p['icon']}</div>
            <div class="persona-role">Detailer / HR</div>
            <div class="persona-name">{p['name']}</div>
            <div class="persona-desc">{p['description']}</div>
            <div class="persona-unit">{p['unit']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Login as {p['name']}", key="login_detailer", use_container_width=True):
            st.session_state.update({
                "logged_in": True, "role": "detailer",
                "demo_name": p["name"], "demo_full_title": p["full_title"],
                "demo_dod": p["dod_id"], "demo_command_id": p["command_id"],
                "demo_unit": p["unit"], "demo_icon": p["icon"], "demo_color": p["color"],
                "current_page": "Detailing / Billet Match",
            })
            st.rerun()

    st.stop()


# =============================================================================
# ROLE-BASED SIDEBAR NAVIGATION
# =============================================================================
role             = st.session_state["role"]
demo_name        = st.session_state["demo_name"]
demo_full_title  = st.session_state.get("demo_full_title", demo_name)
demo_dod         = st.session_state["demo_dod"]
demo_command_id  = st.session_state["demo_command_id"]
demo_unit        = st.session_state["demo_unit"]
demo_icon        = st.session_state["demo_icon"]
demo_color       = st.session_state["demo_color"]

ROLE_PAGES = {
    "sailor": [
        "My Digital Twin",
        "My Career",
        "My Pay & Entitlements",
        "My Training & Quals",
    ],
    "commander": [
        "Command Dashboard",
        "Retention Risk",
        "Promotion Readiness",
        "Detailing / Billet Match",
        "Analytics & Trends",
        "Cases & Workflows",
        "Sailor Profile",
    ],
    "detailer": [
        "Detailing / Billet Match",
        "Cases & Workflows",
        "Retention Risk",
        "Analytics & Trends",
        "Sailor Profile",
    ],
}

PAGE_ICONS = {
    "My Digital Twin":        "🏠",
    "My Career":              "📈",
    "My Pay & Entitlements":  "💰",
    "My Training & Quals":    "🎓",
    "Command Dashboard":      "🎯",
    "Retention Risk":         "⚠️",
    "Promotion Readiness":    "📈",
    "Detailing / Billet Match": "📦",
    "Analytics & Trends":     "📊",
    "Cases & Workflows":      "📋",
    "Sailor Profile":         "👤",
}

pages_for_role = ROLE_PAGES[role]

# Ensure current_page is valid for this role
if st.session_state["current_page"] not in pages_for_role:
    st.session_state["current_page"] = pages_for_role[0]

# Sidebar persona badge
role_badge = {"sailor": "SAILOR", "commander": "COMMANDER", "detailer": "DETAILER"}[role]
st.sidebar.markdown(
    f"""<div style="padding:1rem 0.5rem 0.75rem;">
    <div style="text-align:center;margin-bottom:10px;">
      <div style="font-size:2.2rem;">{demo_icon}</div>
      <div style="font-family:'Roboto Slab',serif;font-size:14px;font-weight:700;
                  color:#fff;letter-spacing:.05em;margin-top:4px;">SAILOR DIGITAL TWIN</div>
      <div style="font-size:10px;color:#C6CCD0;margin-top:2px;">MyNavy HR — POC Demo</div>
    </div>
    <div style="background:rgba(255,255,255,.08);border-radius:8px;padding:10px 12px;">
      <div style="font-size:11px;color:#C6CCD0;font-weight:600;text-transform:uppercase;
                  letter-spacing:.08em;margin-bottom:4px;">{role_badge}</div>
      <div style="font-size:14px;font-weight:700;color:#fff;">{demo_name}</div>
      <div style="font-size:11px;color:#C6CCD0;margin-top:2px;">{demo_unit}</div>
    </div>
    </div>""",
    unsafe_allow_html=True,
)
st.sidebar.divider()

# Page navigation — driven by session state so drill-down buttons work
_idx = pages_for_role.index(st.session_state["current_page"]) if st.session_state["current_page"] in pages_for_role else 0
_labels = [f"{PAGE_ICONS.get(p,'')} {p}" for p in pages_for_role]
_selected_label = st.sidebar.radio("Navigate", _labels, index=_idx, label_visibility="collapsed")
page = pages_for_role[_labels.index(_selected_label)]
st.session_state["current_page"] = page

st.sidebar.divider()

# Switch role button
if st.sidebar.button("🔄 Switch Role / Logout", use_container_width=True):
    for k in ["logged_in","role","demo_name","demo_full_title","demo_dod",
              "demo_command_id","demo_unit","demo_icon","demo_color",
              "profile_dod","current_page","launchpad_dod"]:
        st.session_state[k] = None if k != "logged_in" else False
    st.rerun()

st.sidebar.markdown(
    f"""<div style="font-size:10px;color:#C6CCD0;line-height:1.8;padding:0.5rem 0;">
    {'🗄️ NSIPS · TFMMS · NTMPS<br>🔒 MRRS · DJMS · CIRIMS<br>📊 5,000 synthetic sailors<br>🚫 No PII anywhere' if role != 'sailor' else
     '🔒 Viewing your personal data<br>📊 Sourced from 6 systems<br>🚫 No PII anywhere'}
    </div>""",
    unsafe_allow_html=True,
)


# =============================================================================
# PAGE: COMMAND HEALTH DASHBOARD
# =============================================================================
if page == "Command Dashboard":
    cmd_id = demo_command_id  # "N00001" for CAPT Martinez

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#003B4F 0%,#08262C 100%);
                border-radius:12px;padding:24px 28px;margin-bottom:20px;color:#fff;">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;
                      color:#C6CCD0;margin-bottom:4px;">Command Health Dashboard</div>
          <div style="font-size:24px;font-weight:800;font-family:'Roboto Slab',serif;">
            {demo_unit}
          </div>
          <div style="font-size:13px;color:#C6CCD0;margin-top:4px;">{demo_full_title} &nbsp;·&nbsp; Commanding Officer</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:11px;color:#C6CCD0;text-transform:uppercase;letter-spacing:.08em;">Last Refreshed</div>
          <div style="font-size:13px;font-weight:600;">Live from Digital Twin</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Aggregate command readiness score ─────────────────────────────────────
    cmd_ready = query("""
        SELECT
            AVG(CASE WHEN ms.is_deployable=1 AND ms.dental_class<=2 THEN 25.0
                     WHEN ms.is_deployable=1 THEN 15.0 ELSE 0.0 END) AS med_pts,
            AVG(CASE WHEN nc.current_necs>=1 THEN 25.0
                     WHEN nc.total_necs>0 THEN 10.0 ELSE 15.0 END) AS train_pts,
            AVG(CASE WHEN fr.recent_avg>=3.7 THEN 25.0
                     WHEN fr.recent_avg>=3.0 THEN 15.0 ELSE 5.0 END) AS perf_pts,
            AVG(CASE WHEN CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INT)>24 THEN 25.0
                     WHEN CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INT)>12 THEN 15.0
                     WHEN CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INT)>0 THEN 5.0
                     ELSE 0.0 END) AS svc_pts,
            COUNT(*) AS total_sailors
        FROM sailor s
        LEFT JOIN medical_status ms ON s.dod_id=ms.dod_id
        LEFT JOIN (SELECT dod_id,
            SUM(CASE WHEN qual_type='NEC' AND is_current=1 THEN 1 ELSE 0 END) AS current_necs,
            SUM(CASE WHEN qual_type='NEC' THEN 1 ELSE 0 END) AS total_necs
            FROM qualification GROUP BY dod_id) nc ON s.dod_id=nc.dod_id
        LEFT JOIN (SELECT dod_id, AVG(trait_avg) AS recent_avg FROM
            (SELECT dod_id, trait_avg, ROW_NUMBER() OVER
             (PARTITION BY dod_id ORDER BY period_end DESC) AS rn FROM fitrep)
            WHERE rn<=3 GROUP BY dod_id) fr ON s.dod_id=fr.dod_id
        WHERE s.status='Active' AND s.current_command_id=?
    """, (cmd_id,))

    rr = cmd_ready.iloc[0] if not cmd_ready.empty else None
    if rr is not None:
        cmd_score  = int(round(rr["med_pts"] + rr["train_pts"] + rr["perf_pts"] + rr["svc_pts"]))
        total_sail = int(rr["total_sailors"])
    else:
        cmd_score, total_sail = 0, 0

    cmd_label = ("Mission Ready" if cmd_score >= 85 else
                 "Conditionally Ready" if cmd_score >= 65 else
                 "Limited Readiness")
    cmd_color = "#1a7a4a" if cmd_score >= 85 else ("#E8B00F" if cmd_score >= 65 else "#B30003")

    # Alert counts
    srb_count   = query("SELECT COUNT(*) c FROM sailor s JOIN pay_record pr ON s.dod_id=pr.dod_id WHERE s.status='Active' AND s.current_command_id=? AND pr.srb_zone IS NOT NULL AND julianday(s.eaos)-julianday('now') BETWEEN 0 AND 548", (cmd_id,)).iloc[0]["c"]
    nondep_count= query("SELECT COUNT(*) c FROM sailor s JOIN medical_status ms ON s.dod_id=ms.dod_id WHERE s.status='Active' AND s.current_command_id=? AND ms.is_deployable=0", (cmd_id,)).iloc[0]["c"]
    nec_count   = query("SELECT COUNT(DISTINCT s.dod_id) c FROM sailor s JOIN qualification q ON s.dod_id=q.dod_id WHERE s.status='Active' AND s.current_command_id=? AND q.qual_type='NEC' AND q.is_current=0", (cmd_id,)).iloc[0]["c"]
    pcs_count   = query("SELECT COUNT(*) c FROM sailor s WHERE s.status='Active' AND s.current_command_id=? AND julianday(s.eaos)-julianday('now') BETWEEN 365 AND 608", (cmd_id,)).iloc[0]["c"]

    # ── Readiness score + KPI row ─────────────────────────────────────────────
    r_col, k1, k2, k3, k4 = st.columns([1.5, 1, 1, 1, 1])
    with r_col:
        st.markdown(f"""
        <div style="background:#fff;border:2px solid {cmd_color};border-radius:12px;
                    padding:20px;text-align:center;height:100%;">
          <div style="font-size:11px;color:#546E7A;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">Command Readiness</div>
          <div style="font-size:52px;font-weight:800;color:{cmd_color};line-height:1;">{cmd_score}</div>
          <div style="font-size:11px;color:{cmd_color};font-weight:700;text-transform:uppercase;margin-top:4px;">{cmd_label}</div>
          <div style="font-size:12px;color:#546E7A;margin-top:6px;">{total_sail} Active Sailors</div>
        </div>
        """, unsafe_allow_html=True)
    with k1:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #B30003;"><div class="metric-value" style="color:#B30003;">{srb_count}</div><div class="metric-label">SRB / Reenlistment Cases</div><div style="font-size:11px;color:#B30003;margin-top:4px;">⚡ Action required</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #B30003;"><div class="metric-value" style="color:#B30003;">{nondep_count}</div><div class="metric-label">Non-Deployable</div><div style="font-size:11px;color:#B30003;margin-top:4px;">⚡ Med review needed</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #E8B00F;"><div class="metric-value" style="color:#E8B00F;">{nec_count}</div><div class="metric-label">Lapsed NEC Certs</div><div style="font-size:11px;color:#E8B00F;margin-top:4px;">⚠️ Recert required</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #088199;"><div class="metric-value" style="color:#088199;">{pcs_count}</div><div class="metric-label">In PCS Window</div><div style="font-size:11px;color:#088199;margin-top:4px;">📦 Orders pending</div></div>', unsafe_allow_html=True)

    # ── Readiness domain breakdown ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Readiness by Domain")
    dom_cols = st.columns(4)
    domains = [
        ("🏥 Medical",    int(round(rr["med_pts"])) if rr is not None else 0,   25),
        ("🎓 Training",   int(round(rr["train_pts"])) if rr is not None else 0, 25),
        ("📋 Performance",int(round(rr["perf_pts"])) if rr is not None else 0,  25),
        ("⚓ Service",    int(round(rr["svc_pts"])) if rr is not None else 0,   25),
    ]
    for col, (label, pts, mx) in zip(dom_cols, domains):
        pct = pts / mx * 100
        dc  = "#1a7a4a" if pct >= 80 else ("#E8B00F" if pct >= 60 else "#B30003")
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
              <div style="font-size:13px;font-weight:700;color:#003B4F;margin-bottom:8px;">{label}</div>
              <div style="font-size:28px;font-weight:800;color:{dc};">{pts}<span style="font-size:14px;color:#aaa;">/{mx}</span></div>
              <div style="background:#eee;border-radius:4px;height:8px;margin-top:8px;">
                <div style="background:{dc};width:{pct:.0f}%;height:8px;border-radius:4px;"></div>
              </div>
              <div style="font-size:11px;color:{dc};margin-top:4px;font-weight:600;">{pct:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Top 5 sailors requiring action ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔴 Top Sailors Requiring Action Today")
    st.markdown('<p style="color:#546E7A;font-size:13px;margin-top:-10px;">Ranked by retention risk score — click any sailor to view their full Digital Twin profile</p>', unsafe_allow_html=True)

    top5_sql = f"""
    WITH fitrep_recent AS (
        SELECT dod_id, AVG(trait_avg) AS recent_avg
        FROM (SELECT dod_id, trait_avg,
                ROW_NUMBER() OVER (PARTITION BY dod_id ORDER BY period_end DESC) AS rn
              FROM fitrep) ranked WHERE rn<=3 GROUP BY dod_id
    ),
    nec_currency AS (
        SELECT dod_id,
               SUM(CASE WHEN qual_type='NEC' AND is_current=1 THEN 1 ELSE 0 END) AS curr_necs,
               SUM(CASE WHEN qual_type='NEC' AND is_current=0 THEN 1 ELSE 0 END) AS lapsed_necs
        FROM qualification GROUP BY dod_id
    )
    SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name, r.community, r.is_critical,
           CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INTEGER) AS months_to_eaos,
           ms.is_deployable, pr.srb_zone, pr.srb_multiplier,
           fr.recent_avg AS fitrep_avg,
           nc.curr_necs, nc.lapsed_necs,
           c.command_type
    FROM sailor s
    JOIN rate r ON s.rate_code=r.rate_code
    LEFT JOIN medical_status ms   ON s.dod_id=ms.dod_id
    LEFT JOIN pay_record pr       ON s.dod_id=pr.dod_id
    LEFT JOIN fitrep_recent fr    ON s.dod_id=fr.dod_id
    LEFT JOIN nec_currency nc     ON s.dod_id=nc.dod_id
    LEFT JOIN command c           ON s.current_command_id=c.command_id
    WHERE s.status='Active' AND s.current_command_id='{cmd_id}'
    ORDER BY
        (CASE WHEN ms.is_deployable=0 THEN 30 ELSE 0 END) +
        (CASE WHEN julianday(s.eaos)-julianday('now') BETWEEN 0 AND 180 THEN 25 ELSE 0 END) +
        (CASE WHEN pr.srb_zone IS NOT NULL AND julianday(s.eaos)-julianday('now') BETWEEN 0 AND 548 THEN 15 ELSE 0 END) +
        (CASE WHEN nc.lapsed_necs>0 THEN 10 ELSE 0 END) +
        (CASE WHEN fr.recent_avg<3.5 THEN 10 ELSE 0 END)
    DESC LIMIT 6
    """
    top5 = query(top5_sql)

    if top5.empty:
        st.info("No high-risk sailors found in this command.")
    else:
        for _, row in top5.iterrows():
            concerns = []
            if row.get("is_deployable") == 0:
                concerns.append(("🔴", "Non-Deployable"))
            mos = int(row.get("months_to_eaos") or 99)
            if mos <= 6:
                concerns.append(("🔴", f"EAOS in {mos} months"))
            elif mos <= 12:
                concerns.append(("🟡", f"EAOS in {mos} months"))
            if row.get("srb_zone") and pd.notna(row.get("srb_zone")) and mos <= 18:
                multiplier = row.get("srb_multiplier")
                multiplier_val = float(multiplier) if multiplier and pd.notna(multiplier) else 0.0
                concerns.append(("🟡", f"SRB Zone {row['srb_zone']} ×{multiplier_val:.1f} pending"))
            if (row.get("lapsed_necs") or 0) > 0:
                concerns.append(("🟡", f"{int(row['lapsed_necs'])} lapsed NEC(s)"))
            if row.get("fitrep_avg") and float(row["fitrep_avg"]) < 3.5:
                concerns.append(("🟡", f"FITREP avg {float(row['fitrep_avg']):.2f}"))
            if not concerns:
                concerns.append(("🟢", "Routine check-in"))

            concern_html = " &nbsp;|&nbsp; ".join(f"{ic} {txt}" for ic, txt in concerns[:3])
            top_icon     = concerns[0][0] if concerns else "🟢"
            is_critical  = bool(row.get("is_critical"))
            crit_badge   = '<span style="background:#B30003;color:#fff;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700;margin-left:6px;">CRITICAL RATE</span>' if is_critical else ""

            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e0e0e0;border-left:4px solid
                    {'#B30003' if top_icon=='🔴' else '#E8B00F'};
                    border-radius:8px;padding:12px 16px;margin-bottom:8px;">
                  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;">
                    <span style="font-size:15px;font-weight:700;color:#003B4F;">
                      {row['paygrade']} {row['rate_code']}
                    </span>
                    <span style="font-size:12px;color:#546E7A;">{row.get('rate_name','')}</span>
                    {crit_badge}
                  </div>
                  <div style="font-size:12px;color:#546E7A;margin-top:6px;">{concern_html}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("View Profile →", key=f"drill_{row['dod_id']}", use_container_width=True):
                    st.session_state["profile_dod"]    = row["dod_id"]
                    st.session_state["current_page"]   = "Sailor Profile"
                    st.rerun()

    # ── Force composition mini charts ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🪖 Command Force Snapshot")
    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        pg_dist = query("SELECT paygrade, COUNT(*) AS n FROM sailor WHERE status='Active' AND current_command_id=? GROUP BY paygrade ORDER BY paygrade", (cmd_id,))
        if not pg_dist.empty:
            st.markdown("**Paygrade Distribution**")
            st.bar_chart(pg_dist.set_index("paygrade"), color="#088199", height=200)

    with fc2:
        comm_dist = query("SELECT r.community, COUNT(*) AS n FROM sailor s JOIN rate r ON s.rate_code=r.rate_code WHERE s.status='Active' AND s.current_command_id=? GROUP BY r.community ORDER BY n DESC", (cmd_id,))
        if not comm_dist.empty:
            st.markdown("**By Community**")
            st.bar_chart(comm_dist.set_index("community"), color="#003B4F", height=200)

    with fc3:
        eaos_dist = query("""
            SELECT CASE
                WHEN julianday(eaos)-julianday('now') BETWEEN 0 AND 180 THEN '0-6 mo'
                WHEN julianday(eaos)-julianday('now') BETWEEN 181 AND 365 THEN '6-12 mo'
                WHEN julianday(eaos)-julianday('now') BETWEEN 366 AND 548 THEN '12-18 mo'
                ELSE '18+ mo' END AS window, COUNT(*) AS n
            FROM sailor WHERE status='Active' AND current_command_id=?
            GROUP BY window
        """, (cmd_id,))
        if not eaos_dist.empty:
            eaos_order = ["0-6 mo","6-12 mo","12-18 mo","18+ mo"]
            eaos_dist["window"] = pd.Categorical(eaos_dist["window"], categories=eaos_order, ordered=True)
            eaos_dist = eaos_dist.sort_values("window")
            st.markdown("**EAOS Horizon**")
            import altair as alt
            eaos_chart = alt.Chart(eaos_dist).mark_bar(color="#B30003").encode(
                x=alt.X("window:O", sort=eaos_order, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("n:Q", title="Sailors", scale=alt.Scale(zero=True)),
                tooltip=[alt.Tooltip("window:O", title="Window"), alt.Tooltip("n:Q", title="Sailors")]
            ).properties(height=200)
            st.altair_chart(eaos_chart, use_container_width=True)


# =============================================================================
# SAILOR PAGES  (role == "sailor")
# =============================================================================
elif page == "My Digital Twin":
    dod_id    = demo_dod
    sailor_df = query("SELECT * FROM v_active_sailor WHERE dod_id=?", (dod_id,))
    if sailor_df.empty:
        st.error("Profile not found."); st.stop()
    s = sailor_df.iloc[0]

    ri_score, ri_label, ri_color, ri_breakdown = compute_readiness_indicator(dod_id)
    lc_idx,  lc_sub   = derive_lifecycle_stage(s)
    snap_rows          = get_dt_snapshot(dod_id, s)
    actions            = generate_ai_actions(dod_id, s)
    mos_eaos           = int(s.get("months_to_eaos") or 99)
    yos                = float(s.get("years_of_service") or 0)

    # Welcome banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#003B4F 0%,#088199 100%);
                border-radius:12px;padding:24px 28px;margin-bottom:20px;color:#fff;">
      <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div style="width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.15);
                    display:flex;align-items:center;justify-content:center;
                    font-size:26px;font-weight:700;flex-shrink:0;">
          {demo_icon}
        </div>
        <div style="flex:1;min-width:200px;">
          <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;
                      color:rgba(255,255,255,.7);margin-bottom:4px;">Welcome back</div>
          <div style="font-size:22px;font-weight:800;font-family:'Roboto Slab',serif;">{demo_full_title}</div>
          <div style="font-size:13px;color:rgba(255,255,255,.8);margin-top:4px;">
            {s.get('rate_name','')} &nbsp;·&nbsp; {s.get('community','')} Community
            &nbsp;·&nbsp; {s.get('command_name','')} &nbsp;·&nbsp; YOS: {yos:.1f}
          </div>
        </div>
        <div style="text-align:center;flex-shrink:0;">
          <div style="font-size:48px;font-weight:800;color:#fff;line-height:1;">{ri_score}%</div>
          <div style="font-size:11px;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.8);">{ri_label}</div>
          <div style="font-size:10px;color:rgba(255,255,255,.6);margin-top:2px;">Your Mission Readiness</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # EAOS urgency banner (if < 12 months)
    if mos_eaos <= 12:
        srb_rec = query("SELECT srb_zone, srb_multiplier, srb_eligible_until FROM pay_record WHERE dod_id=?", (dod_id,))
        if not srb_rec.empty and srb_rec.iloc[0]["srb_zone"]:
            p = srb_rec.iloc[0]
            st.markdown(f"""
            <div style="background:#FFF3CD;border:1px solid #E8B00F;border-left:5px solid #E8B00F;
                        border-radius:8px;padding:14px 18px;margin-bottom:16px;font-size:13px;">
              ⚡ <strong>Action Needed — {mos_eaos} months to EAOS:</strong>
              You are eligible for an SRB Zone {p['srb_zone']} reenlistment bonus
              (×{float(p['srb_multiplier']):.1f} multiplier, eligible until {str(p['srb_eligible_until'])[:10]}).
              Speak with your career counselor to initiate your package. Policy: MILPERSMAN 1160-120.
            </div>
            """, unsafe_allow_html=True)

    # Lifecycle timeline
    st.markdown(render_lifecycle_html(lc_idx, lc_sub), unsafe_allow_html=True)

    # Snapshot + readiness breakdown side by side
    snap_col, ready_col = st.columns([3, 2])
    with snap_col:
        section("Digital Twin Snapshot")
        st.markdown(render_dt_snapshot(snap_rows), unsafe_allow_html=True)
    with ready_col:
        section("Readiness Breakdown")
        for domain, pts in ri_breakdown.items():
            pct = pts / 25 * 100
            dc  = "#1a7a4a" if pct >= 80 else ("#E8B00F" if pct >= 50 else "#B30003")
            st.markdown(f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;font-size:13px;">
                <span>{domain}</span><span style="color:{dc};font-weight:600;">{pts}/25</span>
              </div>
              <div style="background:#eee;border-radius:4px;height:8px;margin-top:4px;">
                <div style="background:{dc};width:{pct:.0f}%;height:8px;border-radius:4px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # AI actions
    st.divider()
    section("🤖 Your AI-Recommended Next Steps")
    st.markdown('<p style="color:#546E7A;font-size:12px;margin-top:-8px;">Personalized recommendations based on your Digital Twin data</p>', unsafe_allow_html=True)
    for act in actions[:3]:
        st.markdown(render_ai_card(act, 0), unsafe_allow_html=True)
    st.caption("These are rule-based recommendations for informational purposes only. Consult your chain of command for official guidance.")

# ── MY CAREER ────────────────────────────────────────────────────────────────
elif page == "My Career":
    dod_id = demo_dod
    page_header("My Career", "Your promotion readiness, FITREP history, and career trajectory")

    prom_raw = query(PROMOTION_SQL)
    prom_df  = compute_promotion_readiness(prom_raw)
    p_row    = prom_df[prom_df["dod_id"] == dod_id]

    if p_row.empty:
        st.info("Promotion readiness data not available (sailor may not be in an eligible paygrade).")
    else:
        p = p_row.iloc[0]
        pro_score = int(p["readiness_score"])
        pro_tier  = p["readiness_tier"]
        pro_col   = "#1a7a4a" if pro_tier == "Highly Competitive" else ("#088199" if pro_tier == "Competitive" else ("#E8B00F" if pro_tier == "Approaching" else "#B30003"))

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;border-left:4px solid {pro_col};">
              <div style="font-size:36px;font-weight:800;color:{pro_col};">{pro_score}</div>
              <div class="metric-label">Promotion Readiness Score</div>
              <div style="font-size:12px;color:{pro_col};font-weight:600;margin-top:4px;">{pro_tier}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
              <div style="font-size:24px;font-weight:800;color:#003B4F;">→ {p.get('next_paygrade','—')}</div>
              <div class="metric-label">Target Paygrade</div>
              <div style="font-size:12px;color:#546E7A;margin-top:4px;">TIR eligible: {'✅ Yes' if p.get('tir_eligible') else '❌ No'}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
              <div style="font-size:24px;font-weight:800;color:#003B4F;">{p.get('career_trait_avg',0):.2f}</div>
              <div class="metric-label">Career FITREP Average</div>
              <div style="font-size:12px;color:#546E7A;margin-top:4px;">Threshold: 3.70 for competitive</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 📋 Advancement Gaps")
        gaps = p.get("gaps", [])
        if gaps == ["All criteria met"]:
            st.success("✅ All advancement criteria met. You are competitive for promotion.")
        else:
            for gap in gaps:
                st.markdown(f"""
                <div style="background:#FFF3CD;border-left:4px solid #E8B00F;padding:10px 14px;
                            border-radius:4px;margin-bottom:8px;font-size:13px;">⚠️ {gap}</div>
                """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 📊 FITREP History")
    fitrep_hist = query("SELECT period_start, period_end, paygrade_at_eval, trait_avg, promotion_recommendation, summary_group_size, is_competitive FROM fitrep WHERE dod_id=? ORDER BY period_end DESC", (dod_id,))
    if fitrep_hist.empty:
        st.info("No FITREP records found.")
    else:
        fitrep_hist["Competitive"] = fitrep_hist["is_competitive"].map({1:"✅","0":"❌", 0:"❌"})
        st.dataframe(fitrep_hist[["period_start","period_end","paygrade_at_eval","trait_avg","promotion_recommendation","summary_group_size","Competitive"]].rename(columns={
            "period_start":"Period Start","period_end":"Period End","paygrade_at_eval":"Grade",
            "trait_avg":"Trait Avg","promotion_recommendation":"Recommendation",
            "summary_group_size":"Group Size"
        }), use_container_width=True, hide_index=True)

    st.markdown("#### 🎯 Advancement Exam History")
    exams = query("SELECT exam_cycle, target_paygrade, standard_score, passed, exam_date FROM advancement_exam WHERE dod_id=? ORDER BY exam_date DESC LIMIT 6", (dod_id,))
    if exams.empty:
        st.info("No exam records found.")
    else:
        exams["Result"] = exams["passed"].map({1:"✅ Passed", 0:"❌ Failed"})
        st.dataframe(exams[["exam_cycle","target_paygrade","standard_score","Result","exam_date"]].rename(columns={
            "exam_cycle":"Cycle","target_paygrade":"Target","standard_score":"Score","exam_date":"Date"
        }), use_container_width=True, hide_index=True)


# ── MY PAY & ENTITLEMENTS ─────────────────────────────────────────────────────
elif page == "My Pay & Entitlements":
    dod_id = demo_dod
    page_header("My Pay & Entitlements", "Your complete monthly entitlements, SRB eligibility, and service obligations")

    pay_rec = query("SELECT * FROM pay_record WHERE dod_id=?", (dod_id,))
    sailor_df = query("SELECT * FROM v_active_sailor WHERE dod_id=?", (dod_id,))
    if pay_rec.empty or sailor_df.empty:
        st.warning("No pay record found."); st.stop()
    p  = pay_rec.iloc[0]
    s  = sailor_df.iloc[0]

    base   = float(p["base_pay_monthly"]   or 0)
    bah    = float(p["bah_monthly"]         or 0)
    bas    = float(p["bas_monthly"]         or 0)
    sea    = float(p["sea_pay_monthly"]     or 0)
    spec   = float(p["special_pay_monthly"] or 0)
    total  = base + bah + bas + sea + spec
    srb_z  = p["srb_zone"]
    srb_m  = float(p["srb_multiplier"] or 0)
    srb_u  = str(p["srb_eligible_until"] or "—")[:10]
    mos    = int(s.get("months_to_eaos") or 99)

    # Pay summary cards
    tk1, tk2, tk3 = st.columns(3)
    with tk1:
        st.markdown(f'<div class="metric-card" style="text-align:center;border-left:4px solid #003B4F;"><div style="font-size:28px;font-weight:800;color:#003B4F;">${total:,.0f}</div><div class="metric-label">Total Monthly Pay</div><div style="font-size:11px;color:#546E7A;margin-top:4px;">All entitlements combined</div></div>', unsafe_allow_html=True)
    with tk2:
        st.markdown(f'<div class="metric-card" style="text-align:center;"><div style="font-size:28px;font-weight:800;color:#088199;">${base:,.0f}</div><div class="metric-label">Basic Pay</div><div style="font-size:11px;color:#546E7A;margin-top:4px;">{s.get("paygrade","")} — Taxable</div></div>', unsafe_allow_html=True)
    with tk3:
        srb_color = "#088199" if srb_z else "#aaa"
        srb_label = f"SRB Zone {srb_z} (×{srb_m:.1f})" if srb_z else "Not Eligible"
        st.markdown(f'<div class="metric-card" style="text-align:center;"><div style="font-size:18px;font-weight:800;color:{srb_color};">{srb_label}</div><div class="metric-label">SRB Status</div><div style="font-size:11px;color:#546E7A;margin-top:4px;">Eligible until: {srb_u}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💵 Monthly Entitlements Breakdown")
    rows_ent = [
        ("Basic Pay",               f"${base:,.0f}",  "#003B4F", "NSIPS/DJMS", "Taxable",     "All active duty members receive basic pay based on grade and YOS."),
        ("BAH (Basic Allowance for Housing)", f"${bah:,.0f}", "#003B4F", "NSIPS/DJMS", "Non-Taxable", "BAH based on paygrade, dependent status, and duty station."),
        ("BAS (Basic Allowance for Subsistence)", f"${bas:,.0f}", "#003B4F", "NSIPS/DJMS", "Non-Taxable","Flat rate to offset cost of meals for enlisted members."),
        ("Sea Pay",                 f"${sea:,.0f}",   "#088199" if sea else "#ccc", "NSIPS", "Taxable",    "Career sea pay for assignment to qualifying sea duty."),
        ("Special / Nuclear Pay",   f"${spec:,.0f}",  "#088199" if spec else "#ccc","NSIPS","Taxable",    "Special duty or nuclear propulsion pay per Navy policy."),
    ]
    tbl  = '<div style="border:1px solid #C6CCD0;border-radius:8px;overflow:hidden;margin-bottom:16px;">'
    tbl += '<div style="background:#003B4F;color:#fff;padding:10px 16px;font-size:12px;font-weight:700;display:grid;grid-template-columns:2.5fr .8fr .8fr .8fr;gap:8px;"><span>Entitlement</span><span>Monthly</span><span>Source</span><span>Tax Status</span></div>'
    for i, (name, amt, col, src, tax, _note) in enumerate(rows_ent):
        bg = "#f9f9f9" if i % 2 == 0 else "#fff"
        tbl += f'<div style="background:{bg};padding:9px 16px;font-size:13px;display:grid;grid-template-columns:2.5fr .8fr .8fr .8fr;gap:8px;border-top:1px solid #eee;"><span>{name}</span><span style="font-weight:700;color:{col};">{amt}</span><span style="color:#546E7A;">{src}</span><span style="color:#546E7A;">{tax}</span></div>'
    tbl += f'<div style="background:#EEF2F4;padding:10px 16px;font-size:14px;font-weight:700;display:grid;grid-template-columns:2.5fr .8fr .8fr .8fr;gap:8px;border-top:2px solid #003B4F;"><span>TOTAL</span><span style="color:#003B4F;">${total:,.0f}</span><span></span><span></span></div>'
    tbl += '</div>'
    st.markdown(tbl, unsafe_allow_html=True)

    # SRB / obligation alerts
    if srb_z and mos <= 18:
        st.markdown(f"""
        <div style="background:#E8F8FA;border-left:5px solid #088199;padding:14px 18px;border-radius:6px;margin-bottom:12px;">
          ✅ <strong>SRB Opportunity:</strong> You qualify for an SRB Zone {srb_z} reenlistment bonus
          at a ×{srb_m:.1f} multiplier. With {mos} months to EAOS, your counseling window is open <strong>now</strong>.
          Contact your career counselor to initiate your SRB package in NSIPS.
          <br><small style="color:#546E7A;">Policy: MILPERSMAN 1160-120 &nbsp;|&nbsp; Eligible until: {srb_u}</small>
        </div>
        """, unsafe_allow_html=True)
    if mos <= 18:
        st.markdown(f"""
        <div class="pay-alert">
          ⚠️ <strong>EAOS Alert — {mos} months remaining:</strong>
          PCS travel entitlements and separation allowances may apply.
          Ensure your DD-214, final FITREP, and transition documentation are initiated NLT 12 months prior.
          <br><small>Policy: MILPERSMAN 1900-010 &nbsp;|&nbsp; System: NSIPS / TOPS</small>
        </div>
        """, unsafe_allow_html=True)

# ── MY TRAINING & QUALS ───────────────────────────────────────────────────────
elif page == "My Training & Quals":
    dod_id = demo_dod
    page_header("My Training & Quals", "Your NEC certifications, PQS qualifications, and advancement exam history")

    df_nec  = query("SELECT qual_code, qual_title, date_earned, currency_expires, is_current FROM qualification WHERE dod_id=? AND qual_type='NEC' ORDER BY date_earned DESC", (dod_id,))
    df_pqs  = query("SELECT qual_code, qual_title, date_earned, granting_command FROM qualification WHERE dod_id=? AND qual_type='PQS' ORDER BY date_earned DESC", (dod_id,))
    df_exam = query("SELECT exam_cycle, target_paygrade, standard_score, passed, exam_date FROM advancement_exam WHERE dod_id=? ORDER BY exam_date DESC LIMIT 6", (dod_id,))

    # NEC summary
    curr_necs   = (df_nec["is_current"] == 1).sum() if not df_nec.empty else 0
    lapsed_necs = (df_nec["is_current"] == 0).sum() if not df_nec.empty else 0
    n1, n2, n3 = st.columns(3)
    n1.metric("Total NECs", len(df_nec))
    n2.metric("Current", int(curr_necs))
    n3.metric("Lapsed ⚠️", int(lapsed_necs))
    st.divider()

    st.markdown("#### ⚙️ NEC Qualifications")
    if df_nec.empty:
        st.info("No NEC records on file.")
    else:
        df_nec["Status"] = df_nec["is_current"].map({1:"✅ Current", 0:"⚠️ Lapsed — recertification required"})
        for _, row in df_nec.iterrows():
            stat_col = "#088199" if row["is_current"] else "#B30003"
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e0e0e0;border-left:4px solid {stat_col};
                        border-radius:6px;padding:12px 16px;margin-bottom:8px;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div>
                  <span style="background:#003B4F;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:700;">NEC {row['qual_code']}</span>
                  <span style="font-size:14px;font-weight:600;color:#003B4F;margin-left:8px;">{row['qual_title']}</span>
                </div>
                <span style="font-size:12px;font-weight:600;color:{stat_col};">{row['Status']}</span>
              </div>
              <div style="font-size:12px;color:#546E7A;margin-top:6px;">
                Awarded: {str(row['date_earned'])[:10]} &nbsp;|&nbsp;
                Expires: {str(row['currency_expires'])[:10] if row['currency_expires'] else 'Does not expire'}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### 📋 PQS Qualifications")
    if df_pqs.empty:
        st.info("No PQS records on file.")
    else:
        for _, row in df_pqs.iterrows():
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e0e0e0;border-left:4px solid #088199;
                        border-radius:6px;padding:10px 16px;margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
                <span><span style="background:#088199;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;">✅ {row['qual_code']}</span>
                &nbsp;<span style="font-size:13px;color:#003B4F;">{row['qual_title']}</span></span>
                <span style="font-size:12px;color:#546E7A;">Completed: {str(row['date_earned'])[:10]}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### 🏆 Advancement Exam History")
    if df_exam.empty:
        st.info("No exam records on file.")
    else:
        df_exam["Result"] = df_exam["passed"].map({1:"✅ Passed", 0:"❌ Failed"})
        st.dataframe(df_exam[["exam_cycle","target_paygrade","standard_score","Result","exam_date"]].rename(columns={
            "exam_cycle":"Cycle","target_paygrade":"Target PG","standard_score":"Score","exam_date":"Date"
        }), use_container_width=True, hide_index=True)

elif page == "Enterprise Overview":
    page_header("Enterprise Overview",
                "One authoritative view across 7 domains — Personnel, Manpower, Training, Pay, Medical, Education, Recruiting")

    total_sailors  = query("SELECT COUNT(*) as c FROM sailor WHERE status='Active'").iloc[0]["c"]
    total_billets  = query("SELECT COUNT(*) as c FROM billet WHERE billet_id NOT LIKE 'BIN-HIST-%'").iloc[0]["c"]
    filled_billets = query("SELECT SUM(is_filled) as c FROM billet WHERE billet_id NOT LIKE 'BIN-HIST-%'").iloc[0]["c"]
    total_events   = query("SELECT COUNT(*) as c FROM personnel_event").iloc[0]["c"]
    eaos_12mo      = query("SELECT COUNT(*) as c FROM sailor WHERE status='Active' AND julianday(eaos)-julianday('now') BETWEEN 0 AND 365").iloc[0]["c"]
    non_deployable = query("SELECT COUNT(*) as c FROM medical_status WHERE is_deployable=0").iloc[0]["c"]

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Active Sailors",    f"{total_sailors:,}")
    c2.metric("Total Billets",     f"{total_billets:,}")
    c3.metric("Billet Fill Rate",  f"{filled_billets/total_billets*100:.1f}%")
    c4.metric("Personnel Events",  f"{total_events:,}")
    c5.metric("EAOS within 12 mo", f"{eaos_12mo:,}")
    c6.metric("Non-Deployable",    f"{non_deployable:,}", delta_color="inverse")
    st.divider()

    section("Force Composition")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Paygrade Distribution")
        st.bar_chart(query("SELECT paygrade, COUNT(*) AS sailors FROM sailor WHERE status='Active' GROUP BY paygrade ORDER BY paygrade").set_index("paygrade"), color="#088199")
    with col_r:
        st.subheader("Sailors by Community")
        st.bar_chart(query("SELECT r.community, COUNT(*) AS sailors FROM sailor s JOIN rate r ON s.rate_code=r.rate_code WHERE s.status='Active' GROUP BY r.community ORDER BY sailors DESC").set_index("community"), color="#003B4F")

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Fleet Distribution")
        st.bar_chart(query("SELECT c.fleet, COUNT(*) AS sailors FROM sailor s JOIN command c ON s.current_command_id=c.command_id WHERE s.status='Active' AND c.fleet IS NOT NULL GROUP BY c.fleet ORDER BY sailors DESC").set_index("fleet"), color="#E8B00F")
    with col_r:
        st.subheader("Sea / Shore Balance")
        st.bar_chart(query("SELECT c.command_type AS type, COUNT(*) AS sailors FROM sailor s JOIN command c ON s.current_command_id=c.command_id WHERE s.status='Active' GROUP BY c.command_type ORDER BY sailors DESC").set_index("type"), color="#088199")

    section("Geographic Distribution")
    region_df = query("""SELECT c.region, COUNT(*) AS sailors,
        SUM(CASE WHEN c.command_type='Sea' THEN 1 ELSE 0 END) AS sea,
        SUM(CASE WHEN c.command_type='Shore' THEN 1 ELSE 0 END) AS shore,
        SUM(CASE WHEN c.command_type='Overseas' THEN 1 ELSE 0 END) AS overseas
        FROM sailor s JOIN command c ON s.current_command_id=c.command_id
        WHERE s.status='Active' AND c.region IS NOT NULL
        GROUP BY c.region ORDER BY sailors DESC""")
    st.dataframe(region_df.rename(columns={"region":"Region","sailors":"Total","sea":"Sea Duty","shore":"Shore Duty","overseas":"Overseas"}), use_container_width=True, hide_index=True)

    section("EAOS Horizon — Quarterly View, Next 24 Months")
    eaos_df = query("""SELECT CAST(strftime('%Y',eaos) AS TEXT)||'-Q'||CAST(((CAST(strftime('%m',eaos) AS INTEGER)-1)/3)+1 AS TEXT) AS quarter,
        COUNT(*) AS sailors FROM sailor WHERE status='Active' AND julianday(eaos)-julianday('now') BETWEEN 0 AND 730
        GROUP BY quarter ORDER BY quarter""")
    if not eaos_df.empty:
        st.bar_chart(eaos_df.set_index("quarter"), color="#B30003")
        st.caption("Sailors reaching EAOS each quarter over the next 24 months.")

    st.divider()
    section("Domain Coverage")
    coverage = pd.DataFrame([
        {"Domain":"Personnel",         "Records":query("SELECT COUNT(*) c FROM sailor").iloc[0]["c"],            "Source":"NSIPS"},
        {"Domain":"Manpower (billets)","Records":query("SELECT COUNT(*) c FROM billet").iloc[0]["c"],           "Source":"TFMMS"},
        {"Domain":"Assignments",       "Records":query("SELECT COUNT(*) c FROM assignment").iloc[0]["c"],        "Source":"NSIPS / MAPP"},
        {"Domain":"Training / NECs",   "Records":query("SELECT COUNT(*) c FROM qualification").iloc[0]["c"],     "Source":"NTMPS / FLTMPS"},
        {"Domain":"FITREPs",           "Records":query("SELECT COUNT(*) c FROM fitrep").iloc[0]["c"],            "Source":"NSIPS BUPERS Online"},
        {"Domain":"Pay",               "Records":query("SELECT COUNT(*) c FROM pay_record").iloc[0]["c"],        "Source":"DJMS / DFAS"},
        {"Domain":"Medical Readiness", "Records":query("SELECT COUNT(*) c FROM medical_status").iloc[0]["c"],    "Source":"MRRS / BUMED"},
        {"Domain":"Education",         "Records":query("SELECT COUNT(*) c FROM education_record").iloc[0]["c"],  "Source":"Navy College"},
        {"Domain":"Recruiting",        "Records":query("SELECT COUNT(*) c FROM accession").iloc[0]["c"],         "Source":"CIRIMS / PRIDE"},
        {"Domain":"Personnel Events",  "Records":query("SELECT COUNT(*) c FROM personnel_event").iloc[0]["c"],   "Source":"Cross-cutting event spine"},
    ])
    st.dataframe(coverage, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE: RETENTION RISK
# =============================================================================
elif page == "Retention Risk":
    page_header("Retention Risk", "Identify Sailors at risk of separation — scored across Compensation, Stagnation, Quality of Life, and Engagement")
    raw  = query(RETENTION_RISK_SQL)
    risk = compute_retention_risk(raw)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("High Risk",               f"{(risk['risk_tier']=='High').sum():,}")
    c2.metric("Medium Risk",             f"{(risk['risk_tier']=='Medium').sum():,}")
    c3.metric("Critical-Rate at Risk",   f"{risk['is_critical_retention'].sum():,}")
    c4.metric("EAOS Window (<=18 mo)",   f"{(risk['months_to_eaos'].between(0,18)).sum():,}")
    st.divider()
    section("Filters")
    cf1,cf2,cf3,cf4 = st.columns(4)
    tier_f  = cf1.multiselect("Risk tier", ["High","Medium","Low","Minimal"], default=["High","Medium"])
    comm_f  = cf2.multiselect("Community", sorted(risk["community"].dropna().unique()), default=[])
    reg_f   = cf3.multiselect("Region",    sorted(risk["region"].dropna().unique()),    default=[])
    crit_f  = cf4.checkbox("Critical-rate only")
    filtered = risk[risk["risk_tier"].isin(tier_f)]
    if comm_f: filtered = filtered[filtered["community"].isin(comm_f)]
    if reg_f:  filtered = filtered[filtered["region"].isin(reg_f)]
    if crit_f: filtered = filtered[filtered["rate_is_critical"]==1]

    section(f"Risk Drivers — {len(filtered):,} Sailors")
    cl, cr = st.columns(2)
    cl.subheader("Primary Risk Driver")
    cl.bar_chart(filtered["primary_driver"].value_counts(), color="#B30003")
    cr.subheader("Recommended Actions")
    cr.bar_chart(filtered["recommended_action"].value_counts(), color="#E8B00F")

    section("Risk Score Distribution")
    bins = pd.cut(filtered["total_risk"], bins=[0,10,20,30,40,50,60,70,80,100],
        labels=["0-10","11-20","21-30","31-40","41-50","51-60","61-70","71-80","81-100"])
    hist_df = bins.value_counts().sort_index().reset_index(); hist_df.columns=["Score Band","Sailors"]
    st.bar_chart(hist_df.set_index("Score Band"), color="#003B4F")

    section("Risk by Community")
    comm_risk = (filtered.groupby("community").agg(
        Total=("dod_id","count"), High=("risk_tier",lambda x:(x=="High").sum()),
        Medium=("risk_tier",lambda x:(x=="Medium").sum()), Avg_Score=("total_risk","mean"),
        Critical=("is_critical_retention","sum")).sort_values("High",ascending=False).reset_index())
    comm_risk["Avg Score"] = comm_risk["Avg_Score"].round(1)
    st.dataframe(comm_risk.drop(columns=["Avg_Score"]).rename(columns={"community":"Community"}), use_container_width=True, hide_index=True)

    section("Sailor Detail — Top 200 by Risk Score")
    disp = filtered.sort_values("total_risk",ascending=False).head(200)[[
        "dod_id","paygrade","rate_code","community","region","command_name",
        "months_to_eaos","total_risk","risk_tier","primary_driver",
        "risk_compensation","risk_stagnation","risk_qol","risk_engagement",
        "srb_zone","recommended_action"
    ]].rename(columns={"dod_id":"DoD ID","paygrade":"PG","rate_code":"Rate","community":"Community",
        "region":"Region","command_name":"Command","months_to_eaos":"Mo to EAOS",
        "total_risk":"Risk Score","risk_tier":"Tier","primary_driver":"Primary Driver",
        "risk_compensation":"Comp","risk_stagnation":"Stag","risk_qol":"QoL",
        "risk_engagement":"Eng","srb_zone":"SRB Zone","recommended_action":"Recommended Action"})
    st.dataframe(disp, use_container_width=True, hide_index=True)
    csv_buf = io.StringIO(); disp.to_csv(csv_buf, index=False)
    st.download_button("⬇️  Export to CSV", data=csv_buf.getvalue(), file_name="retention_risk.csv", mime="text/csv")


# =============================================================================
# PAGE: PROMOTION READINESS
# =============================================================================
elif page == "Promotion Readiness":
    page_header("Promotion Readiness", "Identify advancement-ready Sailors and close gaps for those who aren't")
    raw  = query(PROMOTION_SQL)
    prom = compute_promotion_readiness(raw)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Highly Competitive",f"{(prom['readiness_tier']=='Highly Competitive').sum():,}")
    c2.metric("Competitive",       f"{(prom['readiness_tier']=='Competitive').sum():,}")
    c3.metric("Approaching",       f"{(prom['readiness_tier']=='Approaching').sum():,}")
    c4.metric("Needs Development", f"{(prom['readiness_tier']=='Needs Development').sum():,}")
    st.divider()
    section("Filters")
    cf1, cf2 = st.columns(2)
    tgt_pg  = cf1.selectbox("Target paygrade", ["All","E4","E5","E6","E7","E8"])
    comm_f  = cf2.multiselect("Community", sorted(prom["community"].dropna().unique()), default=[])
    filtered = prom.copy()
    if tgt_pg != "All": filtered = filtered[filtered["next_paygrade"]==tgt_pg]
    if comm_f: filtered = filtered[filtered["community"].isin(comm_f)]

    tier_order  = ["Highly Competitive","Competitive","Approaching","Needs Development"]
    tier_counts = filtered["readiness_tier"].value_counts().reindex(tier_order, fill_value=0)
    section(f"Readiness Distribution — {len(filtered):,} Sailors")
    st.bar_chart(tier_counts, color="#003B4F")

    tab_cand, tab_gaps, tab_bench, tab_cohort = st.tabs(["Top Candidates","Closeable Gaps","Peer Benchmarking","Cohort Comparison"])

    with tab_cand:
        disp = filtered[filtered["readiness_score"]>=80].sort_values("readiness_score",ascending=False).head(100)[[
            "dod_id","paygrade","next_paygrade","rate_code","community","command_name","readiness_score","career_trait_avg","best_recent_score"
        ]].rename(columns={"dod_id":"DoD ID","paygrade":"PG","next_paygrade":"->","rate_code":"Rate","community":"Community",
            "command_name":"Command","readiness_score":"Score","career_trait_avg":"FITREP Avg","best_recent_score":"Best Exam"})
        st.dataframe(disp, use_container_width=True, hide_index=True)

    with tab_gaps:
        closeable = filtered[(filtered["readiness_score"]>=50)&(filtered["readiness_score"]<80)].sort_values("readiness_score",ascending=False).head(100).copy()
        closeable["gaps_text"] = closeable["gaps"].apply(lambda l: " | ".join(l))
        disp = closeable[["dod_id","paygrade","next_paygrade","rate_code","command_name","readiness_score","gap_count","gaps_text"]].rename(
            columns={"dod_id":"DoD ID","paygrade":"PG","next_paygrade":"->","rate_code":"Rate","command_name":"Command",
                     "readiness_score":"Score","gap_count":"# Gaps","gaps_text":"Gaps to Close"})
        st.dataframe(disp, use_container_width=True, hide_index=True)
        all_gaps = [g for lst in closeable["gaps"] for g in lst]
        st.bar_chart(pd.Series(all_gaps).value_counts().head(8), color="#E8B00F")
        st.caption("Most common gaps among 'within-reach' Sailors.")

    with tab_bench:
        bench = (filtered.groupby("community").agg(
            Sailors=("dod_id","count"), Avg_Score=("readiness_score","mean"),
            Highly_Comp=("readiness_tier",lambda x:(x=="Highly Competitive").sum()),
            Needs_Dev=("readiness_tier",lambda x:(x=="Needs Development").sum()),
            Avg_FITREP=("career_trait_avg","mean"), Avg_Exam=("best_recent_score","mean"))
            .sort_values("Avg_Score",ascending=False).reset_index())
        for c in ["Avg_Score","Avg_FITREP","Avg_Exam"]: bench[c] = bench[c].round(1)
        bench["% Highly Comp"] = (bench["Highly_Comp"]/bench["Sailors"]*100).round(1)
        st.dataframe(bench.rename(columns={"community":"Community","Avg_Score":"Avg Readiness","Highly_Comp":"Highly Comp","Needs_Dev":"Needs Dev","Avg_FITREP":"Avg FITREP","Avg_Exam":"Avg Exam Score"}), use_container_width=True, hide_index=True)

    with tab_cohort:
        cohort = (filtered.groupby(["paygrade","readiness_tier"])["dod_id"].count().reset_index()
            .rename(columns={"dod_id":"count","paygrade":"Paygrade","readiness_tier":"Tier"}))
        pivot = cohort.pivot(index="Paygrade",columns="Tier",values="count").fillna(0)
        for c in tier_order:
            if c not in pivot.columns: pivot[c] = 0
        st.bar_chart(pivot[tier_order].loc[sorted(pivot.index)], color=["#003B4F","#088199","#E8B00F","#B30003"])


# ── DETAILING / BILLET MATCH ─────────────────────────────────────────────────
elif page == "Detailing / Billet Match":
    page_header("Detailing / Billet Match",
                "NEC-to-billet alignment and sea/shore rotation readiness — sourced from TFMMS")

    billets = query(BILLET_MATCH_SQL)
    pool    = query(SAILOR_POOL_SQL)

    if billets.empty or pool.empty:
        st.warning("No billet or sailor data available.")
    else:
        open_billets   = len(billets)
        critical       = int(billets["billet_is_critical"].sum())
        sea_open       = int((billets["sea_shore"] == "Sea").sum())
        communities    = billets["rate_community"].nunique()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Open Billets",       f"{open_billets:,}")
        c2.metric("Critical Billets",   f"{critical:,}")
        c3.metric("Sea Duty Billets",   f"{sea_open:,}")
        c4.metric("Communities",        f"{communities:,}")
        st.divider()

        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            comm_opts = ["All"] + sorted(billets["rate_community"].dropna().unique().tolist())
            comm_sel  = st.selectbox("Community", comm_opts, key="bdet_comm")
        with fc2:
            pg_opts = ["All"] + sorted(billets["paygrade_required"].dropna().unique().tolist())
            pg_sel  = st.selectbox("Paygrade Required", pg_opts, key="bdet_pg")
        with fc3:
            ss_opts = ["All", "Sea", "Shore"]
            ss_sel  = st.selectbox("Sea / Shore", ss_opts, key="bdet_ss")

        fb = billets.copy()
        if comm_sel != "All": fb = fb[fb["rate_community"] == comm_sel]
        if pg_sel   != "All": fb = fb[fb["paygrade_required"] == pg_sel]
        if ss_sel   != "All": fb = fb[fb["sea_shore"] == ss_sel]
        st.markdown(f"**{len(fb):,} open billets** match filters")

        tab_dist, tab_match, tab_table = st.tabs(["📊 Distribution", "🔵 Top Billet Matches", "📋 Billet Table"])

        with tab_dist:
            c_l, c_r = st.columns(2)
            with c_l:
                cdf = fb["rate_community"].value_counts().reset_index()
                cdf.columns = ["Community", "Count"]
                fig = px.pie(cdf, names="Community", values="Count", hole=0.4,
                             title="Open Billets by Community")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
                st.plotly_chart(fig, use_container_width=True)
            with c_r:
                ssdf = fb["sea_shore"].value_counts().reset_index()
                ssdf.columns = ["Type", "Count"]
                fig2 = px.bar(ssdf, x="Type", y="Count", color="Type",
                              color_discrete_sequence=["#088199","#003B4F"],
                              title="Sea vs. Shore Open Billets")
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            region_counts = fb["region"].value_counts().reset_index()
            region_counts.columns = ["Region", "Open Billets"]
            fig3 = px.bar(region_counts, x="Region", y="Open Billets",
                          color="Open Billets", color_continuous_scale=[[0,"#EEF2F4"],[1,"#003B4F"]],
                          title="Open Billets by Region")
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C", coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)

        with tab_match:
            st.markdown("Select a billet to find top-matched sailors from the active pool:")
            billet_options = fb.apply(
                lambda r: f"{r['billet_id']} — {r['rate_name']} {r['paygrade_required']} @ {r['command_name']} ({r['sea_shore']})",
                axis=1
            ).tolist()
            if not billet_options:
                st.info("No billets match current filters.")
            else:
                selected_label = st.selectbox("Choose billet", billet_options, key="bdet_sel")
                sel_idx = billet_options.index(selected_label)
                billet  = fb.iloc[sel_idx]
                matches = compute_billet_match(pool, billet)
                if matches.empty:
                    st.warning("No eligible sailors found for this billet (rate/paygrade).")
                else:
                    top = matches.head(10).reset_index(drop=True)
                    st.markdown(f"**Top {len(top)} matches for {billet['rate_name']} {billet['paygrade_required']} — {billet['command_name']}:**")
                    disp = top[["dod_id","paygrade","rate_code","community","match_score","match_tier",
                                "match_nec","match_rotation","match_dwell","match_deployable","command_type","months_to_eaos"]]
                    st.dataframe(disp.rename(columns={
                        "dod_id":"DoD ID","paygrade":"Grade","rate_code":"Rate",
                        "community":"Community","match_score":"Score","match_tier":"Tier",
                        "match_nec":"NEC Pts","match_rotation":"Rotation Pts",
                        "match_dwell":"Dwell Pts","match_deployable":"Deploy Pts",
                        "command_type":"Cur Duty","months_to_eaos":"Mo to EAOS"
                    }), use_container_width=True, hide_index=True)

        with tab_table:
            show_cols = ["billet_id","command_name","rate_name","paygrade_required",
                         "nec_required_title","sea_shore","region","billet_is_critical"]
            st.dataframe(
                fb[show_cols].rename(columns={
                    "billet_id":"Billet ID","command_name":"Command","rate_name":"Rate",
                    "paygrade_required":"Grade Req","nec_required_title":"NEC Required",
                    "sea_shore":"Sea/Shore","region":"Region","billet_is_critical":"Critical"
                }).head(200),
                use_container_width=True, hide_index=True
            )

# ── SAILOR PROFILE ────────────────────────────────────────────────────────────
elif page == "Sailor Profile":
    page_header("Sailor Profile",
                "Individual sailor digital twin — complete data across all authoritative source systems")

    # ── Search controls ─────────────────────────────────────────────────────────
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        search_val = st.text_input("Search by DoD ID, rate code, or paygrade",
                                   placeholder="e.g., 9990000123 or BM or E5",
                                   label_visibility="collapsed")
    with sc2:
        if st.button("🎲 Random Sailor", key="prof_rand"):
            r = query("SELECT dod_id FROM sailor WHERE status='Active' ORDER BY RANDOM() LIMIT 1")
            if not r.empty:
                st.session_state["profile_dod"] = r.iloc[0]["dod_id"]

    if search_val:
        results = query(
            "SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name FROM sailor s JOIN rate r ON s.rate_code=r.rate_code "
            "WHERE s.status='Active' AND (s.dod_id LIKE ? OR s.rate_code LIKE ? OR s.paygrade LIKE ?) LIMIT 20",
            (f"%{search_val}%", f"%{search_val}%", f"%{search_val}%"),
        )
        if results.empty:
            st.warning("No sailors matched your search.")
        elif len(results) == 1:
            st.session_state["profile_dod"] = results.iloc[0]["dod_id"]
        else:
            chosen = st.selectbox(
                f"{len(results)} results — select a sailor:",
                results["dod_id"].tolist(),
                format_func=lambda d: f"{d} — {results[results['dod_id']==d]['paygrade'].iloc[0]} {results[results['dod_id']==d]['rate_code'].iloc[0]}"
            )
            st.session_state["profile_dod"] = chosen

    dod_id = st.session_state.get("profile_dod")
    if not dod_id:
        st.info("Enter a DoD ID, rate code, or paygrade — or click **Random Sailor** to load a profile.")
        st.stop()

    sailor_df = query("SELECT * FROM v_active_sailor WHERE dod_id=?", (dod_id,))
    if sailor_df.empty:
        st.error("Sailor not found in the active duty roster.")
        st.stop()
    s = sailor_df.iloc[0]

    # ── Compute scores ──────────────────────────────────────────────────────────
    ri_score, ri_label, ri_color, ri_breakdown = compute_readiness_indicator(dod_id)
    lc_idx, lc_sub   = derive_lifecycle_stage(s)
    snapshot_rows     = get_dt_snapshot(dod_id, s)
    ai_actions        = generate_ai_actions(dod_id, s)

    yos       = float(s.get("years_of_service", 0) or 0)
    mos_eaos  = int(s.get("months_to_eaos", 99) or 99)

    # ── Hero card ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sailor-card">
      <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
        <div style="width:68px;height:68px;border-radius:50%;background:#003B4F;
                    display:flex;align-items:center;justify-content:center;
                    font-size:26px;color:#fff;font-weight:700;flex-shrink:0;">
          {s['rate_code'][:2].upper()}
        </div>
        <div style="flex:1;min-width:200px;">
          <div style="font-size:21px;font-weight:700;color:#003B4F;">
            {s['paygrade']} {s['rate_code']} — {s['rate_name']}
          </div>
          <div style="font-size:13px;color:#546E7A;margin-top:4px;">
            DoD ID: {dod_id} &nbsp;|&nbsp; {s.get('community','—')} Community
            &nbsp;|&nbsp; YOS: {yos:.1f} &nbsp;|&nbsp; EAOS in {mos_eaos} mo
          </div>
          <div style="font-size:13px;color:#546E7A;margin-top:2px;">
            Command: {s.get('command_name','—')} &nbsp;|&nbsp; {s.get('command_type','—')} Duty
            &nbsp;|&nbsp; {s.get('region','—')} &nbsp;|&nbsp; Fleet: {s.get('fleet','—')}
          </div>
        </div>
        <div style="text-align:center;flex-shrink:0;">
          <div class="readiness-pct" style="color:{ri_color};">{ri_score}%</div>
          <div style="font-size:11px;font-weight:600;color:{ri_color};text-transform:uppercase;">{ri_label}</div>
          <div style="font-size:10px;color:#888;margin-top:2px;">Mission Readiness</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Lifecycle timeline ──────────────────────────────────────────────────────
    st.markdown(render_lifecycle_html(lc_idx, lc_sub), unsafe_allow_html=True)

    # ── Digital Twin Snapshot ───────────────────────────────────────────────────
    section("Digital Twin Snapshot")
    st.markdown(render_dt_snapshot(snapshot_rows), unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────────────────────
    tab_pers, tab_career, tab_pay, tab_train, tab_medical, tab_prov, tab_ai = st.tabs([
        "👤 Personnel", "📈 Career", "💰 Pay & Entitlements",
        "🎓 Training", "🏥 Medical", "🗂 Provenance", "🤖 AI Actions"
    ])

    # ── PERSONNEL TAB ─────────────────────────────────────────────────────────
    with tab_pers:
        p1, p2 = st.columns(2)
        with p1:
            st.markdown(f"**DoD ID:** {dod_id}")
            st.markdown(f"**Paygrade:** {s.get('paygrade','—')}")
            st.markdown(f"**Rate Code:** {s.get('rate_code','—')}")
            st.markdown(f"**Rate Name:** {s.get('rate_name','—')}")
            st.markdown(f"**Community:** {s.get('community','—')}")
            st.markdown(f"**Gender:** {s.get('gender','—')}")
        with p2:
            st.markdown(f"**Years of Service:** {yos:.1f}")
            st.markdown(f"**Time in Rate (mo):** {int(s.get('time_in_rate_months',0))}")
            st.markdown(f"**Age:** {int(s.get('age',0))}")
            st.markdown(f"**Marital Status:** {s.get('marital_status','—')}")
            st.markdown(f"**Dependents:** {int(s.get('num_dependents',0))}")
            st.markdown(f"**EFM Enrolled:** {'Yes' if s.get('has_efm') else 'No'}")
        st.divider()
        p3, p4 = st.columns(2)
        with p3:
            st.markdown(f"**Command:** {s.get('command_name','—')}")
            st.markdown(f"**Command Type:** {s.get('command_type','—')}")
            st.markdown(f"**Region:** {s.get('region','—')}")
        with p4:
            st.markdown(f"**Fleet:** {s.get('fleet','—')}")
            st.markdown(f"**EAOS:** {str(s.get('eaos','—'))[:10]}")
            st.markdown(f"**Months to EAOS:** {mos_eaos}")

    # ── CAREER TAB ────────────────────────────────────────────────────────────
    with tab_career:
        risk_raw = query(RETENTION_RISK_SQL)
        prom_raw = query(PROMOTION_SQL)
        risk_df  = compute_retention_risk(risk_raw)
        prom_df  = compute_promotion_readiness(prom_raw)

        r_row = risk_df[risk_df["dod_id"] == dod_id]
        p_row = prom_df[prom_df["dod_id"] == dod_id]

        cc1, cc2 = st.columns(2)
        with cc1:
            if not r_row.empty:
                r = r_row.iloc[0]
                risk_score = int(r["total_risk"])
                risk_tier  = r["risk_tier"]
                risk_col   = "#B30003" if risk_tier == "High" else ("#E8B00F" if risk_tier == "Medium" else "#088199")
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:12px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="metric-label">Retention Risk Score</span>
                    <span style="font-size:22px;font-weight:700;color:{risk_col};">{risk_score}</span>
                  </div>
                  <div style="font-size:12px;color:{risk_col};font-weight:600;margin-top:4px;">{risk_tier}</div>
                  <div style="background:#eee;border-radius:4px;height:6px;margin-top:8px;">
                    <div style="background:{risk_col};width:{min(risk_score,100)}%;height:6px;border-radius:4px;"></div>
                  </div>
                  <div style="font-size:12px;color:#546E7A;margin-top:6px;">Driver: {r['primary_driver']}</div>
                  <div style="font-size:12px;color:#546E7A;">Action: {r['recommended_action']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No retention risk data.")

            if not p_row.empty:
                p = p_row.iloc[0]
                pro_score = int(p["readiness_score"])
                pro_tier  = p["readiness_tier"]
                pro_col   = "#088199" if pro_tier == "Highly Competitive" else ("#003B4F" if pro_tier == "Competitive" else ("#E8B00F" if pro_tier == "Approaching" else "#B30003"))
                gaps_str  = " | ".join(p["gaps"][:2])
                st.markdown(f"""
                <div class="metric-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="metric-label">Promotion Readiness</span>
                    <span style="font-size:22px;font-weight:700;color:{pro_col};">{pro_score}</span>
                  </div>
                  <div style="font-size:12px;color:{pro_col};font-weight:600;margin-top:4px;">{pro_tier} → {p['next_paygrade']}</div>
                  <div style="background:#eee;border-radius:4px;height:6px;margin-top:8px;">
                    <div style="background:{pro_col};width:{pro_score}%;height:6px;border-radius:4px;"></div>
                  </div>
                  <div style="font-size:12px;color:#546E7A;margin-top:6px;">{gaps_str}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Sailor not in promotion-eligible paygrade.")

        with cc2:
            section("Readiness Breakdown")
            for domain, pts in ri_breakdown.items():
                pct = pts / 25 * 100
                bar_col = "#088199" if pct >= 80 else ("#E8B00F" if pct >= 50 else "#B30003")
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                  <div style="display:flex;justify-content:space-between;font-size:13px;">
                    <span>{domain}</span><span style="color:{bar_col};font-weight:600;">{pts}/25</span>
                  </div>
                  <div style="background:#eee;border-radius:4px;height:8px;margin-top:4px;">
                    <div style="background:{bar_col};width:{pct:.0f}%;height:8px;border-radius:4px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── PAY & ENTITLEMENTS TAB ───────────────────────────────────────────────
    with tab_pay:
        pay_rec = query("SELECT * FROM pay_record WHERE dod_id=?", (dod_id,))
        if pay_rec.empty:
            st.warning("No pay record found for this sailor.")
        else:
            p = pay_rec.iloc[0]
            base   = float(p["base_pay_monthly"]   or 0)
            bah    = float(p["bah_monthly"]         or 0)
            bas    = float(p["bas_monthly"]         or 0)
            sea    = float(p["sea_pay_monthly"]     or 0)
            spec   = float(p["special_pay_monthly"] or 0)
            total  = base + bah + bas + sea + spec
            srb_z  = p["srb_zone"]
            srb_m  = float(p["srb_multiplier"] or 0)
            srb_u  = str(p["srb_eligible_until"] or "—")[:10]

            st.markdown("#### 💵 Monthly Pay Entitlements")
            entitlements = [
                ("Basic Pay",       f"${base:,.0f}",  "#003B4F", "NSIPS/DJMS", "Taxable"),
                ("BAH",             f"${bah:,.0f}",   "#003B4F", "NSIPS/DJMS", "Non-Taxable"),
                ("BAS",             f"${bas:,.0f}",   "#003B4F", "NSIPS/DJMS", "Non-Taxable"),
                ("Sea Pay",         f"${sea:,.0f}",   "#088199" if sea > 0 else "#aaa", "NSIPS", "Taxable"),
                ("Special Pay",     f"${spec:,.0f}",  "#088199" if spec > 0 else "#aaa", "NSIPS", "Taxable"),
            ]
            ent_html = '<div style="border:1px solid #C6CCD0;border-radius:8px;overflow:hidden;margin-bottom:16px;">'
            ent_html += ('<div style="background:#003B4F;color:#fff;padding:10px 16px;font-weight:700;font-size:13px;'
                         'display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:8px;">'
                         '<span>Entitlement</span><span>Amount/Mo</span><span>Source</span><span>Tax Status</span></div>')
            for idx_e, (name, amt, color, src, tax) in enumerate(entitlements):
                bg = "#f9f9f9" if idx_e % 2 == 0 else "#fff"
                ent_html += (f'<div style="background:{bg};padding:9px 16px;font-size:13px;'
                             f'display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:8px;border-top:1px solid #eee;">'
                             f'<span>{name}</span><span style="font-weight:700;color:{color};">{amt}</span>'
                             f'<span style="color:#546E7A;">{src}</span><span style="color:#546E7A;">{tax}</span></div>')
            ent_html += (f'<div style="background:#EEF2F4;padding:10px 16px;font-size:14px;font-weight:700;'
                         f'display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:8px;border-top:2px solid #003B4F;">'
                         f'<span>TOTAL MONTHLY</span><span style="color:#003B4F;">${total:,.0f}</span>'
                         f'<span></span><span></span></div>')
            ent_html += '</div>'
            st.markdown(ent_html, unsafe_allow_html=True)

            st.markdown("#### 📋 Reenlistment & Service Obligations")
            if srb_z:
                st.markdown(f"""
                <div style="background:#E8F8FA;border-left:4px solid #088199;padding:12px 16px;
                            border-radius:4px;margin-bottom:12px;font-size:13px;">
                  ✅ <strong>SRB Eligible — Zone {srb_z}</strong> (x{srb_m:.1f} multiplier)
                  &nbsp;|&nbsp; Eligible until: <strong>{srb_u}</strong><br>
                  Initiate SRB counseling and documentation through NSIPS. Policy: MILPERSMAN 1160-120.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="background:#EEF2F4;border-left:4px solid #C6CCD0;padding:12px 16px;border-radius:4px;font-size:13px;margin-bottom:12px;">No current SRB eligibility on record.</div>', unsafe_allow_html=True)

            if mos_eaos <= 18:
                st.markdown(f"""
                <div class="pay-alert">
                  ⚠️ <strong>PCS/Transition Window:</strong> {mos_eaos} months until EAOS.
                  PCS travel entitlements and separation allowances may apply. Coordinate with detailer NLT 12 months prior.
                  Policy: MILPERSMAN 1300-300.
                </div>
                """, unsafe_allow_html=True)

    # ── TRAINING TAB ─────────────────────────────────────────────────────────
    with tab_train:
        df_nec = query(
            "SELECT qual_code AS nec_code, qual_title, date_earned, currency_expires, is_current "
            "FROM qualification WHERE dod_id=? AND qual_type='NEC' ORDER BY date_earned DESC",
            (dod_id,)
        )
        df_pqs = query(
            "SELECT qual_code, qual_title, date_earned, is_current "
            "FROM qualification WHERE dod_id=? AND qual_type='PQS' ORDER BY date_earned DESC",
            (dod_id,)
        )
        df_exam = query(
            "SELECT exam_cycle, target_paygrade, standard_score, passed, exam_date "
            "FROM advancement_exam WHERE dod_id=? ORDER BY exam_date DESC LIMIT 5",
            (dod_id,)
        )

        st.markdown("**NEC Qualifications**")
        if df_nec.empty:
            st.info("No NEC records found.")
        else:
            df_nec["Status"] = df_nec["is_current"].map({1: "✅ Current", 0: "⚠️ Lapsed"})
            st.dataframe(df_nec[["nec_code","qual_title","date_earned","currency_expires","Status"]].rename(columns={
                "nec_code":"NEC","qual_title":"Title","date_earned":"Awarded","currency_expires":"Expires"
            }), use_container_width=True, hide_index=True)

        st.markdown("**PQS Qualifications**")
        if df_pqs.empty:
            st.info("No PQS records found.")
        else:
            st.dataframe(df_pqs[["qual_code","qual_title","date_earned"]].rename(columns={
                "qual_code":"PQS Code","qual_title":"Title","date_earned":"Completed"
            }), use_container_width=True, hide_index=True)

        st.markdown("**Advancement Exam History**")
        if df_exam.empty:
            st.info("No exam records found.")
        else:
            df_exam["Result"] = df_exam["passed"].map({1:"✅ Passed", 0:"❌ Failed"})
            st.dataframe(df_exam[["exam_cycle","target_paygrade","standard_score","Result","exam_date"]].rename(columns={
                "exam_cycle":"Cycle","target_paygrade":"Target PG",
                "standard_score":"Score","exam_date":"Date"
            }), use_container_width=True, hide_index=True)

    # ── MEDICAL TAB ──────────────────────────────────────────────────────────
    with tab_medical:
        med = query("SELECT * FROM medical_status WHERE dod_id=?", (dod_id,))
        if med.empty:
            st.warning("No medical record found.")
        else:
            m = med.iloc[0]
            dep_stat  = "Deployable" if m["is_deployable"] else "Non-Deployable"
            dep_col   = "#088199" if m["is_deployable"] else "#B30003"
            imm_stat  = "Current" if m["immunizations_current"] else "Action Required"
            imm_col   = "#088199" if m["immunizations_current"] else "#E8B00F"
            dental_cl = int(m["dental_class"] or 0)
            dental_col = "#088199" if dental_cl <= 2 else "#B30003"

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{dep_col};font-size:18px;">{dep_stat}</div><div class="metric-label">Deployable Status</div></div>', unsafe_allow_html=True)
            with mc2:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{imm_col};font-size:18px;">{imm_stat}</div><div class="metric-label">Immunization Status</div></div>', unsafe_allow_html=True)
            with mc3:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{dental_col};">Class {dental_cl}</div><div class="metric-label">Dental Class</div></div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("**Medical Record Detail**")
            details = {
                "PHA Date":              str(m["pha_date"] or "—")[:10],
                "PHA Due Date":          str(m["pha_due_date"] or "—")[:10],
                "Dental Classification": f"Class {dental_cl}",
                "Immunizations Current": "Yes" if m["immunizations_current"] else "No",
                "Deployable":            dep_stat,
                "Deployment Limit Until":str(m["deployment_limit_until"] or "—")[:10],
                "Limit Reason":          m["deployment_limit_reason"] or "—",
                "Last Updated":          str(m["last_updated"] or "—")[:10],
            }
            d1, d2 = st.columns(2)
            items  = list(details.items())
            with d1:
                for k, v in items[:4]:
                    st.markdown(f"**{k}:** {v}")
            with d2:
                for k, v in items[4:]:
                    st.markdown(f"**{k}:** {v}")

    # ── PROVENANCE TAB ────────────────────────────────────────────────────────
    with tab_prov:
        section("Data Lineage & Provenance")
        st.markdown('<p style="color:#546E7A;font-size:13px;margin-bottom:16px;">Authoritative source systems feeding this Digital Twin record — sourced at runtime from connected feeds</p>', unsafe_allow_html=True)
        provenance = [
            ("Personnel / Identity",   "NSIPS",         "PERS-1 (MyNavy HR)", "Daily",              "NPC",              "MILPERSMAN 1000-010", "DoD ID, Paygrade, Rate, Gender, Status"),
            ("Pay & Entitlements",     "NSIPS / DJMS",  "DFAS",               "Real-time",          "DFAS Cleveland",   "DoDFMR Vol 7A",       "Base Pay, BAH, BAS, Sea Pay, SRB Zone"),
            ("Training & NEC",         "NTMPS",         "NETC (N7)",          "Within 30 days",     "NETC",             "NAVEDTRA 10500",      "NEC Codes, PQS, Course Completions"),
            ("Medical / Readiness",    "MRRS / AHLTA",  "BUMED",              "Within 7 days",      "MTF",              "MANMED CH-15",        "PHA, Immunizations, Deployability, Dental"),
            ("Assignments",            "TFMMS",         "PERS-4",             "Daily",              "NPC Detailing",    "MILPERSMAN 1300-300", "UIC, Billet, Orders, EAOS, Sea/Shore"),
            ("Performance (FITREP)",   "NSIPS",         "PERS-32",            "Per reporting period","PERS-32",         "BUPERSINST 1610.10",  "Trait Avg, Promotion Rec, EP %"),
            ("Advancement",            "NSIPS / NEAS",  "PERS-803",           "Per exam cycle",     "NETPDTC",          "MILPERSMAN 1430-010", "Exam Scores, Multiple, PNA Points"),
        ]
        for domain, source, owner, refresh, authority, policy, fields in provenance:
            st.markdown(f"""
            <div class="prov-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
                <div>
                  <span style="font-size:15px;font-weight:700;color:#003B4F;">{domain}</span>
                  <span style="margin-left:10px;background:#003B4F;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">{source}</span>
                </div>
              </div>
              <div class="prov-grid">
                <div><span style="color:#888;font-size:10px;text-transform:uppercase;">Data Owner</span><br><span style="font-size:13px;">{owner}</span></div>
                <div><span style="color:#888;font-size:10px;text-transform:uppercase;">Refresh Rate</span><br><span style="font-size:13px;">{refresh}</span></div>
                <div><span style="color:#888;font-size:10px;text-transform:uppercase;">Validating Authority</span><br><span style="font-size:13px;">{authority}</span></div>
                <div><span style="color:#888;font-size:10px;text-transform:uppercase;">Policy Reference</span><br><span style="font-size:13px;font-family:monospace;">{policy}</span></div>
              </div>
              <div style="margin-top:8px;font-size:12px;color:#546E7A;">📋 Fields: {fields}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── AI ACTIONS TAB ────────────────────────────────────────────────────────
    with tab_ai:
        section("AI-Assisted Next Best Actions")
        st.markdown('<p style="color:#546E7A;font-size:13px;">Rule-based recommendations from digital twin data. Not a substitute for official guidance or command authority.</p>', unsafe_allow_html=True)

        for act in ai_actions:
            conf_cls   = act.get("conf_cls", "ai-conf-med")
            conf_label = act.get("confidence", "Medium")
            st.markdown(render_ai_card(act, 0), unsafe_allow_html=True)

        st.divider()
        st.markdown("""
        <div style="background:#EEF2F4;padding:12px 16px;border-radius:6px;font-size:12px;color:#546E7A;">
          <strong>Disclaimer:</strong> Recommendations are generated by rule-based logic using MyNavy HR source data.
          They are for informational purposes only and do not constitute official Navy orders, guidance, or policy interpretation.
          All actions requiring documentation must be initiated through proper channels with appropriate command authorization.
        </div>
        """, unsafe_allow_html=True)


# ── ANALYTICS & TRENDS ────────────────────────────────────────────────────────
elif page == "Analytics & Trends":
    page_header("Analytics & Trends",
                "Enterprise workforce analytics across the sailor lifecycle — sourced from 7 authoritative systems")


    tab_ret, tab_pro, tab_force, tab_eaos = st.tabs([
        "📉 Retention Trends", "📈 Promotion Pipeline", "🪖 Force Composition", "📅 EAOS Outlook"
    ])

    with tab_ret:
        section("Retention Risk Distribution by Community")
        df_r = query(RETENTION_RISK_SQL)
        df_r = compute_retention_risk(df_r)

        risk_comm = (df_r.groupby(["community","risk_tier"])["dod_id"]
                     .count().reset_index().rename(columns={"dod_id":"sailors","community":"Community","risk_tier":"Risk Tier"}))
        tier_order = ["High","Medium","Low","Minimal"]
        fig = px.bar(risk_comm, x="Community", y="sailors", color="Risk Tier",
                     barmode="stack",
                     color_discrete_map={"High":"#B30003","Medium":"#E8B00F","Low":"#088199","Minimal":"#C6CCD0"},
                     category_orders={"Risk Tier": tier_order},
                     title="Retention Risk Tiers by Community")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
        st.plotly_chart(fig, use_container_width=True)

        section("SRB Eligibility vs. EAOS Proximity")
        srb_df = query("""
            SELECT s.paygrade, r.community,
                   AVG(CASE WHEN julianday(s.eaos)-julianday('now') BETWEEN 0 AND 540 THEN 1.0 ELSE 0.0 END)*100 AS pct_near_eaos,
                   AVG(CASE WHEN pr.srb_zone IS NOT NULL THEN 1.0 ELSE 0.0 END)*100 AS pct_srb,
                   COUNT(*) AS sailors
            FROM sailor s
            JOIN rate r ON s.rate_code=r.rate_code
            LEFT JOIN pay_record pr ON s.dod_id=pr.dod_id
            WHERE s.status='Active'
            GROUP BY s.paygrade, r.community
        """)
        if not srb_df.empty:
            fig2 = px.scatter(srb_df, x="pct_near_eaos", y="pct_srb",
                              size="sailors", color="community",
                              labels={"pct_near_eaos":"% Near EAOS (0-18 mo)","pct_srb":"% SRB Eligible","community":"Community"},
                              title="SRB Eligibility vs. EAOS Proximity by Community",
                              hover_data=["paygrade","sailors"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
            st.plotly_chart(fig2, use_container_width=True)

        section("Primary Retention Risk Drivers")
        driver_counts = df_r["primary_driver"].value_counts().reset_index()
        driver_counts.columns = ["Driver", "Count"]
        fig3 = px.bar(driver_counts, x="Driver", y="Count",
                      color="Count", color_continuous_scale=[[0,"#EEF2F4"],[1,"#B30003"]],
                      title="Most Common Retention Risk Drivers Across Force")
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C", coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with tab_pro:
        section("Promotion Readiness by Paygrade")
        df_p = query(PROMOTION_SQL)
        df_p = compute_promotion_readiness(df_p)

        tier_order = ["Highly Competitive","Competitive","Approaching","Needs Development"]
        promo_pg = (df_p.groupby(["paygrade","readiness_tier"])["dod_id"]
                    .count().reset_index().rename(columns={"dod_id":"sailors","paygrade":"Paygrade","readiness_tier":"Tier"}))
        fig = px.bar(promo_pg, x="Paygrade", y="sailors", color="Tier", barmode="stack",
                     color_discrete_map={"Highly Competitive":"#088199","Competitive":"#003B4F",
                                         "Approaching":"#E8B00F","Needs Development":"#B30003"},
                     category_orders={"Tier": tier_order},
                     title="Promotion Readiness Tiers by Paygrade")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
        st.plotly_chart(fig, use_container_width=True)

        section("FITREP vs. Exam Score Correlation")
        fig2 = px.scatter(df_p.dropna(subset=["career_trait_avg","best_recent_score"]),
                          x="best_recent_score", y="career_trait_avg", color="readiness_tier",
                          color_discrete_map={"Highly Competitive":"#088199","Competitive":"#003B4F",
                                              "Approaching":"#E8B00F","Needs Development":"#B30003"},
                          labels={"best_recent_score":"Best Exam Score","career_trait_avg":"Career FITREP Avg","readiness_tier":"Tier"},
                          title="Exam Score vs. FITREP — Promotion Readiness Correlation",
                          opacity=0.6)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
        st.plotly_chart(fig2, use_container_width=True)

        section("Community Benchmarking")
        bench = (df_p.groupby("community").agg(
            Sailors=("dod_id","count"),
            Avg_Score=("readiness_score","mean"),
            Highly_Comp=("readiness_tier", lambda x: (x=="Highly Competitive").sum()),
            Avg_FITREP=("career_trait_avg","mean"),
            Avg_Exam=("best_recent_score","mean")
        ).sort_values("Avg_Score", ascending=False).reset_index())
        for c in ["Avg_Score","Avg_FITREP","Avg_Exam"]:
            bench[c] = bench[c].round(1)
        bench["% Highly Comp"] = (bench["Highly_Comp"]/bench["Sailors"]*100).round(1)
        st.dataframe(bench.rename(columns={"community":"Community","Avg_Score":"Avg Readiness",
                                           "Highly_Comp":"Highly Comp","Avg_FITREP":"Avg FITREP","Avg_Exam":"Avg Exam"}),
                     use_container_width=True, hide_index=True)

    with tab_force:
        section("Force Composition")
        c_l, c_r = st.columns(2)
        with c_l:
            pg_df = query("SELECT paygrade, COUNT(*) AS sailors FROM sailor WHERE status='Active' GROUP BY paygrade ORDER BY paygrade")
            fig = px.bar(pg_df, x="paygrade", y="sailors",
                         color="sailors", color_continuous_scale=[[0,"#EEF2F4"],[1,"#003B4F"]],
                         title="Active Sailors by Paygrade", labels={"paygrade":"Paygrade","sailors":"Sailors"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C", coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        with c_r:
            comm_df = query("SELECT r.community, COUNT(*) AS sailors FROM sailor s JOIN rate r ON s.rate_code=r.rate_code WHERE s.status='Active' GROUP BY r.community ORDER BY sailors DESC")
            fig2 = px.pie(comm_df, names="community", values="sailors", hole=0.35,
                          title="Force Distribution by Community")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
            st.plotly_chart(fig2, use_container_width=True)

        section("Critical Rate Manning")
        crit_df = query("""
            SELECT r.rate_code, r.rate_name, r.community, COUNT(*) AS sailors,
                   SUM(CASE WHEN julianday(s.eaos)-julianday('now') BETWEEN 0 AND 365 THEN 1 ELSE 0 END) AS eaos_12mo
            FROM sailor s JOIN rate r ON s.rate_code=r.rate_code
            WHERE s.status='Active' AND r.is_critical=1
            GROUP BY r.rate_code ORDER BY eaos_12mo DESC LIMIT 20
        """)
        if not crit_df.empty:
            crit_df["EAOS Risk %"] = (crit_df["eaos_12mo"] / crit_df["sailors"] * 100).round(1)
            st.dataframe(crit_df.rename(columns={"rate_code":"Rate","rate_name":"Name","community":"Community","sailors":"Sailors","eaos_12mo":"EAOS <12mo"}),
                         use_container_width=True, hide_index=True)
            st.caption("Critical rates with highest percentage reaching EAOS in 12 months.")

    with tab_eaos:
        section("EAOS Outlook — Rolling 24-Month Window")
        eaos_q = query("""
            SELECT CAST(strftime('%Y',eaos) AS TEXT)||'-Q'||CAST(((CAST(strftime('%m',eaos) AS INTEGER)-1)/3)+1 AS TEXT) AS quarter,
                   r.community, COUNT(*) AS sailors
            FROM sailor s JOIN rate r ON s.rate_code=r.rate_code
            WHERE s.status='Active' AND julianday(eaos)-julianday('now') BETWEEN 0 AND 730
            GROUP BY quarter, r.community ORDER BY quarter
        """)
        if not eaos_q.empty:
            fig = px.bar(eaos_q, x="quarter", y="sailors", color="community", barmode="stack",
                         labels={"quarter":"Quarter","sailors":"Sailors","community":"Community"},
                         title="Sailors Reaching EAOS by Quarter and Community")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
            st.plotly_chart(fig, use_container_width=True)

        section("EAOS Bucket Summary")
        eaos_bucket = query("""
            SELECT CASE
                WHEN julianday(eaos)-julianday('now') BETWEEN 0 AND 90    THEN '0-3 months'
                WHEN julianday(eaos)-julianday('now') BETWEEN 91 AND 180  THEN '3-6 months'
                WHEN julianday(eaos)-julianday('now') BETWEEN 181 AND 365 THEN '6-12 months'
                WHEN julianday(eaos)-julianday('now') BETWEEN 366 AND 548 THEN '12-18 months'
                ELSE '18+ months'
            END AS window, COUNT(*) AS sailors
            FROM sailor WHERE status='Active' AND julianday(eaos)-julianday('now') >= 0
            GROUP BY window
        """)
        order = ["0-3 months","3-6 months","6-12 months","12-18 months","18+ months"]
        if not eaos_bucket.empty:
            eaos_bucket["window"] = pd.Categorical(eaos_bucket["window"], categories=order, ordered=True)
            eaos_bucket = eaos_bucket.sort_values("window")
            fig2 = px.funnel(eaos_bucket, x="sailors", y="window",
                             title="EAOS Funnel — Sailors by Time-to-Separation",
                             labels={"sailors":"Sailors","window":"Window"},
                             color_discrete_sequence=["#003B4F"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#08262C")
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("Sailors in the 0-6 month window require immediate retention or transition coordination.")

# ── CASES & WORKFLOWS ─────────────────────────────────────────────────────────
elif page == "Cases & Workflows":
    page_header("Cases & Workflows",
                "Enterprise workflow queue — actionable cases derived from digital twin data")

    # Build workflow case sets from live data
    df_srb = query("""
        SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name, r.community,
               c.command_name, c.region,
               CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INTEGER) AS months_to_eaos,
               pr.srb_zone, pr.srb_multiplier, pr.srb_eligible_until
        FROM sailor s
        JOIN rate r     ON s.rate_code=r.rate_code
        LEFT JOIN command c    ON s.current_command_id=c.command_id
        LEFT JOIN pay_record pr ON s.dod_id=pr.dod_id
        WHERE s.status='Active'
          AND pr.srb_zone IS NOT NULL
          AND julianday(s.eaos)-julianday('now') BETWEEN 0 AND 548
        ORDER BY months_to_eaos ASC
        LIMIT 300
    """)

    df_nec_lapsed = query("""
        SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name, r.community,
               c.command_name,
               q.qual_code AS nec_code, q.qual_title, q.currency_expires
        FROM sailor s
        JOIN rate r        ON s.rate_code=r.rate_code
        LEFT JOIN command c ON s.current_command_id=c.command_id
        JOIN qualification q ON s.dod_id=q.dod_id
        WHERE s.status='Active'
          AND q.qual_type='NEC'
          AND q.is_current=0
        ORDER BY q.currency_expires ASC
        LIMIT 300
    """)

    df_pcs = query("""
        SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name, r.community,
               c.command_name, c.command_type, c.region,
               CAST((julianday(s.eaos)-julianday('now'))/30.0 AS INTEGER) AS months_to_eaos
        FROM sailor s
        JOIN rate r     ON s.rate_code=r.rate_code
        LEFT JOIN command c ON s.current_command_id=c.command_id
        WHERE s.status='Active'
          AND julianday(s.eaos)-julianday('now') BETWEEN 365 AND 608
        ORDER BY months_to_eaos ASC
        LIMIT 300
    """)

    df_nondeploy = query("""
        SELECT s.dod_id, s.paygrade, s.rate_code, r.rate_name, r.community,
               c.command_name,
               ms.dental_class, ms.immunizations_current, ms.deployment_limit_reason,
               ms.deployment_limit_until
        FROM sailor s
        JOIN rate r         ON s.rate_code=r.rate_code
        LEFT JOIN command c  ON s.current_command_id=c.command_id
        JOIN medical_status ms ON s.dod_id=ms.dod_id
        WHERE s.status='Active' AND ms.is_deployable=0
        ORDER BY s.paygrade
        LIMIT 300
    """)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("SRB / Reenlistment",   f"{len(df_srb):,}",       delta="cases open", delta_color="off")
    k2.metric("Lapsed NEC Certs",     f"{len(df_nec_lapsed):,}", delta="need recert", delta_color="off")
    k3.metric("PCS Orders Window",    f"{len(df_pcs):,}",        delta="12-20 mo EAOS", delta_color="off")
    k4.metric("Non-Deployable",       f"{len(df_nondeploy):,}",  delta="action required", delta_color="inverse")

    st.divider()

    wf_type = st.radio("Workflow Type",
                       ["SRB / Reenlistment", "Training / NEC Recertification", "PCS Orders", "Medical Readiness"],
                       horizontal=True)

    # ── SRB / Reenlistment ──────────────────────────────────────────────────
    if wf_type == "SRB / Reenlistment":
        st.markdown(f"### 📝 SRB / Reenlistment Queue — {len(df_srb)} open cases")

        fc1, fc2 = st.columns(2)
        with fc1:
            pg_opts = ["All"] + sorted(df_srb["paygrade"].dropna().unique().tolist()) if not df_srb.empty else ["All"]
            pg_sel  = st.selectbox("Paygrade", pg_opts, key="srb_pg")
        with fc2:
            cm_opts = ["All"] + sorted(df_srb["community"].dropna().unique().tolist()) if not df_srb.empty else ["All"]
            cm_sel  = st.selectbox("Community", cm_opts, key="srb_cm")

        flt = df_srb.copy()
        if pg_sel != "All": flt = flt[flt["paygrade"] == pg_sel]
        if cm_sel != "All": flt = flt[flt["community"] == cm_sel]

        for _, row in flt.head(25).iterrows():
            mos  = int(row.get("months_to_eaos", 99) or 99)
            urg  = "🔴 URGENT" if mos <= 6 else ("🟡 ACTION REQUIRED" if mos <= 12 else "🟢 MONITOR")
            ucol = "#B30003" if mos <= 6 else ("#E8B00F" if mos <= 12 else "#088199")
            st.markdown(f"""
            <div class="wf-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-size:15px;font-weight:700;color:#003B4F;">
                    {row['paygrade']} {row['rate_code']} &nbsp;
                    <span style="font-weight:400;color:#546E7A;font-size:13px;">{row.get('rate_name','')}</span>
                  </div>
                  <div style="font-size:12px;color:#546E7A;margin-top:2px;">
                    DoD ID: {row['dod_id']} &nbsp;|&nbsp; Command: {row.get('command_name','—')} &nbsp;|&nbsp; {row.get('community','—')}
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:13px;font-weight:700;color:{ucol};">{urg}</div>
                  <div style="font-size:12px;color:#546E7A;">EAOS in {mos} months</div>
                </div>
              </div>
              <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
                <span style="background:#003B4F;color:#fff;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:600;">SRB Zone {row.get('srb_zone','—')}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">x{float(row.get('srb_multiplier') or 0):.1f} multiplier</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">Eligible until: {str(row.get('srb_eligible_until','—'))[:10]}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">📋 Initiate via NSIPS &nbsp;|&nbsp; Policy: MILPERSMAN 1160-120</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        if len(flt) > 25:
            st.info(f"Showing top 25 of {len(flt)} filtered cases.")

    # ── NEC Recertification ──────────────────────────────────────────────────
    elif wf_type == "Training / NEC Recertification":
        st.markdown(f"### 🎓 NEC Recertification Queue — {len(df_nec_lapsed)} lapsed certificates")

        fc1, fc2 = st.columns(2)
        with fc1:
            nec_opts = ["All"] + sorted(df_nec_lapsed["nec_code"].dropna().unique().tolist()) if not df_nec_lapsed.empty else ["All"]
            nec_sel  = st.selectbox("NEC Code", nec_opts, key="nec_sel")
        with fc2:
            cm_opts  = ["All"] + sorted(df_nec_lapsed["community"].dropna().unique().tolist()) if not df_nec_lapsed.empty else ["All"]
            cm_sel   = st.selectbox("Community", cm_opts, key="nec_cm")

        flt = df_nec_lapsed.copy()
        if nec_sel != "All": flt = flt[flt["nec_code"] == nec_sel]
        if cm_sel  != "All": flt = flt[flt["community"] == cm_sel]

        for _, row in flt.head(25).iterrows():
            try:
                days_lapsed = (pd.Timestamp.today() - pd.to_datetime(row["currency_expires"])).days
            except Exception:
                days_lapsed = 0
            ucol = "#B30003" if days_lapsed > 90 else "#E8B00F"
            st.markdown(f"""
            <div class="wf-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-size:15px;font-weight:700;color:#003B4F;">
                    {row['paygrade']} {row['rate_code']}
                    <span style="font-weight:400;color:#546E7A;font-size:13px;"> — {row.get('rate_name','')}</span>
                  </div>
                  <div style="font-size:12px;color:#546E7A;margin-top:2px;">
                    DoD ID: {row['dod_id']} &nbsp;|&nbsp; Command: {row.get('command_name','—')} &nbsp;|&nbsp; {row.get('community','—')}
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:13px;font-weight:700;color:{ucol};">⚠️ LAPSED {days_lapsed}d ago</div>
                  <div style="font-size:12px;color:#546E7A;">Expired: {str(row.get('currency_expires','—'))[:10]}</div>
                </div>
              </div>
              <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
                <span style="background:#003B4F;color:#fff;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:600;">NEC {row.get('nec_code','—')}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">{row.get('qual_title','—')}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">📋 Schedule via NTMPS/FLTMPS &nbsp;|&nbsp; Policy: NAVEDTRA 10500</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        if len(flt) > 25:
            st.info(f"Showing top 25 of {len(flt)} filtered cases.")

    # ── PCS Orders ──────────────────────────────────────────────────────────
    elif wf_type == "PCS Orders":
        st.markdown(f"### 📦 PCS Orders Queue — {len(df_pcs)} sailors in detailing window")

        fc1, fc2 = st.columns(2)
        with fc1:
            pg_opts = ["All"] + sorted(df_pcs["paygrade"].dropna().unique().tolist()) if not df_pcs.empty else ["All"]
            pg_sel  = st.selectbox("Paygrade", pg_opts, key="pcs_pg")
        with fc2:
            dt_opts = ["All"] + sorted(df_pcs["command_type"].dropna().unique().tolist()) if not df_pcs.empty else ["All"]
            dt_sel  = st.selectbox("Current Duty Type", dt_opts, key="pcs_dt")

        flt = df_pcs.copy()
        if pg_sel != "All": flt = flt[flt["paygrade"] == pg_sel]
        if dt_sel != "All": flt = flt[flt["command_type"] == dt_sel]

        for _, row in flt.head(25).iterrows():
            mos = int(row.get("months_to_eaos", 99) or 99)
            st.markdown(f"""
            <div class="wf-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-size:15px;font-weight:700;color:#003B4F;">
                    {row['paygrade']} {row['rate_code']}
                    <span style="font-weight:400;color:#546E7A;font-size:13px;"> — {row.get('rate_name','')}</span>
                  </div>
                  <div style="font-size:12px;color:#546E7A;margin-top:2px;">
                    DoD ID: {row['dod_id']} &nbsp;|&nbsp; Command: {row.get('command_name','—')} ({row.get('command_type','—')}) &nbsp;|&nbsp; {row.get('region','—')}
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:13px;font-weight:700;color:#003B4F;">📦 PCS WINDOW</div>
                  <div style="font-size:12px;color:#546E7A;">EAOS in {mos} months</div>
                </div>
              </div>
              <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">Community: {row.get('community','—')}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">📋 Initiate orders in TFMMS / CMS-ID &nbsp;|&nbsp; Policy: MILPERSMAN 1300-300</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        if len(flt) > 25:
            st.info(f"Showing top 25 of {len(flt)} filtered cases.")

    # ── Medical Readiness ────────────────────────────────────────────────────
    elif wf_type == "Medical Readiness":
        st.markdown(f"### 🏥 Medical Readiness Queue — {len(df_nondeploy)} non-deployable sailors")

        fc1, fc2 = st.columns(2)
        with fc1:
            pg_opts = ["All"] + sorted(df_nondeploy["paygrade"].dropna().unique().tolist()) if not df_nondeploy.empty else ["All"]
            pg_sel  = st.selectbox("Paygrade", pg_opts, key="med_pg")
        with fc2:
            cm_opts = ["All"] + sorted(df_nondeploy["community"].dropna().unique().tolist()) if not df_nondeploy.empty else ["All"]
            cm_sel  = st.selectbox("Community", cm_opts, key="med_cm")

        flt = df_nondeploy.copy()
        if cm_sel != "All": flt = flt[flt["community"] == cm_sel]

        for _, row in flt.head(25).iterrows():
            reason = row.get("deployment_limit_reason") or "Not specified"
            until  = str(row.get("deployment_limit_until") or "—")[:10]
            imm    = "✅" if row.get("immunizations_current") else "⚠️"
            dc     = int(row.get("dental_class") or 0)
            dc_col = "#088199" if dc <= 2 else "#B30003"
            st.markdown(f"""
            <div class="wf-card" style="border-left-color:#B30003;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-size:15px;font-weight:700;color:#003B4F;">
                    {row['paygrade']} {row['rate_code']}
                    <span style="font-weight:400;color:#546E7A;font-size:13px;"> — {row.get('rate_name','')}</span>
                  </div>
                  <div style="font-size:12px;color:#546E7A;margin-top:2px;">
                    DoD ID: {row['dod_id']} &nbsp;|&nbsp; Command: {row.get('command_name','—')} &nbsp;|&nbsp; {row.get('community','—')}
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:13px;font-weight:700;color:#B30003;">🔴 NON-DEPLOYABLE</div>
                  <div style="font-size:12px;color:#546E7A;">Until: {until}</div>
                </div>
              </div>
              <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">Reason: {reason}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">Immunizations: {imm}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;color:{dc_col};">Dental Class {dc}</span>
                <span style="background:#EEF2F4;padding:3px 10px;border-radius:4px;font-size:12px;">📋 Schedule eval via MRRS/AHLTA &nbsp;|&nbsp; Policy: MANMED CH-15</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        if len(flt) > 25:
            st.info(f"Showing top 25 of {len(flt)} filtered cases.")
