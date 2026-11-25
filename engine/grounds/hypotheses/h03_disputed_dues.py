"""H03: disputed statutory dues.

Contested indirect tax does not mean the company is wrong. It means a return it
filed and an assessment it received disagree, repeatedly and at scale, and
interest runs at 18% a year under s.50(1) while the dispute sits. The useful
question is not who is right but which reconciliation produced the gap.
"""

from __future__ import annotations

from grounds.fmt import inr
from grounds.hypotheses.base import Finding
from grounds.hypotheses.rates import GST_INTEREST_CITE, GST_INTEREST_RATE
from grounds.provenance import Derivation, SignalSet


class DisputedStatutoryDues:
    id = "H03"
    title = "Interest running on disputed statutory dues"
    requires = ("disputed_statutory_dues", "revenue")

    def evaluate(self, signals: SignalSet) -> Finding | None:
        disputed, revenue = signals.require("disputed_statutory_dues", "revenue")

        if disputed.num <= 0:
            return None

        magnitude = disputed.num * GST_INTEREST_RATE

        mechanism = (
            "{amount} of statutory dues sits contested. Whatever the merits, interest "
            "accrues at 18% a year while it does, and a contested assessment begins as a "
            "mismatch between a filed return and the underlying transactions. The "
            "disputes are the visible end of a reconciliation that did not hold."
        ).format(amount=inr(disputed.num))

        return Finding(
            hypothesis_id=self.id,
            title=self.title,
            mechanism=mechanism,
            magnitude=magnitude,
            derivation=Derivation(
                label="Annual interest exposure on contested dues",
                formula="disputed_statutory_dues x {rate}  [{cite}]".format(
                    rate=GST_INTEREST_RATE, cite=GST_INTEREST_CITE
                ),
                substituted="{amount} x {rate}".format(
                    amount=inr(disputed.num), rate=GST_INTEREST_RATE
                ),
                result=magnitude,
                unit="INR per year",
                inputs=(disputed,),
            ),
            confidence="medium",
            confirming_question=(
                "Of the disputed demands, how many began as a mismatch between your own "
                "filed return and your ledger rather than a difference of legal opinion?"
            ),
            kills_if=(
                "The disputes are substantive points of law on a handful of assessments, "
                "not recurring reconciliation differences, and tax can name each one."
            ),
            evidence=(disputed, revenue),
        )
