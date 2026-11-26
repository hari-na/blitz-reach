"""Command line entry point.

    python -m grounds.cli screen data/companies
    python -m grounds.cli brief data/companies/example.yaml
    python -m grounds.cli brief data/companies/example.yaml --prose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from grounds.loader import load_all, load_company
from grounds.render import render, render_capacity, render_table
from grounds.verdict import assess


def _assess_file(path: Path):
    cf = load_company(path)
    return cf, _assess_company(cf)


def _assess_company(cf):
    return assess(
        cf.signals,
        company=cf.company,
        fiscal_year=cf.fiscal_year,
        capture=cf.capture,
        slug=cf.path.stem,
    )


def cmd_screen(args: argparse.Namespace) -> int:
    files = load_all(args.directory)
    if not files:
        print("No company files found in {d}".format(d=args.directory))
        return 1

    assessments = [_assess_company(cf) for cf in files]

    if args.capacity:
        print(render_capacity(assessments, args.capacity))
        return 0

    print(render_table(assessments))
    print()

    counts: dict[str, int] = {}
    for a in assessments:
        counts[a.verdict] = counts.get(a.verdict, 0) + 1

    total = len(assessments)
    actionable = counts.get("actionable", 0)
    print(
        "{total} screened. {act} actionable, {thin} thin, {abst} abstain. "
        "{pct:.0f}% refused.".format(
            total=total,
            act=actionable,
            thin=counts.get("thin", 0),
            abst=counts.get("abstain", 0),
            pct=100 * (total - actionable) / total,
        )
    )
    return 0


def cmd_brief(args: argparse.Namespace) -> int:
    cf, assessment = _assess_file(Path(args.path))

    prose = ""
    if args.prose:
        from grounds.compose import compose_opening

        prose = compose_opening(assessment, mode=args.prose_mode, take=args.take)

    out = render(assessment, prose=prose)

    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print("Wrote {p}".format(p=args.out))
    else:
        print(out)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="grounds",
        description="Evidence-bound account briefs. Refuses more than it reports.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_screen = sub.add_parser("screen", help="one row per company, verdict first")
    p_screen.add_argument("directory", help="directory of company YAML files")
    p_screen.add_argument(
        "--capacity",
        type=int,
        help=(
            "how many companies you can actually work this month. Returns that many, "
            "in order, and says plainly when there are fewer worth the slots."
        ),
    )
    p_screen.set_defaults(func=cmd_screen)

    p_brief = sub.add_parser("brief", help="full brief for one company")
    p_brief.add_argument("path", help="company YAML file")
    p_brief.add_argument(
        "--prose",
        action="store_true",
        help="add a written opening. Works with no API key: falls back to a recorded take.",
    )
    p_brief.add_argument(
        "--prose-mode",
        choices=("auto", "live", "replay", "off"),
        default="auto",
        help=(
            "auto (default): live if ANTHROPIC_API_KEY is set, else replay a recorded "
            "take. live: call the model. replay: use a recorded take. off: deterministic."
        ),
    )
    p_brief.add_argument(
        "--take",
        default="accepted",
        help=(
            "which recorded take to replay. 'rejected' is a deliberately bad draft, "
            "kept so the number guard can be watched catching one."
        ),
    )
    p_brief.add_argument("--out", help="write markdown to this path instead of stdout")
    p_brief.set_defaults(func=cmd_brief)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
