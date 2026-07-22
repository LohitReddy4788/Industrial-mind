"""Page 6 — Expert Knowledge Capture (Killer Feature 1)."""

import html as html_lib
import streamlit as st

st.set_page_config(page_title="Knowledge Capture · IndustrialMind", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

from app.session import load_for_page
from app.ui_helpers import inject_css, sidebar_logo, sidebar_nav, loading_screen, render_knowledge_card, render_metric_card

inject_css()
sidebar_logo()
with st.sidebar:
    sidebar_nav("Knowledge_Capture")

_lph = loading_screen()
_c  = load_for_page(["em", "kca"])
kca = _c["kca"]
em = _c["em"]
_lph.empty()

st.markdown("""
<style>
.why-card {
    background: linear-gradient(135deg,#fff 0%,#FFFBF0 100%);
    border: 1px solid #D1D5DB; border-left: 3px solid #F59E0B;
    border-radius: 16px; padding: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05),0 4px 12px rgba(245,158,11,.05);
    word-break: break-word; overflow-wrap: break-word;
}
.why-quote {
    background: #FAFAFB; border-left: 3px solid #F59E0B; padding: 12px 16px;
    border-radius: 0 10px 10px 0; margin-bottom: 16px; font-size: 13.5px; color: #6B7280;
    line-height: 1.75; font-style: italic;
}
.benefit-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px; }
.capture-tag {
    background: #FAFAFB; border: 1px solid #D1D5DB; border-radius: 8px;
    padding: 9px 14px; font-size: 12.5px; color: #374151; margin: 6px 0;
    transition: background .15s, border-color .15s;
}
.capture-tag:hover { background: #FFFBEB; border-color: #FDE68A; }
.session-card {
    background: #fff; border: 1px solid #D1D5DB; border-radius: 14px;
    padding: 20px 18px; margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
    transition: box-shadow .2s, transform .2s;
}
.session-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,.08); transform: translateY(-1px); }
</style>
<div class="hero-wrap">
  <div class="hero-eyebrow">Killer Feature 1 · Knowledge Preservation</div>
  <div class="hero-title">Expert Knowledge Capture</div>
  <div class="hero-sub">25% of India's experienced engineers will retire this decade — taking decades of undocumented operational knowledge with them. IndustrialMind interviews them and preserves that knowledge forever.</div>
  <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎤 Start Interview", "📋 Session History", "📚 Knowledge Library"])

# ── Tab 1: Interview ───────────────────────────────────────────────────────────
with tab1:
    col_form, col_info = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="section-label">New Expert Interview</div>', unsafe_allow_html=True)
        expert_name = st.text_input("Expert Name *", placeholder="e.g. Rajesh Kumar")
        expert_role = st.text_input("Role / Designation *", placeholder="e.g. Senior Maintenance Engineer")
        topic = st.selectbox(
            "Interview Topic",
            ["equipment_expertise", "maintenance_wisdom", "process_knowledge"],
            format_func=lambda x: {
                "equipment_expertise": "Equipment Expertise",
                "maintenance_wisdom":  "Maintenance Wisdom",
                "process_knowledge":   "Process Knowledge",
            }[x],
        )
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        if st.button("Begin Interview", type="primary", use_container_width=True):
            if not expert_name.strip():
                st.error("Please enter the expert's name.")
            elif not expert_role.strip():
                st.error("Please enter the expert's role/designation.")
            else:
                session = kca.start_session(expert_name.strip(), expert_role.strip(), topic)
                st.session_state["active_session_id"]  = session.session_id
                st.session_state["current_question"]   = session.get_next_question()
                st.session_state["interview_chat"]     = []
                st.session_state["interview_complete"] = False
                st.rerun()

    with col_info:
        st.markdown(
            '<div class="why-card">'
            '<div class="section-label">Why This Matters</div>'
            '<div class="why-quote">"An estimated 25% of India\'s experienced industrial engineers will retire '
            'within the next decade, taking decades of undocumented operational knowledge with them."</div>'
            '<div class="benefit-row"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:1px"><polyline points="20 6 9 17 4 12"/></svg>'
            '<div style="font-size:13px;color:#374151">Structured AI interview — one focused question at a time</div></div>'
            '<div class="benefit-row"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:1px"><polyline points="20 6 9 17 4 12"/></svg>'
            '<div style="font-size:13px;color:#374151">Extracts equipment quirks, failure warning signs, undocumented procedures</div></div>'
            '<div class="benefit-row"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:1px"><polyline points="20 6 9 17 4 12"/></svg>'
            '<div style="font-size:13px;color:#374151">Stored as searchable knowledge in ChromaDB permanently</div></div>'
            '<div class="benefit-row"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:1px"><polyline points="20 6 9 17 4 12"/></svg>'
            '<div style="font-size:13px;color:#374151">Every future engineer benefits from this session forever</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    session_id = st.session_state.get("active_session_id")
    if not session_id:
        st.info("Fill the form above and click **▶️ Begin Interview** to start.")
    else:
        session = kca.get_session(session_id)
        if session is None:
            st.warning("Session not found — please start a new interview.")
        else:
            # Interview header
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;'
                f'background:#FAFAFB;border:1px solid #D1D5DB;border-radius:14px;padding:16px 20px">'
                f'<div style="width:44px;height:44px;background:#7c3aed;border-radius:12px;'
                f'display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">👷</div>'
                f'<div>'
                f'<div style="font-size:15px;font-weight:700;color:#0f172a">Interview: {html_lib.escape(session.expert_name)}</div>'
                f'<div style="font-size:12px;color:#64748b">{html_lib.escape(session.role)}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            total_q = len(session.questions)
            done_q  = min(session.question_index, total_q)
            st.progress(done_q / max(total_q, 1), text=f"Question {done_q} of {total_q} — {int(done_q/max(total_q,1)*100)}% complete")

            # Conversation history
            for item in st.session_state.get("interview_chat", []):
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f"**{item['question']}**")
                with st.chat_message("user", avatar="👷"):
                    st.markdown(item["answer"])
                if item.get("knowledge"):
                    k = item["knowledge"]
                    st.markdown(
                        f'<div class="capture-tag">✅ Captured: <b>{html_lib.escape(k.get("title",""))}</b> '
                        f'<span style="color:#059669">[{html_lib.escape(k.get("knowledge_type","").replace("_"," "))}]</span></div>',
                        unsafe_allow_html=True,
                    )

            current_q = st.session_state.get("current_question")
            complete  = st.session_state.get("interview_complete", False)

            if current_q and not complete:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f"**{current_q}**")
                answer = st.text_area(
                    "Your answer", height=130,
                    key=f"ans_{session.question_index}",
                    placeholder="Share your experience in as much detail as possible — specific values, dates, and equipment IDs are very helpful…",
                )
                col_sub, col_end = st.columns([1, 1])
                with col_sub:
                    if st.button("Submit Answer →", type="primary", use_container_width=True):
                        if not answer.strip():
                            st.warning("Please type an answer before submitting.")
                        elif len(answer.strip()) < 50:
                            st.warning("Please provide more detail (at least 50 characters). The richer the answer, the more knowledge is preserved.")
                        else:
                            with st.spinner("Extracting knowledge…"):
                                result = session.process_answer(current_q, answer.strip())
                            chat = st.session_state.get("interview_chat", [])
                            chat.append({"question": current_q, "answer": answer.strip(), "knowledge": result.get("extracted_knowledge")})
                            st.session_state["interview_chat"] = chat
                            if result["is_complete"]:
                                st.session_state["current_question"]   = None
                                st.session_state["interview_complete"] = True
                            else:
                                st.session_state["current_question"] = result["follow_up_question"]
                            st.rerun()
                with col_end:
                    if st.button("⏹ End & Save to KB", use_container_width=True):
                        st.session_state["current_question"]   = None
                        st.session_state["interview_complete"] = True
                        st.session_state["_auto_save"]         = True
                        st.rerun()

            if complete:
                entries = len(session.knowledge_entries)
                st.success(f"✅ Interview complete — {entries} knowledge entries captured.")
                st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

                auto_save = st.session_state.pop("_auto_save", False)
                if auto_save or st.button("💾 Save to Knowledge Base & Make Searchable", type="primary", use_container_width=True):
                    with st.spinner("Saving and ingesting into ChromaDB…"):
                        saved = session.finalize_and_save()
                        if saved["files_saved"]:
                            from app.embeddings import full_pipeline
                            full_pipeline(file_paths=saved["files_saved"], embedding_manager=em)
                    st.success(f"🎉 {saved['entries_captured']} entries saved — now searchable in the AI Copilot.")
                    st.session_state["interview_complete"] = False
                    st.session_state["active_session_id"]  = None
                    st.rerun()

# ── Tab 2: Session history ─────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-label" style="margin-top:4px">Past Interview Sessions</div>', unsafe_allow_html=True)
    sessions = kca.get_all_sessions_summary()

    # Also scan disk for sessions saved in previous app runs
    from pathlib import Path as _Path
    from app.config import DOCS_PATH
    _saved_sessions = []
    _maint_dir = _Path(DOCS_PATH) / "maintenance"
    if _maint_dir.exists():
        for _f in sorted(_maint_dir.glob("expert_session_summary_*.txt"), reverse=True):
            try:
                _text = _f.read_text(encoding="utf-8")
                _expert = next((l.split("Expert:")[1].strip() for l in _text.splitlines() if "Expert:" in l), "Unknown")
                _date   = next((l.split("Date:")[1].strip()[:10] for l in _text.splitlines() if l.startswith("Date:")), "")
                _topic  = next((l.split("Topic:")[1].strip() for l in _text.splitlines() if "Topic:" in l), "")
                _count  = next((l.split("Total Knowledge Entries:")[1].strip() for l in _text.splitlines() if "Total Knowledge Entries:" in l), "?")
                _sid    = _f.stem.replace("expert_session_summary_", "")
                # Only add if not already in in-memory list
                if not any(s["session_id"] == _sid for s in sessions):
                    _saved_sessions.append({"session_id": _sid, "expert": _expert, "role": "(saved)", "topic": _topic, "entries": _count, "created_at": _date})
            except Exception:
                pass
    sessions = _saved_sessions + sessions

    if not sessions:
        st.markdown(
            '<div style="text-align:center;padding:60px 32px;color:#94a3b8;font-size:14px">'
            '🎤 No sessions yet — start your first interview in the tab above.</div>',
            unsafe_allow_html=True,
        )
    else:
        for s in sessions:
            topic_label = {"equipment_expertise":"Equipment","maintenance_wisdom":"Maintenance","process_knowledge":"Process"}.get(s["topic"], s["topic"])
            st.markdown(
                f'<div class="session-card">'
                f'<div style="display:flex;align-items:center;justify-content:space-between">'
                f'<div>'
                f'<div style="font-size:15px;font-weight:700;color:#0f172a">{html_lib.escape(s["expert"])}</div>'
                f'<div style="font-size:12px;color:#94a3b8;margin-top:3px">'
                f'{html_lib.escape(s["role"])} &nbsp;·&nbsp; {topic_label} &nbsp;·&nbsp; {s["created_at"][:10]}</div>'
                f'</div>'
                f'<div style="background:#FAFAFB;color:#374151;border:1px solid #D1D5DB;'
                f'padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700">'
                f'{s["entries"]} entries</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

# ── Tab 3: Knowledge library ───────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-label" style="margin-top:4px">Captured Knowledge Library</div>', unsafe_allow_html=True)
    search_q = st.text_input("Search captured knowledge", placeholder="seal failure, P-101, startup sequence…")
    if search_q and em:
        results = em.search(search_q, n_results=8)
        # Match by doc_type or filename pattern (not full path — path varies by OS/install)
        expert_results = [
            r for r in results
            if r.get("doc_type") == "expert_knowledge"
            or "expert_knowledge" in r.get("source_file", "").replace("\\", "/").split("/")[-1]
        ]
        if expert_results:
            for r in expert_results:
                st.markdown(
                    f'<div style="background:#fff;border:1px solid #D1D5DB;border-radius:12px;'
                    f'padding:16px 20px;margin-bottom:10px">'
                    f'<div style="font-size:13px;color:#334155;line-height:1.7">{html_lib.escape(r["text"][:350])}</div>'
                    f'<div style="font-size:11px;color:#94a3b8;margin-top:8px">'
                    f'Source: {html_lib.escape(r["source_file"].split("/")[-1])}'
                    f'&nbsp; · &nbsp; Match: {int(r.get("score",0)*100)}%</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No expert knowledge entries match this search yet.")

    # Merge in-memory entries with entries reloaded from saved disk files
    _mem_entries = [e for s in kca.sessions.values() for e in s.knowledge_entries]
    _mem_ids     = {e["id"] for e in _mem_entries}

    _disk_entries: list = []
    from pathlib import Path as _KPath
    from app.config import DOCS_PATH as _DOCS
    _ke_dir = _KPath(_DOCS) / "maintenance"
    if _ke_dir.exists():
        for _kf in sorted(_ke_dir.glob("expert_knowledge_*.txt")):
            try:
                _lines  = _kf.read_text(encoding="utf-8").splitlines()
                _get    = lambda prefix: next((l.split(prefix, 1)[1].strip() for l in _lines if l.startswith(prefix)), "")
                _ctype  = _get("Knowledge Type:") or "lesson_learned"
                _title  = _get("Title:") or _kf.stem
                _expert = _get("Expert:").split("(")[0].strip()
                _conf   = _get("Confidence:") or "Medium"
                _equip  = [e.strip() for e in _get("Equipment:").split(",") if e.strip()]
                _tags   = [t.strip() for t in _get("Tags:").split(",") if t.strip()]
                # Content is everything after 'KNOWLEDGE CONTENT:'
                _ci     = next((i for i, l in enumerate(_lines) if l.startswith("KNOWLEDGE CONTENT:")), None)
                _content = "\n".join(_lines[_ci + 1:]).strip() if _ci is not None else ""
                _eid    = _kf.stem  # use filename as stable id
                if _eid not in _mem_ids:
                    _disk_entries.append({
                        "id": _eid, "expert_name": _expert, "expert_role": "(saved)",
                        "knowledge_type": _ctype, "title": _title, "content": _content,
                        "equipment_ids": _equip, "tags": _tags, "confidence": _conf,
                        "captured_at": "", "actionable": True,
                    })
            except Exception:
                pass

    all_entries = _disk_entries + _mem_entries
    if all_entries:
        st.markdown(f'<div style="font-size:13px;font-weight:600;color:#475569;margin:12px 0 10px">{len(all_entries)} knowledge entries in library</div>', unsafe_allow_html=True)
        type_options = ["All","equipment_quirk","failure_warning","undocumented_procedure","lesson_learned","process_insight"]
        filter_type = st.selectbox("Filter by type", type_options)
        for entry in all_entries:
            if filter_type == "All" or entry.get("knowledge_type") == filter_type:
                render_knowledge_card(entry)
    else:
        st.markdown(
            '<div style="text-align:center;padding:40px;color:#94a3b8;font-size:14px">'
            'Complete interviews to see captured knowledge entries here.</div>',
            unsafe_allow_html=True,
        )


