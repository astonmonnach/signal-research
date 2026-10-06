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

# On-time starts for the GitHub jobs (kicks.gs)

GitHub's own schedules are "best effort" and can start hours late (on 6 Oct the 22:15 recap started at 02:52 and the
morning briefing hadn't started by 08:40). `kicks.gs` runs every 10 minutes on Google Apps Script and starts each
job at the right London time:
- the morning briefing from 07:45 on weekdays (after the 06:30 research run);
- alerts every 30 minutes from 07:00 to midnight;
- the evening recap from 21:20 on weekdays;
- the press feed every 30 minutes from 07:00 to 23:00.

The GitHub schedules stay on as a backup, and both jobs post at most once a day.

Setup, in the same Apps Script project as the live ALL:
1. On GitHub: your avatar → **Settings → Developer settings → Personal access tokens → Fine-grained tokens →
   Generate new token**. Set **Repository access** to *Only select repositories* → signal-research, and under
   **Permissions → Repository permissions** set **Actions: Read and write**. Generate it and copy it.
2. In Apps Script, click **+** next to Files → **Script**, name it `kicks`, and paste `kicks.gs`.
3. Open **Project Settings → Script properties → Add**: `GITHUB_TOKEN` = the token.
4. Pick **setupKicks** in the function dropdown, press **Run**, and allow it.
