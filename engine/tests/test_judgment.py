"""Tests for the decisions, not the plumbing.

Each test below pins a judgment the engine has to get right. Three of them pin a
refusal, because refusing is the behavior that makes the output worth reading and
the behavior most likely to erode as hypotheses get added.

Run: python -m pytest tests -q   (or: python tests/test_judgment.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from grounds.compose import check_no_new_numbers, compose  # noqa: E402
from grounds.loader import load_company  # noqa: E402
from grounds.provenance import (  # noqa: E402
    ProvenanceError,
    Signal,
    SignalSet,
    Source,
)
from grounds.verdict import assess  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[1] / "data" / "companies"

GOOD_SOURCE = Source(
    doc_type="annual_report",
    title="Test Co Annual Report",
    year="FY2025",
    locator="Note 1, page 1",
)


def _assess(name: str):
    cf = load_company(FIXTURES / name)
    return assess(
        cf.signals,
        company=cf.company,
        fiscal_year=cf.fiscal_year,
        capture=cf.capture,
        slug=cf.path.stem,
    )


def test_signal_cannot_exist_without_a_citation() -> None:
    """The reliability claim is structural, so it is enforced at construction."""
    try:
        Signal(key="revenue", value=1.0, unit="INR", kind="money", source=None)  # type: ignore[arg-type]
    except ProvenanceError:
        pass
    else:
        raise AssertionError("a Signal with no Source was constructed")

    try:
        Source(doc_type="annual_report", title="X", year="FY2025", locator="")
    except ProvenanceError:
        pass
    else:
        raise AssertionError("a Source with no locator was constructed")


def test_immaterial_findings_do_not_produce_a_brief() -> None:
    """Interview 02. Real filed numbers, correctly judged not worth anyone's time."""
    a = _assess("nilgiri-textiles.yaml")
    assert a.verdict == "abstain", a.verdict
    assert a.lead is None
    assert len(a.discarded) == 2, a.discarded
    assert "materiality floor" in a.reason


def test_no_revenue_means_abstain_before_anything_runs() -> None:
    """No denominator, no materiality test, so no claim about a named company."""
    a = _assess("vaigai-paper.yaml")
    assert a.verdict == "abstain", a.verdict
    assert a.lead is None
    assert not a.discarded and not a.skipped
    assert "No revenue figure" in a.reason


def test_material_but_not_enough_comes_out_thin() -> None:
    """Two findings clear materiality and neither earns an approach.

    H03 is medium confidence but only 0.33% of revenue, under the 0.5% lead
    floor. H05 clears materiality and is hard-capped at low confidence, so it
    can never lead however little else is on the page. Both facts have to hold
    at once or an engine with nothing good to say starts promoting its weakest
    signal, which is the failure mode of every tool in this category.
    """
    a = _assess("palani-sugars.yaml")
    assert a.verdict == "thin", a.verdict
    assert a.lead is None, a.lead
    assert [f.hypothesis_id for f in a.supporting] == ["H03", "H05"], a.supporting

    by_id = {f.hypothesis_id: f for f in a.supporting}
    assert by_id["H03"].confidence == "medium", by_id["H03"].confidence
    assert a.share(by_id["H03"]) < 0.005, a.share(by_id["H03"])
    assert by_id["H05"].confidence == "low", by_id["H05"].confidence
    assert a.share(by_id["H05"]) >= 0.001, a.share(by_id["H05"])


def test_filed_and_material_leads_with_its_arithmetic() -> None:
    a = _assess("kaveri-cements.yaml")
    assert a.verdict == "actionable", a.verdict
    assert a.lead is not None
    assert a.lead.confidence == "high"
    assert a.share(a.lead) >= 0.005
    # A lead with no sources, or arithmetic that cannot be written out, is not a lead.
    assert a.lead.sources()
    assert a.lead.derivation.substituted
    assert a.lead.kills_if


def test_ranking_prefers_confidence_over_size() -> None:
    """A bigger number on weaker evidence must not outrank a smaller filed one."""
    a = _assess("kaveri-cements.yaml")
    order = [f.confidence for f in a.material]
    ranks = {"high": 3, "medium": 2, "low": 1}
    assert order == sorted(order, key=lambda c: -ranks[c]), order


def test_nil_filed_interest_means_say_nothing() -> None:
    """LMW Limited, real filing, and the best test in this suite.

    Every interest line in its MSMED note is nil, which is an audited statement
    that it pays micro and small suppliers inside the appointed day. Its
    principal balance is Rs 75.52 crore, and an engine that sized off that
    balance would announce a problem at a company whose own auditors say there
    isn't one. The first version of H01 did exactly that. This pins the fix.
    """
    a = _assess("lmw.yaml")
    assert a.verdict == "abstain", a.verdict
    assert a.lead is None, a.lead
    assert "mse_principal_outstanding" in a.signals_present, a.signals_present
    fired = [f.hypothesis_id for f in a.material] + [
        d.finding.hypothesis_id for d in a.discarded
    ]
    assert "H01" not in fired, fired


def test_disputed_dues_are_sized_on_the_gst_slice_only() -> None:
    """The India Cements Limited, real filing.

    Its disputed-dues annexure totals Rs 930.26 crore, most of it excise and
    sales tax litigation running from 1995-96 and sitting at the Supreme Court,
    plus Rs 438.62 crore of electricity, stamp duty and mining cases. Thirty
    years of tax law under appeal is not a reconciliation failure. H03 takes the
    GST slice, Rs 190.48 crore, and the test fails if anyone widens it back.
    """
    a = _assess("india-cements.yaml")
    assert a.verdict == "actionable", a.verdict
    assert a.lead is not None and a.lead.hypothesis_id == "H03", a.lead

    gst_slice = 1_904_811_038
    expected = gst_slice * 0.18
    assert abs(a.lead.magnitude - expected) < 1.0, a.lead.magnitude
    # Sized off the grand total this would be more than four times larger.
    assert a.lead.magnitude < 9_302_553_773 * 0.18 / 4, a.lead.magnitude
    # And the brief has to admit what it left out.
    assert "pre-GST" in a.lead.mechanism, a.lead.mechanism


def test_real_interest_that_was_actually_paid_is_still_immaterial() -> None:
    """India Cements paid Rs 1.41 crore of MSMED penal interest. It does not matter.

    H01 fires on real filed evidence of habitual late payment, and the
    materiality floor throws it out at 0.059% of revenue. Both halves have to
    work: detecting it, and then declining to lead with it.
    """
    a = _assess("india-cements.yaml")
    discarded = {d.finding.hypothesis_id: d for d in a.discarded}
    assert "H01" in discarded, list(discarded)
    assert discarded["H01"].share < 0.001, discarded["H01"].share


def test_a_half_finished_capture_says_so() -> None:
    """Seshasayee's CARO and disputed-dues figures were never captured.

    The brief must abstain and name the missing signals rather than quietly
    scoring the company on the two hypotheses that happened to have data.
    """
    a = _assess("seshasayee-paper.yaml")
    assert a.verdict == "abstain", a.verdict
    assert len(a.skipped) == 4, a.skipped
    needed = {m for s in a.skipped for m in s.missing}
    assert "disputed_gst_dues" in needed, needed
    assert "undisputed_statutory_dues_over_6m" in needed, needed


def test_composer_rejects_invented_numbers() -> None:
    facts = "Amount at stake per year: Rs 47.50 cr\nShare of revenue: 1.131%"
    assert check_no_new_numbers("Rs 47.50 cr, which is 1.131% of revenue.", facts) == ""
    problem = check_no_new_numbers("This is costing them Rs 92.40 cr a year.", facts)
    assert "92.40" in problem, problem


def test_a_clean_recorded_draft_survives_the_guard() -> None:
    """The whole project has to run with no API key, so this path is load-bearing."""
    a = _assess("kaveri-cements.yaml")
    prose = compose(a, mode="replay", take="accepted")
    assert prose.origin == "replay", prose.origin
    assert "47.50" in prose.opening, prose.opening
    assert "Replayed take" in prose.note, prose.note


def test_a_dirty_recorded_draft_is_caught_and_replaced() -> None:
    """The rejected take invents a total and a share of revenue. Both must be named."""
    a = _assess("kaveri-cements.yaml")
    prose = compose(a, mode="replay", take="rejected")
    assert prose.origin == "deterministic", prose.origin
    assert "number guard" in prose.note, prose.note
    assert "126.00" in prose.note and "3.2" in prose.note, prose.note
    # The invented figures must not reach the reader at all.
    assert "126.00" not in prose.opening and "3.2%" not in prose.opening


def test_composing_without_a_lead_is_refused() -> None:
    a = _assess("nilgiri-textiles.yaml")
    assert a.lead is None
    try:
        compose(a)
    except ValueError:
        pass
    else:
        raise AssertionError("composed prose for a company we decided to say nothing to")


def test_hypotheses_that_cannot_run_are_reported_not_hidden() -> None:
    sigs = SignalSet(
        [
            Signal(
                key="revenue",
                value=1_000_000_000,
                unit="INR",
                kind="money",
                source=GOOD_SOURCE,
            )
        ]
    )
    a = assess(sigs, company="Bare Co", fiscal_year="FY2025", capture="synthetic")
    assert a.verdict == "abstain"
    assert len(a.skipped) == 5, a.skipped


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS  {n}".format(n=name))
            except AssertionError as exc:
                failures += 1
                print("FAIL  {n}: {e}".format(n=name, e=exc))
    print()
    print("{n} failed".format(n=failures) if failures else "all passed")
    sys.exit(1 if failures else 0)
