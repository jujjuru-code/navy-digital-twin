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
    [data-testid="stSidebar"] { display: none; }
    .login-hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }
    .login-hero h1 {
        font-family: 'Roboto Slab', serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #003B4F;
        letter-spacing: .04em;
        margin-bottom: 4px;
    }
    .login-hero p {
        color: #546E7A;
        font-size: 1rem;
        margin-bottom: 0;
    }
    .persona-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        max-width: 860px;
        margin: 0 auto 2rem;
    }
    @media (max-width: 700px) {
        .persona-grid { grid-template-columns: 1fr; }
    }
    .persona-card {
        background: #fff;
        border: 2px solid #C6CCD0;
        border-radius: 12px;
        padding: 28px 20px 20px;
        text-align: center;
        transition: border-color .2s, box-shadow .2s;
        cursor: pointer;
    }
    .persona-card:hover { border-color: #088199; box-shadow: 0 4px 18px rgba(8,129,153,.15); }
    .persona-icon { font-size: 3rem; margin-bottom: 10px; }
    .persona-role { font-size: 18px; font-weight: 800; color: #003B4F; margin-bottom: 4px; }
    .persona-name { font-size: 15px; font-weight: 600; color: #08262C; margin-bottom: 2px; }
    .persona-desc { font-size: 12px; color: #546E7A; margin-bottom: 4px; line-height: 1.5; }
    .persona-unit { font-size: 11px; color: #088199; font-weight: 600; }
    .login-divider {
        text-align: center;
        color: #C6CCD0;
        font-size: 11px;
        letter-spacing: .1em;
        margin: 0 auto 1.5rem;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

    # Navy anchor + branding
    st.markdown("""
    <div class="login-hero">
        <div style="font-size:4rem;margin-bottom:8px;">⚓</div>
        <h1>Sailor Digital Twin</h1>
        <p>MyNavy HR &nbsp;·&nbsp; Powered by Anthropic Claude &nbsp;·&nbsp; POC Demo</p>
        <p style="margin-top:6px;font-size:12px;color:#aaa;">All data is synthetic — no PII</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="login-divider">— Select your role to begin the demo —</p>', unsafe_allow_html=True)

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
            if row.get("srb_zone") and mos <= 18:
                concerns.append(("🟡", f"SRB Zone {row['srb_zone']} ×{float(row['srb_multiplier'] or 0):.1f} pending"))
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
                    <span style="font-size:11px;color:#888;margin-left:auto;">DoD ID: {row['dod_id']}</span>
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
            st.bar_chart(eaos_dist.set_index("window"), color="#B30003", height=200)


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
        if pg_sel != "All": flt = flt[flt["paygrade"] == pg_sel]
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
