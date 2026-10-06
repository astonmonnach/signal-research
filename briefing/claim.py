"""Claim a once-only send BEFORE sending, so a later failure can never cause a repost.

Lesson of 6 Oct 2026: the morning briefing posted, then the job's commit step failed, so the "sent today" marker was
lost and the next five runs posted the same briefing again. Now the marker is committed and pushed first:

    if claim("briefings/.sent-2026-10-06"):   # True only if this run pushed the marker and nobody had before
        send(...)

If the push fails, or another run already claimed it, nothing is sent. Outside a git checkout with a remote (local dry
runs), it falls back to the local marker file only.
"""
import subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOT = ["-c", "user.name=signal-lab-bot", "-c", "user.email=signal-lab-bot@users.noreply.github.com"]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def claim(rel, note="claimed"):
    path = ROOT / rel
    if git("remote").stdout.strip() == "":                 # no remote: local-only behaviour
        if path.exists(): return False
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(note + "\n", encoding="utf-8")
        return True
    for attempt in range(5):
        git("pull", "--rebase", "--autostash", "-X", "theirs", "-q")
        if path.exists():
            return False                                    # someone already sent it
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(note + "\n", encoding="utf-8")
        git("add", "-f", rel)
        git(*BOT, "commit", "-q", "-m", f"claim {rel}", "--", rel)
        if git("push", "-q").returncode == 0:
            return True
        git("reset", "-q", "--soft", "HEAD~1")               # undo our claim commit and retry on fresh main
        git("restore", "--staged", rel); path.unlink(missing_ok=True)
        time.sleep(3 * (attempt + 1))
    return False
