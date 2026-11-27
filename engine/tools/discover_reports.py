"""Find each listed company's latest annual report URL, and write a manifest.

    python -I tools/discover_reports.py --sitemap                 refresh the company list
    python -I tools/discover_reports.py --hours 2.5               walk it, build the manifest
    python -I tools/discover_reports.py --status
    python -I tools/discover_reports.py --limit 25 --hours 0.02   trial run

## Why this exists

Annual report URLs on BSE are opaque GUIDs. Nothing derives
7c127e93-ce6f-45a9-98d5-efee5deb8b54.pdf from "India Cements", and BSE's own
index API refuses automated clients outright: it answers 403 to plain curl, and
the only way past it is to imitate a browser, which is not something this
project will do for a figure it then has to defend in a room.

screener.in publishes the same BSE links on each company page, permits
/company/<id>/ in robots.txt, and advertises a company sitemap for crawlers. So
both the list of companies and the links come from pages the site asks crawlers
to read. The check that these are the same documents: screener's "Annual Report
2026" for India Cements is the GUID this project had already downloaded and read
by hand, character for character.

## Pacing and politeness

screener.in is a small site and this walks roughly five thousand of its pages.
`--hours` is a budget rather than a delay: after each company the script works
out how far ahead of pace it is and sleeps the difference, with `--min-delay` as
a floor that always applies. One request at a time, no concurrency.

## Resume

Every result, including every failure and every company that lists no report, is
appended to corpus/discovered.jsonl. A restart skips companies already recorded,
so an interrupted run costs only what it had not reached.
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "corpus"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "discover.log"
STATUS_FILE = ROOT / "discover-status.json"
LEDGER = ROOT / "discovered.jsonl"
MANIFEST = ROOT / "manifest.csv"
SITEMAP_DIR = ROOT / "sitemaps"

SITEMAPS = (
    "https://www.screener.in/sitemap-companies.xml",
    "https://www.screener.in/sitemap-companies.xml?p=2",
    "https://www.screener.in/sitemap-companies.xml?p=3",
)

LOC = re.compile(r"<loc>https://www\.screener\.in/company/([^/<]+)/?</loc>")
# The annual reports column on a company page, then the dated links inside it.
BLOCK = re.compile(r'class="documents annual-reports.*?</div>\s*</div>', re.S)
LINK = re.compile(
    r'href="(?P<url>https?://[^"]+?\.pdf[^"]*)"[^>]*>\s*Annual Report\s*(?P<year>\d{4})',
    re.I,
)
NAME = re.compile(r"<h1[^>]*>\s*(.*?)\s*</h1>", re.S)
MIN_PAGE_BYTES = 2000

# screener answers a throttled request with a page whose heading reads "Too
# many requests". The first run paced at 0.8s, tripped this on 2,419 of 4,929
# companies, and recorded every one of them as a company by that name. The
# links on those pages were still correct for the right company - 21 of 21
# numeric ids matched the scrip embedded in the URL they gave - so no figure
# was mis-attributed, but 1,255 companies lost their reports section and were
# written down as having no report, which is a false negative dressed as a
# finding. A throttled page is now never a result: it is retried with backoff
# and, if it will not clear, recorded as retryable so a later pass picks it up.
THROTTLED = re.compile(r"too\s+many\s+requests", re.I)
BACKOFF_SECONDS = (20, 45, 90, 180)


def log(msg: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write("{s}  {m}\n".format(s=stamp, m=msg))
        fh.flush()


def get(url: str, timeout: float = 45.0) -> str | None:
    """Fetch with curl, which identifies itself honestly as curl."""
    try:
        proc = subprocess.run(
            [
                "curl", "-sS", "-L", "--compressed",
                "--max-time", str(int(timeout)),
                "--retry", "2", "--retry-delay", "3",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 60,
            errors="replace",
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def refresh_sitemaps() -> list[str]:
    SITEMAP_DIR.mkdir(parents=True, exist_ok=True)
    ids: list[str] = []
    for i, url in enumerate(SITEMAPS, 1):
        body = get(url, 90)
        if body is None:
            log("sitemap {i} failed".format(i=i))
            continue
        (SITEMAP_DIR / "companies-{i}.xml".format(i=i)).write_text(body, encoding="utf-8")
        found = LOC.findall(body)
        log("sitemap {i}: {n} company ids".format(i=i, n=len(found)))
        ids += found
        time.sleep(2)

    out: list[str] = []
    seen: set[str] = set()
    for cid in ids:
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    (ROOT / "companies.txt").write_text("\n".join(out), encoding="utf-8")
    log("universe: {n} unique companies".format(n=len(out)))
    return out


def load_universe() -> list[str]:
    f = ROOT / "companies.txt"
    if f.exists():
        return [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return refresh_sitemaps()


def ledger_records() -> dict[str, dict]:
    """Latest record per company id. A repair pass supersedes an earlier one."""
    out: dict[str, dict] = {}
    if not LEDGER.exists():
        return out
    for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            r = json.loads(line)
            out[r["id"]] = r
        except (ValueError, KeyError):
            continue
    return out


def done_ids() -> set[str]:
    return {k for k, r in ledger_records().items() if not r.get("retryable")}


def throttled_ids() -> list[str]:
    """Companies whose record came from a rate-limit page, in sitemap order."""
    recs = ledger_records()
    out = []
    for cid, r in recs.items():
        name = (r.get("name") or "")
        if r.get("retryable") or THROTTLED.search(name):
            out.append(cid)
    return out


def clean_name(text: str) -> str:
    """A company name as a person would read it, tags and entities resolved."""
    s = re.sub(r"<[^>]+>", "", text or "")
    # Screener serves names HTML-escaped, so "India Sugars &amp; Refineries"
    # arrives with the entity intact. Left alone it slugs to "...-amp-...",
    # a filename nobody can match back to a company. Twice, because a few
    # names arrive double-escaped as "&amp;amp;".
    s = html_mod.unescape(html_mod.unescape(s))
    return re.sub(r"\s+", " ", s).strip()


def slugify(text: str, fallback: str) -> str:
    s = clean_name(text).lower()
    s = re.sub(r"\b(limited|ltd|private|pvt|the)\b", " ", s)
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-and$", "", s)
    return s[:60].strip("-") or fallback.lower()


def is_throttled(html: str) -> bool:
    """True when this is screener's rate-limit page rather than a company."""
    head = html[:4000]
    m = NAME.search(head)
    if m is not None and THROTTLED.search(re.sub(r"<[^>]+>", "", m.group(1))):
        return True
    return bool(THROTTLED.search(head)) and "annual-reports" not in html


def parse(html: str, cid: str) -> dict:
    name_m = NAME.search(html)
    name = clean_name(name_m.group(1)) if name_m is not None else ""

    blk = BLOCK.search(html)
    if blk is None:
        return {"id": cid, "name": name, "ok": False, "why": "no annual reports section"}

    links = [(int(m.group("year")), m.group("url")) for m in LINK.finditer(blk.group(0))]
    if not links:
        return {
            "id": cid, "name": name, "ok": False,
            "why": "section present but lists no report",
        }

    year, url = max(links, key=lambda t: t[0])
    return {
        "id": cid,
        "name": name,
        "ok": True,
        "year": year,
        "url": url,
        "slug": slugify(name, cid),
        "years_listed": sorted({y for y, _ in links}, reverse=True)[:8],
    }


def write_manifest() -> tuple[int, int]:
    rows: list[tuple[str, str, str, object, str]] = []
    bad = 0
    seen_slug: dict[str, int] = {}

    for r in ledger_records().values():
        if not r.get("ok"):
            bad += 1
            continue
        url = r["url"]
        # A few links are http. The fetcher refuses anything but https, and
        # these same hosts serve https, so upgrade rather than drop 34 reports.
        if url.startswith("http://") and re.match(
            r"http://(www\.)?(bseindia|nseindia)\.com/", url
        ):
            url = "https://" + url[len("http://") :]
        slug = slugify(r.get("name") or "", r["id"])
        seen_slug[slug] = seen_slug.get(slug, 0) + 1
        if seen_slug[slug] > 1:
            slug = "{s}-{n}".format(s=slug, n=seen_slug[slug])
        rows.append((slug, r["id"], url, r.get("year", ""), clean_name(r.get("name", ""))))

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    lines = ["slug,scrip,url,year,company"]
    for slug, cid, url, year, name in rows:
        clean = (name or "").replace('"', "'")
        lines.append("{s},{c},{u},{y},\"{n}\"".format(s=slug, c=cid, u=url, y=year, n=clean))
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows), bad


def show_status() -> int:
    if not STATUS_FILE.exists():
        print("no discovery run yet ({p})".format(p=STATUS_FILE))
        return 1
    s = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    print("discovery  -  {st}".format(st=s.get("state", "?")))
    for k in ("started", "updated", "elapsed", "projected_finish"):
        print("  {k:17}{v}".format(k=k, v=s.get(k, "-")))
    print(
        "  progress         {d} of {t}  ({p:.1f}%)".format(
            d=s.get("done", 0), t=s.get("total", 0), p=s.get("percent", 0.0)
        )
    )
    print(
        "  found {f}   lists none {n}   failed {e}".format(
            f=s.get("found", 0), n=s.get("no_report", 0), e=s.get("failed", 0)
        )
    )
    print("  rate             {r:.1f} companies/min".format(r=s.get("per_min", 0.0)))
    if s.get("last_error"):
        print("  last error       {e}".format(e=s["last_error"]))
    print("\nlog:      {p}".format(p=LOG_FILE))
    print("manifest: {m}".format(m=MANIFEST))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=2.5, help="wall-clock budget")
    ap.add_argument("--min-delay", type=float, default=2.0, help="floor between requests")
    ap.add_argument("--limit", type=int, default=0, help="stop after N (trial run)")
    ap.add_argument("--sitemap", action="store_true", help="refresh the company list and exit")
    ap.add_argument("--status", action="store_true", help="print progress and exit")
    ap.add_argument("--manifest-only", action="store_true", help="rebuild the CSV from the ledger")
    ap.add_argument(
        "--redo-throttled",
        action="store_true",
        help="re-walk only the companies whose record came from a rate-limit page",
    )
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    ROOT.mkdir(parents=True, exist_ok=True)

    if args.status:
        return show_status()
    if args.sitemap:
        ids = refresh_sitemaps()
        print("{n} companies written to {p}".format(n=len(ids), p=ROOT / "companies.txt"))
        return 0
    if args.manifest_only:
        n, bad = write_manifest()
        print("manifest: {n} rows ({b} companies list no report)".format(n=n, b=bad))
        return 0

    universe = load_universe()
    if args.redo_throttled:
        order = {c: i for i, c in enumerate(universe)}
        todo = sorted(throttled_ids(), key=lambda c: order.get(c, 10**9))
        already = set()
    else:
        already = done_ids()
        todo = [c for c in universe if c not in already]
    if args.limit:
        todo = todo[: args.limit]
    if not todo:
        n, bad = write_manifest()
        print("nothing left to discover. manifest: {n} rows".format(n=n))
        return 0

    pace = args.hours * 3600 / max(1, len(todo))
    started = datetime.now(timezone.utc).astimezone()
    log("=" * 68)
    log(
        "discovery start: {u} in universe, {d} already recorded, {t} to walk, "
        "budget {h}h, pace {p:.2f}s each".format(
            u=len(universe), d=len(already), t=len(todo), h=args.hours, p=pace
        )
    )

    found = none = failed = throttles = 0
    retryable = 0
    last_error = ""
    t0 = time.monotonic()

    for i, cid in enumerate(todo, 1):
        due = t0 + pace * (i - 1)
        wait = max(args.min_delay, due - time.monotonic()) if i > 1 else 0.0
        if wait > 0:
            time.sleep(wait)

        rec: dict | None = None
        for attempt, pause in enumerate((0,) + BACKOFF_SECONDS):
            if pause:
                log("throttled on {c}, backing off {p}s".format(c=cid, p=pause))
                time.sleep(pause)
            html = get("https://www.screener.in/company/{c}/".format(c=cid))
            if html is None or len(html) < MIN_PAGE_BYTES:
                rec = {"id": cid, "ok": False, "why": "fetch failed or page too small"}
                break
            if is_throttled(html):
                throttles += 1
                rec = None
                continue
            rec = parse(html, cid)
            break
        if rec is None:
            # Still throttled after every backoff. Recorded so the walk can go
            # on, flagged so a later pass redoes it, and never counted as a
            # company that has no report.
            rec = {
                "id": cid, "ok": False, "retryable": True,
                "why": "rate limited after {n} attempts".format(n=len(BACKOFF_SECONDS) + 1),
            }

        rec["seen"] = datetime.now(timezone.utc).isoformat()
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
            fh.flush()

        if rec.get("ok"):
            found += 1
            log(
                "ok   {i}/{t} {c} {y} {n}".format(
                    i=i, t=len(todo), c=cid, y=rec.get("year"),
                    n=(rec.get("name") or "")[:42],
                )
            )
        elif rec.get("retryable"):
            retryable += 1
            last_error = "{c}: {w}".format(c=cid, w=rec["why"])
            log("RETRY {i}/{t} {c} {w}".format(i=i, t=len(todo), c=cid, w=rec["why"]))
        elif "fetch failed" in rec.get("why", ""):
            failed += 1
            last_error = "{c}: {w}".format(c=cid, w=rec["why"])
            log("FAIL {i}/{t} {c} {w}".format(i=i, t=len(todo), c=cid, w=rec["why"]))
        else:
            none += 1
            log("none {i}/{t} {c} {w}".format(i=i, t=len(todo), c=cid, w=rec["why"]))

        elapsed = time.monotonic() - t0
        eta = datetime.now(timezone.utc).astimezone() + timedelta(
            seconds=(len(todo) - i) * (elapsed / i)
        )
        STATUS_FILE.write_text(
            json.dumps(
                {
                    "state": "running",
                    "started": started.isoformat(timespec="seconds"),
                    "updated": datetime.now(timezone.utc)
                    .astimezone()
                    .isoformat(timespec="seconds"),
                    "universe": len(universe),
                    "total": len(todo),
                    "done": i,
                    "percent": i / len(todo) * 100,
                    "found": found,
                    "no_report": none,
                    "failed": failed,
                    "retryable": retryable,
                    "throttle_hits": throttles,
                    "per_min": round(i / (elapsed / 60), 2) if elapsed else 0.0,
                    "elapsed": str(timedelta(seconds=int(elapsed))),
                    "projected_finish": eta.isoformat(timespec="seconds"),
                    "last_error": last_error,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        if i % 50 == 0:
            write_manifest()

    rows, bad = write_manifest()
    log(
        "discovery end: {f} found, {n} list no report, {e} failed, {y} rate limited "
        "({h} throttle hits). manifest {r} rows".format(
            f=found, n=none, e=failed, y=retryable, h=throttles, r=rows
        )
    )
    st = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    st["state"] = "finished"
    st["manifest_rows"] = rows
    STATUS_FILE.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(
        "done: {f} found, {n} no report, {e} failed, {y} rate limited. "
        "manifest: {r} rows at {m}".format(
            f=found, n=none, e=failed, y=retryable, r=rows, m=MANIFEST
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
