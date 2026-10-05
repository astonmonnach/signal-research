"""Discord server setup: check which channels have a webhook, and post each channel's intro. No emojis.

  python briefing/discord_setup.py --check   # lists configured / missing channels (never prints a URL)
  python briefing/discord_setup.py --intro   # welcome guide to #start-here, a short intro to every other channel

Run it from GitHub: Actions -> "discord-setup" -> Run workflow (it reads the DISCORD_WEBHOOKS secret).

Server layout (category: channel = webhook name in DISCORD_WEBHOOKS):
  INFO           #start-here = start, #chat (no webhook)
  STRATEGIES     #all (live, Google Apps Script: live/all_live.gs), #calls = calls, #trades-open = positions,
  (the IBKR      #gov-filings = govfilings, #overhang = overhang, #spinoff = spinoff, #setups = setups,
   watchlists)   #long-term = longterm
  BY SIZE        #micro-caps = microcaps, #small-caps = smallcaps, #mid-caps = midcaps, #large-caps = largecaps
  RECAPS         #briefing = briefing, #daily-recap = dailyrecap, #weekly-recap = weeklyrecap, #calendar = calendar
  RESEARCH FEED  #filings = filings, #press = press, #ledger = ledger
  CRYPTO         #crypto = crypto
"""
import json, sys
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
             f"New and closed calls are posted as they happen; marks after every close.",
    "positions": "**#trades-open**\nOpen trades after each US close (the IBKR \"TRADES open\" list): price against entry, P&L after all "
                 "fees, move against IWM, distance to the exit line, and the next thesis check.",
    "govfilings": "**#gov-filings**\nThe IBKR \"Gov Filings pipeline findings\" list: stocks the SEC and DoD filing pipeline found. After each "
                  "close: a table, then each stock's verdict, thesis, next dated event, funding-pot status and its latest SEC filings as links.",
    "overhang": "**#overhang**\nThe IBKR \"STRAT overhang\" list: registered share supply (resale S-1s, lock-up expiries) waiting to hit "
                "the market. The test is to buy only after the supply has been absorbed. Updated after each close, with SEC links.",
    "spinoff": "**#spinoff**\nThe IBKR \"STRAT spinoff\" list: spin-offs and their parents. Forced index and holder selling in the first "
               "weeks, then the re-rating test. Updated after each close, with SEC links.",
    "microcaps": size("micro-caps", "under $300M", "IWM"),
    "smallcaps": size("small-caps", "of $300M to $2B", "IWM"),
    "midcaps": size("mid-caps", "of $2B to $10B", "MDY (S&P MidCap 400)"),
    "largecaps": size("large-caps", "over $10B", "SPY"),
    "longterm": f"**#long-term**\nMedium and long-term research (6 to 36 months). The same nth-order method plus six long-term gates: "
                f"the theme is in reported numbers, the balance sheet survives two bad years, dilution, not already run, liquidity, "
                f"and it is measured against SPY. New research is posted when it is added; a summary every Monday.",
    "setups": "**#setups**\nThe IBKR \"SETUP supply+deficiency\" list. Watch only, not buys. Warning patterns: fresh share supply plus "
              "an exchange deficiency, usually under $1. Most of them collapse. Updated after each close, with spikes or collapses flagged.",
    "briefing": "**#briefing**\nThe morning briefing before the US open: new SEC filings, press releases, positions, watchlist, setups, "
                "ledger, crypto and the next 14 days, all in one post.",
    "dailyrecap": "**#daily-recap**\nAfter each US close: the market and key inputs (steel, copper, gold, silver, oil), the calls, "
                  "positions, the best and worst watchlist stocks against the market, each size bucket, and what is dated for the next session.",
    "weeklyrecap": "**#weekly-recap**\nEvery Friday after the close: the week for every watchlist stock against its benchmark, the calls, "
                   f"positions, and next week's dated events.",
    "calendar": "**#calendar**\nStock events for the next 14 days, every morning: earnings, votes, lock-ups, index changes, deadlines.",
    "filings": "**#filings**\nNew SEC filings and DoD contract awards worth reading, with notes. Every morning.",
    "press": "**#press**\nCompany press releases from trusted wires only (GlobeNewswire, PR Newswire, Business Wire, company IR). Every morning.",
    "ledger": f"**#ledger**\nEvery scan item measured against IWM. This is how we find out which patterns work before trusting any of them. "
              f"Every morning.",
    "crypto": "**#crypto**\nTrending-token research. So far the median trending token is down about 85% within 24 hours, so read it as a warning feed.",
    "alerts": "**#alerts**\nLive alerts during market hours (not built yet).",
}

START_HERE = f"""# Start here
Everything in this server is posted automatically by a research pipeline.
It is a research log, **not financial advice**. Nothing here tells anyone to buy or sell.

**STRATEGIES** (the same lists as the broker watchlists)
- **#all**: every watchlist stock in one live table, updated every 5 minutes while the US market is open
- **#calls**: public calls with the exit price and review date stated up front, measured against the market. Losers stay on the record
- **#trades-open**: open trades and P&L after fees
- **#gov-filings**: what the SEC and DoD filing pipeline found
- **#overhang**: share supply waiting to hit the market
- **#spinoff**: spin-offs and their parents
- **#setups**: watch only. Warning patterns, not buys
- **#long-term**: 6 to 36 month research

**BY SIZE**
- **#micro-caps** under $300M · **#small-caps** $300M to $2B · **#mid-caps** $2B to $10B · **#large-caps** over $10B

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
        # Each channel is introduced once (briefing/introduced.json), so re-running after adding channels only
        # posts to the new ones. --all re-posts everywhere.
        done_p = Path(__file__).resolve().parent / "introduced.json"
        done = set(json.loads(done_p.read_text(encoding="utf-8"))) if done_p.exists() and "--all" not in sys.argv else set()
        for ch in have:
            text = START_HERE if ch == "start" else INTRO.get(ch)
            if not text or ch in done:
                continue
            sent = notify.send(text, ch)
            print(f"#{ch}: {'posted' if sent else 'FAILED (check that webhook)'}")
            if sent: done.add(ch)
        done_p.write_text(json.dumps(sorted(done), indent=1), encoding="utf-8")
    if not have:
        sys.exit("No webhooks found. Add the DISCORD_WEBHOOKS secret (one 'name=url' line per channel).")


if __name__ == "__main__":
    main()
