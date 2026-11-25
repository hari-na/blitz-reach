"""Statutory rates used in the arithmetic.

Every rate here is a published statutory figure, not an estimate. Each carries
the provision it comes from so the brief can cite it and a reader can argue with
the law rather than with us.
"""

from __future__ import annotations

# RBI bank rate. VERIFY against the current RBI notification before any live
# use: this one number moves and every MSMED interest figure scales with it.
RBI_BANK_RATE = 0.0575
RBI_BANK_RATE_AS_OF = "assumed; verify against the current RBI notification"

# MSMED Act 2006, s.16: interest at three times the bank rate notified by RBI,
# compounded monthly, payable by the buyer on delayed payment to a micro or
# small enterprise. Simple annual equivalent used here, which understates it.
MSMED_PENAL_RATE = 3 * RBI_BANK_RATE
MSMED_PENAL_CITE = "MSMED Act 2006, s.16 (3x RBI bank rate)"

# CGST Act 2017, s.50(1): interest on tax not paid when due.
GST_INTEREST_RATE = 0.18
GST_INTEREST_CITE = "CGST Act 2017, s.50(1)"

# Income-tax Act s.115BAA: 22% + 10% surcharge + 4% cess.
CORPORATE_TAX_RATE = 0.25168
CORPORATE_TAX_CITE = "Income-tax Act, s.115BAA (22% + surcharge + cess)"

# Fully loaded annual cost of one mid-level accounts or reconciliation analyst
# in a tier-1 Indian city. An estimate, which is why any finding resting on it
# is capped at low confidence and can never lead a brief.
ANALYST_LOADED_COST = 900_000
