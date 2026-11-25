"""Provenance-bound value types.

Nothing enters the pipeline without a citation. A Signal that cannot name the
document and the exact place inside it cannot be constructed. That is the whole
reliability argument of this project: a reader never has to trust the engine,
only check its arithmetic against a document they can open themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

SignalKind = Literal["money", "days", "count", "ratio", "text", "date"]


class ProvenanceError(ValueError):
    """A signal was built without a checkable citation."""


class MissingSignal(LookupError):
    """A hypothesis asked for a signal this company does not have."""


class ScaleError(ValueError):
    """A figure's stated scale does not reconcile with the value recorded."""


# Indian annual reports are denominated in lakhs, crores or millions, and the
# choice is made per statement, not per document. A survey of ten FY2025-26
# reports found the scale declared on the note's own page in only six, declared
# nowhere nearby in three, and in The India Cements Limited the note is in lakhs
# while the document's own first declaration says crore. Taking the scale from
# the wrong place is a hundredfold error, which is the single most dangerous
# mistake available in this whole pipeline.
UNIT_MULTIPLIERS: dict[str, float] = {
    "unit": 1.0,
    "thousand": 1_000.0,
    "lakh": 100_000.0,
    "million": 1_000_000.0,
    "crore": 10_000_000.0,
}


@dataclass(frozen=True)
class Source:
    """A document the reader can open and check."""

    doc_type: str  # annual_report | mca_msme_1 | caro | job_posting | gst_portal
    title: str
    year: str
    locator: str  # "Note 34, page 187" or "CARO 2020, para vii(a)"
    url: str = ""

    def __post_init__(self) -> None:
        for name in ("doc_type", "title", "year", "locator"):
            if not str(getattr(self, name)).strip():
                raise ProvenanceError(
                    f"Source.{name} is required. A signal with no {name} cannot "
                    "be checked by the reader, so it must not enter the pipeline."
                )

    def cite(self) -> str:
        base = f"{self.title} ({self.year}), {self.locator}"
        return f"{base} [{self.url}]" if self.url else base


@dataclass(frozen=True)
class Signal:
    """One value read off one document."""

    key: str
    value: float | str
    unit: str
    kind: SignalKind
    source: Source
    note: str = ""
    # How the figure is printed in the filing, and the scale it is printed on.
    # When both are given the conversion is checked, so a scale error cannot be
    # typed into a capture without the loader rejecting it.
    as_filed: str = ""
    filed_unit: str = ""

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ProvenanceError("Signal.key is required.")
        if not isinstance(self.source, Source):
            raise ProvenanceError(
                f"Signal {self.key!r} has no Source. Every value must cite a document."
            )
        if self.kind in ("money", "days", "count", "ratio") and not isinstance(
            self.value, (int, float)
        ):
            raise ProvenanceError(
                f"Signal {self.key!r} is kind={self.kind} but value is not numeric."
            )
        self._check_scale()

    def _check_scale(self) -> None:
        if not self.as_filed and not self.filed_unit:
            return
        if not (self.as_filed and self.filed_unit):
            raise ProvenanceError(
                f"Signal {self.key!r} gives only one of as_filed / filed_unit. "
                "A figure's printed form and its scale are one fact; record both or "
                "neither."
            )

        unit = self.filed_unit.strip().lower().rstrip("s")
        if unit not in UNIT_MULTIPLIERS:
            raise ScaleError(
                f"Signal {self.key!r} has filed_unit {self.filed_unit!r}. "
                f"Known scales: {sorted(UNIT_MULTIPLIERS)}."
            )

        try:
            printed = float(self.as_filed.replace(",", "").strip())
        except ValueError as exc:
            raise ProvenanceError(
                f"Signal {self.key!r} as_filed {self.as_filed!r} is not a number."
            ) from exc

        expected = printed * UNIT_MULTIPLIERS[unit]
        # Tolerate rounding in the last printed digit, nothing more. A scale
        # mistake is off by at least a factor of ten and can never pass this.
        if abs(float(self.value) - expected) > max(abs(expected) * 1e-6, 1.0):
            raise ScaleError(
                f"Signal {self.key!r} does not reconcile: {self.as_filed} "
                f"{self.filed_unit} is {expected:,.0f}, but {float(self.value):,.0f} "
                "was recorded. Check the scale declared on the page the figure "
                "came from, not the one at the front of the document."
            )

    @property
    def num(self) -> float:
        if not isinstance(self.value, (int, float)):
            raise ProvenanceError(f"Signal {self.key!r} is not numeric.")
        return float(self.value)


@dataclass(frozen=True)
class Derivation:
    """One arithmetic step, written out so a reader can redo it by hand.

    `formula` names the inputs, `substituted` shows the numbers put in. Both are
    printed in the brief. A finding whose arithmetic cannot be written out this
    way does not belong in a brief.
    """

    label: str
    formula: str
    substituted: str
    result: float
    unit: str
    inputs: tuple[Signal, ...]

    def sources(self) -> list[Source]:
        seen: list[Source] = []
        for sig in self.inputs:
            if sig.source not in seen:
                seen.append(sig.source)
        return seen


class SignalSet:
    """The signals available for one company."""

    def __init__(self, signals: Iterable[Signal]) -> None:
        self._by_key: dict[str, Signal] = {}
        for sig in signals:
            self._by_key[sig.key] = sig

    def __contains__(self, key: str) -> bool:
        return key in self._by_key

    def __len__(self) -> int:
        return len(self._by_key)

    def keys(self) -> list[str]:
        return sorted(self._by_key)

    def get(self, key: str) -> Signal | None:
        return self._by_key.get(key)

    def require(self, *keys: str) -> tuple[Signal, ...]:
        missing = [k for k in keys if k not in self._by_key]
        if missing:
            raise MissingSignal(", ".join(missing))
        return tuple(self._by_key[k] for k in keys)
