"""Related party trade volume, and whether the auditor called it out.

Two readers that do not fit the label-and-value shape in `extract.py`, because
neither figure is a labeled row.

## Related party trade volume

An Ind AS 24 note is a transaction-type heading, then one line per party with
its current and prior figure, then an unlabeled total pair:

    Sale of Goods
    Coromandel Sugars Limited
    0.00
    146.59
    UltraTech Cement Limited
    2,47,270.02
    14,440.55
    2,47,270.02          <- block total, no label of its own
    14,720.52

The first attempt at this read "scan forward until the next known heading" and
got Purchase of Goods wrong by reporting 24,173.17 instead of 27,405.14: the
block ran on past "Redemption of Debentures", a heading that was not in the
list. No list of transaction types can ever be complete, so that approach is
unsound by construction.

So the rule here is structural instead. A party row is text, number, number. A
total is a number pair with no name in front of it. And a total is accepted
only when it equals the sum of at least two party rows above it, which proves
the block boundary by arithmetic rather than assuming it. One party row is not
proof: with a single row, sum == total holds for any repeated pair.

Only the four trade headings are summed. India Cements' note also contains
"Received during the Year", "Repaid During the Year" and KMP remuneration;
those are financing and payroll flows, and adding them to trade volume would
conflate three different things to make one bigger number.

## Related party as a key audit matter

Separately, the auditor publishes the matters that took most of their audit.
Where related party transactions are one of them, that is the auditor
independently naming what the volume figure points at.

Reading those matters is bounded at both ends on purpose. An unbounded match
lies twice over: too short and the boilerplate paragraph is mistaken for the
section, which read Dalmia as silent when its matters sit forty pages later;
too long and the section swallows what follows it, which read JSW Steel as
naming related parties when the phrase was CARO text about loans to promoters.
Both were false until the section was pinned at both ends.

The title must also begin with a capital, which is not decorative. With
`re.I` on the whole pattern, `[A-Z]` matches lowercase too, and that one flag
turned "the other liabilities payable such as liquidated" into a key audit
matter for Suzlon. The structure is matched case-sensitively and only the
topic word is not.

Titles are read from numbered headings alone. Nine of ten reports number the
audit report's own paragraphs rather than the matters, so prose scanning
returns sentences like "We reviewed the significant litigations" dressed up as
titles. Those nine are refused rather than guessed at.
"""

from __future__ import annotations

import re

from grounds.extract import Extracted, Refused, page_unit

# The note itself, which may begin pages before the transaction table.
RPT_ANCHOR = re.compile(r"related\s+part(?:y|ies)\s+(?:disclosur|transaction)", re.I)
RPT_WINDOW = 5

# Trade flows only. These four create invoices to match and balances to
# eliminate. Financing and payroll flows are deliberately excluded.
TRADE_HEADINGS = re.compile(
    r"^\s*(sale\s+of\s+(?:goods|products)|purchase\s+of\s+(?:goods|products|materials)"
    r"|rendering\s+of\s+services|receiving\s+of\s+services"
    r"|sale\s+of\s+services|services\s+rendered|services\s+received)\s*:?\s*$",
    re.I,
)

_NUM = re.compile(r"^\(?\s*([\d][\d,]*(?:\.\d+)?)\s*\)?$")
_SKIP = re.compile(
    r"^\s*$|^\d+$|lakh|crore|million|^`|^₹|31-03-|31\.03\.|as\s+at|year\s+ended",
    re.I,
)

MIN_PARTIES = 2  # below this, sum == printed total proves nothing
MIN_TRADE_BLOCKS = 2  # one proved block is a fragment, not a trade volume

# --- key audit matters ---
KAM_START = re.compile(r"key\s+audit\s+matters?\b", re.I)
KAM_END = re.compile(
    r"(information\s+other\s+than|other\s+information\b"
    r"|responsibilit(?:y|ies)\s+of\s+(?:management|the\s+board)"
    r"|management.{0,3}s\s+responsibilit|auditor.{0,3}s\s+responsibilit(?:y|ies)"
    r"|report\s+on\s+other\s+legal)",
    re.I,
)
KAM_MIN, KAM_MAX = 1500, 16000
KAM_PAGE_WINDOW = 6
_NUM_OWN_LINE = re.compile(r"^[ \t]*(\d{1,2})[.)][ \t]*$")
_NUM_INLINE = re.compile(r"^[ \t]*(\d{1,2})[.)][ \t]+([A-Z][^\n]{7,78})$")
_RELATED_PARTY_WORD = re.compile(r"related\s+part", re.I)


def _val(s: str) -> float:
    return float(s.replace(",", ""))


def _blocks(lines: list[str]) -> list[tuple[str, int, float, float]]:
    """Proved blocks on one page: (heading, party_count, total_now, total_prior)."""
    out: list[tuple[str, int, float, float]] = []
    head: str | None = None
    rows: list[tuple[float, float]] = []
    i = 0

    def close(total: tuple[float, float] | None) -> None:
        nonlocal head, rows
        if head is not None and total is not None and len(rows) >= MIN_PARTIES:
            s_now = sum(r[0] for r in rows)
            s_pri = sum(r[1] for r in rows)
            # The boundary is only correct if the printed total reconciles.
            if abs(total[0] - s_now) <= max(abs(s_now) * 1e-4, 0.05) and abs(
                total[1] - s_pri
            ) <= max(abs(s_pri) * 1e-4, 0.05):
                out.append((head, len(rows), total[0], total[1]))
        head, rows = None, []

    while i < len(lines):
        ln = lines[i].strip()
        if _SKIP.match(ln):
            i += 1
            continue
        m1 = _NUM.match(ln)
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        m2 = _NUM.match(nxt)

        if m1 and m2:
            close((_val(m1.group(1)), _val(m2.group(1))))
            i += 2
            continue
        if m1:
            i += 1
            continue
        if m2:
            third = lines[i + 2].strip() if i + 2 < len(lines) else ""
            m3 = _NUM.match(third)
            if m3:
                rows.append((_val(m2.group(1)), _val(m3.group(1))))
                i += 3
                continue
            i += 2
            continue
        # plain text, no figures after it: a new heading
        close(None)
        head, rows = ln, []
        i += 1

    close(None)
    return out


def extract_related_party_trade(pages: list[str]) -> Extracted | Refused:
    """Total trade volume with related parties, summed from proved block totals."""
    hits = [i for i, t in enumerate(pages) if RPT_ANCHOR.search(t)]
    if not hits:
        return Refused(
            "related_party_trade_value",
            "no related party disclosure note was located",
        )

    scan = sorted({j for i in hits for j in range(i, min(i + RPT_WINDOW, len(pages)))})
    # Keep the first proved total per heading. The standalone note comes before
    # the consolidated one, and summing both would double count.
    seen: dict[str, tuple[float, float, int, int]] = {}
    for pg in scan:
        unit = page_unit(pages[pg])
        if unit is None:
            continue
        for head, parties, now, prior in _blocks(pages[pg].split("\n")):
            if not TRADE_HEADINGS.match(head):
                continue
            norm = re.sub(r"\s+", " ", head).strip().lower().rstrip(":")
            if norm in seen:
                continue
            seen[norm] = (now, prior, pg, parties)

    if len(seen) < MIN_TRADE_BLOCKS:
        return Refused(
            "related_party_trade_value",
            "{n} trade block(s) reconciled against their party rows, which is too "
            "few to call a trade volume. The note is present but its layout is not "
            "one this reader can prove".format(n=len(seen)),
        )

    # Blocks are grouped by the scale their page declares, never by page. A
    # note runs across pages: India Cements prints sale and purchase of goods
    # on one page and both services blocks on the next, all in lakh, and
    # keeping to a single page silently dropped half the trade volume. What
    # must not be mixed is lakh with crore, so the unit is what groups them.
    by_unit: dict[str, list[tuple[str, float, float, int, int]]] = {}
    for norm, (now, prior, pg, parties) in seen.items():
        u = page_unit(pages[pg])
        if u is None:
            continue
        by_unit.setdefault(u, []).append((norm, now, prior, parties, pg))
    if not by_unit:
        return Refused(
            "related_party_trade_value",
            "trade blocks reconciled but no page declared a scale, so the figures "
            "cannot be read at a known magnitude",
        )
    unit = max(by_unit, key=lambda u: len(by_unit[u]))
    chosen = by_unit[unit]
    if len(chosen) < MIN_TRADE_BLOCKS:
        return Refused(
            "related_party_trade_value",
            "proved trade blocks were spread across pages declaring different "
            "scales, so they cannot be summed honestly",
        )

    best_pg = min(c[4] for c in chosen)
    total_now = sum(c[1] for c in chosen)
    total_prior = sum(c[2] for c in chosen)
    names = ", ".join(sorted(c[0] for c in chosen))

    from grounds.extract import _scaled  # local import: shared scale table

    return Extracted(
        key="related_party_trade_value",
        kind="money",
        value=_scaled("{v:.2f}".format(v=total_now), unit),
        as_filed="{v:.2f}".format(v=total_now),
        filed_unit=unit,
        page=best_pg,
        label="Related party trade volume",
        prior_value=_scaled("{v:.2f}".format(v=total_prior), unit),
        prior_as_filed="{v:.2f}".format(v=total_prior),
        note=(
            "Sum of {n} trade blocks ({names}), each one's printed total "
            "reconciled against its own party rows before being used. "
            "Financing and payroll flows in the same note are excluded."
        ).format(n=len(chosen), names=names),
    )


def _kam_section(pages: list[str]) -> tuple[str, int] | None:
    """The key audit matters section, pinned at both ends, or None."""
    best: tuple[str, int] | None = None
    for i, t in enumerate(pages):
        if not KAM_START.search(t):
            continue
        txt = "".join(pages[i : min(i + KAM_PAGE_WINDOW, len(pages))])
        m = KAM_START.search(txt)
        if m is None:
            continue
        seg = txt[m.end() :]
        e = KAM_END.search(seg)
        if e is not None:
            seg = seg[: e.start()]
        if KAM_MIN <= len(seg) <= KAM_MAX:
            return seg, i
        if best is None or len(seg) > len(best[0]):
            best = (seg, i)
    return best


def _numbered_titles(seg: str) -> list[str]:
    """Titles from numbered headings only. Prose is not a title."""
    lines = [ln.rstrip() for ln in seg.split("\n")]
    out: list[str] = []
    for i, ln in enumerate(lines):
        m = _NUM_OWN_LINE.match(ln)
        if m is not None:
            for nxt in lines[i + 1 : i + 3]:
                s = nxt.strip()
                if 8 < len(s) < 80 and re.match(r"^[A-Z]", s):
                    out.append(s)
                    break
            continue
        m2 = _NUM_INLINE.match(ln)
        if m2 is not None:
            out.append(m2.group(2).strip())
    return out


def extract_kam_related_party(pages: list[str]) -> Extracted | Refused:
    """Did the auditor name related party transactions as a key audit matter?"""
    got = _kam_section(pages)
    if got is None:
        return Refused(
            "kam_related_party",
            "no key audit matters section was located",
        )
    seg, pg = got
    if not (KAM_MIN <= len(seg) <= KAM_MAX):
        return Refused(
            "kam_related_party",
            "the key audit matters section could not be pinned at both ends "
            "({n} characters), and an unbounded read of it reports both false "
            "silence and false hits".format(n=len(seg)),
            page=pg,
        )

    titles = _numbered_titles(seg)
    # A title that is really a boilerplate sentence about what matters are.
    titles = [
        t
        for t in titles
        if not re.search(r"key\s+audit\s+matters?\s+(are|is)|we\s+have\s+determined", t, re.I)
    ]
    if not titles:
        return Refused(
            "kam_related_party",
            "the matters section was read but this report numbers the audit "
            "report's own paragraphs rather than the matters, so no title could "
            "be isolated. Scanning its prose instead returns sentences, not titles",
            page=pg,
        )

    named = [t for t in titles if _RELATED_PARTY_WORD.search(t)]
    if not named:
        return Refused(
            "kam_related_party",
            "the auditor named {n} key audit matter(s) and none of them is about "
            "related party transactions".format(n=len(titles)),
            page=pg,
        )

    return Extracted(
        key="kam_related_party",
        kind="count",
        value=1.0,
        as_filed="1",
        filed_unit="unit",
        page=pg,
        label="Related parties named as a key audit matter",
        note=(
            'The auditor listed "{t}" among {n} key audit matters, which are the '
            "matters they judged most significant in the whole audit"
        ).format(t=named[0].rstrip(".").strip(), n=len(titles)),
    )
