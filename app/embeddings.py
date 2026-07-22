"""
Embeddings + ChromaDB vector store.
Uses sentence-transformers (free, local) by default.
Falls back to OpenAI embeddings if OPENAI_API_KEY is set.
"""

import os
import warnings
# Silence protobuf/tensorflow version mismatch before any chromadb/tf imports
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
warnings.filterwarnings("ignore", message=".*Protobuf.*")
warnings.filterwarnings("ignore", message=".*GenCode.*")

from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb

from app.config import CHROMA_DB_PATH, OPENAI_API_KEY

# ─── Sentence-transformer model (loaded once, used for both indexing & query) ──
_ST_MODEL = None

def _get_st_model():
    """Load sentence-transformer model once and cache in module-level var."""
    global _ST_MODEL
    if _ST_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            import os
            local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "paraphrase-MiniLM-L3-v2")
            model_path = local_path if os.path.exists(local_path) else "paraphrase-MiniLM-L3-v2"
            _ST_MODEL = SentenceTransformer(model_path)
        except Exception as e:
            print(f"[WARN] SentenceTransformer unavailable: {e}")
    return _ST_MODEL

def _embed(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts using sentence-transformers. Returns list of vectors."""
    model = _get_st_model()
    if model is None:
        return [[0.0] * 384 for _ in texts]
    vecs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vecs.tolist()


# ─── Manager ──────────────────────────────────────────────────────────────────

class EmbeddingManager:
    """Manages document embeddings stored in ChromaDB."""

    def __init__(self):
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        # Use no embedding_function — we supply embeddings manually.
        # This avoids ChromaDB's protobuf-wrapped SentenceTransformer that breaks
        # on version mismatch, and lets us control the model directly.
        self.collection = self.client.get_or_create_collection(
            name="industrial_docs",
        )
        # Pre-warm the model so first search isn't slow
        _get_st_model()

    def embed_and_store(self, chunks: List[Dict]) -> Dict:
        """Embed a list of chunks and store in ChromaDB. Skips duplicates."""
        if not chunks:
            return {"total_chunks": 0, "new_chunks_added": 0, "skipped": 0}

        existing_ids: set = set()
        try:
            existing = self.collection.get(include=[])
            existing_ids = set(existing["ids"])
        except Exception:
            pass

        new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]
        skipped = len(chunks) - len(new_chunks)

        if not new_chunks:
            return {"total_chunks": self.collection.count(),
                    "new_chunks_added": 0, "skipped": skipped}

        batch_size = 100
        added = 0
        for i in range(0, len(new_chunks), batch_size):
            batch = new_chunks[i : i + batch_size]
            texts = [c["text"] for c in batch]
            embeddings = _embed(texts)
            self.collection.add(
                ids=[c["chunk_id"] for c in batch],
                documents=texts,
                embeddings=embeddings,
                metadatas=[{
                    "source_file": c["source_file"],
                    "page_num": str(c["page_num"]),
                    "doc_type": c["doc_type"],
                    "char_start": str(c["char_start"]),
                } for c in batch],
            )
            added += len(batch)

        return {
            "total_chunks": self.collection.count(),
            "new_chunks_added": added,
            "skipped": skipped,
        }

    def search(self, query: str, n_results: int = 5,
               filter_doc_type: Optional[str] = None) -> List[Dict]:
        """Semantic search. Returns ranked chunks with metadata."""
        total = self.collection.count()
        if total == 0:
            return []

        # Never request more results than exist
        safe_n = min(n_results, total)
        where = {"doc_type": filter_doc_type} if filter_doc_type else None

        try:
            query_embedding = _embed([query])[0]
            kwargs: Dict = {
                "query_embeddings": [query_embedding],
                "n_results": safe_n,
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where
            results = self.collection.query(**kwargs)
        except Exception as e:
            print(f"[ChromaDB search error] {e}")
            return []

        hits = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            dist = results["distances"][0][i]
            hits.append({
                "text": doc,
                "source_file": meta.get("source_file", ""),
                "page_num": int(meta.get("page_num", 1)),
                "doc_type": meta.get("doc_type", ""),
                "score": round(1 / (1 + dist), 3),
            })
        return hits

    def get_all_for_file(self, source_file: str) -> List[Dict]:
        """Retrieve all stored chunks for a given file."""
        try:
            results = self.collection.get(
                where={"source_file": source_file},
                include=["documents", "metadatas"],
            )
            return [{"text": d, **m} for d, m in
                    zip(results["documents"], results["metadatas"])]
        except Exception:
            return []

    def delete_document(self, source_file: str):
        """Remove all chunks for a file."""
        try:
            self.collection.delete(where={"source_file": source_file})
        except Exception as e:
            print(f"[ChromaDB delete error] {e}")

    def get_stats(self) -> Dict:
        """Return stats about what's stored. Cached for 60s to avoid O(n) on every render."""
        import time
        now = time.time()
        cached = getattr(self, "_stats_cache", None)
        if cached and now - cached["ts"] < 60:
            return cached["data"]

        total = self.collection.count()
        if total == 0:
            result = {"total_chunks": 0, "total_documents": 0, "doc_types": {}}
        else:
            try:
                all_meta = self.collection.get(include=["metadatas"])["metadatas"]
                from collections import Counter
                type_counts = Counter(m.get("doc_type", "unknown") for m in all_meta)
                files = set(m.get("source_file", "") for m in all_meta)
                result = {
                    "total_chunks": total,
                    "total_documents": len(files),
                    "doc_types": dict(type_counts),
                }
            except Exception:
                result = {"total_chunks": total, "total_documents": 0, "doc_types": {}}

        self._stats_cache = {"ts": now, "data": result}
        return result


# ─── Full pipeline ────────────────────────────────────────────────────────────

def full_pipeline(
    docs_folder: str = None,
    file_paths: List[str] = None,
    embedding_manager: "EmbeddingManager" = None,
) -> Dict:
    """
    Load documents → chunk → extract entities → embed → store.
    Pass embedding_manager to reuse the shared cached instance.
    """
    from app.ingestion import DocumentLoader, TextChunker
    from app.entity_extractor import EntityExtractor

    loader = DocumentLoader()
    chunker = TextChunker()
    extractor = EntityExtractor()
    em = embedding_manager or EmbeddingManager()

    if file_paths:
        pages = []
        for fp in file_paths:
            pages.extend(loader.load_file(fp))
    else:
        pages = loader.load_folder(docs_folder)

    if not pages:
        return {"error": "No documents loaded", "chunks": [], "entities": []}

    chunks = chunker.chunk_documents(pages)
    entities = extractor.extract_from_chunks(chunks)
    store_result = em.embed_and_store(chunks)

    all_equipment: set = set()
    all_failures: set = set()
    for e in entities:
        all_equipment.update(e.get("equipment_ids", []))
        all_failures.update(e.get("failure_modes", []))

    return {
        "pages_loaded": len(pages),
        "chunks_created": len(chunks),
        "new_chunks_stored": store_result["new_chunks_added"],
        "equipment_found": sorted(all_equipment),
        "failure_modes_found": sorted(all_failures),
        "entities_extracted": len(entities),
        "chunks": chunks,
        "entities": entities,
    }
