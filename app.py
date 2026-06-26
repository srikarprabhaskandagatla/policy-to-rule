"""
PolicyToRule - AI-assisted conversion of written healthcare policy into
executable rules, applied to sample claims.

By default this runs FULLY SELF-CONTAINED (deterministic mock extractor) so the
demo never depends on a network during a recording. To use a real LLM instead,
set an API key in the environment (see extractor.py) and toggle "Use live LLM".
"""

import json
import streamlit as st

from extractor import extract_rule, MOCK_AVAILABLE, LLM_AVAILABLE
from rule_engine import adjudicate
from samples import SAMPLE_POLICIES, SAMPLE_CLAIMS

st.set_page_config(page_title="PolicyToRule", layout="wide")

st.title("PolicyToRule")
st.caption(
    "Convert written healthcare billing/coding policy into a structured, "
    "executable rule - then run it against claims. "
)

with st.sidebar:
    st.header("Controls")
    use_llm = st.toggle(
        "Use live LLM",
        value=False,
        help="Off = deterministic mock extractor (offline-safe for video). "
             "On = call a real LLM API (needs an API key set in environment).",
    )
    if use_llm and not LLM_AVAILABLE:
        st.warning("No API key found. Falling back to mock extractor.")
        use_llm = False
    st.markdown("---")
    st.subheader("Pipeline")
    st.markdown(
        "1. Written policy (text)\n"
        "2. LLM to structured JSON rule\n"
        "3. Rule engine runs vs. claims\n"
        "4. Adjudication results"
    )


st.header("1 - Written Policy")
policy_choice = st.selectbox(
    "Pick a sample policy (or choose 'Custom' to paste your own):",
    list(SAMPLE_POLICIES.keys()) + ["Custom"],
)

if policy_choice == "Custom":
    policy_text = st.text_area("Paste policy text", height=180)
else:
    policy_text = st.text_area(
        "Policy text", value=SAMPLE_POLICIES[policy_choice], height=180
    )


st.header("2 - Structured Rule (machine-readable)")
if "rule" not in st.session_state:
    st.session_state.rule = None

if st.button("Convert policy To rule", type="primary"):
    if not policy_text.strip():
        st.error("Enter or select a policy first.")
    else:
        with st.spinner("Extracting structured rule..."):
            st.session_state.rule = extract_rule(policy_text, use_llm=use_llm)

if st.session_state.rule:
    rule = st.session_state.rule
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Human-readable summary**")
        st.markdown(
            f"- **Rule name:** {rule.get('rule_name','-')}\n"
            f"- **Applies to codes:** {', '.join(rule.get('codes', [])) or '-'}\n"
            f"- **Limit:** {rule.get('max_occurrences','-')} "
            f"per {rule.get('period_months','-')} months\n"
            f"- **Patient gender required:** {rule.get('gender','any')}\n"
            f"- **Min age:** {rule.get('min_age','-')} | "
            f"**Max age:** {rule.get('max_age','-')}"
        )
    with col2:
        st.markdown("**Executable JSON**")
        st.code(json.dumps(rule, indent=2), language="json")


st.header("3 - Sample Claims")
st.caption("Edit the JSON below to test different claim scenarios.")
claims_text = st.text_area(
    "Claims (JSON list)",
    value=json.dumps(SAMPLE_CLAIMS, indent=2),
    height=240,
)


st.header("4 - Adjudication Results")
if st.button("Run rule against claims"):
    if not st.session_state.rule:
        st.error("Convert a policy to a rule first (Step 2).")
    else:
        try:
            claims = json.loads(claims_text)
        except json.JSONDecodeError as e:
            st.error(f"Claims JSON is invalid: {e}")
            claims = None

        if claims:
            results = adjudicate(st.session_state.rule, claims)
            applicable = [r for r in results if r["decision"] != "NOT_APPLICABLE"]
            skipped = len(results) - len(applicable)

            n_deny = sum(1 for r in applicable if r["decision"] == "DENY")
            n_pay = sum(1 for r in applicable if r["decision"] == "PAY")

            col1, col2, col3 = st.columns(3)
            col1.metric("Evaluated", len(applicable))
            col2.metric("Approved (PAY)", n_pay)
            col3.metric("Denied", n_deny)

            if skipped:
                st.caption(f"{skipped} claim(s) skipped — code not covered by this rule.")

            if applicable:
                st.dataframe(
                    [
                        {
                            "claim_id": r["claim_id"],
                            "patient": r["patient_id"],
                            "code": r["code"],
                            "decision": r["decision"],
                            "reason": r["reason"],
                        }
                        for r in applicable
                    ],
                    use_container_width=True,
                )
            else:
                st.info("No claims match the codes in this rule.")
