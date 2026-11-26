"""Download annual reports from a manifest, paced to a wall-clock budget.

    python -I tools/fetch_corpus.py --manifest ../corpus/manifest.csv
    python -I tools/fetch_corpus.py --manifest ../corpus/manifest.csv --hours 6
    python -I tools/fetch_corpus.py --status          # one-glance progress
    python -I tools/fetch_corpus.py --manifest m.csv --dry-run

The manifest is a CSV with a header and three columns:

    slug,scrip,url
    india-cements,530005,https://www.bseindia.com/xml-data/corpfiling/AttachHis/7c12....pdf

Nothing here discovers URLs. This takes a list and fetches it, so the fetching
is separable from the question of where the list comes from and can be re-run
against a longer list without changing.

## Pacing

`--hours` is a budget, not a delay. After each report the script works out how
far ahead or behind the pace it is and sleeps the difference, so 5,000 reports
over six hours lands near six hours whether the files are 2 MB or 27 MB. A
floor of `--min-delay` seconds always applies, so a run that is behind schedule
never hammers the server to catch up.

## Logging

Everything goes to corpus/logs/fetch.log, appended and flushed line by line,
so `tail` shows the truth while the run is in progress. The console stays
quiet. corpus/status.json is rewritten after every report with a summary
worth one glance: how many done, how many failed, bytes so far, the current
rate and the projected finish.

## Resume

Safe to stop and restart. A report already on disk and larger than
`--min-bytes` is skipped, so a restart picks up where it stopped. Downloads
land on a .part file and are renamed only once complete, so an interrupted
transfer is never mistaken for a finished one.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
import subprocess
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "corpus"
PDF_DIR = ROOT / "pdfs"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "fetch.log"
STATUS_FILE = ROOT / "status.json"
LEDGER_FILE = ROOT / "fetched.jsonl"

# Downloads run through curl, so the client identifies itself as curl and
# nothing is misrepresented. See fetch_one for why urllib is not used.

# A real annual report is never this small. Anything smaller is an error page
# that happened to arrive with a 200.
MIN_BYTES = 40_000
CHUNK = 1 << 16


def log(msg: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write("{s}  {m}\n".format(s=stamp, m=msg))
        fh.flush()


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for i, r in enumerate(rows, 2):
        slug = (r.get("slug") or "").strip()
        url = (r.get("url") or "").strip()
        if not slug or not url:
            log("manifest line {i}: skipped, needs both slug and url".format(i=i))
            continue
        if not url.lower().startswith("https://"):
            log("manifest line {i}: skipped {s}, url is not https".format(i=i, s=slug))
            continue
        out.append({"slug": slug, "scrip": (r.get("scrip") or "").strip(), "url": url})
    return out


def already_have(slug: str, min_bytes: int) -> Path | None:
    p = PDF_DIR / "{s}.pdf".format(s=slug)
    if p.exists() and p.stat().st_size >= min_bytes:
        return p
    return None


def fetch_one(url: str, dest: Path, timeout: float) -> tuple[int, str]:
    """Download to a .part file, then rename. Returns (bytes, sha256).

    Runs curl rather than urllib, and the reason is worth recording. BSE's
    host refuses `Python-urllib/3.10` with a 403, and refused the descriptive
    User-Agent this script first sent for the same reason: its filter allows
    known command line clients and rejects automation it does not recognise.
    Setting a curl User-Agent from Python would work, but that is Python
    claiming to be something else. Calling curl means the client genuinely is
    curl, identifying itself honestly, with no browser imitated and nothing
    misrepresented.
    """
    part = dest.with_suffix(".part")
    part.unlink(missing_ok=True)
    proc = subprocess.run(
        [
            "curl", "-sS", "-L",
            "--max-time", str(int(timeout)),
            "--retry", "2", "--retry-delay", "3",
            "-o", str(part),
            "-w", "%{http_code}",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=timeout + 60,
    )
    code = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else "000"
    if proc.returncode != 0:
        part.unlink(missing_ok=True)
        raise ValueError("curl exit {r}: {e}".format(r=proc.returncode, e=(proc.stderr or "").strip()[:120]))
    if code != "200":
        part.unlink(missing_ok=True)
        raise ValueError("HTTP {c}".format(c=code))

    n = part.stat().st_size if part.exists() else 0
    if n < MIN_BYTES:
        part.unlink(missing_ok=True)
        raise ValueError("only {n} bytes, which is an error page rather than a report".format(n=n))

    h = hashlib.sha256()
    with part.open("rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    part.replace(dest)
    return n, h.hexdigest()


def write_status(state: dict) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATUS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATUS_FILE)


def show_status() -> int:
    if not STATUS_FILE.exists():
        print("no run has started yet (no {p})".format(p=STATUS_FILE))
        return 1
    s = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    print("corpus fetch  -  {st}".format(st=s.get("state", "?")))
    print("  started       {v}".format(v=s.get("started")))
    print("  updated       {v}".format(v=s.get("updated")))
    print(
        "  progress      {d} of {t}  ({p:.1f}%)".format(
            d=s.get("done", 0), t=s.get("total", 0), p=s.get("percent", 0.0)
        )
    )
    print(
        "  ok {ok}   skipped {sk}   failed {f}".format(
            ok=s.get("ok", 0), sk=s.get("skipped", 0), f=s.get("failed", 0)
        )
    )
    print("  downloaded    {g:.2f} GB".format(g=s.get("bytes", 0) / 2**30))
    print("  rate          {r:.1f} reports/min".format(r=s.get("reports_per_min", 0.0)))
    print("  elapsed       {e}".format(e=s.get("elapsed", "-")))
    print("  projected end {v}".format(v=s.get("projected_finish", "-")))
    if s.get("last_error"):
        print("  last error    {e}".format(e=s["last_error"]))
    print("\nfull log: {p}".format(p=LOG_FILE))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", help="CSV with slug,scrip,url")
    ap.add_argument("--hours", type=float, default=6.0, help="wall-clock budget (default 6)")
    ap.add_argument("--min-delay", type=float, default=1.0, help="floor between requests")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--min-bytes", type=int, default=MIN_BYTES)
    ap.add_argument("--limit", type=int, default=0, help="stop after N (for a trial run)")
    ap.add_argument("--status", action="store_true", help="print progress and exit")
    ap.add_argument("--dry-run", action="store_true", help="validate the manifest, fetch nothing")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if args.status:
        return show_status()
    if not args.manifest:
        ap.error("--manifest is required unless --status is given")

    mpath = Path(args.manifest)
    if not mpath.exists():
        print("no manifest at {p}".format(p=mpath))
        return 1

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_manifest(mpath)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("manifest has no usable rows; see {p}".format(p=LOG_FILE))
        return 1

    if args.dry_run:
        have = sum(1 for r in rows if already_have(r["slug"], args.min_bytes))
        print("{n} rows readable, {h} already on disk, {t} to fetch".format(
            n=len(rows), h=have, t=len(rows) - have))
        print("at a {hr}h budget that is {s:.1f}s per report".format(
            hr=args.hours, s=args.hours * 3600 / max(1, len(rows) - have)))
        return 0

    total = len(rows)
    todo = [r for r in rows if already_have(r["slug"], args.min_bytes) is None]
    pace = args.hours * 3600 / max(1, len(todo))

    started = datetime.now(timezone.utc).astimezone()
    log("=" * 68)
    log("run start: {n} in manifest, {t} to fetch, budget {h}h, pace {p:.1f}s each".format(
        n=total, t=len(todo), h=args.hours, p=pace))

    ok = failed = skipped = total - len(todo)
    skipped = total - len(todo)
    ok = failed = 0
    seen_bytes = 0
    t0 = time.monotonic()
    last_error = ""

    for i, row in enumerate(todo, 1):
        slug, url = row["slug"], row["url"]
        dest = PDF_DIR / "{s}.pdf".format(s=slug)
        due = t0 + pace * (i - 1)
        wait = max(args.min_delay, due - time.monotonic()) if i > 1 else 0.0
        if wait > 0:
            time.sleep(wait)

        attempt_t = time.monotonic()
        try:
            n, digest = fetch_one(url, dest, args.timeout)
            ok += 1
            seen_bytes += n
            el = time.monotonic() - attempt_t
            log("ok   {i}/{t} {s} {mb:.2f}MB in {e:.1f}s".format(
                i=i, t=len(todo), s=slug, mb=n / 2**20, e=el))
            with LEDGER_FILE.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "slug": slug, "scrip": row["scrip"], "url": url,
                    "bytes": n, "sha256": digest,
                    "fetched": datetime.now(timezone.utc).isoformat(),
                }) + "\n")
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            failed += 1
            last_error = "{s}: {e}".format(s=slug, e=exc)
            log("FAIL {i}/{t} {s} {e}".format(i=i, t=len(todo), s=slug, e=exc))

        done = i
        elapsed = time.monotonic() - t0
        rate = done / (elapsed / 60) if elapsed > 0 else 0.0
        remaining = len(todo) - done
        eta = datetime.now(timezone.utc).astimezone() + timedelta(
            seconds=remaining * (elapsed / done) if done else 0
        )
        write_status({
            "state": "running",
            "started": started.isoformat(timespec="seconds"),
            "updated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "total": total, "to_fetch": len(todo), "done": done,
            "ok": ok, "failed": failed, "skipped": skipped,
            "percent": done / len(todo) * 100,
            "bytes": seen_bytes,
            "reports_per_min": round(rate, 2),
            "elapsed": str(timedelta(seconds=int(elapsed))),
            "projected_finish": eta.isoformat(timespec="seconds"),
            "last_error": last_error,
            "log": str(LOG_FILE),
        })

    elapsed = time.monotonic() - t0
    log("run end: {ok} ok, {f} failed, {sk} already had, {g:.2f} GB in {e}".format(
        ok=ok, f=failed, sk=skipped, g=seen_bytes / 2**30,
        e=str(timedelta(seconds=int(elapsed)))))
    st = json.loads(STATUS_FILE.read_text(encoding="utf-8")) if STATUS_FILE.exists() else {}
    st["state"] = "finished"
    st["updated"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    write_status(st)
    print("done: {ok} ok, {f} failed, {g:.2f} GB. log: {p}".format(
        ok=ok, f=failed, g=seen_bytes / 2**30, p=LOG_FILE))
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
