<h1 align="center">
  <br>
  PolicyToRule
  <br>
</h1>

<h4 align="center">Convert written healthcare billing policy into executable rules - then run them against claims for instant adjudication.</h4>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
  </a>
  <a href="https://litellm.ai/">
    <img src="https://img.shields.io/badge/-LiteLLM-6C47FF?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6TTIgMTdsOSA1IDktNXYtNWwtOSA1LTktNXoiLz48L3N2Zz4=&logoColor=white" alt="LiteLLM">
  </a>
  <a href="https://groq.com/">
    <img src="https://img.shields.io/badge/-Groq-F55036?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIi8+PC9zdmc+&logoColor=white" alt="Groq">
  </a>
  <a href="https://ai.google.dev/">
    <img src="https://img.shields.io/badge/-Gemini-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini">
  </a>
</p>

<p align="center">
  <a href="#why-this-matters-in-practice">Why It Matters</a>
  •
  <a href="#pipeline">Pipeline</a>
  •
  <a href="#run">Run</a>
  •
  <a href="#files">Files</a>
  •
  <a href="#scope--honesty">Scope</a>
</p>

---
PolicyToRule converts a written US healthcare billing/coding policy into a structured, machine-executable rule (JSON), then runs that rule against sample claims to produce pay/deny adjudication decisions - a miniature of what a payment-integrity edit does.

## Why this matters in practice

In healthcare billing and payment integrity, the ability to translate written coverage policy into executable logic is foundational. Payers, clearinghouses, and audit firms all depend on this loop to catch overpayments, enforce clinical guidelines, and ensure consistent adjudication at scale. This POC demonstrates that core loop end to end:

```
Written policy (English) to Structured rule (JSON) to Claims adjudication
```

## Pipeline

1. **Policy input** - paste or select a written policy.
2. **Extraction** - an extractor converts the text into a structured rule
   (`codes`, `max_occurrences`, `period_months`, `gender`, `min_age`, `max_age`).
   - *Mock mode (default):* deterministic regex/keyword extraction. No network - safe for a recorded demo.
   - *Live LLM mode (optional):* sends the policy to a real model and asks for JSON. Enabled only when an API key is set.
3. **Rule engine** - applies the rule to claims: frequency limits within a rolling time window, plus age and gender eligibility.
4. **Adjudication** - per-claim PAY / DENY with a human-readable reason.

## Run

```bash
pip install -r requirements.txt
```

### Optional: live LLM mode

Copy `.env.example` to `.env`, uncomment your provider, and fill in your key:

```bash
cp .env.example .env
# edit .env - pick Groq, Gemini, Anthropic, or OpenAI
```

Then load the env and run:

```bash
export $(cat .env | grep -v '#' | xargs)
streamlit run app.py
```

Toggle **"Use live LLM"** in the sidebar. If the call fails, the app falls back to the mock extractor so the demo never crashes.

## Files

| File             | Purpose                                            |
|------------------|----------------------------------------------------|
| `app.py`         | Streamlit UI (4-step pipeline)                     |
| `extractor.py`   | Policy to structured rule (mock + optional LLM)    |
| `rule_engine.py` | Applies a rule to claims; produces decisions       |
| `samples.py`     | Sample policies and claims                         |
| `.env.example`   | Template for API keys (Groq, Gemini, Anthropic, OpenAI) |

## Scope & honesty

The extractor and rule set are intentionally simple to "hack to prove a concept." Sample policies are paraphrased, simplified versions of common coverage rules - illustrative, not official payer policy. Production use would require validated policy sources, a richer rule schema, and clinical review.
