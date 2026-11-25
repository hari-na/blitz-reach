"""The hypothesis registry.

Order here is presentation order within a confidence band, not priority.
Ranking happens in grounds.verdict, against money and confidence.
"""

from __future__ import annotations

from grounds.hypotheses.base import (
    CONFIDENCE_ORDER,
    Confidence,
    Finding,
    Hypothesis,
    Skipped,
    run_one,
)
from grounds.hypotheses.h01_mse_delay import MsePaymentDelay
from grounds.hypotheses.h02_payables_drift import PayablesDrift
from grounds.hypotheses.h03_disputed_dues import DisputedStatutoryDues
from grounds.hypotheses.h04_statutory_arrears import StatutoryArrears
from grounds.hypotheses.h05_manual_ops import ManualOpsLoad

REGISTRY: tuple[Hypothesis, ...] = (
    StatutoryArrears(),
    MsePaymentDelay(),
    DisputedStatutoryDues(),
    PayablesDrift(),
    ManualOpsLoad(),
)

__all__ = [
    "CONFIDENCE_ORDER",
    "Confidence",
    "DisputedStatutoryDues",
    "Finding",
    "Hypothesis",
    "ManualOpsLoad",
    "MsePaymentDelay",
    "PayablesDrift",
    "REGISTRY",
    "Skipped",
    "StatutoryArrears",
    "run_one",
]
