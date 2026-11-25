"""H05: a deliberately weak signal, kept to prove the engine labels it weak.

Open reconciliation and accounts-payable roles say something about manual load,
but hiring is lumpy, titles are inconsistent, and a posting may be a backfill.
This hypothesis is hard-capped at low confidence and can never lead a brief. It
exists so that a brief resting only on it comes out as thin rather than
actionable.
"""

from __future__ import annotations

from grounds.fmt import inr
from grounds.hypotheses.base import Finding
from grounds.hypotheses.rates import ANALYST_LOADED_COST
from grounds.provenance import Derivation, SignalSet

MIN_OPENINGS = 3


class ManualOpsLoad:
    id = "H05"
    title = "Open headcount in reconciliation and payables"
    requires = ("finance_recon_openings", "revenue")

    def evaluate(self, signals: SignalSet) -> Finding | None:
        openings, revenue = signals.require("finance_recon_openings", "revenue")

        if openings.num < MIN_OPENINGS:
            return None

        magnitude = openings.num * ANALYST_LOADED_COST

        mechanism = (
            "{count:.0f} open roles name reconciliation, accounts payable or invoice "
            "processing in the job description. That is a weak signal. Hiring is lumpy, "
            "titles drift, and some of these are backfills. It is listed so the brief is "
            "honest about what it is resting on, not because it carries a conclusion."
        ).format(count=openings.num)

        return Finding(
            hypothesis_id=self.id,
            title=self.title,
            mechanism=mechanism,
            magnitude=magnitude,
            derivation=Derivation(
                label="Annual cost of the open roles (estimate, not a filed figure)",
                formula="finance_recon_openings x {cost} loaded cost".format(
                    cost=inr(ANALYST_LOADED_COST)
                ),
                substituted="{count:.0f} x {cost}".format(
                    count=openings.num, cost=inr(ANALYST_LOADED_COST)
                ),
                result=magnitude,
                unit="INR per year",
                inputs=(openings,),
            ),
            confidence="low",
            confirming_question=(
                "What are those roles replacing, and what would have to be true for you "
                "not to fill them?"
            ),
            kills_if="They are growth backfills against new entities or geographies.",
            evidence=(openings, revenue),
        )
