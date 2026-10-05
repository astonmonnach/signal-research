"""Send markdown messages to Discord channels and/or Telegram. Standard library only.

Discord: one webhook per channel (channel settings -> Integrations -> Webhooks -> New Webhook ->
Copy Webhook URL). The quick way is ONE GitHub Actions secret, DISCORD_WEBHOOKS, holding one line
per channel:

  briefing=https://discord.com/api/webhooks/...
  calls=https://discord.com/api/webhooks/...
  longterm=https://discord.com/api/webhooks/...

Channel names (briefing/discord_setup.py has the server layout and what each one gets; #trades-open = positions):
  start, calls, positions, govfilings, overhang, spinoff, setups, longterm, microcaps, smallcaps, midcaps, largecaps,
  briefing, dailyrecap, weeklyrecap, calendar, filings, press, ledger, crypto, alerts
Hyphens are ignored, so "micro-caps" or "daily-recap" work too.
To add channels later, put just the new lines in DISCORD_WEBHOOKS_2 (then _3, _4, _5): no re-pasting.
A separate DISCORD_WEBHOOK_<CHANNEL> secret still works and wins over the list. DISCORD_WEBHOOK_URL is
the old single-webhook fallback for #briefing. A channel with no webhook isn't posted on its own, but
its section is still in the full #briefing post.

Telegram (optional): TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID get the full briefing only.
WhatsApp isn't supported: it needs a paid Meta Business / Twilio account.
Never print a webhook URL: anyone holding one can post to that channel.
"""
import json, os, re, time, urllib.request

CHANNELS = ["start", "calls", "positions", "govfilings", "overhang", "spinoff", "setups", "longterm",
            "microcaps", "smallcaps", "midcaps", "largecaps", "briefing", "dailyrecap", "weeklyrecap", "calendar",
            "filings", "press", "ledger", "crypto", "alerts"]
# #all is not here: its one live message is edited by Google Apps Script (live/all_live.gs), not GitHub.
_ALIASES = {"starthere": "start", "micro": "microcaps", "small": "smallcaps", "mid": "midcaps", "large": "largecaps",
            "daily": "dailyrecap", "weekly": "weeklyrecap", "position": "positions", "openpositions": "positions",
            "tradesopen": "positions", "trades": "positions", "called": "calls", "govfilingspipelinefindings": "govfilings",
            "gov": "govfilings", "stratoverhang": "overhang", "stratspinoff": "spinoff", "spinoffs": "spinoff"}
# No emojis or pictographs in anything posted (his rule): stripped here as a last line of defence.
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿️‍]+ ?")


REPO_BLOB = "github.com/astonmonnach/signal-research/blob/main/"
_LINK = re.compile(r"(\[[^\]\n]*\]\(<?https?://[^)\s]+>?\))|<(https?://[^>\s]+)>|(?<![(\[<])(https?://[^\s)>\]]+)")
_HOSTS = [("sec.gov/Archives", "SEC filing"), ("sec.gov", "SEC EDGAR"), ("usaspending.gov", "USAspending"),
          ("prnewswire.com", "PR Newswire"), ("globenewswire.com", "GlobeNewswire"), ("businesswire.com", "Business Wire"),
          ("war.gov", "DoD contracts"), ("defense.gov", "DoD contracts"), ("govinfo.gov", "govinfo"),
          ("raw.githubusercontent.com", "Calendar subscription"), ("x.com", "X post"), ("twitter.com", "X post")]
_REPO_NAMES = {"calls/README.md": "Calls record", "ledger/LEDGER.md": "Ledger", "stocks/README.md": "Dossiers",
               "longterm/README.md": "Long-term table", "longterm/METHOD.md": "Long-term method"}


def label_for(url):
    """A short name for a link, so Discord shows "SEC filing" or "Ledger" instead of a long URL."""
    if REPO_BLOB in url or "github.com/astonmonnach/signal-research/tree/main/" in url:
        path = url.split("/main/", 1)[1]
        if path in _REPO_NAMES: return _REPO_NAMES[path]
        m = re.match(r"stocks/(\w+)\.md", path)
        if m: return f"{m.group(1)} dossier"
        m = re.match(r"(recaps/daily|briefings)/(\d{4}-\d\d-\d\d)\.md", path)
        if m: return ("Recap " if "recap" in m.group(1) else "Briefing ") + m.group(2)
        m = re.match(r"reports/(weekly|monthly|quarterly)/([\w-]+)\.md", path)
        if m: return f"{m.group(1).title()} report {m.group(2)}"
        return path.rstrip("/").split("/")[-1].replace(".md", "") or "Repo"
    host = next((name for h, name in _HOSTS if h in url), None)
    return host or re.sub(r"^https?://(www\.)?", "", url).split("/")[0]


_OWN = ("github.com/astonmonnach", "raw.githubusercontent.com/astonmonnach")


def shorten_links(text):
    """Bare or <angle-bracket> URLs become masked links ([label](url)); existing [text](url) links are kept.
    Links to our own repo are removed entirely (his rule, 6 Oct 2026: no repo links in Discord); primary sources
    such as SEC filings and press releases stay, with short labels."""
    def rep(m):
        url = m.group(1) or m.group(2) or m.group(3)
        if any(o in url for o in _OWN): return ""
        if m.group(1): return m.group(1)
        url, trail = m.group(2) or m.group(3), ""
        while m.group(3) and url[-1] in ".,;:!?'\"":         # sentence punctuation after a bare link
            url, trail = url[:-1], url[-1] + trail
        return f"[{label_for(url)}]({url}){trail}"
    out, in_code = [], False
    for line in text.split("\n"):                      # never touch tables inside ``` blocks
        if line.strip().startswith("```"): in_code = not in_code
        if in_code:
            out.append(line); continue
        new = _LINK.sub(rep, line)
        if new != line:                                # tidy what a removed link leaves behind
            new = re.sub(r"(\s*·\s*)+$", "", re.sub(r"^(\s*[-*]?\s*)(·\s*)+", r"\1", re.sub(r"(·\s*){2,}", "· ", new))).rstrip()
            if re.fullmatch(r"\s*[-*]?\s*([\w ]+:)?\s*", new): continue
        out.append(new)
    return "\n".join(out)


def plain(text):
    """Remove emojis (and the space after one), so '**X Calls**' style headings stay valid markdown,
    and give every bare link a short label."""
    return shorten_links(_EMOJI.sub("", text))


def chunks(text, limit):
    """Split on line boundaries under Discord's limit. A split inside a ``` table closes it and reopens it
    in the next message, so a table never turns into raw text."""
    out, cur, in_code = [], "", False
    for line in text.splitlines(keepends=True):
        while len(line) > limit:
            out.append(cur); cur = ""; out.append(line[:limit]); line = line[limit:]
        if len(cur) + len(line) + 4 > limit:
            out.append(cur + ("```" if in_code else "")); cur = "```\n" if in_code else ""
        cur += line
        if line.strip().startswith("```"): in_code = not in_code
    if cur.strip(): out.append(cur)
    return [c for c in out if c.strip() and c.strip() != "```"]


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


def _parse(raw):
    raw = (raw or "").strip()
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


def webhook_map():
    """DISCORD_WEBHOOKS, then DISCORD_WEBHOOKS_2 ... _5: 'name=url' lines (also 'name: url', or a JSON object).
    Extra secrets mean new channels can be added without re-pasting the old ones (GitHub never shows a secret
    again). A later secret wins if the same name appears twice."""
    out = {}
    for key in ["DISCORD_WEBHOOKS"] + [f"DISCORD_WEBHOOKS_{i}" for i in range(2, 6)]:
        out.update(_parse(os.getenv(key)))
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
    """Send to a channel's own webhook, else (briefing only) the default webhook + Telegram. Emojis are removed."""
    sent, text = [], plain(text)
    url = webhook(channel) or (os.getenv("DISCORD_WEBHOOK_URL") if channel == "briefing" else None)
    if url:
        try: send_discord(text, url); sent.append(f"discord#{channel}")
        except Exception as e: print(f"discord #{channel} failed:", e)
    if channel == "briefing" and os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        try: send_telegram(text, os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]); sent.append("telegram")
        except Exception as e: print("telegram failed:", e)
    return sent
