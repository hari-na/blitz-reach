"""Find the notes we need inside an annual report PDF.

An Indian annual report runs 200 to 400 pages and the figures this engine wants
live in four or five specific places. This prints the page number and the
surrounding lines for each one, so a capture is a matter of reading five short
excerpts rather than a whole document.

Usage, from the engine directory:

    python -I tools/peek.py data/filings/<file>.pdf
    python -I tools/peek.py data/filings/<file>.pdf --term "appointed day"
    python -I tools/peek.py data/filings/<file>.pdf --page 187
    python -I tools/peek.py data/filings/<file>.pdf --list

Run it with -I. These PDFs are downloaded files and -I stops Python importing
anything that happens to sit next to them.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# What to look for, and why each one matters to a hypothesis.
TERMS: dict[str, str] = {
    "micro and small": "H01, the MSMED disclosure note",
    "appointed day": "H01, principal unpaid past the due date",
    "MSMED": "H01, the statute named directly",
    "undisputed statutory dues": "H04, CARO 2020 clause vii(a)",
    "outstanding for a period of more than six months": "H04, the six-month test",
    "disputed statutory dues": "H03, CARO clause vii(b)",
    "Revenue from operations": "the denominator everything is divided by",
    "Trade payables": "H02",
    "Cost of materials consumed": "H02, the purchases figure",
    "Rupees in lakhs": "units, so the figures are read at the right scale",
    "Rs. in crores": "units",
    "in Lakhs": "units",
}


def extract_pages(path: Path) -> list[str]:
    """Page text, one string per page. PyMuPDF first, pypdf as a fallback."""
    try:
        import fitz  # PyMuPDF

        with fitz.open(path) as doc:
            return [page.get_text() for page in doc]
    except ImportError:
        pass

    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit(
            "Need a PDF reader. Install one of:\n"
            "    pip install pymupdf\n"
            "    pip install pypdf"
        )

    reader = PdfReader(str(path))
    return [(page.extract_text() or "") for page in reader.pages]


def show_hits(pages: list[str], term: str, why: str, context: int = 3) -> int:
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    hits = 0

    for page_no, text in enumerate(pages, start=1):
        if not pattern.search(text):
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if not pattern.search(line):
                continue
            hits += 1
            if hits > 4:
                print("    ... more hits on later pages, narrow with --term")
                return hits
            lo = max(0, i - context)
            hi = min(len(lines), i + context + 1)
            print("    [page {p}]".format(p=page_no))
            for j in range(lo, hi):
                marker = "  >" if j == i else "   "
                print("    {m} {line}".format(m=marker, line=lines[j].rstrip()[:160]))
            print()
    if not hits:
        print("    not found")
        print()
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="path to the annual report PDF")
    parser.add_argument("--term", help="search one phrase instead of the standard set")
    parser.add_argument("--page", type=int, help="dump one page in full (1-indexed)")
    parser.add_argument("--list", action="store_true", help="page count and first page")
    parser.add_argument("--context", type=int, default=3, help="lines either side")
    args = parser.parse_args(argv)

    path = Path(args.pdf)
    if not path.exists():
        sys.exit("No such file: {p}".format(p=path))

    pages = extract_pages(path)
    print("{p}  |  {n} pages".format(p=path.name, n=len(pages)))
    print()

    if args.list:
        print(pages[0][:1500] if pages else "(empty)")
        return 0

    if args.page:
        if not 1 <= args.page <= len(pages):
            sys.exit("Page out of range (1 to {n})".format(n=len(pages)))
        print(pages[args.page - 1])
        return 0

    if args.term:
        print("== {t} ==".format(t=args.term))
        show_hits(pages, args.term, "", context=args.context)
        return 0

    for term, why in TERMS.items():
        print("== {t}  ({w}) ==".format(t=term, w=why))
        show_hits(pages, term, why, context=args.context)

    return 0


if __name__ == "__main__":
    sys.exit(main())
