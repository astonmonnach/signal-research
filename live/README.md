# Live ALL watchlist in Discord

`all_live.gs` keeps **one message** in Discord **#all** up to date. It is edited every 5 minutes while the US market
is open (09:25–16:05 New York), with one final update after the close. It runs free on Google Apps Script, so it
doesn't need your PC switched on or any GitHub Actions minutes.

The tickers are the same as the IBKR **ALL** list, read from `watch/watchlist.json`: add a stock there and it shows
up here. Prices come from Yahoo Finance and can be up to 15 minutes delayed.

## Setup (about 5 minutes, once)

1. In Discord, create **#all** (read-only for members) and make a webhook for it. Copy the URL.
2. Go to [script.google.com](https://script.google.com), click **New project**, and paste the whole of `all_live.gs`
   over the default code. Save it and name it something like "ALL live".
3. Open **Project Settings** (the gear icon) and go to **Script properties** → **Add script property**:
   `WEBHOOK_ALL` = the webhook URL.
4. Back in the editor, pick **setup** in the function dropdown, then press **Run** and allow the permissions.
   This posts the message and starts the 5-minute timer. Pin the message in Discord.

To stop it, run **teardown**. If the repo goes private, also add a `TICKERS` property (for example
`MTUS,PUSA,ELMT`), because the script can't read a private repo.
