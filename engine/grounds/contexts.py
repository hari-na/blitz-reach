"""Context: filed facts that shape a brief without pretending to be findings.

Two indicators survived testing against ten annual reports, and neither one
converts honestly into rupees.

The share of purchases sourced from micro and small enterprises is a filed
percentage. It is exposure, not a loss. A company buying a fifth of its inputs
from small suppliers and paying them on time has no problem at all.

The number of entities a group consolidates is a filed count. It makes the
month-end close structurally harder, but turning "forty subsidiaries" into a
rupee figure needs a cost-per-entity that no filing states, and inventing one
is precisely what the number guard in `compose.py` exists to prevent.

So they are contexts. A context carries no magnitude, never leads, never vetoes
and never moves a verdict. It tells the reader the shape of the company, which
is what decides how to open a conversation even when the money figure comes
from somewhere else.

Context also does something a finding cannot: it says when a silence is
uninformative. H01 staying quiet at a company that sources 2.69% of its
purchases from small suppliers means nothing, because there was almost nothing
to be late on. The same silence at 22% is real evidence of discipline.
"""

from __future__ import annotations

from dataclasses import dataclass

from grounds.fmt import inr
from grounds.provenance import Signal, SignalSet

# Below this share of purchases, the MSMED signal cannot say anything about a
# company either way, so H01's silence is not evidence of anything.
MSME_RELEVANCE_FLOOR = 0.05

# Below this share of revenue, intercompany trade is not what shapes a close.
RPT_INTENSITY_FLOOR = 0.05
# A share that has at least doubled against a base that now matters is a
# structural change in close workload inside one year.
RPT_SHARP_RISE = 2.0

# Bands for how many legal entities roll up into one set of accounts. These are
# judgment, not filed, and the brief says so. Anchored on what the corpus
# actually contains: India Cements consolidates 4, Dalmia 40, JSW Steel 70.
ENTITY_BANDS: tuple[tuple[int, str], ...] = (
    (5, "simple"),
    (25, "moderate"),
    (10**9, "complex"),
)

DIRECTION_WORDS = {
    "rising": "up from",
    "falling": "down from",
    "flat": "level with",
    "new": "up from nothing at",
    "gone": "down from",
    "unknown": "",
}


@dataclass(frozen=True)
class Context:
    context_id: str
    title: str
    statement: str
    evidence: tuple[Signal, ...]
    # What this means for reading the rest of the brief, where it means anything.
    bearing: str = ""

    def sources(self) -> list[str]:
        seen: list[str] = []
        for sig in self.evidence:
            cite = sig.source.cite()
            if cite not in seen:
                seen.append(cite)
        return seen


def _band(count: float) -> str:
    for ceiling, word in ENTITY_BANDS:
        if count <= ceiling:
            return word
    return "complex"


def small_supplier_exposure(signals: SignalSet) -> Context | None:
    """C01. How much of what this company buys comes from small suppliers."""
    share = signals.get("msme_sourcing_share")
    if share is None:
        return None

    pct_now = share.num * 100
    direction = share.direction()
    movement = ""
    if direction != "unknown" and share.prior_value is not None:
        movement = ", {w} {p:.2f}% last year".format(
            w=DIRECTION_WORDS[direction], p=float(share.prior_value) * 100
        )

    statement = (
        "{pct:.2f}% of purchases are sourced directly from micro and small "
        "enterprises{move}. The figure is filed in the company's own "
        "sustainability report, where the format is prescribed."
    ).format(pct=pct_now, move=movement)

    if share.num < MSME_RELEVANCE_FLOOR:
        bearing = (
            "Below {floor:.0f}% the MSMED signal cannot say anything about this "
            "company. If H01 is silent here that is not evidence of discipline, it is "
            "evidence that there was almost nothing to be late on, and the brief should "
            "not be read as clearing them on it."
        ).format(floor=MSME_RELEVANCE_FLOOR * 100)
    elif direction == "rising":
        bearing = (
            "Exposure is growing. Spend is moving toward suppliers whose late payment "
            "carries statutory interest and, since AY 2024-25, a disallowed deduction "
            "under s.43B(h). Accounts payable processes rarely change when a supplier "
            "mix does, so this is where to ask what has been adjusted."
        )
    else:
        bearing = (
            "Enough of the supplier base is small for the MSMED signal to be meaningful, "
            "so H01's reading here carries weight either way."
        )

    return Context(
        context_id="C01",
        title="Exposure to small suppliers",
        statement=statement,
        evidence=(share,),
        bearing=bearing,
    )


def close_complexity(signals: SignalSet) -> Context | None:
    """C02. How many legal entities have to be closed and consolidated."""
    subs = signals.get("subsidiary_count")
    if subs is None:
        return None

    jvs = signals.get("joint_venture_count")
    assoc = signals.get("associate_count")
    total = subs.num + (jvs.num if jvs else 0) + (assoc.num if assoc else 0)

    def plural(n: float, one: str, many: str) -> str:
        return "{n:.0f} {w}".format(n=n, w=one if n == 1 else many)

    parts = [plural(subs.num, "subsidiary", "subsidiaries")]
    if jvs is not None and jvs.num:
        parts.append(plural(jvs.num, "joint venture", "joint ventures"))
    if assoc is not None and assoc.num:
        parts.append(plural(assoc.num, "associate", "associates"))
    listed = ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]

    tail = (
        "{listed}, which is a {band} close."
        if len(parts) == 1
        else "{listed}: {total:.0f} entities in all, which is a {band} close."
    ).format(listed=listed, total=total, band=_band(total))

    statement = (
        "The group consolidates {tail} Companies are required to list them, so the "
        "count is filed rather than estimated, though the band is our judgment and "
        "not theirs."
    ).format(tail=tail)

    if _band(total) == "complex":
        bearing = (
            "Every entity is its own ledger, its own intercompany balances to eliminate "
            "and, where it sits abroad, its own currency and statutory calendar. Closing "
            "is one of the six workflows Zamp publishes, and the number it quotes is 75% "
            "of close touchpoints removed. A group this size is where that argument "
            "lands hardest, independently of anything owed to anyone."
        )
    elif _band(total) == "simple":
        # An entity count is a poor proxy for close workload, and C03 can
        # contradict it outright. India Cements consolidates four entities and
        # runs 62% of its revenue through them, which is not a simple close by
        # any reading. Where trade volume says otherwise, the count does not
        # get to clear the company.
        trade = signals.get("related_party_trade_value")
        revenue = signals.get("revenue")
        busy = (
            trade is not None
            and revenue is not None
            and revenue.num > 0
            and trade.num / revenue.num >= RPT_INTENSITY_FLOOR
        )
        bearing = (
            "Few entities, but see C03: the volume running between them is what makes "
            "this close heavy, not how many there are. An entity count is the wrong "
            "measure here and the close argument is still open."
            if busy
            else "A group this small has a close that a competent team already handles in "
            "days. The close argument is not the way in here."
        )
    else:
        bearing = ""

    evidence = tuple(s for s in (subs, jvs, assoc) if s is not None)
    return Context(
        context_id="C02",
        title="Close complexity",
        statement=statement,
        evidence=evidence,
        bearing=bearing,
    )





def related_party_intensity(signals: SignalSet) -> Context | None:
    """C03. How much of the company's trade is with its own group.

    The largest filed figure this engine reads, and still not a finding. Every
    rupee of it has to be matched between two ledgers and eliminated on
    consolidation, which is close work and is exactly what Zamp sells against.
    But no filing anywhere states the cost of reconciling an intercompany
    invoice, and multiplying a volume by a rate I invented is the one thing the
    number guard in `compose.py` exists to stop. So it carries no magnitude,
    cannot lead, and cannot move a verdict. The ratio is the signal.
    """
    trade = signals.get("related_party_trade_value")
    revenue = signals.get("revenue")
    if trade is None or revenue is None or revenue.num <= 0:
        return None

    share_now = trade.num / revenue.num
    share_prior: float | None = None
    if trade.prior_value is not None:
        # Measured against the same denominator on purpose. A prior-year
        # revenue is not always captured, and the question here is how much of
        # this year's business runs through the group, not a restated history.
        share_prior = float(trade.prior_value) / revenue.num

    movement = ""
    if share_prior is not None:
        movement = ", against {p:.1f}% of the same revenue a year earlier".format(
            p=share_prior * 100
        )

    statement = (
        "{amt} of trade ran through related parties, {pct:.1f}% of revenue{move}. "
        "Each of those transactions exists twice, once in each entity's ledger, "
        "and has to be matched and eliminated before the group's accounts close."
    ).format(amt=inr(trade.num), pct=share_now * 100, move=movement)

    named_by_auditor = signals.get("kam_related_party") is not None
    auditor_clause = (
        " The auditor reached the same place independently: related party "
        "transactions are one of the matters they named as most significant in "
        "the entire audit."
        if named_by_auditor
        else ""
    )

    if share_now < RPT_INTENSITY_FLOOR:
        bearing = (
            "Intercompany trade is a small part of this company's activity, so the "
            "close argument does not rest here."
        )
    elif share_prior is not None and share_prior > 0 and share_now / share_prior >= RPT_SHARP_RISE:
        bearing = (
            "This is the thing to ask about. The share has moved {x:.1f}x in a single "
            "year, which is a structural change in how much reconciliation the close "
            "requires. Processes do not re-fit themselves that fast, and whoever runs "
            "the close absorbed it with the headcount they already had.{aud}"
        ).format(x=share_now / share_prior, aud=auditor_clause)
    else:
        bearing = (
            "A substantial share of trade is intercompany, so elimination and matching "
            "are a standing part of every close here rather than an occasional "
            "adjustment.{aud}"
        ).format(aud=auditor_clause)

    evidence = tuple(
        s for s in (trade, signals.get("kam_related_party")) if s is not None
    )
    return Context(
        context_id="C03",
        title="Trade with its own group",
        statement=statement,
        evidence=evidence,
        bearing=bearing,
    )


CONTEXTS = (small_supplier_exposure, close_complexity, related_party_intensity)


def run_contexts(signals: SignalSet) -> tuple[Context, ...]:
    out: list[Context] = []
    for fn in CONTEXTS:
        got = fn(signals)
        if got is not None:
            out.append(got)
    return tuple(out)
