"""Qualifiers: a second source that cannot find anything, only stop you.

Adding a second signal family was meant to produce more findings. Reading two
credit rating rationales in full established the opposite, and it is the more
useful result.

The Ramco Cements Crisil rationale of March 2026, AA+/Stable, 29,859 characters
read end to end, mentions creditors, trade payables, creditor days and the
working capital cycle exactly nowhere. Nor does the India Cements Crisil
rationale of March 2023. Analysts write about payables only when payables are
already the problem, so a rating document is not a place to discover one.

What a rating document does carry, reliably and in machine-readable form, is
whether the company can act on anything at all. The India Cements rationale
revised the company to BB/Stable "Issuer Not Cooperating", then withdrew the
ratings at the company's own request, after Crisil chased it with letters on
four dates in 2023 and received nothing.

That changes what a finding is worth. The engine sizes a real Rs 34.29 crore
interest exposure at India Cements. A company that stopped answering its own
rating agency and has had no rated facility since is not going to buy finance
automation, so naming a real problem there wastes the approach just as surely as
naming an immaterial one.

So a qualifier never creates a finding. It vetoes the approach, and the brief
prints what was found alongside the reason for not calling.
"""

from __future__ import annotations

from dataclasses import dataclass

from grounds.provenance import SignalSet

# Long-term rating grades, best first. A grade below BBB- is sub-investment
# grade in the Indian scale, which is the line used here.
GRADE_ORDER: tuple[str, ...] = (
    "AAA",
    "AA+",
    "AA",
    "AA-",
    "A+",
    "A",
    "A-",
    "BBB+",
    "BBB",
    "BBB-",
    "BB+",
    "BB",
    "BB-",
    "B+",
    "B",
    "B-",
    "C",
    "D",
)
INVESTMENT_GRADE_FLOOR = GRADE_ORDER.index("BBB-")


@dataclass(frozen=True)
class Veto:
    qualifier_id: str
    reason: str
    citation: str


def _grade_rank(grade: str) -> int | None:
    g = grade.strip().upper().replace("CRISIL", "").replace("CARE", "").strip()
    return GRADE_ORDER.index(g) if g in GRADE_ORDER else None


def creditworthiness(signals: SignalSet) -> list[Veto]:
    """Can this company act on a finding at all?"""
    out: list[Veto] = []

    inc = signals.get("issuer_not_cooperating")
    if inc is not None and inc.num > 0:
        out.append(
            Veto(
                qualifier_id="Q01",
                reason=(
                    "The company's own rating agency has tagged it Issuer Not "
                    "Cooperating, meaning it stopped supplying the information needed to "
                    "rate it. An organisation that does not answer its rating agency "
                    "will not answer an outbound approach about its accounts payable."
                ),
                citation=inc.source.cite(),
            )
        )

    withdrawn = signals.get("rating_withdrawn")
    if withdrawn is not None and withdrawn.num > 0:
        out.append(
            Veto(
                qualifier_id="Q02",
                reason=(
                    "Its credit ratings have been withdrawn, so there is no current "
                    "public assessment of whether it can fund anything. Absence of a "
                    "rating is not neutral when the company previously had one."
                ),
                citation=withdrawn.source.cite(),
            )
        )

    grade = signals.get("credit_rating_grade")
    if grade is not None and isinstance(grade.value, str):
        rank = _grade_rank(grade.value)
        if rank is not None and rank > INVESTMENT_GRADE_FLOOR:
            out.append(
                Veto(
                    qualifier_id="Q03",
                    reason=(
                        "Its last long-term rating was {g}, below investment grade. A "
                        "company in that position cuts discretionary spend rather than "
                        "buying software, however well the problem is evidenced."
                    ).format(g=grade.value),
                    citation=grade.source.cite(),
                )
            )

    return out


QUALIFIERS = (creditworthiness,)


def run_qualifiers(signals: SignalSet) -> tuple[Veto, ...]:
    out: list[Veto] = []
    for fn in QUALIFIERS:
        out.extend(fn(signals))
    return tuple(out)
