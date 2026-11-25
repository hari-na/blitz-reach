"""H01: late payment to micro and small suppliers.

Every audited Indian buyer must disclose, in its annual financial statements,
the principal still unpaid to micro and small enterprise suppliers beyond the
appointed day and the interest accrued on it. That makes "this company pays its
small suppliers late" a filed, audited number rather than an inference.

The mechanism this points at is the one interview 04 described from the other
side. A motor rewinding shop in Coimbatore draws 80% of its revenue from ten
customers above Rs 2,000 crore turnover, waits 30 to 60 days, and when an
invoice is held for a purchase-order mismatch the owner or his father drives to
the customer's accounts department carrying printed email threads. The
correction takes months. None of that is visible inside the buyer's own system,
where the invoice simply sits unapproved.
"""

from __future__ import annotations

from grounds.fmt import inr
from grounds.hypotheses.base import Confidence, Finding
from grounds.hypotheses.rates import (
    MSMED_PENAL_CITE,
    MSMED_PENAL_RATE,
)
from grounds.provenance import Derivation, SignalSet


class MsePaymentDelay:
    id = "H01"
    title = "Statutory interest accruing on late payment to small suppliers"
    requires = ("mse_principal_overdue", "revenue")

    def evaluate(self, signals: SignalSet) -> Finding | None:
        principal, revenue = signals.require("mse_principal_overdue", "revenue")

        if principal.num <= 0:
            return None

        disclosed = signals.get("mse_interest_accrued")
        confidence: Confidence

        if disclosed is not None and disclosed.num > 0:
            # Two independently filed numbers. Prefer the company's own figure
            # over ours, and say so.
            magnitude = disclosed.num
            derivation = Derivation(
                label="Interest accrued on overdue MSE principal",
                formula="interest_accrued_as_disclosed",
                substituted=f"{inr(disclosed.num)} (as filed)",
                result=magnitude,
                unit="INR per year",
                inputs=(disclosed, principal),
            )
            confidence = "high"
        else:
            magnitude = principal.num * MSMED_PENAL_RATE
            derivation = Derivation(
                label="Statutory interest on overdue MSE principal",
                formula=f"mse_principal_overdue x {MSMED_PENAL_RATE:.4f}  [{MSMED_PENAL_CITE}]",
                substituted=f"{inr(principal.num)} x {MSMED_PENAL_RATE:.4f}",
                result=magnitude,
                unit="INR per year",
                inputs=(principal,),
            )
            confidence = "medium"

        return Finding(
            hypothesis_id=self.id,
            title=self.title,
            mechanism=(
                "The company has filed that it owes micro and small suppliers "
                f"{inr(principal.num)} past the appointed day. Interest on that runs "
                "automatically under the MSMED Act whether or not anyone raises it, and "
                "from AY 2024-25 the unpaid principal is also disallowed as a deduction "
                "under s.43B(h) until it is paid. Neither consequence is triggered by a "
                "supplier complaining. Both are triggered by the date on the invoice."
            ),
            magnitude=magnitude,
            derivation=derivation,
            confidence=confidence,
            confirming_question=(
                "Of your suppliers below the small-enterprise threshold, what share were "
                "paid inside 45 days last quarter, and which system computes that number?"
            ),
            kills_if=(
                "Treasury already reports days-to-pay split by supplier size, the 45-day "
                "breach rate is tracked monthly, and the disclosed balance is a timing "
                "artifact of the year-end cutoff rather than a standing pattern."
            ),
            evidence=(principal, revenue) + ((disclosed,) if disclosed else ()),
        )
