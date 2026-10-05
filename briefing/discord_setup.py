"""Discord server setup: check which channels have a webhook, and post each channel's intro.

  python briefing/discord_setup.py --check   # lists configured / missing channels (never prints a URL)
  python briefing/discord_setup.py --intro   # posts the welcome guide to #start-here and a one-line intro to every other channel

Run it from GitHub: Actions -> "discord-setup" -> Run workflow (it reads the DISCORD_WEBHOOKS secret).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notify  # noqa: E402

REPO = "https://github.com/astonmonnach/signal-research"

INTRO = {
    "briefing": "☀️ **#briefing**: the whole morning briefing in one post, weekday mornings. Every other channel gets its own slice of it.",
    "calls": "📈 **#calls**: the public calls. Each one is stated with its exit price and review date before it starts, measured from the "
             "next open against the market and one similar stock, and kept on the record win or lose. New calls and closed calls are posted "
             f"here, with daily marks in the morning. Record: <{REPO}/blob/main/calls/README.md>",
    "longterm": "🌳 **#long-term**: medium/long-term research (6–36 months). Same nth-order method, plus extra checks: the theme must show up "
                "in reported revenue, the balance sheet has to survive two bad years, dilution, and whether it has already run. "
                f"Weekly update on Mondays. <{REPO}/blob/main/longterm/README.md>",
    "watchlist": "👀 **#watchlist**: positions, watchlist moves, peers and the commodity prices behind them, weekday mornings.",
    "calendar": "📅 **#calendar**: dated events for the next 14 days (earnings, votes, deadlines, lock-ups). "
                f"Subscribe in any calendar app: <https://raw.githubusercontent.com/astonmonnach/signal-research/main/calendar/catalyst-dates.ics>",
    "filings": "📄 **#filings**: new SEC filings and DoD contract awards worth reading, with notes.",
    "press": "📰 **#press**: company press releases from trusted wires only (GlobeNewswire, PR Newswire, Business Wire, company IR).",
    "setups": "⚠️ **#setups**: WATCH ONLY, not buys. Warning patterns such as fresh share supply plus an exchange deficiency: most of them collapse.",
    "ledger": f"🧾 **#ledger**: every scan item measured against the market (IWM). This is how we find out which patterns actually work. <{REPO}/blob/main/ledger/LEDGER.md>",
    "reports": f"🗂️ **#reports**: weekly summary every Monday; monthly and quarterly reports in the repo. <{REPO}/tree/main/reports>",
    "crypto": "🪙 **#crypto**: trending-token research. So far the median trending token is down ~85% within 24 hours. Treat it as a warning feed.",
    "alerts": "🚨 **#alerts**: live alerts during market hours (coming later).",
}

START_HERE = f"""# 👋 Start here
Everything in this server is posted automatically by a research pipeline. The code and every past post are public: <{REPO}>
It's a research log, **not financial advice**. Nothing here tells anyone to buy or sell.

**📈 Calls**
- **#calls**: the public calls. Exit price and review date are stated up front, each call is measured against the market, and losers stay on the record.
- **#long-term**: 6–36 month research, using the nth-order method plus balance-sheet, dilution and "already run" checks. Updated Mondays.

**☀️ Daily** (weekday mornings)
- **#briefing**: everything in one post
- **#watchlist**: watchlist moves, peers, commodity prices
- **#calendar**: the next 14 days of dated events

**🔎 Research feed**
- **#filings**: SEC filings and DoD contracts worth reading
- **#press**: press releases from trusted wires
- **#setups**: ⚠️ watch only. These are warning patterns, not buys
- **#ledger**: every scan item vs the market (which patterns actually work)
- **#reports**: weekly summary on Mondays

**🪙 #crypto**: trending-token research (mostly a warning feed)

**How to read it**
- *The result is the spread, not the return.* A stock up 5% on a day the market is up 5% did nothing.
- One winner proves nothing. Calls are judged after 20+, against the market.
- Most long-term money usually goes into a broad index fund. Single stocks are the small part.
- 💬 Talk in **#chat**. The other channels are for the feed.
"""


def configured():
    return [c for c in notify.CHANNELS if notify.webhook(c)], [c for c in notify.CHANNELS if not notify.webhook(c)]


def main():
    have, missing = configured()
    print("configured:", ", ".join(have) or "none")
    print("missing:   ", ", ".join(missing) or "none", "(alerts is optional until the live watcher exists)")
    if "--intro" in sys.argv:
        for ch in have:
            text = START_HERE if ch == "start" else INTRO.get(ch)
            if text:
                sent = notify.send(text, ch)
                print(f"#{ch}: {'posted' if sent else 'FAILED (check that webhook)'}")
    if not have:
        sys.exit("No webhooks found. Add the DISCORD_WEBHOOKS secret (one 'name=url' line per channel).")


if __name__ == "__main__":
    main()
