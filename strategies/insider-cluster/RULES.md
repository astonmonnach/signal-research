# Insider cluster buying
Stage: IDEA · Created: 2026-09-30

**Tested 14 Oct 2026 (IC1, `ic1/RESULTS.md`):** following every cluster does not pay (60-session excess mean +1.20%, interval -0.67% to +3.03%, median -3.02%). Clusters in companies under $300M did 7.0 points better than larger ones (interval +2.07 to +12.05), but their median only just beats the controls (+0.08%). Lone insider buys show nothing. Any follow-up on small companies is a new study (IC2), not a change to IC1.

- **Who is on the other side:** the market, which underreacts to insiders buying with their own money.
- **Evidence:** Lakonishok & Lee (2001), *Review of Financial Studies*: insider purchases predict returns, most strongly in small caps. Cohen, Malloy & Pomorski (2012), *Journal of Finance*: "opportunistic" insider trades carry the signal and routine ones don't.
- **Trigger:** Form 4 open-market purchases (transaction code P), with 2+ different insiders buying within 30 days. Awards, option exercises and 10b5-1 plan trades don't count.
- **Build needed:** a Form 4 parser for the market scan (the XML is structured, so this is doable).
