"""H03: disputed GST dues, and only GST.

Corrected after reading India Cements' FY2026 disputed-dues annexure, which is
the clearest argument against the first version of this hypothesis.

That annexure totals Rs 930.26 crore. Most of it is excise and sales tax
litigation running from 1995-96, sitting at the Supreme Court, the High Courts
and CESTAT, plus Rs 438.62 crore of electricity, stamp duty and mining cases.
Thirty years of tax law under appeal is not a reconciliation failure, and sizing
a process problem off it would have been exactly the kind of confident nonsense
this engine is supposed to refuse to produce.

So this hypothesis takes the GST-era slice only. GST is self-assessed and
return-driven: a demand under it starts life as a disagreement between a return
the company filed and its own underlying transactions. That is a process
mechanism. Interest runs at 18% a year under s.50(1) while the dispute sits.

The pre-GST total is still captured, as context, so a reader can see what was
deliberately left out and argue with the choice.
"""

from __future__ import annotations

from grounds.fmt import inr
from grounds.hypotheses.base import Finding
from grounds.hypotheses.rates import GST_INTEREST_CITE, GST_INTEREST_RATE
from grounds.provenance import Derivation, Signal, SignalSet


class DisputedStatutoryDues:
    id = "H03"
    title = "Interest exposure on disputed GST demands"
    requires = ("disputed_gst_dues", "revenue")

    def evaluate(self, signals: SignalSet) -> Finding | None:
        disputed, revenue = signals.require("disputed_gst_dues", "revenue")

        if disputed.num <= 0:
            return None

        magnitude = disputed.num * GST_INTEREST_RATE
        total = signals.get("disputed_dues_total")

        context_clause = ""
        if total is not None and total.num > disputed.num:
            context_clause = (
                " The company's full disputed-dues annexure comes to {t}, but the rest is "
                "pre-GST excise, customs, sales tax and other litigation, some of it "
                "decades old and sitting at the Supreme Court. That is tax law under "
                "appeal, not a process failure, and it is deliberately excluded from the "
                "figure above.".format(t=inr(total.num))
            )

        mechanism = (
            "{amount} of GST demands sit contested. Whatever the merits, GST is "
            "self-assessed and return-driven, so a demand under it begins as a "
            "disagreement between a return the company filed and its own underlying "
            "transactions. Interest accrues at 18% a year while the dispute sits. The "
            "demands are the visible end of a reconciliation that did not hold.{context}"
        ).format(amount=inr(disputed.num), context=context_clause)

        evidence: tuple[Signal, ...] = (disputed, revenue)
        if total is not None:
            evidence += (total,)

        return Finding(
            hypothesis_id=self.id,
            title=self.title,
            mechanism=mechanism,
            magnitude=magnitude,
            derivation=Derivation(
                label="Annual interest exposure on contested GST demands",
                formula="disputed_gst_dues x {rate}  [{cite}]".format(
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
                "Of the GST demands under appeal, how many began as a mismatch between "
                "your filed return and your own ledger rather than a difference of legal "
                "opinion?"
            ),
            kills_if=(
                "The GST demands are substantive points of law on a handful of "
                "assessments, not recurring reconciliation differences, and tax can name "
                "each one and what it turns on."
            ),
            evidence=evidence,
        )
