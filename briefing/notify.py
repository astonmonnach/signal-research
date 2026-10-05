"""Send markdown messages to Discord channels and/or Telegram. Standard library only.

Discord: one webhook per channel (channel settings -> Integrations -> Webhooks -> New Webhook ->
Copy Webhook URL). The quick way is ONE GitHub Actions secret, DISCORD_WEBHOOKS, holding one line
per channel:

  briefing=https://discord.com/api/webhooks/...
  calls=https://discord.com/api/webhooks/...
  longterm=https://discord.com/api/webhooks/...

Channel names (briefing/discord_setup.py says what each one gets):
  start, briefing, calls, longterm, watchlist, calendar, filings, press, setups, ledger, reports, crypto, alerts
A separate DISCORD_WEBHOOK_<CHANNEL> secret still works and wins over the list. DISCORD_WEBHOOK_URL is
the old single-webhook fallback for #briefing. A channel with no webhook isn't posted on its own, but
its section is still in the full #briefing post.

Telegram (optional): TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID get the full briefing only.
WhatsApp isn't supported: it needs a paid Meta Business / Twilio account.
Never print a webhook URL: anyone holding one can post to that channel.
"""
import json, os, time, urllib.request

CHANNELS = ["start", "briefing", "calls", "longterm", "watchlist", "calendar", "filings", "press", "setups", "ledger",
            "reports", "crypto", "alerts"]
_ALIASES = {"long-term": "longterm", "long_term": "longterm", "start-here": "start", "starthere": "start"}


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


def _name(raw):
    n = raw.strip().lower().lstrip("#-*• ").strip()
    n = n.split()[-1] if n.split() else n          # tolerate "📈 calls"-style emoji prefixes
    n = _ALIASES.get(n, n).lstrip("#")
    return n.replace("-", "")


def webhook_map():
    """DISCORD_WEBHOOKS: 'name=url' lines (also 'name: url', or a JSON object). Other lines are skipped."""
    raw = os.getenv("DISCORD_WEBHOOKS", "").strip()
    if not raw: return {}
    if raw.startswith("{"):
        try: return {_name(k): str(v).strip() for k, v in json.loads(raw).items()}
        except Exception: return {}
    out = {}
    for line in raw.splitlines():
        i = line.find("https://")
        if i <= 0: continue
        name, url = line[:i].strip().rstrip("=:").strip(), line[i:].strip().strip("\"',")
        if name and "/api/webhooks/" in url: out[_name(name)] = url
    return out


def webhook(channel):
    return os.getenv(f"DISCORD_WEBHOOK_{channel.upper()}") or webhook_map().get(channel) or None


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
