"""Run the extractor over the whole corpus and report base rates.

    python -I tools/corpus_stats.py ../corpus/pdfs
    python -I tools/corpus_stats.py ../corpus/pdfs --limit 300

Writes corpus/stats.json and prints a summary. The point is not the briefs, it
is the denominators: how often a disclosure is present at all, and how often it
reports anything. A clause the law requires is present almost always and says
nothing almost always, and that ratio is the finding.

Reports what it could not read separately from what it read and found empty.
Those are different claims and conflating them is the one thing this engine
exists not to do.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from grounds.extract import Extracted, extract  # noqa: E402

ROOT = Path(__file__).resolve().parents[2] / "corpus"
OUT = ROOT / "stats.json"
PROGRESS = ROOT / "stats-progress.json"

MONEY_FIELDS = (
    "mse_interest_accrued_unpaid",
    "mse_interest_paid_during_year",
    "mse_principal_outstanding",
    "disputed_gst_dues",
    "related_party_trade_value",
    "undisputed_statutory_dues_over_6m",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", nargs="?", default=str(ROOT / "pdfs"))
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    pdfs = sorted(Path(args.target).glob("*.pdf"))
    if args.limit:
        pdfs = pdfs[: args.limit]
    n = len(pdfs)
    if not n:
        print("no PDFs at {t}".format(t=args.target))
        return 1

    present = collections.Counter()   # field was captured at all
    nonzero = collections.Counter()   # captured and not a filed zero
    zero = collections.Counter()      # captured as an explicit filed nil
    refusals = collections.Counter()  # per field, why not
    unreadable = 0
    nothing = 0
    years = collections.Counter()
    t0 = time.monotonic()

    for i, p in enumerate(pdfs, 1):
        try:
            d = extract(p)
        except Exception as exc:  # a corrupt download must not stop the run
            unreadable += 1
            refusals["*unreadable*"] += 1
            continue
        if d.pages <= 2:
            unreadable += 1
            continue
        years[d.fiscal_year or "?"] += 1
        got = {e.key: e for e in d.found}
        if not got:
            nothing += 1
        for k, e in got.items():
            present[k] += 1
            (zero if e.value == 0 else nonzero)[k] += 1
        for r in d.refused:
            refusals[r.key] += 1

        if i % 100 == 0 or i == n:
            el = time.monotonic() - t0
            PROGRESS.write_text(
                json.dumps(
                    {
                        "done": i, "total": n,
                        "percent": round(i / n * 100, 1),
                        "seconds": round(el, 1),
                        "eta_seconds": round((n - i) * el / i, 1),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    el = time.monotonic() - t0
    stats = {
        "reports": n,
        "seconds": round(el, 1),
        "unreadable": unreadable,
        "nothing_captured": nothing,
        "fiscal_years": dict(years.most_common(10)),
        "present": dict(present),
        "nonzero": dict(nonzero),
        "filed_zero": dict(zero),
        "refusals": dict(refusals.most_common(20)),
    }
    OUT.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print("{n} reports in {s:.0f}s ({r:.2f}s each)".format(n=n, s=el, r=el / n))
    print("unreadable {u}   nothing captured {z}\n".format(u=unreadable, z=nothing))
    print("{f:38}{p:>9}{nz:>9}{zz:>9}".format(f="field", p="present", nz="nonzero", zz="filed 0"))
    for k, c in present.most_common():
        print(
            "  {k:36}{c:9}{nz:9}{zz:9}   {pc:3.0f}% present".format(
                k=k, c=c, nz=nonzero[k], zz=zero[k], pc=c / n * 100
            )
        )
    print("\nwritten to {p}".format(p=OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
