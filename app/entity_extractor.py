"""
Entity extraction for industrial documents.
Pulls equipment IDs, dates, regulation codes, people, and failure modes.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


# ─── Patterns ─────────────────────────────────────────────────────────────────

EQUIPMENT_PATTERNS = [
    r"\b([A-Z]{1,4}-\d{2,4}[A-Z]?)\b",          # P-101, FCV-12A, HE-201  (hyphen format — most reliable)
    r"\b([PVECTHFKB]\d{3,4}[A-Z]?)\b",           # V205, E304, P101 — single-letter prefix only (reduced false positives)
    r"(?:Pump|Vessel|Valve|Exchanger|Compressor|Tank)\s+([A-Z0-9\-]+)",
]

# Words that look like equipment IDs but aren't
_EQ_BLOCKLIST = {
    "API", "ISO", "SOP", "PPE", "PTW", "LNG", "LPG", "CNG", "HSD", "MOC",
    "HSE", "RCA", "NDT", "LOTO", "RPM", "PSI", "BAR", "KPA", "KWH",
}

REGULATION_PATTERNS = [
    (r"OISD[-\s]?(\d{2,3})", "OISD"),
    (r"Factory\s+Act\s+(?:Section\s+)?(\d+)", "Factory Act"),
    (r"DGMS\s+Circular\s+(?:No\.?\s*)?(\d+)", "DGMS"),
    (r"IS\s*:\s*(\d{4,5})", "IS Standard"),
    (r"PESO\s+(?:Circular\s+)?(\w+)", "PESO"),
]

FAILURE_KEYWORDS = [
    "seal failure", "bearing failure", "corrosion", "leak", "vibration",
    "overheating", "cavitation", "blockage", "rupture", "explosion",
    "fire", "gas leak", "pressure surge", "erosion", "fatigue crack",
    "coupling failure", "impeller damage", "mechanical failure",
]

DATE_PATTERNS = [
    (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", "%d/%m/%Y"),
    (r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", "dMonY"),
    (r"\b(\d{4})[/-](\d{2})[/-](\d{2})\b", "ISO"),
]

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


# ─── Extractor ────────────────────────────────────────────────────────────────

class EntityExtractor:
    """Extracts structured entities from industrial text."""

    def __init__(self):
        self._nlp = None  # lazy load spaCy

    def _get_nlp(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("[WARN] spaCy model 'en_core_web_sm' not found — "
                      "run: python -m spacy download en_core_web_sm. Person extraction disabled.")
                self._nlp = False
            except ImportError:
                print("[WARN] spaCy not installed — person extraction disabled.")
                self._nlp = False
        return self._nlp

    # ── Equipment IDs ─────────────────────────────────────────────────────────

    def extract_equipment_ids(self, text: str) -> List[str]:
        found = set()
        for pattern in EQUIPMENT_PATTERNS:
            for m in re.finditer(pattern, text):
                tag = m.group(1).strip()
                if len(tag) >= 3 and tag.upper() not in _EQ_BLOCKLIST:
                    found.add(tag)
        return sorted(found)

    # ── Dates ─────────────────────────────────────────────────────────────────

    def extract_dates(self, text: str) -> List[Dict]:
        dates = []
        seen = set()

        # DD/MM/YYYY or DD-MM-YYYY
        for m in re.finditer(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b", text):
            raw = m.group(0)
            if raw in seen:
                continue
            seen.add(raw)
            try:
                d = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                dates.append({"date_str": raw, "date_normalized": d.strftime("%Y-%m-%d")})
            except ValueError:
                pass

        # DD Month YYYY
        for m in re.finditer(
            r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+(\d{4})\b",
            text, re.IGNORECASE
        ):
            raw = m.group(0).strip()
            if raw in seen:
                continue
            seen.add(raw)
            try:
                month = MONTH_MAP[m.group(2)[:3].lower()]
                d = datetime(int(m.group(3)), month, int(m.group(1)))
                dates.append({"date_str": raw, "date_normalized": d.strftime("%Y-%m-%d")})
            except ValueError:
                pass

        # YYYY-MM-DD
        for m in re.finditer(r"\b(\d{4})[/\-](\d{2})[/\-](\d{2})\b", text):
            raw = m.group(0)
            if raw in seen:
                continue
            seen.add(raw)
            try:
                d = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                dates.append({"date_str": raw, "date_normalized": d.strftime("%Y-%m-%d")})
            except ValueError:
                pass

        return dates

    # ── Regulation references ─────────────────────────────────────────────────

    def extract_regulation_references(self, text: str) -> List[Dict]:
        refs = []
        seen = set()
        for pattern, standard_name in REGULATION_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                code = f"{standard_name}-{m.group(1)}"
                if code not in seen:
                    seen.add(code)
                    refs.append({"code": code, "standard_name": standard_name, "number": m.group(1)})
        return refs

    # ── People ────────────────────────────────────────────────────────────────

    def extract_people(self, text: str) -> List[str]:
        nlp = self._get_nlp()
        if not nlp:
            return []
        try:
            doc = nlp(text[:5000])  # limit for speed
            return list({ent.text for ent in doc.ents if ent.label_ == "PERSON" and len(ent.text.split()) >= 2})
        except Exception:
            return []

    # ── Failure modes ─────────────────────────────────────────────────────────

    def extract_failure_modes(self, text: str) -> List[str]:
        text_lower = text.lower()
        return [kw for kw in FAILURE_KEYWORDS if kw in text_lower]

    # ── Severity ──────────────────────────────────────────────────────────────

    def extract_severity(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["fatality", "fatal", "death", "critical", "explosion", "fire"]):
            return "Critical"
        if any(w in text_lower for w in ["serious", "high", "injury", "near-miss", "near miss"]):
            return "High"
        if any(w in text_lower for w in ["medium", "moderate", "significant"]):
            return "Medium"
        return "Low"

    # ── Combined ──────────────────────────────────────────────────────────────

    def extract_all(self, text: str, source_file: str) -> Dict:
        return {
            "source_file": source_file,
            "equipment_ids": self.extract_equipment_ids(text),
            "dates": self.extract_dates(text),
            "regulation_refs": self.extract_regulation_references(text),
            "people": self.extract_people(text),
            "failure_modes": self.extract_failure_modes(text),
            "severity": self.extract_severity(text),
        }

    def extract_from_chunks(self, chunks: List[Dict]) -> List[Dict]:
        results = []
        for chunk in chunks:
            entities = self.extract_all(chunk["text"], chunk["source_file"])
            entities["chunk_id"] = chunk["chunk_id"]
            entities["doc_type"] = chunk.get("doc_type", "general")
            results.append(entities)
        return results

    def aggregate_for_document(self, chunk_entities: List[Dict], source_file: str) -> Dict:
        """Merge entities from all chunks of one document."""
        all_equipment = set()
        all_dates = []
        all_regs = []
        all_people = set()
        all_failures = set()

        for e in chunk_entities:
            if e["source_file"] != source_file:
                continue
            all_equipment.update(e["equipment_ids"])
            all_dates.extend(e["dates"])
            all_regs.extend(e["regulation_refs"])
            all_people.update(e["people"])
            all_failures.update(e["failure_modes"])

        # deduplicate regulation refs by code
        seen_codes = set()
        unique_regs = []
        for r in all_regs:
            if r["code"] not in seen_codes:
                seen_codes.add(r["code"])
                unique_regs.append(r)

        return {
            "source_file": source_file,
            "equipment_ids": sorted(all_equipment),
            "dates": all_dates[:20],
            "regulation_refs": unique_regs,
            "people": sorted(all_people),
            "failure_modes": sorted(all_failures),
        }
