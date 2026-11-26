"""Ranking, and the decision to say nothing.

Abstaining is the product. Every tool in this category produces a confident
paragraph about whatever company you type in, which is why none of them get
answered. This one is built to read a thousand companies and refuse most of
them, so that the ones it does not refuse are worth an hour of someone's time.

Three verdicts:

  actionable  one finding clears the lead floor on evidence better than weak
  thin        something fired, but nothing worth opening a conversation with
  abstain     nothing survived, or the filings were too thin to size anything
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from grounds.fmt import inr, pct
from grounds.hypotheses import CONFIDENCE_ORDER, REGISTRY, Finding, Skipped, run_one
from grounds.materiality import (
    LEAD_FLOOR,
    QUICKLIME_FLOOR,
    can_lead,
    share_of_revenue,
)
from grounds.provenance import SignalSet
from grounds.contexts import Context, run_contexts
from grounds.qualifiers import Veto, run_qualifiers

Verdict = Literal["actionable", "thin", "abstain"]


@dataclass(frozen=True)
class Discarded:
    finding: Finding
    share: float


@dataclass(frozen=True)
class Assessment:
    company: str
    fiscal_year: str
    capture: str
    verdict: Verdict
    reason: str
    revenue: float
    lead: Finding | None
    supporting: tuple[Finding, ...]
    discarded: tuple[Discarded, ...]
    skipped: tuple[Skipped, ...]
    signal_count: int
    slug: str = ""
    signals_present: tuple[str, ...] = ()
    # Hypotheses that ran on complete data and found nothing. Distinct from
    # `skipped`, which never ran. An abstain backed by these means the filings
    # were read and are clean; an abstain backed only by `skipped` means nobody
    # finished the capture. Conflating the two would be the worst bug in here.
    cleared: tuple[tuple[str, str], ...] = ()
    # Reasons not to approach this company whatever was found. A qualifier
    # never creates a finding; it only stops one being acted on.
    vetoes: tuple[Veto, ...] = ()
    # Filed facts with no money figure. They never move a verdict; they say
    # what shape the company is, and when a silence is uninformative.
    contexts: tuple[Context, ...] = ()

    @property
    def material(self) -> tuple[Finding, ...]:
        head = (self.lead,) if self.lead else ()
        return head + self.supporting

    def share(self, finding: Finding) -> float:
        return share_of_revenue(finding.magnitude, self.revenue)


def _rank_key(finding: Finding) -> tuple[int, float]:
    return (CONFIDENCE_ORDER[finding.confidence], finding.magnitude)


def assess(
    signals: SignalSet,
    company: str,
    fiscal_year: str,
    capture: str = "unknown",
    slug: str = "",
) -> Assessment:
    revenue_sig = signals.get("revenue")

    def empty(verdict: Verdict, reason: str, revenue: float = 0.0) -> Assessment:
        return Assessment(
            company=company,
            fiscal_year=fiscal_year,
            capture=capture,
            verdict=verdict,
            reason=reason,
            revenue=revenue,
            lead=None,
            supporting=(),
            discarded=(),
            skipped=(),
            signal_count=len(signals),
            slug=slug,
            signals_present=tuple(signals.keys()),
        )

    # Without revenue nothing can be sized, and an unsized finding cannot be
    # tested against the materiality floor. That is an abstain, not a guess.
    if revenue_sig is None or revenue_sig.num <= 0:
        return empty(
            "abstain",
            "No revenue figure was captured, so no finding can be tested against the "
            "materiality floor. Sizing a problem without a denominator is the error this "
            "engine exists to avoid.",
        )

    revenue = revenue_sig.num
    vetoes = run_qualifiers(signals)
    contexts = run_contexts(signals)

    findings: list[Finding] = []
    skipped: list[Skipped] = []
    cleared: list[tuple[str, str]] = []

    for hyp in REGISTRY:
        result = run_one(hyp, signals)
        if isinstance(result, Skipped):
            skipped.append(result)
        elif result is not None:
            findings.append(result)
        else:
            cleared.append((hyp.id, hyp.title))

    material: list[Finding] = []
    discarded: list[Discarded] = []

    for finding in findings:
        share = share_of_revenue(finding.magnitude, revenue)
        if share >= QUICKLIME_FLOOR:
            material.append(finding)
        else:
            discarded.append(Discarded(finding=finding, share=share))

    material.sort(key=_rank_key, reverse=True)
    discarded.sort(key=lambda d: d.share, reverse=True)

    cleared_clause = (
        " {n} ran on complete filings and found nothing.".format(n=len(cleared))
        if cleared
        else ""
    )

    if not material:
        if discarded:
            reason = (
                "{n} {word} fired and every one came in below the {floor} materiality "
                "floor. The largest was {title} at {amount} a year, {share} of revenue."
                "{cleared} Nothing here is worth an outbound conversation."
            ).format(
                n=len(discarded),
                word="hypothesis" if len(discarded) == 1 else "hypotheses",
                floor=pct(QUICKLIME_FLOOR, 1),
                title=discarded[0].finding.title.lower(),
                amount=inr(discarded[0].finding.magnitude),
                share=pct(discarded[0].share),
                cleared=cleared_clause,
            )
        elif cleared:
            reason = (
                "No hypothesis fired.{cleared} {n} of {total} could not be tested for "
                "want of the filings they need."
            ).format(cleared=cleared_clause, n=len(skipped), total=len(REGISTRY))
        else:
            reason = (
                "No hypothesis fired, and {n} of {total} could not be tested at all for "
                "want of the filings they need. This is an unfinished capture, not a "
                "clean company."
            ).format(n=len(skipped), total=len(REGISTRY))
        return Assessment(
            company=company,
            fiscal_year=fiscal_year,
            capture=capture,
            verdict="abstain",
            reason=reason,
            revenue=revenue,
            lead=None,
            supporting=(),
            discarded=tuple(discarded),
            skipped=tuple(skipped),
            signal_count=len(signals),
            slug=slug,
            signals_present=tuple(signals.keys()),
            cleared=tuple(cleared),
            vetoes=vetoes,
            contexts=contexts,
        )

    lead = next(
        (
            f
            for f in material
            if f.confidence != "low" and can_lead(f.magnitude, revenue)
        ),
        None,
    )

    if lead is not None and vetoes:
        # Something real was found and the company still should not be called.
        # The findings stay on the page so the reader sees both halves.
        reason = (
            "{title} is filed and material at {share} of revenue, and this company "
            "should still not be approached: {why}"
        ).format(
            title=lead.title,
            share=pct(share_of_revenue(lead.magnitude, revenue)),
            why=vetoes[0].reason[0].lower() + vetoes[0].reason[1:],
        )
        return Assessment(
            company=company,
            fiscal_year=fiscal_year,
            capture=capture,
            verdict="abstain",
            reason=reason,
            revenue=revenue,
            lead=None,
            supporting=tuple(material),
            discarded=tuple(discarded),
            skipped=tuple(skipped),
            signal_count=len(signals),
            slug=slug,
            signals_present=tuple(signals.keys()),
            cleared=tuple(cleared),
            vetoes=vetoes,
            contexts=contexts,
        )

    if lead is None:
        reason = (
            "{n} findings clear the materiality floor but none clears the {floor} lead "
            "floor on better-than-weak evidence. There is something here, and it is not "
            "yet a reason to call anyone."
        ).format(n=len(material), floor=pct(LEAD_FLOOR, 1))
        verdict: Verdict = "thin"
        supporting = tuple(material)
    else:
        reason = (
            "{title} is filed, sized at {amount} a year, {share} of revenue, and rests on "
            "{conf}-confidence evidence."
        ).format(
            title=lead.title,
            amount=inr(lead.magnitude),
            share=pct(share_of_revenue(lead.magnitude, revenue)),
            conf=lead.confidence,
        )
        verdict = "actionable"
        supporting = tuple(f for f in material if f is not lead)

    return Assessment(
        company=company,
        fiscal_year=fiscal_year,
        capture=capture,
        verdict=verdict,
        reason=reason,
        revenue=revenue,
        lead=lead,
        supporting=supporting,
        discarded=tuple(discarded),
        skipped=tuple(skipped),
        signal_count=len(signals),
        slug=slug,
        signals_present=tuple(signals.keys()),
        cleared=tuple(cleared),
        vetoes=vetoes,
        contexts=contexts,
    )
