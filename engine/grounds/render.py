"""Render an assessment as markdown. No model involved.

Every number printed here came out of a hypothesis, which got it from a Signal,
which cannot exist without a citation. The arithmetic is printed as a formula
and then again with the numbers substituted, so a reader can redo it by hand
against the filing and does not have to take the engine's word for anything.
"""

from __future__ import annotations

from grounds.fmt import inr, pct
from grounds.hypotheses import Finding
from grounds.materiality import LEAD_FLOOR, QUICKLIME_FLOOR
from grounds.verdict import Assessment

VERDICT_LINE = {
    "actionable": "ACTIONABLE - there is a filed, sized problem worth opening with",
    "thin": "THIN - something fired, nothing worth a conversation yet",
    "abstain": "ABSTAIN - say nothing to this company",
}

CAPTURE_NOTE = {
    "parsed": "Signals parsed from the source documents.",
    "hand_seeded": "Signals entered by hand from the cited filings, not parsed.",
    "mixed": "Some signals parsed, some entered by hand from the cited filings.",
    "synthetic": (
        "SYNTHETIC FIXTURE. These numbers describe no real company and the cited "
        "documents do not exist. The fixture exercises the engine; it is not evidence."
    ),
    "unknown": "Capture method not recorded.",
}


def _finding_block(finding: Finding, share: float, label: str) -> list[str]:
    d = finding.derivation
    out = [
        "### {label}: {title}".format(label=label, title=finding.title),
        "",
        "`{hid}`  |  confidence **{conf}**  |  **{amount} a year**  |  {share} of revenue".format(
            hid=finding.hypothesis_id,
            conf=finding.confidence,
            amount=inr(finding.magnitude),
            share=pct(share),
        ),
        "",
        finding.mechanism,
        "",
        "**Arithmetic**",
        "",
        "```",
        "{label}".format(label=d.label),
        "  formula      {f}".format(f=d.formula),
        "  substituted  {s}".format(s=d.substituted),
        "  result       {r}".format(r=inr(d.result)),
        "```",
        "",
        "**Ask them this:** {q}".format(q=finding.confirming_question),
        "",
        "**This is wrong if:** {k}".format(k=finding.kills_if),
        "",
        "**Read it yourself**",
        "",
    ]
    for cite in finding.sources():
        out.append("- {cite}".format(cite=cite))
    out.append("")
    return out


def render(assessment: Assessment, prose: str = "") -> str:
    a = assessment
    lines: list[str] = [
        "# {company}".format(company=a.company),
        "",
        "{fy}  |  revenue {rev}  |  {n} signals captured".format(
            fy=a.fiscal_year, rev=inr(a.revenue) if a.revenue else "not captured",
            n=a.signal_count,
        ),
        "",
        "## {verdict}".format(verdict=VERDICT_LINE[a.verdict]),
        "",
        a.reason,
        "",
    ]

    if prose:
        lines += ["---", "", prose.strip(), ""]

    lines.append("---")
    lines.append("")

    if a.lead is not None:
        lines += _finding_block(a.lead, a.share(a.lead), "Lead")

    for i, finding in enumerate(a.supporting, start=1):
        lines += _finding_block(finding, a.share(finding), "Also {i}".format(i=i))

    if a.discarded:
        lines += [
            "## Thrown out below the materiality floor",
            "",
            "Anything worth less than {floor} of revenue is discarded regardless of how "
            "interesting it looks. A finding like this is not a problem found, it is "
            "attention wasted.".format(floor=pct(QUICKLIME_FLOOR, 1)),
            "",
            "| Hypothesis | Finding | Per year | Share of revenue |",
            "|---|---|---|---|",
        ]
        for d in a.discarded:
            lines.append(
                "| `{hid}` | {title} | {amount} | {share} |".format(
                    hid=d.finding.hypothesis_id,
                    title=d.finding.title,
                    amount=inr(d.finding.magnitude),
                    share=pct(d.share),
                )
            )
        lines.append("")

    if a.skipped:
        lines += [
            "## Not tested",
            "",
            "These hypotheses need filings this company has not been captured from. A "
            "reader who knows the company can tell from this table whether the engine "
            "missed something or whether nobody fetched the document.",
            "",
            "| Hypothesis | Needs |",
            "|---|---|",
        ]
        for s in a.skipped:
            lines.append(
                "| `{hid}` {title} | {missing} |".format(
                    hid=s.hypothesis_id,
                    title=s.title,
                    missing=", ".join("`{m}`".format(m=m) for m in s.missing),
                )
            )
        lines.append("")

    lines += [
        "---",
        "",
        "Materiality floor {mf} of revenue, lead floor {lf}. {capture} Every figure above "
        "names the document and the place inside it. Check it rather than believe it.".format(
            mf=pct(QUICKLIME_FLOOR, 1),
            lf=pct(LEAD_FLOOR, 1),
            capture=CAPTURE_NOTE.get(a.capture, CAPTURE_NOTE["unknown"]),
        ),
        "",
    ]

    return "\n".join(lines)


def render_table(assessments: list[Assessment]) -> str:
    """One row per company. This is the screen that does the actual work."""
    rows = [
        "| Company | Verdict | Lead | Per year | Share | Tested | Skipped |",
        "|---|---|---|---|---|---|---|",
    ]
    for a in sorted(assessments, key=lambda x: (x.verdict != "actionable", x.company)):
        lead = a.lead.title if a.lead else "-"
        amount = inr(a.lead.magnitude) if a.lead else "-"
        share = pct(a.share(a.lead)) if a.lead else "-"
        rows.append(
            "| {c} | **{v}** | {lead} | {amt} | {sh} | {t} | {s} |".format(
                c=a.company,
                v=a.verdict,
                lead=lead,
                amt=amount,
                sh=share,
                t=len(a.material) + len(a.discarded),
                s=len(a.skipped),
            )
        )
    return "\n".join(rows)
