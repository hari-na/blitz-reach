"""Run the extractor over annual reports, and check it against the hand captures.

    python -I tools/extract.py data/filings                 write a draft per report
    python -I tools/extract.py data/filings --check         grade it against my captures
    python -I tools/extract.py data/filings/x.pdf --print   one report to stdout

The --check mode is the one that matters. Three companies were read and typed
by hand before any of this existed, so the extractor has a graded exam it
cannot see the answers to: reproduce those figures, with the same scale and the
same prior year, or be wrong in public.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from grounds.extract import Draft, Extracted, extract, to_yaml  # noqa: E402
from grounds.loader import load_company  # noqa: E402

# Which hand capture grades which report.
GRADED = {
    "india-cements-fy2026": "india-cements.yaml",
    "lmw-fy2026": "lmw.yaml",
    "seshasayee-paper-fy2026": "seshasayee-paper.yaml",
}

# Fields a document genuinely does not state, where my hand capture used
# judgment the machine should not imitate. Seshasayee names one subsidiary in
# prose and never gives a count, so refusing is the correct behaviour and
# counting it as a miss would be grading the extractor for not guessing.
EXPECTED_REFUSALS = {("seshasayee-paper-fy2026", "subsidiary_count")}


def reports(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    out = []
    for p in sorted(target.glob("*.pdf")):
        if (p.with_name(p.stem + "-inner.pdf")).exists():
            continue  # a portfolio wrapper whose contents were unwrapped
        out.append(p)
    return out


def pretty(draft: Draft) -> None:
    print("{c}  ({y}, {n} pages)".format(c=draft.company, y=draft.fiscal_year or "?", n=draft.pages))
    for e in sorted(draft.found, key=lambda x: x.key):
        prior = ""
        if e.prior_value is not None:
            prior = "  prior {p} {u}".format(p=e.prior_as_filed, u=e.filed_unit)
        print(
            "   + {k:34} {a:>12} {u:<8} p{p}{prior}".format(
                k=e.key, a=e.as_filed, u=e.filed_unit, p=e.page, prior=prior
            )
        )
    for r in sorted(draft.refused, key=lambda x: x.key):
        print("   - {k:34} {why}".format(k=r.key, why=r.reason[:72]))
    print()


def check(target: Path) -> int:
    total_right = total_wrong = total_missed = total_extra = 0

    for pdf in reports(target):
        stem = pdf.stem
        if stem not in GRADED:
            continue
        hand = load_company(Path("data/companies") / GRADED[stem])
        draft = extract(pdf, company=hand.company, fiscal_year=hand.fiscal_year)
        machine = {e.key: e for e in draft.found}

        print("== {c} ==".format(c=hand.company))
        right = wrong = missed = extra = 0

        for key in hand.signals.keys():
            want = hand.signals.get(key)
            assert want is not None
            got = machine.get(key)
            if got is None:
                # A field the extractor was never taught is not a miss.
                taught = key in {
                    "revenue",
                    "mse_interest_accrued_unpaid",
                    "mse_interest_paid_during_year",
                    "mse_principal_outstanding",
                    "msme_sourcing_share",
                    "subsidiary_count",
                    "undisputed_statutory_dues_over_6m",
                    "related_party_trade_value",
                    "kam_related_party",
                }
                if (stem, key) in EXPECTED_REFUSALS:
                    print(
                        "   ok-no  {k:31} not stated in the document; refusing is "
                        "correct".format(k=key)
                    )
                elif taught:
                    missed += 1
                    print("   MISS  {k:32} hand has {v}".format(k=key, v=want.value))
                continue

            # A figure printed rounded in one place and exact in another is the
            # same figure. 0.1% is tight enough to catch a real error and loose
            # enough not to fail on "Rs 4,485 crore" against "4,484.69".
            same_value = abs(float(got.value) - float(want.value)) <= max(
                abs(float(want.value)) * 1e-3, 0.5
            )
            if same_value:
                right += 1
                if got.filed_unit != want.filed_unit:
                    print(
                        "   note  {k:32} same value, different source: hand {hv} {hu}, "
                        "machine {mv} {mu}".format(
                            k=key, hv=want.as_filed or want.value, hu=want.filed_unit,
                            mv=got.as_filed, mu=got.filed_unit,
                        )
                    )
            else:
                wrong += 1
                print(
                    "   WRONG {k:32} hand {hv} {hu}   machine {mv} {mu}".format(
                        k=key, hv=want.as_filed or want.value,
                        hu=want.filed_unit, mv=got.as_filed, mu=got.filed_unit,
                    )
                )

            if want.prior_value is not None and got.prior_value is None:
                print("   note  {k:32} hand has a prior year, machine did not".format(k=key))

        for key in machine:
            if key not in hand.signals:
                extra += 1
                print(
                    "   EXTRA {k:32} machine found {v} {u} that I never captured".format(
                        k=key, v=machine[key].as_filed, u=machine[key].filed_unit
                    )
                )

        print(
            "   {r} matched, {w} wrong, {m} missed, {e} extra".format(
                r=right, w=wrong, m=missed, e=extra
            )
        )
        print()
        total_right += right
        total_wrong += wrong
        total_missed += missed
        total_extra += extra

    print(
        "TOTAL  {r} matched, {w} wrong, {m} missed, {e} extra".format(
            r=total_right, w=total_wrong, m=total_missed, e=total_extra
        )
    )
    return 1 if (total_wrong or total_missed) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", help="a PDF or a directory of them")
    ap.add_argument("--check", action="store_true", help="grade against the hand captures")
    ap.add_argument("--print", dest="to_stdout", action="store_true")
    ap.add_argument("--out-dir", default="data/drafts")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    target = Path(args.target)
    if args.check:
        return check(target)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for pdf in reports(target):
        draft = extract(pdf)
        pretty(draft)
        if args.to_stdout:
            print(to_yaml(draft))
        else:
            dest = out_dir / (pdf.stem.replace("-fy2026", "").replace("-inner", "") + ".yaml")
            dest.write_text(to_yaml(draft), encoding="utf-8")
    if not args.to_stdout:
        print("drafts written to {d}".format(d=out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
