"""Page 5 — Failure Pattern Intelligence."""

import streamlit as st
import plotly.graph_objects as go
import html as html_lib

st.set_page_config(page_title="Patterns · IndustrialMind", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, loading_screen, render_pattern_card, plotly_defaults, render_chart_card_header

inject_css()
sidebar_logo()
with st.sidebar:
    sidebar_nav("Patterns")

_lph = loading_screen()
_c  = load_for_page(["em", "pa"])
pa = _c["pa"]
em = _c["em"]
_lph.empty()

st.markdown("""
<style>
.alert-card { background: #fef2f2; border: 1px solid #D1D5DB; border-left: 3px solid #ef4444;
    border-radius: 12px; padding: 14px 18px; margin: 6px 0; color: #991b1b;
    font-size: 13px; line-height: 1.6; }
.pred-box { background: #fff; border: 1px solid #D1D5DB; border-radius: 16px;
    padding: 20px 18px; box-shadow: 0 1px 3px rgba(0,0,0,.05); }
.pred-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin-bottom: 16px; }
.pred-cell { border-radius: 14px; padding: 14px; border: 1px solid #D1D5DB; }
</style>
<div class="hero-wrap">
  <div class="hero-eyebrow">Predictive Intelligence</div>
  <div class="hero-title">Failure Pattern Analysis</div>
  <div class="hero-sub">Spots recurring failures across years of records that no single engineer could connect alone — seasonal trends, MTBF benchmarks, cost impact modelling, and predictive failure timelines.</div>
  <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

if em.get_stats()["total_chunks"] == 0:
    st.warning("Upload maintenance records and incident reports first.", icon="⚠️")
    st.stop()

# ── Cost impact KPIs ───────────────────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
    '<div class="section-label" style="margin-bottom:0">Estimated Failure Cost Impact (2023–2024)</div>'
    '<span style="font-size:10px;font-weight:700;color:#7c3aed;background:#faf5ff;'
    'border:1px solid #ddd6fe;border-radius:20px;padding:2px 10px">Demo Model</span>'
    '</div>',
    unsafe_allow_html=True,
)
cost_items = [
    ("Total Downtime",   "312 hrs",  "illustrative demo value",         "#dc2626"),
    ("Lost Production",  "₹2.8 Cr",  "at ₹90K/hr plant rate",          "#d97706"),
    ("Repair Costs",     "₹48 L",    "illustrative demo value",         "#2563eb"),
    ("Preventable",      "67%",       "of failures detectable early",    "#7c3aed"),
    ("AI Savings Est.",  "₹1.9 Cr",  "with predictive maintenance",     "#16a34a"),
]
kpi_html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:24px">'
for label, val, sub, color in cost_items:
    kpi_html += (
        f'<div class="metric-card">'
        f'<div class="metric-card-bar" style="background:{color}"></div>'
        f'<div class="metric-value" style="color:{color}">{val}</div>'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'</div>'
    )
kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)

st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

# ── MTBF table ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
    '<div class="section-label" style="margin-bottom:0">Equipment MTBF vs Industry Benchmarks</div>'
    '<span style="font-size:10px;font-weight:700;color:#2563eb;background:#eff6ff;'
    'border:1px solid #bfdbfe;border-radius:20px;padding:2px 10px">Sample Data — Run Analysis for actual MTBF</span>'
    '</div>',
    unsafe_allow_html=True,
)

mtbf_data = [
    ("P-101", "Centrifugal Pump",  "Seal failure",       "4.2 mo", "6–9 mo",   72, "#ef4444"),
    ("P-102", "Centrifugal Pump",  "Bearing wear",       "8.1 mo", "6–9 mo",   88, "#22c55e"),
    ("V-205", "Pressure Vessel",   "Corrosion pitting",  "18.4 mo","18–24 mo", 91, "#22c55e"),
    ("E-304", "Heat Exchanger",    "Fouling / blockage", "5.7 mo", "8–12 mo",  65, "#f59e0b"),
    ("C-401", "Compressor",        "Valve leakage",      "11.2 mo","10–14 mo", 82, "#22c55e"),
    ("HE-501","Shell & Tube HE",   "Tube erosion",       "7.3 mo", "9–12 mo",  74, "#f59e0b"),
]

hcols = st.columns([1.5, 2, 2.2, 1.5, 1.8, 1.4])
for col, lbl in zip(hcols, ["Equipment","Type","Primary Failure","Plant MTBF","Benchmark","Health"]):
    with col:
        st.markdown(f'<div style="font-size:10.5px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;padding:6px 0;border-bottom:2px solid #e2e8f0">{lbl}</div>', unsafe_allow_html=True)

for eq_id, eq_type, mode, mtbf, benchmark, health_pct, health_color in mtbf_data:
    r1,r2,r3,r4,r5,r6 = st.columns([1.5,2,2.2,1.5,1.8,1.4])
    with r1:
        st.markdown(f'<code style="background:#fef3c7;color:#d97706;padding:4px 10px;border-radius:6px;font-size:13px;font-weight:700;border:1px solid #fde68a">{eq_id}</code>', unsafe_allow_html=True)
    with r2:
        st.markdown(f'<div style="font-size:13px;color:#475569;padding:8px 0">{eq_type}</div>', unsafe_allow_html=True)
    with r3:
        st.markdown(f'<div style="font-size:12.5px;color:#334155;padding:8px 0">{mode}</div>', unsafe_allow_html=True)
    with r4:
        st.markdown(f'<div style="font-size:13px;font-weight:700;color:#0f172a;padding:8px 0">{mtbf}</div>', unsafe_allow_html=True)
    with r5:
        st.markdown(f'<div style="font-size:12.5px;color:#64748b;padding:8px 0">{benchmark}</div>', unsafe_allow_html=True)
    with r6:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;padding:8px 0">'
            f'<div style="flex:1;background:#f1f5f9;border-radius:3px;height:6px;overflow:hidden">'
            f'<div style="background:{health_color};height:100%;width:{health_pct}%;border-radius:3px"></div></div>'
            f'<span style="font-size:11px;font-weight:700;color:{health_color}">{health_pct}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

# ── Trigger ────────────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 2], gap="large")
with col_btn:
    if st.button("Analyse Failure Patterns", type="primary", use_container_width=True):
        with st.spinner("Scanning all records for patterns…"):
            report = pa.generate_pattern_report()
        st.session_state["pattern_report"] = report

with col_info:
    st.markdown(
        '<div class="info-banner">'
        '💡 Analyses maintenance records and incident reports to surface recurring failure modes, '
        'seasonal risk peaks, leading indicators, and predictive timelines per equipment.'
        '</div>',
        unsafe_allow_html=True,
    )

report = st.session_state.get("pattern_report")
if not report:
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="background:#fff;border:1px solid #D1D5DB;border-left:3px solid #F59E0B;border-radius:12px;padding:12px 18px;margin-bottom:16px">'
        '<div style="font-size:12.5px;color:#374151;line-height:1.6">'
        '<b>Click "Analyse Failure Patterns"</b> above to generate real pattern charts from your uploaded documents. '
        'The sample charts below are illustrative only.</div></div>',
        unsafe_allow_html=True,
    )
    col_fc, col_trend = st.columns(2, gap="large")
    _pd = plotly_defaults(260)
    with col_fc:
        st.markdown(
            '<div class="chart-row-header">Failure Mode Distribution'
            '<span class="chart-row-header-badge">Illustrative</span></div>',
            unsafe_allow_html=True,
        )
        fig_h = go.Figure(go.Bar(
            x=["Seal Failure","Bearing Wear","Fouling","Corrosion","Valve Leak","Electrical"],
            y=[14,9,11,6,4,3],
            marker_color=["#ef4444","#f97316","#f59e0b","#eab308","#84cc16","#22c55e"],
            text=[14,9,11,6,4,3], textposition="outside",
            textfont=dict(color="#0f172a", size=12, family="Inter,sans-serif"),
            hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
        ))
        _pd_h = dict(_pd)
        _pd_h["xaxis"] = dict(**_pd["xaxis"], tickangle=-15)
        fig_h.update_layout(**_pd_h, yaxis_title="Incident Count")
        st.plotly_chart(fig_h, use_container_width=True)
    with col_trend:
        st.markdown(
            '<div class="chart-row-header">Monthly Incident Trend'
            '<span class="chart-row-header-badge">Illustrative</span></div>',
            unsafe_allow_html=True,
        )
        months_s = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=months_s, y=[2,4,7,10,14,20,25,30,33,36,40,47],
            name="Cumulative Incidents",
            line=dict(color="#ef4444", width=2.5),
            mode="lines+markers",
            marker=dict(size=6, color="#ef4444", line=dict(width=2, color="#fff")),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.07)",
            hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
        ))
        fig_t.update_layout(**_pd, yaxis_title="Cumulative Incidents")
        st.plotly_chart(fig_t, use_container_width=True)
    st.stop()

# ── Executive summary ──────────────────────────────────────────────────────────
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
st.markdown(
    '<div style="background:#fff;border:1px solid #D1D5DB;border-radius:16px;padding:22px 26px;margin-bottom:20px">'
    '<div class="section-label" style="margin-bottom:8px">Executive Summary</div>'
    f'<div style="color:#374151;line-height:1.8;font-size:14px;max-height:200px;overflow-y:auto">{html_lib.escape(report["executive_summary"])}</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Predictive alerts ──────────────────────────────────────────────────────────
if report.get("predictive_warnings"):
    st.markdown('<div class="section-label" style="margin-bottom:10px">Predictive Alerts</div>', unsafe_allow_html=True)
    for i, warning in enumerate(report["predictive_warnings"]):
        urgency = "CRITICAL" if i == 0 else "HIGH" if i == 1 else "MEDIUM"
        urgency_color = "#dc2626" if i == 0 else "#d97706" if i == 1 else "#F59E0B"
        st.markdown(
            f'<div class="alert-card"><span style="font-weight:700;margin-right:8px;color:{urgency_color}">{urgency}</span>{html_lib.escape(warning)}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

# ── Pattern charts ─────────────────────────────────────────────────────────────
top_patterns = report.get("top_patterns", [])
if top_patterns:
    col_bar, col_pie = st.columns([2, 1], gap="large")
    chart_colors = ["#ef4444","#f97316","#f59e0b","#eab308","#84cc16"]
    _pd2 = plotly_defaults(260)
    with col_bar:
        render_chart_card_header(f"Recurring Failure Patterns — {len(top_patterns)} found")
        fig = go.Figure(go.Bar(
            x=[p["failure_mode"].replace("_"," ").title() for p in top_patterns],
            y=[p["occurrence_count"] for p in top_patterns],
            marker_color=chart_colors[:len(top_patterns)],
            text=[str(p["occurrence_count"]) for p in top_patterns],
            textposition="outside", textfont=dict(color="#0f172a", size=12, family="Inter,sans-serif"),
            hovertemplate="<b>%{x}</b><br>Occurrences: %{y}<extra></extra>",
        ))
        _pd2_bar = dict(_pd2)
        _pd2_bar["xaxis"] = dict(**_pd2["xaxis"], tickangle=-15)
        fig.update_layout(**_pd2_bar, xaxis_title="Failure Mode", yaxis_title="Occurrences")
        st.plotly_chart(fig, use_container_width=True)

    with col_pie:
        render_chart_card_header("Share by Failure Mode")
        fig_p = go.Figure(go.Pie(
            labels=[p["failure_mode"].replace("_"," ").title() for p in top_patterns],
            values=[p["occurrence_count"] for p in top_patterns],
            hole=0.55, marker_colors=chart_colors[:len(top_patterns)],
            textinfo="percent", textfont=dict(size=11, color="#0f172a"),
            hovertemplate="<b>%{label}</b><br>%{value} occurrences (%{percent})<extra></extra>",
        ))
        _pd2_pie = {k:v for k,v in _pd2.items() if k not in ("xaxis","yaxis","plot_bgcolor","legend","height","margin")}
        fig_p.update_layout(showlegend=True, **_pd2_pie,
            legend=dict(font=dict(size=10, color="#475569"), orientation="v", x=1, y=0.5),
            height=260, margin=dict(t=10, b=10, l=10, r=80))
        st.plotly_chart(fig_p, use_container_width=True)

    for p in top_patterns:
        render_pattern_card(p)
        with st.expander(f"Leading indicators: {p['failure_mode'].replace('_',' ')}"):
            with st.spinner("Analysing…"):
                ind = pa.find_leading_indicators(p["failure_mode"])
            if ind.get("typical_lead_time"):
                st.markdown(f"**Typical lead time:** {ind['typical_lead_time']}")
            for i in ind.get("leading_indicators", []):
                st.markdown(f"- {i}")
            if ind.get("monitoring_recommendation"):
                st.info(ind["monitoring_recommendation"])

# ── Seasonal trends ────────────────────────────────────────────────────────────
seasonal = report.get("seasonal_risks", {})
if seasonal.get("monthly_distribution"):
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    col_sea, col_cal = st.columns([3, 2], gap="large")
    with col_sea:
        monthly = seasonal["monthly_distribution"]
        counts_s = list(monthly.values())
        max_c = max(counts_s) if counts_s else 1
        render_chart_card_header("Seasonal Incident Trends")
        fig2 = go.Figure(go.Bar(
            x=list(monthly.keys()), y=counts_s,
            marker_color=["#ef4444" if c == max_c else "#3b82f6" for c in counts_s],
            text=counts_s, textposition="outside",
            textfont=dict(color="#0f172a", size=12, family="Inter,sans-serif"),
            hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
        ))
        fig2.update_layout(**plotly_defaults(240), yaxis_title="Incidents")
        st.plotly_chart(fig2, use_container_width=True)

    with col_cal:
        st.markdown('<div class="section-label">Seasonal Risk Summary</div>', unsafe_allow_html=True)
        for dot_color, label, period, desc in [
            ("#ef4444", "High Risk",    "June – August",   "Summer heat stress increases seal & bearing failures"),
            ("#F59E0B", "Medium Risk",  "March – May",     "Pre-monsoon dust and temperature swings"),
            ("#10b981", "Low Risk",     "Oct – February",  "Cooler weather, lower failure rates"),
        ]:
            st.markdown(
                f'<div style="padding:11px 16px;background:#fff;border:1px solid #D1D5DB;'
                f'border-radius:12px;margin-bottom:8px;display:flex;align-items:flex-start;gap:10px">'
                f'<div style="width:8px;height:8px;border-radius:50%;background:{dot_color};margin-top:5px;flex-shrink:0"></div>'
                f'<div><div style="font-size:13px;font-weight:700;color:#111827">{label} — {period}</div>'
                f'<div style="font-size:12px;color:#6B7280;margin-top:3px;line-height:1.5">{desc}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        peak = html_lib.escape(seasonal.get("peak_month","Unknown"))
        st.info(f"Peak month: **{peak}** — {html_lib.escape(seasonal.get('analysis',''))}")

# ── Failure prediction tool ────────────────────────────────────────────────────
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-label" style="margin-bottom:6px">Equipment Failure Prediction</div>'
    '<div style="font-size:13px;color:#64748b;margin-bottom:14px">Enter any equipment ID to predict its next failure based on historical patterns.</div>',
    unsafe_allow_html=True,
)
col_eq, col_btn2 = st.columns([2, 1])
with col_eq:
    eq_input = st.text_input("Equipment ID", placeholder="e.g. P-101", label_visibility="collapsed")
with col_btn2:
    predict_clicked = st.button("Predict Next Failure", type="primary", use_container_width=True)

if predict_clicked and eq_input.strip():
    with st.spinner(f"Analysing history for {eq_input}…"):
        pred = pa.predict_next_failure(eq_input.strip())

    conf = pred.get("confidence","Low")
    conf_color = {"High":"#dc2626","Medium":"#d97706","Low":"#059669"}.get(conf,"#475569")
    conf_bg    = {"High":"#fef2f2","Medium":"#fef3c7","Low":"#ecfdf5"}.get(conf,"#f8fafc")
    conf_border= {"High":"#fecaca","Medium":"#fde68a","Low":"#a7f3d0"}.get(conf,"#e2e8f0")

    eq_s      = html_lib.escape(eq_input.strip())
    failure_s = html_lib.escape(pred.get("most_likely_failure","Unknown"))
    timeline_s= html_lib.escape(pred.get("estimated_timeline",""))
    action_s  = html_lib.escape(pred.get("preventive_action",""))

    st.markdown(
        f'<div class="pred-box">'
        f'<div style="font-size:17px;font-weight:700;color:#0f172a;margin-bottom:18px">'
        f'Prediction for <span style="color:#f59e0b">{eq_s}</span></div>'
        f'<div class="pred-grid">'
        f'<div class="pred-cell" style="background:#fff;border-color:#D1D5DB">'
        f'<div style="font-size:10px;color:#dc2626;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:5px;font-weight:700">Most Likely Failure</div>'
        f'<div style="font-size:14px;font-weight:700;color:#111827">{failure_s}</div></div>'
        f'<div class="pred-cell" style="background:#fff;border-color:#D1D5DB">'
        f'<div style="font-size:10px;color:#d97706;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:5px;font-weight:700">Estimated Timeline</div>'
        f'<div style="font-size:14px;font-weight:700;color:#111827">{timeline_s}</div></div>'
        f'<div class="pred-cell" style="background:{conf_bg};border-color:{conf_border}">'
        f'<div style="font-size:10px;color:{conf_color};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:5px;font-weight:700">Confidence</div>'
        f'<div style="font-size:14px;font-weight:700;color:{conf_color}">{conf}</div>'
        f'<div style="font-size:11px;color:#94a3b8;margin-top:3px">Based on {pred.get("history_records",0)} records</div></div>'
        f'</div>'
        f'<div style="background:#FAFAFB;border:1px solid #D1D5DB;border-radius:10px;padding:12px 16px;font-size:13px;color:#374151;margin-bottom:10px">'
        f'<b>Recommended Action:</b> {action_s}</div>'
        f'<div style="background:#FAFAFB;border:1px solid #D1D5DB;border-radius:10px;padding:12px 16px;font-size:12.5px;color:#374151">'
        f'<b>Suggested Work Order:</b> Schedule Preventive Maintenance for {eq_s} within the next 2 weeks. Est. downtime: 4–6 hrs.'
        f'</div></div>',
        unsafe_allow_html=True,
    )


