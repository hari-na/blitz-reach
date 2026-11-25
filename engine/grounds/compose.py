"""The only part of the pipeline a language model touches.

By the time this runs, every decision has been made: whether there is a problem,
how big it is, how confident we are, and whether to say anything at all. The
model writes the opening paragraph and a subject line. That is all it does.

It is also not trusted to do that. `check_no_new_numbers` re-reads the output and
rejects it if it contains a number that was not in the input, because an invented
figure in a brief about a named company is the one failure this whole design
exists to prevent.

Three origins, one verification path. A live call, a recorded take replayed from
disk, and a deterministic opening written from the finding itself all go through
the same check. That means the project runs, and the guardrail can be watched
firing, with no API key and no network.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from grounds.fmt import inr, pct
from grounds.verdict import Assessment

MODEL = "claude-opus-5-5"
REPLAY_DIR = Path(__file__).resolve().parents[1] / "data" / "replay"

Origin = Literal["live", "replay", "deterministic"]

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
    origin: Origin
    note: str = ""

    def render(self) -> str:
        parts = ["**Subject:** {s}".format(s=self.subject), "", self.opening]
        if self.note:
            parts += ["", "> {n}".format(n=self.note)]
        return "\n".join(parts)


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


def facts_for(assessment: Assessment) -> str:
    """Exactly what the model is allowed to know. Also the whitelist it is checked against."""
    a = assessment
    if a.lead is None:
        raise ValueError("there is no lead finding to write about")

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


def deterministic(assessment: Assessment, note: str = "") -> Prose:
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
        origin="deterministic",
        note=note,
    )


def _accept(text: str, facts: str, assessment: Assessment, origin: Origin) -> Prose:
    """Parse and verify one draft, whatever produced it."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return deterministic(
            assessment, "Draft discarded: not JSON. Using the deterministic opening."
        )

    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        return deterministic(
            assessment,
            "Draft discarded: JSON did not parse ({e}). Using the deterministic "
            "opening.".format(e=exc),
        )

    subject = str(payload.get("subject", "")).strip()
    opening = str(payload.get("opening", "")).strip()

    if not subject or not opening:
        return deterministic(
            assessment,
            "Draft discarded: subject or opening missing. Using the deterministic opening.",
        )

    problem = check_no_new_numbers(subject + " " + opening, facts)
    if problem:
        return deterministic(
            assessment,
            "Draft discarded by the number guard: {p}. Using the deterministic "
            "opening instead.".format(p=problem),
        )

    return Prose(subject=subject, opening=opening, origin=origin)


def available_takes(assessment: Assessment) -> list[str]:
    path = _replay_path(assessment)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [str(t.get("label", "")) for t in data.get("takes", [])]


def _replay_path(assessment: Assessment) -> Path:
    slug = assessment.slug or re.sub(
        r"[^a-z0-9]+", "-", assessment.company.lower()
    ).strip("-")
    return REPLAY_DIR / "{slug}.json".format(slug=slug)


def from_replay(assessment: Assessment, take: str = "accepted") -> Prose:
    """Replay a stored draft through the live verification path."""
    path = _replay_path(assessment)
    if not path.exists():
        return deterministic(
            assessment,
            "No recorded take for this company. Using the deterministic opening.",
        )

    data = json.loads(path.read_text(encoding="utf-8"))
    takes = {str(t.get("label")): t for t in data.get("takes", [])}
    if take not in takes:
        return deterministic(
            assessment,
            "No take named {t!r}. Available: {a}.".format(
                t=take, a=", ".join(sorted(takes)) or "none"
            ),
        )

    entry = takes[take]
    facts = facts_for(assessment)
    result = _accept(str(entry.get("text", "")), facts, assessment, "replay")

    provenance = "Replayed take {t!r}. {src}".format(
        t=take, src=str(data.get("source", "")).strip()
    )
    return Prose(
        subject=result.subject,
        opening=result.opening,
        origin=result.origin,
        note=(result.note + " " + provenance).strip(),
    )


def from_live(assessment: Assessment) -> Prose:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return deterministic(
            assessment, "No ANTHROPIC_API_KEY set. Using the deterministic opening."
        )
    try:
        import anthropic
    except ImportError:
        return deterministic(
            assessment, "anthropic package not installed. Using the deterministic opening."
        )

    facts = facts_for(assessment)
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
    return _accept(text, facts, assessment, "live")


def compose(
    assessment: Assessment,
    mode: str = "auto",
    take: str = "accepted",
) -> Prose:
    """mode: auto (live if a key is set, else replay), live, replay, off."""
    if assessment.lead is None:
        raise ValueError("nothing to compose: this assessment has no lead finding")

    if mode == "off":
        return deterministic(assessment)
    if mode == "replay":
        return from_replay(assessment, take=take)
    if mode == "live":
        return from_live(assessment)

    if os.environ.get("ANTHROPIC_API_KEY"):
        return from_live(assessment)
    return from_replay(assessment, take=take)


def compose_opening(
    assessment: Assessment, mode: str = "auto", take: str = "accepted"
) -> str:
    if assessment.lead is None:
        return ""
    return compose(assessment, mode=mode, take=take).render()
