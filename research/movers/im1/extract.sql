WITH bars AS ({BARS}),
pr AS (SELECT column1 AS k, column2 AS lvl, column3 AS om, column4 AS cm FROM (VALUES {PARAMS})),
rth AS (SELECT b.k, b.t, b.o, b.h, b.l, b.c, pr.lvl FROM bars b JOIN pr ON b.k = pr.k WHERE b.t >= pr.om AND b.t < pr.cm),
trig AS (SELECT k, MIN(t) AS tt FROM rth WHERE h >= lvl GROUP BY k),
ent AS (SELECT r.k, r.t AS tt, CASE WHEN r.o >= r.lvl THEN r.o ELSE r.lvl END AS entry, CASE WHEN r.o >= r.lvl THEN 1 ELSE 0 END AS jumped
        FROM rth r JOIN trig g ON r.k = g.k AND r.t = g.tt),
x AS (SELECT e.k, e.tt, e.entry, e.jumped,
  (SELECT o FROM rth r WHERE r.k = e.k AND r.t >= e.tt + 1800000 ORDER BY r.t LIMIT 1) AS x30,
  (SELECT o FROM rth r WHERE r.k = e.k AND r.t >= e.tt + 3600000 ORDER BY r.t LIMIT 1) AS x60,
  (SELECT o FROM rth r WHERE r.k = e.k AND r.t >= e.tt + 7200000 ORDER BY r.t LIMIT 1) AS x120,
  (SELECT t FROM rth r WHERE r.k = e.k AND r.t >= e.tt + 7200000 ORDER BY r.t LIMIT 1) AS t120,
  (SELECT c FROM rth r WHERE r.k = e.k ORDER BY r.t DESC LIMIT 1) AS xclose
  FROM ent e)
SELECT pr.k,
  (SELECT COUNT(*) FROM bars b WHERE b.k = pr.k) AS n_all,
  (SELECT COUNT(*) FROM rth r WHERE r.k = pr.k) AS n_rth,
  x.tt, x.entry, x.jumped, x.x30, x.x60, x.x120, x.t120, x.xclose,
  (SELECT MAX(h) FROM rth r WHERE r.k = pr.k AND r.t > x.tt AND r.t < COALESCE(x.t120, 99999999999999)) AS hi,
  (SELECT MIN(l) FROM rth r WHERE r.k = pr.k AND r.t > x.tt AND r.t < COALESCE(x.t120, 99999999999999)) AS lo
FROM pr LEFT JOIN x ON pr.k = x.k ORDER BY pr.k
