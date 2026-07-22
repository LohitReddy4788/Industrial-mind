"""Page 2 — AI Copilot (best-possible version)."""

import re
import time as _time
import datetime
import html as _html
import streamlit as st

st.set_page_config(page_title="AI Copilot · IndustrialMind", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, loading_screen
from app.config import llm_display_name
from app.rag import suggest_followups, intent_display

inject_css()
sidebar_logo()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_nav("Copilot")
    st.markdown('<div style="padding:10px 10px 2px">', unsafe_allow_html=True)

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

    _hist = st.session_state.get("chat_history", [])
    if _hist:
        _lines = [
            f"# IndustrialMind — Chat Export\n"
            f"_Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n---"
        ]
        for _m in _hist:
            _r = "**Engineer**" if _m["role"] == "user" else "**IndustrialMind**"
            _lines.append(f"\n{_r}:\n{_m['content']}\n")
        st.download_button(
            "📥 Export as Markdown", "\n".join(_lines),
            f"copilot_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
            "text/markdown", use_container_width=True,
        )
        st.markdown(
            f'<div style="font-size:11px;color:#94a3b8;text-align:center;padding:6px 0">'
            f'{len([m for m in _hist if m["role"]=="user"])} questions · '
            f'{len([m for m in _hist if m["role"]=="assistant"])} answers</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ── Load components ─────────────────────────────────────────────────────────────
_lph = loading_screen()
_c   = load_for_page(["em", "rag"])
rag  = _c["rag"]
em   = _c["em"]
_lph.empty()

stats        = em.get_stats()
total_chunks = stats.get("total_chunks", 0)
total_docs   = stats.get("total_documents", 0)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Page layout */
.main .block-container,
section[data-testid="stMain"] .block-container,
.stMain .block-container,
div.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 6rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: none !important;
    width: 100% !important;
}
section[data-testid="stMain"] > div > div > div {
    max-width: none !important;
    width: 100% !important;
}

/* ── Bottom bar ──────────────────────────────────────────────────────────── */
.stBottom,
.stBottom > div,
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: #ffffff !important;
    border-top: 1px solid #e5e7eb !important;
    padding: 10px 24px 14px !important;
}

/* ── Chat input container ────────────────────────────────────────────────── */
div[data-testid="stChatInput"],
div[data-testid="stChatInput"] *:not(button):not(svg):not(path) {
    background: #ffffff !important;
}
div[data-testid="stChatInput"] {
    border-radius: 10px !important;
    border: 1.5px solid #111827 !important;
    box-shadow: none !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 auto !important;
    transition: border-color .15s !important;
    overflow: hidden !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #374151 !important;
    box-shadow: 0 0 0 3px rgba(17,24,39,0.06) !important;
}
div[data-testid="stChatInput"] > div {
    background: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
}

/* Textarea */
div[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    color: #111827 !important;
    font-size: 14px !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    padding: 14px 16px !important;
    line-height: 1.6 !important;
    -webkit-text-fill-color: #111827 !important;
    caret-color: #111827 !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #9ca3af !important;
    font-size: 13.5px !important;
    -webkit-text-fill-color: #9ca3af !important;
}

/* ── Send button ─────────────────────────────────────────────────────────── */
div[data-testid="stChatInput"] button {
    background: transparent !important;
    border-radius: 0 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    margin: 4px 6px !important;
    flex-shrink: 0 !important;
    transition: opacity .15s, transform .1s !important;
    padding: 0 !important;
}
div[data-testid="stChatInput"] button:hover {
    background: transparent !important;
    opacity: 0.6 !important;
    transform: scale(1.12) !important;
}
div[data-testid="stChatInput"] button svg {
    stroke: #000000 !important;
    fill: #000000 !important;
    width: 28px !important;
    height: 28px !important;
}
div[data-testid="stChatInput"] button svg path,
div[data-testid="stChatInput"] button svg polyline,
div[data-testid="stChatInput"] button svg line {
    stroke: #000000 !important;
    fill: #000000 !important;
}
div[data-testid="stChatInput"] button svg rect {
    display: none !important;
}

/* ── Chat Bubbles ───────────────────────────────────────────────────────── */
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    border-radius: 18px 18px 6px 18px !important;
    border: 1px solid #e2e8f0 !important;
    margin-left: 48px !important;
    padding: 14px 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(15,23,42,0.04) !important;
}
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #ffffff !important;
    border-radius: 6px 18px 18px 18px !important;
    border: 1px solid #e2e8f0 !important;
    margin-right: 48px !important;
    padding: 16px 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(15,23,42,0.04) !important;
}

/* Chat text */
.stChatMessage p { font-size: 14.5px !important; line-height: 1.75 !important; color: #1e293b !important; }
.stChatMessage h3 { font-size: 15px !important; font-weight: 700 !important; }
.stChatMessage li { font-size: 14.5px !important; line-height: 1.7 !important; }
.stChatMessage strong { font-weight: 700 !important; color: #0f172a !important; }
.stChatMessage code {
    background: #f1f5f9 !important; border-radius: 5px !important;
    padding: 2px 7px !important; font-size: 13px !important;
    border: 1px solid #e2e8f0 !important;
}

/* ── Expander ───────────────────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
    margin-top: 10px !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] summary {
    font-size: 12.5px !important;
    font-weight: 600 !important;
    color: #475569 !important;
}

/* ── Follow-up chips ────────────────────────────────────────────────────── */
div[data-testid="stChatMessage"] [data-testid="stBaseButton-secondary"] {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #334155 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-align: left !important;
    min-height: 46px !important;
    height: auto !important;
    padding: 9px 13px !important;
    box-shadow: 0 1px 4px rgba(15,23,42,.05) !important;
    transition: all .15s ease !important;
    white-space: normal !important;
    line-height: 1.4 !important;
}
div[data-testid="stChatMessage"] [data-testid="stBaseButton-secondary"]:hover {
    background: #eef2ff !important;
    border-color: #a5b4fc !important;
    color: #4338ca !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.15) !important;
}

/* ── Welcome suggestion buttons ─────────────────────────────────────────── */
div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]
  div[data-testid="stColumn"] [data-testid="stBaseButton-secondary"] {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 14px !important;
    color: #334155 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-align: left !important;
    min-height: 76px !important;
    height: auto !important;
    padding: 14px 18px !important;
    box-shadow: 0 2px 8px rgba(15,23,42,.06) !important;
    transition: all .18s ease !important;
    line-height: 1.55 !important;
    white-space: normal !important;
}
div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]
  div[data-testid="stColumn"] [data-testid="stBaseButton-secondary"]:hover {
    background: #fafafa !important;
    border-color: #a5b4fc !important;
    color: #1e1b4b !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.15) !important;
    transform: translateY(-3px) !important;
}

/* ── Animations ─────────────────────────────────────────────────────────── */
@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 1; }
    30%           { transform: translateY(-5px); opacity: 0.6; }
}
@keyframes im-fade-in {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 0 3.5px rgba(99,102,241,0.12), 0 16px 40px rgba(99,102,241,0.14); }
    50%       { box-shadow: 0 0 0 5px rgba(99,102,241,0.18), 0 20px 48px rgba(99,102,241,0.2); }
}
.im-chat-meta { animation: im-fade-in .3s ease both; }

/* Mobile */
@media (max-width: 768px) {
    .main .block-container { max-width: 100% !important; }
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) { margin-left: 10px !important; }
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) { margin-right: 10px !important; }
    div[data-testid="stChatInput"] textarea { padding-left: 40px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
_total_docs = stats.get("total_documents", 0)
_llm_name   = llm_display_name()

st.markdown(f"""
<style>
.im-cop-header{{
  background:linear-gradient(135deg,#ffffff 0%,#FFFBF0 100%);
  border:1px solid #D1D5DB;
  border-top:none;
  border-left:4px solid #F59E0B;
  border-radius:18px;
  padding:0;margin-bottom:18px;overflow:hidden;
  box-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 12px rgba(245,158,11,.06);
  animation:fadeUp .38s cubic-bezier(.16,1,.3,1);
  position:relative;
}}
.im-cop-main{{padding:22px 32px 20px;}}
.im-cop-eyebrow{{
  display:inline-flex;align-items:center;gap:7px;
  font-size:10.5px;font-weight:700;color:#d97706;
  text-transform:uppercase;letter-spacing:.14em;margin-bottom:16px;
  background:#fffbeb;border:1px solid #fde68a;
  padding:4px 13px;border-radius:99px;
}}
.im-cop-title{{
  font-size:2rem;font-weight:900;color:#0f172a;letter-spacing:-.045em;
  line-height:1.1;margin-bottom:12px;
}}
.im-cop-meta{{
  display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin-bottom:16px;
}}
.im-cop-meta-item{{font-size:12px;color:#64748b;display:flex;align-items:center;gap:5px;font-weight:500}}
.im-cop-meta-dot{{width:7px;height:7px;border-radius:50%;background:#22c55e;
  box-shadow:0 0 0 3px rgba(34,197,94,.2);animation:dot-pulse 2.5s infinite}}
.im-cop-sub{{font-size:14px;color:#64748b;line-height:1.78;max-width:600px;margin-bottom:16px}}
.im-cop-pills{{display:flex;gap:7px;flex-wrap:wrap}}
.im-cop-pill{{
  display:inline-flex;align-items:center;gap:5px;
  font-size:11px;font-weight:600;padding:4px 12px;border-radius:99px;
}}
</style>
<div class="im-cop-header">
  <div class="im-cop-main">
    <div class="im-cop-eyebrow">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
      Killer Feature &middot; AI Engine
    </div>
    <div style="display:flex;align-items:flex-start;gap:16px">
      <div style="width:48px;height:48px;border-radius:12px;flex-shrink:0;
        background:#FAFAFB;border:1px solid #D1D5DB;
        display:flex;align-items:center;justify-content:center;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </div>
      <div style="flex:1">
        <div class="im-cop-title">AI Knowledge Copilot</div>
        <div class="im-cop-meta">
          <div class="im-cop-meta-item"><div class="im-cop-meta-dot"></div><span style="color:#059669;font-weight:600">Live</span></div>
          <div class="im-cop-meta-item">{_llm_name}</div>
          <div class="im-cop-meta-item" style="color:#059669;font-weight:600">
            {total_chunks:,} chunks indexed
          </div>
          <div class="im-cop-meta-item">{_total_docs} documents</div>
        </div>
      </div>
    </div>
    <div class="im-cop-sub">
      Instant answers from your plant's own documents — maintenance logs, incident reports, SOPs,
      and regulations. Every response is <b style="color:#0f172a">cited</b> and fully <b style="color:#0f172a">traceable</b>.
    </div>
    <div class="im-cop-pills">
      <span class="im-cop-pill" style="background:#fff;color:#374151;border:1px solid #D1D5DB">Root Cause Analysis</span>
      <span class="im-cop-pill" style="background:#fff;color:#374151;border:1px solid #D1D5DB">Procedures</span>
      <span class="im-cop-pill" style="background:#fff;color:#374151;border:1px solid #D1D5DB">Compliance</span>
      <span class="im-cop-pill" style="background:#fff;color:#374151;border:1px solid #D1D5DB">Maintenance</span>
      <span class="im-cop-pill" style="background:#fff;color:#374151;border:1px solid #D1D5DB">Prediction</span>
      <span class="im-cop-pill" style="background:#fff;color:#374151;border:1px solid #D1D5DB">Visual Analysis</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── No docs warning ─────────────────────────────────────────────────────────────
if total_chunks == 0:
    st.markdown("""
    <div style="background:#fff;border:1px solid #D1D5DB;border-radius:16px;padding:28px 32px;text-align:center;margin:20px 0">
      <div style="margin-bottom:12px"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
      <div style="font-size:18px;font-weight:700;color:#111827;margin-bottom:8px">No documents indexed yet</div>
      <div style="font-size:14px;color:#64748b;margin-bottom:18px">
        Upload maintenance logs, incident reports, SOPs, and regulations to unlock the AI Copilot.</div>
      <a href="/Upload" target="_self"
         style="display:inline-block;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;
         font-size:13px;font-weight:700;padding:10px 24px;border-radius:10px;text-decoration:none;
         box-shadow:0 4px 14px rgba(245,158,11,.35)">📤 Upload Documents →</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Welcome / empty state ────────────────────────────────────────────────────────
if not st.session_state["chat_history"]:
    st.markdown("""
<style>
.im-welcome-hero{
  text-align:center;padding:36px 24px 20px;animation:fadeUp .35s ease;
}
.im-welcome-logo{
  width:110px;height:110px;margin:0 auto 20px;
  display:flex;align-items:center;justify-content:center;
  filter:drop-shadow(0 12px 32px rgba(245,158,11,.45));
}
.im-welcome-title{
  font-size:28px;font-weight:900;color:#0f172a;letter-spacing:-.04em;margin-bottom:10px;
}
.im-welcome-sub{
  font-size:14.5px;color:#64748b;max-width:700px;margin:0 auto 28px;line-height:1.75;
}
</style>
<div class="im-welcome-hero">
  <div class="im-welcome-logo">
    <svg width="110" height="110" viewBox="0 0 110 110" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="wbg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#FCD34D"/>
          <stop offset="100%" style="stop-color:#D97706"/>
        </linearGradient>
        <linearGradient id="weye" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:#FFF3C4"/>
          <stop offset="100%" style="stop-color:#F59E0B"/>
        </linearGradient>
        <linearGradient id="whi" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:rgba(255,255,255,0.22)"/>
          <stop offset="100%" style="stop-color:rgba(255,255,255,0)"/>
        </linearGradient>
      </defs>
      <!-- Card -->
      <rect width="110" height="110" rx="26" fill="url(#wbg)"/>
      <!-- Highlight -->
      <rect x="4" y="4" width="102" height="52" rx="23" fill="url(#whi)"/>
      <!-- Antenna stem -->
      <rect x="53" y="10" width="4" height="18" rx="2" fill="white" opacity="0.92"/>
      <!-- Antenna ball -->
      <circle cx="55" cy="9" r="6" fill="white"/>
      <circle cx="53" cy="7" r="2.5" fill="rgba(255,255,255,0.55)"/>
      <!-- Pulse ring -->
      <circle cx="55" cy="9" r="9" fill="none" stroke="white" stroke-width="1" opacity="0.35"/>
      <!-- Robot head -->
      <rect x="22" y="26" width="66" height="40" rx="12" fill="white"/>
      <!-- Left eye socket -->
      <rect x="31" y="34" width="19" height="14" rx="5" fill="#1E293B"/>
      <!-- Right eye socket -->
      <rect x="60" y="34" width="19" height="14" rx="5" fill="#1E293B"/>
      <!-- Eye amber fill -->
      <rect x="33" y="36" width="15" height="10" rx="3.5" fill="url(#weye)"/>
      <rect x="62" y="36" width="15" height="10" rx="3.5" fill="url(#weye)"/>
      <!-- Eye shine -->
      <circle cx="37" cy="39" r="2.5" fill="white" opacity="0.9"/>
      <circle cx="66" cy="39" r="2.5" fill="white" opacity="0.9"/>
      <!-- Smile / grille dots -->
      <circle cx="41" cy="57" r="2" fill="#F59E0B" opacity="0.7"/>
      <circle cx="55" cy="57" r="2" fill="#F59E0B" opacity="0.7"/>
      <circle cx="69" cy="57" r="2" fill="#F59E0B" opacity="0.7"/>
      <rect x="34" y="55" width="42" height="4" rx="2" fill="#E2E8F0" opacity="0.5"/>
      <!-- Neck -->
      <rect x="50" y="66" width="10" height="9" rx="3" fill="white" opacity="0.88"/>
      <!-- Body -->
      <rect x="18" y="74" width="74" height="27" rx="12" fill="white"/>
      <!-- Gear (left side of body) -->
      <circle cx="34" cy="87" r="8" fill="none" stroke="#F59E0B" stroke-width="2.8"/>
      <circle cx="34" cy="87" r="3.5" fill="#F59E0B"/>
      <line x1="34" y1="78" x2="34" y2="80.5" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
      <line x1="34" y1="93.5" x2="34" y2="96" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
      <line x1="25" y1="87" x2="27.5" y2="87" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
      <line x1="40.5" y1="87" x2="43" y2="87" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
      <line x1="27.4" y1="80.4" x2="29.2" y2="82.2" stroke="#F59E0B" stroke-width="2" stroke-linecap="round"/>
      <line x1="38.8" y1="91.8" x2="40.6" y2="93.6" stroke="#F59E0B" stroke-width="2" stroke-linecap="round"/>
      <!-- Chat lines (right side of body) -->
      <rect x="50" y="80" width="34" height="3" rx="1.5" fill="#CBD5E1"/>
      <rect x="50" y="86" width="26" height="3" rx="1.5" fill="#CBD5E1"/>
      <rect x="50" y="92" width="20" height="3" rx="1.5" fill="#F59E0B" opacity="0.6"/>
      <!-- Connector dots -->
      <circle cx="13" cy="22" r="2.5" fill="white" opacity="0.35"/>
      <circle cx="97" cy="22" r="2.5" fill="white" opacity="0.35"/>
      <circle cx="13" cy="88" r="2" fill="white" opacity="0.25"/>
      <circle cx="97" cy="88" r="2" fill="white" opacity="0.25"/>
    </svg>
  </div>
  <div class="im-welcome-title">Ask me anything about your plant</div>
  <div class="im-welcome-sub">
    I've read every document in your knowledge base. Ask about a specific pump, a past incident,
    a regulation, or a procedure — every answer is <b>cited</b> with the exact source.
  </div>
</div>
""", unsafe_allow_html=True)

    _categories = [
        {
            "label": "Root Cause Analysis",
            "color": "#dc2626",
            "prompts": [
                ("What are the critical failure modes for P-101 and root cause of the last failure?"),
                ("Summarise all incidents with mechanical seal failures and find the pattern."),
            ]
        },
        {
            "label": "Procedures & Safety",
            "color": "#7c3aed",
            "prompts": [
                ("Walk me through the SOP for confined space entry step by step."),
                ("What PPE, PTW, and LOTO requirements apply to hot work on a compressor?"),
            ]
        },
        {
            "label": "Compliance",
            "color": "#2563eb",
            "prompts": [
                ("Are we compliant with OISD-118 rotating equipment requirements? List any gaps."),
                ("What are our obligations under the Factories Act for pressure vessel inspection?"),
            ]
        },
        {
            "label": "Maintenance & Prediction",
            "color": "#d97706",
            "prompts": [
                ("What maintenance history do we have for E-304 and is it due for an overhaul?"),
                ("Which equipment is at highest risk of failure in the next 3 months?"),
            ]
        },
    ]

    _all_prompts_flat = []
    for _cat in _categories:
        for _text in _cat["prompts"]:
            _all_prompts_flat.append((_text, _cat["color"], _cat["label"]))

    _cat_icons = {
        "Root Cause Analysis":    "🔴",
        "Procedures & Safety":    "🛡️",
        "Compliance":             "📜",
        "Maintenance & Prediction": "🔧",
    }
    _sq_cols = st.columns(2)
    for _pi, (_text, _color, _cat_label) in enumerate(_all_prompts_flat):
        with _sq_cols[_pi % 2]:
            _icon = _cat_icons.get(_cat_label, "●")
            if st.button(
                f"**{_icon} {_cat_label}**\n\n{_text}",
                key=f"sq_{_pi}",
                use_container_width=True,
            ):
                st.session_state["chat_history"].append({"role": "user", "content": _text})
                st.rerun()

# ── Helper functions ─────────────────────────────────────────────────────────────
_DOC_TYPE_CFG = {
    "maintenance": ("M", "#d97706", "#fff", "#D1D5DB"),
    "incidents":   ("I", "#dc2626", "#fff", "#D1D5DB"),
    "procedures":  ("P", "#7c3aed", "#fff", "#D1D5DB"),
    "regulations": ("R", "#2563eb", "#fff", "#D1D5DB"),
}
_INTENT_BADGE_CFG = {
    "rca":         ("#dc2626", "#fef2f2", "#fecaca", "🔴 RCA"),
    "procedure":   ("#7c3aed", "#faf5ff", "#ddd6fe", "📋 Procedure"),
    "regulation":  ("#2563eb", "#eff6ff", "#bfdbfe", "📜 Compliance"),
    "safety":      ("#d97706", "#fffbeb", "#fde68a", "⚠️ Safety"),
    "maintenance": ("#d97706", "#fffbeb", "#fde68a", "🔧 Maintenance"),
    "prediction":  ("#7c3aed", "#faf5ff", "#ddd6fe", "🔮 Predictive"),
    "failure":     ("#dc2626", "#fef2f2", "#fecaca", "⚡ Failure Mode"),
    "general":     ("#475569", "#f8fafc", "#e2e8f0", "💬 General"),
}
_EQ_BLOCKLIST = {"API", "ISO", "SOP", "PPE", "PTW", "LNG", "LPG", "RPM", "PSI", "OISD", "DGMS", "IBR"}


def _render_sources(sources: list) -> None:
    for s in sources[:8]:
        fname     = s.get("source_file", "").replace("\\", "/").split("/")[-1] or "Unknown"
        doc_type  = s.get("doc_type", "general")
        score     = int(s.get("combined_score", s.get("score", 0)) * 100)
        page      = s.get("page_num", "?")
        preview   = _html.escape(s.get("text", "")[:150].strip().replace("\n", " "))
        icon, color, bg, border = _DOC_TYPE_CFG.get(doc_type, ("📄", "#64748b", "#f8fafc", "#e2e8f0"))
        bar_color = "#10b981" if score >= 68 else "#f59e0b" if score >= 42 else "#94a3b8"
        st.markdown(
            f'<div style="padding:10px 14px;border:1.5px solid {border};border-left:3px solid {color};'
            f'border-radius:10px;margin-bottom:8px;background:{bg}">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
            f'<span style="font-size:15px">{icon}</span>'
            f'<span style="font-size:12.5px;font-weight:700;color:#0f172a;flex:1">{_html.escape(fname)}</span>'
            f'<span style="font-size:10.5px;color:#94a3b8">p.{page}</span>'
            f'<span style="font-size:11px;font-weight:700;color:{bar_color};background:#fff;'
            f'border-radius:6px;padding:1px 8px">{score}%</span>'
            f'</div>'
            f'<div style="background:#e2e8f0;border-radius:3px;height:3px;margin-bottom:8px;overflow:hidden">'
            f'<div style="background:{bar_color};height:100%;width:{score}%;border-radius:3px;'
            f'transition:width .6s ease"></div></div>'
            f'<div style="font-size:11.5px;color:#475569;line-height:1.6;font-style:italic">"{preview}…"</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _meta_bar(confidence: float, intent: str, response_time: float, n_sources: int) -> str:
    """Build the metadata bar HTML shown below each assistant response."""
    parts = []

    # Confidence pill
    if confidence >= 0.65:
        parts.append('<span style="font-size:11px;font-weight:700;color:#059669;background:#ecfdf5;'
                     'border:1px solid #a7f3d0;padding:2px 10px;border-radius:20px">● High confidence</span>')
    elif confidence >= 0.38:
        parts.append('<span style="font-size:11px;font-weight:700;color:#d97706;background:#fffbeb;'
                     'border:1px solid #fde68a;padding:2px 10px;border-radius:20px">● Medium confidence</span>')
    elif confidence > 0:
        parts.append('<span style="font-size:11px;font-weight:700;color:#94a3b8;background:#f8fafc;'
                     'border:1px solid #e2e8f0;padding:2px 10px;border-radius:20px">● Low confidence</span>')

    # Intent badge
    if intent and intent != "general":
        c, bg, bd, lbl = _INTENT_BADGE_CFG.get(intent, _INTENT_BADGE_CFG["general"])
        parts.append(f'<span style="font-size:11px;font-weight:700;color:{c};background:{bg};'
                     f'border:1px solid {bd};padding:2px 10px;border-radius:20px">{lbl}</span>')

    # Stats
    if n_sources:
        parts.append(f'<span style="font-size:11px;color:#94a3b8">{n_sources} sources</span>')
    if response_time:
        parts.append(f'<span style="font-size:11px;color:#94a3b8">{response_time:.1f}s</span>')

    return (
        '<div class="im-chat-meta" style="display:flex;gap:8px;flex-wrap:wrap;'
        'align-items:center;margin-top:10px;padding-top:10px;'
        'border-top:1px solid #f1f5f9">' + " ".join(parts) + '</div>'
    )


def _equipment_action_bar(answer: str) -> list:
    """Extract equipment IDs from answer and return quick-action chips."""
    eq_ids = [e for e in re.findall(r'\b[A-Z]{1,4}-\d{2,4}[A-Z]?\b', answer)
              if e not in _EQ_BLOCKLIST]
    return list(dict.fromkeys(eq_ids))[:3]


def _render_followups(followups: list, key_prefix: str) -> None:
    if not followups:
        return
    st.markdown(
        '<div style="margin-top:12px;font-size:10.5px;color:#94a3b8;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">Continue exploring →</div>',
        unsafe_allow_html=True,
    )
    _cols = st.columns(min(len(followups), 2))
    for _fi, _fq in enumerate(followups):
        with _cols[_fi % 2]:
            if st.button(_fq, key=f"{key_prefix}_{_fi}", use_container_width=True):
                st.session_state["chat_history"].append({"role": "user", "content": _fq})
                st.rerun()


# ── Chat history ─────────────────────────────────────────────────────────────────
_all_msgs = st.session_state["chat_history"]
for _mi, _msg in enumerate(_all_msgs):
    _role    = _msg["role"]
    _content = _msg["content"]
    _avatar  = "🧑" if _role == "user" else "🤖"
    _is_last = (_mi == len(_all_msgs) - 1)

    with st.chat_message(_role, avatar=_avatar):
        st.markdown(_content)

        if _role == "assistant":
            _conf  = _msg.get("confidence", 0.0)
            _intent = _msg.get("intent", "general")
            _rtime  = _msg.get("response_time", 0.0)
            _srcs   = _msg.get("sources", [])
            _meta   = _meta_bar(_conf, _intent, _rtime, len(_srcs))
            st.markdown(_meta, unsafe_allow_html=True)

            if _srcs:
                with st.expander(f"📚 {len(_srcs)} source document(s) cited", expanded=False):
                    _render_sources(_srcs)

            # Equipment quick-actions for last message
            if _is_last and _content and not _content.startswith("⚠️"):
                _eq_ids = _equipment_action_bar(_content)
                if _eq_ids:
                    st.markdown(
                        '<div style="margin-top:8px;font-size:10.5px;color:#94a3b8;font-weight:700;'
                        'text-transform:uppercase;letter-spacing:0.08em">Equipment in this answer →</div>',
                        unsafe_allow_html=True,
                    )
                    _eq_cols = st.columns(min(len(_eq_ids) * 2, 6))
                    for _ei, _eq in enumerate(_eq_ids):
                        with _eq_cols[_ei * 2]:
                            st.markdown(
                                f'<a href="/Graph" target="_self" style="display:block;'
                                f'background:#FAFAFB;border:1px solid #D1D5DB;border-radius:8px;'
                                f'padding:6px 10px;font-size:11.5px;font-weight:700;color:#334155;'
                                f'text-decoration:none;text-align:center">{_html.escape(_eq)} in Graph</a>',
                                unsafe_allow_html=True,
                            )
                        with _eq_cols[_ei * 2 + 1]:
                            st.markdown(
                                f'<a href="/Work_Orders" target="_self" style="display:block;'
                                f'background:#FAFAFB;border:1px solid #D1D5DB;border-radius:8px;'
                                f'padding:6px 10px;font-size:11.5px;font-weight:700;color:#334155;'
                                f'text-decoration:none;text-align:center">{_html.escape(_eq)} Work Order</a>',
                                unsafe_allow_html=True,
                            )

                _fups = _msg.get("followups", [])
                if not _fups:
                    _fups = suggest_followups(_content, _all_msgs[_mi - 1]["content"] if _mi > 0 else "", _intent)
                _render_followups(_fups, f"fq_{_mi}")

# ── Shared thinking indicator ──────────────────────────────────────────────────
def _thinking(ph, step: str, detail: str = "") -> None:
    ph.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:10px 0;font-size:13px;color:#64748b">'
        f'<span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;'
        f'animation:typing-bounce 1.3s ease infinite;flex-shrink:0"></span>'
        f'<span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;'
        f'animation:typing-bounce 1.3s ease .22s infinite;flex-shrink:0"></span>'
        f'<span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;'
        f'animation:typing-bounce 1.3s ease .44s infinite;flex-shrink:0"></span>'
        f'&nbsp;<span style="font-weight:600;color:#334155">{step}</span>'
        + (f'<span style="color:#94a3b8;font-size:11.5px">&nbsp;— {detail}</span>' if detail else '')
        + '</div>',
        unsafe_allow_html=True,
    )


def _post_answer(answer: str, sources: list, confidence: float,
                 intent_str: str, response_time: float, prompt_text: str) -> None:
    """Render metadata, sources, equipment links, follow-ups after an answer."""
    if not answer or answer.startswith("⚠️"):
        if answer.startswith("⚠️"):
            if st.button("🔄 Retry", key=f"retry_{len(st.session_state['chat_history'])}"):
                st.session_state["chat_history"] = st.session_state["chat_history"][:-2]
                st.rerun()
        return

    st.markdown(_meta_bar(confidence, intent_str, response_time, len(sources)), unsafe_allow_html=True)

    if sources:
        with st.expander(f"📚 {len(sources)} source document(s) cited", expanded=False):
            _render_sources(sources)

    _eq_ids = _equipment_action_bar(answer)
    if _eq_ids:
        st.markdown(
            '<div style="margin-top:8px;font-size:10.5px;color:#94a3b8;font-weight:700;'
            'text-transform:uppercase;letter-spacing:0.08em">Equipment in this answer →</div>',
            unsafe_allow_html=True,
        )
        _ea_cols = st.columns(min(len(_eq_ids) * 2, 6))
        for _ei, _eq in enumerate(_eq_ids):
            with _ea_cols[_ei * 2]:
                st.markdown(
                    f'<a href="/Graph" target="_self" style="display:block;background:#fff;'
                    f'border:1px solid #D1D5DB;border-radius:8px;padding:6px 10px;'
                    f'font-size:11.5px;font-weight:700;color:#374151;text-decoration:none;text-align:center">'
                    f'{_html.escape(_eq)} in Graph</a>', unsafe_allow_html=True,
                )
            with _ea_cols[_ei * 2 + 1]:
                st.markdown(
                    f'<a href="/Work_Orders" target="_self" style="display:block;background:#fff;'
                    f'border:1px solid #D1D5DB;border-radius:8px;padding:6px 10px;'
                    f'font-size:11.5px;font-weight:700;color:#374151;text-decoration:none;text-align:center">'
                    f'{_html.escape(_eq)} Work Order</a>', unsafe_allow_html=True,
                )

    _fups = suggest_followups(answer, prompt_text, intent_str)
    _render_followups(_fups, "fq_new")


# ── Image upload panel (above chat input) ──────────────────────────────────────
st.markdown("""
<style>
/* Vision upload panel */
.vision-panel {
    background: linear-gradient(135deg,#fffbeb,#fff7ed);
    border: 1.5px solid #fde68a;
    border-radius: 16px;
    padding: 18px 22px 14px;
    margin-bottom: 14px;
    position: relative;
}
.vision-severity-critical { color:#dc2626;background:#fef2f2;border:1px solid #fecaca;
    padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700 }
.vision-severity-high { color:#ea580c;background:#fff7ed;border:1px solid #fed7aa;
    padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700 }
.vision-severity-medium { color:#d97706;background:#fffbeb;border:1px solid #fde68a;
    padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700 }
.vision-severity-low { color:#059669;background:#ecfdf5;border:1px solid #a7f3d0;
    padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700 }
</style>
""", unsafe_allow_html=True)

with st.expander("📸 Upload a photo for visual diagnosis", expanded=st.session_state.get("vision_expanded", False)):
    _v_col1, _v_col2 = st.columns([1, 1], gap="large")
    with _v_col1:
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px">Upload Image</div>',
            unsafe_allow_html=True,
        )
        _uploaded_img = st.file_uploader(
            "Upload image", type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed", key="vision_upload",
        )
        _active_img = _uploaded_img

        if _active_img:
            st.image(_active_img, use_container_width=True,
                     caption="Image ready for analysis")

    with _v_col2:
        _vision_q = st.text_area(
            "What do you want to know? (optional)",
            placeholder="What is causing this leak?\nIs this corrosion or erosion?\nHow urgent is this?",
            height=110,
            key="vision_question",
        )
        _severity_hint = st.select_slider(
            "Apparent severity",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium",
            key="vision_severity_hint",
        )

        _v_ready = _active_img is not None
        _analyze_btn = st.button(
            "🔍 Analyse Image" if _v_ready else "📸 Upload an image first",
            type="primary" if _v_ready else "secondary",
            disabled=not _v_ready,
            use_container_width=True,
            key="vision_analyze_btn",
        )

# ── Vision analysis trigger ────────────────────────────────────────────────────
if st.session_state.get("vision_analyze_btn") and _active_img:
    _img_bytes = _active_img.getvalue()
    _mime      = f"image/{_active_img.type.split('/')[-1]}" if "/" in (_active_img.type or "") else "image/jpeg"
    _vision_q_val = st.session_state.get("vision_question", "").strip()
    _sev_hint  = st.session_state.get("vision_severity_hint", "Medium")

    # Build the user message that goes into chat history
    _user_label = f"📷 **Photo analysis** — {_vision_q_val}" if _vision_q_val else "📷 **Photo sent for analysis**"
    st.session_state["chat_history"].append({"role": "user", "content": _user_label})
    st.session_state["vision_expanded"] = False

    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(_user_label)
        st.image(_img_bytes, width=260, caption="Attached photo")

    _hist_for_vision = st.session_state["chat_history"][:-1]
    _ph_v = st.empty()
    _t0_v = _time.time()

    _thinking(_ph_v, "Analysing image with vision AI…")

    try:
        vision_result, v_sources, v_token_gen, v_conf, v_intent = rag.ask_with_image(
            _img_bytes, _mime, _vision_q_val, _hist_for_vision
        )
    except Exception as _ve:
        vision_result = {"error": str(_ve), "description": "", "severity": ""}
        v_sources, v_token_gen = [], iter([f"⚠️ Vision error: {_ve}"])
        v_conf, v_intent = 0.0, "failure"

    _ph_v.empty()

    # Show vision findings card before the streamed answer
    if vision_result.get("description") and not vision_result.get("error"):
        sev = vision_result.get("severity", "Medium")
        sev_cls = f"vision-severity-{sev.lower()}"
        _eq_vis = vision_result.get("equipment", "")
        _find   = vision_result.get("finding", "")
        _fm     = vision_result.get("failure_mode", "")
        _cause  = vision_result.get("cause", "")
        _action = vision_result.get("action", "")
        _kws    = ", ".join(vision_result.get("keywords", [])[:6])

        st.markdown(
            f'<div style="background:linear-gradient(135deg,#fff7ed,#fffbeb);'
            f'border:1.5px solid #fde68a;border-left:4px solid #f59e0b;border-radius:14px;'
            f'padding:16px 20px;margin:10px 0 6px">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
            f'<span style="font-size:20px">🔬</span>'
            f'<span style="font-size:14px;font-weight:800;color:#0f172a">Visual Analysis Complete</span>'
            f'<span class="{sev_cls}">{sev} Severity</span>'
            f'</div>'
            + (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">'
               f'<div style="background:#fff;border-radius:8px;padding:10px 12px;border:1px solid #e2e8f0">'
               f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase;margin-bottom:4px">Equipment</div>'
               f'<div style="font-size:13px;font-weight:700;color:#0f172a">{_html.escape(_eq_vis) or "—"}</div></div>'
               f'<div style="background:#fff;border-radius:8px;padding:10px 12px;border:1px solid #e2e8f0">'
               f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase;margin-bottom:4px">Failure Mode</div>'
               f'<div style="font-size:13px;font-weight:700;color:#dc2626">{_html.escape(_fm) or "—"}</div></div>'
               f'</div>' if _eq_vis or _fm else "")
            + (f'<div style="font-size:12.5px;color:#475569;margin-bottom:8px;line-height:1.6">'
               f'<b>Finding:</b> {_html.escape(_find)}</div>' if _find else "")
            + (f'<div style="font-size:12.5px;color:#475569;margin-bottom:8px;line-height:1.6">'
               f'<b>Probable cause:</b> {_html.escape(_cause)}</div>' if _cause else "")
            + (f'<div style="background:#fef2f2;border-radius:8px;padding:10px 12px;'
               f'font-size:12.5px;color:#991b1b;font-weight:600;margin-bottom:8px">'
               f'⚡ Immediate action: {_html.escape(_action)}</div>' if _action else "")
            + (f'<div style="font-size:11px;color:#94a3b8">🔍 Searching plant KB for: {_html.escape(_kws)}</div>' if _kws else "")
            + '</div>',
            unsafe_allow_html=True,
        )
    elif vision_result.get("error"):
        st.warning(vision_result["error"])

    # Stream the RAG-grounded answer
    _v_answer = ""
    with st.chat_message("assistant", avatar="🤖"):
        if vision_result.get("description"):
            _thinking(_ph_v, f"Searching {total_chunks:,} plant records…", vision_result.get("failure_mode", ""))
            _ph_v.empty()
        try:
            _v_answer = st.write_stream(v_token_gen)
        except Exception as _se:
            _v_answer = f"⚠️ Streaming error: {_se}"
            st.markdown(_v_answer)

    _v_answer     = _v_answer or ""
    _v_resp_time  = round(_time.time() - _t0_v, 1)
    _v_followups  = suggest_followups(_v_answer, _vision_q_val or "image analysis", v_intent) if _v_answer and not _v_answer.startswith("⚠️") else []

    st.session_state["chat_history"].append({
        "role": "assistant", "content": _v_answer,
        "sources": v_sources, "confidence": v_conf,
        "intent": v_intent, "response_time": _v_resp_time,
        "followups": _v_followups,
        "timestamp": datetime.datetime.now().strftime("%H:%M"),
        "vision": True,
    })

    _post_answer(_v_answer, v_sources, v_conf, v_intent, _v_resp_time, _vision_q_val)
    st.rerun()


# ── Text input & live response ─────────────────────────────────────────────────
prompt = st.chat_input("Ask anything about equipment failures, maintenance procedures, compliance, and history…")

# Also fire when a suggested-question button put an unanswered user message in history
_history = st.session_state["chat_history"]
if not prompt and _history and _history[-1]["role"] == "user":
    prompt = _history[-1]["content"]
    _history.pop()  # will be re-appended below so the flow stays identical

if prompt:
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)

    _history_for_rag = st.session_state["chat_history"][:-1]
    sources: list = []
    confidence    = 0.0
    intent_str    = "general"

    _ph = st.empty()
    _thinking(_ph, "Classifying question…")
    _t0 = _time.time()

    try:
        _thinking(_ph, "Searching knowledge base…", f"{total_chunks:,} chunks")
        sources, token_gen, confidence, intent_str = rag.ask_stream(
            prompt, n_sources=7, chat_history=_history_for_rag
        )
        if sources:
            _src_names = " · ".join(
                s.get("source_file", "").replace("\\", "/").split("/")[-1]
                for s in sources[:3]
            )
            _thinking(_ph, f"Found {len(sources)} relevant chunks", _src_names[:60])
    except Exception as _e:
        token_gen  = iter([f"⚠️ Error connecting to knowledge base: {_e}"])
        confidence = 0.0
        intent_str = "general"

    _ph.empty()

    answer = ""
    with st.chat_message("assistant", avatar="🤖"):
        try:
            answer = st.write_stream(token_gen)
        except Exception as _e:
            answer = f"⚠️ Streaming error: {_e}"
            st.markdown(answer)

    answer        = answer or ""
    response_time = round(_time.time() - _t0, 1)
    _followups    = suggest_followups(answer, prompt, intent_str) if answer and not answer.startswith("⚠️") else []

    st.session_state["chat_history"].append({
        "role": "assistant", "content": answer,
        "sources": sources, "confidence": confidence,
        "intent": intent_str, "response_time": response_time,
        "followups": _followups,
        "timestamp": datetime.datetime.now().strftime("%H:%M"),
    })

    _post_answer(answer, sources, confidence, intent_str, response_time, prompt)
