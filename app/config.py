"""Central configuration — loads .env and exposes typed settings."""

import os
import pathlib
import warnings

# Anchor all relative paths to the industrial_mind package directory,
# regardless of which directory Streamlit is launched from.
_APP_DIR = pathlib.Path(__file__).resolve().parent.parent  # .../industrial_mind/

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
warnings.filterwarnings("ignore", message=".*Protobuf.*")
warnings.filterwarnings("ignore", message=".*oneDNN.*")
warnings.filterwarnings("ignore", message=".*absl.*")

from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "")      # Free at console.groq.com
USE_OLLAMA        = os.getenv("USE_OLLAMA", "false").lower() == "true"
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL      = os.getenv("OLLAMA_MODEL", "llama3.1")

# ── Neo4j ────────────────────────────────────────────────────────────────────
NEO4J_URI      = os.getenv("NEO4J_URI", "")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
USE_NEO4J      = bool(NEO4J_URI and NEO4J_PASSWORD and "your_" not in NEO4J_PASSWORD)

# ── Paths ─────────────────────────────────────────────────────────────────────
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(_APP_DIR / "data" / "chroma_db"))
DOCS_PATH      = os.getenv("DOCS_PATH",      str(_APP_DIR / "docs"))
APP_NAME       = os.getenv("APP_NAME", "IndustrialMind")

# ── Derived: which LLM backend to use ────────────────────────────────────────
_PLACEHOLDER = ("your_", "sk-placeholder")

def _is_real_key(val: str) -> bool:
    return bool(val) and not any(val.startswith(p) for p in _PLACEHOLDER)

def llm_backend() -> str:
    if _is_real_key(GROQ_API_KEY):
        return "groq"
    if _is_real_key(ANTHROPIC_API_KEY):
        return "anthropic"
    if _is_real_key(OPENAI_API_KEY):
        return "openai"
    if USE_OLLAMA:
        return "ollama"
    return "smart_rag"  # built-in, no key needed — always works

def llm_display_name() -> str:
    b = llm_backend()
    return {
        "groq":      "Groq Llama 3.3 70B",
        "anthropic": "Anthropic Haiku",
        "openai":    "GPT-4o Mini",
        "ollama":    f"Ollama ({OLLAMA_MODEL})",
        "smart_rag": "Smart RAG (No Key)",
    }.get(b, b)
