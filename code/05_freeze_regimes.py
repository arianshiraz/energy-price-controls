"""Freeze record for the coded regimes (regime coding rule, section 7).

  py -3 code/05_freeze_regimes.py write   writes data/classification/freeze_manifest.csv (SHA-256 of each coded file, line endings normalised to LF)
  py -3 code/05_freeze_regimes.py check   stops with an error if any coded file differs from the manifest

Estimation scripts call check() before reading regimes.csv, so a change to the coded files after the
freeze cannot pass silently; such a change must be logged as a dated amendment and the manifest rewritten
in a separate commit.
"""
import csv
import hashlib
import sys
from pathlib import Path

CLS = Path(__file__).resolve().parents[1] / "data" / "classification"
FILES = ["regime_measures.csv", "regime_baseline.csv", "regimes.csv", "not_coded_measures.csv",
         "tracker_reconciliation.csv"]
MANIFEST = CLS / "freeze_manifest.csv"


def sha(p):
    # Line endings are normalised to LF so the hash is the same on any checkout (Git may convert them).
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def write(date):
    """Files whose checksum is unchanged keep their original frozen_on date; changed files get `date`
    (each such rewrite follows a dated amendment to the coding rule)."""
    old = {r["file"]: r for r in csv.DictReader(open(MANIFEST, encoding="utf-8"))} if MANIFEST.exists() else {}
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "bytes", "sha256", "frozen_on"])
        for n in FILES:
            h = sha(CLS / n)
            keep = n in old and old[n]["sha256"] == h
            w.writerow([n, (CLS / n).stat().st_size, h, old[n]["frozen_on"] if keep else date])
    print(f"manifest written for {len(FILES)} files")


def check():
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    bad = [r["file"] for r in rows if sha(CLS / r["file"]) != r["sha256"]]
    if bad:
        raise SystemExit(f"coded files changed since the freeze: {bad}")
    print(f"freeze intact ({len(rows)} files, frozen on {rows[0]['frozen_on']})")


if __name__ == "__main__":
    if sys.argv[1] == "write":
        write(sys.argv[2])
    else:
        check()
