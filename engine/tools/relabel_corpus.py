"""Rename reports that were downloaded under a rate-limit page's name.

    python -I tools/relabel_corpus.py --dry-run
    python -I tools/relabel_corpus.py

The first discovery run paced at 0.8s and tripped screener's rate limit on
2,419 of 4,929 companies. Those pages still carried the correct links for the
correct company - 21 of 21 numeric ids matched the scrip embedded in the URL
they gave, against 363 of 363 on the clean pages - but the heading read "Too
many requests", so every one of them was slugged `too-many-requests-N` and the
downloaded file took that name.

The files are real reports for known companies. Only the names are wrong. The
repair discovery pass recovers the proper company name per id, and this maps
each downloaded file back to its id through corpus/fetched.jsonl, which records
the scrip it was fetched for, then renames it.

Renaming rather than re-downloading matters: roughly 1,164 files at the 13 MB
mean is about 15 GB, and BSE does not need to serve that twice because of a
mistake made here.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "corpus"
PDF_DIR = ROOT / "pdfs"
FETCHED = ROOT / "fetched.jsonl"
LEDGER = ROOT / "discovered.jsonl"
RENAMES = ROOT / "relabelled.jsonl"

THROTTLED_SLUG = re.compile(r"^too-many-requests(-\d+)?$")
THROTTLED_NAME = re.compile(r"too\s+many\s+requests", re.I)


def latest_by_id(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            r = json.loads(line)
            out[r["id"]] = r
        except (ValueError, KeyError):
            continue
    return out


def fetched_rows() -> list[dict]:
    out: list[dict] = []
    if not FETCHED.exists():
        return out
    for line in FETCHED.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    ledger = latest_by_id(LEDGER)
    rows = fetched_rows()
    if not rows:
        print("no download ledger at {p}".format(p=FETCHED))
        return 1

    misnamed = [r for r in rows if THROTTLED_SLUG.match(r.get("slug", ""))]
    print("{n} downloaded files carry a rate-limit page's name".format(n=len(misnamed)))

    renamed = skipped = missing = unresolved = 0
    taken: set[str] = {p.stem for p in PDF_DIR.glob("*.pdf")}

    for r in misnamed:
        cid = str(r.get("scrip") or "")
        src = PDF_DIR / "{s}.pdf".format(s=r["slug"])
        if not src.exists():
            missing += 1
            continue

        rec = ledger.get(cid)
        if rec is None or not rec.get("slug") or THROTTLED_NAME.search(rec.get("name") or ""):
            # The repair pass has not reached this company yet, or it is still
            # throttled. Leave the file alone rather than invent a name.
            unresolved += 1
            continue

        want = rec["slug"]
        if want == r["slug"]:
            skipped += 1
            continue
        # The URL is the identity here, so a name collision on a different
        # company gets a suffix rather than overwriting someone else's report.
        final = want
        n = 1
        while final in taken and final != r["slug"]:
            n += 1
            final = "{w}-{n}".format(w=want, n=n)

        dest = PDF_DIR / "{s}.pdf".format(s=final)
        print("  {a}  ->  {b}   ({name})".format(
            a=r["slug"], b=final, name=(rec.get("name") or "")[:40]))
        if not args.dry_run:
            src.replace(dest)
            taken.discard(r["slug"])
            taken.add(final)
            with RENAMES.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "scrip": cid, "from": r["slug"], "to": final,
                    "name": rec.get("name", ""), "url": r.get("url", ""),
                    "sha256": r.get("sha256", ""),
                }) + "\n")
        renamed += 1

    print()
    print("{v}{r} renamed, {u} not yet resolved, {m} file missing, {s} already correct".format(
        v="would rename: " if args.dry_run else "", r=renamed, u=unresolved, m=missing, s=skipped))
    if args.dry_run:
        print("nothing was moved. Run without --dry-run to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
