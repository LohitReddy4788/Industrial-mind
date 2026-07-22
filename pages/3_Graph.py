"""Page 3 — Knowledge Graph Explorer."""

import streamlit as st
import streamlit.components.v1 as components
import html as html_lib

st.set_page_config(page_title="Graph · IndustrialMind", page_icon="🕸️", layout="wide", initial_sidebar_state="expanded")

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, loading_screen, render_metric_card, no_docs_warning

inject_css()
sidebar_logo()
with st.sidebar:
    sidebar_nav("Graph")

_lph = loading_screen()
_c  = load_for_page(["gb", "gq"])
gq = _c["gq"]
gb = _c["gb"]
_lph.empty()

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-wrap">'
    '<div class="hero-eyebrow">Relationship Intelligence · Graph Database</div>'
    '<div class="hero-title">Knowledge Graph</div>'
    '<div class="hero-sub">Equipment, incidents, regulations, and procedures — all connected automatically into a living knowledge graph. Click any node to instantly explore its full failure history, related assets, and compliance status.</div>'
    '<div class="hero-divider"></div>'
    '</div>',
    unsafe_allow_html=True,
)

stats    = gq.get_graph_stats()
by_label = stats.get("by_label", {})

# ── Stats ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: render_metric_card("Total Nodes",     str(stats.get("nodes", 0)),         "—",  accent="#2563eb")
with c2: render_metric_card("Relationships",   str(stats.get("relationships", 0)), "—",  accent="#7c3aed")
with c3: render_metric_card("Equipment Nodes", str(by_label.get("Equipment", 0)),  "—",  accent="#F59E0B")
_mode_label = {"NETWORKX": "NetworkX", "NEO4J": "Neo4j", "MEMORY": "In-Memory"}.get(gb.mode.upper(), gb.mode)
with c4: render_metric_card("Storage Mode",    _mode_label,                        "—",  accent="#10b981")

st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

# ── Initialise default state BEFORE any widgets render ─────────────────────────
if "graph_eq" not in st.session_state and stats.get("nodes", 0) > 0:
    st.session_state["graph_eq"]   = "P-101"
    st.session_state["graph_full"] = False

# ── Layout ─────────────────────────────────────────────────────────────────────
col_ctrl, col_graph = st.columns([1, 3], gap="large")

with col_ctrl:
    # ── Explore panel ──────────────────────────────────────────────────────────
    st.markdown(
        '<div class="im-info-card" style="margin-bottom:14px">'
        '<div class="section-label" style="margin-bottom:14px">Explore</div>',
        unsafe_allow_html=True,
    )
    _eq_default = st.session_state.get("graph_eq", "")
    eq_search = st.text_input("Equipment ID", placeholder="P-101, V-205…",
                             value=_eq_default)
    show_full = st.checkbox("Show full graph", value=False)
    if st.button("🔄 Render Graph", type="primary", use_container_width=True):
        st.session_state["graph_eq"]        = eq_search.strip()
        st.session_state["graph_full"]      = show_full
        st.session_state["graph_force_full"] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── High-Risk Equipment panel ───────────────────────────────────────────────
    st.markdown(
        '<div class="im-info-card" style="margin-bottom:14px">'
        '<div class="section-label" style="margin-bottom:12px">High-Risk Equipment</div>',
        unsafe_allow_html=True,
    )
    high_risk = gq.get_high_risk_equipment()
    if high_risk:
        for item in high_risk[:5]:
            eq_id = item["equipment_id"]
            risk  = item["risk_score"]
            inc   = item["incident_count"]
            fail  = item["failure_mode_count"]
            if risk > 4:   risk_color, risk_bg = "#dc2626", "#fef2f2"
            elif risk > 2: risk_color, risk_bg = "#d97706", "#fef3c7"
            else:          risk_color, risk_bg = "#059669", "#ecfdf5"
            st.markdown(
                f'<div style="background:{risk_bg};border:1.5px solid {risk_color}25;border-left:3px solid {risk_color};'
                f'border-radius:10px;padding:10px 14px;margin:0 0 8px;box-shadow:0 1px 3px rgba(0,0,0,0.05)">'
                f'<div style="font-weight:700;font-size:13px;color:{risk_color}">{html_lib.escape(eq_id)}</div>'
                f'<div style="font-size:11px;color:#64748b;margin-top:3px">'
                f'Risk score: <b>{risk}</b> · {inc} incidents · {fail} failure modes</div></div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Focus on {eq_id}", key=f"focus_{eq_id}", use_container_width=True):
                st.session_state["graph_eq"]   = eq_id
                st.session_state["graph_full"] = False
                st.rerun()
    else:
        st.markdown(
            '<div style="font-size:13px;color:#94a3b8;text-align:center;padding:20px 0">'
            'No equipment nodes yet.<br>Upload documents first.</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Legend panel ────────────────────────────────────────────────────────────
    legend = gq.get_legend()
    if legend:
        legend_items = "".join(
            f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0">'
            f'<div style="width:11px;height:11px;border-radius:50%;background:{color};'
            f'flex-shrink:0;box-shadow:0 0 5px {color}66"></div>'
            f'<span style="font-size:12.5px;color:#475569;font-weight:500">{html_lib.escape(label)}</span>'
            f'</div>'
            for label, color in legend.items()
        )
        st.markdown(
            '<div style="background:#fff;border:1px solid #D1D5DB;border-radius:16px;'
            'padding:20px 18px;box-shadow:0 1px 3px rgba(0,0,0,.05)">'
            '<div class="section-label" style="margin-bottom:12px">Legend</div>'
            + legend_items +
            '</div>',
            unsafe_allow_html=True,
        )

with col_graph:
    if stats.get("nodes", 0) == 0:
        st.markdown(
            '<div style="background:#FAFAFB;border:1px solid #D1D5DB;border-radius:18px;'
            'text-align:center;padding:72px 40px;margin-top:8px">'
            '<div style="margin-bottom:20px;opacity:0.3"><svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#111827" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg></div>'
            '<div style="font-size:20px;font-weight:700;color:#111827;margin-bottom:10px;letter-spacing:-0.03em">'
            'Knowledge graph is empty</div>'
            '<div style="font-size:14px;color:#6B7280;max-width:380px;margin:0 auto;line-height:1.75">'
            'Upload maintenance records, SOPs, and incident reports on the '
            '<b>Upload Documents</b> page. Equipment, incidents, regulations and procedures '
            'will be linked automatically as a searchable graph.</div>'
            '<div style="margin-top:24px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">'
            '<div style="background:#fff;border:1px solid #D1D5DB;border-radius:8px;padding:8px 14px;'
            'font-size:12px;color:#374151;font-weight:600">Equipment nodes</div>'
            '<div style="background:#fff;border:1px solid #D1D5DB;border-radius:8px;padding:8px 14px;'
            'font-size:12px;color:#374151;font-weight:600">Incident nodes</div>'
            '<div style="background:#fff;border:1px solid #D1D5DB;border-radius:8px;padding:8px 14px;'
            'font-size:12px;color:#374151;font-weight:600">Regulation nodes</div>'
            '<div style="background:#fff;border:1px solid #D1D5DB;border-radius:8px;padding:8px 14px;'
            'font-size:12px;color:#374151;font-weight:600">Procedure nodes</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        eq_target  = st.session_state.get("graph_eq", "")
        use_full   = st.session_state.get("graph_full", False)
        node_count = stats.get("nodes", 0)
        edge_count = stats.get("relationships", 0)

        # Node/edge count banner
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:16px;background:#FAFAFB;'
            f'border:1px solid #D1D5DB;border-radius:10px;padding:10px 16px;'
            f'font-size:13px;color:#6B7280;margin-bottom:12px">'
            f'<span><b style="color:#111827">{node_count}</b> nodes</span>'
            f'<span style="color:#D1D5DB">|</span>'
            f'<span><b style="color:#111827">{edge_count}</b> edges</span>'
            + (f'<span style="color:#cbd5e1">|</span>'
               f'<span style="color:#d97706;font-weight:600">⚠️ Large graph — use Equipment ID filter for best performance</span>'
               if node_count > 100 and use_full and not eq_target else '')
            + '</div>',
            unsafe_allow_html=True,
        )

        # Guard: full graph with >100 nodes — ask user to confirm or use filter
        _blocked = False
        if node_count > 100 and use_full and not eq_target:
            st.warning(
                f"⚠️ The graph has **{node_count} nodes** — rendering may be slow. "
                "Enter an Equipment ID in the filter and uncheck 'Show full graph' to render a focused subgraph, "
                "or click **Render Graph** again to force full render."
            )
            if not st.session_state.get("graph_force_full"):
                _blocked = True
            else:
                st.session_state["graph_force_full"] = False
        if not _blocked:
            if eq_target and not use_full:
                st.markdown(
                    f'<div style="background:#fff;border:1px solid #D1D5DB;border-left:3px solid #F59E0B;'
                    f'border-radius:10px;padding:10px 16px;font-size:13px;color:#374151;margin-bottom:12px">'
                    f'Showing subgraph for: <b>{html_lib.escape(eq_target)}</b></div>',
                    unsafe_allow_html=True,
                )
                with st.spinner("Rendering subgraph…"):
                    graph_html = gq.get_equipment_subgraph_html(eq_target)
            else:
                st.markdown(
                    '<div style="background:#FAFAFB;border:1px solid #D1D5DB;'
                    'border-radius:10px;padding:10px 16px;font-size:13px;color:#6B7280;margin-bottom:12px">'
                    'Full knowledge graph — click and drag to explore</div>',
                    unsafe_allow_html=True,
                )
                with st.spinner("Rendering graph…"):
                    graph_html = gq.get_full_graph_html()

            if graph_html and len(graph_html) > 200:
                components.html(graph_html, height=520, scrolling=False)
            else:
                st.warning("Graph could not be rendered. Ensure pyvis is installed: `pip install pyvis`")

        if by_label:
            st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label" style="margin-bottom:12px">Node Breakdown</div>', unsafe_allow_html=True)
            NODE_ICONS = {
                "Equipment": "E", "Incident": "I", "Regulation": "R",
                "Procedure": "P", "Person": "Pe", "Document": "D", "FailureMode": "F",
            }
            NODE_COLORS_MAP = {
                "Equipment": "#3b82f6", "Incident": "#ef4444", "Regulation": "#22c55e",
                "Procedure": "#f59e0b", "Person": "#a855f7", "Document": "#64748b",
                "FailureMode": "#f97316",
            }
            label_cols = st.columns(min(len(by_label), 7))
            for i, (label, count) in enumerate(by_label.items()):
                color = NODE_COLORS_MAP.get(label, "#94a3b8")
                icon = NODE_ICONS.get(label, "●")
                with label_cols[i % len(label_cols)]:
                    st.markdown(
                        f'<div style="background:#fff;border:1px solid #D1D5DB;'
                        f'border-top:3px solid {color};border-radius:10px;padding:12px 10px;'
                        f'text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04)">'
                        f'<div style="font-size:10px;font-weight:700;color:{color};margin-bottom:4px;letter-spacing:.05em">{icon}</div>'
                        f'<div style="font-size:22px;font-weight:900;color:#111827;'
                        f'letter-spacing:-0.04em;line-height:1">{count}</div>'
                        f'<div style="font-size:10px;color:#94a3b8;margin-top:4px;'
                        f'text-transform:uppercase;letter-spacing:0.07em;font-weight:600">'
                        f'{label}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


