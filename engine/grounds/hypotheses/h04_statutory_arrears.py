"""H04: undisputed statutory dues in arrears.

The strongest single signal available in Indian filings. CARO 2020 clause vii(a)
requires the statutory auditor to report undisputed statutory dues outstanding
for more than six months. Undisputed means the company agrees it owes the money.
Six months means nobody paid it anyway. The auditor said so, in writing, in a
document the company published.
"""

from __future__ import annotations

from grounds.fmt import inr
from grounds.hypotheses.base import Finding
from grounds.hypotheses.rates import GST_INTEREST_CITE, GST_INTEREST_RATE
from grounds.provenance import Derivation, SignalSet


class StatutoryArrears:
    id = "H04"
    title = "Undisputed statutory dues outstanding over six months"
    requires = ("undisputed_statutory_dues_over_6m", "revenue")

    def evaluate(self, signals: SignalSet) -> Finding | None:
        arrears, revenue = signals.require(
            "undisputed_statutory_dues_over_6m", "revenue"
        )

        if arrears.num <= 0:
            return None

        magnitude = arrears.num * GST_INTEREST_RATE

        mechanism = (
            "The statutory auditor reported {amount} of undisputed dues outstanding more "
            "than six months. Undisputed means the liability is not contested. Six months "
            "means it was not paid regardless. That combination is not a dispute and not a "
            "cash problem at this revenue. It is a process that failed to produce a "
            "payment and failed to escalate."
        ).format(amount=inr(arrears.num))

        return Finding(
            hypothesis_id=self.id,
            title=self.title,
            mechanism=mechanism,
            magnitude=magnitude,
            derivation=Derivation(
                label="Annual interest exposure on undisputed arrears",
                formula=(
                    "undisputed_statutory_dues_over_6m x {rate}  [{cite}]"
                ).format(rate=GST_INTEREST_RATE, cite=GST_INTEREST_CITE),
                substituted="{amount} x {rate}".format(
                    amount=inr(arrears.num), rate=GST_INTEREST_RATE
                ),
                result=magnitude,
                unit="INR per year",
                inputs=(arrears,),
            ),
            confidence="high",
            confirming_question=(
                "Who owned the six-month arrears the auditor flagged, and what alerted "
                "them before the audit did?"
            ),
            kills_if=(
                "The arrears were a single disputed-then-conceded assessment already "
                "cleared, and the control that missed it has been named and changed."
            ),
            evidence=(arrears, revenue),
        )
