"""
Compliance gap detection agent.
Compares procedure documents against regulatory requirements.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

from app.embeddings import EmbeddingManager
from app.llm_client import get_llm_response


COMPLIANCE_SYSTEM = """You are a regulatory compliance expert for Indian heavy industry.
You specialize in OISD standards, the Factories Act 1948, DGMS circulars, and PESO regulations.

When comparing a procedure against a regulation, you must:
1. Identify EVERY specific requirement in the regulation
2. Check if the procedure explicitly addresses each requirement
3. Flag gaps with exact quotes from both documents
4. Be conservative — if a requirement is only partially addressed, mark it PARTIAL

Always respond in valid JSON format."""


class ComplianceAgent:
    """Detects compliance gaps between procedures and regulations."""

    def __init__(self, embedding_manager: EmbeddingManager = None):
        self.em = embedding_manager or EmbeddingManager()

    def _get_doc_text(self, source_file: str, max_chars: int = 3000) -> str:
        chunks = self.em.get_all_for_file(source_file)
        return " ".join(c["text"] for c in chunks)[:max_chars]

    def check_compliance(self, procedure_file: str, regulation_id: str) -> Dict:
        """
        Compare one procedure file against one regulation.
        Returns structured gap analysis.
        """
        proc_text = self._get_doc_text(procedure_file)
        if not proc_text:
            return {"error": f"Procedure not found: {procedure_file}"}

        # Find regulation text from ChromaDB
        reg_results = self.em.search(
            f"{regulation_id} requirements obligations", n_results=5,
            filter_doc_type="regulations"
        )
        if not reg_results:
            reg_text = f"Regulation {regulation_id} — text not available in knowledge base."
        else:
            reg_text = "\n".join(r["text"] for r in reg_results[:3])[:2000]

        user_prompt = f"""Compare this PROCEDURE against this REGULATION and identify compliance gaps.

PROCEDURE ({Path(procedure_file).name}):
{proc_text}

REGULATION ({regulation_id}):
{reg_text}

Respond in this exact JSON format:
{{
  "regulation_id": "{regulation_id}",
  "procedure_file": "{Path(procedure_file).name}",
  "compliance_status": "COMPLIANT | PARTIAL | NON_COMPLIANT",
  "overall_score": 0-100,
  "met_requirements": ["requirement 1", "requirement 2"],
  "gaps": [
    {{
      "requirement": "exact requirement text",
      "gap_description": "what is missing",
      "severity": "Critical | High | Medium | Low",
      "recommendation": "specific action to fix"
    }}
  ],
  "confidence": 0.0-1.0
}}"""

        response = get_llm_response(COMPLIANCE_SYSTEM, user_prompt)

        # Parse JSON from response
        try:
            # Find JSON block in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response)
        except Exception:
            result = {
                "regulation_id": regulation_id,
                "procedure_file": Path(procedure_file).name,
                "compliance_status": "UNKNOWN",
                "overall_score": 0,
                "met_requirements": [],
                "gaps": [{"requirement": "Parse error", "gap_description": response[:200],
                          "severity": "Unknown", "recommendation": "Review manually"}],
                "confidence": 0.5,
                "raw_response": response,
            }
        return result

    def audit_all_procedures(self) -> List[Dict]:
        """Run compliance check for all procedure × regulation pairs."""
        # Get all procedure files
        proc_results = self.em.search("procedure safety maintenance", n_results=20,
                                       filter_doc_type="procedures")
        proc_files = list({r["source_file"] for r in proc_results})

        # Get all regulations
        reg_results = self.em.search("OISD Factory Act DGMS regulation requirement", n_results=20,
                                      filter_doc_type="regulations")
        reg_refs = []
        from app.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        for r in reg_results:
            refs = extractor.extract_regulation_references(r["text"])
            reg_refs.extend(refs)

        # Deduplicate regulation IDs
        reg_ids = list({ref["code"] for ref in reg_refs})
        if not reg_ids:
            reg_ids = ["OISD-118", "Factory Act-31", "OISD-116"]  # common defaults

        # Cap at 3 procedures × 2 regulations = 6 LLM calls max (Groq free tier: ~30/min)
        audit_results = []
        for proc_file in proc_files[:3]:
            for reg_id in reg_ids[:2]:
                result = self.check_compliance(proc_file, reg_id)
                audit_results.append(result)

        return audit_results

    def generate_compliance_report(self) -> Dict:
        """Full compliance audit with executive summary."""
        audit_results = self.audit_all_procedures()

        if not audit_results:
            return {
                "summary": {"total_checks": 0, "compliant": 0, "partial": 0, "non_compliant": 0},
                "critical_gaps": [],
                "recommendations": ["Upload procedure and regulation documents first."],
                "full_results": [],
            }

        compliant = [r for r in audit_results if r.get("compliance_status") == "COMPLIANT"]
        partial   = [r for r in audit_results if r.get("compliance_status") == "PARTIAL"]
        non_comp  = [r for r in audit_results if r.get("compliance_status") == "NON_COMPLIANT"]

        # Collect critical gaps
        critical_gaps = []
        for r in non_comp + partial:
            for gap in r.get("gaps", []):
                if gap.get("severity") in ("Critical", "High"):
                    critical_gaps.append({
                        "procedure": r.get("procedure_file"),
                        "regulation": r.get("regulation_id"),
                        **gap,
                    })

        # Generate recommendations
        recommendations = list({g["recommendation"] for g in critical_gaps if g.get("recommendation")})

        return {
            "summary": {
                "total_checks": len(audit_results),
                "compliant": len(compliant),
                "partial": len(partial),
                "non_compliant": len(non_comp),
            },
            "critical_gaps": critical_gaps[:10],
            "recommendations": recommendations[:5],
            "full_results": audit_results,
        }

    def check_specific_requirement(self, requirement_text: str) -> Dict:
        """Search procedures for how a specific requirement is addressed."""
        results = self.em.search(requirement_text, n_results=5,
                                  filter_doc_type="procedures")
        if not results:
            return {
                "requirement": requirement_text,
                "addressed_in": [],
                "gap": True,
                "evidence": "No procedures found addressing this requirement.",
            }

        files = [r["source_file"] for r in results]
        evidence = results[0]["text"][:500] if results else ""
        return {
            "requirement": requirement_text,
            "addressed_in": list(set(Path(f).name for f in files)),
            "gap": len(results) == 0,
            "evidence": evidence,
            "score": results[0]["score"] if results else 0,
        }
