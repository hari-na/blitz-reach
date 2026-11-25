"""The only part of the pipeline a language model touches.

By the time this runs, every decision has been made: whether there is a problem,
how big it is, how confident we are, and whether to say anything at all. The
model writes the opening paragraph and a subject line. That is all it does.

It is also not trusted to do that. `check_no_new_numbers` re-reads the model's
output and rejects it if it contains a number that was not in the input, because
an invented figure in a brief about a named company is the one failure this
whole design exists to prevent. On rejection the deterministic opening is used
instead and the brief says the model's draft was discarded.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from grounds.fmt import inr, pct
from grounds.verdict import Assessment

MODEL = "claude-opus-5-5"

SYSTEM = """You write the opening of a briefing note for a field engineer who is \
about to approach a company's finance leadership for the first time.

Hard rules:

1. Use only the facts given to you. You may not add context, benchmarks, \
industry commentary or anything you happen to know about the company or sector.
2. You may not write any number that is not already in the input. No rounding to \
a different figure, no deriving a new one, no "roughly", no percentages of your own.
3. Write as one professional to another. No greeting, no sign-off, no flattery, no \
sales language, no promise about what any product can do.
4. Do not claim the company is doing anything wrong. The filings say what they say. \
The point of the note is that a number is sitting in public and nobody inside has \
been asked about it.
5. American English. No em dashes or en dashes; use a hyphen or rephrase.

Return JSON only, with exactly these keys:
  "subject"  a subject line under 70 characters, specific to this company
  "opening"  two or three sentences, under 90 words total
"""

FALLBACK_TEMPLATE = (
    "{company} has filed a figure that sizes a problem in its own accounts payable: "
    "{lead_title_lower}, worth {amount} a year, {share} of revenue. The number is in "
    "{source}. The question worth putting to them is simple: {question}"
)


@dataclass(frozen=True)
class Prose:
    subject: str
    opening: str
    model_used: bool
    rejected_reason: str = ""

    def render(self) -> str:
        head = "**Subject:** {s}".format(s=self.subject)
        body = self.opening
        if not self.model_used and self.rejected_reason:
            body += "\n\n> Model draft discarded: {r}".format(r=self.rejected_reason)
        return head + "\n\n" + body


NUMBER_RE = re.compile(r"\d[\d,.]*")


def _numeric_tokens(text: str) -> set[str]:
    """Numbers in a string, normalized so 47.50 and 47,50 compare as digits."""
    found: set[str] = set()
    for match in NUMBER_RE.findall(text):
        cleaned = match.replace(",", "").rstrip(".")
        if cleaned:
            found.add(cleaned)
    return found


def check_no_new_numbers(output: str, allowed_source_text: str) -> str:
    """Return an empty string if clean, otherwise why the draft is rejected."""
    allowed = _numeric_tokens(allowed_source_text)
    # A bare year or a small integer is not a claim about the company's money.
    invented = {
        tok
        for tok in _numeric_tokens(output)
        if tok not in allowed and not (len(tok) <= 2 and "." not in tok)
    }
    if invented:
        return "introduced numbers not present in the evidence: {nums}".format(
            nums=", ".join(sorted(invented))
        )
    return ""


def _facts(assessment: Assessment) -> str:
    a = assessment
    if a.lead is None:
        raise ValueError("compose_opening is only for an actionable assessment")

    lines = [
        "Company: {c}".format(c=a.company),
        "Fiscal year: {fy}".format(fy=a.fiscal_year),
        "Revenue: {r}".format(r=inr(a.revenue)),
        "",
        "Lead finding: {t}".format(t=a.lead.title),
        "Amount at stake per year: {amt}".format(amt=inr(a.lead.magnitude)),
        "Share of revenue: {sh}".format(sh=pct(a.share(a.lead))),
        "Confidence: {c}".format(c=a.lead.confidence),
        "",
        "Mechanism (do not contradict this):",
        a.lead.mechanism,
        "",
        "Arithmetic shown in the brief:",
        "  {f}".format(f=a.lead.derivation.formula),
        "  {s}".format(s=a.lead.derivation.substituted),
        "  = {r}".format(r=inr(a.lead.derivation.result)),
        "",
        "Source documents:",
    ]
    for cite in a.lead.sources():
        lines.append("  - {c}".format(c=cite))
    lines += [
        "",
        "The question the brief tells the engineer to ask:",
        a.lead.confirming_question,
    ]
    if a.supporting:
        lines += ["", "Other findings, lower priority:"]
        for f in a.supporting:
            lines.append(
                "  - {t}: {amt} a year, {sh} of revenue, {c} confidence".format(
                    t=f.title, amt=inr(f.magnitude), sh=pct(a.share(f)), c=f.confidence
                )
            )
    return "\n".join(lines)


def _fallback(assessment: Assessment) -> Prose:
    a = assessment
    assert a.lead is not None
    sources = a.lead.sources()
    return Prose(
        subject="{c}: {t}".format(c=a.company, t=a.lead.title),
        opening=FALLBACK_TEMPLATE.format(
            company=a.company,
            lead_title_lower=a.lead.title[0].lower() + a.lead.title[1:],
            amount=inr(a.lead.magnitude),
            share=pct(a.share(a.lead)),
            source=sources[0] if sources else "the filings cited below",
            question=a.lead.confirming_question,
        ),
        model_used=False,
    )


def compose(assessment: Assessment) -> Prose:
    """Ask the model for an opening, verify it, fall back if it invents anything."""
    if assessment.lead is None:
        raise ValueError("nothing to compose: this assessment has no lead finding")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        return Prose(
            **{
                **_fallback(assessment).__dict__,
                "rejected_reason": "no ANTHROPIC_API_KEY set, used the deterministic opening",
            }
        )

    facts = _facts(assessment)

    try:
        import anthropic
    except ImportError:
        return Prose(
            **{
                **_fallback(assessment).__dict__,
                "rejected_reason": "anthropic package not installed",
            }
        )

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM,
        messages=[{"role": "user", "content": facts}],
    )

    text = "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    ).strip()

    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return Prose(
            **{
                **_fallback(assessment).__dict__,
                "rejected_reason": "model did not return JSON",
            }
        )

    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        return Prose(
            **{
                **_fallback(assessment).__dict__,
                "rejected_reason": "model JSON did not parse: {e}".format(e=exc),
            }
        )

    subject = str(payload.get("subject", "")).strip()
    opening = str(payload.get("opening", "")).strip()

    if not subject or not opening:
        return Prose(
            **{
                **_fallback(assessment).__dict__,
                "rejected_reason": "model omitted subject or opening",
            }
        )

    problem = check_no_new_numbers(subject + " " + opening, facts)
    if problem:
        return Prose(
            **{**_fallback(assessment).__dict__, "rejected_reason": problem}
        )

    return Prose(subject=subject, opening=opening, model_used=True)


def compose_opening(assessment: Assessment) -> str:
    if assessment.lead is None:
        return ""
    return compose(assessment).render()
