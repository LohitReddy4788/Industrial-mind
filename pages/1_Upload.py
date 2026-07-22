"""Page 1 — Document Intelligence Hub."""

import streamlit as st
from pathlib import Path
import html as html_lib

st.set_page_config(page_title="Upload · IndustrialMind", page_icon="📥", layout="wide", initial_sidebar_state="expanded")

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, loading_screen, render_metric_card, no_docs_warning
from app.config import DOCS_PATH

inject_css()
sidebar_logo()
with st.sidebar:
    sidebar_nav("Upload")

_lph = loading_screen()
_c  = load_for_page(["em", "gb"])
em = _c["em"]
gb = _c["gb"]
_lph.empty()

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* block-container — inherit global (1320px, 1.75rem top) */
.file-row {
    display:flex;align-items:center;justify-content:space-between;
    padding:12px 16px;border-bottom:1px solid #D1D5DB;
    transition:background .15s;border-radius:4px;
}
.file-row:hover { background:#FAFAFB; }
.file-row:last-child { border-bottom:none; }
.step-bar { display:flex;align-items:flex-start;gap:0;margin:20px 0 28px; }
.step-item { flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;position:relative; }
.step-item:not(:last-child)::after { content:'';position:absolute;top:16px;left:50%;width:100%;height:2px;background:#D1D5DB;z-index:0; }
.step-item.done:not(:last-child)::after { background:rgba(245,158,11,.4); }
.step-circle { width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;position:relative;z-index:1;transition:box-shadow .2s; }
.step-done { background:linear-gradient(135deg,#F59E0B,#D97706);color:#fff;box-shadow:0 2px 8px rgba(245,158,11,.35); }
.step-todo { background:#fff;color:#9CA3AF;border:1.5px solid #D1D5DB; }
.step-label { font-size:11px;font-weight:600;color:#374151;margin-top:8px; }
.step-desc { font-size:10px;color:#9CA3AF;margin-top:2px; }
[data-testid="stFileUploader"] section {
    background:#fff !important;border:1.5px dashed #D1D5DB !important;
    border-radius:12px !important;padding:20px 24px !important;
    transition:border-color .15s,background .15s !important;
}
[data-testid="stFileUploader"] section:hover { border-color:#F59E0B !important;background:#FFFBEB !important; }
[data-testid="stFileUploader"] section > div { color:#374151 !important; }
[data-testid="stFileUploader"] section small { color:#9CA3AF !important; }
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] span { color:#374151 !important;font-weight:600 !important; }
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"],
[data-testid="stFileUploaderDropzone"] button {
    background:#F59E0B !important;color:#fff !important;border:none !important;
    border-radius:8px !important;font-weight:600 !important;font-size:13px !important;
    box-shadow:0 3px 10px rgba(245,158,11,.3) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] svg { color:#F59E0B !important;stroke:#F59E0B !important; }
</style>
<div class="hero-wrap">
  <div class="hero-eyebrow">Document Intelligence Hub</div>
  <div class="hero-title">Upload &amp; Index Documents</div>
  <div class="hero-sub">Drop PDFs, work orders, SOPs, regulations, and incident reports. IndustrialMind automatically chunks, extracts entities, embeds, and indexes everything — ready for instant AI search.</div>
  <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── Pipeline stepper — dynamic state ──────────────────────────────────────────
_has_files   = bool(st.session_state.get("uploaded_files_state") or
                    st.session_state.get("last_ingestion_done", False))
_ingested    = st.session_state.get("last_ingestion_done", False)

def _step_html(num, label, desc, done):
    cls = "step-done" if done else "step-todo"
    txt = "✓" if done else str(num)
    return (f'<div class="step-item">'
            f'<div class="step-circle {cls}">{txt}</div>'
            f'<div class="step-label">{label}</div>'
            f'<div class="step-desc">{desc}</div>'
            f'</div>')

_steps = [
    ("Select files",    "PDF · Excel · CSV · TXT",       _has_files or _ingested),
    ("Choose category", "Maintenance / SOP / Regs",      _has_files or _ingested),
    ("Process & embed", "Text + entity extraction",       _ingested),
    ("Graph build",     "Equipment relationships",        _ingested),
    ("Ready!",          "Fully searchable AI",            _ingested),
]
st.markdown(
    '<div class="step-bar">'
    + "".join(_step_html(i+1, l, d, done) for i, (l, d, done) in enumerate(_steps))
    + '</div>',
    unsafe_allow_html=True,
)

# ── Demo data banner ──────────────────────────────────────────────────────────
_stats = em.get_stats()
if _stats.get("total_chunks", 0) > 0 and not _ingested:
    st.markdown(
        f'<div class="success-banner" style="margin-bottom:18px;display:flex;align-items:center;gap:12px">'
        f'<div style="font-size:20px;flex-shrink:0">✅</div>'
        f'<div><div style="font-size:13px;font-weight:700">Demo knowledge base loaded</div>'
        f'<div style="font-size:12px;margin-top:2px">'
        f'{_stats["total_chunks"]} knowledge chunks from {_stats.get("total_documents", "?")} documents already indexed. '
        f'You can explore all features now, or upload your own documents to replace the demo data.'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )

# ── Upload + category ──────────────────────────────────────────────────────────
col_up, col_right = st.columns([3, 2], gap="large")

with col_up:
    uploaded_files = st.file_uploader(
        "Drop files here or click to browse",
        accept_multiple_files=True,
        type=["pdf", "xlsx", "xls", "csv", "txt", "md", "docx"],
        help="PDF (text or scanned/OCR), Excel, CSV, Word (.docx), plain text",
    )

    type_map = {
        "🔧  Maintenance Record":    "maintenance",
        "📜  Regulation / Standard": "regulations",
        "⚠️  Incident Report":       "incidents",
        "📋  Procedure / SOP":       "procedures",
    }
    doc_type = st.selectbox("Document Category", list(type_map.keys()))
    folder_name = type_map[doc_type]

    tag_info = {
        "🔧  Maintenance Record":    ("🔧 Maintenance", "#d97706", "#fffbeb", "Tagged for failure analysis, equipment history, and work order briefs."),
        "📜  Regulation / Standard": ("📜 Regulations", "#2563eb", "#eff6ff", "Tagged for compliance audits, OISD-118 and Factory Act checks."),
        "⚠️  Incident Report":       ("⚠️ Incidents",   "#dc2626", "#fef2f2", "Tagged for pattern analysis, predictive alerts, and risk assessment."),
        "📋  Procedure / SOP":       ("📋 Procedures",  "#7c3aed", "#faf5ff", "Tagged for work order context, safety steps, and operator guidance."),
    }
    label, color, bg, desc = tag_info[doc_type]
    st.markdown(
        f'<div style="background:{bg};border:1.5px solid {color}30;border-radius:12px;'
        f'padding:12px 16px;font-size:13px;color:{color};margin-top:8px;line-height:1.6">'
        f'<b>{label}</b> &mdash; {desc}</div>',
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("""
    <div style="background:#fff;border:1px solid #D1D5DB;border-radius:14px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.05)">
      <div class="section-label">Supported Formats</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:34px;height:34px;background:#FAFAFB;border:1px solid #D1D5DB;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0">PDF</div>
          <div style="font-size:13px;font-weight:500;color:#111827">PDF <span style="color:#9CA3AF;font-weight:400">— text-based or scanned (OCR)</span></div>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:34px;height:34px;background:#FAFAFB;border:1px solid #D1D5DB;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#22C55E;flex-shrink:0">XLS</div>
          <div style="font-size:13px;font-weight:500;color:#111827">Excel / CSV <span style="color:#9CA3AF;font-weight:400">— work orders, inspection logs</span></div>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:34px;height:34px;background:#FAFAFB;border:1px solid #D1D5DB;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#6B7280;flex-shrink:0">TXT</div>
          <div style="font-size:13px;font-weight:500;color:#111827">TXT / Markdown <span style="color:#9CA3AF;font-weight:400">— SOPs, field notes</span></div>
        </div>
      </div>
      <div style="border-top:1px solid #D1D5DB;margin-top:14px;padding-top:12px">
        <div style="font-size:11.5px;color:#9CA3AF;line-height:1.7">
          Auto-extracted: equipment IDs, failure modes, dates, regulatory references, actions.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── File list + process ────────────────────────────────────────────────────────
if uploaded_files:
    total_kb = sum(f.size for f in uploaded_files) // 1024
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    ext_colors = {"PDF":"#d97706","XLSX":"#16a34a","XLS":"#16a34a","CSV":"#2563eb","TXT":"#7c3aed","MD":"#7c3aed"}
    _rows_html = ""
    for f in uploaded_files:
        size_kb = f.size // 1024 or 1
        ext = f.name.rsplit(".", 1)[-1].upper() if "." in f.name else "FILE"
        ec = ext_colors.get(ext, "#64748b")
        _rows_html += (
            f'<div class="file-row">'
            f'<div style="display:flex;align-items:center;gap:10px">'
            f'<span style="background:{ec}15;color:{ec};font-size:10px;font-weight:700;'
            f'padding:3px 8px;border-radius:5px;border:1px solid {ec}30">{ext}</span>'
            f'<span style="font-size:13px;color:#1e293b;font-weight:500">{html_lib.escape(f.name)}</span>'
            f'</div>'
            f'<span style="font-size:12px;color:#94a3b8">{size_kb} KB</span>'
            f'</div>'
        )
    st.markdown(
        f'<div style="background:#fff;border:1px solid #D1D5DB;border-radius:14px;padding:16px 18px;box-shadow:0 1px 3px rgba(0,0,0,.05)">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">'
        f'<div style="font-size:13px;font-weight:600;color:#111827">{len(uploaded_files)} file(s) ready to process</div>'
        f'<div style="font-size:11.5px;color:#9CA3AF;background:#FAFAFB;padding:3px 10px;border-radius:99px;border:1px solid #D1D5DB">{total_kb:,} KB</div>'
        f'</div>'
        + _rows_html +
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    if st.button("⚡ Process & Ingest Documents", type="primary", use_container_width=True):
        from app.embeddings import full_pipeline
        save_dir = Path(DOCS_PATH) / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        already_indexed = []
        for uf in uploaded_files:
            sp = save_dir / uf.name
            if sp.exists():
                already_indexed.append(uf.name)
            with open(sp, "wb") as fh:
                fh.write(uf.getbuffer())
            saved_paths.append(str(sp))

        if already_indexed:
            st.info(f"ℹ️ {len(already_indexed)} file(s) already in knowledge base (will re-index): {', '.join(already_indexed[:3])}"
                    + (" …" if len(already_indexed) > 3 else ""))

        progress = st.progress(0, text="📄 Reading documents…")
        status_ph = st.empty()
        try:
            progress.progress(10, text="📄 Extracting text…")
            status_ph.info("Step 1 / 4 — Splitting into chunks and extracting entities…")
            result = full_pipeline(file_paths=saved_paths, embedding_manager=em)

            progress.progress(55, text="🔗 Embedding into vector store…")
            status_ph.info("Step 2 / 4 — Generating embeddings and storing in ChromaDB…")

            progress.progress(75, text="🕸️ Building knowledge graph…")
            status_ph.info("Step 3 / 4 — Linking equipment, incidents and procedures…")
            if gb and result.get("entities") and result.get("chunks"):
                gb.build_from_entities(result["entities"], result["chunks"])

            progress.progress(100, text="✅ Done!")
            status_ph.empty()

            st.session_state["last_ingestion_done"] = True
            _new_count = len(saved_paths) - len(already_indexed)
            _msg = f"✅ {_new_count} new + {len(already_indexed)} re-indexed — knowledge base updated!" if already_indexed else f"✅ {len(saved_paths)} document(s) processed — knowledge base updated!"
            st.success(_msg)

            r1, r2, r3, r4 = st.columns(4)
            with r1: render_metric_card("Pages Loaded",    str(result.get("pages_loaded", 0)),              "—", accent="#2563eb")
            with r2: render_metric_card("Chunks Created",  str(result.get("chunks_created", 0)),            "—", accent="#F59E0B")
            with r3: render_metric_card("Equipment Found", str(len(result.get("equipment_found", []))),      "—", accent="#7c3aed")
            with r4: render_metric_card("Failure Modes",   str(len(result.get("failure_modes_found", []))), "—", accent="#ef4444")

            if result.get("equipment_found"):
                st.markdown('<div class="section-label" style="margin-top:14px;margin-bottom:6px">Equipment detected</div>', unsafe_allow_html=True)
                st.markdown("  ".join(f"`{e}`" for e in result["equipment_found"][:16]))
            if result.get("failure_modes_found"):
                st.markdown('<div class="section-label" style="margin-top:10px;margin-bottom:6px">Failure modes detected</div>', unsafe_allow_html=True)
                st.markdown("  ".join(f"`{f}`" for f in result["failure_modes_found"][:10]))

            st.markdown(
                '<div style="display:flex;gap:10px;margin-top:16px">'
                '<a href="/Copilot" target="_self" style="display:inline-flex;align-items:center;gap:7px;'
                'background:#F59E0B;color:#fff;font-size:13px;font-weight:700;'
                'padding:9px 18px;border-radius:9px;text-decoration:none;">Ask AI Copilot</a>'
                '<a href="/Graph" target="_self" style="display:inline-flex;align-items:center;gap:7px;'
                'background:#fff;color:#374151;font-size:13px;font-weight:600;padding:9px 18px;'
                'border-radius:9px;text-decoration:none;border:1px solid #D1D5DB">View Graph</a>'
                '</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            status_ph.empty()
            st.error(f"Processing failed: {str(e)[:300]}")
        finally:
            progress.empty()

# ── Knowledge Base stats ───────────────────────────────────────────────────────
st.markdown('<div style="height:36px"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Knowledge Base</div>', unsafe_allow_html=True)

stats = em.get_stats()
s1, s2, s3, s4 = st.columns(4)
with s1: render_metric_card("Total Chunks",  str(stats["total_chunks"]),                            "—", accent="#F59E0B")
with s2: render_metric_card("Documents",     str(stats["total_documents"]),                         "—", accent="#2563eb")
with s3: render_metric_card("Categories",    str(len(stats["doc_types"])),                          "—", accent="#10b981")
with s4: render_metric_card("Incidents",     str(stats["doc_types"].get("incidents", 0)),           "—", accent="#ef4444")

if stats.get("doc_types"):
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    type_colors = {
        "maintenance": "#d97706",
        "incidents":   "#dc2626",
        "procedures":  "#7c3aed",
        "regulations": "#2563eb",
        "general":     "#6B7280",
    }
    dcols = st.columns(len(stats["doc_types"]))
    for i, (dtype, count) in enumerate(stats["doc_types"].items()):
        color = type_colors.get(dtype, "#6B7280")
        with dcols[i]:
            st.markdown(
                f'<div style="background:#fff;border:1px solid #D1D5DB;border-radius:12px;'
                f'padding:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04)">'
                f'<div style="font-size:2rem;font-weight:800;color:#111827;letter-spacing:-0.04em;line-height:1">{count}</div>'
                f'<div style="font-size:10.5px;color:#9CA3AF;margin-top:5px;text-transform:uppercase;'
                f'letter-spacing:0.07em;font-weight:600">{dtype.title()}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ── File table ─────────────────────────────────────────────────────────────────
st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
col_title, col_filter = st.columns([3, 1])
with col_title:
    st.markdown('<div class="section-label">Files in knowledge base</div>', unsafe_allow_html=True)
with col_filter:
    filter_cat = st.selectbox("Filter", ["All", "maintenance", "incidents", "procedures", "regulations"],
                              label_visibility="collapsed")

docs_path = Path(DOCS_PATH)
if docs_path.exists():
    files = sorted(
        [f for f in docs_path.rglob("*") if f.is_file() and not f.name.startswith(".")],
        key=lambda f: f.stat().st_mtime, reverse=True,
    )
    if filter_cat != "All":
        files = [f for f in files if f.parent.name == filter_cat]

    if files:
        type_icons = {"maintenance":"🔧","incidents":"⚠️","procedures":"📋","regulations":"📜"}
        # Table header
        _h1, _h2, _h3, _h4 = st.columns([5, 1.2, 1, 0.8])
        with _h1:
            st.markdown('<div style="font-size:10.5px;font-weight:700;color:#94a3b8;text-transform:uppercase;'
                        'letter-spacing:0.08em;padding:4px 0 8px">File</div>', unsafe_allow_html=True)
        with _h2:
            st.markdown('<div style="font-size:10.5px;font-weight:700;color:#94a3b8;text-transform:uppercase;'
                        'letter-spacing:0.08em;padding:4px 0 8px">Category</div>', unsafe_allow_html=True)
        with _h3:
            st.markdown('<div style="font-size:10.5px;font-weight:700;color:#94a3b8;text-transform:uppercase;'
                        'letter-spacing:0.08em;padding:4px 0 8px">Size</div>', unsafe_allow_html=True)
        with _h4:
            st.markdown('<div style="font-size:10.5px;font-weight:700;color:#94a3b8;text-transform:uppercase;'
                        'letter-spacing:0.08em;padding:4px 0 8px"></div>', unsafe_allow_html=True)
        st.markdown('<div style="border-top:2px solid #f1f5f9;margin-bottom:2px"></div>', unsafe_allow_html=True)
        for f in files[:50]:
            cat  = f.parent.name
            icon = type_icons.get(cat, "📄")
            kb   = max(f.stat().st_size // 1024, 1)
            c1, c2, c3, c4 = st.columns([5, 1.2, 1, 0.8])
            with c1:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;padding:5px 0">'
                    f'<span>{icon}</span>'
                    f'<span style="font-size:13px;color:#1e293b;font-weight:500">{html_lib.escape(f.name)}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f'<span style="font-size:11px;color:#64748b;background:#f1f5f9;'
                    f'padding:3px 10px;border-radius:20px">{cat}</span>',
                    unsafe_allow_html=True,
                )
            with c3:
                st.markdown(f'<span style="font-size:11px;color:#94a3b8">{kb} KB</span>', unsafe_allow_html=True)
            with c4:
                if st.button("🗑️", key=f"del_{f.name}_{cat}", help="Remove from knowledge base"):
                    try:
                        em.delete_document(str(f))
                        f.unlink()
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    else:
        no_docs_warning()
else:
    no_docs_warning()


