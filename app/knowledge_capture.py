"""
KILLER FEATURE 1: Expert Knowledge Capture Agent.

Conducts a structured interview with a retiring/senior engineer via chat,
extracts undocumented "tribal knowledge", and stores it as a searchable
knowledge entry in ChromaDB — preserving expertise that would otherwise
be lost when the engineer leaves.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from app.llm_client import get_llm_response
from app.config import DOCS_PATH


INTERVIEW_SYSTEM = """You are an industrial knowledge preservation specialist.
Your job is to conduct a structured interview with an experienced engineer to extract
their undocumented operational knowledge — the "tribal knowledge" that exists only in
their head and would be lost when they retire.

Rules:
1. Ask one focused question at a time
2. Follow up on specific technical details mentioned
3. Extract: equipment quirks, failure warning signs, undocumented procedures, lessons learned
4. Summarize concretely — include specific values, timeframes, and equipment IDs
5. Be conversational but technically precise"""


# ─── Interview session ────────────────────────────────────────────────────────

class KnowledgeCaptureSession:
    """
    Manages a multi-turn interview conversation.
    Each session captures knowledge from one expert about one topic area.
    """

    INTERVIEW_TEMPLATES = {
        "equipment_expertise": [
            "Which piece of equipment in this plant do you know best — the one you've spent the most time troubleshooting?",
            "What's the most unusual problem you've ever seen on that equipment that isn't in any manual?",
            "What are the early warning signs that experienced operators recognize but newer engineers miss?",
            "Is there a startup or shutdown sequence that differs from the documented procedure? What's the real-world trick?",
            "What's the single most dangerous thing someone new to this equipment would likely do wrong?",
        ],
        "maintenance_wisdom": [
            "What maintenance task looks straightforward in the SOP but is actually much harder in practice? Why?",
            "Are there any parts that always fail earlier than the manufacturer's recommendation says?",
            "What tool or technique have you developed over the years that isn't in any official document?",
            "Describe a near-miss incident that was never formally reported but taught you something important.",
            "What would you tell someone taking over your role on their first week?",
        ],
        "process_knowledge": [
            "Which process parameters do you watch most carefully that aren't on the standard monitoring list?",
            "How do you know when the process is running 'right' — the feel of it — beyond what the instruments say?",
            "What seasonal or weather-related effects have you noticed on plant performance that aren't documented?",
            "Are there any vendor or contractor relationships where informal knowledge is shared that should be captured?",
            "What has changed about how this plant runs that old documentation doesn't reflect yet?",
        ],
    }

    def __init__(self, expert_name: str, role: str, topic: str = "equipment_expertise"):
        self.session_id = str(uuid.uuid4())[:8]
        self.expert_name = expert_name
        self.role = role
        self.topic = topic
        self.conversation: List[Dict] = []
        self.knowledge_entries: List[Dict] = []
        self.question_index = 0
        self.questions = self.INTERVIEW_TEMPLATES.get(topic, self.INTERVIEW_TEMPLATES["equipment_expertise"])
        self.created_at = datetime.now().isoformat()
        self._in_followup = False  # prevents chained follow-ups creating an infinite loop

    def get_next_question(self) -> Optional[str]:
        """Get the next interview question, or None if interview is complete."""
        if self.question_index < len(self.questions):
            q = self.questions[self.question_index]
            self.question_index += 1
            return q
        return None

    def process_answer(self, question: str, answer: str) -> Dict:
        """
        Process an expert's answer: extract knowledge, generate follow-up.
        Returns {follow_up_question, extracted_knowledge, is_complete}.
        """
        self.conversation.append({"role": "expert", "question": question, "answer": answer})

        # Build conversation history for context
        history = "\n".join(
            f"Q: {item['question']}\nA: {item['answer']}"
            for item in self.conversation[-3:]
        )

        # Extract structured knowledge from this answer
        extract_prompt = f"""Expert: {self.expert_name} ({self.role})
Topic: {self.topic}

Recent conversation:
{history}

Extract the key knowledge from the expert's latest answer as structured data.
Identify: equipment IDs mentioned, specific failure modes, undocumented procedures,
warning signs, numerical thresholds, and any "tribal knowledge" nuggets.

Respond in JSON:
{{
  "knowledge_type": "equipment_quirk | failure_warning | undocumented_procedure | lesson_learned | process_insight",
  "title": "short title for this knowledge item",
  "content": "detailed knowledge content, verbatim where possible",
  "equipment_ids": ["list of equipment tags mentioned"],
  "tags": ["searchable tags"],
  "confidence": "High | Medium | Low",
  "actionable": true or false
}}"""

        extracted = get_llm_response(INTERVIEW_SYSTEM, extract_prompt, max_tokens=600)
        try:
            import re
            parsed = json.loads(re.search(r'\{.*\}', extracted, re.DOTALL).group())
        except Exception:
            parsed = {
                "knowledge_type": "lesson_learned",
                "title": f"Knowledge from {self.expert_name}",
                "content": answer,
                "equipment_ids": [],
                "tags": [self.topic],
                "confidence": "Medium",
                "actionable": True,
            }

        knowledge_entry = {
            "id": f"KE_{self.session_id}_{len(self.knowledge_entries)}",
            "expert_name": self.expert_name,
            "expert_role": self.role,
            "session_id": self.session_id,
            "captured_at": datetime.now().isoformat(),
            **parsed,
        }
        self.knowledge_entries.append(knowledge_entry)

        # Generate follow-up or move to next base question
        next_q = self.get_next_question()
        is_complete = next_q is None

        # Generate a contextual follow-up only when answer is rich AND we're not already
        # answering a follow-up (prevents infinite follow-up chaining)
        if len(answer.split()) > 30 and not is_complete and not self._in_followup:
            followup_prompt = f"""The expert said: "{answer[:500]}"

Generate one specific follow-up question that digs deeper into the most interesting technical detail they mentioned.
Keep it under 20 words. Ask about a specific number, timeframe, or equipment detail they hinted at."""

            followup = get_llm_response(INTERVIEW_SYSTEM, followup_prompt, max_tokens=100)
            if len(followup.strip()) > 10:
                display_q = followup.strip()
                self.question_index -= 1  # re-insert the consumed template question
                self._in_followup = True
            else:
                display_q = next_q or "Thank you — that concludes this session."
                self._in_followup = False
        else:
            display_q = next_q or "Thank you — that concludes this session."
            self._in_followup = False

        return {
            "follow_up_question": display_q,
            "extracted_knowledge": knowledge_entry,
            "is_complete": is_complete,
            "total_entries": len(self.knowledge_entries),
        }

    def finalize_and_save(self) -> Dict:
        """
        Save all captured knowledge as documents for ingestion into ChromaDB.
        Returns the saved file paths.
        """
        saved_files = []
        output_dir = Path(DOCS_PATH) / "maintenance"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save individual knowledge entries as text files
        for entry in self.knowledge_entries:
            filename = f"expert_knowledge_{self.session_id}_{entry['id']}.txt"
            filepath = output_dir / filename

            content = f"""EXPERT KNOWLEDGE CAPTURE
========================
Expert: {self.expert_name} ({self.role})
Date Captured: {entry['captured_at']}
Knowledge Type: {entry['knowledge_type']}
Title: {entry['title']}
Equipment: {', '.join(entry.get('equipment_ids', []))}
Confidence: {entry['confidence']}

KNOWLEDGE CONTENT:
{entry['content']}

Tags: {', '.join(entry.get('tags', []))}
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            saved_files.append(str(filepath))

        # Save session summary
        summary_file = output_dir / f"expert_session_summary_{self.session_id}.txt"
        summary_content = f"""EXPERT KNOWLEDGE SESSION SUMMARY
==================================
Expert: {self.expert_name} ({self.role})
Session ID: {self.session_id}
Topic: {self.topic}
Date: {self.created_at}
Total Knowledge Entries: {len(self.knowledge_entries)}

ENTRIES CAPTURED:
"""
        for i, entry in enumerate(self.knowledge_entries, 1):
            summary_content += f"\n{i}. [{entry['knowledge_type'].upper()}] {entry['title']}\n"
            summary_content += f"   Equipment: {', '.join(entry.get('equipment_ids', ['None']))}\n"
            summary_content += f"   {entry['content'][:200]}...\n"

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_content)
        saved_files.append(str(summary_file))

        return {
            "session_id": self.session_id,
            "expert": self.expert_name,
            "entries_captured": len(self.knowledge_entries),
            "files_saved": saved_files,
            "message": f"Captured {len(self.knowledge_entries)} knowledge entries. Ready for ingestion.",
        }


class KnowledgeCaptureAgent:
    """Manages multiple capture sessions and provides summary analytics."""

    def __init__(self):
        self.sessions: Dict[str, KnowledgeCaptureSession] = {}

    def start_session(self, expert_name: str, role: str,
                      topic: str = "equipment_expertise") -> KnowledgeCaptureSession:
        session = KnowledgeCaptureSession(expert_name, role, topic)
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[KnowledgeCaptureSession]:
        return self.sessions.get(session_id)

    def get_all_sessions_summary(self) -> List[Dict]:
        return [
            {
                "session_id": s.session_id,
                "expert": s.expert_name,
                "role": s.role,
                "topic": s.topic,
                "entries": len(s.knowledge_entries),
                "created_at": s.created_at,
            }
            for s in self.sessions.values()
        ]
