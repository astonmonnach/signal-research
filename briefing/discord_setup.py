"""Discord server setup: check which channels have a webhook, and post each channel's intro. No emojis.

  python briefing/discord_setup.py --check   # lists configured / missing channels (never prints a URL)
  python briefing/discord_setup.py --intro   # welcome guide to #start-here, a short intro to every other channel

Run it from GitHub: Actions -> "discord-setup" -> Run workflow (it reads the DISCORD_WEBHOOKS secret).

Server layout (category: channel = webhook name in DISCORD_WEBHOOKS):
  INFO           #start-here = start, #chat (no webhook)
  CALLS          #calls = calls, #positions = positions
  WATCHLISTS     #micro-caps = microcaps, #small-caps = smallcaps, #mid-caps = midcaps, #large-caps = largecaps,
                 #long-term = longterm, #setups = setups
  RECAPS         #briefing = briefing, #daily-recap = dailyrecap, #weekly-recap = weeklyrecap, #calendar = calendar
  RESEARCH FEED  #filings = filings, #press = press, #ledger = ledger
  CRYPTO         #crypto = crypto
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notify  # noqa: E402

REPO = "https://github.com/astonmonnach/signal-research"
BLOB = REPO + "/blob/main"


def size(name, rng, bench):
    return (f"**#{name}**\nWatchlist stocks with a market cap {rng}. After each US close: a table of every stock "
            f"(close, day move, move against {bench}, 5-day move, move since we found it), then one line each with our verdict, "
            f"the thesis and the next dated event. Moves include cash and spun-off shares received.")


INTRO = {
    "calls": f"**#calls**\nThe public calls. Each call states its exit price and review date before it starts, is measured from the "
             f"first open after it was posted against the market and one similar stock, and stays on the record win or lose. "
             f"New and closed calls are posted as they happen; marks after every close.\nRecord: <{BLOB}/calls/README.md>",
    "positions": "**#positions**\nOpen positions after each US close: price against entry, P&L after all fees, move against IWM, "
                 "distance to the exit line, and the next thesis check.",
    "microcaps": size("micro-caps", "under $300M", "IWM"),
    "smallcaps": size("small-caps", "of $300M to $2B", "IWM"),
    "midcaps": size("mid-caps", "of $2B to $10B", "MDY (S&P MidCap 400)"),
    "largecaps": size("large-caps", "over $10B", "SPY"),
    "longterm": f"**#long-term**\nMedium and long-term research (6 to 36 months). The same nth-order method plus six long-term gates: "
                f"the theme is in reported numbers, the balance sheet survives two bad years, dilution, not already run, liquidity, "
                f"and it is measured against SPY. New research is posted when it is added; a summary every Monday.\n"
                f"Method: <{BLOB}/longterm/METHOD.md>",
    "setups": "**#setups**\nWatch only, not buys. Warning patterns: fresh share supply plus an exchange deficiency, usually under $1. "
              "Most of them collapse. Updated after each close, with any spike or collapse flagged.",
    "briefing": "**#briefing**\nThe morning briefing before the US open: new SEC filings, press releases, positions, watchlist, setups, "
                "ledger, crypto and the next 14 days, all in one post.",
    "dailyrecap": "**#daily-recap**\nAfter each US close: the market and key inputs (steel, copper, gold, silver, oil), the calls, "
                  "positions, the best and worst watchlist stocks against the market, each size bucket, and what is dated for the next session.",
    "weeklyrecap": "**#weekly-recap**\nEvery Friday after the close: the week for every watchlist stock against its benchmark, the calls, "
                   f"positions, and next week's dated events. Full weekly reports: <{REPO}/tree/main/reports/weekly>",
    "calendar": "**#calendar**\nStock events for the next 14 days, every morning: earnings, votes, lock-ups, index changes, deadlines. "
                "Subscribe in any calendar app: <https://raw.githubusercontent.com/astonmonnach/signal-research/main/calendar/catalyst-dates.ics>",
    "filings": "**#filings**\nNew SEC filings and DoD contract awards worth reading, with notes. Every morning.",
    "press": "**#press**\nCompany press releases from trusted wires only (GlobeNewswire, PR Newswire, Business Wire, company IR). Every morning.",
    "ledger": f"**#ledger**\nEvery scan item measured against IWM. This is how we find out which patterns work before trusting any of them. "
              f"Every morning.\nFull table: <{BLOB}/ledger/LEDGER.md>",
    "crypto": "**#crypto**\nTrending-token research. So far the median trending token is down about 85% within 24 hours, so read it as a warning feed.",
    "alerts": "**#alerts**\nLive alerts during market hours (not built yet).",
}

START_HERE = f"""# Start here
Everything in this server is posted automatically by a research pipeline. The code and every past post are public: <{REPO}>
It is a research log, **not financial advice**. Nothing here tells anyone to buy or sell.

**CALLS**
- **#calls**: public calls with the exit price and review date stated up front, measured against the market. Losers stay on the record.
- **#positions**: open positions and P&L after fees.

**WATCHLISTS** (same headings as the broker watchlists)
- **#micro-caps**: under $300M
- **#small-caps**: $300M to $2B
- **#mid-caps**: $2B to $10B
- **#large-caps**: over $10B
- **#long-term**: 6 to 36 month research
- **#setups**: watch only. Warning patterns, not buys

**RECAPS**
- **#briefing**: before the US open
- **#daily-recap**: after the US close
- **#weekly-recap**: Fridays after the close
- **#calendar**: stock events, next 14 days

**RESEARCH FEED**
- **#filings**: SEC filings and DoD contracts worth reading
- **#press**: press releases from trusted wires
- **#ledger**: every scan item against the market (which patterns actually work)

**CRYPTO**
- **#crypto**: trending-token research, mostly a warning feed

**How to read it**
- The result is the spread, not the return. A stock up 5% on a day the market is up 5% did nothing.
- One winner proves nothing. Calls are judged after 20 or more, against the market.
- For most long-term investors a broad index fund is the core; single stocks are the small part.
- Talk in **#chat**. The other channels are the feed.
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
