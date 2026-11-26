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
        bearing = (
            "A group this small has a close that a competent team already handles in "
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


CONTEXTS = (small_supplier_exposure, close_complexity)


def run_contexts(signals: SignalSet) -> tuple[Context, ...]:
    out: list[Context] = []
    for fn in CONTEXTS:
        got = fn(signals)
        if got is not None:
            out.append(got)
    return tuple(out)
