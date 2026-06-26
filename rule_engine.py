"""
Apply a structured rule (from extractor) to claims.

A claim is a dict:
  {claim_id, patient_id, code, date (YYYY-MM-DD), age, gender}
"""

from datetime import date
from collections import defaultdict


def _parse_date(s: str) -> date:
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


def _months_between(d1: date, d2: date) -> float:
    return abs((d2.year - d1.year) * 12 + (d2.month - d1.month) + (d2.day - d1.day) / 30.0)


def adjudicate(rule: dict, claims: list) -> list:
    codes = set(rule.get("codes") or [])
    max_occ = rule.get("max_occurrences")
    period = rule.get("period_months")
    gender_req = rule.get("gender", "any")
    min_age = rule.get("min_age")
    max_age = rule.get("max_age")

    # Group matching claims by patient + code, sorted by date
    grouped = defaultdict(list)
    for c in claims:
        if not codes or c.get("code") in codes:
            grouped[(c.get("patient_id"), c.get("code"))].append(c)

    results = []
    for c in claims:
        code = c.get("code")
        reason = "Allowed"
        decision = "PAY"

        # Skip claims the rule doesn't cover
        if codes and code not in codes:
            results.append(_row(c, "NOT_APPLICABLE", "Code not covered by this rule"))
            continue

        # eligibility: gender
        if gender_req in ("M", "F") and c.get("gender") != gender_req:
            results.append(_row(c, "DENY", f"Patient gender must be {gender_req}"))
            continue

        # eligibility: age
        age = c.get("age")
        if min_age is not None and age is not None and age < min_age:
            results.append(_row(c, "DENY", f"Patient under min age {min_age}"))
            continue
        if max_age is not None and age is not None and age > max_age:
            results.append(_row(c, "DENY", f"Patient over max age {max_age}"))
            continue

        # frequency limit
        if max_occ is not None:
            same = sorted(
                grouped[(c.get("patient_id"), code)], key=lambda x: _parse_date(x["date"])
            )
            this_date = _parse_date(c["date"])
            if period:
                window = [
                    s for s in same
                    if _months_between(_parse_date(s["date"]), this_date) <= period
                    and _parse_date(s["date"]) <= this_date
                ]
            else:
                window = [s for s in same if _parse_date(s["date"]) <= this_date]
            if len(window) > max_occ:
                period_txt = f" within {period} months" if period else ""
                results.append(
                    _row(c, "DENY",
                         f"Exceeds {max_occ} allowed{period_txt} "
                         f"(occurrence #{len(window)})")
                )
                continue

        results.append(_row(c, decision, reason))

    return results


def _row(c: dict, decision: str, reason: str) -> dict:
    return {
        "claim_id": c.get("claim_id"),
        "patient_id": c.get("patient_id"),
        "code": c.get("code"),
        "decision": decision,
        "reason": reason,
    }
