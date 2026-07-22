"""Page 7 — Work Order Intelligence (Killer Feature 2)."""

import html as html_lib
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Work Orders · IndustrialMind", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, loading_screen, render_metric_card, render_source_citation

inject_css()
st.markdown("""
<style>
/* Equipment quick-select chip buttons — pill style */
div[data-testid="stHorizontalBlock"] [data-testid="stBaseButton-secondary"] {
    border-radius: 99px !important;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    padding: 2px 6px !important;
    background: #f1f5f9 !important;
    border: 1px solid #D1D5DB !important;
    color: #475569 !important;
    line-height: 1.6 !important;
    min-height: 28px !important;
}
div[data-testid="stHorizontalBlock"] [data-testid="stBaseButton-secondary"]:hover {
    background: #D1D5DB !important;
    border-color: #94a3b8 !important;
    color: #1e293b !important;
}
</style>
""", unsafe_allow_html=True)
sidebar_logo()
with st.sidebar:
    sidebar_nav("Work_Orders")

_lph = loading_screen()
_c  = load_for_page(["em", "rag"])
rag = _c["rag"]
em = _c["em"]
_lph.empty()

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-wrap">'
    '<div class="hero-eyebrow">Killer Feature 2 · Maintenance Intelligence</div>'
    '<div class="hero-title">Work Order Intelligence</div>'
    '<div class="hero-sub">Raise a work order and IndustrialMind instantly surfaces all relevant history, procedures, safety requirements, spare parts, and regulatory compliance — eliminating the 35% of time engineers spend searching for information.</div>'
    '<div class="hero-divider"></div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── WO KPI strip — computed from demo data ─────────────────────────────────────
_open_wos    = [{"id": "WO-2026-0867", "equipment": "P-101", "priority": "Critical",  "due": "2026-07-18"},
                {"id": "WO-2026-0866", "equipment": "HE-501", "priority": "High",     "due": "2026-07-22"},
                {"id": "WO-2026-0863", "equipment": "C-401",  "priority": "High",     "due": "2026-07-25"},
                {"id": "WO-2026-0861", "equipment": "E-304",  "priority": "Medium",   "due": "2026-07-30"},
                {"id": "WO-2026-0858", "equipment": "V-205",  "priority": "Low",      "due": "2026-08-05"}]
_prog_wos    = [{"id": "WO-2026-0847"}, {"id": "WO-2026-0843"}, {"id": "WO-2026-0831"}]
_closed_wos  = [{"created": "2026-06-28", "closed": "2026-07-02"},
                {"created": "2026-06-24", "closed": "2026-06-27"},
                {"created": "2026-06-18", "closed": "2026-06-22"}]
import datetime as _dt
_today = _dt.date.today()
_overdue = sum(1 for w in _open_wos if _dt.date.fromisoformat(w["due"]) < _today)
from statistics import mean as _mean
_close_days = [(_dt.date.fromisoformat(w["closed"]) - _dt.date.fromisoformat(w["created"])).days
               for w in _closed_wos]
_avg_close = _mean(_close_days) if _close_days else 0

k1, k2, k3, k4, k5 = st.columns(5)
with k1: render_metric_card("Open WOs",       str(len(_open_wos)),        "—", accent="#ef4444",  sub="awaiting action")
with k2: render_metric_card("In Progress",    str(len(_prog_wos)),        "—", accent="#2563eb",  sub="currently executing")
with k3: render_metric_card("Overdue",        str(_overdue),              "—", accent="#F59E0B",  sub="past target date")
with k4: render_metric_card("Closed (Month)", str(len(_closed_wos)),      "—", accent="#10b981",  sub="completed this month")
with k5: render_metric_card("Avg Close Time", f"{_avg_close:.1f}d",       "—", accent="#7c3aed",  sub="target: 4 days")

st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

# Impact banner
st.markdown(
    '<div style="background:#fff;border:1px solid #D1D5DB;border-left:3px solid #F59E0B;border-radius:12px;padding:14px 18px;margin-bottom:24px;font-size:13px;color:#374151">'
    '<b>The "35% wasted time" problem, solved.</b> Knowledge comes to the engineer '
    'the moment the work order is created — not after hours of searching.'
    '</div>',
    unsafe_allow_html=True,
)

# ── Work order form ────────────────────────────────────────────────────────────
col_form, col_preview = st.columns([1, 1], gap="large")

with col_form:
    st.markdown('<div class="section-label" style="margin-bottom:14px">Raise Work Order</div>', unsafe_allow_html=True)

    # Quick-launch equipment buttons
    st.markdown('<div style="font-size:11px;color:#94a3b8;margin-bottom:6px">Quick select:</div>',
                unsafe_allow_html=True)
    _eq_chip_cols = st.columns(5)
    for _ci, _eq in enumerate(["P-101", "V-205", "E-304", "C-401", "HE-501"]):
        with _eq_chip_cols[_ci]:
            if st.button(_eq, key=f"wo_chip_{_eq}", use_container_width=True):
                st.session_state["wo_quick_eq"] = _eq
                st.rerun()
    _preselect = st.session_state.get("wo_quick_eq", "")
    equipment_id = st.text_input("Equipment ID *", placeholder="P-101, V-205, E-304…",
                                 value=_preselect)
    work_type    = st.selectbox(
        "Work Type *",
        ["Corrective Maintenance","Preventive Maintenance","Inspection","Seal Replacement",
         "Bearing Replacement","Hot Work / Welding","Confined Space Entry",
         "Hydro Test / Pressure Test","Electrical Isolation","Shutdown / Turnaround"],
    )
    col_prio, col_crew = st.columns(2)
    with col_prio:
        priority = st.select_slider("Priority", ["Low", "Medium", "High", "Critical"])
    with col_crew:
        crew_size = st.number_input("Crew Size", min_value=1, max_value=20, value=2)

    description = st.text_area("Work Description", placeholder="Brief description of work…", height=80)

    col_est, col_permit = st.columns(2)
    with col_est:
        est_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=72.0, value=4.0, step=0.5)
    with col_permit:
        requires_ptw = st.checkbox("Requires PTW", value=True)

    if st.button("Generate Knowledge Brief", type="primary", use_container_width=True):
        if not equipment_id.strip():
            st.error("Equipment ID is required.")
        else:
            if em.get_stats()["total_chunks"] == 0:
                st.warning("Upload documents first to generate a knowledge brief.")
            else:
                with st.spinner(f"Pulling all knowledge for {equipment_id.strip()}…"):
                    brief = rag.generate_work_context(equipment_id.strip(), work_type)
                st.session_state["work_brief"]    = brief
                st.session_state["work_eq"]       = equipment_id.strip()
                st.session_state["work_type"]     = work_type
                st.session_state["work_priority"] = priority
                st.session_state["work_crew"]     = crew_size
                st.session_state["work_est_hrs"]  = est_hours
                st.session_state["work_ptw"]      = requires_ptw
                st.rerun()

with col_preview:
    st.markdown(
        '<div style="background:#fff;border:1px solid #D1D5DB;border-radius:16px;padding:22px;box-shadow:0 1px 3px rgba(0,0,0,.05)">'
        '<div class="section-label" style="margin-bottom:14px">What Gets Retrieved</div>'
        '<div style="display:flex;flex-direction:column;gap:8px">'
        + "".join(
            f'<div style="display:flex;align-items:flex-start;gap:12px;padding:10px 12px;'
            f'background:#FAFAFB;border:1px solid #D1D5DB;border-radius:10px">'
            f'<div style="width:6px;height:16px;border-radius:50%;background:#F59E0B;flex-shrink:0;margin-top:5px"></div>'
            f'<div><div style="font-size:13px;font-weight:600;color:#111827">{title}</div>'
            f'<div style="font-size:12px;color:#6B7280">{desc}</div></div></div>'
            for title, desc in [
                ("Maintenance History", "Last 3 failures, parts replaced, labour hours, dates"),
                ("Procedure Steps", "Exact SOP for this work type, step-by-step"),
                ("Incident History", "Past accidents, near-misses, lessons learned"),
                ("Regulations", "OISD / Factory Act / DGMS requirements"),
                ("Expert Knowledge", "Tribal knowledge from senior engineers"),
                ("Safety Checklist", "PPE, LOTO, PTW, gas test requirements"),
            ]
        )
        + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Knowledge Brief display ────────────────────────────────────────────────────
brief = st.session_state.get("work_brief")
if brief:
    eq   = st.session_state.get("work_eq", "")
    wt   = st.session_state.get("work_type", "")
    prio = st.session_state.get("work_priority", "Medium")
    crew = st.session_state.get("work_crew", 2)
    est  = st.session_state.get("work_est_hrs", 4.0)
    ptw  = st.session_state.get("work_ptw", True)

    prio_map = {
        "Critical": ("#dc2626", "#fef2f2", "#fecaca"),
        "High":     ("#ea580c", "#fff7ed", "#fed7aa"),
        "Medium":   ("#d97706", "#fef3c7", "#fde68a"),
        "Low":      ("#059669", "#ecfdf5", "#a7f3d0"),
    }
    p_color, p_bg, p_border = prio_map.get(prio, ("#475569", "#FAFAFB", "#D1D5DB"))

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    # Brief header
    st.markdown(
        f'<div style="background:#fff;border:2px solid {p_border};border-radius:16px;padding:20px 24px;'
        f'margin-bottom:16px;box-shadow:0 2px 12px rgba(0,0,0,0.06)">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px">'
        f'<div style="font-size:18px;font-weight:800;color:#0f172a;letter-spacing:-0.02em">'
        f'Knowledge Brief: <span style="color:#f59e0b">{html_lib.escape(eq)}</span>'
        f'<span style="color:#64748b;font-weight:400"> — {html_lib.escape(wt)}</span></div>'
        f'<span style="background:{p_bg};color:{p_color};border:1.5px solid {p_border};'
        f'padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700">⚠️ {html_lib.escape(prio)}</span>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px">'
        f'<div style="background:#FAFAFB;border-radius:8px;padding:10px 12px">'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase">Est. Duration</div>'
        f'<div style="font-size:15px;font-weight:700;color:#0f172a">{est} hrs</div>'
        f'</div>'
        f'<div style="background:#FAFAFB;border-radius:8px;padding:10px 12px">'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase">Crew Size</div>'
        f'<div style="font-size:15px;font-weight:700;color:#0f172a">{crew} persons</div>'
        f'</div>'
        f'<div style="background:{"#fef2f2" if ptw else "#F0FDF4"};border-radius:8px;padding:10px 12px">'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase">PTW Required</div>'
        f'<div style="font-size:14px;font-weight:700;color:{"#dc2626" if ptw else "#16a34a"}">{"Yes" if ptw else "No"}</div>'
        f'</div>'
        f'<div style="background:#FAFAFB;border:1px solid #D1D5DB;border-radius:8px;padding:10px 12px">'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase">Est. Labour Cost</div>'
        f'<div style="font-size:14px;font-weight:700;color:#d97706">₹{int(est*crew*850):,}</div>'
        f'<div style="font-size:10px;color:#94a3b8;margin-top:2px">@ ₹850/person-hr</div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(brief.get("brief") or brief.get("summary", "No brief generated."))

    sections = brief.get("sections", {})
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: render_metric_card("Maintenance Records", str(len(sections.get("maintenance_history", []))), "—", accent="#F59E0B")
    with m2: render_metric_card("Procedures Found",    str(len(sections.get("procedures", []))),          "—", accent="#7c3aed")
    with m3: render_metric_card("Incident Records",    str(len(sections.get("incidents", []))),           "—", accent="#ef4444")
    with m4: render_metric_card("Regulations",         str(len(sections.get("regulations", []))),         "—", accent="#2563eb")

    # Safety checklist — real interactive checkboxes
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="background:#fff;border:1px solid #D1D5DB;border-left:3px solid #F59E0B;border-radius:12px;'
        'padding:12px 18px 6px;margin-bottom:4px">'
        '<div style="font-size:13px;font-weight:700;color:#D97706">Pre-Work Safety Checklist</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    _checklist_items = [
        "Permit to Work issued and signed",
        "LOTO (Lockout/Tagout) applied",
        "Gas test completed — LEL <10%",
        "PPE issued: coveralls, gloves, goggles",
        "Rescue team on standby (if CSE)",
        "Emergency shutdown procedure briefed",
        "Fire extinguisher positioned at worksite",
        "Toolbox talk conducted with crew",
    ]
    _cl_col1, _cl_col2 = st.columns(2)
    _cl_checked = 0
    for _ci, _item in enumerate(_checklist_items):
        _col = _cl_col1 if _ci % 2 == 0 else _cl_col2
        with _col:
            if st.checkbox(_item, key=f"ptw_{eq}_{_ci}"):
                _cl_checked += 1
    _cl_all = len(_checklist_items)
    _cl_pct = int(_cl_checked / _cl_all * 100)
    _cl_color = "#16a34a" if _cl_pct == 100 else "#d97706" if _cl_pct >= 50 else "#dc2626"
    st.markdown(
        f'<div style="background:#FAFAFB;border:1px solid #D1D5DB;border-radius:0 0 12px 12px;'
        f'padding:8px 18px 12px;margin-bottom:12px;font-size:12px;font-weight:700;color:{_cl_color}">'
        f'{"All checks complete — safe to proceed" if _cl_pct == 100 else f"{_cl_checked}/{_cl_all} checks complete ({_cl_pct}%)"}'
        f'</div>',
        unsafe_allow_html=True,
    )

    for section_key, label, sources in [
        ("maintenance_history", "Maintenance History",    sections.get("maintenance_history", [])),
        ("procedures",          "Applicable Procedures",  sections.get("procedures", [])),
        ("incidents",           "Incident History",       sections.get("incidents", [])),
        ("regulations",         "Regulatory Requirements",sections.get("regulations", [])),
    ]:
        if sources:
            with st.expander(f"{label} ({len(sources)} records)", expanded=(section_key == "incidents")):
                for s in sources:
                    render_source_citation(s)

    brief_text = (
        f"WORK ORDER KNOWLEDGE BRIEF\n{'='*40}\n"
        f"Equipment : {eq}\nWork Type : {wt}\nPriority  : {prio}\n"
        f"Est Hours : {est}\nCrew Size : {crew}\n\n" + (brief.get("brief") or brief.get("summary", ""))
    )
    st.download_button("📥 Download Brief (TXT)", brief_text, f"brief_{eq}_{wt.replace(' ','_')}.txt", "text/plain")

st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

# ── Work order tracker ─────────────────────────────────────────────────────────
DEMO_WOS = {
    "open": [
        {"id": "WO-2026-0867", "equipment": "P-101", "type": "Seal Replacement",      "priority": "Critical",  "created": "2026-07-10", "due": "2026-07-18", "crew": 3},
        {"id": "WO-2026-0866", "equipment": "HE-501","type": "Tube Cleaning",          "priority": "High",      "created": "2026-07-11", "due": "2026-07-22", "crew": 2},
        {"id": "WO-2026-0863", "equipment": "C-401", "type": "Valve Inspection",       "priority": "High",      "created": "2026-07-09", "due": "2026-07-25", "crew": 2},
        {"id": "WO-2026-0861", "equipment": "E-304", "type": "Corrective Maintenance", "priority": "Medium",    "created": "2026-07-08", "due": "2026-07-30", "crew": 2},
        {"id": "WO-2026-0858", "equipment": "V-205", "type": "Inspection",             "priority": "Low",       "created": "2026-07-06", "due": "2026-08-05", "crew": 1},
    ],
    "progress": [
        {"id": "WO-2026-0847", "equipment": "P-101", "type": "Bearing Replacement",    "priority": "High",      "created": "2026-07-01", "due": "2026-07-20", "crew": 2},
        {"id": "WO-2026-0843", "equipment": "E-304", "type": "Hydro Test",             "priority": "Critical",  "created": "2026-06-29", "due": "2026-07-15", "crew": 4},
        {"id": "WO-2026-0831", "equipment": "V-205", "type": "Inspection",             "priority": "Medium",    "created": "2026-06-27", "due": "2026-07-19", "crew": 1},
    ],
    "closed": [
        {"id": "WO-2026-0819", "equipment": "E-304", "type": "Corrective Maintenance", "priority": "High",      "created": "2026-06-28", "closed": "2026-07-02", "crew": 3},
        {"id": "WO-2026-0812", "equipment": "C-401", "type": "PM Schedule",            "priority": "Medium",    "created": "2026-06-24", "closed": "2026-06-27", "crew": 2},
        {"id": "WO-2026-0806", "equipment": "HE-501","type": "Tube Replacement",       "priority": "Critical",  "created": "2026-06-18", "closed": "2026-06-22", "crew": 4},
    ],
}

status_cfg = {
    "Critical": ("#dc2626", "#fef2f2", "#fecaca"),
    "High":     ("#ea580c", "#fff7ed", "#fed7aa"),
    "Medium":   ("#d97706", "#fef3c7", "#fde68a"),
    "Low":      ("#059669", "#ecfdf5", "#a7f3d0"),
}

def render_wo_table(wos, show_closed=False):
    for wo in wos:
        s_color, s_bg, s_border = status_cfg.get(wo["priority"], ("#475569", "#FAFAFB", "#D1D5DB"))
        date_label = wo.get("closed", wo.get("due", "—"))
        date_key   = "Closed" if show_closed else "Due"

        cols = st.columns([2, 1.2, 2.2, 1.2, 1.2, 1])
        with cols[0]:
            st.markdown(
                f'<div style="padding:8px 0">'
                f'<div style="font-size:13.5px;font-weight:700;color:#0f172a">{html_lib.escape(wo["id"])}</div>'
                f'<div style="font-size:11px;color:#94a3b8;margin-top:2px">Created: {wo["created"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(
                f'<div style="padding:8px 0">'
                f'<code style="background:#fef3c7;color:#d97706;padding:4px 10px;'
                f'border-radius:6px;font-size:13px;font-weight:700;border:1px solid #fde68a">'
                f'{html_lib.escape(wo["equipment"])}</code>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with cols[2]:
            st.markdown(
                f'<div style="padding:8px 0;font-size:13px;color:#334155">{html_lib.escape(wo["type"])}</div>',
                unsafe_allow_html=True,
            )
        with cols[3]:
            st.markdown(
                f'<div style="padding:8px 0">'
                f'<span style="background:{s_bg};color:{s_color};border:1px solid {s_border};'
                f'padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">'
                f'{html_lib.escape(wo["priority"])}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with cols[4]:
            st.markdown(
                f'<div style="padding:8px 0;font-size:11.5px;color:#64748b">'
                f'<div style="font-weight:600;color:#334155">{date_key}:</div>{date_label}'
                f'</div>',
                unsafe_allow_html=True,
            )
        with cols[5]:
            if st.button("Brief →", key=f"wo_{wo['id']}", use_container_width=True, type="primary"):
                with st.spinner("Generating brief…"):
                    b = rag.generate_work_context(wo["equipment"], wo["type"])
                st.session_state["work_brief"]    = b
                st.session_state["work_eq"]       = wo["equipment"]
                st.session_state["work_type"]     = wo["type"]
                st.session_state["work_priority"] = wo["priority"]
                st.session_state["work_crew"]     = wo.get("crew", 2)
                st.session_state["work_est_hrs"]  = 4.0
                st.session_state["work_ptw"]      = True
                st.rerun()

        st.markdown('<div style="border-bottom:1px solid #f1f5f9;margin:0 0 4px"></div>', unsafe_allow_html=True)

n_open     = len(DEMO_WOS["open"])
n_progress = len(DEMO_WOS["progress"])
n_closed   = len(DEMO_WOS["closed"])
wo_tab_open, wo_tab_progress, wo_tab_closed = st.tabs([
    f"🔴 Open ({n_open})",
    f"🔄 In Progress ({n_progress})",
    f"✅ Closed ({n_closed})",
])

with wo_tab_open:
    st.markdown('<div class="section-label" style="margin:10px 0 12px">Open Work Orders — click Brief → for knowledge pack</div>', unsafe_allow_html=True)
    render_wo_table(DEMO_WOS["open"])

with wo_tab_progress:
    st.markdown('<div class="section-label" style="margin:10px 0 12px">Work Orders In Progress</div>', unsafe_allow_html=True)
    render_wo_table(DEMO_WOS["progress"])

with wo_tab_closed:
    st.markdown('<div class="section-label" style="margin:10px 0 12px">Recently Closed Work Orders</div>', unsafe_allow_html=True)
    render_wo_table(DEMO_WOS["closed"], show_closed=True)

st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

# ── WO analytics charts ────────────────────────────────────────────────────────
st.markdown('<div class="section-label" style="margin-bottom:14px">Work Order Analytics</div>', unsafe_allow_html=True)

ch1, ch2 = st.columns(2, gap="large")

with ch1:
    st.markdown('<div class="chart-row-header">Monthly WO Volume</div>', unsafe_allow_html=True)
    fig_wo = go.Figure(go.Bar(
        x=["Jan","Feb","Mar","Apr","May","Jun"],
        y=[18, 22, 19, 25, 31, 28],
        name="Closed", marker_color="#22c55e",
        text=[18, 22, 19, 25, 31, 28], textposition="auto",
        textfont=dict(color="#fff", size=11),
    ))
    fig_wo.add_trace(go.Bar(
        x=["Jan","Feb","Mar","Apr","May","Jun"],
        y=[8, 11, 7, 14, 12, 12],
        name="Open", marker_color="#ef4444",
        text=[8, 11, 7, 14, 12, 12], textposition="auto",
        textfont=dict(color="#fff", size=11),
    ))
    fig_wo.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFB",
        font=dict(color="#475569", size=11, family="Inter"),
        height=240, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#D1D5DB"),
    )
    st.plotly_chart(fig_wo, use_container_width=True)

with ch2:
    st.markdown('<div class="chart-row-header">WOs by Equipment (2026)</div>', unsafe_allow_html=True)
    wo_by_eq = {"P-101": 14, "E-304": 11, "HE-501": 8, "V-205": 6, "C-401": 5, "P-102": 4}
    fig_eq = go.Figure(go.Bar(
        y=list(wo_by_eq.keys()), x=list(wo_by_eq.values()),
        orientation="h",
        marker_color=["#ef4444","#f97316","#f59e0b","#3b82f6","#7c3aed","#22c55e"],
        text=list(wo_by_eq.values()), textposition="auto",
        textfont=dict(color="#fff", size=12),
    ))
    fig_eq.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFB",
        font=dict(color="#475569", size=11, family="Inter"),
        height=240, margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(gridcolor="#D1D5DB"),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_eq, use_container_width=True)


