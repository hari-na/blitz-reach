"""H02: payables cycle out of line with the sector.

Days payable outstanding is computable from any annual report. On its own it is
weak, because a short cycle can mean discipline and a long one can mean
negotiating power. It earns a place only as a carrying cost against a sector
comparator, and it is capped at medium confidence for exactly that reason.
"""

from __future__ import annotations

from grounds.fmt import inr
from grounds.hypotheses.base import Finding
from grounds.provenance import Derivation, SignalSet

# Annual cost of working capital for a large Indian corporate borrower.
COST_OF_CAPITAL = 0.09
MIN_GAP_DAYS = 5.0


class PayablesDrift:
    id = "H02"
    title = "Payables cycle out of line with the sector"
    requires = ("trade_payables", "purchases", "sector_payable_days_median", "revenue")

    def evaluate(self, signals: SignalSet) -> Finding | None:
        payables, purchases, median, revenue = signals.require(
            "trade_payables", "purchases", "sector_payable_days_median", "revenue"
        )

        if purchases.num <= 0:
            return None

        dpo = payables.num / purchases.num * 365
        gap = dpo - median.num

        if abs(gap) < MIN_GAP_DAYS:
            return None

        daily_purchases = purchases.num / 365
        magnitude = abs(gap) * daily_purchases * COST_OF_CAPITAL
        direction = "longer" if gap > 0 else "shorter"

        mechanism = (
            "Days payable outstanding works out at {dpo:.0f} days against a sector "
            "median of {median:.0f}, so the company holds supplier cash {gap:.0f} days "
            "{direction} than its peers. A longer cycle pushes cost onto suppliers who "
            "finance it at their own borrowing rate and price it back in. A shorter one "
            "is working capital sitting idle. Either way the gap is a number nobody "
            "inside accounts payable is measured on."
        ).format(dpo=dpo, median=median.num, gap=abs(gap), direction=direction)

        return Finding(
            hypothesis_id=self.id,
            title=self.title,
            mechanism=mechanism,
            magnitude=magnitude,
            derivation=Derivation(
                label="Annual carrying cost of the payables gap",
                formula=(
                    "(trade_payables / purchases x 365 - sector_median) "
                    "x (purchases / 365) x {rate}"
                ).format(rate=COST_OF_CAPITAL),
                substituted=(
                    "({payables} / {purchases} x 365 - {median:.0f}) "
                    "x ({purchases} / 365) x {rate}"
                ).format(
                    payables=inr(payables.num),
                    purchases=inr(purchases.num),
                    median=median.num,
                    rate=COST_OF_CAPITAL,
                ),
                result=magnitude,
                unit="INR per year",
                inputs=(payables, purchases, median),
            ),
            confidence="medium",
            confirming_question=(
                "What are your contractual payment terms by supplier tier, and what does "
                "actual days-to-pay look like against them?"
            ),
            kills_if=(
                "The gap is deliberate and negotiated, terms are set per tier, and finance "
                "can produce the actual-versus-contracted variance on request."
            ),
            evidence=(payables, purchases, median, revenue),
        )
