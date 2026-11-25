"""H01: late payment to micro and small suppliers.

Corrected after reading three real annual reports. The first version sized this
off the principal balance, which is wrong, and the filings are what showed it.

Section 22 of the MSMED Act requires the disclosure of "the principal amount and
the interest due thereon remaining unpaid to any supplier at the end of each
accounting year." That is a closing balance. It includes invoices that are not
yet due. A large principal balance proves only that the company buys from small
suppliers, which is not a finding.

The interest lines are different. Interest under s.16 exists only where payment
went past the appointed day, so a non-zero figure is the company's own audited
admission that it paid late, and a nil figure is its audited claim that it did
not. Two of the three companies captured report nil, and this hypothesis
correctly says nothing about either.

The mechanism it points at is the one interview 04 described from the other side.
A motor rewinding shop in Coimbatore draws 80% of its revenue from ten customers
above Rs 2,000 crore turnover, waits 30 to 60 days, and when an invoice is held
for a purchase-order mismatch the owner or his father drives to the customer's
accounts department carrying printed email threads. The correction takes months.
None of that is visible inside the buyer's system, where the invoice simply sits.
"""

from __future__ import annotations

from grounds.fmt import inr
from grounds.hypotheses.base import Finding
from grounds.hypotheses.rates import MSMED_PENAL_CITE
from grounds.provenance import Derivation, Signal, SignalSet


class MsePaymentDelay:
    id = "H01"
    title = "Interest on late payment to micro and small suppliers"
    requires = ("mse_interest_accrued_unpaid", "revenue")

    def evaluate(self, signals: SignalSet) -> Finding | None:
        accrued, revenue = signals.require("mse_interest_accrued_unpaid", "revenue")

        paid = signals.get("mse_interest_paid_during_year")
        paid_amount = paid.num if paid is not None else 0.0

        # Nil interest is a filed, audited statement that the company paid its
        # small suppliers on time. Saying anything here would be inventing a
        # problem out of a balance sheet line.
        if accrued.num <= 0 and paid_amount <= 0:
            return None

        magnitude = accrued.num + paid_amount
        principal = signals.get("mse_principal_outstanding")

        if paid is not None and paid_amount > 0:
            formula = "mse_interest_accrued_unpaid + mse_interest_paid_during_year"
            substituted = "{a} + {p}".format(a=inr(accrued.num), p=inr(paid_amount))
            label = "Interest on late payment, accrued plus actually paid out"
        else:
            formula = "mse_interest_accrued_unpaid"
            substituted = inr(accrued.num)
            label = "Interest accrued and remaining unpaid"

        paid_clause = (
            " It also paid out {p} of such interest during the year, so this is not a "
            "year-end timing artifact: money left the building.".format(
                p=inr(paid_amount)
            )
            if paid_amount > 0
            else ""
        )
        principal_clause = (
            " The outstanding balance owed to those suppliers is {b}, though that "
            "figure includes invoices not yet due and is context rather than "
            "evidence.".format(b=inr(principal.num))
            if principal is not None
            else ""
        )

        mechanism = (
            "The company has filed, in audited accounts, that {a} of interest under the "
            "MSMED Act is accrued and unpaid to micro and small suppliers. That interest "
            "exists only where payment went past the appointed day, so this is its own "
            "admission of late payment rather than our inference.{paid} It runs at three "
            "times the RBI bank rate whether or not a supplier ever raises it, and since "
            "AY 2024-25 the unpaid principal is also disallowed as a deduction under "
            "s.43B(h) until paid. Neither consequence is triggered by a supplier "
            "complaining. Both are triggered by the date on the invoice.{principal}"
        ).format(a=inr(accrued.num), paid=paid_clause, principal=principal_clause)

        evidence: tuple[Signal, ...] = (accrued, revenue)
        if paid is not None:
            evidence += (paid,)
        if principal is not None:
            evidence += (principal,)

        return Finding(
            hypothesis_id=self.id,
            title=self.title,
            mechanism=mechanism,
            magnitude=magnitude,
            derivation=Derivation(
                label="{l}  [{cite}]".format(l=label, cite=MSMED_PENAL_CITE),
                formula=formula,
                substituted=substituted,
                result=magnitude,
                unit="INR per year",
                inputs=evidence[:1] + ((paid,) if paid is not None else ()),
            ),
            confidence="high",
            confirming_question=(
                "Of your suppliers below the small-enterprise threshold, what share were "
                "paid inside 45 days last quarter, and which system computes that number?"
            ),
            kills_if=(
                "Treasury already reports days-to-pay split by supplier size, the 45-day "
                "breach rate is tracked monthly, and the interest arose on a small number "
                "of disputed invoices rather than across the supplier base."
            ),
            evidence=evidence,
        )
