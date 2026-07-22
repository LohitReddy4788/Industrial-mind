"""IndustrialMind — Enterprise Dashboard. Run: streamlit run run.py"""

import html as html_lib
import streamlit as st

st.set_page_config(
    page_title="IndustrialMind · Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, plotly_defaults, ICONS, logo_img_tag, _LOGO_B64
from app.config import llm_backend, llm_display_name

_LOGO_SRC = ("data:image/png;base64," + _LOGO_B64) if _LOGO_B64 else ""
inject_css(loading_logo=_LOGO_SRC)
sidebar_logo()

with st.sidebar:
    sidebar_nav()

_loading_ph = st.empty()
with _loading_ph.container():
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:center;height:60vh;flex-direction:column;gap:16px">'
        '<div style="font-size:32px">⚙️</div>'
        '<div style="font-size:16px;font-weight:600;color:#374151">Loading IndustrialMind…</div>'
        '<div style="font-size:13px;color:#4C6075">Initializing AI engine, ChromaDB and knowledge graph</div>'
        '</div>',
        unsafe_allow_html=True,
    )

c  = load_for_page(["em", "gb"])
em = c["em"]
gb = c["gb"]

_loading_ph.empty()

# ── Stats ──────────────────────────────────────────────────────────────────────
em_stats    = em.get_stats()
graph_stats = gb.get_stats()
doc_count   = em_stats["total_documents"]
chunk_count = em_stats["total_chunks"]
node_count  = graph_stats.get("nodes", 0)
edge_count  = graph_stats.get("relationships", 0)
llm_name    = llm_display_name()

import plotly.graph_objects as go

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.im-hero{{
  background:linear-gradient(135deg,#111827 0%,#131F30 100%);
  border:1.5px solid #6B7280;
  border-left:4px solid #F59E0B;
  border-radius:14px;
  display:grid;grid-template-columns:1fr 260px;
  align-items:start;
  margin-bottom:20px;
  box-shadow:0 1px 4px rgba(0,0,0,0.07),0 4px 16px rgba(245,158,11,0.06);
  overflow:hidden;
  animation:fadeUp .32s cubic-bezier(.16,1,.3,1);
  position:relative;
}}
.im-hero-left{{padding:24px 28px 22px;}}
.im-hero-right{{
  background:linear-gradient(160deg,#0F1623 0%,#111827 100%);
  border-left:1px solid rgba(255,255,255,0.07);
  padding:24px 28px;display:flex;flex-direction:column;justify-content:space-evenly;gap:0;
}}
.im-hero-badge{{
  display:inline-flex;align-items:center;gap:6px;
  background:#F0FDF4;border:1px solid #BBF7D0;border-radius:99px;
  padding:4px 12px;font-size:10.5px;font-weight:700;color:#166534;letter-spacing:.05em;
  margin-bottom:12px;
}}
.im-hero-badge-dot{{width:6px;height:6px;border-radius:50%;background:#22C55E;animation:dot-pulse 2.5s infinite;}}
.im-hero-title{{
  font-size:2.4rem;font-weight:900;color:#E8EDF5;
  letter-spacing:-0.05em;line-height:1;margin-bottom:10px;
}}
.im-hero-title span{{color:#F59E0B;}}
.im-hero-sub{{font-size:14px;color:#8FA3BE;line-height:1.7;max-width:520px;margin-bottom:18px;}}
.im-hero-sub strong{{color:#E8EDF5;font-weight:600;}}
.im-hero-cta{{display:flex;gap:8px;flex-wrap:wrap;}}
.im-hero-cta-primary,.im-hero-cta-primary:link,.im-hero-cta-primary:visited{{
  display:inline-flex;align-items:center;gap:7px;
  background:linear-gradient(135deg,#F59E0B 0%,#D97706 100%);
  color:#fff !important;font-size:13px;font-weight:600;
  padding:10px 22px;border-radius:8px;text-decoration:none !important;
  box-shadow:0 3px 10px rgba(245,158,11,.35);transition:all .15s;letter-spacing:-.01em;
  border:none;cursor:pointer;
}}
.im-hero-cta-primary:hover{{filter:brightness(1.08);box-shadow:0 6px 20px rgba(245,158,11,.45);transform:translateY(-1px);color:#fff !important;text-decoration:none !important;}}
.im-hero-cta-secondary,.im-hero-cta-secondary:link,.im-hero-cta-secondary:visited{{
  display:inline-flex;align-items:center;gap:7px;
  background:#ffffff;color:#374151 !important;font-size:13px;font-weight:500;
  padding:10px 20px;border-radius:8px;text-decoration:none !important;
  border:1px solid #E4E4E7;transition:all .15s;cursor:pointer;
}}
.im-hero-cta-secondary:hover{{background:#FAFAFB;border-color:#D1D5DB;color:#E8EDF5 !important;text-decoration:none !important;}}
.im-kpi-label{{font-size:10px;font-weight:700;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;}}
.im-kpi-value{{font-size:1.9rem;font-weight:800;color:#FFFFFF;letter-spacing:-.05em;line-height:1;}}
.im-kpi-value.empty{{color:rgba(255,255,255,0.15);font-size:1.4rem;}}
.im-kpi-sub{{font-size:11px;color:rgba(255,255,255,0.3);margin-top:4px;}}
.im-kpi-sep{{height:1px;background:rgba(255,255,255,0.07);}}
</style>
<div class="im-hero">
  <div class="im-hero-left">
    <div class="im-hero-badge">
      <div class="im-hero-badge-dot"></div>
      ET AI Hackathon 2026 &nbsp;&middot;&nbsp; Problem Statement 8
    </div>
    <div class="im-hero-title">Industrial<span>Mind</span></div>
    <div class="im-hero-sub">
      Enterprise AI Operating System for heavy industrial plants &mdash;
      transforms scattered maintenance records, SOPs, regulations &amp; expert knowledge into
      <strong>instant, cited, actionable intelligence.</strong>
    </div>
    <div class="im-hero-cta">
      <a class="im-hero-cta-primary" href="/Copilot" target="_self">Ask AI Copilot</a>
      <a class="im-hero-cta-secondary" href="/Upload" target="_self">Upload Documents</a>
      <a class="im-hero-cta-secondary" href="/Graph" target="_self">Knowledge Graph</a>
    </div>
  </div>
  <div class="im-hero-right">
    <div>
      <div class="im-kpi-label">Documents indexed</div>
      <div class="im-kpi-value" id="hv1">{doc_count}</div>
      <div class="im-kpi-sub">uploaded &amp; embedded</div>
    </div>
    <div class="im-kpi-sep"></div>
    <div>
      <div class="im-kpi-label">Knowledge chunks</div>
      <div class="im-kpi-value" id="hv2">{chunk_count}</div>
      <div class="im-kpi-sub">semantic fragments</div>
    </div>
    <div class="im-kpi-sep"></div>
    <div>
      <div class="im-kpi-label">Graph nodes / edges</div>
      <div class="im-kpi-value" id="hv3">{node_count}</div>
      <div class="im-kpi-sub"><span id="hv4">{edge_count}</span> relationships</div>
    </div>
    <div class="im-kpi-sep"></div>
    <div>
      <div class="im-kpi-label">AI Engine</div>
      <div style="font-size:1rem;font-weight:700;color:#D97706;letter-spacing:-.02em;margin-top:3px">{html_lib.escape(llm_name)}</div>
      <div class="im-kpi-sub">active &amp; responding</div>
    </div>
  </div>
</div>
<script>
(function(){{
  function cnt(el,n,dur){{
    if(!el)return;if(n===0){{el.textContent='0';return;}}
    var s=0,step=n/60,t=dur/60,iv=setInterval(function(){{
      s+=step;if(s>=n){{s=n;clearInterval(iv);}}
      el.textContent=Math.floor(s).toLocaleString();
    }},t);
  }}
  setTimeout(function(){{
    cnt(document.getElementById('hv1'),{doc_count},700);
    cnt(document.getElementById('hv2'),{chunk_count},800);
    cnt(document.getElementById('hv3'),{node_count},900);
    cnt(document.getElementById('hv4'),{edge_count},1000);
  }},200);
}})();
</script>
""", unsafe_allow_html=True)

# ── No-docs banner ─────────────────────────────────────────────────────────────
if chunk_count == 0:
    st.markdown(
        '<div class="warn-banner" style="margin-bottom:20px;display:flex;align-items:center;gap:14px">'
        '<div style="flex-shrink:0;color:#D97706">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
        '</div>'
        '<div><div style="font-size:13.5px;font-weight:600;margin-bottom:2px">No documents loaded yet</div>'
        '<div style="font-size:13px">Go to <a href="/Upload" target="_self" style="color:#D97706;font-weight:600;text-decoration:none">Upload Documents</a> '
        'or run <code>python seed_data.py</code> to load demo data.</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Analytics ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Card-border every column that holds a chart-row-header */
[data-testid="stColumn"]:has(.chart-row-header) {
  background: #111827;
  border: 1.5px solid #D1D5DB;
  border-radius: 14px;
  padding: 20px 20px 14px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 2px 8px rgba(0,0,0,.04);
}
/* Gap between chart-card columns */
[data-testid="stHorizontalBlock"]:has([data-testid="stColumn"]:has(.chart-row-header)) {
  gap: 20px !important;
}
/* Section spacing — more breathing room above/below each row */
.section-label { margin-top: 0; margin-bottom: 18px; }
/* Plotly charts — small top gap inside card */
[data-testid="stColumn"]:has(.chart-row-header) [data-testid="stPlotlyChart"] {
  margin-top: 6px;
}
/* Row spacing between the two chart rows */
[data-testid="stHorizontalBlock"]:has([data-testid="stColumn"]:has(.chart-row-header)) {
  margin-bottom: 20px !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Analytics &amp; Intelligence</div>', unsafe_allow_html=True)

_col_bench, _col_donut, _col_radar = st.columns([5, 3, 3], gap="large")

with _col_bench:
    st.markdown('<div class="chart-row-header">Performance vs Industry Average'
                '<span class="chart-row-header-badge">Illustrative</span></div>',
                unsafe_allow_html=True)
    _cats = ["Knowledge<br>Retrieval","Compliance<br>Checks","Failure<br>Prediction",
             "Work Order<br>Efficiency","Expert<br>Knowledge"]
    _ind  = [32, 54, 28, 65, 12]
    _im   = [94, 87, 78, 91, 85]
    _fig_b = go.Figure()
    _fig_b.add_trace(go.Bar(name="Industry Avg", x=_cats, y=_ind,
        marker_color="#E4E4E7", text=_ind, textposition="auto",
        textfont=dict(color="#4C6075", size=10)))
    _fig_b.add_trace(go.Bar(name="IndustrialMind", x=_cats, y=_im,
        marker=dict(color="#F59E0B", line=dict(color="rgba(0,0,0,0)", width=0)),
        text=_im, textposition="auto", textfont=dict(color="#fff", size=10)))
    _kw = plotly_defaults(240)
    _fig_b.update_layout(
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        **{k: v for k, v in _kw.items() if k not in ("legend", "yaxis", "xaxis")},
        yaxis=dict(gridcolor="#D1D5DB", linecolor="#D1D5DB", zerolinecolor="#D1D5DB",
                   tickfont=dict(size=11, color="#4C6075"), range=[0, 110], ticksuffix="%"),
        xaxis=_kw["xaxis"],
    )
    st.plotly_chart(_fig_b, use_container_width=True)

with _col_donut:
    st.markdown('<div class="chart-row-header">Knowledge Base</div>', unsafe_allow_html=True)
    _dt = em_stats.get("doc_types", {})
    if _dt:
        _fig_d = go.Figure(go.Pie(
            labels=[k.title() for k in _dt.keys()],
            values=list(_dt.values()), hole=0.65,
            marker=dict(colors=["#F59E0B","#3B82F6","#22C55E","#8B5CF6","#8FA3BE"],
                        line=dict(color="#fff", width=2)),
            textinfo="label+percent", textfont=dict(size=10),
        ))
        _fig_d.update_layout(**{k: v for k, v in plotly_defaults(240).items()
                                 if k in ["paper_bgcolor","height","margin","font"]},
                              showlegend=False)
        st.plotly_chart(_fig_d, use_container_width=True)
    else:
        st.markdown(
            '<div style="height:240px;display:flex;align-items:center;justify-content:center;'
            'border:1px solid #D1D5DB;border-radius:18px;background:#FAFAFB">'
            '<div style="text-align:center">'
            '<div style="font-size:13px;color:#4C6075">Upload documents to see composition</div>'
            '</div></div>',
            unsafe_allow_html=True)

with _col_radar:
    st.markdown('<div class="chart-row-header">Plant Risk Radar'
                '<span class="chart-row-header-badge">Illustrative</span></div>',
                unsafe_allow_html=True)
    _rc = ["Pump<br>Systems","Heat<br>Exchangers","Vessels","Electrical","Safety<br>Systems"]
    _rv = [72, 45, 88, 61, 55]
    _fig_r = go.Figure()
    _fig_r.add_trace(go.Scatterpolar(
        r=_rv + [_rv[0]], theta=_rc + [_rc[0]],
        fill="toself", fillcolor="rgba(239,68,68,0.08)",
        line=dict(color="#EF4444", width=2),
        marker=dict(size=5, color="#EF4444"),
    ))
    _fig_r.update_layout(
        polar=dict(bgcolor="#101620",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#D1D5DB",
                            tickfont=dict(size=8, color="#4C6075")),
            angularaxis=dict(gridcolor="#D1D5DB", tickfont=dict(size=9, color="#8FA3BE"))),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        height=240, margin=dict(t=20, b=20, l=30, r=30),
        font=dict(family="Inter", size=11, color="#8FA3BE"),
    )
    st.plotly_chart(_fig_r, use_container_width=True)

# ── ROI + Heatmap ──────────────────────────────────────────────────────────────
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
_col_roi, _col_heat = st.columns([2, 3], gap="large")

with _col_roi:
    st.markdown('<div class="chart-row-header">Monthly Time Savings</div>', unsafe_allow_html=True)
    _months = ["Jan","Feb","Mar","Apr","May","Jun"]
    _fig_roi = go.Figure()
    _fig_roi.add_trace(go.Scatter(x=_months, y=[65]*6, name="Full Potential",
        line=dict(color="#E4E4E7", width=1.5, dash="dot")))
    _fig_roi.add_trace(go.Scatter(x=_months, y=[0,0,12,28,42,58], name="Actual Savings",
        line=dict(color="#3B82F6", width=2.5),
        fill="tonexty", fillcolor="rgba(59,130,246,0.06)",
        mode="lines+markers", marker=dict(size=6, color="#3B82F6", line=dict(color="#fff", width=1.5))))
    _fig_roi.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#101620",
        font=dict(color="#8FA3BE", size=11, family="Inter"),
        height=210, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        yaxis=dict(gridcolor="#D1D5DB", ticksuffix=" hrs", tickfont=dict(size=10, color="#4C6075")),
        xaxis=dict(gridcolor="#D1D5DB", tickfont=dict(size=10, color="#4C6075")),
    )
    st.plotly_chart(_fig_roi, use_container_width=True)
    st.markdown(
        '<div style="background:#F0FDF4;border:1px solid #BBF7D0;'
        'border-radius:8px;padding:10px 14px;font-size:12.5px;color:#166534;display:flex;align-items:center;gap:8px">'
        '<span style="font-weight:600">₹1.45 lakh/month</span> estimated savings @ 58 hrs × ₹2,500/hr'
        '</div>',
        unsafe_allow_html=True,
    )

with _col_heat:
    st.markdown('<div class="chart-row-header">Equipment Failure Heatmap'
                '<span class="chart-row-header-badge">2023–2024</span></div>',
                unsafe_allow_html=True)
    _eqids  = ["P-101","P-102","V-205","E-304","C-401","HE-501"]
    _fmonths = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    _hdata  = [
        [3,1,2,0,1,4,2,1,3,2,1,0],[0,0,1,0,0,1,0,0,2,1,0,1],
        [1,0,0,1,2,1,0,1,0,0,1,2],[2,1,3,1,0,2,1,2,1,0,1,2],
        [0,0,0,0,1,0,0,0,1,0,0,0],[1,2,0,1,1,2,1,3,2,1,0,1],
    ]
    _fig_h = go.Figure(go.Heatmap(
        z=_hdata, x=_fmonths, y=_eqids,
        colorscale=[[0,"#101620"],[0.35,"#1E3A1A"],[0.65,"#7A2020"],[1,"#DC2626"]],
        text=[[str(v) for v in r] for r in _hdata],
        texttemplate="%{text}", textfont=dict(size=10, color="#E8EDF5"),
        showscale=True,
        colorbar=dict(title=dict(text="Failures", font=dict(size=10)),
                      tickfont=dict(size=9), thickness=12),
    ))
    _fig_h.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#101620",
        font=dict(color="#8FA3BE", size=11, family="Inter"),
        height=240, margin=dict(t=10, b=10, l=60, r=10),
        xaxis=dict(side="top", tickfont=dict(size=10, color="#4C6075")),
        yaxis=dict(tickfont=dict(size=10, color="#8FA3BE")),
    )
    st.plotly_chart(_fig_h, use_container_width=True)
    st.markdown(
        '<div style="background:#FAFAFB;border:1px solid #D1D5DB;'
        'border-radius:8px;padding:8px 12px;font-size:12px;color:#8FA3BE">'
        '<span style="color:#EF4444;font-weight:600">P-101 June</span>'
        ' — highest failure rate (4 incidents). Summer months show elevated pump risk.</div>',
        unsafe_allow_html=True,
    )

# ── Platform Modules ───────────────────────────────────────────────────────────
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Platform Modules</div>', unsafe_allow_html=True)

st.markdown("""
<style>
.im-mod-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px;}
@media(max-width:900px){.im-mod-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:480px){.im-mod-grid{grid-template-columns:1fr}}
a.im-mod{text-decoration:none;display:block;}
.im-mod-inner{
  background:#ffffff;border:1.5px solid #D1D5DB;border-radius:12px;
  padding:16px 15px;box-shadow:0 1px 3px rgba(0,0,0,.07),0 2px 6px rgba(0,0,0,.05);
  display:flex;flex-direction:column;gap:9px;height:100%;
  transition:box-shadow .2s,transform .2s,border-color .2s;
}
.im-mod-inner:hover{box-shadow:0 6px 18px rgba(0,0,0,.09);transform:translateY(-2px);border-color:#E4E4E7;}
.im-mod-head{display:flex;align-items:center;gap:10px;}
.im-mod-icon{
  width:36px;height:36px;border-radius:9px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  background:#F9FAFB;border:1.5px solid #D1D5DB;
}
.im-mod-name{font-size:13px;font-weight:700;color:#E8EDF5;letter-spacing:-.01em;}
.im-mod-desc{font-size:11.5px;color:#8FA3BE;line-height:1.6;flex:1;}
.im-mod-footer{display:flex;align-items:center;justify-content:space-between;}
.im-mod-badge{font-size:9px;font-weight:600;padding:2px 8px;border-radius:99px;letter-spacing:.05em;text-transform:uppercase;background:#F9FAFB;color:#4C6075;border:1.5px solid #D1D5DB;}
.im-mod-arrow{
  width:22px;height:22px;border-radius:6px;background:#F9FAFB;
  display:flex;align-items:center;justify-content:center;
  transition:background .2s,transform .2s;border:1.5px solid #D1D5DB;
}
.im-mod-inner:hover .im-mod-arrow{background:#F59E0B;border-color:#F59E0B;transform:translateX(2px);}
.im-mod-inner:hover .im-mod-arrow svg{stroke:#fff;}
</style>
""", unsafe_allow_html=True)

_arrow = '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#4C6075" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'

_modules_r1 = [
    ("/Upload",     "upload",   "Upload Documents",  "Core",   "#3B82F6"),
    ("/Copilot",    "chat",     "AI Copilot",        "LLM",    "#F59E0B"),
    ("/Graph",      "graph",    "Knowledge Graph",   "Graph",  "#8B5CF6"),
    ("/Compliance", "shield",   "Compliance Audit",  "AI",     "#22C55E"),
]
_modules_r2 = [
    ("/Patterns",         "activity", "Failure Patterns",  "ML",     "#EF4444"),
    ("/Work_Orders",      "wrench",   "Work Orders",       "Killer", "#0D9488"),
    ("/Knowledge_Capture","brain",    "Knowledge Capture", "Killer", "#8B5CF6"),
]

_descs = {
    "/Upload": "PDF, Excel, SOP — auto-chunked, embedded, fully searchable.",
    "/Copilot": "Ask anything — every answer cited from your plant documents.",
    "/Graph": "Equipment relationships as an interactive visual graph.",
    "/Compliance": "Semantic gap analysis vs OISD-118, Factory Act, DGMS.",
    "/Patterns": "Recurring failure detection, MTBF, seasonal risk trends.",
    "/Work_Orders": "Auto-generate knowledge briefs the moment a WO is raised.",
    "/Knowledge_Capture": "AI-led expert interviews — preserve tribal knowledge forever.",
}

from app.ui_helpers import ICONS as _ICONS

def _mod_html(href, icon_key, name, badge, color):
    svg = _ICONS.get(icon_key, _ICONS["file"]).replace(
        "stroke=\"currentColor\"", f"stroke=\"{color}\""
    ).replace("width=\"16\"","width=\"17\"").replace("height=\"16\"","height=\"17\"")
    desc = _descs.get(href, "")
    return (
        f'<a href="{href}" target="_self" class="im-mod">'
        f'<div class="im-mod-inner">'
        f'<div class="im-mod-head"><div class="im-mod-icon">{svg}</div>'
        f'<div class="im-mod-name">{name}</div></div>'
        f'<div class="im-mod-desc">{desc}</div>'
        f'<div class="im-mod-footer"><span class="im-mod-badge">{badge}</span>'
        f'<div class="im-mod-arrow">{_arrow}</div></div>'
        f'</div></a>'
    )

r1 = '<div class="im-mod-grid">' + "".join(_mod_html(*m) for m in _modules_r1) + '</div>'
r2 = '<div class="im-mod-grid" style="grid-template-columns:repeat(3,1fr)">' + "".join(_mod_html(*m) for m in _modules_r2) + '</div>'
st.markdown(r1 + r2, unsafe_allow_html=True)

# ── Live Activity Feed ─────────────────────────────────────────────────────────
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Recent Activity</div>', unsafe_allow_html=True)

_activities = [
    ("Knowledge Graph updated", "graph nodes recalculated after document indexing", "2m ago", "#8B5CF6"),
    ("AI Copilot answered question", "Seal replacement procedure for P-101 retrieved", "8m ago", "#F59E0B"),
    ("Compliance audit completed", "3 gaps found vs OISD-118 standard", "14m ago", "#EF4444"),
    ("Work order brief generated", "WO-2026-0867 — P-101 Seal Replacement", "31m ago", "#0D9488"),
    ("Document indexed", "Maintenance_SOP_2026.pdf — 847 chunks created", "1h ago", "#3B82F6"),
    ("Expert interview completed", "Senior Technician — Compressor maintenance captured", "2h ago", "#22C55E"),
]

_act_html = '<div style="background:#ffffff;border:1px solid #D1D5DB;border-radius:14px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08),0 2px 8px rgba(0,0,0,.06);">'
for i, (title, desc, ts, color) in enumerate(_activities):
    border_b = "border-bottom:1px solid #D1D5DB;" if i < len(_activities)-1 else ""
    _act_html += (
        f'<div style="display:flex;align-items:flex-start;gap:14px;padding:14px 20px;{border_b}">'
        f'<div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;margin-top:5px;"></div>'
        f'<div style="flex:1;min-width:0;">'
        f'<div style="font-size:13px;font-weight:600;color:#E8EDF5;margin-bottom:2px">{html_lib.escape(title)}</div>'
        f'<div style="font-size:12px;color:#4C6075">{html_lib.escape(desc)}</div>'
        f'</div>'
        f'<div style="font-size:11px;color:#4C6075;white-space:nowrap;flex-shrink:0">{html_lib.escape(ts)}</div>'
        f'</div>'
    )
_act_html += '</div>'
st.markdown(_act_html, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:40px;padding:20px 24px;border-radius:12px;background:#FAFAFB;
  border:1px solid #D1D5DB;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px">
  <div>
    <div style="font-size:13.5px;font-weight:700;color:#E8EDF5;margin-bottom:3px">IndustrialMind</div>
    <div style="font-size:11.5px;color:#4C6075">ET AI Hackathon 2026 · PS-8 · Streamlit + ChromaDB + Groq Llama 3.3 70B</div>
  </div>
  <div style="display:flex;gap:8px">
    <a href="/Copilot" target="_self" style="font-size:12.5px;font-weight:600;color:#fff;text-decoration:none;
       background:#F59E0B;padding:8px 16px;border-radius:8px;box-shadow:0 3px 10px rgba(245,158,11,.3)">Ask AI Copilot</a>
    <a href="/Upload" target="_self" style="font-size:12.5px;font-weight:500;color:#8FA3BE;text-decoration:none;
       background:#ffffff;border:1px solid #E4E4E7;padding:8px 16px;border-radius:8px">Upload Docs</a>
  </div>
</div>
<div style="height:32px"></div>
""", unsafe_allow_html=True)


