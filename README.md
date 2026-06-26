# PolicyToRule

Topic: *Content Management in Health Care - Conversion of Written Policy into Programming Languages, Rules, or Models.*

PolicyToRule converts a written US healthcare billing/coding policy into a
structured, machine-executable rule (JSON), then runs that rule against sample
claims to produce pay/deny adjudication decisions - a miniature of what a
payment-integrity edit does.

## Why this matters in practice

In healthcare billing and payment integrity, the ability to translate written
coverage policy into executable logic is foundational. Payers, clearinghouses,
and audit firms all depend on this loop to catch overpayments, enforce clinical
guidelines, and ensure consistent adjudication at scale. This POC demonstrates
that core loop end to end:

```
Written policy (English) to Structured rule (JSON) to Claims adjudication
```

## Pipeline

1. **Policy input** - paste or select a written policy.
2. **Extraction** - an extractor converts the text into a structured rule
   (`codes`, `max_occurrences`, `period_months`, `gender`, `min_age`, `max_age`).
   - *Mock mode (default):* deterministic regex/keyword extraction. No network -
     safe for a recorded demo.
   - *Live LLM mode (optional):* sends the policy to a real model and asks for
     JSON. Enabled only when an API key is set.
3. **Rule engine** - applies the rule to claims: frequency limits within a
   rolling time window, plus age and gender eligibility.
4. **Adjudication** - per-claim PAY / DENY with a human-readable reason.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Optional: live LLM mode

Set one of:

```bash
export ANTHROPIC_API_KEY=...   
# or
export OPENAI_API_KEY=...     
```

Then toggle **"Use live LLM"** in the sidebar. If the call fails, the app falls
back to the mock extractor so the demo never crashes.

## Files

| File             | Purpose                                            |
|------------------|----------------------------------------------------|
| `app.py`         | Streamlit UI (4-step pipeline)                     |
| `extractor.py`   | Policy to structured rule (mock + optional LLM)    |
| `rule_engine.py` | Applies a rule to claims; produces decisions       |
| `samples.py`     | Sample policies and claims                         |

## Scope & honesty

The extractor and rule set are intentionally simple to "hack to prove a
concept." Sample policies are paraphrased, simplified versions of common
coverage rules - illustrative, not official payer policy. Production use would
require validated policy sources, a richer rule schema, and clinical review.
