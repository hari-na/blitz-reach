"""What a hypothesis is.

A hypothesis is a deterministic function over filed signals. It either fires
with a computed magnitude and written-out arithmetic, or it does not fire. No
language model is involved in deciding whether there is a problem, and none is
involved in producing a number. The model's only job, later, is prose.

Every hypothesis must state `kills_if`: the answer that would disprove it. A
claim with no disconfirming answer is not a hypothesis, it is a sales line.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

from grounds.provenance import Derivation, MissingSignal, Signal, SignalSet

Confidence = Literal["high", "medium", "low"]

CONFIDENCE_ORDER: dict[Confidence, int] = {"high": 3, "medium": 2, "low": 1}


@dataclass(frozen=True)
class Finding:
    hypothesis_id: str
    title: str
    mechanism: str
    magnitude: float
    derivation: Derivation
    confidence: Confidence
    confirming_question: str
    kills_if: str
    evidence: tuple[Signal, ...]

    def sources(self) -> list[str]:
        seen: list[str] = []
        for sig in self.evidence:
            cite = sig.source.cite()
            if cite not in seen:
                seen.append(cite)
        return seen


@dataclass(frozen=True)
class Skipped:
    """A hypothesis that could not be tested, and exactly what was missing.

    Printed in every brief. A reader who knows the company can tell at a glance
    whether the engine missed something because the filing is silent or because
    nobody fetched the document.
    """

    hypothesis_id: str
    title: str
    missing: tuple[str, ...]


@runtime_checkable
class Hypothesis(Protocol):
    id: str
    title: str
    requires: tuple[str, ...]

    def evaluate(self, signals: SignalSet) -> Finding | None: ...


def run_one(hyp: Hypothesis, signals: SignalSet) -> Finding | Skipped | None:
    try:
        return hyp.evaluate(signals)
    except MissingSignal as exc:
        return Skipped(
            hypothesis_id=hyp.id,
            title=hyp.title,
            missing=tuple(str(exc).split(", ")),
        )
