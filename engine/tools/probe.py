"""Test candidate indicators against the whole corpus before building any of them.

Proposing an indicator is free. The question that decides whether one is worth
coding is whether it can actually be found, in consistent wording, across many
reports. The MSMED interest line passed that test at 10 out of 10, which is why
H01 exists. H04 passed too and then turned out to be nil almost every time,
which is a different failure and one only real data shows.

So every candidate below gets probed before anything is built on it.

Usage, from the engine directory:

    python -I tools/probe.py data/filings
    python -I tools/probe.py data/filings --show subsidiaries
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# name -> (what it would tell us, regex)
CANDIDATES: dict[str, tuple[str, str]] = {
    "key_audit_matters": (
        "Where the auditor says the risk is, in their own words",
        r"key\s+audit\s+matter",
    ),
    "kam_payables": (
        "A key audit matter that is specifically about payables or procurement",
        r"key\s+audit\s+matter[\s\S]{0,3000}?(trade\s+payable|procure|vendor)",
    ),
    "kam_revenue": (
        "A key audit matter about revenue recognition",
        r"key\s+audit\s+matter[\s\S]{0,3000}?revenue\s+recognition",
    ),
    "subsidiary_list": (
        "Close complexity: how many entities get consolidated",
        r"(form\s+aoc[\s\-]?1|salient\s+features\s+of\s+the\s+financial\s+statement\s+of\s+subsidiar)",
    ),
    "subsidiary_count_phrase": (
        "A stated count of subsidiaries",
        r"\b(\d{1,3})\s+(?:wholly[\s\-]owned\s+)?subsidiar(?:y|ies)\b",
    ),
    "ifc_adverse": (
        "Internal financial controls reported as weak",
        r"(material\s+weakness|adverse\s+opinion\s+on\s+(?:the\s+)?internal\s+financial)",
    ),
    "emphasis_of_matter": (
        "The auditor flagging something without qualifying the opinion",
        r"emphasis\s+of\s+matter",
    ),
    "brsr_msme_sourcing": (
        "What share of purchases come from small suppliers: H01's population",
        r"(sourced\s+(?:directly\s+)?from\s+MSMEs|input\s+material.{0,40}MSME|MSMEs/\s?small\s+producers)",
    ),
    "employee_count": (
        "Scale proxy: how many people the back office serves",
        r"(total\s+number\s+of\s+employees|permanent\s+employees)",
    ),
    "related_party_value": (
        "Intercompany volume, which is close workload",
        r"related\s+part(?:y|ies)\s+(?:transactions|disclosures)",
    ),
    "secretarial_observations": (
        "A second auditor's view on compliance discipline",
        r"secretarial\s+audit",
    ),
    "penalties": (
        "Fines and penalties actually paid in the year",
        r"(penalt(?:y|ies).{0,60}(?:imposed|levied|paid)|details\s+of\s+penalt)",
    ),
    "doubtful_advances": (
        "Money paid to vendors and then written off",
        r"(advances?\s+(?:to\s+)?(?:vendors?|suppliers?).{0,80}doubtful|provision.{0,40}doubtful\s+advance)",
    ),
    "gst_input_credit": (
        "Input credit reconciliation differences, a direct process failure",
        r"(input\s+tax\s+credit.{0,120}(?:reconcil|mismatch|difference)|GSTR[\s\-]?2[AB])",
    ),
    "plant_locations": (
        "Number of sites feeding the same back office",
        r"(manufacturing\s+(?:units|plants|facilities|locations)|plant\s+locations)",
    ),
}


def load_reports(directory: Path) -> list[tuple[str, list[str]]]:
    import fitz

    out: list[tuple[str, list[str]]] = []
    for p in sorted(directory.glob("*.pdf")):
        # Prefer the unwrapped copy and skip the portfolio wrapper it came from.
        if (p.with_name(p.stem + "-inner.pdf")).exists():
            continue
        with fitz.open(p) as doc:
            if len(doc) <= 2:
                continue
            out.append(
                (p.stem.replace("-fy2026", "").replace("-inner", ""), [pg.get_text() for pg in doc])
            )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory")
    parser.add_argument("--show", help="print sample matches for one candidate")
    parser.add_argument("--context", type=int, default=240)
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    reports = load_reports(Path(args.directory))
    if not reports:
        sys.exit("No readable reports in {d}".format(d=args.directory))
    print("{n} readable reports\n".format(n=len(reports)))

    if args.show:
        if args.show not in CANDIDATES:
            sys.exit("Unknown candidate. Known: {k}".format(k=", ".join(CANDIDATES)))
        _, pattern = CANDIDATES[args.show]
        rx = re.compile(pattern, re.IGNORECASE)
        for name, pages in reports:
            hit = None
            for i, text in enumerate(pages, start=1):
                m = rx.search(text)
                if m:
                    s = max(0, m.start() - 40)
                    hit = (i, " ".join(text[s : m.end() + args.context].split()))
                    break
            print("== {n} ==".format(n=name))
            print("   p{p}: {t}".format(p=hit[0], t=hit[1]) if hit else "   not found")
            print()
        return 0

    width = max(len(k) for k in CANDIDATES) + 2
    print("{:{w}} {:>7}  {}".format("candidate", "found", "missing from", w=width))
    print("-" * (width + 50))

    for name, (why, pattern) in CANDIDATES.items():
        rx = re.compile(pattern, re.IGNORECASE)
        hits, missing = 0, []
        for rname, pages in reports:
            if any(rx.search(t) for t in pages):
                hits += 1
            else:
                missing.append(rname)
        mark = "" if hits == len(reports) else ""
        print(
            "{:{w}} {:>3}/{:<3}  {}".format(
                name,
                hits,
                len(reports),
                ", ".join(m[:12] for m in missing[:4]) + ("..." if len(missing) > 4 else "") or "-",
                w=width,
            )
        )

    print()
    print("What each would tell us:")
    for name, (why, _) in CANDIDATES.items():
        print("  {:{w}} {}".format(name, why, w=width))
    return 0


if __name__ == "__main__":
    sys.exit(main())
