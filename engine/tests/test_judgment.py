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
from grounds.loader import load_all, load_company  # noqa: E402
from grounds.provenance import (  # noqa: E402
    ProvenanceError,
    ScaleError,
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


def test_a_scale_error_cannot_be_captured() -> None:
    """The India Cements trap, made impossible.

    Its MSMED note is denominated in lakhs while the first scale declared in the
    document says crore. A survey of ten FY2025-26 reports found the scale
    stated on the note's own page in only six of nine readable ones, so anyone
    automating this will be tempted to take it from the document. That is a
    hundredfold error. Recording the printed figure and its scale makes the
    conversion checkable, and a mismatch raises instead of screening.
    """
    # 123.34 lakhs is the real figure: Rs 12,334,000.
    ok = Signal(
        key="mse_interest_accrued_unpaid",
        value=12_334_000,
        unit="INR",
        kind="money",
        source=GOOD_SOURCE,
        as_filed="123.34",
        filed_unit="lakh",
    )
    assert ok.num == 12_334_000

    # The same value labelled crore is the mistake. It must not be constructible.
    try:
        Signal(
            key="mse_interest_accrued_unpaid",
            value=12_334_000,
            unit="INR",
            kind="money",
            source=GOOD_SOURCE,
            as_filed="123.34",
            filed_unit="crore",
        )
    except ScaleError as exc:
        assert "does not reconcile" in str(exc), str(exc)
    else:
        raise AssertionError("a hundredfold scale error was accepted")

    # Half a provenance record is not a provenance record.
    try:
        Signal(
            key="revenue",
            value=1.0,
            unit="INR",
            kind="money",
            source=GOOD_SOURCE,
            as_filed="123.34",
        )
    except ProvenanceError:
        pass
    else:
        raise AssertionError("as_filed without filed_unit was accepted")


def test_every_real_capture_reconciles_to_its_printed_figure() -> None:
    """Not a unit test. A standing audit of the three hand captures."""
    for name in ("india-cements.yaml", "lmw.yaml", "seshasayee-paper.yaml"):
        cf = load_company(FIXTURES / name)
        checked = 0
        for key in cf.signals.keys():
            sig = cf.signals.get(key)
            assert sig is not None
            if sig.as_filed:
                checked += 1  # construction already verified the arithmetic
        assert checked >= 4, "{n} records only {c} checkable figures".format(
            n=name, c=checked
        )


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
    found = {f.hypothesis_id: f for f in a.material}
    assert "H03" in found, list(found)
    h03 = found["H03"]

    gst_slice = 1_904_811_038
    expected = gst_slice * 0.18
    assert abs(h03.magnitude - expected) < 1.0, h03.magnitude
    # Sized off the grand total this would be more than four times larger.
    assert h03.magnitude < 9_302_553_773 * 0.18 / 4, h03.magnitude
    # And the brief has to admit what it left out.
    assert "pre-GST" in h03.mechanism, h03.mechanism
    assert a.share(h03) >= 0.005, a.share(h03)


def test_a_real_finding_is_vetoed_when_the_company_cannot_act() -> None:
    """India Cements is the case that justifies a second signal source.

    H03 fires on filed evidence at 0.765% of revenue, well past the lead floor.
    And Crisil revised the company to BB/Stable Issuer Not Cooperating in March
    2023, then withdrew its ratings at the company's own request, after chasing
    it by letter on four dates and receiving nothing. A company that stops
    answering its own rating agency will not answer an outbound approach about
    its accounts payable, so the approach is wasted either way.

    The verdict must flip to abstain, the finding must stay visible so a reader
    sees both halves, and the reason must cite the rating document.
    """
    a = _assess("india-cements.yaml")
    assert a.verdict == "abstain", a.verdict
    assert a.lead is None, a.lead
    assert a.material, "the finding must still be reported"
    assert len(a.vetoes) == 3, [v.qualifier_id for v in a.vetoes]
    assert {v.qualifier_id for v in a.vetoes} == {"Q01", "Q02", "Q03"}
    assert all("crisil" in v.citation.lower() for v in a.vetoes), a.vetoes
    assert "should still not be approached" in a.reason, a.reason


def test_a_qualifier_never_invents_a_finding() -> None:
    """Qualifiers only subtract. A company with no rating data is unaffected."""
    for name in ("lmw.yaml", "seshasayee-paper.yaml"):
        a = _assess(name)
        assert a.vetoes == (), (name, a.vetoes)


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


def test_capacity_view_leaves_slots_empty_rather_than_padding() -> None:
    """The prioritiser has to be able to say there is no second company.

    An FDE team with N slots does not want a list of length N. It wants the
    companies worth a slot, which may be fewer. A tool that always returns N is
    a lead generator with a different label, and it reproduces the problem it
    was built to fix: a pipeline full of companies nobody can name a reason for.
    """
    from grounds.render import render_capacity

    files = load_all(FIXTURES)
    assessments = [
        assess(
            cf.signals,
            company=cf.company,
            fiscal_year=cf.fiscal_year,
            capture=cf.capture,
            slug=cf.path.stem,
        )
        for cf in files
    ]
    qualified = [a for a in assessments if a.lead is not None]
    assert qualified, "fixtures must include at least one actionable company"

    out = render_capacity(assessments, capacity=len(qualified) + 2)
    assert "2 slots unfilled" in out, out[:400]
    assert "The constraint is not people. It is evidence." in out

    # Everything without a lead has to appear with a stated reason, not vanish.
    for a in assessments:
        if a.lead is None:
            assert a.company in out, a.company

    # And a smaller capacity must not promote an unqualified company.
    tight = render_capacity(assessments, capacity=1)
    assert "slots unfilled" not in tight, tight[:400]
    for a in assessments:
        if a.lead is None:
            assert "1. **{c}**".format(c=a.company) not in tight


def test_the_prior_year_is_scale_checked_as_well() -> None:
    """A trend is only worth having if last year's figure is as guarded as this year's."""
    ok = Signal(
        key="msme_sourcing_share",
        value=0.59,
        unit="share",
        kind="ratio",
        source=GOOD_SOURCE,
        as_filed="59",
        filed_unit="percent",
        prior_value=0.51,
        prior_as_filed="51",
    )
    assert ok.direction() == "rising", ok.direction()
    assert ok.change_ratio is not None and ok.change_ratio > 0.15

    try:
        Signal(
            key="msme_sourcing_share",
            value=0.59,
            unit="share",
            kind="ratio",
            source=GOOD_SOURCE,
            as_filed="59",
            filed_unit="percent",
            prior_value=51.0,  # forgot to scale the prior year
            prior_as_filed="51",
        )
    except ScaleError:
        pass
    else:
        raise AssertionError("an unscaled prior year was accepted")


def test_a_context_never_changes_a_verdict() -> None:
    """Contexts carry no magnitude and must not leak into the decision.

    Seshasayee carries both contexts. Stripping them has to leave the verdict,
    the lead and the findings exactly as they were, or a fact with no money
    figure has started deciding who gets called.
    """
    cf = load_company(FIXTURES / "seshasayee-paper.yaml")
    with_ctx = assess(
        cf.signals, company=cf.company, fiscal_year=cf.fiscal_year, capture=cf.capture
    )
    assert with_ctx.contexts, "fixture should carry contexts"

    stripped = SignalSet(
        cf.signals.get(k)  # type: ignore[misc]
        for k in cf.signals.keys()
        if k not in ("msme_sourcing_share", "subsidiary_count")
    )
    without = assess(
        stripped, company=cf.company, fiscal_year=cf.fiscal_year, capture=cf.capture
    )
    assert without.contexts == ()
    assert with_ctx.verdict == without.verdict, (with_ctx.verdict, without.verdict)
    assert with_ctx.lead == without.lead
    assert len(with_ctx.material) == len(without.material)


def test_exposure_says_when_a_silence_means_nothing() -> None:
    """The point of C01: H01's nil is only evidence if there was exposure.

    Seshasayee buys 59% of its inputs from small suppliers and reports nil
    interest, so the nil is real discipline. At a low enough share the same nil
    would be an artifact, and the brief has to say so rather than let a reader
    treat the company as cleared.
    """
    from grounds.contexts import MSME_RELEVANCE_FLOOR, small_supplier_exposure

    high = _assess("seshasayee-paper.yaml")
    c01 = next(c for c in high.contexts if c.context_id == "C01")
    assert "59.00%" in c01.statement, c01.statement
    assert "51.00% last year" in c01.statement, c01.statement
    assert "not evidence of discipline" not in c01.bearing

    thin_exposure = SignalSet(
        [
            Signal(
                key="msme_sourcing_share",
                value=0.0269,
                unit="share",
                kind="ratio",
                source=GOOD_SOURCE,
                as_filed="2.69",
                filed_unit="percent",
            )
        ]
    )
    low = small_supplier_exposure(thin_exposure)
    assert low is not None
    assert "not evidence of discipline" in low.bearing, low.bearing
    assert MSME_RELEVANCE_FLOOR == 0.05


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
