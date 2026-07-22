"""
seed_data.py — Populate IndustrialMind with demo data.

Run once after configuring .env:
    python seed_data.py

What it does:
  1. Loads all documents from docs/
  2. Embeds everything into ChromaDB
  3. Builds the knowledge graph
  4. Prints an ingestion summary
  5. Writes demo_questions.txt
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from app.embeddings import EmbeddingManager, full_pipeline
from app.graph_builder import GraphBuilder

DOCS_ROOT = project_root / "docs"

DEMO_QUESTIONS = """\
INDUSTRIAL MIND — DEMO QUESTION BANK
======================================

--- KNOWLEDGE RETRIEVAL (Copilot) ---
1. What caused the P-101 pump to fail in June 2023 and what regulatory requirement was violated?
2. What are the vibration limits for centrifugal pumps under OISD-118?
3. Who investigated the V-205 overpressure incident and what were the contributing causes?
4. What is the step-by-step procedure for replacing a mechanical seal on a centrifugal pump?
5. What PSV testing interval does OISD-118 Section 12.4 require?

--- COMPLIANCE ---
6. Does SOP-007 comply fully with OISD-118 Section 6.2 for dual-seal pump maintenance?
7. What Factory Act sections apply to pressure vessel operation and what are the penalties?
8. Which procedures are missing confined space entry requirements?

--- PATTERN ANALYSIS ---
9. How many times has P-101 experienced a seal failure in the last 3 years?
10. What are the leading indicators of a seal failure on centrifugal pumps?
11. When is P-101 predicted to fail next based on historical pattern?

--- WORK ORDER INTELLIGENCE ---
12. I need to raise a work order for P-101 seal replacement — what do I need to know?
13. What maintenance history and regulatory requirements apply to work on V-205?

--- KNOWLEDGE GRAPH ---
14. Which equipment has the highest risk based on incident history?
15. What regulations govern both P-101 and V-205?
"""


def main():
    print("=" * 60)
    print("  INDUSTRIAL MIND — DATA SEEDER")
    print("=" * 60)

    # ── Step 1: Embed all documents ──────────────────────────────────────────
    print("\n[1/3] Loading and embedding all documents from docs/ ...")
    em = EmbeddingManager()
    result = full_pipeline(docs_folder=str(DOCS_ROOT), embedding_manager=em)

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        sys.exit(1)

    print(f"  Pages loaded   : {result['pages_loaded']}")
    print(f"  Chunks created : {result['chunks_created']}")
    print(f"  Chunks stored  : {result['new_chunks_stored']}")
    print(f"  Equipment found: {result['equipment_found']}")
    print(f"  Failure modes  : {result['failure_modes_found']}")

    # ── Step 2: Build knowledge graph ────────────────────────────────────────
    print("\n[2/3] Building knowledge graph ...")
    gb = GraphBuilder()
    stats = gb.build_from_entities(result["entities"], result["chunks"])
    print(f"  Nodes: {stats.get('nodes', 0)}  |  Edges: {stats.get('relationships', 0)}")
    print(f"  By label: {stats.get('by_label', {})}")

    # ── Step 3: Summary ───────────────────────────────────────────────────────
    em_stats = em.get_stats()
    print("\n[3/3] Final stats:")
    print(f"  ChromaDB chunks    : {em_stats['total_chunks']}")
    print(f"  Documents indexed  : {em_stats['total_documents']}")
    print(f"  By doc type        : {em_stats['doc_types']}")

    questions_path = project_root / "demo_questions.txt"
    questions_path.write_text(DEMO_QUESTIONS, encoding="utf-8")

    print("\n" + "=" * 60)
    print("  Seeding complete!")
    print(f"  Demo questions -> {questions_path.name}")
    print("  Run: streamlit run run.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
