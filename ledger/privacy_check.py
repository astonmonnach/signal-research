"""Privacy check for this public repo (rule 2026-11-24): no personal details in tracked files.

Fails on: the owner's local username or home paths, local Desktop paths, personal email addresses,
account funding or balance lines, and personal trade sizes in pounds. Market data and quoted filings
(research/evidence, research/rumours, data/) are skipped for the pound check because they quote
companies, not the owner.

Run:  python ledger/privacy_check.py      (prints problems; exit 1 if any)
Run it before every commit (SKILL.md step 10).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = [
    ("local username or home path", re.compile(r"Users[\\/]thoma\b|C--Users-thoma", re.I)),
    ("local Desktop path", re.compile(r"\bDesktop[\\/]")),
    ("personal email", re.compile(r"[\w.+-]+@(gmail|hotmail|outlook|icloud|yahoo)\.(com|co\.uk)", re.I)),
    ("account funding or balance", re.compile(r"Fund accounts|net_liquidation|buying_power|test account", re.I)),
    ("personal trade size in pounds", re.compile(r"£\s?\d{2,3}(?![\d,.])")),
    ("git conflict marker", re.compile(r"^(<{7}|>{7}) ", re.M)),
]
POUND_SKIP = ("research/evidence/", "research/rumours/", "data/")
FILE_SKIP = ("ledger/privacy_check.py", "data/crypto/c2_panel.json")  # the frozen C2 panel is not edited


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
    out = []
    for f in files:
        if not f or f in FILE_SKIP or f.endswith((".png", ".jpg", ".parquet", ".gz", ".zip")):
            continue
        try:
            text = (ROOT / f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for name, rx in CHECKS:
            if name.startswith("personal trade size") and f.startswith(POUND_SKIP):
                continue
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                out.append(f"{f}:{line}: {name}: {m.group(0)!r}")
    print("\n".join(out) if out else "privacy: no personal details found")
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
