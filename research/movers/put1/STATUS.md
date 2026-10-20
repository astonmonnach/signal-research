# PUT1 status: finished on 20 Oct 2026

Pre-registration: `research/movers/PREREG_PUT1.md` (git 60e910c). Nothing in the method, sample, contract choice, entry, costs, exits or pass marks changed. Results: `RESULTS.md`.

## Verdict
T1 does not pay. It fails all three pass marks. Mean after 10% costs -31.2% (n 103). 95% interval -47.0% to -14.6%. Halves -33.7% and -28.3%. T2 (comparison only): -22.6% (n 95).

## How the run went
- 19 Oct: sample drawn (300 T1, 150 T2). 300 Massive responses cached, 162 T1 events finished, then paused for the night. The interim state is kept in `cache/progress.csv` and `cache/interim_2026-10-19.json`.
- 20 Oct: resumed with the procedure below. 631 more calls, 5 a minute, no rate-limit errors. 630 were saved; one split call was refused by the connector (deviation 10). `python run.py plan` then reported `missing 0`, and `python run.py` built `trades_T1.csv`, `trades_T2.csv` and `results.json`. `RESULTS.md` was written from those.
- All 450 events have a final status. None are pending.

## Deviations
The full list is in `RESULTS.md` under Deviations (15 items). Items 1 to 9 were first listed in the 19 Oct pause report. Until now they were not written into this file. Items 10 to 15 are new on 20 Oct:
- 10: split records came from `/stocks/v1/splits`, because the connector refuses `/v3/reference/splits`. `ingest.py` maps that path to the same cache file.
- 11: responses were saved through `ingest.py`'s transcript method, with this session's transcript passed by path.
- 12: `RESULTS.md` was written by Claude from `results.json` and the trades files. `run.py` has no writer.
- 13: in `results.json`, T1 `put_listed` (134) counts 2 events never looked up. The true count is 132.
- 14: the stock's own return is MV1's `ret20_net`, missing for 3 used events per test.
- 15: premium share = entry VWAP before costs / gain-day close.

## To rebuild
```
cd C:/Users/thoma/catalyst-research/research/movers/put1 && PYTHONIOENCODING=utf-8 python run.py
```
It reads only `cache/` and local files. `python run.py plan 5 0` should print `missing 0`.

## How the cache was filled (for reference)
Each step: make the 5 calls the last `plan` printed (Massive connector `call_api`, exactly as printed), then in the same message run:
```
cd C:/Users/thoma/catalyst-research/research/movers/put1 && PYTHONIOENCODING=utf-8 python ingest.py <this session's transcript .jsonl> && PYTHONIOENCODING=utf-8 python run.py plan 5
```
Pass the transcript path when other agents are running. With no argument, `ingest.py` reads the four newest transcripts of the project.
