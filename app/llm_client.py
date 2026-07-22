"""
LLM abstraction layer.
Supports Anthropic, OpenAI, Groq (free), Ollama, and a built-in
Smart RAG formatter that works with ZERO API keys.
"""

import re
from app.config import (
    llm_backend,
    ANTHROPIC_API_KEY, OPENAI_API_KEY, GROQ_API_KEY,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
)


def get_llm_response(system_prompt: str, user_prompt: str,
                     temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Call the configured LLM and return the text response."""
    backend = llm_backend()

    if backend == "anthropic":
        return _anthropic(system_prompt, user_prompt, temperature, max_tokens)
    elif backend == "openai":
        return _openai(system_prompt, user_prompt, temperature, max_tokens)
    elif backend == "groq":
        return _groq(system_prompt, user_prompt, temperature, max_tokens)
    elif backend == "ollama":
        return _ollama(system_prompt, user_prompt, temperature, max_tokens)
    else:
        return _smart_rag(system_prompt, user_prompt)


def get_llm_response_stream(system_prompt: str, user_prompt: str,
                            temperature: float = 0.5, max_tokens: int = 2048):
    """Streaming generator — yields text chunks as they arrive. Groq streams natively; others yield one chunk."""
    backend = llm_backend()
    if backend == "groq":
        yield from _groq_stream(system_prompt, user_prompt, temperature, max_tokens)
    else:
        # Non-Groq backends: call synchronously then yield the whole response
        result = get_llm_response(system_prompt, user_prompt, temperature, max_tokens)
        if result:
            yield result


# ── Backend implementations ────────────────────────────────────────────────────

def _anthropic(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return msg.content[0].text
    except ImportError:
        return "⚠️ **Anthropic package not installed** — run `pip install anthropic`."
    except Exception as e:
        err = str(e)
        if "authentication" in err.lower() or "api_key" in err.lower() or "401" in err:
            return "⚠️ **Anthropic API key invalid** — check ANTHROPIC_API_KEY in your .env file."
        if "rate" in err.lower() or "429" in err:
            return "⚠️ **Anthropic rate limit** — please wait a moment and try again."
        return f"⚠️ **Anthropic error:** {err}"


def _openai(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except ImportError:
        return "⚠️ **OpenAI package not installed** — run `pip install openai`."
    except Exception as e:
        err = str(e)
        if "authentication" in err.lower() or "api_key" in err.lower() or "401" in err:
            return "⚠️ **OpenAI API key invalid** — check OPENAI_API_KEY in your .env file."
        if "rate" in err.lower() or "429" in err:
            return "⚠️ **OpenAI rate limit** — please wait a moment and try again."
        if "quota" in err.lower() or "billing" in err.lower():
            return "⚠️ **OpenAI quota exceeded** — check your billing at platform.openai.com."
        return f"⚠️ **OpenAI error:** {err}"


def _groq(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int,
          _retry: int = 0) -> str:
    """Groq — free tier, very fast Llama 3.3 70B. Sign up at console.groq.com"""
    import time
    import requests
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload, headers=headers, timeout=60,
        )
        data = resp.json()
        if resp.status_code == 200:
            return data["choices"][0]["message"]["content"]
        err_msg = data.get("error", {}).get("message", resp.text)
        if resp.status_code == 429 and _retry == 0:
            # Auto-retry once after a short back-off
            retry_after = int(resp.headers.get("retry-after", 8))
            time.sleep(min(retry_after, 15))
            return _groq(system_prompt, user_prompt, temperature, max_tokens, _retry=1)
        if resp.status_code == 429:
            return f"⚠️ **Rate limit reached** — Groq free tier allows ~30 requests/min. Please wait a moment and try again.\n\n*Details: {err_msg}*"
        return f"⚠️ **Groq API error ({resp.status_code}):** {err_msg}"
    except requests.exceptions.Timeout:
        return "⚠️ **Request timed out** — Groq took too long to respond. Please try again."
    except Exception as e:
        return f"⚠️ **Connection error:** {e}"


def _groq_stream(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int,
                 _retry: int = 0):
    """Groq streaming generator — yields text deltas via SSE. Auto-retries once on 429."""
    import json
    import time
    import requests
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    try:
        # (connect_timeout, read_timeout) — 12s to connect, 90s to receive each chunk
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload, headers=headers, timeout=(12, 90), stream=True,
        )
        if resp.status_code == 429 and _retry == 0:
            retry_after = int(resp.headers.get("retry-after", 8))
            time.sleep(min(retry_after, 15))
            yield from _groq_stream(system_prompt, user_prompt, temperature, max_tokens, _retry=1)
            return
        if resp.status_code != 200:
            try:
                err_msg = resp.json().get("error", {}).get("message", resp.text)
            except Exception:
                err_msg = resp.text
            if resp.status_code == 429:
                yield "⚠️ **Rate limit reached** — Groq free tier allows ~30 requests/min. Please wait a moment and try again."
            else:
                yield f"⚠️ **Groq API error ({resp.status_code}):** {err_msg}"
            return
        tokens_yielded = 0
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
            if not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    tokens_yielded += 1
                    yield delta
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
        # If nothing was yielded at all, fall back to non-streaming call
        if tokens_yielded == 0:
            fallback = _groq(system_prompt, user_prompt, temperature, max_tokens)
            if fallback:
                yield fallback
    except requests.exceptions.Timeout:
        yield "⚠️ **Request timed out** — Groq is taking too long. Please try again."
    except requests.exceptions.ConnectionError:
        yield "⚠️ **Connection error** — check your internet and try again."
    except Exception as e:
        yield f"⚠️ **Streaming error:** {e}"


def _ollama(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    import requests
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
        data = resp.json()
        if resp.status_code == 200:
            return data["message"]["content"]
        return f"⚠️ **Ollama error ({resp.status_code}):** {data}"
    except requests.exceptions.ConnectionError:
        return f"⚠️ **Ollama not running** — start Ollama with `ollama serve`, then `ollama pull {OLLAMA_MODEL}`."
    except requests.exceptions.Timeout:
        return "⚠️ **Ollama timed out** — the model may still be loading. Try again in a moment."
    except Exception as e:
        return f"⚠️ **Ollama error:** {e}"


# ── Smart RAG — no API key required ────────────────────────────────────────────

def get_vision_response(image_bytes: bytes, mime_type: str, question: str) -> dict:
    """
    Analyse an image with a vision-capable LLM.
    Returns {"description": str, "failure_mode": str, "severity": str,
             "rag_query": str, "backend": str, "error": str|None}
    Priority: Anthropic → OpenAI → graceful fallback (no Groq vision support).
    """
    from app.config import _is_real_key, ANTHROPIC_API_KEY, OPENAI_API_KEY
    import base64

    img_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    VISION_SYSTEM = (
        "You are an expert industrial plant engineer specialising in equipment failure analysis. "
        "When shown an image from a plant, you identify: the equipment type, visible damage or anomaly, "
        "likely failure mode, severity, and suggest 4–6 specific technical keywords for searching "
        "maintenance records and SOPs. Be precise — mention equipment IDs if visible, corrosion types, "
        "crack patterns, seal conditions, measurement readings, colour of fluids, etc."
    )
    VISION_USER = (
        f"Analyse this plant image.\n\n"
        f"Engineer's question: {question or 'What is wrong and what caused it?'}\n\n"
        "Respond in this exact format:\n"
        "**Equipment**: [what is shown]\n"
        "**Visual Finding**: [what you see — be specific]\n"
        "**Likely Failure Mode**: [primary failure mechanism]\n"
        "**Severity**: [Critical / High / Medium / Low]\n"
        "**Probable Cause**: [root cause based on visual evidence]\n"
        "**Search Keywords**: [comma-separated technical terms for RAG search]\n"
        "**Recommended Immediate Action**: [what the engineer should do right now]"
    )

    # ── Anthropic vision ───────────────────────────────────────────────────────
    if _is_real_key(ANTHROPIC_API_KEY):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=VISION_SYSTEM,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": img_b64,
                            },
                        },
                        {"type": "text", "text": VISION_USER},
                    ],
                }],
            )
            raw = msg.content[0].text
            return _parse_vision_response(raw, "anthropic")
        except ImportError:
            pass
        except Exception as e:
            return {"description": raw if 'raw' in dir() else "", "failure_mode": "",
                    "severity": "", "rag_query": question, "backend": "anthropic",
                    "error": f"Anthropic vision error: {e}"}

    # ── OpenAI vision ──────────────────────────────────────────────────────────
    if _is_real_key(OPENAI_API_KEY):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": VISION_SYSTEM},
                    {"role": "user", "content": [
                        {"type": "image_url",
                         "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}},
                        {"type": "text", "text": VISION_USER},
                    ]},
                ],
            )
            raw = resp.choices[0].message.content
            return _parse_vision_response(raw, "openai")
        except ImportError:
            pass
        except Exception as e:
            return {"description": "", "failure_mode": "", "severity": "",
                    "rag_query": question, "backend": "openai",
                    "error": f"OpenAI vision error: {e}"}

    # ── No vision-capable backend available ────────────────────────────────────
    return {
        "description": "", "failure_mode": "", "severity": "",
        "rag_query": question, "backend": "none",
        "error": (
            "Vision analysis requires an **Anthropic** or **OpenAI** API key. "
            "Add `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` to your `.env` file. "
            "You can still describe what you see in the text box and I'll search the knowledge base."
        ),
    }


def _parse_vision_response(raw: str, backend: str) -> dict:
    """Parse the structured vision LLM output into a clean dict."""
    import re

    def _extract(label: str) -> str:
        m = re.search(rf"\*\*{label}\*\*[:\s]*(.+?)(?=\n\*\*|\Z)", raw, re.S | re.I)
        return m.group(1).strip() if m else ""

    equipment     = _extract("Equipment")
    finding       = _extract("Visual Finding")
    failure_mode  = _extract("Likely Failure Mode")
    severity      = _extract("Severity")
    cause         = _extract("Probable Cause")
    keywords_raw  = _extract("Search Keywords")
    action        = _extract("Recommended Immediate Action")

    # Build description for display
    description = raw  # full structured text — displayed as-is in Copilot

    # Build RAG query from keywords + failure mode
    kw_list  = [k.strip() for k in re.split(r"[,;]", keywords_raw) if k.strip()]
    rag_query = " ".join([failure_mode, equipment] + kw_list[:5])[:300]

    return {
        "description":  description,
        "equipment":    equipment,
        "finding":      finding,
        "failure_mode": failure_mode,
        "severity":     severity,
        "cause":        cause,
        "keywords":     kw_list,
        "action":       action,
        "rag_query":    rag_query,
        "backend":      backend,
        "error":        None,
    }


def _smart_rag(system_prompt: str, user_prompt: str) -> str:
    """
    Intelligent context formatter that produces structured, cited answers
    from retrieved document chunks — no LLM or API key required.
    Works 100% offline using the ChromaDB search results embedded in user_prompt.
    """
    # ── Extract question ───────────────────────────────────────────────────────
    question = ""
    for q_marker in ["ENGINEER'S QUESTION:", "QUESTION:"]:
        if q_marker in user_prompt:
            question = user_prompt.split(q_marker)[-1].strip().split("\n")[0].strip()
            break
    if not question and "?" in user_prompt:
        for line in user_prompt.split("\n"):
            if "?" in line:
                question = line.strip()
                break

    # ── Extract document blocks ────────────────────────────────────────────────
    context_raw = ""
    if "DOCUMENT CONTEXT" in user_prompt:
        context_raw = user_prompt.split("DOCUMENT CONTEXT")[1]
        # strip the header label up to the first newline
        context_raw = context_raw.split("\n", 1)[1] if "\n" in context_raw else context_raw
        # cut off at the question marker
        for marker in ["ENGINEER'S QUESTION:", "QUESTION:"]:
            if marker in context_raw:
                context_raw = context_raw.split(marker)[0]
        context_raw = context_raw.strip()
    elif "Documents:\n" in user_prompt:
        context_raw = user_prompt.split("Documents:\n")[1].strip()

    if not context_raw:
        return (
            "No documents found in the knowledge base. "
            "Please upload documents first using the **Upload Documents** page."
        )

    # ── Parse individual document blocks ─────────────────────────────────────
    doc_blocks = re.split(r'\[Document \d+:', context_raw)
    docs = []
    for block in doc_blocks[1:]:
        header_end = block.find(']')
        header = block[:header_end].strip() if header_end > 0 else ""
        text = block[header_end + 1:].strip() if header_end > 0 else block.strip()
        # also handle [filename] style from work orders
        docs.append({"header": header, "text": text})

    # Also try [filename.ext] style blocks (from work order context)
    if not docs:
        alt_blocks = re.split(r'\[([^\]]+\.(?:pdf|xlsx|csv|txt|md))\]', context_raw)
        if len(alt_blocks) > 1:
            for i in range(1, len(alt_blocks), 2):
                filename = alt_blocks[i]
                text = alt_blocks[i + 1].strip() if i + 1 < len(alt_blocks) else ""
                docs.append({"header": filename, "text": text})

    if not docs:
        # Raw text, no structured blocks
        docs = [{"header": "knowledge base", "text": context_raw}]

    # ── Determine question intent ──────────────────────────────────────────────
    q_lower = question.lower()
    intent = "general"
    if any(w in q_lower for w in ["fail", "broke", "incident", "accident", "cause", "why"]):
        intent = "failure"
    elif any(w in q_lower for w in ["procedure", "how", "step", "process", "sop"]):
        intent = "procedure"
    elif any(w in q_lower for w in ["regulation", "oisd", "factory act", "compliance", "standard", "limit", "require"]):
        intent = "regulation"
    elif any(w in q_lower for w in ["maintenance", "history", "record", "repair", "service"]):
        intent = "maintenance"
    elif any(w in q_lower for w in ["predict", "next", "upcoming", "when", "timeline"]):
        intent = "prediction"
    elif any(w in q_lower for w in ["safety", "hazard", "risk", "ppe", "permit", "ptw"]):
        intent = "safety"

    # ── Extract keywords from question ────────────────────────────────────────
    stopwords = {"what", "which", "when", "where", "how", "why", "who", "is", "are",
                 "was", "were", "the", "a", "an", "for", "on", "in", "of", "to",
                 "and", "or", "all", "any", "show", "list", "tell", "me", "about",
                 "do", "does", "did", "has", "have", "had", "been", "be"}
    keywords = [w for w in re.findall(r'\b[a-zA-Z0-9\-]+\b', question.lower())
                if w not in stopwords and len(w) > 2]

    # ── Score sentences by keyword relevance ──────────────────────────────────
    def score_sentence(sentence: str) -> float:
        s = sentence.lower()
        score = sum(1.0 for kw in keywords if kw in s)
        # boost for numbers, dates, equipment IDs, regulatory refs
        if re.search(r'\b\d{4}\b', s):  # year
            score += 0.5
        if re.search(r'\b[A-Z]-\d+\b', sentence):  # equipment ID like P-101
            score += 0.8
        if re.search(r'\b(OISD|IS:|IS\s\d|Factory Act|DGMS|PESO)\b', sentence):
            score += 0.8
        if re.search(r'\b\d+[\.,]\d+\s*(mm|bar|psi|rpm|kW|°C|Hz|V|A)\b', s):  # measurements
            score += 0.6
        return score

    # ── Gather best sentences from all docs ──────────────────────────────────
    all_findings = []
    source_names = []

    for doc in docs[:6]:
        raw_header = doc["header"]
        filename = raw_header.split(",")[0].strip() if "," in raw_header else raw_header.strip()
        if filename and filename not in source_names:
            source_names.append(filename)

        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', doc["text"]) if len(s.strip()) > 25]
        scored = sorted([(score_sentence(s), s) for s in sentences], reverse=True)
        top = [s for _, s in scored[:4] if _ > 0] or [s for _, s in scored[:2]]
        if not top and sentences:
            top = sentences[:2]
        for sent in top:
            sent = re.sub(r'\b([A-Z]-\d+[A-Z]?)\b', r'**\1**', sent)
            sent = re.sub(r'\b(\d{2,4}[\.,]\d+\s*(?:mm|bar|psi|rpm|kW|°C|Hz))\b', r'**\1**', sent)
            all_findings.append((score_sentence(sent), sent, filename))

    # sort globally by relevance
    all_findings.sort(reverse=True)

    # ── Build a natural-reading answer ────────────────────────────────────────
    intro_map = {
        "failure":     f"Based on the plant records, here's what I found about this failure:",
        "procedure":   f"Here are the relevant procedure steps from the knowledge base:",
        "regulation":  f"The applicable regulatory requirements are:",
        "maintenance": f"Here's what the maintenance records show:",
        "prediction":  f"Based on historical data, here's the failure prediction picture:",
        "safety":      f"The key safety requirements and precautions are:",
        "general":     f"Here's what the knowledge base has on this:",
    }

    parts = [intro_map.get(intent, "Here's what I found:"), ""]

    seen = set()
    for _, sent, fname in all_findings[:8]:
        if sent not in seen:
            seen.add(sent)
            parts.append(f"- {sent} *(from {fname})*")

    if not seen:
        parts.append("The knowledge base doesn't have a direct match for this query. "
                     "Try uploading more relevant documents, or rephrase your question.")

    # Regulatory limits callout
    if intent == "regulation":
        limits = []
        for doc in docs:
            found = re.findall(r'(?:limit|maximum|minimum|shall not exceed|≤|≥)\s*:?\s*[\d.,]+\s*\w+',
                               doc["text"], re.I)
            limits.extend(found[:3])
        if limits:
            parts += ["", "**Key limits/thresholds:**"]
            for lim in list(dict.fromkeys(limits))[:4]:
                parts.append(f"- {lim}")

    if source_names:
        parts += ["", f"*Sources: {' · '.join(source_names)}*"]

    parts += ["", "---",
              "*Note: This is a keyword-extracted summary. Add a Groq API key in your .env file for full AI-generated answers.*"]

    return "\n".join(parts)
