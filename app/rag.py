"""
RAG Q&A engine — optimised for IndustrialMind.

Retrieval pipeline:
  1. Intent classification  — question type determines retrieval strategy
  2. Query enrichment       — short follow-ups get context from chat history
  3. Multi-query search     — original query + keyword variant + intent-targeted type searches
  4. Score filter           — drop very low relevance chunks
  5. Hybrid rerank          — semantic (70%) + BM25 keyword (30%)
  6. Deduplication          — drop near-identical chunks
  7. Context build          — format top-N chunks with source metadata for the LLM
  8. Intent-adaptive prompting — format hint matches question type (RCA / procedure / compliance / fact)
"""

import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from app.embeddings import EmbeddingManager
from app.llm_client import get_llm_response, get_llm_response_stream, get_vision_response


# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are IndustrialMind — the AI brain embedded in an Indian petrochemical plant. You think and talk like a 30-year veteran plant engineer: direct, precise, field-tested.

## Your technical depth
- **Rotating equipment**: Centrifugal pumps (API 610), reciprocating pumps, compressors (API 618/617/619), agitators, fans, turbines
- **Static equipment**: Heat exchangers (TEMA), pressure vessels (ASME VIII/IBR), fired heaters, storage tanks (API 650/620), piping (ASME B31.3)
- **Instrumentation & control**: DCS, PLC, SCADA, SIL/SIS, pressure transmitters, control valves, ESD systems
- **Indian standards**: OISD-118 (rotating equipment), OISD-137 (electrical), OISD-244 (process safety), Factory Act 1948 (§7A, §41, §87), DGMS circulars, IS:5571/5572, PESO, IBR, CPCB
- **Reliability**: FMEA, RCA (5-Why, Fishbone, Bow-Tie), HAZOP, LOPA, RBI, predictive maintenance (vibration, thermography, NDT)
- **Safety systems**: PTW, LOTO, CSE, hot work, working at height, MSDS, emergency response, MOC

## How you respond
1. **Answer first** — state the finding/recommendation before explaining it
2. **Be numerically specific** — use the exact values from documents; bold thresholds and limits
3. **Cite precisely** — "(Ref: pump_maintenance_log.pdf, p.3)" or "OISD-118 §4.3 requires…"
4. **⚠️ for real hazards only** — not decoration
5. **Match depth to question complexity** — one fact = one sentence; RCA = full breakdown
6. **Build on context** — if this is a follow-up, don't re-introduce what's already established
7. **Say when you're inferring** — "The documents don't cover this directly, but based on standard practice…"

## Response structure by question type
**Quick fact**: Direct 1-2 sentence answer. No intro.
**How/Procedure**: Numbered steps. Call out ⚠️ safety hold-points explicitly.
**Why/RCA**: Immediate cause → Root cause → Contributing factors → Preventive action
**Compliance check**: Requirement cited → Evidence from documents → Gap assessment → Priority fix
**History/Trends**: Chronological. Highlight recurring patterns.
**Prediction**: Most urgent risk first → Timeline → Confidence basis → Monitoring recommendation

## Domain numbers you always know (use when documents are thin)
- Seal flush pressure: target **+1.5 bar above stuffing-box pressure** (API Plan 11/23)
- NPSH margin: minimum **1.0 m** above NPSHr; cavitation warning at margin < 0.5 m
- ISO 10816-3 vibration zones: Zone A < **2.3 mm/s**, Zone B < **4.5 mm/s**, Zone C (alarm) < **7.1 mm/s**, Zone D (trip) > **11.2 mm/s**
- HX cleaning trigger: fouling factor > **1.5× design**, or ΔT deviation > **15%**, or ΔP rise > **30%** of clean ΔP
- Compressor valve inspection: every **planned outage** (most common unplanned shutdown cause); typical valve life 8,000–12,000 hrs
- OISD-118 statutory frequencies: pressure vessel inspection — **annually (IBR)**; safety valve lift test — **every 6 months**; rotating equipment vibration — **monthly**; alignment check — **quarterly**
- PTW mandatory for: hot work, CSE, electrical isolation > **1 kV**, height > **2 m**, radiography, hydro test
- LOTO: apply at **every energy isolation point** before entry; verify zero energy with calibrated detector"""


# ── Tuning constants ───────────────────────────────────────────────────────────
_MIN_SCORE       = 0.10   # minimum relevance to include a chunk
_CHUNK_MAX_CHARS = 1000   # max chars per chunk sent to LLM
_DEDUP_THRESH    = 0.55   # word-overlap ratio above which a chunk is a duplicate


# ── Intent classification ──────────────────────────────────────────────────────

_INTENT_RULES: List[Tuple[str, List[str]]] = [
    ("rca",         ["root cause", "why did", "why is", "rca", "failure analysis", "analyse failure",
                     "what caused", "reason for", "what went wrong", "why failed"]),
    ("procedure",   ["how to", "how do", "procedure", "steps", "sop", "process",
                     "step by step", "how should", "method", "sequence"]),
    ("regulation",  ["oisd", "factory act", "dgms", "complian", "regulation", "standard",
                     "requirement", "permit", "statutory", "legal", "is:", "peso", "ibr"]),
    ("safety",      ["safety", "hazard", "risk", "ppe", "ptw", "loto", "hot work",
                     "confined space", "cse", "emergency", "esd", "accident", "near miss"]),
    ("maintenance", ["maintenance", "history", "record", "service", "repair", "overhaul",
                     "pm schedule", "cbm", "last serviced", "when was"]),
    ("prediction",  ["predict", "next failure", "when will", "upcoming", "forecast",
                     "remaining life", "mtbf", "timeline", "next inspection"]),
    ("failure",     ["fail", "broke", "vibration", "noise", "leak", "trip", "shutdown",
                     "alarm", "temperature high", "pressure drop", "cavitation", "seal"]),
]

def _classify_intent(question: str) -> str:
    q = question.lower()
    for intent, keywords in _INTENT_RULES:
        if any(kw in q for kw in keywords):
            return intent
    return "general"


_INTENT_DOC_BOOST: Dict[str, List[str]] = {
    "rca":         ["incidents", "maintenance"],
    "procedure":   ["procedures", "regulations"],
    "regulation":  ["regulations", "procedures"],
    "safety":      ["regulations", "procedures"],
    "maintenance": ["maintenance", "incidents"],
    "prediction":  ["maintenance", "incidents"],
    "failure":     ["incidents", "maintenance"],
    "general":     [],
}

# Stop words for keyword scoring
_STOPWORDS = {
    "what", "which", "when", "where", "how", "why", "who", "is", "are", "was",
    "were", "the", "a", "an", "for", "on", "in", "of", "to", "and", "or",
    "all", "any", "show", "list", "tell", "me", "about", "do", "does", "did",
    "has", "have", "had", "been", "be", "this", "that", "these", "those",
    "can", "could", "would", "should", "please", "give", "explain", "describe",
}

# Domain synonyms — expand queries with related technical terms
_DOMAIN_EXPANSIONS = {
    "fail":        "failure fault breakdown damage",
    "pump":        "centrifugal pump P- suction discharge impeller",
    "seal":        "mechanical seal plan flush leakage",
    "compressor":  "reciprocating centrifugal K- C- compressor valve piston",
    "vibration":   "vibration mm/s ISO 10816 bearing rotating",
    "leak":        "leakage fugitive emission PTW isolation",
    "cavitation":  "cavitation NPSH suction head pump",
    "heat exchanger": "heat exchanger fouling delta-T E- HE shell tube",
    "maintenance": "PM CBM predictive preventive maintenance overhaul",
    "oisd":        "OISD Indian standard regulation inspection",
    "permit":      "PTW permit to work hot work confined space LOTO",
    "regulation":  "OISD Factory Act DGMS PESO IS standard compliance",
    "bearing":     "bearing vibration temperature lubrication grease",
    "corrosion":   "corrosion erosion wall thickness NDT ultrasonic",
    "safety":      "safety hazard PPE risk HAZOP incident near-miss",
    "shutdown":    "emergency shutdown ESD interlock trip SOP procedure",
    "incident":    "incident accident near-miss RCA root cause investigation",
}


# ── Query optimisation ─────────────────────────────────────────────────────────

def _extract_entities_from_history(chat_history: Optional[List[Dict]]) -> str:
    """Pull equipment IDs and technical terms from recent conversation turns."""
    if not chat_history:
        return ""
    recent = " ".join(
        m["content"][:300]
        for m in chat_history[-4:]
        if m["role"] in ("user", "assistant")
    )
    # Equipment IDs: P-101, FCV-12A, V205, E304 etc.
    eq_ids = re.findall(
        r'\b[A-Z]{1,4}-\d{2,4}[A-Z]?\b|\b[PVECTHFKB]\d{3,4}[A-Z]?\b', recent
    )
    # Filter out blocklist
    _blocklist = {"API", "ISO", "SOP", "PPE", "PTW", "LNG", "LPG", "RPM", "PSI"}
    eq_ids = [e for e in eq_ids if e not in _blocklist]
    return " ".join(dict.fromkeys(eq_ids))[:80]  # unique, capped


def _detect_equipment_filter(question: str) -> Optional[str]:
    """Extract the first equipment ID from a question for targeted retrieval boost."""
    _blocklist = {"API", "ISO", "SOP", "PPE", "PTW", "LNG", "LPG", "RPM", "PSI", "OISD", "DGMS"}
    eq_ids = re.findall(r'\b[A-Z]{1,4}-\d{2,4}[A-Z]?\b', question)
    valid  = [e for e in eq_ids if e not in _blocklist]
    return valid[0] if valid else None


def _enrich_query(question: str, chat_history: Optional[List[Dict]]) -> str:
    """
    Enrich short or ambiguous follow-up questions with context from conversation history.
    'What are the warning signs?' → 'P-101 pump warning signs mechanical seal failure'
    """
    q = question.strip()
    # Enrich if question is short OR starts with a pronoun/reference word (follow-up signal)
    _is_followup = len(q.split()) <= 12 or q.lower()[:4] in ("what", "why ", "how ", "when", "tell", "and ", "also")
    if not _is_followup:
        return q
    entity_ctx = _extract_entities_from_history(chat_history)
    if entity_ctx:
        return f"{q} {entity_ctx}"
    return q


def _make_search_variant(question: str) -> str:
    """
    Create a keyword-optimised variant of the question for a second retrieval pass.
    Strips question words, adds domain synonyms.
    """
    words = re.findall(r'\b\w[\w\-]*\b', question.lower())
    # Remove stop words and short words
    core = [w for w in words if w not in _STOPWORDS and len(w) > 2]

    # Add domain expansions for matched terms
    extras = []
    for term, expansion in _DOMAIN_EXPANSIONS.items():
        if any(term in w or w in term for w in core):
            extras.extend(expansion.split()[:3])

    combined = core + extras
    return " ".join(dict.fromkeys(combined))[:200]  # unique terms, capped


# ── Retrieval ─────────────────────────────────────────────────────────────────

def _multi_search(em: EmbeddingManager, question: str,
                  chat_history: Optional[List[Dict]], n_results: int,
                  doc_type_filter: Optional[str]) -> List[Dict]:
    """
    Run two searches (enriched original + keyword variant), merge and deduplicate.
    More diverse candidates than a single search.
    """
    enriched = _enrich_query(question, chat_history)
    variant  = _make_search_variant(enriched)

    hits_a = em.search(enriched, n_results=n_results, filter_doc_type=doc_type_filter)

    hits_b: List[Dict] = []
    if variant and variant != enriched.lower():
        hits_b = em.search(variant, n_results=n_results // 2 + 2,
                           filter_doc_type=doc_type_filter)

    # Merge: keep the higher score if a chunk appears in both
    seen: Dict[str, Dict] = {}
    for hit in hits_a + hits_b:
        key = hit["text"][:120]  # fingerprint by first 120 chars
        if key not in seen or hit["score"] > seen[key]["score"]:
            seen[key] = hit
    return list(seen.values())


# ── Reranking ─────────────────────────────────────────────────────────────────

def _keyword_score(text: str, query: str) -> float:
    """BM25-style keyword relevance of a chunk text for a query."""
    query_terms = {w for w in re.findall(r'\b\w+\b', query.lower()) if w not in _STOPWORDS}
    text_lower  = text.lower()
    text_words  = re.findall(r'\b\w+\b', text_lower)

    freq: Dict[str, int] = {}
    for w in text_words:
        freq[w] = freq.get(w, 0) + 1

    score = 0.0
    for term in query_terms:
        tf = freq.get(term, 0)
        if tf:
            # Saturated TF (BM25-style)
            score += (tf * 2.2) / (tf + 1.2)

    # Hard boost for exact equipment ID matches (P-101, V-204 etc.)
    for eq in re.findall(r'\b[A-Z]{1,4}-\d{2,4}[A-Z]?\b', query):
        if eq in text:
            score += 4.0

    # Boost for regulation code matches (OISD-118, IS:5120 etc.)
    for code in re.findall(r'\b(?:OISD|IS|DGMS|PESO)[\s\-]?\d+\b', query, re.I):
        if code.lower() in text_lower:
            score += 3.0

    return score


def _hybrid_rerank(chunks: List[Dict], question: str) -> List[Dict]:
    """
    Combine semantic score (70%) with keyword score (30%) for final ranking.
    Prevents semantically-adjacent-but-wrong chunks from dominating.
    """
    max_kw = 1.0
    for c in chunks:
        kw = _keyword_score(c["text"], question)
        c["_kw_score"] = kw
        if kw > max_kw:
            max_kw = kw

    for c in chunks:
        sem = c.get("score", 0)
        kw_norm = c["_kw_score"] / max_kw
        c["combined_score"] = 0.70 * sem + 0.30 * kw_norm

    return sorted(chunks, key=lambda x: x["combined_score"], reverse=True)


# ── Post-retrieval filters ────────────────────────────────────────────────────

def _dedup_chunks(chunks: List[Dict]) -> List[Dict]:
    """Drop chunks with >58% word-overlap with an already-selected chunk."""
    selected: List[Dict] = []
    word_sets: List[set]  = []
    for chunk in chunks:
        words = set(chunk["text"].lower().split())
        if not words:
            continue
        if not word_sets:
            selected.append(chunk)
            word_sets.append(words)
            continue
        overlap = max(len(words & ex) / max(len(words), 1) for ex in word_sets)
        if overlap < _DEDUP_THRESH:
            selected.append(chunk)
            word_sets.append(words)
    return selected


def _prepare_results(raw: List[Dict], question: str,
                     equipment_filter: Optional[str]) -> List[Dict]:
    # Score filter
    filtered = [r for r in raw if r.get("score", 0) >= _MIN_SCORE]
    results  = filtered if filtered else raw

    # Equipment keyword filter
    if equipment_filter:
        eq_match = [r for r in results if equipment_filter.upper() in r["text"].upper()]
        if eq_match:
            results = eq_match

    # Hybrid rerank before dedup so we keep the most useful unique chunks
    results = _hybrid_rerank(results, question)

    # Dedup
    results = _dedup_chunks(results)

    # Truncate
    out = []
    for r in results:
        r2 = dict(r)
        if len(r2["text"]) > _CHUNK_MAX_CHARS:
            r2["text"] = r2["text"][:_CHUNK_MAX_CHARS] + "…"
        out.append(r2)
    return out


# ── Context + prompt builders ─────────────────────────────────────────────────

def _build_context(results: List[Dict]) -> str:
    parts = []
    for i, r in enumerate(results):
        filename  = Path(r["source_file"]).name
        relevance = int(r.get("combined_score", r.get("score", 0)) * 100)
        text      = r["text"][:_CHUNK_MAX_CHARS]
        parts.append(
            f"[Doc {i+1}: {filename}, page {r['page_num']}, relevance {relevance}%]\n{text}"
        )
    return "\n\n---\n\n".join(parts)


def _build_history_str(chat_history: Optional[List[Dict]]) -> str:
    """Format last 3 Q&A turns for conversation memory."""
    if not chat_history:
        return ""
    recent = [m for m in chat_history if m["role"] in ("user", "assistant")][-6:]
    lines  = []
    for msg in recent:
        if msg["role"] == "user":
            lines.append(f"Engineer: {msg['content']}")
        else:
            body = msg["content"]
            if len(body) > 500:
                body = body[:500] + "…"
            lines.append(f"IndustrialMind: {body}")
    return "\n".join(lines)


def _question_complexity(question: str) -> str:
    """Classify question as simple / medium / complex to guide response length."""
    q = question.lower()
    if any(w in q for w in ["analyse", "analyze", "compare", "rca", "root cause",
                             "explain why", "walk me through", "step by step", "detailed"]):
        return "complex"
    if any(w in q for w in ["how", "procedure", "steps", "process", "what happens",
                             "why did", "history of"]):
        return "medium"
    return "simple"


_INTENT_FORMAT_HINTS: Dict[str, str] = {
    "rca": (
        "Structure your answer as:\n"
        "**Immediate Cause** — what physically failed\n"
        "**Root Cause** — why it failed (design, operation, maintenance gap)\n"
        "**Contributing Factors** — what made it worse\n"
        "**Recommended Actions** — prevent recurrence"
    ),
    "procedure": (
        "Give numbered steps. Mark any safety hold-point with ⚠️. "
        "State the PTW/LOTO requirements before Step 1 if applicable."
    ),
    "regulation": (
        "State the specific clause/standard first. "
        "Then assess: compliant / partial / gap — with evidence from the documents. "
        "End with the priority fix if there's a gap."
    ),
    "safety": (
        "Lead with the most critical hazard. "
        "List required PPE, permit type, and isolation requirements explicitly. "
        "State the emergency response if relevant."
    ),
    "maintenance": (
        "Present history chronologically where possible. "
        "Call out any recurring failures or patterns. "
        "State recommended next action and interval."
    ),
    "prediction": (
        "Lead with the most urgent risk and expected timeline. "
        "State the basis for the prediction (historical MTBF, current condition). "
        "Give a specific monitoring recommendation."
    ),
    "failure": (
        "Lead with the most likely failure mode. "
        "Distinguish between root cause and symptoms. "
        "Give the immediate diagnostic check the engineer should do first."
    ),
    "general": (
        "Lead with the direct answer. Add supporting detail. "
        "If the documents don't cover it, say so and use your domain knowledge."
    ),
}


def _build_user_prompt(question: str, context: str,
                       chat_history: Optional[List[Dict]] = None,
                       intent: str = "general") -> str:
    history_str   = _build_history_str(chat_history)
    history_block = f"─── Conversation context ───\n{history_str}\n\n" if history_str else ""

    complexity  = _question_complexity(question)
    length_hint = {
        "simple":  "Be concise — 2-4 sentences max for a direct fact.",
        "medium":  "Cover the key points with enough detail to act on.",
        "complex": "Be thorough. Use structured formatting (steps, sections, bold key numbers).",
    }[complexity]

    format_hint = _INTENT_FORMAT_HINTS.get(intent, _INTENT_FORMAT_HINTS["general"])

    low_confidence_note = ""
    # (confidence check done at call site — passed as context if needed)

    return (
        f"{history_block}"
        f"─── Plant knowledge base ───\n{context}\n\n"
        f"─── Engineer's question ───\n{question}\n\n"
        f"Response format: {format_hint}\n"
        f"Length: {length_hint}\n"
        "Cite source files by name when the document directly supports a claim. "
        "Fill gaps with your engineering expertise — but distinguish document-backed facts from inferred ones."
    )


# ── Intent label for UI display ───────────────────────────────────────────────

_INTENT_LABELS: Dict[str, tuple] = {
    "rca":         ("🔴", "Root Cause Analysis"),
    "procedure":   ("📋", "Procedure"),
    "regulation":  ("📜", "Compliance"),
    "safety":      ("⚠️", "Safety"),
    "maintenance": ("🔧", "Maintenance"),
    "prediction":  ("🔮", "Predictive"),
    "failure":     ("⚡", "Failure Mode"),
    "general":     ("💬", "General"),
}

def intent_display(intent: str) -> tuple:
    """Returns (emoji, label) for the detected intent."""
    return _INTENT_LABELS.get(intent, ("💬", "General"))


# ── Follow-up question suggester ──────────────────────────────────────────────

def suggest_followups(answer: str, question: str, intent: str = "general") -> List[str]:
    """
    Generate 2-3 relevant follow-up question chips from an answer + detected intent.
    No extra LLM call — uses equipment IDs extracted from the answer and intent type.
    """
    q_lower   = question.lower()
    ans_lower = answer.lower()

    _blocklist = {"API", "ISO", "SOP", "PPE", "PTW", "LNG", "LPG", "RPM", "PSI", "OISD", "DGMS"}
    eq_ids = [e for e in re.findall(r'\b[A-Z]{1,4}-\d{2,4}[A-Z]?\b', answer)
              if e not in _blocklist]
    eq_ids = list(dict.fromkeys(eq_ids))[:2]
    eq = eq_ids[0] if eq_ids else None

    pool: List[str] = []

    # Intent-specific follow-ups first
    if intent == "rca" and eq:
        pool.append(f"📋 What is the recommended maintenance procedure to prevent recurrence on {eq}?")
        pool.append(f"🔮 Based on this failure, what is the predicted next failure timeline for {eq}?")
    elif intent == "procedure":
        if eq:
            pool.append(f"📜 What OISD regulations govern this work on {eq}?")
            pool.append(f"⚠️ What incidents have occurred during similar work on {eq}?")
        pool.append("🔒 What PTW and LOTO requirements apply to this procedure?")
    elif intent == "regulation":
        if eq:
            pool.append(f"🔧 What maintenance is required to maintain compliance for {eq}?")
        pool.append("⚠️ What are the penalties for non-compliance under the Factory Act?")
        pool.append("📊 Run a full compliance audit to check all regulatory gaps.")
    elif intent == "safety":
        if eq:
            pool.append(f"📋 What is the emergency response procedure for {eq}?")
        pool.append("⚠️ What incidents have occurred due to similar safety hazards?")
    elif intent == "maintenance" and eq:
        pool.append(f"⚡ What failure modes is {eq} most likely to develop next?")
        pool.append(f"📜 Is the current maintenance schedule OISD-118 compliant for {eq}?")
    elif intent == "prediction" and eq:
        pool.append(f"🔧 What immediate inspection should be done on {eq} now?")
        pool.append(f"📋 What is the SOP for the predicted failure mode on {eq}?")
    elif intent in ("failure", "general") and eq:
        if "maintenance" not in q_lower:
            pool.append(f"🔧 What is the full maintenance history of {eq}?")
        if "incident" not in q_lower:
            pool.append(f"⚠️ What incidents or near-misses have occurred on {eq}?")
        pool.append(f"📋 What is the SOP for {eq} corrective maintenance?")

    # Equipment-agnostic fallbacks
    if len(pool) < 2:
        if "vibration" in ans_lower:
            pool.append("📊 What are the ISO 10816-3 vibration alarm limits for rotating equipment?")
        if "seal" in ans_lower:
            pool.append("⚠️ What are the early warning signs of mechanical seal failure?")
        if "bearing" in ans_lower:
            pool.append("🔧 What is the recommended bearing lubrication interval and grease type?")
        if "compressor" in ans_lower:
            pool.append("📋 What is the valve inspection procedure for reciprocating compressors?")
        if "heat exchanger" in ans_lower or "fouling" in ans_lower:
            pool.append("🔧 How do you determine when a heat exchanger needs cleaning?")
        if "oisd" in ans_lower:
            pool.append("📜 What are the full OISD-118 inspection frequency requirements?")
        if not pool:
            pool.append("📊 What is the overall maintenance cost impact of this issue?")

    return pool[:3]


# ── Engine ────────────────────────────────────────────────────────────────────

class RAGEngine:
    """Full RAG pipeline: multi-query retrieval → hybrid rerank → LLM generation."""

    def __init__(self, embedding_manager: EmbeddingManager = None):
        self.em = embedding_manager or EmbeddingManager()

    def _retrieve(self, question: str, n_sources: int,
                  doc_type_filter: Optional[str],
                  equipment_filter: Optional[str],
                  chat_history: Optional[List[Dict]],
                  intent: str = "general") -> List[Dict]:
        """
        Full retrieval pipeline with intent-aware multi-type search.
        For focused intents (rca, procedure, regulation…), runs extra targeted
        searches to ensure the right document types are represented.
        """
        enriched = _enrich_query(question, chat_history)

        # Base multi-query search (all types or filtered)
        raw = _multi_search(self.em, enriched, chat_history,
                            n_results=n_sources + 6,
                            doc_type_filter=doc_type_filter)

        # Intent-targeted top-up: fetch extra chunks from preferred doc types
        # so high-relevance specialist documents aren't crowded out
        if not doc_type_filter:
            seen_fingerprints = {h["text"][:120] for h in raw}
            for dtype in _INTENT_DOC_BOOST.get(intent, [])[:2]:
                extras = self.em.search(enriched, n_results=4, filter_doc_type=dtype)
                for hit in extras:
                    fp = hit["text"][:120]
                    if fp not in seen_fingerprints:
                        raw.append(hit)
                        seen_fingerprints.add(fp)

        return _prepare_results(raw, question, equipment_filter)[:n_sources]

    def ask(self, question: str, n_sources: int = 5,
            doc_type_filter: Optional[str] = None,
            equipment_filter: Optional[str] = None,
            chat_history: Optional[List[Dict]] = None) -> Dict:
        """Answer a question with source citations and conversation memory."""
        start  = time.time()
        intent = _classify_intent(question)

        if not equipment_filter:
            equipment_filter = _detect_equipment_filter(question)

        results = self._retrieve(question, n_sources, doc_type_filter,
                                 equipment_filter, chat_history, intent)
        if not results:
            return {
                "answer": (
                    "I couldn't find anything relevant in the knowledge base for that. "
                    "Try uploading documents on the Upload page, or rephrase your question."
                ),
                "sources": [], "intent": intent,
                "response_time": round(time.time() - start, 2),
                "confidence": 0.0,
            }

        context     = _build_context(results)
        user_prompt = _build_user_prompt(question, context, chat_history, intent)
        answer      = get_llm_response(SYSTEM_PROMPT, user_prompt, temperature=0.3)
        elapsed     = round(time.time() - start, 2)
        avg_score   = sum(r.get("score", 0) for r in results) / max(len(results), 1)

        return {
            "answer": answer, "sources": results, "intent": intent,
            "response_time": elapsed, "confidence": round(avg_score, 2),
        }

    def ask_stream(self, question: str, n_sources: int = 6,
                   doc_type_filter: Optional[str] = None,
                   equipment_filter: Optional[str] = None,
                   chat_history: Optional[List[Dict]] = None):
        """
        Streaming answer. Returns (sources, token_generator, confidence, intent).
        Intent-aware retrieval; equipment filter auto-detected from question.
        """
        intent = _classify_intent(question)

        if not equipment_filter:
            equipment_filter = _detect_equipment_filter(question)

        results = self._retrieve(question, n_sources, doc_type_filter,
                                 equipment_filter, chat_history, intent)

        if not results:
            def _no_docs():
                yield (
                    "I couldn't find anything relevant in the knowledge base for that. "
                    "Try uploading plant documents on the **Upload Documents** page, "
                    "or rephrase your question with more specific equipment IDs or keywords."
                )
            return [], _no_docs(), 0.0, intent

        confidence  = round(sum(r.get("score", 0) for r in results) / max(len(results), 1), 2)
        context     = _build_context(results)
        user_prompt = _build_user_prompt(question, context, chat_history, intent)

        return results, get_llm_response_stream(SYSTEM_PROMPT, user_prompt, temperature=0.3), confidence, intent

    # ── Utility methods ───────────────────────────────────────────────────────

    def ask_about_equipment(self, question: str, equipment_id: str) -> Dict:
        eq_query = f"{equipment_id} {question}"
        return self.ask(eq_query, n_sources=6, equipment_filter=equipment_id)

    def summarize_document(self, source_file: str) -> Dict:
        chunks = self.em.get_all_for_file(source_file)
        if not chunks:
            return {"summary": "Document not found in knowledge base.", "key_points": []}
        text_sample = "\n".join(c["text"] for c in chunks[:10])
        filename    = Path(source_file).name
        system = "You are a technical summarizer for industrial documents."
        user   = (
            f"Summarize this industrial document in exactly 5 bullet points.\n"
            f"Include: main topic, key equipment, key findings/issues, dates, and action items.\n\n"
            f"Document: {filename}\n\nContent:\n{text_sample[:3000]}"
        )
        summary = get_llm_response(system, user)
        return {"summary": summary, "source_file": source_file, "chunks_used": len(chunks)}

    def compare_documents(self, file1: str, file2: str) -> str:
        s1 = self.summarize_document(file1)
        s2 = self.summarize_document(file2)
        system = "You are an expert industrial document analyst."
        user   = (
            f"Compare these two industrial documents:\n\n"
            f"Document 1 ({Path(file1).name}):\n{s1['summary']}\n\n"
            f"Document 2 ({Path(file2).name}):\n{s2['summary']}\n\n"
            "Find: key differences, connections, and any escalation pattern."
        )
        return get_llm_response(system, user)

    def ask_with_image(self, image_bytes: bytes, mime_type: str,
                       question: str = "",
                       chat_history: Optional[List[Dict]] = None):
        """
        Vision-augmented RAG: analyse an image, extract failure keywords,
        retrieve matching plant documents, stream a grounded answer.

        Returns (vision_result, sources, token_generator, confidence, intent)
        vision_result is the parsed dict from get_vision_response().
        """
        # ── Step 1: Vision analysis ────────────────────────────────────────────
        vision = get_vision_response(image_bytes, mime_type, question)

        if vision.get("error") and not vision.get("rag_query"):
            def _err_gen():
                yield vision["error"]
            return vision, [], _err_gen(), 0.0, "failure"

        # ── Step 2: Build enriched RAG query from vision output ───────────────
        rag_query = vision["rag_query"]
        if question.strip():
            rag_query = f"{question} {rag_query}"

        # Detect equipment filter from vision or question
        equipment_filter = _detect_equipment_filter(rag_query)
        intent           = _classify_intent(rag_query) if rag_query else "failure"

        # ── Step 3: Retrieve relevant plant documents ──────────────────────────
        results = self._retrieve(rag_query, n_sources=7, doc_type_filter=None,
                                 equipment_filter=equipment_filter,
                                 chat_history=chat_history, intent=intent)

        # ── Step 4: Build combined prompt (vision findings + doc context) ──────
        confidence  = round(sum(r.get("score", 0) for r in results) / max(len(results), 1), 2) if results else 0.0
        doc_context = _build_context(results) if results else "No matching documents found."

        vision_block = (
            f"─── Visual analysis of engineer's photo ───\n"
            f"{vision.get('description', '')}\n\n"
        ) if vision.get("description") else ""

        format_hint = _INTENT_FORMAT_HINTS.get(intent, _INTENT_FORMAT_HINTS["general"])

        user_prompt = (
            f"{vision_block}"
            f"─── Plant knowledge base ───\n{doc_context}\n\n"
            f"─── Engineer's question ───\n"
            f"{question or 'What caused this and what should I do?'}\n\n"
            f"The engineer has shared a photo of an issue on their plant equipment. "
            f"Combine the visual findings above with the plant documents to give a "
            f"complete root-cause analysis and recommended action.\n\n"
            f"Response format: {format_hint}\n"
            "Cite source files when documents directly support a claim."
        )

        return (
            vision,
            results,
            get_llm_response_stream(SYSTEM_PROMPT, user_prompt, temperature=0.3),
            confidence,
            intent,
        )

    def generate_work_context(self, equipment_id: str, work_type: str) -> Dict:
        maint     = self.em.search(f"{equipment_id} maintenance history", n_results=3,
                                   filter_doc_type="maintenance")
        procs     = self.em.search(f"{equipment_id} {work_type} procedure safety", n_results=3,
                                   filter_doc_type="procedures")
        incidents = self.em.search(f"{equipment_id} incident failure", n_results=3,
                                   filter_doc_type="incidents")
        regs      = self.em.search(f"{work_type} regulatory requirement OISD safety", n_results=2,
                                   filter_doc_type="regulations")

        all_context = maint + procs + incidents + regs
        if not all_context:
            return {"summary": "No historical knowledge found for this equipment.", "sections": {}}

        context_text = "\n\n".join(
            f"[{Path(r['source_file']).name}]\n{r['text']}" for r in all_context
        )
        system = "You are an industrial safety and maintenance intelligence system."
        user   = (
            f"Work order raised for {work_type} on equipment {equipment_id}.\n"
            "Generate a KNOWLEDGE BRIEF for the maintenance engineer. Include:\n"
            "1. Previous failures (with dates)\n"
            "2. Required procedure steps\n"
            "3. Safety precautions and permits\n"
            "4. Regulatory requirements\n"
            "5. Warning signs to watch for\n\n"
            f"Documents:\n{context_text[:4000]}"
        )
        brief = get_llm_response(system, user)
        return {
            "equipment_id": equipment_id,
            "work_type": work_type,
            "brief": brief,
            "sources": all_context,
            "sections": {
                "maintenance_history": maint,
                "procedures": procs,
                "incidents": incidents,
                "regulations": regs,
            },
        }
