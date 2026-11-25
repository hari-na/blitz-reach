"""Load a company's captured signals from YAML.

A company file names its sources once and then references them by key, so every
signal is forced to point at a document. `capture` records how the numbers got
here: `parsed` means a document was read programmatically, `hand_seeded` means a
person typed them from the filing. Hand-seeded is honest and prints on the
brief; unlabelled is not allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from grounds.provenance import ProvenanceError, Signal, SignalSet, Source

VALID_CAPTURE = {"parsed", "hand_seeded", "mixed", "synthetic"}


@dataclass(frozen=True)
class CompanyFile:
    company: str
    fiscal_year: str
    capture: str
    signals: SignalSet
    path: Path


def load_company(path: str | Path) -> CompanyFile:
    path = Path(path)
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))

    for field in ("company", "fiscal_year", "capture", "sources", "signals"):
        if field not in raw:
            raise ProvenanceError("{path}: missing '{field}'".format(path=path, field=field))

    capture = str(raw["capture"])
    if capture not in VALID_CAPTURE:
        raise ProvenanceError(
            "{path}: capture must be one of {ok}, got {got!r}".format(
                path=path, ok=sorted(VALID_CAPTURE), got=capture
            )
        )

    sources: dict[str, Source] = {}
    for key, spec in (raw["sources"] or {}).items():
        sources[key] = Source(
            doc_type=str(spec.get("doc_type", "")),
            title=str(spec.get("title", "")),
            year=str(spec.get("year", "")),
            locator=str(spec.get("locator", "")),
            url=str(spec.get("url", "") or ""),
        )

    signals: list[Signal] = []
    for spec in raw["signals"] or []:
        src_key = str(spec.get("source", ""))
        if src_key not in sources:
            raise ProvenanceError(
                "{path}: signal {key!r} points at unknown source {src!r}".format(
                    path=path, key=spec.get("key"), src=src_key
                )
            )
        signals.append(
            Signal(
                key=str(spec["key"]),
                value=spec["value"],
                unit=str(spec.get("unit", "")),
                kind=spec.get("kind", "money"),
                source=sources[src_key],
                note=str(spec.get("note", "") or ""),
            )
        )

    return CompanyFile(
        company=str(raw["company"]),
        fiscal_year=str(raw["fiscal_year"]),
        capture=capture,
        signals=SignalSet(signals),
        path=path,
    )


def load_all(directory: str | Path) -> list[CompanyFile]:
    directory = Path(directory)
    return [load_company(p) for p in sorted(directory.glob("*.yaml"))]
