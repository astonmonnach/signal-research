"""Send markdown messages to Discord channels and/or Telegram. Standard library only.

Discord: one webhook per channel (channel settings -> Integrations -> Webhooks -> New -> Copy URL).
Add each as a GitHub Actions secret. Any channel without its own webhook falls back to
DISCORD_WEBHOOK_URL, so a single webhook still works.

  DISCORD_WEBHOOK_URL        default / #briefing
  DISCORD_WEBHOOK_CALENDAR   #calendar   (dated events, next 14 days)
  DISCORD_WEBHOOK_LEDGER     #ledger     (every call vs IWM)
  DISCORD_WEBHOOK_PRESS      #press      (company press releases from trusted wires)
  DISCORD_WEBHOOK_FILINGS    #filings    (SEC/DoD triage)
  DISCORD_WEBHOOK_WATCHLIST  #watchlist  (positions, watchlist, peers & commodities)
  DISCORD_WEBHOOK_SETUPS     #setups     (watch-only setups, e.g. supply + listing deficiency)
  DISCORD_WEBHOOK_CRYPTO     #crypto
  DISCORD_WEBHOOK_ALERTS     #alerts     (live watcher, when it exists)

Telegram (optional): TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID get the full briefing only.
WhatsApp isn't supported: it needs a paid Meta Business / Twilio account.
"""
import json, os, time, urllib.request

CHANNELS = ["briefing", "calendar", "ledger", "press", "filings", "watchlist", "setups", "crypto", "alerts"]


def chunks(text, limit):
    out, cur = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:
            out.append(cur); cur = ""; out.append(line[:limit]); line = line[limit:]
        if len(cur) + len(line) > limit:
            out.append(cur); cur = ""
        cur += line
    if cur.strip(): out.append(cur)
    return [c for c in out if c.strip()]


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "signal-lab-briefing"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


def webhook(channel):
    return os.getenv(f"DISCORD_WEBHOOK_{channel.upper()}") or None


def has_own_channel(channel):
    return bool(webhook(channel))


def send_discord(text, url):
    for c in chunks(text, 1900):  # Discord limit is 2000 chars per message
        post(url, {"content": c, "flags": 4})  # 4 = suppress link previews
        time.sleep(1)


def send_telegram(text, token, chat_id):
    for c in chunks(text.replace("**", ""), 4000):
        post(f"https://api.telegram.org/bot{token}/sendMessage",
             {"chat_id": chat_id, "text": c, "disable_web_page_preview": True})
        time.sleep(1)


def send(text, channel="briefing"):
    """Send to a channel's own webhook, else (briefing only) the default webhook + Telegram."""
    sent = []
    url = webhook(channel) or (os.getenv("DISCORD_WEBHOOK_URL") if channel == "briefing" else None)
    if url:
        try: send_discord(text, url); sent.append(f"discord#{channel}")
        except Exception as e: print(f"discord #{channel} failed:", e)
    if channel == "briefing" and os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        try: send_telegram(text, os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]); sent.append("telegram")
        except Exception as e: print("telegram failed:", e)
    return sent
