"""
Document ingestion pipeline.
Handles PDF (text + scanned), Excel/CSV, and plain text.
Returns normalized chunks with metadata.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

from app.config import DOCS_PATH


# ─── Data structures ──────────────────────────────────────────────────────────

def _make_page(text: str, page_num: int, source_file: str, doc_type: str) -> Dict:
    return {
        "text": clean_text(text),
        "page_num": page_num,
        "source_file": source_file,
        "doc_type": doc_type,
    }


def _make_chunk(text: str, chunk_id: str, source_file: str, page_num: int,
                doc_type: str, char_start: int) -> Dict:
    return {
        "text": text,
        "chunk_id": chunk_id,
        "source_file": source_file,
        "page_num": page_num,
        "doc_type": doc_type,
        "char_start": char_start,
    }


# ─── Utilities ────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters."""
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_doc_type(file_path: str) -> str:
    """Infer document category from its parent folder name."""
    parts = Path(file_path).parts
    for part in reversed(parts):
        if part in ("maintenance", "regulations", "incidents", "procedures"):
            return part
    return "general"


# ─── Loaders ─────────────────────────────────────────────────────────────────

class DocumentLoader:
    """Loads all industrial document types into a uniform page list."""

    def load_pdf(self, file_path: str) -> List[Dict]:
        """Load a text-based PDF using PyMuPDF."""
        try:
            import fitz
        except ImportError:
            print("[WARN] pymupdf not installed — skipping PDF:", file_path)
            return []

        pages = []
        doc_type = get_doc_type(file_path)
        try:
            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    pages.append(_make_page(text, i + 1, file_path, doc_type))
            doc.close()
            print(f"[PDF] {Path(file_path).name}: {len(pages)} pages extracted")
        except Exception as e:
            print(f"[ERROR] PDF load failed {file_path}: {e}")
        return pages

    def detect_if_scanned(self, file_path: str) -> bool:
        """Return True if PDF has no extractable text (needs OCR)."""
        try:
            import fitz
            doc = fitz.open(file_path)
            total_chars = sum(len(p.get_text()) for p in doc)
            doc.close()
            return total_chars < 100
        except Exception:
            return False

    def load_scanned_pdf(self, file_path: str) -> List[Dict]:
        """OCR a scanned PDF using pytesseract."""
        try:
            import fitz
            from PIL import Image
            import pytesseract
            import io
        except ImportError:
            print("[WARN] OCR dependencies missing — skipping:", file_path)
            return []

        pages = []
        doc_type = get_doc_type(file_path)
        try:
            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR accuracy
                pix = page.get_pixmap(matrix=mat)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img)
                if text.strip():
                    pages.append(_make_page(text, i + 1, file_path, doc_type))
            doc.close()
            print(f"[OCR] {Path(file_path).name}: {len(pages)} pages scanned")
        except pytesseract.TesseractNotFoundError:
            print(f"[ERROR] Tesseract binary not found — install from https://github.com/UB-Mannheim/tesseract/wiki")
            pages.append(_make_page(
                f"[OCR FAILED] Tesseract not installed. Install the Tesseract binary and retry.",
                1, file_path, doc_type,
            ))
        except Exception as e:
            print(f"[ERROR] OCR failed {file_path}: {e}")
        return pages

    def load_excel(self, file_path: str) -> List[Dict]:
        """Convert each Excel sheet to text."""
        try:
            import pandas as pd
        except ImportError:
            print("[WARN] pandas not installed — skipping Excel:", file_path)
            return []

        pages = []
        doc_type = get_doc_type(file_path)
        try:
            xl = pd.ExcelFile(file_path)
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name)
                text = f"Sheet: {sheet_name}\n" + df.to_string(index=False)
                pages.append(_make_page(text, 1, file_path, doc_type))
            print(f"[XLSX] {Path(file_path).name}: {len(pages)} sheets loaded")
        except Exception as e:
            print(f"[ERROR] Excel load failed {file_path}: {e}")
        return pages

    def load_csv(self, file_path: str) -> List[Dict]:
        try:
            import pandas as pd
        except ImportError:
            return []

        doc_type = get_doc_type(file_path)
        try:
            df = pd.read_csv(file_path)
            text = df.to_string(index=False)
            return [_make_page(text, 1, file_path, doc_type)]
        except Exception as e:
            print(f"[ERROR] CSV load failed {file_path}: {e}")
            return []

    def load_text(self, file_path: str) -> List[Dict]:
        doc_type = get_doc_type(file_path)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return [_make_page(text, 1, file_path, doc_type)]
        except Exception as e:
            print(f"[ERROR] Text load failed {file_path}: {e}")
            return []

    def load_docx(self, file_path: str) -> List[Dict]:
        """Load a Word .docx file using python-docx."""
        doc_type = get_doc_type(file_path)
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            if not text.strip():
                print(f"[WARN] No text extracted from DOCX: {file_path}")
                return []
            print(f"[DOCX] {Path(file_path).name}: {len(text)} chars extracted")
            return [_make_page(text, 1, file_path, doc_type)]
        except ImportError:
            print("[WARN] python-docx not installed — run `pip install python-docx`. Skipping:", file_path)
            return []
        except Exception as e:
            print(f"[ERROR] DOCX load failed {file_path}: {e}")
            return []

    def load_file(self, file_path: str) -> List[Dict]:
        """Auto-detect file type and load."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            if self.detect_if_scanned(file_path):
                print(f"[INFO] Detected scanned PDF: {Path(file_path).name}")
                return self.load_scanned_pdf(file_path)
            return self.load_pdf(file_path)
        elif ext in (".xlsx", ".xls"):
            return self.load_excel(file_path)
        elif ext == ".csv":
            return self.load_csv(file_path)
        elif ext in (".txt", ".md"):
            return self.load_text(file_path)
        elif ext == ".docx":
            return self.load_docx(file_path)
        else:
            print(f"[SKIP] Unsupported file type: {ext}")
            return []

    def load_folder(self, folder_path: str = None) -> List[Dict]:
        """Recursively load all documents from a folder."""
        folder_path = folder_path or DOCS_PATH
        all_pages = []
        supported = {".pdf", ".xlsx", ".xls", ".csv", ".txt", ".md", ".docx"}

        for path in Path(folder_path).rglob("*"):
            if path.suffix.lower() in supported and path.is_file():
                pages = self.load_file(str(path))
                all_pages.extend(pages)

        print(f"\n[SUMMARY] Loaded {len(all_pages)} pages from {folder_path}")
        return all_pages


# ─── Chunker ──────────────────────────────────────────────────────────────────

class TextChunker:
    """Splits pages into overlapping chunks for embedding."""

    def chunk_documents(self, pages: List[Dict], chunk_size: int = 512,
                        overlap: int = 64) -> List[Dict]:
        chunks = []
        for page in pages:
            text = page["text"]
            words = text.split()
            if not words:
                continue

            start = 0
            chunk_idx = 0
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk_text = " ".join(words[start:end])
                if len(chunk_text.strip()) > 50:  # skip tiny fragments
                    chunk_id = f"{Path(page['source_file']).stem}_p{page['page_num']}_c{chunk_idx}"
                    chunks.append(_make_chunk(
                        text=chunk_text,
                        chunk_id=chunk_id,
                        source_file=page["source_file"],
                        page_num=page["page_num"],
                        doc_type=page["doc_type"],
                        char_start=start,
                    ))
                    chunk_idx += 1
                start += chunk_size - overlap

        print(f"[CHUNKER] Created {len(chunks)} chunks from {len(pages)} pages")
        return chunks
