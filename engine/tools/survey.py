"""Survey how a set of annual reports word the disclosures we depend on.

The point is not to extract figures. It is to find out whether the assumptions
behind the hypotheses survive contact with ten companies instead of three:

  Does every audited Indian company actually print an MSMED interest line?
  Is it worded consistently enough to find programmatically?
  How often is it nil, which is what makes H01 stay silent?
  Does CARO clause vii(a) state a figure or just assert compliance?
  What units is each report denominated in?

Usage, from the engine directory:

    python -I tools/survey.py data/filings
    python -I tools/survey.py data/filings --verbose
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Each probe is (label, pattern). Several alternatives per concept, because the
# whole question is how much the wording varies.
MSMED_NOTE = re.compile(
    r"micro[,\s].{0,10}small.{0,40}enterprises?\s+development|MSMED", re.IGNORECASE | re.DOTALL
)
INTEREST_ACCRUED = re.compile(
    r"interest\s+accrued\s+and\s+remaining\s+unpaid", re.IGNORECASE
)
INTEREST_ANY = re.compile(r"amount\s+of\s+interest", re.IGNORECASE)
PRINCIPAL = re.compile(r"principal\s+amount", re.IGNORECASE)
CARO_SIX_MONTHS = re.compile(
    r"(more than six months|more than 6 months)", re.IGNORECASE
)
CARO_NO_ARREARS = re.compile(
    r"(no undisputed|there were no undisputed|were no undisputed amounts)",
    re.IGNORECASE,
)
# Units must be matched next to whatever glyph the report's embedded font maps
# the rupee sign to. Observed across ten reports: a backtick in India Cements,
# "C" and "D" in LMW, and the real sign elsewhere. So allow any non-word
# character before the unit word, not a fixed list of symbols.
UNITS = re.compile(
    r"(?:in\s+|[^\w\s]\s*|Rs\.?\s*)(lakhs?|crores?|millions?|thousands?)",
    re.IGNORECASE,
)

# A PDF Portfolio is a container of embedded PDFs. It extracts as a single page
# telling you to open it in Acrobat, so the real document is unreachable.
PORTFOLIO = re.compile(r"open this PDF portfolio", re.IGNORECASE)

# A nil marker in an Indian annual report is any of these.
NIL = re.compile(r"^\s*(nil|-|--|–|—|0\.00|0)\s*$", re.IGNORECASE)
NUMERIC = re.compile(r"^\s*\(?\s*[\d,]+\.?\d*\s*\)?\s*$")


@dataclass
class Report:
    name: str
    pages: int = 0
    units: str = "?"
    note_units: str = ""
    unreadable: str = ""
    msmed_pages: list[int] = field(default_factory=list)
    accrued_label_found: bool = False
    accrued_values: list[str] = field(default_factory=list)
    any_interest_label: bool = False
    principal_found: bool = False
    caro_six_months: bool = False
    caro_asserts_none: bool = False


def values_after(lines: list[str], index: int, limit: int = 4) -> list[str]:
    """The next few standalone numeric or nil tokens after a label line.

    Annual report tables extract as a label followed by its column values on
    their own lines, so this is how a figure is recovered from flat text.
    """
    out: list[str] = []
    for line in lines[index + 1 : index + 1 + limit + 6]:
        s = line.strip()
        if not s:
            continue
        if NIL.match(s):
            out.append("nil")
        elif NUMERIC.match(s):
            out.append(s)
        else:
            # Hit the next label. Stop unless nothing was found yet.
            if out:
                break
            continue
        if len(out) >= limit:
            break
    return out


def survey_one(path: Path, verbose: bool = False) -> Report:
    import fitz

    rep = Report(name=path.name)
    with fitz.open(path) as doc:
        rep.pages = len(doc)
        for page_no, page in enumerate(doc, start=1):
            text = page.get_text()

            if PORTFOLIO.search(text):
                rep.unreadable = "PDF Portfolio, real document is embedded"
                return rep

            if rep.units == "?":
                m = UNITS.search(text)
                if m:
                    rep.units = m.group(1).lower().rstrip("s")

            if CARO_SIX_MONTHS.search(text):
                rep.caro_six_months = True
                if CARO_NO_ARREARS.search(text):
                    rep.caro_asserts_none = True

            if not MSMED_NOTE.search(text):
                continue
            rep.msmed_pages.append(page_no)

            # The scale governing this figure, read from this page and nowhere
            # else. A unit taken from a different page is a guess, and a wrong
            # guess here is a hundredfold error.
            if not rep.note_units:
                m = UNITS.search(text)
                rep.note_units = m.group(1).lower().rstrip("s") if m else ""

            lines = text.splitlines()
            if PRINCIPAL.search(text):
                rep.principal_found = True
            if INTEREST_ANY.search(text):
                rep.any_interest_label = True

            for i, line in enumerate(lines):
                if INTEREST_ACCRUED.search(line):
                    rep.accrued_label_found = True
                    vals = values_after(lines, i)
                    if vals and not rep.accrued_values:
                        rep.accrued_values = vals
                    if verbose:
                        print("    [{p}] {l}".format(p=page_no, l=line.strip()[:110]))
                        print("        -> {v}".format(v=vals))
    return rep


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="directory of annual report PDFs")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    pdfs = sorted(Path(args.directory).glob("*.pdf"))
    if not pdfs:
        sys.exit("No PDFs in {d}".format(d=args.directory))

    reports: list[Report] = []
    for p in pdfs:
        if args.verbose:
            print("== {n} ==".format(n=p.name))
        reports.append(survey_one(p, verbose=args.verbose))

    print()
    header = "{:24} {:>5} {:>8} {:>6} {:>13} {:>6} {:>5}".format(
        "report", "pages", "doc unit", "msmed", "accrued value", "unit?", "caro"
    )
    print(header)
    print("-" * len(header))
    for r in reports:
        short = r.name.replace("-fy2026.pdf", "")[:24]
        if r.unreadable:
            print("{:24} {:>5} {}".format(short, r.pages, "UNREADABLE: " + r.unreadable))
            continue
        print(
            "{:24} {:>5} {:>8} {:>6} {:>13} {:>6} {:>5}".format(
                short,
                r.pages,
                r.units,
                len(r.msmed_pages),
                ",".join(r.accrued_values[:2]) or "-",
                r.note_units or "NONE",
                "nil" if r.caro_asserts_none else ("amt" if r.caro_six_months else "-"),
            )
        )

    n = len(reports)
    readable = [r for r in reports if not r.unreadable]
    with_value = [r for r in readable if r.accrued_values]
    nils = [r for r in with_value if r.accrued_values[0] == "nil"]
    unit_on_page = [r for r in with_value if r.note_units]
    unit_mismatch = [
        r
        for r in unit_on_page
        if r.units != "?" and r.note_units.rstrip("s") != r.units.rstrip("s")
    ]

    print()
    print("{n} reports surveyed, {r} readable".format(n=n, r=len(readable)))
    print(
        "  MSMED note located:              {k}/{n}".format(
            k=sum(1 for r in readable if r.msmed_pages), n=len(readable)
        )
    )
    print(
        "  interest line found and parsed:  {k}/{n}".format(
            k=len(with_value), n=len(readable)
        )
    )
    print(
        "  of those, interest is nil:       {k}/{n}  <- H01 stays silent".format(
            k=len(nils), n=len(with_value)
        )
    )
    print(
        "  unit declared on the note page:  {k}/{n}  <- the rest cannot be sized".format(
            k=len(unit_on_page), n=len(with_value)
        )
    )
    print(
        "  note unit differs from doc unit: {k}  <- a 100x error if taken from the document".format(
            k=len(unit_mismatch)
        )
    )
    caro = [r for r in readable if r.caro_six_months]
    print(
        "  CARO six-month clause found:     {k}/{n}".format(k=len(caro), n=len(readable))
    )
    print(
        "  of those, auditor says none:     {k}/{n}  <- H04 almost never fires".format(
            k=sum(1 for r in caro if r.caro_asserts_none), n=len(caro)
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
