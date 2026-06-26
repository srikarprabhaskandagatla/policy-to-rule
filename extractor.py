"""
Turn free-text policy into a structured rule dict.

Two modes:
  - mock (default): deterministic keyword/regex extraction. No network. Safe for
    a recorded demo. Demonstrates the *concept* of policy to a structured rule.
  - live LLM: sends the policy to a real model and asks for JSON. Enabled only
    when an API key is present AND the user toggles it on.
"""

import os
import re
import json

MOCK_AVAILABLE = True

LLM_AVAILABLE = bool(
    os.environ.get("ANTHROPIC_API_KEY")
    or os.environ.get("OPENAI_API_KEY")
    or os.environ.get("GROQ_API_KEY")
    or os.environ.get("GEMINI_API_KEY")
)


# Mock Extractor
_CODE_RE = re.compile(r"\b([A-Z]?\d{4,5})\b")
_MONTHS_RE = re.compile(r"every\s+(\d+)\s+months", re.I)
_YEARS_RE = re.compile(r"every\s+(\d+)\s+years?", re.I)
_ONCE_RE = re.compile(r"\bonce\b", re.I)
_AGE_MIN_RE = re.compile(r"(?:age|aged|ages?)\s+(\d+)\s*(?:or older|and older|\+)", re.I)
_AGE_BETWEEN_RE = re.compile(r"ages?\s+(\d+)\s*(?:to|-|through)\s*(\d+)", re.I)


def _mock_extract(text: str) -> dict:
    rule = {
        "rule_name": "extracted_policy_rule",
        "codes": sorted(set(_CODE_RE.findall(text))),
        "max_occurrences": 1 if _ONCE_RE.search(text) else None,
        "period_months": None,
        "gender": "any",
        "min_age": None,
        "max_age": None,
        "source_excerpt": text.strip()[:240],
    }

    m = _MONTHS_RE.search(text)
    if m:
        rule["period_months"] = int(m.group(1))
    y = _YEARS_RE.search(text)
    if y:
        rule["period_months"] = int(y.group(1)) * 12

    # Default occurrence to 1 if a period was found but count wasn't stated
    if rule["period_months"] and rule["max_occurrences"] is None:
        rule["max_occurrences"] = 1

    if re.search(r"\bfemale\b", text, re.I):
        rule["gender"] = "F"
    elif re.search(r"\bmale\b", text, re.I):
        rule["gender"] = "M"

    ab = _AGE_BETWEEN_RE.search(text)
    if ab:
        rule["min_age"], rule["max_age"] = int(ab.group(1)), int(ab.group(2))
    else:
        amin = _AGE_MIN_RE.search(text)
        if amin:
            rule["min_age"] = int(amin.group(1))

    # Name the rule from first few words
    first_words = re.sub(r"[^a-zA-Z ]", "", text).split()[:4]
    if first_words:
        rule["rule_name"] = "_".join(w.lower() for w in first_words)

    return rule


# Live LLM Extractor (Optional)
_SYSTEM = (
    "You convert a written US healthcare billing/coding policy into a single "
    "JSON rule object. Respond with ONLY valid JSON, no prose, no markdown. "
    "Schema: {rule_name:str, codes:[str], max_occurrences:int|null, "
    "period_months:int|null, gender:'M'|'F'|'any', min_age:int|null, "
    "max_age:int|null, source_excerpt:str}. Convert years to months."
)


def _call_llm(text: str) -> dict:
    from litellm import completion
    model = os.environ.get("LLM_MODEL", "groq/llama-3.1-8b-instant")
    resp = completion(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": text},
        ],
    )
    raw = resp.choices[0].message.content
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


# Public Entry Point for LLM or Mock Extraction
def extract_rule(text: str, use_llm: bool = False) -> dict:
    if use_llm and LLM_AVAILABLE:
        try:
            return _call_llm(text)
        except Exception as e:  
            fallback = _mock_extract(text)
            fallback["_llm_error"] = str(e)
            return fallback
    return _mock_extract(text)
