"""Pull the real annual report out of a PDF Portfolio.

One report in the ten surveyed, Dalmia Bharat's, is published as a PDF
Portfolio: a wrapper whose only page says "open this PDF portfolio in Acrobat",
with the actual document carried as an embedded attachment. Every text extractor
sees the wrapper and reports a one-page file.

OCR is the wrong tool for this. Nothing is scanned; the text is perfectly
intact, just one level down. This unwraps it.

Usage, from the engine directory:

    python -I tools/unwrap.py data/filings
    python -I tools/unwrap.py data/filings/dalmia-bharat-fy2026.pdf

The largest embedded PDF is written beside the original as `<stem>-inner.pdf`.
Largest, because these wrappers typically carry a signed cover letter as well
and the report is the big one.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def unwrap(path: Path) -> Path | None:
    import fitz

    with fitz.open(path) as doc:
        count = doc.embfile_count()
        if count == 0:
            return None

        entries = []
        for i in range(count):
            info = doc.embfile_info(i)
            name = str(info.get("filename", "embedded-{i}".format(i=i)))
            entries.append((int(info.get("length", 0)), i, name))

        pdfs = [e for e in entries if e[2].lower().endswith(".pdf")]
        if not pdfs:
            print("  {n}: {c} attachments, none a PDF".format(n=path.name, c=count))
            return None

        size, index, name = max(pdfs)
        data = doc.embfile_get(index)

    out = path.with_name(path.stem + "-inner.pdf")
    out.write_bytes(data)

    with __import__("fitz").open(out) as inner:
        pages = len(inner)

    print(
        "  {n}: {c} attachments, took {name!r} ({mb:.1f} MB, {p} pages) -> {o}".format(
            n=path.name, c=count, name=name[:50], mb=size / 1e6, p=pages, o=out.name
        )
    )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="a PDF, or a directory of them")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    target = Path(args.target)
    if target.is_dir():
        paths = [
            p for p in sorted(target.glob("*.pdf")) if not p.stem.endswith("-inner")
        ]
    else:
        paths = [target]

    print("Checking {n} file(s) for embedded documents".format(n=len(paths)))
    found = 0
    for p in paths:
        if unwrap(p) is not None:
            found += 1
    print("{n} unwrapped".format(n=found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
