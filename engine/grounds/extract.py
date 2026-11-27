"""Read an annual report and write a capture file, or refuse.

Every figure this produces goes through the same loader as a hand capture, so
the scale guard checks it: a value that does not reconcile with the figure and
scale printed on the page raises rather than screening. That makes the
extractor safe to be wrong in the loud way, and this module's job is to make
sure it is never wrong in the quiet way.

So the rule here is the same one the rest of the engine follows. Where the
scale governing a number cannot be read off the same page, where a label is
ambiguous, or where the number does not parse, the field is **refused** and
named in the output. A capture with four fields and three refusals is useful.
A capture with seven fields, three of them guessed, is poison.

The test that matters is in tools/extract.py --check: the extractor must
reproduce, with no help, the three captures that were read and typed by hand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

NIL = re.compile(r"^\s*\(?\s*(nil|n\.?a\.?|-{1,2}|–|—|0\.00|0)\s*\)?\s*$", re.I)
NUMERIC = re.compile(r"^\s*\(?\s*([\d][\d,]*\.?\d*)\s*\)?\s*%?\s*(?:approx\.?)?\s*$", re.I)

# The scale word, and the cue that marks it as a scale declaration rather than
# prose. The cue list is deliberately loose because the rupee sign extracts as
# a different character in every report depending on the embedded font: a
# backtick in India Cements, "C" and "D" in LMW. Anchoring on the symbol finds
# nothing; anchoring on the word and then looking backwards works.
UNIT_WORD = re.compile(r"\b(lakhs?|crores?|millions?|thousands?)\b", re.I)
# What must sit immediately before a scale word for it to declare this page's
# units, rather than just be a figure in running prose.
#
# Case-insensitive, and that is not cosmetic. Without re.I the in-branch never
# matched a capitalised "In", so "(Rs. In Lakhs)" - an ordinary header - was
# read as declaring no scale at all. Across 60 downloaded reports the revenue
# figure was present and refused 43 times, and this was the larger half of the
# reason. The ten reports read by hand all happened to write "in lakhs" in
# lower case, so the graded exam could never have caught it.
#
# A currency token may also sit between the cue and the scale word, as in
# "(All Amounts in INR Lakhs unless otherwise stated)".
UNIT_CUE = re.compile(
    r"(\bin\b|\bRs\.?|[`₹ ]|\b[A-Z]\b)\s*(?:INR|Rs\.?|[`₹])?\s*$", re.I
)

FY_PATTERNS = (
    re.compile(r"year\s+ended\s+(?:on\s+)?31(?:st)?\s+March,?\s+(\d{4})", re.I),
    re.compile(r"for\s+the\s+year\s+ended\s+31[-/.]0?3[-/.](\d{4})", re.I),
    re.compile(r"annual\s+report\s+20(\d\d)\s*[-–]\s*(\d\d)", re.I),
    re.compile(r"FY\s*20(\d\d)\s*[-–]\s*(\d\d)", re.I),
)


@dataclass(frozen=True)
class Extracted:
    key: str
    kind: str
    value: float
    as_filed: str
    filed_unit: str
    page: int
    label: str
    note: str = ""
    prior_value: float | None = None
    prior_as_filed: str = ""


@dataclass(frozen=True)
class Refused:
    key: str
    reason: str
    page: int | None = None


@dataclass
class Draft:
    company: str
    fiscal_year: str
    source_file: str
    pages: int
    found: list[Extracted] = field(default_factory=list)
    refused: list[Refused] = field(default_factory=list)


# --------------------------------------------------------------------------
# page utilities


def page_unit(text: str) -> str | None:
    """The scale declared on this page, or None. Never falls back to the document."""
    for m in UNIT_WORD.finditer(text):
        before = text[max(0, m.start() - 30) : m.start()]
        if UNIT_CUE.search(before):
            return m.group(1).lower().rstrip("s")
    return None


def _clean(tok: str) -> str:
    return tok.replace(",", "").replace("%", "").replace(")", "").replace("(", "").strip()


def values_after(lines: list[str], index: int, want: int, lookahead: int = 14) -> list[str]:
    """The next `want` standalone numeric-or-nil tokens after a label line.

    A table in extracted PDF text is a label line followed by its column values
    each on their own line. Stops at the next line that is clearly another
    label, so a missing value is reported short rather than silently filled
    from the row below.
    """
    out: list[str] = []
    for raw in lines[index + 1 : index + 1 + lookahead]:
        s = raw.strip()
        if not s:
            continue
        if NIL.match(s):
            out.append("0")
        else:
            m = NUMERIC.match(s)
            if m:
                out.append(_clean(m.group(1)))
            elif out:
                break  # hit the next label after collecting something
            else:
                continue  # wrapped label text, keep looking
        if len(out) >= want:
            break
    return out


# --------------------------------------------------------------------------
# field definitions


@dataclass(frozen=True)
class TableField:
    """A row in a table: a label, then its current and prior year values."""

    key: str
    kind: str
    label: re.Pattern[str]
    page_guard: re.Pattern[str] | None = None
    fixed_unit: str | None = None  # None means read the scale off the page
    want: int = 2
    note: str = ""


@dataclass(frozen=True)
class InlineField:
    """A number stated in prose with its scale beside it."""

    key: str
    kind: str
    pattern: re.Pattern[str]  # group 1 = number, group 2 = unit (optional)
    fixed_unit: str | None = None
    note: str = ""


MSMED_PAGE = re.compile(
    r"micro[,\s].{0,12}small.{0,45}enterprises?\s+development|MSMED", re.I | re.S
)

TABLE_FIELDS: tuple[TableField, ...] = (
    TableField(
        key="mse_interest_accrued_unpaid",
        kind="money",
        label=re.compile(r"interest\s+accrued\s+and\s+remaining\s+unpaid", re.I),
        page_guard=MSMED_PAGE,
        note="Interest accrued and remaining unpaid at the end of the year",
    ),
    TableField(
        key="mse_interest_paid_during_year",
        kind="money",
        label=re.compile(
            r"(?:amount\s+of\s+)?interest\s+paid\s+by\s+the\s+(?:buyer|company)", re.I
        ),
        page_guard=MSMED_PAGE,
        note="Interest paid along with payments made beyond the appointed day",
    ),
    TableField(
        key="mse_principal_outstanding",
        kind="money",
        label=re.compile(r"principal\s+amount[\s\S]{0,90}?remaining\s+unpaid", re.I),
        page_guard=MSMED_PAGE,
        note="Closing balance owed to micro and small enterprises, not an overdue figure",
    ),
    TableField(
        key="disputed_gst_dues",
        kind="money",
        # H03's input, and the only hypothesis that has ever fired on a real
        # company. Read from the contingent liabilities note, where a GST row
        # is a plain label and value, rather than from the auditor's
        # disputed-dues annexure, which is a five-column table of statutes,
        # periods and forums that this reader cannot parse honestly yet. Where
        # a company only discloses it in the annexure, this is refused, and
        # India Cements is that case.
        label=re.compile(r"^\s*goods\s+and\s+services?\s+tax\b(?!\s+act)", re.I),
        page_guard=re.compile(
            r"(contingent\s+liabilit|claims?\s+against\s+the\s+company"
            r"|not\s+been\s+deposited)",
            re.I,
        ),
        want=1,
        note="Goods and Service Tax claims not acknowledged as debt",
    ),
    TableField(
        key="msme_sourcing_share",
        kind="ratio",
        label=re.compile(r"sourced\s+from\s+MSMEs?\s*/?\s*small\s+producers", re.I),
        fixed_unit="percent",
        note="Share of input material by value sourced from micro and small enterprises",
    ),
)

INLINE_FIELDS: tuple[InlineField, ...] = (
    InlineField(
        key="subsidiary_count",
        kind="count",
        pattern=re.compile(
            r"\b(?:had|has)\b[^.]{0,30}?\b([\d]{1,3})\s+(?:wholly[\s\-]owned\s+)?subsidiar(?:y|ies)",
            re.I,
        ),
        fixed_unit="unit",
        note="Subsidiaries consolidated, as stated in the directors' report",
    ),
    InlineField(
        key="joint_venture_count",
        kind="count",
        pattern=re.compile(r"\b([\d]{1,3})\s+joint\s+ventures?", re.I),
        fixed_unit="unit",
        note="Joint ventures, as stated in the directors' report",
    ),
    InlineField(
        key="associate_count",
        kind="count",
        pattern=re.compile(r"\b([\d]{1,3})\s+associate\s+compan(?:y|ies)", re.I),
        fixed_unit="unit",
        note="Associates, as stated in the directors' report",
    ),
)

# The auditor asserting there is nothing to report is itself a captured zero.
CARO_NONE = re.compile(
    r"(no\s+undisputed\s+(?:statutory\s+dues|amounts)|there\s+were\s+no\s+undisputed)"
    r"[\s\S]{0,320}?more\s+than\s+six\s+months",
    re.I,
)
CARO_NONE_ALT = re.compile(
    r"more\s+than\s+six\s+months[\s\S]{0,200}?(no\s+undisputed|were\s+no\s+undisputed)",
    re.I,
)

UNIT_MULT = {
    "unit": 1.0,
    "percent": 0.01,
    "thousand": 1_000.0,
    "lakh": 100_000.0,
    "million": 1_000_000.0,
    "crore": 10_000_000.0,
}


# --------------------------------------------------------------------------
# extraction


# Revenue gets its own reader, because getting it wrong is the worst failure
# available here: it is the denominator for every materiality test, so a wrong
# revenue silently rescales every finding in the brief.
#
# Dalmia Bharat prints "Rs. 14,804 crore Revenue from Operations Rs. 33,312
# crore Total Asset Base" on a single line. A pattern that finds the label and
# then looks forward for a number takes the asset base and is quietly wrong by
# more than double. So: read both word orders, discard anything that reads like
# a ratio or a different line item, and refuse unless two pages agree.

# Three word orders occur across ten reports, so each pattern declares which
# group holds the number and which holds the scale.
#   number then label   "Rs. 14,804 crore Revenue from Operations"   (Dalmia)
#   label then number   "Revenue from Operations ... was 1710.17 crores" (Seshasayee prose)
#   scale in the header "Revenue from Operations (Rs Crores) 1,710.17"  (ten-year tables)
# The gap in the label-first form uses \D so it can never skip over another
# number to reach the one it wants.
REV_PATTERNS: tuple[tuple[re.Pattern[str], int, int], ...] = (
    (
        re.compile(
            r"([\d][\d,]*\.?\d*)\s*(crores?|crs?|lakhs?|lacs?|millions?|mn)\s{0,3}revenue\s+from\s+operations",
            re.I,
        ),
        1,
        2,
    ),
    (
        re.compile(
            r"revenue\s+from\s+operations\D{0,40}?([\d][\d,]*\.?\d*)\s*(crores?|crs?|lakhs?|lacs?|millions?|mn)",
            re.I,
        ),
        1,
        2,
    ),
    (
        re.compile(
            r"revenue\s+from\s+operations[^\d]{0,25}?(crores?|crs?|lakhs?|lacs?|millions?|mn)[^\d]{0,6}"
            r"([\d][\d,]*\.?\d*)",
            re.I,
        ),
        2,
        1,
    ),
    # "Revenue from Operations in FY 26 was Rs 4,485 crore" (India Cements).
    # The year sits between the label and the figure, and the \D gap above
    # cannot pass a digit, so this form needs its own pattern. It is written to
    # allow exactly one short year-like token and nothing longer.
    (
        re.compile(
            r"revenue\s+from\s+operations[^\d]{0,25}(?<![\d,.])\d{2,4}(?![\d,.])"
            r"[^\d]{0,20}?(?<![\d,.])([\d][\d,]*\.?\d*)\s*(crores?|crs?|lakhs?|lacs?|millions?|mn)",
            re.I,
        ),
        1,
        2,
    ),
)
# Phrases that mean the figure beside the label is a ratio or a different line
# item. The window is deliberately narrow: Dalmia prints "Rs.14,804 crore
# Revenue from Operations Rs. 1,027 EBITDA/tonne", so a wide window rejects the
# correct figure because another metric is printed next to it on the same card.
REV_POISON = re.compile(
    r"(per\s+rupee|intensity|per\s+employee|/\s*revenue|total\s+asset|net\s+worth|"
    r"per\s+tonne|adjusted\s+for)",
    re.I,
)
POISON_BEFORE, POISON_AFTER = 25, 20


ABBREVIATIONS = {
    "cr": "crore", "crs": "crore", "crore": "crore", "crores": "crore",
    "lac": "lakh", "lacs": "lakh", "lakh": "lakh", "lakhs": "lakh",
    "mn": "million", "million": "million", "millions": "million",
}


def _canonical_unit(raw: str) -> str:
    return ABBREVIATIONS.get(raw.strip().lower(), raw.strip().lower().rstrip("s"))


def _extract_revenue(pages: list[str]) -> Extracted | Refused:
    seen: list[tuple[float, str, str, int]] = []  # value, printed, unit, page
    for page_no, text in enumerate(pages, start=1):
        flat = " ".join(text.split())
        for rx, num_g, unit_g in REV_PATTERNS:
            for m in rx.finditer(flat):
                around = flat[max(0, m.start() - POISON_BEFORE) : m.end() + POISON_AFTER]
                if REV_POISON.search(around):
                    continue
                printed = _clean(m.group(num_g))
                unit = _canonical_unit(m.group(unit_g))
                if unit not in UNIT_MULT:
                    continue
                try:
                    seen.append((_scaled(printed, unit), printed, unit, page_no))
                except ValueError:
                    continue

    # Table rows are read too, but only ever as corroboration. Letting them win
    # outright was tried and was a disaster: they match every small table that
    # mentions revenue, and the noise outvoted the right figure on two of three
    # companies (India Cements came out at 445,386 lakh, LMW at 20 crore).
    #
    # As corroboration they are safe and genuinely useful. An inline figure is
    # self-describing, because the scale sits against the number; a table figure
    # that agrees with one confirms it. A table figure that agrees with nothing
    # is ignored, and an inline figure that nothing confirms is refused. That is
    # what catches Vardhman, where the only inline sighting is 318.57 crore and
    # the tables all say 9,652.33.
    corroborators: list[float] = []
    for page_no, text in enumerate(pages, start=1):
        unit = page_unit(text)
        if unit is None or unit not in UNIT_MULT:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if not re.search(r"revenue\s+from\s+operations", line, re.I):
                continue
            around = " ".join(" ".join(lines[max(0, i - 2) : i + 3]).split())
            if REV_POISON.search(around):
                continue
            vals = values_after(lines, i, 1)
            if not vals:
                continue
            try:
                corroborators.append(_scaled(vals[0], unit))
            except ValueError:
                continue

    if not seen:
        return Refused("revenue", "no revenue figure is stated with a scale beside it")

    groups: list[list[tuple[float, str, str, int]]] = []
    for item in sorted(seen, key=lambda x: x[0]):
        if groups and abs(item[0] - groups[-1][0][0]) <= max(groups[-1][0][0] * 0.01, 1):
            groups[-1].append(item)
        else:
            groups.append([item])

    files_brsr = any("business responsibility" in p.lower() for p in pages[:400])
    if files_brsr:
        credible = [g for g in groups if g[0][0] >= 1_000_000_000]
        if credible:
            groups = credible

    def support(group: list[tuple[float, str, str, int]]) -> int:
        """Inline sightings plus any table figure that agrees with them."""
        target = group[0][0]
        agreeing = sum(1 for c in corroborators if abs(c - target) <= max(target * 0.01, 1))
        return len(group) + agreeing

    # The winning figure is the one the most separate statements agree on, which
    # is how Dalmia's asset base loses to its revenue three sightings to one.
    best = max(groups, key=lambda g: (support(g), len({x[3] for x in g})))
    if support(best) < 2:
        return Refused(
            "revenue",
            "the only revenue figure stated with a scale beside it is {v} {u} on page "
            "{p}, and nothing in the document agrees with it, so it is refused rather "
            "than used as the denominator for every other finding".format(
                v=best[0][1], u=best[0][2], p=best[0][3]
            ),
            best[0][3],
        )
    pages_seen = sorted({x[3] for x in best})

    value, printed, unit, page = max(
        best, key=lambda x: len(x[1].split(".")[1]) if "." in x[1] else 0
    )
    note = (
        "Revenue from operations, stated {n} times and agreeing, on page{s} {p}".format(
            n=len(best),
            s="" if len(pages_seen) == 1 else "s",
            p=", ".join(str(x) for x in pages_seen[:4]),
        )
        if len(best) > 1
        else (
            "Revenue from operations, stated once on page {p} and not corroborated "
            "anywhere else in the document".format(p=page)
        )
    )
    return Extracted(
        key="revenue",
        kind="money",
        value=value,
        as_filed=printed,
        filed_unit=unit,
        page=page,
        label="Revenue from operations",
        note=note,
    )


def read_pages(path: Path) -> list[str]:
    import fitz

    with fitz.open(path) as doc:
        return [p.get_text() for p in doc]


def detect_fiscal_year(pages: list[str]) -> str:
    head = "\n".join(pages[:40])
    years: list[int] = []
    for rx in FY_PATTERNS:
        for m in rx.finditer(head):
            groups = m.groups()
            raw = "20" + groups[1] if len(groups) == 2 else groups[0]
            try:
                years.append(int(raw))
            except ValueError:
                continue
    # Front matter carries ten-year highlight tables, so the first match found
    # is the oldest year in the document rather than the year it reports on.
    return "FY{y}".format(y=max(years)) if years else ""


def _scaled(printed: str, unit: str) -> float:
    return float(printed) * UNIT_MULT[unit]


def _extract_table_field(spec: TableField, pages: list[str]) -> Extracted | Refused:
    for page_no, text in enumerate(pages, start=1):
        if spec.page_guard is not None and not spec.page_guard.search(text):
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            # A table label wraps across lines when the column is narrow:
            # India Cements prints "Directly sourced from" and "MSMEs/ small
            # producers" on separate lines. Match a short window so the label
            # is found, and let values_after skip the continuation lines.
            window = " ".join(ln.strip() for ln in lines[i : i + 3])
            m = spec.label.search(window)
            if m is None:
                continue
            # The match must BEGIN on line i. Without this the window reaches
            # backwards: scanning at the line "40.93", the window picks up the
            # next row's label two lines down, and the values collected then
            # belong to the row above. That silently reported a principal
            # balance as an interest figure on two of three companies.
            if m.start() > len(lines[i].strip()):
                continue

            unit = spec.fixed_unit or page_unit(text)
            if unit is None:
                return Refused(
                    key=spec.key,
                    reason=(
                        "found the row on page {p} but no scale is declared on that "
                        "page, and taking one from elsewhere in the document is how a "
                        "hundredfold error happens"
                    ).format(p=page_no),
                    page=page_no,
                )
            if unit not in UNIT_MULT:
                return Refused(spec.key, "unknown scale {u!r}".format(u=unit), page_no)

            vals = values_after(lines, i, spec.want)
            if not vals:
                return Refused(
                    spec.key,
                    "found the row on page {p} but no value followed it".format(p=page_no),
                    page_no,
                )

            try:
                value = _scaled(vals[0], unit)
                prior_printed = vals[1] if len(vals) > 1 else ""
                prior = _scaled(prior_printed, unit) if prior_printed else None
            except ValueError:
                return Refused(spec.key, "value did not parse", page_no)

            return Extracted(
                key=spec.key,
                kind=spec.kind,
                value=value,
                as_filed=vals[0],
                filed_unit=unit,
                page=page_no,
                label=line.strip()[:90],
                note=spec.note,
                prior_value=prior,
                prior_as_filed=prior_printed,
            )
    return Refused(spec.key, "the row was not found in this document")


def _extract_inline_field(spec: InlineField, pages: list[str]) -> Extracted | Refused:
    # A figure often appears more than once: rounded in the chairman's letter,
    # exact in the table. Collect every match and keep the most precise one,
    # measured by decimal places, so "4,485 crore" loses to "4,484.69 crore".
    hits: list[tuple[int, int, re.Match[str]]] = []
    for page_no, text in enumerate(pages, start=1):
        flat = " ".join(text.split())
        for m in spec.pattern.finditer(flat):
            printed_raw = _clean(m.group(1))
            decimals = len(printed_raw.split(".")[1]) if "." in printed_raw else 0
            hits.append((decimals, -page_no, m))
            if spec.key != "revenue":
                break
        if hits and spec.key != "revenue":
            break

    for _, neg_page, m in sorted(hits, key=lambda h: (h[0], h[1]), reverse=True):
        page_no = -neg_page
        printed = _clean(m.group(1))
        if spec.fixed_unit:
            unit = spec.fixed_unit
        else:
            raw_unit = m.group(2) if m.lastindex and m.lastindex >= 2 else None
            if not raw_unit:
                return Refused(spec.key, "no scale beside the figure", page_no)
            unit = raw_unit.lower().rstrip("s")
        if unit not in UNIT_MULT:
            return Refused(spec.key, "unknown scale {u!r}".format(u=unit), page_no)
        try:
            value = _scaled(printed, unit)
        except ValueError:
            return Refused(spec.key, "value did not parse", page_no)
        return Extracted(
            key=spec.key,
            kind=spec.kind,
            value=value,
            as_filed=printed,
            filed_unit=unit,
            page=page_no,
            label=m.group(0)[:90],
            note=spec.note,
        )
    return Refused(spec.key, "not stated in this document")


def _extract_caro_zero(pages: list[str]) -> Extracted | Refused:
    for page_no, text in enumerate(pages, start=1):
        flat = " ".join(text.split())
        if CARO_NONE.search(flat) or CARO_NONE_ALT.search(flat):
            return Extracted(
                key="undisputed_statutory_dues_over_6m",
                kind="money",
                value=0.0,
                as_filed="0",
                filed_unit="unit",
                page=page_no,
                label="CARO clause (vii)(a)",
                note="Auditor states no undisputed statutory dues in arrears over six months",
            )
    return Refused(
        "undisputed_statutory_dues_over_6m",
        "the auditor's six-month clause was not located, so this is untested rather than clean",
    )


def extract(path: Path, company: str = "", fiscal_year: str = "") -> Draft:
    pages = read_pages(path)

    if len(pages) <= 2:
        return Draft(
            company=company or path.stem,
            fiscal_year=fiscal_year,
            source_file=path.name,
            pages=len(pages),
            refused=[
                Refused(
                    "*",
                    "this file holds no readable text. If it is a PDF Portfolio run "
                    "tools/unwrap.py first; if it is scanned it needs OCR",
                )
            ],
        )

    draft = Draft(
        company=company or path.stem,
        fiscal_year=fiscal_year or detect_fiscal_year(pages),
        source_file=path.name,
        pages=len(pages),
    )

    for spec in TABLE_FIELDS:
        got = _extract_table_field(spec, pages)
        (draft.found if isinstance(got, Extracted) else draft.refused).append(got)  # type: ignore[arg-type]

    for ispec in INLINE_FIELDS:
        got2 = _extract_inline_field(ispec, pages)
        (draft.found if isinstance(got2, Extracted) else draft.refused).append(got2)  # type: ignore[arg-type]

    rev = _extract_revenue(pages)
    (draft.found if isinstance(rev, Extracted) else draft.refused).append(rev)  # type: ignore[arg-type]

    caro = _extract_caro_zero(pages)
    (draft.found if isinstance(caro, Extracted) else draft.refused).append(caro)  # type: ignore[arg-type]

    # Imported here rather than at module scope: extract_rpt reads Extracted,
    # Refused and page_unit from this module, so a top-level import would be
    # circular.
    from grounds.extract_rpt import extract_kam_related_party, extract_related_party_trade

    for fn in (extract_related_party_trade, extract_kam_related_party):
        got3 = fn(pages)
        (draft.found if isinstance(got3, Extracted) else draft.refused).append(got3)  # type: ignore[arg-type]

    return draft


# --------------------------------------------------------------------------
# emit


def to_yaml(draft: Draft, report_title: str = "") -> str:
    title = report_title or "{c} Annual Report".format(c=draft.company)
    lines = [
        "company: {c}".format(c=draft.company),
        "fiscal_year: {y}".format(y=draft.fiscal_year or "UNKNOWN"),
        "capture: parsed",
        "",
        "# Written by tools/extract.py from {f}.".format(f=draft.source_file),
        "# Page numbers are PDF pages, not printed pages. Every figure records the",
        "# number as printed and the scale declared on that same page, so the loader",
        "# re-checks the arithmetic and refuses the file if it does not reconcile.",
        "",
    ]

    if draft.refused:
        lines.append("# Refused, and therefore absent rather than guessed:")
        for r in draft.refused:
            where = " (page {p})".format(p=r.page) if r.page else ""
            lines.append("#   {k}: {why}{w}".format(k=r.key, why=r.reason, w=where))
        lines.append("")

    lines.append("sources:")
    for page in sorted({e.page for e in draft.found}):
        lines += [
            "  p{p}:".format(p=page),
            "    doc_type: annual_report",
            '    title: "{t}"'.format(t=title),
            "    year: {y}".format(y=draft.fiscal_year or "UNKNOWN"),
            '    locator: "PDF page {p}"'.format(p=page),
        ]

    lines += ["", "signals:"]
    for e in draft.found:
        lines += [
            "  - key: {k}".format(k=e.key),
            "    value: {v}".format(v=_fmt(e.value)),
            "    unit: {u}".format(u="share" if e.kind == "ratio" else ("entities" if e.kind == "count" else "INR")),
            "    kind: {k}".format(k=e.kind),
            '    as_filed: "{a}"'.format(a=e.as_filed),
            "    filed_unit: {u}".format(u=e.filed_unit),
        ]
        if e.prior_value is not None:
            lines += [
                "    prior_value: {v}".format(v=_fmt(e.prior_value)),
                '    prior_as_filed: "{a}"'.format(a=e.prior_as_filed),
            ]
        lines += [
            "    source: p{p}".format(p=e.page),
            '    note: "{n}"'.format(n=e.note.replace('"', "'")),
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def _fmt(v: float) -> str:
    if v == int(v):
        return str(int(v))
    return repr(round(v, 6))
