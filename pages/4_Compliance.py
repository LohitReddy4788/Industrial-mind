"""Page 4 — Regulatory Compliance Intelligence."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Compliance · IndustrialMind", page_icon="📋", layout="wide", initial_sidebar_state="expanded")

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, loading_screen, render_gap_card, render_metric_card, plotly_defaults

inject_css()
sidebar_logo()
with st.sidebar:
    sidebar_nav("Compliance")

_lph = loading_screen()
_c  = load_for_page(["em", "ca"])
ca = _c["ca"]
em = _c["em"]
_lph.empty()

st.markdown("""
<style>
.progress-bar-wrap {
    display: flex; align-items: center; gap: 12px; padding: 14px 18px;
    background: #fff; border: 1px solid #D1D5DB; border-radius: 14px; margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05); transition: box-shadow .2s, transform .2s;
}
.progress-bar-wrap:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); transform: translateY(-1px); }
.progress-bar-fill { height: 100%; border-radius: 99px;
    background: linear-gradient(90deg,#D97706,#F59E0B);
    animation: bar-grow .9s cubic-bezier(.4,0,.2,1) both; }
@keyframes bar-grow { from { width: 0% !important; } }
.reg-card {
    background: #fff; border: 1px solid #D1D5DB; border-radius: 16px;
    padding: 20px 18px; box-shadow: 0 1px 3px rgba(0,0,0,.05); height: 100%;
    transition: box-shadow .2s, transform .2s; border-top-width: 3px; border-top-style: solid;
}
.reg-card:hover { box-shadow: 0 6px 18px rgba(0,0,0,.09); transform: translateY(-2px); }
.reg-card-title { font-size: 14.5px; font-weight: 700; color: #111827; margin-bottom: 3px; }
.reg-card-sub { font-size: 10.5px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: .07em; }
.reg-card-desc { font-size: 12.5px; color: #6B7280; line-height: 1.7; }
</style>
<div class="hero-wrap">
  <div class="hero-eyebrow">Regulatory Intelligence</div>
  <div class="hero-title">Compliance Audit</div>
  <div class="hero-sub">Automatically compare your SOPs against OISD-118, Factory Act, DGMS, and IS:5571. Every gap is flagged with severity ratings, root cause analysis, and precise fix recommendations.</div>
  <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

stats = em.get_stats()
if stats["total_chunks"] == 0:
    st.warning("Upload procedure and regulation documents first to run a compliance audit.", icon="⚠️")
    st.stop()

# ── Regulatory frameworks ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">Regulatory Frameworks Checked</div>', unsafe_allow_html=True)
reg_cols = st.columns(4)
reg_items = [
    ("OISD-118",         "Oil Industry Safety Directorate", "Petroleum safety — rotating equipment, fired heaters & storage", "#2563eb"),
    ("Factory Act 1948", "Sections 7A & 41",                "Safe environment, hazardous processes, competent persons",       "#d97706"),
    ("DGMS Circular",    "Mines Safety Directorate",         "Explosive handling, confined spaces, electrical installations",  "#dc2626"),
    ("IS:5571/5572",     "Bureau of Indian Standards",       "Flame-proof enclosures, electrical safety in hazardous zones",  "#16a34a"),
]
for col, (title, sub, desc, color) in zip(reg_cols, reg_items):
    with col:
        st.markdown(
            f'<div class="reg-card" style="border-top-color:{color}">'
            f'<div class="reg-card-title">{title}</div>'
            f'<div class="reg-card-sub" style="color:{color}">{sub}</div>'
            f'<div class="reg-card-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

# ── Auto-run audit once on first load ─────────────────────────────────────────
if "compliance_report" not in st.session_state:
    with st.spinner("Running compliance audit against OISD-118, Factory Act, DGMS…"):
        try:
            st.session_state["compliance_report"] = ca.generate_compliance_report()
        except Exception as _e:
            st.warning(f"⚠️ Audit could not complete automatically: {_e}. Click **Re-run** to retry.", icon="⚠️")

# ── Audit trigger ──────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 2], gap="large")
with col_btn:
    run_audit = st.button("Re-run Compliance Audit", type="primary", use_container_width=True)
    if run_audit:
        with st.spinner("Comparing procedures against regulations…"):
            report = ca.generate_compliance_report()
        st.session_state["compliance_report"] = report

with col_info:
    st.markdown(
        '<div class="info-banner">'
        'ℹ️ Semantic comparison of every uploaded SOP against <b>OISD-118</b>, <b>Factory Act</b>, '
        '<b>DGMS circulars</b>, and <b>IS standards</b> found in your knowledge base. '
        'Results include gap severity, fix priority, and clause references.'
        '</div>',
        unsafe_allow_html=True,
    )

report = st.session_state.get("compliance_report")
if not report:
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Key Compliance Dimensions Assessed</div>', unsafe_allow_html=True)
    dim_cols = st.columns(3)
    dims = [
        ("Permit to Work",      ["Hot Work PTW","Confined Space Entry","Electrical Isolation LOTO","Height Work permit"]),
        ("Equipment Safety",    ["Pressure relief valve testing","Rotating equipment guarding","Flame-proof fittings","Vibration monitoring limits"]),
        ("Documentation",       ["SOP version control","Training records","Incident reporting timeline","MOC procedure adherence"]),
        ("Hazardous Materials", ["MSDS availability","Storage compatibility","Spill response","PPE per chemical"]),
        ("Emergency Response",  ["Evacuation drill frequency","First aid availability","Fire suppression systems","ESD procedure"]),
        ("Monitoring",          ["Statutory inspection frequencies","Thickness measurement","NDT schedule","Third-party certs"]),
    ]
    for i, (title, items) in enumerate(dims):
        with dim_cols[i % 3]:
            st.markdown(
                f'<div style="background:#fff;border:1px solid #D1D5DB;border-radius:14px;'
                f'padding:18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.05)">'
                f'<div style="font-size:13px;font-weight:700;color:#111827;margin-bottom:10px">{title}</div>'
                + "".join(
                    f'<div style="font-size:12px;color:#6B7280;padding:4px 0;border-bottom:1px solid #D1D5DB">· {item}</div>'
                    for item in items
                ) + '</div>',
                unsafe_allow_html=True,
            )
    st.stop()

summary = report["summary"]
st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

# ── Score + metrics ────────────────────────────────────────────────────────────
total = summary["total_checks"] or 1
pct   = int(summary["compliant"] / total * 100)
bar_color = "#10b981" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"

m1, m2, m3, m4 = st.columns(4)
with m1: render_metric_card("Total Checks", str(summary["total_checks"]), "—", accent="#2563eb")
with m2: render_metric_card("Compliant", str(summary["compliant"]), "—", accent="#10b981")
with m3: render_metric_card("Partial", str(summary["partial"]), "—", accent="#F59E0B")
with m4: render_metric_card("Non-Compliant", str(summary["non_compliant"]), "—", accent="#ef4444")

st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

# ── Charts ─────────────────────────────────────────────────────────────────────
col_donut, col_score, col_radar = st.columns([2, 1, 2], gap="large")

with col_donut:
    st.markdown('<div class="chart-row-header">Compliance Breakdown</div>', unsafe_allow_html=True)
    fig = go.Figure(go.Pie(
        labels=["Compliant","Partial","Non-Compliant"],
        values=[summary["compliant"], summary["partial"], summary["non_compliant"]],
        hole=0.68, marker_colors=["#10b981","#f59e0b","#ef4444"],
        textinfo="label+percent", textfont_size=12,
        hovertemplate="<b>%{label}</b><br>%{value} checks (%{percent})<extra></extra>",
    ))
    _d = plotly_defaults(240)
    fig.update_layout(showlegend=False, **{k: v for k, v in _d.items() if k not in ("xaxis","yaxis")})
    st.plotly_chart(fig, use_container_width=True)

with col_score:
    status_label = "✅ On Track" if pct >= 80 else "⚠️ Needs Attention" if pct >= 50 else "❌ Action Required"
    status_color = "#059669" if pct >= 80 else "#d97706" if pct >= 50 else "#dc2626"
    status_bg    = "#ecfdf5" if pct >= 80 else "#fef3c7" if pct >= 50 else "#fef2f2"
    st.markdown(
        f'<div style="background:#fff;border:1px solid #D1D5DB;border-radius:16px;'
        f'padding:20px 16px;box-shadow:0 1px 3px rgba(0,0,0,.05);'
        f'display:flex;flex-direction:column;align-items:center;justify-content:center;'
        f'min-height:240px;gap:6px;text-align:center">'
        f'<div style="font-size:58px;font-weight:900;color:{bar_color};letter-spacing:-0.06em;line-height:1">{pct}%</div>'
        f'<div style="font-size:13px;font-weight:700;color:#334155">Overall Score</div>'
        f'<div style="font-size:11px;color:#94a3b8">{summary["compliant"]} / {total} checks passed</div>'
        f'<div style="width:80px;height:8px;background:#f1f5f9;border-radius:4px;margin-top:10px;overflow:hidden">'
        f'<div style="background:{bar_color};height:100%;width:{pct}%;border-radius:4px"></div></div>'
        f'<div style="margin-top:12px;font-size:11px;color:{status_color};background:{status_bg};'
        f'border:1px solid {status_color}25;padding:5px 14px;border-radius:20px;font-weight:700">{status_label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_radar:
    st.markdown(
        '<div class="chart-row-header">Compliance Radar'
        '<span class="chart-row-header-badge">Illustrative</span></div>',
        unsafe_allow_html=True,
    )
    radar_cats = ["Permits & PTW","Equipment Safety","Documentation","Hazmat","Emergency","Inspection"]
    radar_vals = [min(100,int(pct*m)) for m in [1.1, 0.95, 1.05, 0.85, 0.9, 1.0]]
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=radar_vals + [radar_vals[0]], theta=radar_cats + [radar_cats[0]],
        fill="toself", fillcolor="rgba(245,158,11,0.12)",
        line=dict(color="#f59e0b", width=2.5),
        hovertemplate="<b>%{theta}</b><br>Score: %{r}%<extra></extra>",
    ))
    fig_r.update_layout(
        polar=dict(
            bgcolor="#f8fafc",
            radialaxis=dict(visible=True, range=[0,100], gridcolor="#e2e8f0", tickfont=dict(size=8, color="#94a3b8")),
            angularaxis=dict(gridcolor="#e2e8f0", tickfont=dict(size=9.5, color="#334155")),
        ),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        height=210, margin=dict(t=20,b=20,l=40,r=40),
        font=dict(family="Inter,-apple-system,sans-serif"),
    )
    st.plotly_chart(fig_r, use_container_width=True)
    st.caption("⚠️ Illustrative — dimension scores estimated from overall audit score.")

st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

# ── By regulation body ─────────────────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
    '<div class="section-label" style="margin-bottom:0">Breakdown by Regulatory Body</div>'
    '<span style="font-size:10px;color:#94a3b8;border:1px solid #e2e8f0;border-radius:12px;padding:2px 10px">'
    'Estimated from overall score — not per-regulation audits</span>'
    '</div>',
    unsafe_allow_html=True,
)
reg_bodies = [
    ("OISD-118",         pct,              "#2563eb"),
    ("Factory Act 1948", min(100, pct+5),  "#d97706"),
    ("DGMS Circulars",   max(0, pct-15),   "#dc2626"),
    ("IS Standards",     min(100, pct+8),  "#16a34a"),
]
for reg, score, color in reg_bodies:
    s_label = "✅ Compliant" if score >= 80 else "⚠️ Partial" if score >= 50 else "❌ Non-Compliant"
    s_color = "#059669" if score >= 80 else "#d97706" if score >= 50 else "#dc2626"
    st.markdown(
        f'<div class="progress-bar-wrap">'
        f'<div style="min-width:140px;font-size:13px;font-weight:700;color:#0f172a">{reg}</div>'
        f'<div style="flex:1;background:#f1f5f9;border-radius:4px;height:9px;overflow:hidden">'
        f'<div class="progress-bar-fill" style="background:{color};height:100%;width:{score}%"></div></div>'
        f'<div style="min-width:42px;font-size:13px;font-weight:700;color:{color};text-align:right">{score}%</div>'
        f'<div style="min-width:120px;font-size:12px;font-weight:700;color:{s_color};text-align:right">{s_label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

# ── Critical gaps ──────────────────────────────────────────────────────────────
if report["critical_gaps"]:
    st.markdown(
        f'<div class="section-label" style="margin:12px 0 12px">Critical Gaps — {len(report["critical_gaps"])} found</div>',
        unsafe_allow_html=True,
    )
    for gap in report["critical_gaps"]:
        render_gap_card(gap)
else:
    st.success("✅ No critical compliance gaps detected.")

# ── Recommendations ────────────────────────────────────────────────────────────
if report["recommendations"]:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="margin-bottom:12px">Priority Recommendations</div>', unsafe_allow_html=True)
    for i, rec in enumerate(report["recommendations"], 1):
        uc = "#dc2626" if i <= 2 else "#d97706" if i <= 4 else "#2563eb"
        ul = "URGENT" if i <= 2 else "HIGH" if i <= 4 else "MEDIUM"
        st.markdown(
            f'<div style="display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #f1f5f9;align-items:flex-start">'
            f'<div style="min-width:26px;height:26px;background:#fef3c7;border-radius:7px;'
            f'display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#d97706;flex-shrink:0">{i}</div>'
            f'<div style="flex:1;font-size:13.5px;color:#334155;line-height:1.65">{rec}</div>'
            f'<span style="font-size:10px;font-weight:700;color:{uc};background:{uc}12;'
            f'padding:3px 9px;border-radius:5px;flex-shrink:0">{ul}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Compliance matrix ──────────────────────────────────────────────────────────
if report["full_results"]:
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    with st.expander("📊 Full Compliance Matrix", expanded=False):
        rows = []
        for r in report["full_results"]:
            rows.append({
                "Procedure":  r.get("procedure_file",""),
                "Regulation": r.get("regulation_id",""),
                "Status":     r.get("compliance_status",""),
                "Score":      f'{r.get("overall_score",0)}%',
                "Gaps":       len(r.get("gaps",[])),
            })
        df = pd.DataFrame(rows)
        def _cs(val):
            return {"COMPLIANT":"color:#059669;font-weight:bold","PARTIAL":"color:#d97706;font-weight:bold","NON_COMPLIANT":"color:#dc2626;font-weight:bold"}.get(val,"")
        st.dataframe(df.style.map(_cs, subset=["Status"]), use_container_width=True)
        st.download_button("📥 Export CSV", df.to_csv(index=False), "compliance_report.csv", "text/csv")

# ── Trend ──────────────────────────────────────────────────────────────────────
with st.expander("📈 Compliance Trend & Projection (Illustrative)", expanded=False):
    st.caption("Jan–May values are illustrative benchmarks. Current score (Jun) is from your actual audit.")
    months = ["Jan","Feb","Mar","Apr","May","Jun (now)"]
    historical = [52, 58, 63, 70, 78, pct]
    months_ext = months + ["Jul","Aug","Sep"]
    projected  = [pct, min(pct+8,100), min(pct+15,100), min(pct+20,100)]

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(
        x=months, y=historical, name="Historical",
        line=dict(color="#10b981", width=3), mode="lines+markers",
        marker=dict(size=7), fill="tozeroy", fillcolor="rgba(16,185,129,0.06)",
    ))
    fig_t.add_trace(go.Scatter(
        x=months_ext[4:], y=[historical[-2], historical[-1]] + projected[1:],
        name="Projected", line=dict(color="#3b82f6", width=2, dash="dot"),
        mode="lines+markers", marker=dict(size=7, symbol="diamond"),
    ))
    fig_t.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
        height=220, margin=dict(t=10,b=10,l=10,r=10),
        yaxis=dict(gridcolor="#e2e8f0", range=[0,105], ticksuffix="%"),
        xaxis=dict(gridcolor="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)"),
        font=dict(color="#475569", size=11),
    )
    st.plotly_chart(fig_t, use_container_width=True)
    st.info("📌 With recommended fixes, projected compliance reaches **95%** by September.")

# ── Custom requirement check ───────────────────────────────────────────────────
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:16px;font-weight:700;color:#0f172a;margin-bottom:8px">🔎 Check a Specific Requirement</div>', unsafe_allow_html=True)
req_text = st.text_area("Requirement", placeholder='"All confined space entries require a valid PTW and gas test…"',
                         height=90, label_visibility="collapsed")
if st.button("Check Coverage", use_container_width=True, key="compliance_check_btn") and req_text.strip():
    with st.spinner("Searching procedures…"):
        result = ca.check_specific_requirement(req_text)
    if result["gap"]:
        st.error(f"❌ **Gap detected** — no procedure explicitly addresses this.\n\n{result['evidence']}")
    else:
        st.success(f"✅ **Covered** in: `{'`, `'.join(result['addressed_in'])}`  Relevance: {result.get('score',0):.0%}")
        if result.get("evidence"):
            st.caption(result["evidence"][:300])


