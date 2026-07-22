# Industrial Mind — AI for Industrial Knowledge Intelligence

**ET AI Hackathon 2026 | Problem Statement 8**

A unified AI-powered "brain" for industrial asset and operations knowledge. Combines RAG search, a knowledge graph, compliance auditing, failure pattern prediction, expert knowledge capture, and proactive work order intelligence.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure environment
```bash
copy .env.example .env
```
Open `.env` and set your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Seed demo data
```bash
python seed_data.py
```
This loads all synthetic documents, embeds them into ChromaDB, builds the knowledge graph, and writes `demo_questions.txt`.

### 4. Launch the app
```bash
streamlit run run.py
```
Open http://localhost:8501

---

## Architecture

```
industrial_mind/
├── run.py                    # Streamlit entry point + home dashboard
├── seed_data.py              # One-time data seeder
├── app/
│   ├── config.py             # Settings from .env
│   ├── ingestion.py          # PDF/Excel/CSV/OCR document loader
│   ├── entity_extractor.py   # Equipment IDs, regulations, failure modes (NER)
│   ├── embeddings.py         # ChromaDB vector store (sentence-transformers)
│   ├── rag.py                # RAG engine + work order context generator
│   ├── graph_builder.py      # Neo4j / NetworkX knowledge graph
│   ├── graph_query.py        # Pyvis visualization + graph queries
│   ├── compliance_agent.py   # Procedure vs. regulation gap analysis
│   ├── pattern_agent.py      # Failure pattern detection + failure prediction
│   ├── knowledge_capture.py  # Expert interview agent (retiring engineer)
│   └── ui_helpers.py         # Dark industrial CSS + UI components
├── pages/
│   ├── 1_Upload.py           # Document ingestion UI
│   ├── 2_Copilot.py          # Chat with your documents
│   ├── 3_Graph.py            # Interactive knowledge graph
│   ├── 4_Compliance.py       # Compliance audit dashboard
│   ├── 5_Patterns.py         # Failure pattern analysis
│   ├── 6_Knowledge_Capture.py # Expert knowledge interviews
│   └── 7_Work_Orders.py      # Work order intelligence briefs
└── docs/
    ├── maintenance/          # Maintenance work order records
    ├── incidents/            # Incident investigation reports
    ├── procedures/           # SOPs
    └── regulations/          # OISD, Factories Act summaries
```

---

## LLM Options

Set `LLM_BACKEND` in `.env`:

| Backend | Model | Cost |
|---------|-------|------|
| `anthropic` | claude-haiku-4-5 | Low (recommended) |
| `openai` | gpt-4o-mini | Low |
| `ollama` | llama3 (local) | Free |

---

## Key Features

| Feature | Description |
|---------|-------------|
| **RAG Copilot** | Natural language Q&A over all uploaded industrial documents |
| **Knowledge Graph** | Visual map of equipment, incidents, regulations, and people |
| **Compliance Audit** | Automatic gap analysis of SOPs against OISD/Factory Act |
| **Failure Patterns** | Detects recurring failure modes + predicts next failure date |
| **Expert Capture** | AI interviews retiring engineers to preserve tribal knowledge |
| **Work Order Briefs** | Auto-generates knowledge context when raising a work order |

---

## Demo Scenario

The pre-loaded synthetic data demonstrates:
- **P-101** pump with 3 seal failures (2021–2023) — pattern detected, next failure predicted
- **V-205** pressure vessel overpressure incident — PSV testing gap identified
- **SOP-007** missing dual-seal backup testing — compliance gap flagged against OISD-118 §6.2.2(e)
- Expert knowledge from fictional retiring engineers in maintenance records

Use the questions in `demo_questions.txt` to demo each page.

---

## Requirements

- Python 3.10+
- Anthropic / OpenAI API key (or Ollama running locally)
- Optional: Neo4j Desktop for persistent graph (falls back to NetworkX in-memory)
- Optional: Tesseract OCR for scanned PDF support
