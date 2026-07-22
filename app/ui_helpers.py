"""
IndustrialMind — Enterprise Design System v6
Premium white canvas · Linear-style sidebar · Minimal cards · Inter
"""

import base64
import html as html_lib
import streamlit as st
from pathlib import Path
from typing import List, Dict

# ── Logo (base64 encoded once at startup) ────────────────────────────────────
def _load_logo_b64() -> str:
    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return ""

_LOGO_B64: str = _load_logo_b64()

def logo_img_tag(size: int = 48, style: str = "") -> str:
    if _LOGO_B64:
        return f'<img src="data:image/png;base64,{_LOGO_B64}" width="{size}" height="{size}" style="object-fit:contain;{style}" alt="IndustrialMind logo">'
    return f'<div style="width:{size}px;height:{size}px;background:#F59E0B;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;color:#fff;font-size:{size//3}px">IM</div>'

# ── SVG icon library (Lucide-style outlined) ─────────────────────────────────
ICONS = {
    "upload":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "chat":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "graph":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>',
    "shield":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "search":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "brain":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></svg>',
    "wrench":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    "home":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "trending": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "file":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "alert":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "check":    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "clock":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "database": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "zap":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "layers":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "activity": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "arrow_r":  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "cpu":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "settings": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "inbox":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>',
    "user":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "bell":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
    "x":        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "plus":     '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    "download": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "eye":      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "refresh":  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
    "info":     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "chevron_r":'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
    "bar_chart":'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
    "target":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "link":     '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "package":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
}

INDUSTRIAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ══════════════════════════════════════════════════════════════════════════════
   INDUSTRIALMIND — ENTERPRISE DESIGN SYSTEM v6
   Premium white canvas · Linear-style sidebar · Minimal cards
   ══════════════════════════════════════════════════════════════════════════════ */

/* ─── DESIGN TOKENS ──────────────────────────────────────────────────────────*/
:root {
  /* Core palette */
  --white:          #FFFFFF;
  --bg-primary:     #FFFFFF;
  --bg-secondary:   #FAFAFB;
  --bg-tertiary:    #F4F4F5;
  --card-bg:        #FFFFFF;

  /* Borders */
  --border-light:   #9CA3AF;
  --border-medium:  #9CA3AF;
  --border-strong:  #6B7280;

  /* Text */
  --text-primary:   #030712;
  --text-secondary: #374151;
  --text-muted:     #6B7280;
  --text-faint:     #9CA3AF;

  /* Brand */
  --amber:          #F59E0B;
  --amber-light:    #FFFBEB;
  --amber-dark:     #D97706;
  --amber-border:   #FDE68A;
  --amber-text:     #92400E;

  /* Semantic */
  --green:          #22C55E;
  --green-light:    #F0FDF4;
  --green-border:   #BBF7D0;
  --green-text:     #166534;

  --red:            #EF4444;
  --red-light:      #FEF2F2;
  --red-border:     #FECACA;
  --red-text:       #991B1B;

  --blue:           #3B82F6;
  --blue-light:     #EFF6FF;
  --blue-border:    #BFDBFE;
  --blue-text:      #1D4ED8;

  --purple:         #8B5CF6;
  --purple-light:   #F5F3FF;
  --purple-border:  #DDD6FE;
  --purple-text:    #6D28D9;

  /* Shadows — minimal and elegant */
  --shadow-xs:   0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm:   0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md:   0 4px 6px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.04);
  --shadow-lg:   0 10px 15px rgba(0,0,0,0.06), 0 4px 6px rgba(0,0,0,0.04);
  --shadow-xl:   0 20px 25px rgba(0,0,0,0.07), 0 8px 10px rgba(0,0,0,0.04);
  --shadow-amber: 0 4px 14px rgba(245,158,11,0.30);
  --focus-ring:  0 0 0 3px rgba(245,158,11,0.25);

  /* Radii */
  --r-xs:  6px;
  --r-sm:  8px;
  --r:     12px;
  --r-md:  14px;
  --r-lg:  18px;
  --r-xl:  24px;
  --r-full: 9999px;

  /* Spacing */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Sidebar */
  --sidebar-bg:     #0C0C0E;
  --sidebar-border: rgba(255,255,255,0.06);
  --sidebar-hover:  rgba(255,255,255,0.06);
  --sidebar-active: rgba(245,158,11,0.12);
  --sidebar-text:   rgba(255,255,255,0.50);
  --sidebar-text-hover: rgba(255,255,255,0.88);
  --sidebar-text-active: #F59E0B;

  /* Backwards compat */
  --text-1: var(--text-primary);
  --text-2: var(--text-secondary);
  --text-3: var(--text-secondary);
  --text-4: var(--text-muted);
  --surface: var(--card-bg);
  --surface-2: var(--bg-secondary);
  --border: var(--border-light);
  --amber-500: var(--amber);
  --amber-600: var(--amber-dark);
  --amber-100: var(--amber-light);
  --green-500: var(--green);
  --red-500: var(--red);
  --blue-500: var(--blue);
  --blue-600: #2563EB;
  --blue-700: var(--blue-text);
  --green-700: var(--green-text);
  --red-600: #DC2626;
  --red-700: var(--red-text);
  --purple-500: var(--purple);
  --purple-700: var(--purple-text);
  --navy-100: var(--bg-tertiary);
  --navy-200: var(--border-medium);
  --navy-300: var(--border-strong);
  --primary: var(--amber);
  --shadow-focus: var(--focus-ring);
}

/* ─── RESET STREAMLIT CHROME ─────────────────────────────────────────────────*/
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stHeader"] {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
}

/* ══ ZERO-GAP TOP — eliminate every wrapper that reserves vertical space ══ */
[data-testid="stMain"],
[data-testid="stMain"] > div,
[data-testid="stMain"] > div > div,
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
[data-testid="stMainBlockContainer"] > div,
.main,
.main > div,
.main > div > div,
.stMain,
.stMain > div,
.stMain > div > div,
section[data-testid="stMain"],
section[data-testid="stMain"] > div {
  padding-top: 0 !important;
  margin-top: 0 !important;
}

/* ─── BLOCK CONTAINER — tight padding, full width ────────────────────────── */
.block-container,
div.block-container,
[data-testid="stMainBlockContainer"] > div > div {
  padding-top: 0.75rem !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
  padding-bottom: 5rem !important;
  max-width: 100% !important;
  width: 100% !important;
  margin-top: 0 !important;
  margin-left: auto !important;
  margin-right: auto !important;
  box-sizing: border-box !important;
}

/* ─── COLUMN GAPS — uniform 20px between Streamlit columns ──────────────── */
[data-testid="stHorizontalBlock"] {
  gap: 20px !important;
  align-items: stretch !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  gap: 0 !important;
  min-width: 0 !important;
}

/* ─── VERTICAL BLOCK GAPS — consistent section spacing ──────────────────── */
[data-testid="stVerticalBlock"] > div {
  gap: 0 !important;
}
[data-testid="stVerticalBlockSeparator"] {
  margin: 0 !important;
  padding: 0 !important;
  height: 0 !important;
}

/* ─── ELEMENT CONTAINER — no extra bottom margins ────────────────────────── */
[data-testid="stElementContainer"] {
  margin-bottom: 0 !important;
}
/* give breathing room between stacked markdown blocks */
[data-testid="stMarkdown"] { margin-bottom: 0 !important; }
[data-testid="stMarkdown"] + [data-testid="stMarkdown"] { margin-top: 0 !important; }

[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stPageLink"] a img,
[data-testid="stPageLink"] a span[aria-hidden="true"],
[data-testid="stPageLink"] [data-testid="stPageLinkIcon"] { display: none !important; }

/* ─── GLOBAL BASE ────────────────────────────────────────────────────────────*/
html, body { background: var(--bg-primary) !important; }
*, button, input, select, textarea {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
  background: var(--bg-primary) !important;
}

h1,h2,h3,h4,h5,h6 {
  font-family: 'Inter', sans-serif !important;
  letter-spacing: -0.025em !important;
  color: var(--text-primary) !important;
  margin: 0 !important;
}
h1 { font-size: 2rem !important; font-weight: 800 !important; line-height: 1.2 !important; }
h2 { font-size: 1.25rem !important; font-weight: 700 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; }
p, li { color: var(--text-secondary) !important; line-height: 1.7 !important; font-size: 15px !important; }
label { color: var(--text-secondary) !important; font-size: 13px !important; font-weight: 500 !important; }
code {
  background: var(--bg-tertiary) !important; color: var(--amber-dark) !important;
  padding: 2px 7px !important; border-radius: var(--r-xs) !important;
  font-size: 12.5px !important; border: 1px solid var(--border-medium) !important;
}
hr { border: none !important; border-top: 1px solid var(--border-light) !important; margin: 1.5rem 0 !important; }

/* ─── ANIMATIONS ─────────────────────────────────────────────────────────────*/
@keyframes fadeUp   { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:none } }
@keyframes fadeIn   { from { opacity:0 } to { opacity:1 } }
@keyframes shimmer  { 0% { background-position: -200% 0 } 100% { background-position: 200% 0 } }
@keyframes dot-pulse{ 0%,100%{ box-shadow:0 0 0 0 rgba(34,197,94,.5) } 60%{ box-shadow:0 0 0 5px rgba(34,197,94,.0) } }
@keyframes spin     { from { transform: rotate(0deg) } to { transform: rotate(360deg) } }
@keyframes countUp  { from { opacity:0; transform:translateY(4px) } to { opacity:1; transform:none } }

.block-container { animation: fadeUp .3s ease both; }

/* ─── SIDEBAR — Linear-style dark ───────────────────────────────────────────*/
[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--sidebar-border) !important;
  box-shadow: none !important;
}
[data-testid="stSidebarContent"],
[data-testid="stSidebarContent"] > div,
[data-testid="stSidebarContent"] > div > div,
[data-testid="stSidebarContent"] > div > div > div,
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* ─── SIDEBAR COLLAPSE BUTTON — visible dark arrow ───────────────────────────*/
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
  background: #ffffff !important;
  border: 1px solid #D1D5DB !important;
  border-radius: 8px !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.10) !important;
  color: #374151 !important;
  width: 28px !important;
  height: 28px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg {
  stroke: #374151 !important;
  fill: none !important;
}
[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"]:hover {
  background: #F59E0B !important;
  border-color: #F59E0B !important;
}
[data-testid="stSidebarCollapsedControl"]:hover svg,
[data-testid="collapsedControl"]:hover svg {
  stroke: #ffffff !important;
}

/* ─── SIDEBAR EXPAND BUTTON (inside dark sidebar) ───────────────────────────*/
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebar"] button[kind="header"] {
  color: rgba(255,255,255,0.6) !important;
  background: transparent !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebar"] button[kind="header"]:hover {
  color: #ffffff !important;
  background: rgba(255,255,255,0.08) !important;
}

/* ─── FULL-WIDTH CONTENT WHEN SIDEBAR COLLAPSED ─────────────────────────────*/
[data-testid="stMain"] {
  transition: margin-left 0.25s ease, width 0.25s ease;
}
/* When sidebar is collapsed Streamlit keeps it in the DOM but collapses it.
   Force the main area to stretch all the way to the left edge. */
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"],
[data-testid="stSidebar"][data-collapsed="true"] ~ [data-testid="stMain"] {
  margin-left: 0 !important;
  width: 100% !important;
}
/* Also target the app view container layout */
[data-testid="stAppViewContainer"] {
  display: flex !important;
  flex-direction: row !important;
}
[data-testid="stAppViewContainer"] > [data-testid="stMain"] {
  flex: 1 1 0% !important;
  min-width: 0 !important;
}

/* Brand mark */
.im-brand {
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
  padding: 20px 16px 18px !important;
  border-bottom: 1px solid var(--sidebar-border) !important;
  margin-bottom: 8px !important;
  text-decoration: none !important;
  color: inherit !important;
}
/* Kill Streamlit's blue anchor override */
.im-brand, .im-brand:link, .im-brand:visited,
.im-brand:hover, .im-brand:active {
  color: inherit !important;
  text-decoration: none !important;
}
.im-brand-mark {
  width: 100px !important; height: 100px !important;
  border-radius: 18px !important;
  background: transparent !important;
  display: flex !important; align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important; overflow: visible !important;
}
.im-brand-mark img {
  width: 100px !important; height: 100px !important;
  object-fit: contain !important;
  border-radius: 18px !important;
  box-shadow: 0 2px 16px rgba(0,0,0,0.45), 0 0 0 1.5px rgba(255,255,255,0.10) !important;
}
.im-brand-text { line-height: 1.2 !important; }
.im-brand-name {
  font-size: 18px !important; font-weight: 800 !important;
  color: #FFFFFF !important;
  letter-spacing: -0.02em !important;
  text-decoration: none !important;
}
.im-brand-sub {
  font-size: 12px !important; font-weight: 500 !important;
  color: rgba(255,255,255,0.35) !important;
  letter-spacing: 0.03em !important;
  margin-top: 3px !important;
  text-decoration: none !important;
}

/* Nav */
.im-nav-section { padding: 4px 8px; }
.im-nav-label {
  font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.22);
  text-transform: uppercase; letter-spacing: 0.10em;
  padding: 0 8px 6px; display: block;
}
.im-nav-link {
  display: flex; align-items: center; gap: 9px;
  padding: 9px 12px; border-radius: var(--r-sm); margin: 2px 0;
  color: var(--sidebar-text); font-size: 15px; font-weight: 500;
  text-decoration: none !important;
  transition: background 0.12s, color 0.12s;
  position: relative; cursor: pointer;
}
.im-nav-link svg {
  flex-shrink: 0; width: 17px; height: 17px;
  opacity: 0.4; transition: opacity 0.12s;
}
.im-nav-link:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text-hover);
}
.im-nav-link:hover svg { opacity: 0.75; }
.im-nav-link.active {
  background: var(--sidebar-active);
  color: var(--sidebar-text-active);
  font-weight: 600;
}
.im-nav-link.active svg { color: var(--amber); opacity: 1; }
.im-nav-link.active::before {
  content: '';
  position: absolute; left: 0; top: 6px; bottom: 6px;
  width: 2.5px; background: var(--amber);
  border-radius: 0 2px 2px 0;
}
.im-nav-divider {
  height: 1px;
  background: var(--sidebar-border);
  margin: 8px 8px;
}

/* Status indicator */
.im-sidebar-status {
  margin: 8px 8px 12px;
  padding: 8px 12px;
  border-radius: var(--r-sm);
  background: rgba(34,197,94,0.06);
  border: 1px solid rgba(34,197,94,0.12);
  display: flex; align-items: center; gap: 7px;
}
.im-sidebar-status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green); flex-shrink: 0;
  animation: dot-pulse 2.5s infinite;
}
.im-sidebar-status-text {
  font-size: 13px; color: rgba(74,222,128,0.7);
  font-weight: 600; letter-spacing: 0.01em;
}

/* ─── INPUTS ─────────────────────────────────────────────────────────────────*/
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-medium) !important;
  color: var(--text-primary) !important;
  border-radius: var(--r-sm) !important;
  font-size: 14px !important;
  box-shadow: var(--shadow-xs) !important;
  transition: border-color 0.12s, box-shadow 0.12s !important;
}
[data-testid="stSelectbox"] > div > div {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-medium) !important;
  color: var(--text-primary) !important;
  border-radius: var(--r-sm) !important;
  font-size: 14px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--amber) !important;
  box-shadow: var(--focus-ring) !important;
  outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: var(--text-muted) !important; }

/* ─── BUTTONS ────────────────────────────────────────────────────────────────*/
[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(135deg, var(--amber) 0%, var(--amber-dark) 100%) !important;
  color: #fff !important; font-weight: 600 !important;
  border: none !important; border-radius: var(--r-sm) !important;
  font-size: 13.5px !important; padding: 0 20px !important;
  height: 38px !important; letter-spacing: -0.01em !important;
  box-shadow: 0 2px 8px rgba(245,158,11,0.35) !important;
  transition: box-shadow 0.15s, transform 0.1s, filter 0.15s !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
  filter: brightness(1.08) !important;
  box-shadow: 0 6px 20px rgba(245,158,11,0.45) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stButton"] button[kind="primary"]:active {
  transform: translateY(0) !important; filter: brightness(0.97) !important;
}
[data-testid="stButton"] button[kind="secondary"],
[data-testid="stButton"] button[kind="tertiary"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-medium) !important;
  color: var(--text-secondary) !important;
  border-radius: var(--r-sm) !important;
  font-size: 13.5px !important; font-weight: 500 !important;
  height: 38px !important; padding: 0 16px !important;
  box-shadow: var(--shadow-xs) !important;
  transition: border-color 0.12s, box-shadow 0.12s, color 0.12s, background 0.12s, transform 0.1s !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover,
[data-testid="stButton"] button[kind="tertiary"]:hover {
  border-color: var(--amber-border) !important;
  background: var(--amber-light) !important;
  color: var(--amber-text) !important;
  box-shadow: var(--shadow-sm) !important;
  transform: translateY(-1px) !important;
}

/* Work-Order chip pills */
div[data-testid="stHorizontalBlock"] [data-testid="stBaseButton-secondary"] {
  border-radius: 99px !important;
  font-size: 11.5px !important;
  font-weight: 600 !important;
  padding: 2px 6px !important;
  background: var(--bg-secondary) !important;
  border: 1px solid var(--border-medium) !important;
  color: var(--text-secondary) !important;
  line-height: 1.6 !important;
  min-height: 28px !important;
  box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"] [data-testid="stBaseButton-secondary"]:hover {
  background: var(--bg-tertiary) !important;
  border-color: var(--border-strong) !important;
  color: var(--text-primary) !important;
  transform: none !important;
}

/* ─── WIDGETS ────────────────────────────────────────────────────────────────*/
[data-testid="stExpander"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-light) !important;
  border-radius: var(--r) !important; margin: 6px 0 !important;
  overflow: hidden !important; box-shadow: var(--shadow-xs) !important;
}
[data-testid="stExpander"] summary {
  color: var(--text-secondary) !important;
  font-size: 14px !important; font-weight: 500 !important;
}
[data-testid="stTabs"] [role="tablist"] {
  border-bottom: 2px solid var(--border-light) !important;
  gap: 0 !important; background: transparent !important;
  margin-bottom: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
  color: var(--text-muted) !important;
  font-size: 13.5px !important; font-weight: 500 !important;
  padding: 10px 22px !important;
  transition: color 0.12s, background 0.12s !important;
  border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
  color: var(--text-secondary) !important;
  background: var(--bg-secondary) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--text-primary) !important; font-weight: 600 !important;
  border-bottom: 2px solid var(--amber) !important;
  margin-bottom: -2px !important;
}
[data-testid="stFileUploader"] {
  background: var(--card-bg) !important;
  border: 1.5px dashed var(--border-strong) !important;
  border-radius: var(--r-md) !important;
  transition: all 0.15s !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--amber) !important;
  background: var(--amber-light) !important;
}
[data-testid="stChatMessage"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-light) !important;
  border-radius: var(--r-md) !important;
  padding: 20px !important; margin: 8px 0 !important;
  box-shadow: var(--shadow-sm) !important;
  transition: box-shadow 0.15s !important;
}
[data-testid="stChatMessage"]:hover { box-shadow: var(--shadow-md) !important; }
[data-testid="stChatInput"] textarea {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-medium) !important;
  border-radius: var(--r) !important;
  box-shadow: var(--shadow-md) !important;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--amber) !important;
  box-shadow: var(--shadow-md), var(--focus-ring) !important;
}
[data-testid="stMetric"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-light) !important;
  border-radius: var(--r-lg) !important;
  padding: 24px !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-muted) !important;
  font-size: 11px !important; font-weight: 600 !important;
  text-transform: uppercase !important; letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] {
  color: var(--text-primary) !important; font-weight: 800 !important;
}
[data-testid="stProgress"] > div > div {
  background: var(--amber) !important; border-radius: 99px !important;
}
[data-testid="stProgress"] > div {
  background: var(--border-light) !important; border-radius: 99px !important;
}
[data-testid="stAlert"] { border-radius: var(--r-sm) !important; font-size: 14px !important; }
[data-testid="stCheckbox"] span { font-size: 14px !important; color: var(--text-secondary) !important; }
[data-testid="stSpinner"] svg { color: var(--amber) !important; }

/* ─── PLOTLY CHARTS ──────────────────────────────────────────────────────────*/
[data-testid="stPlotlyChart"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-light) !important;
  border-radius: var(--r-lg) !important;
  padding: 4px 4px 0 !important;
  box-shadow: var(--shadow-sm) !important;
  transition: box-shadow 0.2s !important;
}
[data-testid="stPlotlyChart"]:hover { box-shadow: var(--shadow-md) !important; }

/* ─── DATAFRAME ──────────────────────────────────────────────────────────────*/
[data-testid="stDataFrame"] {
  border-radius: var(--r) !important;
  border: 1px solid var(--border-light) !important;
  overflow: hidden !important;
  box-shadow: var(--shadow-xs) !important;
}

/* ─── TABLE ──────────────────────────────────────────────────────────────────*/
[data-testid="stTable"] table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
[data-testid="stTable"] th {
  background: var(--bg-secondary) !important;
  color: var(--text-muted) !important;
  font-size: 11px !important; font-weight: 600 !important;
  text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid var(--border-light) !important;
  padding: 10px 14px !important;
}
[data-testid="stTable"] td {
  padding: 10px 14px !important;
  color: var(--text-secondary) !important;
  border-bottom: 1px solid var(--border-light) !important;
}
[data-testid="stTable"] tr:hover td { background: var(--bg-secondary) !important; }

/* ─── DOWNLOAD BUTTON ────────────────────────────────────────────────────────*/
[data-testid="stDownloadButton"] button {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-medium) !important;
  color: var(--text-secondary) !important;
  border-radius: var(--r-sm) !important;
  font-size: 13px !important; font-weight: 500 !important;
  box-shadow: var(--shadow-xs) !important;
  transition: all 0.12s !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: var(--amber) !important;
  color: var(--amber-dark) !important;
}

/* ─── NUMBER INPUT ───────────────────────────────────────────────────────────*/
[data-testid="stNumberInput"] button {
  border-radius: var(--r-xs) !important;
  background: var(--bg-secondary) !important;
  border-color: var(--border-medium) !important;
  color: var(--text-secondary) !important;
}

/* ─── SCROLLBAR ──────────────────────────────────────────────────────────────*/
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ─── CODE BLOCKS ────────────────────────────────────────────────────────────*/
pre { background: #0F172A !important; border-radius: var(--r) !important;
  padding: 16px 20px !important; color: #E2E8F0 !important; font-size: 13px !important; }
pre code { background: transparent !important; color: inherit !important;
  border: none !important; padding: 0 !important; }

/* ─── SPACING UTILITIES ──────────────────────────────────────────────────────*/
.im-section { margin-top: 28px; }
.im-section-sm { margin-top: 16px; }
.im-section-lg { margin-top: 40px; }
.im-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.im-grid-3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
.im-grid-4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 20px; }
@media(max-width:900px){ .im-grid-3,.im-grid-4{ grid-template-columns:1fr 1fr; } }
@media(max-width:600px){ .im-grid-2,.im-grid-3,.im-grid-4{ grid-template-columns:1fr; } }

/* ─── PAGE HERO ──────────────────────────────────────────────────────────────*/
.im-page-header {
  background: linear-gradient(135deg, #ffffff 0%, #FFFBF0 100%);
  border: 1px solid var(--border-light);
  border-top: none;
  border-left: 4px solid var(--amber);
  border-radius: var(--r-lg);
  padding: 24px 32px 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(245,158,11,0.06);
  animation: fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative; overflow: hidden;
}
.im-page-header::after {
  content: ''; position: absolute; top: 0; right: 0; width: 200px; height: 100%;
  background: radial-gradient(ellipse at top right, rgba(245,158,11,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.im-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 10px; font-weight: 700;
  color: var(--amber-dark);
  text-transform: uppercase; letter-spacing: 0.12em;
  margin-bottom: 10px;
  background: var(--amber-light);
  border: 1px solid var(--amber-border);
  padding: 3px 12px; border-radius: var(--r-full);
}
.im-page-title {
  font-size: 1.75rem; font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.035em; line-height: 1.15;
  margin-bottom: 8px !important;
}
.im-page-sub {
  font-size: 14px; color: var(--text-secondary);
  line-height: 1.65; max-width: 560px; font-weight: 400;
}
.im-divider { height: 1px; background: var(--border-light); margin: 16px 0 0; }

/* Backwards-compat .hero-wrap */
.hero-wrap {
  background: linear-gradient(135deg, #ffffff 0%, #FFFBF0 100%);
  border: 1.5px solid #D1D5DB;
  margin-bottom: 24px !important;
  border-top: none;
  border-left: 4px solid var(--amber);
  border-radius: var(--r-lg);
  padding: 24px 32px 20px; margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(245,158,11,0.06);
  animation: fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative; overflow: hidden;
}
.hero-wrap::after {
  content: ''; position: absolute; top: 0; right: 0; width: 200px; height: 100%;
  background: radial-gradient(ellipse at top right, rgba(245,158,11,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 10px; font-weight: 700;
  color: var(--amber-dark); text-transform: uppercase;
  letter-spacing: 0.12em; margin-bottom: 10px;
  background: var(--amber-light); border: 1px solid var(--amber-border);
  padding: 3px 12px; border-radius: var(--r-full);
}
.hero-title {
  font-size: 1.75rem; font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.035em; line-height: 1.15;
  margin-bottom: 8px !important;
}
.hero-sub { font-size: 14px; color: var(--text-secondary); line-height: 1.65; max-width: 560px; }
.hero-divider { height: 1.5px; background: #D1D5DB; margin-top: 18px; }

/* ─── ENTERPRISE CARDS ───────────────────────────────────────────────────────*/
.im-card {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: var(--r-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.22s, transform 0.22s, border-color 0.22s;
}
.im-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
  border-color: var(--border-medium);
}
.im-card-title {
  font-size: 14px; font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em; margin-bottom: 4px;
}
.im-card-sub {
  font-size: 12px; color: var(--text-muted);
  line-height: 1.5;
}

/* ─── METRIC CARDS ───────────────────────────────────────────────────────────*/
.metric-card {
  background: var(--card-bg);
  border: 1.5px solid #D1D5DB;
  border-radius: var(--r-lg);
  padding: 20px 20px 20px 24px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
  position: relative; overflow: hidden;
}
/* accent bar rendered as a real child div — see render_metric_card() */
.metric-card-bar {
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px; border-radius: 3px 0 0 3px;
  background: var(--amber); /* overridden inline per card */
}
.metric-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--amber-border);
}
.metric-card-bar { display: none; }
.metric-icon { display: none; }
.metric-value {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  font-weight: 800; color: var(--text-primary);
  letter-spacing: -0.04em; line-height: 1;
  animation: countUp 0.4s ease both;
}
.metric-label {
  font-size: 11px; color: var(--text-muted);
  margin-top: 6px; text-transform: uppercase;
  letter-spacing: 0.07em; font-weight: 600;
}
.metric-sub { font-size: 11px; color: var(--text-muted); margin-top: 3px; }

/* ─── STAT STRIP ─────────────────────────────────────────────────────────────*/
.im-stat {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: var(--r-lg);
  padding: 24px; position: relative; overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s;
}
.im-stat:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.im-stat-icon {
  width: 36px; height: 36px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px;
}
.im-stat-label {
  font-size: 11px; font-weight: 600; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px;
}
.im-stat-value {
  font-size: 2rem; font-weight: 800; color: var(--text-primary);
  letter-spacing: -0.05em; line-height: 1;
}
.im-stat-sub { font-size: 11.5px; color: var(--text-muted); margin-top: 6px; }

/* ─── GLOBAL CHART COLUMN CARDS ─────────────────────────────────────────────*/
/* Any st.column that contains a .chart-row-header gets card styling globally  */
[data-testid="stColumn"]:has(.chart-row-header) {
  background: #ffffff !important;
  border: 1.5px solid #D1D5DB !important;
  border-radius: 14px !important;
  padding: 18px 18px 12px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 2px 8px rgba(0,0,0,.04) !important;
}
[data-testid="stHorizontalBlock"]:has([data-testid="stColumn"]:has(.chart-row-header)) {
  gap: 20px !important;
}
[data-testid="stColumn"]:has(.chart-row-header) [data-testid="stPlotlyChart"] {
  margin-top: 6px;
}

/* ─── CHART CONTAINERS ───────────────────────────────────────────────────────*/
.chart-card {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: var(--r-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}
.chart-card-header {
  display: flex; align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.chart-card-title {
  font-size: 13px; font-weight: 600;
  color: var(--text-primary); letter-spacing: -0.01em;
}
.chart-card-badge {
  font-size: 10.5px; font-weight: 500; color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 3px 10px; border-radius: var(--r-full);
  border: 1px solid var(--border-light);
}
.chart-row-header {
  font-size: 12.5px; font-weight: 600; color: var(--text-primary);
  letter-spacing: -0.01em; margin-bottom: 8px;
  display: flex; align-items: center; justify-content: space-between;
}
.chart-row-header-badge {
  font-size: 10px; font-weight: 500; color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 2px 9px; border-radius: var(--r-full);
  border: 1px solid var(--border-light);
}

/* ─── SECTION LABELS ─────────────────────────────────────────────────────────*/
.section-label {
  font-size: 11.5px; font-weight: 700; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.10em;
  margin-top: 4px; margin-bottom: 16px;
  display: flex; align-items: center; gap: 8px;
}
.section-label::before {
  content: '';
  width: 3px; height: 14px;
  background: var(--amber);
  border-radius: 2px; flex-shrink: 0;
}

/* ─── BADGE PILLS ─────────────────────────────────────────────────────────────*/
.im-badge {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 10px; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 3px 10px;
  border-radius: var(--r-full);
}
.im-badge-amber { background: var(--amber-light); color: var(--amber-dark); border: 1px solid var(--amber-border); }
.im-badge-green { background: var(--green-light); color: var(--green-text); border: 1px solid var(--green-border); }
.im-badge-red   { background: var(--red-light);   color: var(--red-text);   border: 1px solid var(--red-border); }
.im-badge-blue  { background: var(--blue-light);  color: var(--blue-text);  border: 1px solid var(--blue-border); }
.im-badge-purple{ background: var(--purple-light);color: var(--purple-text);border: 1px solid var(--purple-border);}

/* ─── INFO / REG CARDS ────────────────────────────────────────────────────────*/
.im-info-card {
  background: var(--card-bg); border: 1.5px solid #D1D5DB;
  border-radius: var(--r-lg); padding: 20px 22px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 2px 8px rgba(0,0,0,.04);
  transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
  height: 100%;
}
.im-info-card:hover {
  box-shadow: var(--shadow-md); transform: translateY(-2px);
  border-color: var(--border-medium);
}
.im-info-card-title {
  font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 3px;
}
.im-info-card-sub {
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; margin-bottom: 8px;
}
.im-info-card-desc { font-size: 12.5px; color: var(--text-secondary); line-height: 1.65; }

/* ─── CONTENT CARDS — minimal, no colored backgrounds ───────────────────────*/
.source-box {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: var(--r);
  padding: 16px 18px; margin: 6px 0;
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.15s, border-color 0.15s;
}
.source-box:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--blue);
}
.source-file { color: var(--blue-text); font-weight: 600; font-size: 13px; }
.source-meta { color: var(--text-muted); font-size: 11.5px; margin-left: 8px; }
.source-text { color: var(--text-secondary); margin-top: 8px; line-height: 1.65; font-size: 13px; }

.gap-card {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-left: 3px solid var(--red);
  border-radius: var(--r);
  padding: 18px 20px 18px 18px; margin: 8px 0;
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.2s, transform 0.2s;
}
.gap-card:hover { box-shadow: var(--shadow-md); transform: translateX(2px); }
.gap-card-title { color: var(--text-primary); font-weight: 700; font-size: 14px; }
.gap-card-desc { color: var(--text-secondary); font-size: 13px; margin-top: 8px; line-height: 1.7; }
.gap-fix {
  color: var(--amber-text); font-size: 12px; font-weight: 500;
  margin-top: 12px; padding: 10px 12px;
  background: var(--amber-light); border-radius: var(--r-xs);
  border: 1px solid var(--amber-border);
}

.pattern-card {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-left: 3px solid var(--green);
  border-radius: var(--r);
  padding: 18px 20px 18px 18px; margin: 8px 0;
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.2s, border-color 0.2s, transform 0.2s;
}
.pattern-card:hover { box-shadow: var(--shadow-md); transform: translateX(2px); }
.pattern-title { color: var(--text-primary); font-weight: 700; font-size: 14px; }
.pattern-count {
  color: var(--text-muted); font-size: 11.5px; margin-top: 4px;
  font-weight: 500; letter-spacing: 0.02em;
}
.pattern-body { color: var(--text-secondary); font-size: 13px; margin-top: 10px; line-height: 1.7; }
.pattern-rec {
  color: var(--green-text); font-size: 12px; font-weight: 500;
  margin-top: 12px; padding: 10px 12px;
  background: var(--green-light); border-radius: var(--r-xs);
  border: 1px solid var(--green-border);
}

.knowledge-card {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-left: 3px solid var(--purple);
  border-radius: var(--r);
  padding: 18px 20px 18px 18px; margin: 8px 0;
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.2s, transform 0.2s;
}
.knowledge-card:hover { box-shadow: var(--shadow-md); transform: translateX(2px); }
.knowledge-type {
  display: inline-block;
  background: var(--purple-light);
  color: var(--purple-text);
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; padding: 2px 9px; border-radius: var(--r-full);
  border: 1px solid var(--purple-border);
}
.knowledge-title { color: var(--text-primary); font-weight: 700; font-size: 14px; margin: 9px 0 5px; }
.knowledge-content { color: var(--text-secondary); font-size: 13px; line-height: 1.7; }
.knowledge-meta {
  color: var(--text-muted); font-size: 11.5px;
  margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-light);
}

/* Session card */
.session-card {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: var(--r);
  padding: 20px; margin: 6px 0;
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.15s;
}
.session-card:hover { box-shadow: var(--shadow-sm); }

/* ─── STATUS PILLS & BADGES ──────────────────────────────────────────────────*/
.pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 9px; border-radius: var(--r-full);
  font-size: 11px; font-weight: 600; letter-spacing: 0.01em;
}
.pill-amber  { background: var(--amber-light);  color: var(--amber-text);  border: 1px solid var(--amber-border); }
.pill-green  { background: var(--green-light);  color: var(--green-text);  border: 1px solid var(--green-border); }
.pill-red    { background: var(--red-light);    color: var(--red-text);    border: 1px solid var(--red-border); }
.pill-blue   { background: var(--blue-light);   color: var(--blue-text);   border: 1px solid var(--blue-border); }
.pill-purple { background: var(--purple-light); color: var(--purple-text); border: 1px solid var(--purple-border); }
.pill-gray   { background: var(--bg-secondary); color: var(--text-secondary); border: 1px solid var(--border-light); }

.status-badge {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 11px; font-weight: 600;
  padding: 3px 10px; border-radius: var(--r-full);
}
.status-open     { background: var(--blue-light);   color: var(--blue-text);  border: 1px solid var(--blue-border); }
.status-progress { background: var(--amber-light);  color: var(--amber-text); border: 1px solid var(--amber-border); }
.status-done     { background: var(--green-light);  color: var(--green-text); border: 1px solid var(--green-border); }
.status-overdue  { background: var(--red-light);    color: var(--red-text);   border: 1px solid var(--red-border); }
.status-critical { background: var(--red-light);    color: var(--red-text);   border: 1px solid var(--red-border); }
.status-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }

/* ─── BANNERS ────────────────────────────────────────────────────────────────*/
.info-banner {
  background: var(--blue-light);
  border: 1px solid var(--blue-border);
  border-radius: var(--r); padding: 14px 18px;
  font-size: 13.5px; color: var(--blue-text); margin: 10px 0;
}
.warn-banner {
  background: var(--amber-light);
  border: 1px solid var(--amber-border);
  border-radius: var(--r); padding: 14px 18px;
  font-size: 13.5px; color: var(--amber-text); margin: 10px 0;
}
.success-banner {
  background: var(--green-light);
  border: 1px solid var(--green-border);
  border-radius: var(--r); padding: 14px 18px;
  font-size: 13.5px; color: var(--green-text); margin: 10px 0;
}

/* ─── PROGRESS BARS ──────────────────────────────────────────────────────────*/
.progress-wrap {
  background: var(--border-light);
  border-radius: 99px; height: 6px; overflow: hidden; margin: 4px 0;
}
.progress-bar-fill {
  height: 100%; border-radius: 99px;
  background: var(--amber);
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.progress-bar-wrap {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: var(--r-md);
  padding: 16px 20px; margin: 6px 0;
  box-shadow: var(--shadow-xs);
}

/* ─── EMPTY STATES ───────────────────────────────────────────────────────────*/
.empty-state { text-align: center; padding: 64px 32px; animation: fadeIn 0.35s ease; }
.empty-state-icon {
  width: 64px; height: 64px; border-radius: 18px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px; font-size: 28px;
  color: var(--text-muted);
}
.empty-state-title {
  font-size: 18px; font-weight: 700;
  color: var(--text-primary); margin-bottom: 8px;
  letter-spacing: -0.02em;
}
.empty-state-body {
  font-size: 14px; color: var(--text-secondary);
  max-width: 380px; margin: 0 auto; line-height: 1.7;
}

/* ─── TYPING INDICATOR ───────────────────────────────────────────────────────*/
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.3 }
  30% { transform: translateY(-5px); opacity: 1 }
}
.typing-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--text-muted); display: inline-block;
  animation: typing-bounce 1.4s ease infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
.typing-dots {
  display: inline-flex; gap: 5px; align-items: center;
  padding: 10px 14px; background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: 16px 16px 16px 4px;
  box-shadow: var(--shadow-sm);
}

/* ─── FEATURE CARDS ──────────────────────────────────────────────────────────*/
.im-feat {
  background: var(--card-bg);
  border: 1px solid var(--border-light);
  border-radius: var(--r-lg); padding: 28px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
}
.im-feat:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
  border-color: var(--amber-border);
}
.im-feat-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 18px; background: var(--bg-secondary);
  border: 1px solid var(--border-light);
}
.im-feat-title {
  font-size: 14.5px; font-weight: 700;
  color: var(--text-primary); margin-bottom: 6px;
  letter-spacing: -0.015em;
}
.im-feat-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.7; }
.im-feat-tag {
  display: inline-flex; align-items: center; gap: 4px;
  margin-top: 16px; font-size: 10px; font-weight: 600;
  padding: 3px 10px; border-radius: var(--r-full);
  text-transform: uppercase; letter-spacing: 0.07em;
  background: var(--bg-secondary);
  color: var(--text-muted);
  border: 1px solid var(--border-light);
}
.im-features { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }

/* ─── SHIMMER LOADER ─────────────────────────────────────────────────────────*/
.shimmer {
  background: linear-gradient(90deg, var(--bg-secondary) 25%, #fff 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.6s infinite;
}

/* ─── ACCESSIBILITY ──────────────────────────────────────────────────────────*/
:focus-visible {
  outline: 2px solid var(--amber) !important;
  outline-offset: 2px !important;
  border-radius: 4px !important;
}
[data-testid="stTextInput"] input:focus-visible,
[data-testid="stTextArea"] textarea:focus-visible {
  outline: 2px solid var(--amber) !important;
  outline-offset: 0 !important;
  box-shadow: var(--focus-ring) !important;
}
a.im-nav-link:focus-visible {
  outline: 2px solid var(--amber) !important;
  outline-offset: 2px !important;
  border-radius: var(--r-sm) !important;
}
.im-skip-link {
  position: fixed; top: -100px; left: 16px; z-index: 99999;
  background: var(--amber); color: #fff; font-weight: 700;
  padding: 10px 18px; border-radius: var(--r-sm); font-size: 14px;
  transition: top 0.15s; text-decoration: none;
}
.im-skip-link:focus { top: 16px !important; }
[data-testid="stButton"] button { min-height: 38px !important; }
[data-testid="stCheckbox"] label { min-height: 36px !important; display: flex !important; align-items: center !important; }

/* ─── RESPONSIVE ─────────────────────────────────────────────────────────────*/
@media (max-width: 768px) {
  .block-container { padding: 0.5rem 0.75rem 4rem !important; }
  .im-page-title, .hero-title { font-size: 1.5rem !important; }
  [data-testid="stHorizontalBlock"]:has(.metric-card) { flex-wrap: wrap !important; }
  [data-testid="stHorizontalBlock"] > div:has(.metric-card) {
    min-width: calc(50% - 8px) !important; flex: 1 1 calc(50% - 8px) !important;
  }
  [data-testid="stPlotlyChart"] { padding: 4px !important; }
}
@media (max-width: 480px) {
  .block-container { padding: 0.4rem 0.6rem 4rem !important; }
  [data-testid="stHorizontalBlock"] > div:has(.metric-card) {
    min-width: 100% !important; flex: 1 1 100% !important;
  }
  .im-page-title, .hero-title { font-size: 1.3rem !important; }
}
</style>
<script>
(function(){
  const css=`
    [data-testid="stFileUploaderDropzone"] button{background:var(--amber)!important;color:#fff!important;border:none!important;border-radius:var(--r-sm)!important;font-weight:600!important;}
  `;
  function inject(){
    if(document.getElementById('im-v6'))return;
    const s=document.createElement('style');s.id='im-v6';s.textContent=css;document.head.appendChild(s);
  }
  inject();
  const obs=new MutationObserver(inject);
  const wait=setInterval(()=>{if(document.head){obs.observe(document.head,{childList:true});clearInterval(wait);}},50);

  /* ── Full-width fix: inject CSS AFTER Streamlit's emotion-cache styles ── */
  function injectLayoutCSS(){
    if(document.getElementById('im-layout-fix')) return;
    /* Check emotion-cache styles are loaded first */
    const hasEmotionCache = [...document.styleSheets].some(function(ss){
      try{ return ss.cssRules && [...ss.cssRules].some(function(r){ return r.selectorText && r.selectorText.includes('emotion'); }); }
      catch(e){ return false; }
    });
    /* Always inject — we use !important which wins regardless of order */
    const s = document.createElement('style');
    s.id = 'im-layout-fix';
    s.textContent = [
      /* Sidebar collapsed: zero out its width so main fills full screen */
      'section[data-testid="stSidebar"][aria-expanded="false"]{',
      '  width:0!important;min-width:0!important;',
      '  overflow:hidden!important;border:none!important;',
      '}',
      /* Main always grows to fill remaining flex space */
      'section[data-testid="stMain"]{flex:1 1 0%!important;min-width:0!important;}',
      /* Collapsed control (the > arrow) should be position:fixed so it doesn\'t consume layout space */
      '[data-testid="stSidebarCollapsedControl"]{position:fixed!important;top:12px!important;left:12px!important;z-index:999!important;}',
    ].join('');
    document.head.appendChild(s);
  }
  /* Run immediately and also after a short delay to beat emotion-cache re-injection */
  injectLayoutCSS();
  setTimeout(injectLayoutCSS, 500);
  setTimeout(injectLayoutCSS, 1500);
  /* Re-inject if Streamlit removes our style (e.g. on hot-reload) */
  new MutationObserver(function(){
    if(!document.getElementById('im-layout-fix')) injectLayoutCSS();
  }).observe(document.head,{childList:true});
})();
</script>
"""

_LOADING_SCREEN_CSS = """
<style>
.im-page-loader {
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  min-height:55vh;text-align:center;padding:48px 32px;animation:fadeIn .25s ease;
}
.im-pl-logo {
  width:60px;height:60px;border-radius:16px;
  background:transparent;
  display:flex;align-items:center;justify-content:center;
  font-size:26px;margin:0 auto 20px;
  box-shadow:var(--shadow-amber);
  animation:pl-pulse 2s ease infinite;
}
@keyframes pl-pulse{0%,100%{box-shadow:0 4px 14px rgba(245,158,11,.3);}50%{box-shadow:0 8px 24px rgba(245,158,11,.5);}}
.im-pl-title{font-size:1.3rem;font-weight:800;color:var(--text-primary);letter-spacing:-0.03em;margin-bottom:5px;}
.im-pl-sub{font-size:13px;color:var(--text-muted);margin-bottom:24px;}
.im-pl-bar-wrap{width:240px;height:3px;background:var(--border-light);border-radius:99px;overflow:hidden;margin:0 auto 10px;}
.im-pl-bar{height:100%;border-radius:99px;width:0%;background:var(--amber);animation:pl-fill 22s cubic-bezier(.4,0,.2,1) forwards;}
@keyframes pl-fill{from{width:0%}15%{width:18%}35%{width:42%}55%{width:61%}75%{width:78%}to{width:92%}}
.im-pl-status{font-size:11px;color:var(--text-muted);font-weight:500;transition:opacity .2s;margin-bottom:20px;}
.im-pl-steps{display:flex;gap:20px;align-items:flex-start;justify-content:center;margin-top:4px;flex-wrap:wrap;max-width:360px;}
.im-pl-step{display:flex;flex-direction:column;align-items:center;gap:5px;font-size:9.5px;color:var(--text-faint);font-weight:600;text-transform:uppercase;letter-spacing:.08em;transition:color .4s;}
.im-pl-step-dot{width:22px;height:22px;border-radius:50%;background:var(--bg-secondary);border:1.5px solid var(--border-light);display:flex;align-items:center;justify-content:center;font-size:10px;transition:all .4s;}
.im-pl-step.done .im-pl-step-dot{background:var(--green);border-color:var(--green);color:#fff;}
.im-pl-step.active .im-pl-step-dot{background:var(--amber);border-color:var(--amber);color:#fff;box-shadow:0 0 0 3px rgba(245,158,11,.2);animation:pl-pulse 1.5s ease infinite;}
.im-pl-step.done{color:var(--green-text);}
.im-pl-step.active{color:var(--amber-dark);}
</style>
"""

_LOADING_STEPS_JS = """
<script>
(function(){
  var steps=["embed","vec","llm","graph","ready"];
  var timings=[0,5000,9000,14000,19000];
  var msgs=["Initialising embedding model…","Loading vector store…","Warming up LLM…","Building graph index…","Almost ready…"];
  var el_st=document.getElementById("im-pl-st");
  function setStep(n){
    steps.forEach(function(id,i){
      var el=document.getElementById("im-step-"+id);if(!el)return;
      el.className="im-pl-step"+(i<n?" done":i===n?" active":"");
    });
    if(el_st&&msgs[n]){el_st.style.opacity=0;setTimeout(function(){el_st.textContent=msgs[n];el_st.style.opacity=1;},150);}
  }
  setStep(0);timings.forEach(function(t,i){setTimeout(function(){setStep(i);},t);});
})();
</script>
"""


def loading_screen(title: str = "Loading AI engine", sub: str = "First load takes ~25s, then instant."):
    ph = st.empty()
    _steps_html = (
        '<div class="im-pl-steps" role="list" aria-label="Loading steps">'
        '<div class="im-pl-step" id="im-step-embed" role="listitem"><div class="im-pl-step-dot">①</div><span>Embed</span></div>'
        '<div class="im-pl-step" id="im-step-vec"   role="listitem"><div class="im-pl-step-dot">②</div><span>Vector</span></div>'
        '<div class="im-pl-step" id="im-step-llm"   role="listitem"><div class="im-pl-step-dot">③</div><span>LLM</span></div>'
        '<div class="im-pl-step" id="im-step-graph" role="listitem"><div class="im-pl-step-dot">④</div><span>Graph</span></div>'
        '<div class="im-pl-step" id="im-step-ready" role="listitem"><div class="im-pl-step-dot">⑤</div><span>Ready</span></div>'
        '</div>'
    )
    ph.markdown(
        _LOADING_SCREEN_CSS +
        f'<div class="im-page-loader" role="status" aria-live="polite">'
        f'<div class="im-pl-logo" aria-hidden="true" style="background:transparent!important;display:flex;align-items:center;justify-content:center;">{logo_img_tag(60)}</div>'
        f'<div class="im-pl-title">{html_lib.escape(title)}</div>'
        f'<div class="im-pl-sub">{html_lib.escape(sub)}</div>'
        f'<div class="im-pl-bar-wrap" role="progressbar" aria-valuemin="0" aria-valuemax="100">'
        f'<div class="im-pl-bar"></div></div>'
        f'<div class="im-pl-status" id="im-pl-st" aria-live="polite">Initialising models…</div>'
        f'{_steps_html}'
        f'{_LOADING_STEPS_JS}'
        f'</div>',
        unsafe_allow_html=True,
    )
    return ph


def inject_css(loading_logo: str = ""):
    st.markdown(
        '<meta name="referrer" content="strict-origin-when-cross-origin">'
        '<meta http-equiv="X-Content-Type-Options" content="nosniff">'
        + INDUSTRIAL_CSS +
        '<a class="im-skip-link" href="#main-content" tabindex="0">Skip to main content</a>'
        '<div id="main-content" tabindex="-1" style="outline:none"></div>',
        unsafe_allow_html=True,
    )
    # Inject real JS via components (runs in iframe with parent DOM access)
    import streamlit.components.v1 as components
    _loading_js = ""
    if loading_logo:
        _ls = loading_logo.replace("\\", "\\\\").replace("`", "\\`")
        _loading_js = (
            "\n(function(){\n"
            "var LOGO_SRC=`" + _ls + "`;\n"
            "var doc=window.parent.document;\n"
            "var old=doc.getElementById('iml');if(old)old.remove();\n"
            "var old2=doc.getElementById('iml-style');if(old2)old2.remove();\n"
            "var s=doc.createElement('style');s.id='iml-style';\n"
            "s.textContent='#iml{position:fixed;inset:0;z-index:99999;background:radial-gradient(ellipse at 20% 50%,#0f1923 0%,#060a0f 60%,#000 100%);display:flex;align-items:center;justify-content:center;font-family:-apple-system,sans-serif;overflow:hidden;}'\n"
            "+'@keyframes fadeIn{from{opacity:0}to{opacity:1}}@keyframes slideUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:none}}@keyframes floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}@keyframes rotateBorder{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}@keyframes particleDrift{0%{transform:translateY(0) translateX(0);opacity:0}10%{opacity:1}90%{opacity:1}100%{transform:translateY(-120vh) translateX(40px);opacity:0}}@keyframes scanLine{0%{top:-10%}100%{top:110%}}@keyframes textGlow{0%,100%{text-shadow:0 0 20px rgba(245,158,11,.3)}50%{text-shadow:0 0 40px rgba(245,158,11,.7)}}'\n"
            "+'#iml{animation:fadeIn .3s ease;}#iml-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(245,158,11,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(245,158,11,.04) 1px,transparent 1px);background-size:60px 60px;}'\n"
            "+'#iml-scan{position:absolute;left:0;right:0;height:2px;top:-10%;background:linear-gradient(90deg,transparent,rgba(245,158,11,.4),transparent);animation:scanLine 4s linear infinite;}'\n"
            "+'.iml-corner{position:absolute;width:60px;height:60px;}.iml-corner::before,.iml-corner::after{content:\"\";position:absolute;background:rgba(245,158,11,.5);}.iml-corner::before{width:2px;height:100%;top:0;left:0;}.iml-corner::after{width:100%;height:2px;top:0;left:0;}'\n"
            "+'.iml-corner.tl{top:24px;left:24px;}.iml-corner.tr{top:24px;right:24px;transform:scaleX(-1);}.iml-corner.bl{bottom:24px;left:24px;transform:scaleY(-1);}.iml-corner.br{bottom:24px;right:24px;transform:scale(-1);}'\n"
            "+'#iml-c{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center;width:100%;max-width:560px;padding:0 24px;text-align:center;animation:slideUp .6s cubic-bezier(.16,1,.3,1) .1s both;}'\n"
            "+'#iml-logo-wrap{position:relative;width:130px;height:130px;margin:0 auto 28px;display:flex;align-items:center;justify-content:center;animation:floatY 3s ease-in-out infinite;}'\n"
            "+'#iml-logo-wrap img{width:130px;height:130px;object-fit:contain;display:block;z-index:2;filter:drop-shadow(0 0 28px rgba(245,158,11,0.8));}'\n"
            "+'#iml-ring{position:absolute;inset:-8px;border-radius:50%;border:1.5px solid transparent;background:linear-gradient(#060a0f,#060a0f) padding-box,conic-gradient(from 0deg,rgba(245,158,11,0),rgba(245,158,11,.8),rgba(245,158,11,0)) border-box;animation:rotateBorder 3s linear infinite;}'\n"
            "+'#iml-ring2{position:absolute;inset:-16px;border-radius:50%;border:1px solid transparent;background:linear-gradient(#060a0f,#060a0f) padding-box,conic-gradient(from 180deg,rgba(245,158,11,0),rgba(245,158,11,.3),rgba(245,158,11,0)) border-box;animation:rotateBorder 5s linear infinite reverse;}'\n"
            "+'#iml-badge{display:inline-flex;align-items:center;gap:8px;font-size:10px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#F59E0B;background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.25);padding:5px 16px;border-radius:99px;margin-bottom:20px;}'\n"
            "+'#iml-badge-dot{width:6px;height:6px;border-radius:50%;background:#F59E0B;animation:pulse 1.5s ease infinite;}'\n"
            "+'#iml-title{font-size:clamp(36px,5vw,56px);font-weight:900;letter-spacing:-.04em;line-height:1;margin-bottom:12px;animation:textGlow 3s ease-in-out infinite;}'\n"
            "+'#iml-title span.w{color:#FFF;}#iml-title span.a{color:#F59E0B;}'\n"
            "+'#iml-sub{font-size:14px;color:rgba(255,255,255,.4);margin-bottom:36px;}'\n"
            "+'#iml-prog-area{width:100%;margin-bottom:32px;}#iml-msg{font-size:13px;color:rgba(255,255,255,.6);margin-bottom:14px;min-height:18px;transition:opacity .3s;}'\n"
            "+'#iml-bar-wrap{width:100%;height:3px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden;margin-bottom:8px;}#iml-bar{height:100%;border-radius:99px;width:0%;background:linear-gradient(90deg,#D97706,#F59E0B,#FCD34D);transition:width .6s;}'\n"
            "+'#iml-prog-row{display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,.25);}#iml-pct{color:#F59E0B;font-weight:700;}'\n"
            "+'#iml-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;width:100%;background:rgba(255,255,255,.06);border-radius:14px;overflow:hidden;border:1px solid rgba(255,255,255,.07);margin-bottom:28px;}'\n"
            "+'.iml-stat{padding:16px 12px;background:#060a0f;text-align:center;}.iml-stat-v{font-size:22px;font-weight:800;color:#F59E0B;margin-bottom:4px;}.iml-stat-l{font-size:9px;font-weight:600;color:rgba(255,255,255,.3);text-transform:uppercase;letter-spacing:.12em;}'\n"
            "+'#iml-steps{display:flex;align-items:center;width:100%;margin-bottom:24px;}.iml-step{display:flex;flex-direction:column;align-items:center;flex:1;position:relative;}.iml-step:not(:last-child)::after{content:\"\";position:absolute;top:10px;left:50%;width:100%;height:1px;background:rgba(255,255,255,.08);}'\n"
            "+'.iml-step.done:not(:last-child)::after{background:rgba(245,158,11,.4);}.iml-step-dot{width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,.06);border:1.5px solid rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center;font-size:8px;color:rgba(255,255,255,.3);margin-bottom:6px;position:relative;z-index:1;}'\n"
            "+'.iml-step.done .iml-step-dot{background:rgba(245,158,11,.15);border-color:#F59E0B;color:#F59E0B;}.iml-step.act .iml-step-dot{background:#F59E0B;border-color:#F59E0B;color:#000;}'\n"
            "+'.iml-step-lbl{font-size:8.5px;font-weight:600;color:rgba(255,255,255,.2);text-transform:uppercase;}.iml-step.done .iml-step-lbl{color:rgba(245,158,11,.6);}.iml-step.act .iml-step-lbl{color:#F59E0B;}'\n"
            "+'#iml-footer{font-size:11px;color:rgba(255,255,255,.18);}.iml-particle{position:absolute;bottom:-20px;border-radius:50%;background:rgba(245,158,11,.6);animation:particleDrift linear infinite;}';\n"
            "doc.head.appendChild(s);\n"
            "var logoHTML=LOGO_SRC?'<img src=\"'+LOGO_SRC+'\" style=\"width:130px;height:130px;object-fit:contain;\" alt=\"IndustrialMind\"/>':'<div style=\"width:130px;height:130px;background:linear-gradient(135deg,#F59E0B,#D97706);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:900;color:#fff;\">IM</div>';\n"
            "var div=doc.createElement('div');div.id='iml';\n"
            "div.innerHTML='<div id=\"iml-bg\"><div id=\"iml-grid\"></div><div id=\"iml-scan\"></div><div class=\"iml-corner tl\"></div><div class=\"iml-corner tr\"></div><div class=\"iml-corner bl\"></div><div class=\"iml-corner br\"></div></div>'\n"
            "+'<div id=\"iml-c\"><div id=\"iml-logo-wrap\"><div id=\"iml-ring\"></div><div id=\"iml-ring2\"></div>'+logoHTML+'</div>'\n"
            "+'<div id=\"iml-badge\"><div id=\"iml-badge-dot\"></div>Enterprise AI Platform</div>'\n"
            "+'<div id=\"iml-title\"><span class=\"w\">Industrial</span><span class=\"a\">Mind</span></div>'\n"
            "+'<div id=\"iml-sub\">Enterprise AI Operating System for Heavy Industries</div>'\n"
            "+'<div id=\"iml-prog-area\"><div id=\"iml-msg\">Initializing AI services...</div><div id=\"iml-bar-wrap\"><div id=\"iml-bar\"></div></div><div id=\"iml-prog-row\"><span id=\"iml-stage-lbl\">Starting up</span><span id=\"iml-pct\">0%</span></div></div>'\n"
            "+'<div id=\"iml-stats\"><div class=\"iml-stat\"><div class=\"iml-stat-v\" id=\"_mn\">\\u2014</div><div class=\"iml-stat-l\">Graph Nodes</div></div><div class=\"iml-stat\"><div class=\"iml-stat-v\" id=\"_mr\">\\u2014</div><div class=\"iml-stat-l\">Relationships</div></div><div class=\"iml-stat\"><div class=\"iml-stat-v\" id=\"_mc\">\\u2014</div><div class=\"iml-stat-l\">Chunks</div></div><div class=\"iml-stat\"><div class=\"iml-stat-v\" id=\"_md\">\\u2014</div><div class=\"iml-stat-l\">Documents</div></div></div>'\n"
            "+'<div id=\"iml-steps\"></div><div id=\"iml-footer\">Groq Llama 3.3 70B &nbsp;&middot;&nbsp; ChromaDB &nbsp;&middot;&nbsp; sentence-transformers</div></div>';\n"
            "doc.body.appendChild(div);\n"
            "var bg=doc.getElementById('iml-bg');if(bg){for(var k=0;k<12;k++){var pp=doc.createElement('div');pp.className='iml-particle';var sz=Math.random()*3+1;pp.style.cssText='width:'+sz+'px;height:'+sz+'px;left:'+(Math.random()*100)+'%;opacity:0;animation-duration:'+(Math.random()*12+8)+'s;animation-delay:'+(Math.random()*6)+'s;';bg.appendChild(pp);}}\n"
            "var STEPS=[['\\u2460','Embed'],['\\u2461','Vector'],['\\u2462','LLM'],['\\u2463','Graph'],['\\u2464','Ready']];\n"
            "var MSGS=['Initializing AI services...','Loading embedding model...','Connecting to vector store...','Warming up Llama 3.3 70B...','Building knowledge graph...','Almost ready...'];\n"
            "var STAGES=['Starting up','Embedding engine','Vector store','LLM connection','Graph builder','System ready'];\n"
            "var TL=[{t:600,p:12},{t:3000,p:28},{t:7000,p:48},{t:11000,p:65},{t:15000,p:80},{t:19000,p:95}];\n"
            "var stepsEl=doc.getElementById('iml-steps');\n"
            "if(stepsEl){stepsEl.innerHTML=STEPS.map(function(ss,i){return'<div class=\"iml-step\" id=\"ist'+i+'\"><div class=\"iml-step-dot\">'+ss[0]+'</div><div class=\"iml-step-lbl\">'+ss[1]+'</div></div>';}).join('');}\n"
            "function setStep(n){STEPS.forEach(function(_,i){var el=doc.getElementById('ist'+i);if(!el)return;el.className='iml-step'+(i<n?' done':i===n?' act':'');});}\n"
            "var pct=0,tgt=0;\n"
            "TL.forEach(function(x,i){setTimeout(function(){tgt=x.p;setStep(i);var ml=doc.getElementById('iml-stage-lbl');if(ml)ml.textContent=STAGES[i]||'';var mm=doc.getElementById('iml-msg');if(mm){mm.style.opacity=0;setTimeout(function(){mm.textContent=MSGS[i]||'';mm.style.opacity=1;},200);}},x.t);});\n"
            "setInterval(function(){if(pct<tgt){pct=Math.min(pct+.5,tgt);}var b=doc.getElementById('iml-bar'),pp2=doc.getElementById('iml-pct');if(b)b.style.width=pct+'%';if(pp2)pp2.textContent=Math.round(pct)+'%';},20);\n"
            "function cu(id,n){var el=doc.getElementById(id);if(!el)return;var v=0,step=Math.max(1,Math.ceil(n/40));var iv=setInterval(function(){v=Math.min(v+step,n);el.textContent=v;if(v>=n)clearInterval(iv);},35);}\n"
            "setTimeout(function(){cu('_mn',160);cu('_mr',511);cu('_mc',112);cu('_md',19);},800);\n"
            "var chk=setInterval(function(){var main=doc.querySelector('[data-testid=\"stMain\"] [data-testid=\"stVerticalBlock\"]');if(main&&main.children.length>2){var ov=doc.getElementById('iml');if(ov){ov.style.transition='opacity .4s';ov.style.opacity='0';setTimeout(function(){ov.remove();var ss=doc.getElementById('iml-style');if(ss)ss.remove();},420);}clearInterval(chk);}},200);\n"
            "setTimeout(function(){clearInterval(chk);var ov=doc.getElementById('iml');if(ov)ov.remove();},25000);\n"
            "})();\n"
        )
    components.html("""
<script>
(function(){
  var doc = window.parent.document;

  /* ── 1. Inject a <style> directly into the parent page <head> ── */
  /* This beats emotion-cache because it's the LAST stylesheet added */
  function injectHeadStyle(){
    var id = 'im-zero-gap-v2';
    if(doc.getElementById(id)) return;
    var s = doc.createElement('style');
    s.id = id;
    s.textContent = [
      'section[data-testid="stMain"]{padding-top:0!important;margin-top:0!important;}',
      'section[data-testid="stMain"]>div{padding-top:0!important;margin-top:0!important;}',
      'section[data-testid="stMain"]>div>div{padding-top:0!important;margin-top:0!important;}',
      'section[data-testid="stMain"]>div>div>div{padding-top:0!important;margin-top:0!important;}',
      '[data-testid="stAppViewBlockContainer"]{padding-top:0!important;margin-top:0!important;}',
      '[data-testid="stMainBlockContainer"]{padding-top:0!important;margin-top:0!important;}',
      '[data-testid="stMainBlockContainer"]>div{padding-top:0!important;margin-top:0!important;}',
      '.main{padding-top:0!important;margin-top:0!important;}',
      '.main>div{padding-top:0!important;margin-top:0!important;}',
      '.block-container{padding-top:0.75rem!important;margin-top:0!important;}',
      /* collapse residual st.empty() placeholder containers after loading screen clears */
      '[data-testid="stEmpty"]{height:0!important;min-height:0!important;max-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;}',
      /* force nav link colors so emotion-cache anchor reset can\'t override */
      'a.im-nav-link{color:rgba(255,255,255,0.50)!important;text-decoration:none!important;}',
      'a.im-nav-link:hover{color:rgba(255,255,255,0.88)!important;}',
      'a.im-nav-link.active{color:#F59E0B!important;}',
      /* collapse iframe wrapper containers that hold background JS iframes */
      '[data-testid="stCustomComponentV1"]:has(iframe[height="0"]){height:0!important;min-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;}',
      '[data-testid="stCustomComponentV1"]:has(iframe[height="1"]){height:0!important;min-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;}',
      '[data-testid="stElementContainer"]:has(iframe[height="0"]){height:0!important;min-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;}',
      '[data-testid="stElementContainer"]:has(iframe[height="1"]){height:0!important;min-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;}',
      '.stElementContainer:has(iframe[height="0"]){height:0!important;min-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;}',
      '.stElementContainer:has(iframe[height="1"]){height:0!important;min-height:0!important;overflow:hidden!important;margin:0!important;padding:0!important;}',
    ].join('');
    doc.head.appendChild(s);
  }

  /* ── 2. Force padding-top via inline style on every wrapper ── */
  /* inline style.setProperty('x','0','important') beats all CSS */
  function forceZeroGap(){
    var sels = [
      'section[data-testid="stMain"]',
      'section[data-testid="stMain"]>div',
      'section[data-testid="stMain"]>div>div',
      '[data-testid="stAppViewBlockContainer"]',
      '[data-testid="stMainBlockContainer"]',
      '[data-testid="stMainBlockContainer"]>div',
    ];
    sels.forEach(function(sel){
      doc.querySelectorAll(sel).forEach(function(el){
        el.style.setProperty('padding-top','0','important');
        el.style.setProperty('margin-top', '0','important');
      });
    });
  }

  /* ── 3. Sidebar collapse ── */
  function applyLayout(){
    var sb   = doc.querySelector('section[data-testid="stSidebar"]');
    var main = doc.querySelector('section[data-testid="stMain"]');
    if(!sb||!main) return;
    main.style.setProperty('flex','1 1 0%','important');
    main.style.setProperty('min-width','0','important');
    var collapsed = sb.getAttribute('aria-expanded')==='false';
    if(collapsed){
      sb.style.setProperty('width','0','important');
      sb.style.setProperty('min-width','0','important');
      sb.style.setProperty('overflow','hidden','important');
      sb.style.removeProperty('visibility');
    } else {
      sb.style.removeProperty('width');
      sb.style.removeProperty('min-width');
      sb.style.removeProperty('overflow');
      sb.style.removeProperty('visibility');
    }
  }

  function collapseJsIframes(){
    doc.querySelectorAll('iframe[height="0"],iframe[height="1"]').forEach(function(fr){
      var p=fr.parentElement;
      while(p&&p!==doc.body){
        var tid=p.getAttribute('data-testid')||'';
        if(tid==='stElementContainer'||tid==='stCustomComponentV1'||p.classList.contains('stElementContainer')){
          p.style.setProperty('height','0','important');
          p.style.setProperty('min-height','0','important');
          p.style.setProperty('max-height','0','important');
          p.style.setProperty('overflow','hidden','important');
          p.style.setProperty('margin','0','important');
          p.style.setProperty('padding','0','important');
        }
        p=p.parentElement;
      }
    });
  }

  function forceChatBorder(){
    doc.querySelectorAll('[data-testid="stChatInput"]').forEach(function(el){
      el.style.setProperty('border','2px solid #1e293b','important');
      el.style.setProperty('border-radius','12px','important');
      el.style.setProperty('box-shadow','0 2px 8px rgba(0,0,0,0.18)','important');
    });
  }

  function tick(){ injectHeadStyle(); forceZeroGap(); applyLayout(); forceChatBorder(); collapseJsIframes(); }

  /* Re-inject if emotion-cache removes our style tag */
  new MutationObserver(function(){
    if(!doc.getElementById('im-zero-gap-v2')) injectHeadStyle();
    forceZeroGap();
  }).observe(doc.head, {childList:true, subtree:false});

  tick();
  setInterval(tick, 80);
})();
</script>
""" + _loading_js, height=1, scrolling=False)


def sidebar_logo():
    _logo_img = (
        f'<img src="data:image/png;base64,{_LOGO_B64}" '
        'style="display:block;width:120px;height:120px;object-fit:contain;'
        'border-radius:28px;position:relative;z-index:2;" '
        'alt="IndustrialMind logo">'
    ) if _LOGO_B64 else (
        '<div style="width:120px;height:120px;background:linear-gradient(135deg,#F59E0B,#D97706);'
        'border-radius:28px;display:flex;align-items:center;justify-content:center;'
        'font-weight:900;color:#fff;font-size:42px;">IM</div>'
    )
    st.sidebar.markdown(
        '<style>'
        '@keyframes im-dot{'
        '0%,100%{opacity:1;box-shadow:0 0 4px #F59E0B;}'
        '50%{opacity:.35;box-shadow:none;}'
        '}'
        '.im-logo-section{'
        'display:flex;flex-direction:column;align-items:center;'
        'padding:24px 12px 14px;'
        'background:linear-gradient(180deg,rgba(245,158,11,0.05) 0%,transparent 80%);'
        'border-bottom:1px solid rgba(245,158,11,0.15);'
        'margin-bottom:4px;'
        '}'
        '.im-logo-frame{'
        'position:relative;'
        'width:128px;height:128px;'
        'display:flex;align-items:center;justify-content:center;'
        'margin-bottom:12px;'
        '}'
        '.im-logo-border{'
        'position:absolute;inset:0;border-radius:30px;'
        'border:1.5px solid rgba(245,158,11,0.5);'
        'box-shadow:0 0 16px rgba(245,158,11,0.18),0 4px 24px rgba(0,0,0,0.4);'
        'pointer-events:none;'
        '}'
        '.im-logo-shadow{'
        'position:absolute;bottom:-8px;left:50%;transform:translateX(-50%);'
        'width:80px;height:12px;border-radius:50%;'
        'background:rgba(245,158,11,0.18);'
        'filter:blur(6px);'
        '}'
        '.im-brand{'
        'font-size:17px;font-weight:800;letter-spacing:-0.03em;'
        'margin-bottom:3px;text-align:center;'
        'background:linear-gradient(135deg,#fff 20%,#FDE68A 60%,#F59E0B 100%);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'background-clip:text;'
        '}'
        '.im-tagline{'
        'font-size:8.5px;font-weight:600;letter-spacing:0.13em;'
        'color:rgba(255,255,255,0.32);text-transform:uppercase;'
        'text-align:center;margin-bottom:10px;'
        '}'
        '.im-badge{'
        'display:inline-flex;align-items:center;gap:5px;'
        'background:rgba(245,158,11,0.1);'
        'border:1px solid rgba(245,158,11,0.28);'
        'border-radius:99px;padding:3px 10px;'
        '}'
        '.im-badge-dot{'
        'width:5px;height:5px;border-radius:50%;background:#F59E0B;flex-shrink:0;'
        'animation:im-dot 2.2s ease-in-out infinite;'
        '}'
        '.im-badge-text{'
        'font-size:9px;font-weight:700;color:rgba(255,255,255,0.6);letter-spacing:0.04em;'
        '}'
        '</style>'

        '<div class="im-logo-section">'
        '<div class="im-logo-frame">'
        '<div class="im-logo-shadow"></div>'
        f'{_logo_img}'
        '<div class="im-logo-border"></div>'
        '</div>'
        '<div class="im-brand">IndustrialMind</div>'
        '<div class="im-tagline">Enterprise AI · Heavy Industry</div>'
        '<div class="im-badge">'
        '<div class="im-badge-dot"></div>'
        '<span class="im-badge-text">ET Hackathon 2026 · PS-8</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def sidebar_nav(active: str = ""):
    nav_pages = [
        ("upload",   "Upload Documents",  "/Upload"),
        ("chat",     "AI Copilot",        "/Copilot"),
        ("graph",    "Knowledge Graph",   "/Graph"),
        ("shield",   "Compliance Audit",  "/Compliance"),
        ("activity", "Pattern Analysis",  "/Patterns"),
        ("brain",    "Knowledge Capture", "/Knowledge_Capture"),
        ("wrench",   "Work Orders",       "/Work_Orders"),
    ]
    _active_slug = active.strip("/").lower()
    links = (
        '<nav role="navigation" aria-label="Main navigation">'
        '<div class="im-nav-section">'
        '<span class="im-nav-label" aria-hidden="true">Platform</span>'
    )
    for icon_key, label, href in nav_pages:
        svg = ICONS.get(icon_key, ICONS["file"])
        _slug = href.strip("/").lower()
        _is_active = _active_slug and _active_slug == _slug
        _cls = "im-nav-link active" if _is_active else "im-nav-link"
        _aria = ' aria-current="page"' if _is_active else ""
        _svg_hidden = svg.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
        # Inline color beats Emotion's .st-emotion-cache-* a selector (class+element wins over class+element,
        # but inline style specificity 1,0,0,0 beats all class-based rules unconditionally)
        _color = "#F59E0B" if _is_active else "rgba(255,255,255,0.50)"
        links += (
            f'<a class="{_cls}" href="{href}" target="_self"{_aria}'
            f' style="color:{_color};text-decoration:none">'
            f'{_svg_hidden}<span>{label}</span></a>'
        )
    links += '</div>'
    links += '<div class="im-nav-divider" role="separator"></div>'
    links += (
        '<div class="im-sidebar-status" role="status" aria-live="polite">'
        '<span class="im-sidebar-status-dot" aria-hidden="true"></span>'
        '<span class="im-sidebar-status-text">System online</span>'
        '</div>'
    )
    links += '</nav>'
    st.sidebar.markdown(links, unsafe_allow_html=True)


def page_hero(title: str, subtitle: str = "", eyebrow: str = "", icon: str = ""):
    ey = f'<div class="im-eyebrow">{html_lib.escape(eyebrow)}</div>' if eyebrow else ""
    sub = f'<div class="im-page-sub">{html_lib.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<header class="im-page-header" aria-label="{html_lib.escape(title)}">'
        f'{ey}'
        f'<h1 class="im-page-title">{html_lib.escape(title)}</h1>'
        f'{sub}<div class="im-divider" role="separator"></div></header>',
        unsafe_allow_html=True,
    )


def render_feature_card(icon_key: str, title: str, desc: str, tag: str = "",
                        bg: str = "#F4F4F5", color: str = "#6B7280"):
    svg = ICONS.get(icon_key, ICONS["zap"])
    tag_html = f'<div class="im-feat-tag">{html_lib.escape(tag)}</div>' if tag else ""
    st.markdown(
        f'<div class="im-feat">'
        f'<div class="im-feat-icon" style="color:{color}">{svg}</div>'
        f'<div class="im-feat-title">{html_lib.escape(title)}</div>'
        f'<div class="im-feat-desc">{html_lib.escape(desc)}</div>'
        f'{tag_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, icon: str = "",
                       accent: str = "var(--amber)", sub: str = ""):
    sub_html = f'<div class="metric-sub">{html_lib.escape(sub)}</div>' if sub else ""
    _safe_title = html_lib.escape(title)
    _safe_val = html_lib.escape(str(value))
    st.markdown(
        f'<div class="metric-card" role="region" aria-label="{_safe_title}: {_safe_val}">'
        f'<div class="metric-card-bar" style="background:{accent}"></div>'
        f'<div class="metric-value">{_safe_val}</div>'
        f'<div class="metric-label">{_safe_title}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_source_citation(source: Dict):
    filename = Path(source.get("source_file", "")).name or "Unknown"
    page = source.get("page_num", "?")
    score = source.get("score", 0)
    text_safe = html_lib.escape(source.get("text", "")[:300])
    file_safe = html_lib.escape(filename)
    st.markdown(
        f'<div class="source-box">'
        f'<span class="source-file">{file_safe}</span>'
        f'<span class="source-meta"> · p.{page} · {score:.0%}</span>'
        f'<div class="source-text">{text_safe}…</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_answer_with_citations(answer: str, sources: List[Dict], response_time: float = None):
    st.markdown(answer)
    if response_time is not None:
        st.caption(f"Response time: {response_time:.1f}s")
    if sources:
        with st.expander(f"{len(sources)} source{'s' if len(sources) > 1 else ''}", expanded=False):
            for s in sources:
                render_source_citation(s)


def render_gap_card(gap: Dict):
    severity = gap.get("severity", "Unknown")
    pill_cls = {"Critical": "pill-red", "High": "pill-red", "Medium": "pill-amber", "Low": "pill-green"}.get(severity, "pill-gray")
    req = html_lib.escape(gap.get("requirement", ""))
    desc = html_lib.escape(gap.get("gap_description", ""))
    rec = html_lib.escape(gap.get("recommendation", ""))
    st.markdown(
        f'<div class="gap-card">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
        f'<div class="gap-card-title">{req}</div>'
        f'<span class="pill {pill_cls}">{severity}</span>'
        f'</div>'
        f'<div class="gap-card-desc">{desc}</div>'
        f'<div class="gap-fix">Recommendation: {rec}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_pattern_card(pattern: Dict):
    equip = html_lib.escape(", ".join(pattern.get("affected_equipment", [])[:4]))
    fm = html_lib.escape(pattern.get("failure_mode", "").replace("_", " ").title())
    count = pattern.get("occurrence_count", 0)
    body = html_lib.escape(pattern.get("pattern_summary", ""))
    rec = html_lib.escape(pattern.get("recommendation", ""))
    st.markdown(
        f'<div class="pattern-card">'
        f'<div class="pattern-title">{fm}</div>'
        f'<div class="pattern-count">{count} occurrences · {equip}</div>'
        f'<div class="pattern-body">{body}</div>'
        f'<div class="pattern-rec">{rec}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_knowledge_card(entry: Dict):
    ktype = html_lib.escape(entry.get("knowledge_type", "").replace("_", " "))
    title = html_lib.escape(entry.get("title", ""))
    content = html_lib.escape(entry.get("content", "")[:350])
    expert = html_lib.escape(entry.get("expert_name", ""))
    equip = html_lib.escape(", ".join(entry.get("equipment_ids", []) or ["General"]))
    st.markdown(
        f'<div class="knowledge-card">'
        f'<span class="knowledge-type">{ktype}</span>'
        f'<div class="knowledge-title">{title}</div>'
        f'<div class="knowledge-content">{content}</div>'
        f'<div class="knowledge-meta">{expert} · {equip}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_chart_card_header(title: str, badge: str = ""):
    badge_html = (
        f'<span class="chart-card-badge">{html_lib.escape(badge)}</span>' if badge else ""
    )
    st.markdown(
        f'<div class="chart-card-header">'
        f'<div class="chart-card-title">{html_lib.escape(title)}</div>'
        f'{badge_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def plotly_defaults(height: int = 280) -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FAFAFB",
        height=height,
        margin=dict(t=16, b=16, l=8, r=8),
        font=dict(family="Inter,-apple-system,BlinkMacSystemFont,sans-serif", size=11, color="#6B7280"),
        xaxis=dict(gridcolor="#D1D5DB", linecolor="#D1D5DB", zerolinecolor="#D1D5DB", tickfont=dict(size=11, color="#9CA3AF")),
        yaxis=dict(gridcolor="#D1D5DB", linecolor="#D1D5DB", zerolinecolor="#D1D5DB", tickfont=dict(size=11, color="#9CA3AF")),
        hoverlabel=dict(bgcolor="#111827", font_color="#ffffff", font_size=12, bordercolor="#111827"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#6B7280")),
    )


def no_docs_warning():
    st.markdown(
        '<div class="empty-state" role="alert" aria-live="polite">'
        '<div class="empty-state-icon">📂</div>'
        '<div class="empty-state-title">No documents indexed yet</div>'
        '<div class="empty-state-body">'
        'Go to <b>Upload Documents</b> in the sidebar, or run '
        '<code>python seed_data.py</code> to load demo plant data instantly.'
        '</div>'
        '<div style="margin-top:24px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">'
        '<a href="/Upload" target="_self" style="display:inline-flex;align-items:center;gap:7px;'
        'background:#F59E0B;color:#fff;font-size:13px;font-weight:600;'
        'padding:10px 22px;border-radius:8px;text-decoration:none;'
        'box-shadow:0 4px 14px rgba(245,158,11,.3)">'
        'Upload Documents</a>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
