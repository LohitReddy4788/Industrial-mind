"""
Lazy component loader — each component cached independently.
Pages only load what they need, so startup is instant.
"""

import os, warnings
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
warnings.filterwarnings("ignore", message=".*Protobuf.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*oneDNN.*")

import streamlit as st


# ── One cached function per component ─────────────────────────────────────────
# This way each page only pays for what it uses.
# EmbeddingManager is the slow one (~sentence-transformers); everything else
# depends on it but is fast once em is cached.

@st.cache_resource(show_spinner=False)
def _get_em():
    from app.embeddings import EmbeddingManager
    return EmbeddingManager()

@st.cache_resource(show_spinner=False)
def _get_rag():
    from app.rag import RAGEngine
    return RAGEngine(_get_em())

@st.cache_resource(show_spinner=False)
def _get_gb():
    from app.graph_builder import GraphBuilder
    return GraphBuilder()

@st.cache_resource(show_spinner=False)
def _get_gq():
    from app.graph_query import GraphQueryEngine
    return GraphQueryEngine(_get_gb())

@st.cache_resource(show_spinner=False)
def _get_ca():
    from app.compliance_agent import ComplianceAgent
    return ComplianceAgent(_get_em())

@st.cache_resource(show_spinner=False)
def _get_pa():
    from app.pattern_agent import PatternAgent
    return PatternAgent(_get_em(), _get_gb())

@st.cache_resource(show_spinner=False)
def _get_kca():
    from app.knowledge_capture import KnowledgeCaptureAgent
    return KnowledgeCaptureAgent()


# ── Per-page loaders ──────────────────────────────────────────────────────────

def ensure_components() -> dict:
    """Load ALL components (for home page / backwards compat)."""
    components = {
        "em":  _get_em(),
        "rag": _get_rag(),
        "gb":  _get_gb(),
        "gq":  _get_gq(),
        "ca":  _get_ca(),
        "pa":  _get_pa(),
        "kca": _get_kca(),
    }
    st.session_state.update(components)
    return components


def load_for_page(keys: "list[str]") -> "dict":
    """
    Load only the components a specific page needs.
    Keys: any subset of ["em","rag","gb","gq","ca","pa","kca"]
    """
    loaders = {
        "em":  _get_em,
        "rag": _get_rag,
        "gb":  _get_gb,
        "gq":  _get_gq,
        "ca":  _get_ca,
        "pa":  _get_pa,
        "kca": _get_kca,
    }
    components = {k: loaders[k]() for k in keys}
    st.session_state.update(components)
    return components
