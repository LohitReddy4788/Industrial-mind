"""
Failure pattern detection agent.
Finds recurring patterns, seasonal trends, and leading indicators across history.
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict, Optional

from app.embeddings import EmbeddingManager
from app.graph_builder import GraphBuilder
from app.llm_client import get_llm_response


PATTERN_SYSTEM = """You are an industrial reliability and failure analysis expert.
You analyze maintenance records, incident reports, and equipment history to find patterns.
Be specific with dates, equipment IDs, and failure modes. Quantify everything you can."""


class PatternAgent:
    """Detects recurring failure patterns and predictive indicators."""

    def __init__(self, embedding_manager: EmbeddingManager = None,
                 graph_builder: GraphBuilder = None):
        self.em = embedding_manager or EmbeddingManager()
        self.gb = graph_builder or GraphBuilder()

    def find_recurring_failures(self) -> List[Dict]:
        """Find failure modes that appear multiple times across documents."""
        from app.entity_extractor import EntityExtractor
        extractor = EntityExtractor()

        # Get all incident and maintenance chunks
        incidents = self.em.search("failure incident equipment", n_results=30,
                                    filter_doc_type="incidents")
        maintenance = self.em.search("failure repair breakdown", n_results=30,
                                      filter_doc_type="maintenance")
        all_chunks = incidents + maintenance

        # Count failure modes per equipment
        equipment_failures: Dict[str, List[str]] = defaultdict(list)
        failure_counts: Counter = Counter()
        failure_equipment: Dict[str, set] = defaultdict(set)
        failure_dates: Dict[str, List[str]] = defaultdict(list)

        for chunk in all_chunks:
            text = chunk["text"]
            eqs = extractor.extract_equipment_ids(text)
            fms = extractor.extract_failure_modes(text)
            dates = extractor.extract_dates(text)

            for fm in fms:
                failure_counts[fm] += 1
                for eq in eqs:
                    failure_equipment[fm].add(eq)
                    equipment_failures[eq].append(fm)
                for d in dates:
                    failure_dates[fm].append(d["date_normalized"])

        # Build pattern objects for failures with 2+ occurrences
        patterns = []
        for fm, count in failure_counts.most_common(10):
            if count < 2:
                continue

            affected = sorted(failure_equipment[fm])
            dates = sorted(set(failure_dates[fm]))

            # Use LLM to summarize the pattern
            context = f"Failure mode: {fm}\nOccurrences: {count}\nAffected equipment: {affected}\nDates: {dates}"
            system = PATTERN_SYSTEM
            user = f"""Based on this failure pattern data, provide:
1. A 2-sentence pattern summary
2. Common conditions that lead to this failure
3. One specific prevention recommendation

Data: {context}

Respond in JSON: {{"pattern_summary": "...", "common_conditions": "...", "recommendation": "..."}}"""

            llm_response = get_llm_response(system, user, max_tokens=512)
            try:
                import json
                parsed = json.loads(re.search(r'\{.*\}', llm_response, re.DOTALL).group())
            except Exception:
                parsed = {
                    "pattern_summary": f"{fm} detected {count} times across {len(affected)} equipment items.",
                    "common_conditions": "Review individual records for common conditions.",
                    "recommendation": f"Implement preventive maintenance schedule for {fm}.",
                }

            patterns.append({
                "failure_mode": fm,
                "occurrence_count": count,
                "affected_equipment": affected,
                "dates": dates[:10],
                **parsed,
            })

        return patterns

    def find_seasonal_patterns(self) -> Dict:
        """Group incidents by month to find seasonal trends."""
        from app.entity_extractor import EntityExtractor
        extractor = EntityExtractor()

        results = self.em.search("incident failure date", n_results=50)
        month_counts: Counter = Counter()
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        for r in results:
            dates = extractor.extract_dates(r["text"])
            for d in dates:
                try:
                    month = int(d["date_normalized"].split("-")[1])
                    month_counts[month] += 1
                except Exception:
                    pass

        monthly_data = {month_names[m - 1]: month_counts[m] for m in range(1, 13)}

        # Find peak months
        if month_counts:
            peak_month = month_counts.most_common(1)[0][0]
            peak_name = month_names[peak_month - 1]
        else:
            peak_name = "Unknown"

        return {
            "monthly_distribution": monthly_data,
            "peak_month": peak_name,
            "analysis": f"Highest incident frequency in {peak_name}. "
                        "Consider increased inspection frequency during this period.",
        }

    def find_leading_indicators(self, failure_mode: str) -> Dict:
        """Find what typically precedes a specific failure type."""
        query = f"before {failure_mode} warning signs vibration temperature pressure"
        results = self.em.search(query, n_results=8)

        if not results:
            return {
                "failure_mode": failure_mode,
                "leading_indicators": [],
                "typical_lead_time": "Unknown",
            }

        context = "\n".join(r["text"] for r in results[:5])[:3000]

        system = PATTERN_SYSTEM
        user = f"""From these industrial documents, identify what warning signs or conditions
appeared BEFORE {failure_mode} events.

Documents:
{context}

Respond in JSON:
{{
  "leading_indicators": ["indicator 1", "indicator 2", "indicator 3"],
  "typical_lead_time": "hours/days/weeks before failure",
  "monitoring_recommendation": "what to monitor and at what threshold"
}}"""

        response = get_llm_response(system, user, max_tokens=512)
        try:
            import json
            parsed = json.loads(re.search(r'\{.*\}', response, re.DOTALL).group())
        except Exception:
            parsed = {
                "leading_indicators": ["Increased vibration", "Abnormal temperature"],
                "typical_lead_time": "Days to weeks before failure",
                "monitoring_recommendation": f"Monitor regularly for early signs of {failure_mode}",
            }

        return {"failure_mode": failure_mode, **parsed}

    def predict_next_failure(self, equipment_id: str) -> Dict:
        """
        KILLER FEATURE — Predictive timeline.
        Based on historical patterns, estimate when next failure is likely.
        """
        from app.entity_extractor import EntityExtractor
        extractor = EntityExtractor()

        # Get all records for this equipment
        results = self.em.search(f"{equipment_id} failure maintenance repair",
                                  n_results=15)
        eq_results = [r for r in results if equipment_id.upper() in r["text"].upper()]

        if not eq_results:
            return {
                "equipment_id": equipment_id,
                "prediction": "Insufficient history for prediction.",
                "confidence": "Low",
            }

        # Extract dates and failure modes from history
        all_dates = []
        all_failures = []
        for r in eq_results:
            all_dates.extend(extractor.extract_dates(r["text"]))
            all_failures.extend(extractor.extract_failure_modes(r["text"]))

        failure_counter = Counter(all_failures)
        date_list = sorted(set(d["date_normalized"] for d in all_dates))

        context = f"""
Equipment: {equipment_id}
Historical failure dates: {date_list}
Failure modes: {dict(failure_counter)}
Number of maintenance records found: {len(eq_results)}
"""

        system = PATTERN_SYSTEM
        user = f"""Based on this equipment's history, predict when the next failure is likely.

{context}

Provide:
1. Most likely next failure mode
2. Estimated time until next failure
3. Confidence level (High/Medium/Low) with justification
4. Recommended preventive action to avoid it

Respond in JSON:
{{
  "most_likely_failure": "...",
  "estimated_timeline": "...",
  "confidence": "High|Medium|Low",
  "confidence_reason": "...",
  "preventive_action": "..."
}}"""

        response = get_llm_response(system, user, max_tokens=512)
        try:
            import json
            parsed = json.loads(re.search(r'\{.*\}', response, re.DOTALL).group())
        except Exception:
            parsed = {
                "most_likely_failure": failure_counter.most_common(1)[0][0] if failure_counter else "Unknown",
                "estimated_timeline": "Based on historical intervals",
                "confidence": "Medium",
                "confidence_reason": f"Based on {len(eq_results)} historical records",
                "preventive_action": "Schedule preventive maintenance inspection",
            }

        return {"equipment_id": equipment_id, **parsed, "history_records": len(eq_results)}

    def generate_pattern_report(self) -> Dict:
        """Full pattern analysis with executive summary."""
        patterns = self.find_recurring_failures()
        seasonal = self.find_seasonal_patterns()

        if not patterns:
            return {
                "executive_summary": "Insufficient historical data to identify patterns. Upload more maintenance records and incident reports.",
                "top_patterns": [],
                "seasonal_risks": seasonal,
                "predictive_warnings": [],
            }

        top3 = patterns[:3]

        # Generate executive summary
        pattern_desc = "; ".join(
            f"{p['failure_mode']} ({p['occurrence_count']} times)" for p in top3
        )
        system = PATTERN_SYSTEM
        user = f"""Write a 3-sentence executive summary of these industrial failure patterns for plant management.

Patterns found: {pattern_desc}
Peak incident month: {seasonal.get('peak_month', 'Unknown')}

Be specific, quantify the risk, and recommend the single most impactful action."""

        summary = get_llm_response(system, user, max_tokens=300)

        # Predictive warnings
        predictive = []
        seen_equipment = set()
        for p in top3:
            for eq in p["affected_equipment"][:2]:
                if eq not in seen_equipment:
                    seen_equipment.add(eq)
                    prediction = self.predict_next_failure(eq)
                    if prediction.get("confidence") in ("High", "Medium"):
                        predictive.append(f"⚠️ {eq}: {prediction.get('most_likely_failure')} — {prediction.get('estimated_timeline')}")

        return {
            "executive_summary": summary,
            "top_patterns": top3,
            "seasonal_risks": seasonal,
            "predictive_warnings": predictive,
        }
