"""Wait for discovery to finish, then download everything it found.

    python -I tools/run_corpus.py --hours 6
    python -I tools/run_corpus.py --status

Discovery and downloading hit different hosts and have to happen in order, so
this chains them without anyone sitting and watching: it polls discovery's
status file, and the moment that run reports finished it starts the fetcher on
the manifest discovery wrote.

Before starting the download it checks free disk space and refuses rather than
filling the drive. Roughly four thousand annual reports at the 13 MB mean
measured over the ten read by hand is about 50 GB, and the mean is high because
those ten are all large caps.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / "corpus"
LOG_FILE = ROOT / "logs" / "chain.log"
DISCOVER_STATUS = ROOT / "discover-status.json"
MANIFEST = ROOT / "manifest.csv"

POLL_SECONDS = 60
MIN_FREE_GB = 100.0


def log(msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write("{s}  {m}\n".format(s=stamp, m=msg))
        fh.flush()


def discovery_state() -> tuple[str, int, int]:
    if not DISCOVER_STATUS.exists():
        return "missing", 0, 0
    try:
        s = json.loads(DISCOVER_STATUS.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return "unreadable", 0, 0
    return s.get("state", "?"), int(s.get("done", 0)), int(s.get("total", 0))


def free_gb(path: Path) -> float:
    return shutil.disk_usage(str(path)).free / 2**30


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=6.0, help="download budget")
    ap.add_argument("--min-delay", type=float, default=1.0)
    ap.add_argument("--max-wait-hours", type=float, default=6.0)
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if args.status:
        state, done, total = discovery_state()
        print("discovery: {s} ({d}/{t})".format(s=state, d=done, t=total))
        rows = 0
        if MANIFEST.exists():
            rows = max(0, len(MANIFEST.read_text(encoding="utf-8").splitlines()) - 1)
        print("manifest rows: {r}".format(r=rows))
        print("free disk: {g:.1f} GB".format(g=free_gb(ROOT)))
        print("chain log: {p}".format(p=LOG_FILE))
        return 0

    log("=" * 68)
    log("chain start: waiting for discovery, then {h}h of downloading".format(h=args.hours))

    deadline = time.monotonic() + args.max_wait_hours * 3600
    while True:
        state, done, total = discovery_state()
        if state == "finished":
            log("discovery finished at {d}/{t}".format(d=done, t=total))
            break
        if state in ("missing", "unreadable"):
            log("no readable discovery status; giving up rather than guessing")
            return 1
        if time.monotonic() > deadline:
            log("discovery still {s} at {d}/{t} after the wait limit; stopping".format(
                s=state, d=done, t=total))
            return 1
        time.sleep(POLL_SECONDS)

    if not MANIFEST.exists():
        log("discovery finished but wrote no manifest")
        return 1
    rows = max(0, len(MANIFEST.read_text(encoding="utf-8").splitlines()) - 1)
    if rows == 0:
        log("manifest is empty; nothing to download")
        return 1

    have = free_gb(ROOT)
    if have < MIN_FREE_GB:
        log("only {g:.1f} GB free, under the {m:.0f} GB floor. Refusing to start.".format(
            g=have, m=MIN_FREE_GB))
        return 1

    log("starting download of {r} reports, {g:.1f} GB free".format(r=rows, g=have))
    proc = subprocess.run(
        [
            sys.executable, "-I", str(HERE / "fetch_corpus.py"),
            "--manifest", str(MANIFEST),
            "--hours", str(args.hours),
            "--min-delay", str(args.min_delay),
        ],
        cwd=str(HERE.parent),
    )
    log("download finished with exit code {c}".format(c=proc.returncode))
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
