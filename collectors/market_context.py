"""Market context: second-order effects to show next to every signal.

Three questions, answered on every run for the tickers we care about:
  1. Commodities / sectors: what are steel, gold, oil, semis, defence, small caps doing, and is any
     move unusual for that symbol (1-day z-score against its own 60-day daily-return stdev)?
  2. Themes: which commodities does a ticker's story pull on? Keyword map over the ticker's idea file,
     signal summaries, press titles and SEC SIC description -> theme symbols.
  3. Peers: did the rest of the group move with it? Curated peer groups plus same-SIC companies (SEC),
     with a flag when the ticker moved alone or the peers moved without it.

Honest gaps: there is NO free tungsten, antimony, molybdenum or HF-1 steel price. Those themes point at
labelled proxies (XME / REMX broad mining ETFs; HRC=F / SLX for HF-1) and say "no direct price".

Universe: watch/watchlist.json + OPEN trades in journal/trades.csv + data/signals.csv tickers detected in
the last 30 days + watch/press/latest.json tickers (skipped if the file doesn't exist yet).

Outputs:
  watch/context/latest.json        machine-readable snapshot (schema in write_outputs docstring)
  watch/context/YYYY-MM-DD.md      readable version (unusual commodity moves in bold)
  data/context/sic_cache.json      SIC per CIK and member CIKs per SIC (refreshed after 30 days)

Standard library only. Yahoo chart API with a browser User-Agent, ~0.25s between calls, 404 = dropped.
Run: python collectors/market_context.py [--tickers MTUS ELMT] [--no-sic]
"""
import argparse
import csv
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST = ROOT / "watch" / "watchlist.json"
TRADES = ROOT / "journal" / "trades.csv"
SIGNALS = ROOT / "data" / "signals.csv"
PRESS = ROOT / "watch" / "press" / "latest.json"
IDEAS = ROOT / "ideas"
OUT_DIR = ROOT / "watch" / "context"
CACHE_DIR = ROOT / "data" / "context"
SIC_CACHE = CACHE_DIR / "sic_cache.json"

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
SEC_UA = "PersonalResearch research@example.com"
YAHOO = "https://{host}/v8/finance/chart/{sym}?range=3mo&interval=1d"
YAHOO_GAP, SEC_GAP = 0.25, 0.15

SIGNAL_LOOKBACK_DAYS = 30
SIC_CACHE_DAYS = 30
MAX_SIC_PEERS = 8          # same-SIC peers kept per ticker (largest first, by SEC file order)
MAX_SIC_PAGES = 10         # EDGAR SIC browse pages (100 companies each)
UNUSUAL_Z = 2.0            # |z_1d| at or above this = unusual move
SOLO_RATIO = 2.0           # ticker 5d move > 2x peer median 5d ...
SOLO_MIN_MOVE = 3.0        # ... and at least 3% (stops 0.4% vs 0.1% from flagging)
PEER_MOVE = 5.0            # peer median 5d beyond +-5% ...
LAG_FRACTION = 0.5         # ... while the ticker did less than half of it (or the opposite)
CORP_ACTION_JUMP = 0.40    # a single-day move > 40% in the window suggests a spin-off/split
THIN_ZERO_SHARE = 0.40     # > 40% unchanged days in the z window = thin trading (z overstated)
TIME_BUDGET_S = 160        # stop fetching peers after this; the run must stay under ~3 min

# ---------------------------------------------------------------------------------------------
# 1. Commodity / sector table: (symbol, name, theme, proxy note or None)
# ---------------------------------------------------------------------------------------------
COMMODITIES = [
    ("HRC=F", "US Midwest hot-rolled coil steel futures", "steel",
     "general steel price; also the nearest proxy for HF-1 artillery steel (no HF-1 price exists)"),
    ("SLX", "VanEck Steel ETF", "steel", None),
    ("GC=F", "Gold futures", "metals", None),
    ("SI=F", "Silver futures", "metals", None),
    ("HG=F", "Copper futures", "metals", None),
    ("PL=F", "Platinum futures", "metals", None),
    ("PA=F", "Palladium futures", "metals", None),
    ("ALI=F", "Aluminium futures (COMEX)", "metals", None),
    ("XME", "SPDR S&P Metals & Mining ETF", "metals",
     "PROXY for metals with no free price (tungsten, molybdenum, antimony, nickel, titanium)"),
    ("CL=F", "WTI crude oil futures", "energy", None),
    ("NG=F", "Henry Hub natural gas futures", "energy", None),
    ("XLE", "Energy Select Sector SPDR", "energy", None),
    ("OIH", "VanEck Oil Services ETF", "energy", None),
    ("URA", "Global X Uranium ETF", "uranium", None),
    ("LIT", "Global X Lithium & Battery Tech ETF", "lithium/batteries", None),
    ("REMX", "VanEck Rare Earth & Strategic Metals ETF", "rare earths",
     "PROXY: rare-earth/strategic-metal miners; only an indirect read on tungsten/antimony"),
    ("ITA", "iShares US Aerospace & Defense ETF", "defence", None),
    ("XAR", "SPDR S&P Aerospace & Defense ETF", "defence", None),
    ("SOXX", "iShares Semiconductor ETF", "semis", None),
    ("ZC=F", "Corn futures", "agriculture", None),
    ("ZS=F", "Soybean futures", "agriculture", None),
    ("ZW=F", "Chicago wheat futures", "agriculture", None),
    ("IWM", "iShares Russell 2000 (small caps)", "small caps", None),
    ("SPY", "SPDR S&P 500 (broad market)", "broad market", None),
    ("DX-Y.NYB", "US Dollar Index", "dollar", None),
    ("^TNX", "US 10-year Treasury yield (%)", "rates", None),
]

NO_DIRECT_PRICE = [
    {"item": "tungsten", "proxies": ["XME", "REMX"],
     "why": "APT/ferro-tungsten trade OTC (Fastmarkets/Argus, paid); no exchange future on Yahoo"},
    {"item": "antimony", "proxies": ["XME", "REMX"],
     "why": "antimony trades OTC/China-quoted; no free daily series"},
    {"item": "molybdenum", "proxies": ["XME"], "why": "LME moly contract is illiquid and not on Yahoo"},
    {"item": "HF-1 artillery steel", "proxies": ["HRC=F", "SLX"],
     "why": "specialty defence grade sold under contract; no market price. HRC is general flat steel"},
]

# ---------------------------------------------------------------------------------------------
# 2. Theme map: keyword -> themes + commodity symbols. Matching is case-insensitive on word
#    boundaries; "pattern" overrides the default (keyword, optional plural s).
#    "no_direct_price" = the symbols are proxies, not a price for the thing named.
# ---------------------------------------------------------------------------------------------
_STEEL = {"themes": ["steel"], "symbols": ["HRC=F", "SLX"]}
_HF1 = {"themes": ["steel", "defence"], "symbols": ["HRC=F", "SLX", "ITA", "XAR"],
        "no_direct_price": "no HF-1 price; HRC=F/SLX are general-steel proxies"}


def _proxy_metal(name, symbols=("XME", "REMX")):
    return {"themes": ["metals", "strategic metals"], "symbols": list(symbols),
            "no_direct_price": f"no free {name} price; {'/'.join(symbols)} are mining-ETF proxies"}


_CHIPS = {"themes": ["semis", "chip input metals"], "symbols": ["SOXX", "GC=F", "HG=F", "PA=F"],
          "note": "chip/board production pulls gold (bond wire, plating), copper (interconnect, PCB), "
                  "palladium (plating, MLCCs); no free polysilicon price"}
_OIL = {"themes": ["energy"], "symbols": ["CL=F", "OIH", "XLE"]}
_DEFENCE = {"themes": ["defence"], "symbols": ["ITA", "XAR"]}
_AG = {"themes": ["agriculture"], "symbols": ["ZC=F", "ZS=F", "ZW=F"]}

THEME_MAP = {
    "steel": _STEEL,
    "forging": {**_STEEL, "pattern": r"\bforg(?:e|es|ed|ing|ings)\b"},
    "rolling mill": _STEEL,
    "HF-1": {**_HF1, "pattern": r"\bHF-?1\b"},
    "high fragmentation": _HF1,
    "tungsten": _proxy_metal("tungsten"),
    "molybdenum": _proxy_metal("molybdenum", ("XME",)),
    "refractory": {**_proxy_metal("refractory-metal (tungsten/moly/tantalum)"), "pattern": r"\brefractory\b"},
    "antimony": _proxy_metal("antimony"),
    "nickel": _proxy_metal("nickel", ("XME",)),
    "titanium": _proxy_metal("titanium", ("XME",)),
    "superalloy": _proxy_metal("superalloy (nickel/cobalt)", ("XME",)),
    "rare earth": {"themes": ["rare earths"], "symbols": ["REMX"],
                   "no_direct_price": "no free rare-earth oxide price; REMX is a miners ETF",
                   "pattern": r"\brare[- ]earths?\b"},
    "critical minerals": {**_proxy_metal("critical-mineral"), "pattern": r"\bcritical minerals?\b"},
    "gold": {"themes": ["metals"], "symbols": ["GC=F"]},
    "silver": {"themes": ["metals"], "symbols": ["SI=F"]},
    "copper": {"themes": ["metals"], "symbols": ["HG=F"]},
    "platinum": {"themes": ["metals"], "symbols": ["PL=F"]},
    "palladium": {"themes": ["metals"], "symbols": ["PA=F"]},
    "aluminium": {"themes": ["metals"], "symbols": ["ALI=F"], "pattern": r"\balumin(?:i?um)\b"},
    "semiconductor": _CHIPS,
    "CPU": {**_CHIPS, "pattern": r"\b(?:CPU|GPU)s?\b"},
    "chip": {**_CHIPS, "pattern": r"\b(?<!blue )(?<!blue-)(?:chips?|chipmakers?|microchips?|wafers?)\b"},
    "data center": {"themes": ["semis", "data centers"], "symbols": ["SOXX", "HG=F", "NG=F"],
                    "note": "data centers pull copper (power/cabling) and gas-fired power",
                    "pattern": r"\bdata[- ]?cent(?:er|re)s?\b"},
    "uranium": {"themes": ["uranium"], "symbols": ["URA"]},
    "nuclear": {"themes": ["uranium"], "symbols": ["URA"]},
    "oil": {**_OIL, "pattern": r"\b(?:oil|crude|oilfield)\b"},
    "drilling": {**_OIL, "pattern": r"\b(?:drill|drilling|offshore rig|rigs?)\b"},
    "natural gas": {"themes": ["energy"], "symbols": ["NG=F", "XLE"], "pattern": r"\b(?:natural gas|LNG)\b"},
    "lithium": {"themes": ["lithium/batteries"], "symbols": ["LIT"]},
    "battery": {"themes": ["lithium/batteries"], "symbols": ["LIT"], "pattern": r"\batter(?:y|ies)\b"},
    "artillery": _DEFENCE,
    "munitions": {**_DEFENCE, "pattern": r"\b(?:munitions?|ammunition|ordnance|projectiles?)\b"},
    "Department of War": {**_DEFENCE, "pattern": r"\bDepartment of (?:War|Defen[cs]e)\b"},
    "defence": {**_DEFENCE, "pattern": r"\bdefen[cs]e\b"},
    "missile": _DEFENCE,
    "shipbuilding": {**_DEFENCE, "pattern": r"\b(?:shipbuilding|submarines?|warships?)\b"},
    "stockpile": {"themes": ["defence", "strategic metals"], "symbols": ["ITA", "XAR", "XME"],
                  "note": "National Defense Stockpile buys strategic materials; XME is a proxy, not a price",
                  "pattern": r"\bstockpiles?\b"},
    "aerospace": {"themes": ["defence"], "symbols": ["ITA"], "pattern": r"\b(?:aerospace|aircraft)\b"},
    "seed": {**_AG, "pattern": r"\b(?:seeds?|crops?|corn|soybeans?|wheat|agricultur\w*|farm\w*)\b"},
    "fertilizer": {"themes": ["agriculture", "energy"], "symbols": ["ZC=F", "NG=F"],
                   "note": "natural gas is the main input to nitrogen fertilizer",
                   "pattern": r"\b(?:fertili[sz]ers?|nitrogen|potash|phosphate)\b"},
}
_PATTERNS = {kw: re.compile(spec.get("pattern") or (r"\b" + re.escape(kw) + r"s?\b"), re.I)
             for kw, spec in THEME_MAP.items()}


def themes_for_text(text):
    """Keyword matches in `text`, one dict per keyword hit, in THEME_MAP order:
    {"keyword", "hits", "themes", "symbols", "no_direct_price" (str|None), "note" (str|None)}."""
    out = []
    if not text:
        return out
    for kw, spec in THEME_MAP.items():
        hits = len(_PATTERNS[kw].findall(text))
        if hits:
            out.append({"keyword": kw, "hits": hits, "themes": list(spec["themes"]),
                        "symbols": list(spec["symbols"]), "no_direct_price": spec.get("no_direct_price"),
                        "note": spec.get("note")})
    return out


# ---------------------------------------------------------------------------------------------
# 3. Curated peers: ticker -> {group: [peers]}. Groups are reverse-linked at runtime, so a ticker
#    listed in someone else's group also sees that someone in the same group.
# ---------------------------------------------------------------------------------------------
CURATED_PEERS = {
    "MTUS": {"steel": ["NUE", "STLD", "CLF", "CMC", "IIIN", "WS", "ASTL"],
             "defence metals": ["ELMT", "ATI", "CRS"]},
    "ELMT": {"defence metals": ["ATI", "CRS", "HWM", "MTUS"]},
    "ATI": {"defence metals": ["CRS", "HWM", "ELMT", "MTUS"]},
    "CRS": {"defence metals": ["ATI", "HWM", "ELMT", "MTUS"]},
    "HWM": {"defence metals": ["ATI", "CRS", "ELMT"]},
    "OLN": {"chlor-alkali": ["WLK", "DOW", "LYB"], "munitions": ["GD", "NOC"]},
    "CTVA": {"crop inputs": ["FMC", "BAYRY", "NTR", "MOS", "CF"]},
    "VYLR": {"seeds / ag": ["CTVA", "BAYRY", "FMC", "ADM", "DE"]},
    "THRM": {"auto parts": ["BWA", "LEA", "ADNT", "VC", "DAN", "APTV"]},
    "MOD": {"thermal / data-center cooling": ["VRT", "TT", "JCI", "AAON", "SPXC"]},
    "HMH": {"oilfield equipment": ["NOV", "FTI", "WHD", "OII", "WFRD"]},
    "TWST": {"genomics tools": ["ILMN", "TXG", "PACB", "DNA"]},
    "NUE": {"steel": ["STLD", "CLF", "CMC", "MTUS"]},
}

# ---------------------------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------------------------
_last_call = {"yahoo": 0.0, "sec": 0.0}
_series_cache = {}
_failed = {}  # symbol -> reason


def _throttle(kind, gap):
    wait = _last_call[kind] + gap - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_call[kind] = time.time()


def http_get(url, ua, kind, gap, timeout=25):
    _throttle(kind, gap)
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def yahoo_series(symbol):
    """{"symbol","name","currency","dates":[date],"closes":[float]} or None (reason in _failed)."""
    if symbol in _series_cache:
        return _series_cache[symbol]
    data, reason = None, None
    for attempt, host in enumerate(("query1.finance.yahoo.com", "query2.finance.yahoo.com")):
        url = YAHOO.format(host=host, sym=urllib.parse.quote(symbol, safe=""))
        try:
            data = json.loads(http_get(url, BROWSER_UA, "yahoo", YAHOO_GAP))
            break
        except urllib.error.HTTPError as e:
            reason = f"HTTP {e.code}"
            if e.code == 404:
                break
            time.sleep(1.5)
        except Exception as e:  # network blips, bad JSON
            reason = type(e).__name__
            time.sleep(1.0)
    out = None
    try:
        res = data["chart"]["result"][0]
        meta, q = res["meta"], res["indicators"]["quote"][0]
        off = meta.get("gmtoffset") or 0
        crypto = meta.get("instrumentType") == "CRYPTOCURRENCY"
        dates, closes = [], []
        for t, c in zip(res.get("timestamp") or [], q.get("close") or []):
            if c is None:
                continue
            d = datetime.fromtimestamp(t + off, timezone.utc).date()
            if d.weekday() >= 5 and not crypto:  # placeholder weekend bars on futures
                continue
            if dates and dates[-1] == d:  # duplicate live bar for today
                closes[-1] = float(c)
                continue
            dates.append(d)
            closes.append(float(c))
        # The range=3mo response can lag the latest trade on thin futures (seen on HRC=F: last bar 1275
        # while the 1mo response and meta both said 1306). meta.regularMarketPrice/Time is the latest
        # quote, so it overrides the same-day bar or adds the missing weekday bar.
        rmp, rmt = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
        if closes and rmp and rmt:
            d = datetime.fromtimestamp(rmt + off, timezone.utc).date()
            if d == dates[-1]:
                closes[-1] = float(rmp)
            elif d > dates[-1] and (d.weekday() < 5 or crypto):
                dates.append(d)
                closes.append(float(rmp))
        if closes:
            out = {"symbol": symbol, "name": meta.get("longName") or meta.get("shortName"),
                   "currency": meta.get("currency"), "dates": dates, "closes": closes,
                   "exchange": meta.get("fullExchangeName") or meta.get("exchangeName") or ""}
        else:
            reason = reason or "no closes"
    except Exception:
        reason = reason or "no data"
    if out is None:
        _failed[symbol] = reason or "no data"
    _series_cache[symbol] = out
    return out


def sec_json(url):
    return json.loads(http_get(url, SEC_UA, "sec", SEC_GAP))


# ---------------------------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------------------------
def _r(x, n=2):
    return None if x is None else round(x, n)


def moves(series):
    """last, chg_1d/5d/20d (%), z_1d vs the stdev of up to 60 prior daily returns, as_of, warnings."""
    c = series["closes"]
    last = c[-1]

    def chg(n):
        return (last / c[-1 - n] - 1) * 100 if len(c) > n and c[-1 - n] else None

    rets = [c[i] / c[i - 1] - 1 for i in range(1, len(c)) if c[i - 1]]
    z, thin = None, False
    prior = rets[-61:-1]
    if len(prior) >= 20:
        sd = statistics.stdev(prior)
        if sd > 0:
            z = rets[-1] / sd
        thin = sum(1 for r in prior if r == 0) / len(prior) > THIN_ZERO_SHARE
    warn = []
    recent = rets[-20:]
    corp = bool(recent) and max(abs(r) for r in recent) > CORP_ACTION_JUMP
    if corp:
        warn.append("a >40% one-day move in the last 20 sessions: possible spin-off/split/corporate "
                    "action; Yahoo doesn't adjust spin-offs, so 5d/20d may be distorted")
    if len(c) < 21:
        warn.append(f"only {len(c)} daily bars (new listing?)")
    if thin:
        warn.append("thinly traded: many unchanged days, so the z-score overstates how unusual a move is")
    return {"last": _r(last, 4), "chg_1d": _r(chg(1)), "chg_5d": _r(chg(5)), "chg_20d": _r(chg(20)),
            "z_1d": _r(z), "as_of": series["dates"][-1].isoformat(), "warnings": warn,
            "corp_action": corp, "thin": thin}


def median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 2) if xs else None


# ---------------------------------------------------------------------------------------------
# SEC: ticker -> CIK -> SIC, and same-SIC members (EDGAR company browse, Atom output)
# ---------------------------------------------------------------------------------------------
class Sec:
    def __init__(self, notes, enabled=True):
        self.notes, self.enabled = notes, enabled
        self.cache = {"by_cik": {}, "by_sic": {}}
        if SIC_CACHE.exists():
            try:
                self.cache.update(json.loads(SIC_CACHE.read_text(encoding="utf-8")))
            except Exception:
                notes.append("sic_cache.json unreadable; rebuilding")
        self.ticker_cik, self.cik_ticker, self.cik_title, self.rank = {}, {}, {}, {}
        if not enabled:
            return
        try:
            data = sec_json("https://www.sec.gov/files/company_tickers.json")
            for i, v in enumerate(data.values()):  # file order is roughly market-cap order
                tk, cik = v["ticker"].upper(), int(v["cik_str"])
                self.ticker_cik.setdefault(tk, cik)
                if cik not in self.cik_ticker:  # first listed ticker = main share class
                    self.cik_ticker[cik], self.cik_title[cik], self.rank[cik] = tk, v["title"], i
        except Exception as e:
            self.enabled = False
            notes.append(f"SEC company_tickers.json failed ({type(e).__name__}); SIC peers skipped")

    @staticmethod
    def _fresh(entry):
        try:
            return (datetime.now(timezone.utc).date()
                    - datetime.fromisoformat(entry["fetched"]).date()).days < SIC_CACHE_DAYS
        except Exception:
            return False

    def company(self, ticker):
        """{"cik","name","sic","sic_description"} for a ticker, or None."""
        if not self.enabled:
            return None
        cik = self.ticker_cik.get(ticker.upper())
        if cik is None:
            return None
        e = self.cache["by_cik"].get(str(cik))
        if not (e and e.get("sic_description") is not None and self._fresh(e)):
            try:
                s = sec_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
                e = {"sic": s.get("sic") or "", "sic_description": s.get("sicDescription") or "",
                     "name": s.get("name"), "fetched": datetime.now(timezone.utc).date().isoformat()}
                self.cache["by_cik"][str(cik)] = e
            except Exception as ex:
                self.notes.append(f"SEC submissions for {ticker} failed ({type(ex).__name__})")
                return {"cik": cik, "name": self.cik_title.get(cik), "sic": None, "sic_description": None}
        return {"cik": cik, "name": e.get("name") or self.cik_title.get(cik), "sic": e.get("sic") or None,
                "sic_description": e.get("sic_description") or None}

    def sic_members(self, sic):
        """CIKs EDGAR lists under this SIC code (all registrants, listed or not). Cached."""
        e = self.cache["by_sic"].get(sic)
        if e and self._fresh(e):
            return e["ciks"]
        ciks = []
        try:
            for page in range(MAX_SIC_PAGES):
                x = http_get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
                             f"&SIC={sic}&type=&dateb=&owner=include&start={page * 100}&count=100&output=atom",
                             SEC_UA, "sec", SEC_GAP).decode("latin-1")
                found = [int(c) for c in re.findall(r"<cik>(\d+)</cik>", x)]
                ciks += found
                if len(found) < 100:
                    break
        except Exception as ex:
            self.notes.append(f"EDGAR SIC {sic} browse failed ({type(ex).__name__}); using cache if any")
            return e["ciks"] if e else []
        today = datetime.now(timezone.utc).date().isoformat()
        self.cache["by_sic"][sic] = {"ciks": ciks, "fetched": today}
        for c in ciks:  # SIC per CIK for free
            self.cache["by_cik"].setdefault(str(c), {"sic": sic, "fetched": today})
        return ciks

    def sic_peers(self, ticker, sic, exclude):
        """Same-SIC candidates with a ticker, largest first, excluding `exclude` and OTC-style foreign
        tickers (5 letters ending F/Y). Returns 2x MAX_SIC_PEERS [(ticker, name)]; main() keeps the
        first MAX_SIC_PEERS that have prices and aren't OTC."""
        if not (self.enabled and sic):
            return []
        own = self.ticker_cik.get(ticker.upper())
        listed = [c for c in set(self.sic_members(sic)) if c in self.cik_ticker and c != own]
        listed.sort(key=lambda c: self.rank[c])
        out = []
        for c in listed:
            tk = self.cik_ticker[c]
            if tk in exclude or not re.fullmatch(r"[A-Z]{1,5}", tk) or re.fullmatch(r"[A-Z]{4}[FY]", tk):
                continue
            out.append((tk, self.cik_title[c]))
            if len(out) >= 2 * MAX_SIC_PEERS:
                break
        return out

    def save(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        SIC_CACHE.write_text(json.dumps(self.cache, indent=1, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# 4. Universe + text sources
# ---------------------------------------------------------------------------------------------
def _yahoo_symbol(ticker, market):
    t = ticker.strip().upper()
    if market == "JP" and t.isdigit():
        return t + ".T"
    if market == "UK" and "." not in t:
        return t + ".L"
    return t


def _walk_press(obj, ctx, found):
    """Tolerant walk over a press JSON of unknown shape: collects {ticker: [titles]}."""
    if isinstance(obj, dict):
        tks = []
        for k in ("ticker", "symbol"):
            if isinstance(obj.get(k), str) and obj[k].strip():
                tks.append(obj[k].strip().upper())
        if isinstance(obj.get("tickers"), list):
            tks += [t.strip().upper() for t in obj["tickers"] if isinstance(t, str) and t.strip()]
        tks = tks or ([ctx] if ctx else [])
        title = next((obj[k] for k in ("title", "headline", "summary") if isinstance(obj.get(k), str)), None)
        for t in tks:
            found.setdefault(t, [])
            if title:
                found[t].append(title)
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                key_ctx = k.upper() if re.fullmatch(r"[A-Za-z]{1,5}(?:\.[A-Za-z])?", k) and k.isupper() else None
                _walk_press(v, key_ctx or (tks[0] if len(tks) == 1 else ctx), found)
    elif isinstance(obj, list):
        for v in obj:
            _walk_press(v, ctx, found)


def build_universe(notes, only=None):
    """{ticker: {"sources": [...], "texts": [(source, text)], "market": "US"}} in priority order."""
    uni = {}

    def add(t, src, market="US", text=None, text_src=None):
        if not t:
            return
        t = _yahoo_symbol(t, market)
        u = uni.setdefault(t, {"sources": [], "texts": [], "market": market})
        if src not in u["sources"]:
            u["sources"].append(src)
        if text:
            u["texts"].append((text_src or src, text))

    # open trades first
    if TRADES.exists():
        for r in csv.DictReader(open(TRADES, encoding="utf-8")):
            if (r.get("exit_date") or "").strip() or (r.get("asset_class") or "").upper() in ("CRYPTO", "FUTURES", "FX"):
                continue
            add(r.get("symbol"), "open_trade")
    # signals in the last 30 days
    if SIGNALS.exists():
        cutoff = datetime.now(timezone.utc) - timedelta(days=SIGNAL_LOOKBACK_DAYS)
        for r in csv.DictReader(open(SIGNALS, encoding="utf-8")):
            try:
                when = datetime.fromisoformat(r["detected_at_utc"].replace("Z", "+00:00"))
            except Exception:
                continue
            if when >= cutoff and (r.get("ticker") or "").strip():
                add(r["ticker"], "signal", r.get("market") or "US", r.get("event_summary"), "signal")
    # watchlist
    if WATCHLIST.exists():
        try:
            for t in json.loads(WATCHLIST.read_text(encoding="utf-8")).get("tickers", []):
                add(t, "watchlist")
        except Exception:
            notes.append("watch/watchlist.json unreadable")
    # press (another collector writes this; optional)
    if PRESS.exists():
        try:
            found = {}
            _walk_press(json.loads(PRESS.read_text(encoding="utf-8")), None, found)
            for t, titles in found.items():
                add(t, "press")
                for title in titles:
                    uni[_yahoo_symbol(t, "US")]["texts"].append(("press", title))
        except Exception as e:
            notes.append(f"watch/press/latest.json unreadable ({type(e).__name__}); press skipped")
    else:
        notes.append("watch/press/latest.json not found yet; press titles skipped")
    # idea files
    for t, u in uni.items():
        p = IDEAS / f"{t}.md"
        if p.exists():
            u["texts"].append(("ideas", p.read_text(encoding="utf-8", errors="ignore")))
    if only:
        wanted = [o.upper() for o in only]
        for t in wanted:
            if t not in uni:
                uni[t] = {"sources": ["cli"], "texts": [], "market": "US"}
                p = IDEAS / f"{t}.md"
                if p.exists():
                    uni[t]["texts"].append(("ideas", p.read_text(encoding="utf-8", errors="ignore")))
        uni = {t: uni[t] for t in wanted}
    return uni


def ticker_themes(texts):
    """Merge keyword matches across sources -> (themes, theme_symbols, matches)."""
    merged = {}
    for src, text in texts:
        for m in themes_for_text(text):
            e = merged.setdefault(m["keyword"], {**m, "hits": 0, "sources": {}})
            e["hits"] += m["hits"]
            e["sources"][src] = e["sources"].get(src, 0) + m["hits"]
    matches = list(merged.values())
    themes, symbols = [], []
    for m in matches:
        themes += [t for t in m["themes"] if t not in themes]
        symbols += [s for s in m["symbols"] if s not in symbols]
    return themes, symbols, matches


def curated_groups(ticker):
    """{group: [peers]} with reverse links (X lists T under g -> T sees X under g)."""
    groups = {g: list(p) for g, p in CURATED_PEERS.get(ticker, {}).items()}
    for other, gs in CURATED_PEERS.items():
        if other == ticker:
            continue
        for g, peers in gs.items():
            if ticker in peers:
                lst = groups.setdefault(g, [])
                if other not in lst:
                    lst.append(other)
    for g in groups:
        groups[g] = [p for p in groups[g] if p != ticker]
    return groups


def sympathy(ticker, self_5d, peer_med, groups=(), corp_action=False):
    """Divergence between a ticker and its peers over 5 sessions. Returns a flag string or None.
    peer_med: overall peer median 5d; groups: [(group, median_5d)] checked too when a ticker has
    several curated groups (MTUS: steel vs defence metals tell different stories).
    solo_move:        |ticker 5d| > 2x |median| and |ticker 5d| >= 3% (it moved, peers didn't follow).
    missed_peer_move: |median| > 5% while the ticker did under half of it or went the other way."""
    if self_5d is None:
        return None

    def solo(m):
        return m is not None and abs(self_5d) >= SOLO_MIN_MOVE and abs(self_5d) > SOLO_RATIO * abs(m)

    def missed(m):
        return m is not None and abs(m) > PEER_MOVE and (abs(self_5d) < LAG_FRACTION * abs(m) or self_5d * m < 0)

    msgs = []
    by_group = ", ".join(f"{g} {m:+.1f}%" for g, m in groups if m is not None)
    if solo(peer_med):
        msgs.append(f"solo_move: {ticker} {self_5d:+.1f}% 5d vs peer median {peer_med:+.1f}%"
                    + (f" ({by_group})" if by_group else "") + "; peers didn't move with it")
    else:
        msgs += [f"solo_move: {ticker} {self_5d:+.1f}% 5d vs {g} median {m:+.1f}%" for g, m in groups if solo(m)]
    for label, m in [("peer", peer_med)] + list(groups):
        if missed(m):
            msgs.append(f"missed_peer_move: {label} median {m:+.1f}% 5d vs {ticker} {self_5d:+.1f}%; "
                        "peers moved, it didn't")
    if not msgs:
        return None
    out = " | ".join(dict.fromkeys(msgs))
    return ("UNRELIABLE (possible corporate action in window): " + out) if corp_action else out


# ---------------------------------------------------------------------------------------------
# 5. Output
# ---------------------------------------------------------------------------------------------
def _pct(x):
    return "n/a" if x is None else f"{x:+.1f}%"


def _z(x):
    return "n/a" if x is None else f"{x:+.1f}"


def _num(x):
    if x is None:
        return "n/a"
    return f"{x:,.2f}" if abs(x) >= 1 else f"{x:.4f}"


def _label(c):
    return (c["name"] + (" *(proxy)*" if c.get("proxy_note") and "PROXY" in c["proxy_note"] else "")
            + (" *(thin)*" if c.get("thin") else ""))


def write_outputs(snap):
    """latest.json schema (all % values are percent, e.g. 2.5 = +2.5%; null when not computable):
    {
      "generated_utc": "YYYY-MM-DDTHH:MM:SSZ",
      "runtime_s": float,
      "commodities": [{"symbol", "name", "theme", "last", "chg_1d", "chg_5d", "chg_20d", "z_1d",
                       "unusual": bool, "thin": bool, "as_of": "YYYY-MM-DD", "proxy_note": str|null}],
      "failed_symbols": [{"symbol", "reason", "role": "commodity"|"ticker"|"peer"}],
      "no_direct_price": [{"item", "proxies": [sym], "why"}],
      "tickers": {TICKER: {
          "name", "cik", "sic", "sic_description", "universe_sources": [str],
          "last", "self_1d", "self_5d", "self_20d", "self_z_1d", "as_of",
          "themes": [str], "theme_symbols": [sym],
          "theme_matches": [{"keyword", "hits", "themes", "symbols", "no_direct_price", "note",
                             "sources": {source: hits}}],
          "peers": [{"ticker", "name", "group", "source": "curated"|"sic",
                     "chg_1d", "chg_5d", "chg_20d", "excluded": str|null}],  # excluded = left out of medians
          "peer_median_1d", "peer_median_5d", "peer_median_20d",
          "peer_median_basis": "curated"|"sic"|null,
          "peer_groups": {group: {"n", "median_1d", "median_5d", "median_20d"}},
          "sic_peer_median_5d",
          "sympathy_flag": str|null,
          "warnings": [str]}},
      "notes": [str]
    }"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "latest.json").write_text(json.dumps(snap, indent=1), encoding="utf-8")

    com = {c["symbol"]: c for c in snap["commodities"]}
    day = snap["generated_utc"][:10]
    L = [f"# Market context: {day}", "",
         f"Generated {snap['generated_utc']} by `collectors/market_context.py`. Moves are close-to-close "
         f"(1d / 5d / 20d sessions). **Bold** = unusual: |z| >= {UNUSUAL_Z:g}, where z is the 1-day move "
         "divided by that symbol's own 60-day daily-return stdev.", "",
         "## Commodities and sectors", "",
         "| Theme | Symbol | Name | Last | 1d | 5d | 20d | z(1d) | As of |",
         "|---|---|---|---:|---:|---:|---:|---:|---|"]
    for c in snap["commodities"]:
        b = "**" if c["unusual"] else ""
        name = _label(c)
        L.append(f"| {c['theme']} | {b}{c['symbol']}{b} | {name} | {_num(c['last'])} | {b}{_pct(c['chg_1d'])}{b} "
                 f"| {_pct(c['chg_5d'])} | {_pct(c['chg_20d'])} | {b}{_z(c['z_1d'])}{b} | {c['as_of']} |")
    L += ["", "**No direct price** (proxies only, labelled as such):"]
    for n in snap["no_direct_price"]:
        L.append(f"- {n['item']}: proxies {', '.join(n['proxies'])}. {n['why']}.")
    if snap["failed_symbols"]:
        L += ["", "Dropped (no data): " + ", ".join(f"{f['symbol']} ({f['role']}, {f['reason']})"
                                                     for f in snap["failed_symbols"])]

    L += ["", "## Tickers", ""]
    for tk, t in snap["tickers"].items():
        head = f"### {tk}" + (f": {t['name']}" if t.get("name") else "")
        L += [head, ""]
        sic = f"SIC {t['sic']} {t['sic_description']}" if t.get("sic") else "SIC n/a"
        L.append(f"- In universe via: {', '.join(t['universe_sources'])} · {sic}")
        L.append(f"- Self: last {_num(t['last'])} · 1d {_pct(t['self_1d'])} · 5d {_pct(t['self_5d'])} · "
                 f"20d {_pct(t['self_20d'])} · z(1d) {_z(t['self_z_1d'])}")
        flag = t.get("sympathy_flag")
        L.append(f"- **Sympathy flag: {flag}**" if flag else "- Sympathy flag: none")
        if t["theme_matches"]:
            parts = []
            for m in t["theme_matches"]:
                src = ", ".join(f"{s} x{n}" for s, n in m["sources"].items())
                extra = " [no direct price]" if m["no_direct_price"] else ""
                parts.append(f"{m['keyword']} ({src}){extra}")
            L.append(f"- Themes: {', '.join(t['themes'])}. Matched: {'; '.join(parts)}")
            for line in dict.fromkeys(x for m in t["theme_matches"] for x in (m["no_direct_price"], m["note"]) if x):
                L.append(f"  - {line}")
        else:
            L.append("- Themes: none matched (no idea file / signal / press keywords)")
        if t["theme_symbols"]:
            L += ["", "Relevant commodity / sector moves:", "",
                  "| Symbol | Name | 1d | 5d | 20d | z(1d) |", "|---|---|---:|---:|---:|---:|"]
            for s in t["theme_symbols"]:
                c = com.get(s)
                if not c:
                    L.append(f"| {s} | (no data) | | | | |")
                    continue
                b = "**" if c["unusual"] else ""
                L.append(f"| {b}{s}{b} | {_label(c)} | {b}{_pct(c['chg_1d'])}{b} | {_pct(c['chg_5d'])} "
                         f"| {_pct(c['chg_20d'])} | {b}{_z(c['z_1d'])}{b} |")
        if t["peers"]:
            L += ["", "Peers:", "", "| Peer | Group | Source | 1d | 5d | 20d |", "|---|---|---|---:|---:|---:|"]
            for p in t["peers"]:
                ex = f" *(not in median: {p['excluded']})*" if p.get("excluded") else ""
                L.append(f"| {p['ticker']}{ex} | {p['group']} | {p['source']} | {_pct(p['chg_1d'])} "
                         f"| {_pct(p['chg_5d'])} | {_pct(p['chg_20d'])} |")
            L.append(f"| **{tk} (self)** | | | {_pct(t['self_1d'])} | {_pct(t['self_5d'])} | {_pct(t['self_20d'])} |")
            L += [""]
            for g, s in t["peer_groups"].items():
                L.append(f"- {g} median (n={s['n']}): 1d {_pct(s['median_1d'])} · 5d {_pct(s['median_5d'])} · "
                         f"20d {_pct(s['median_20d'])}")
            L.append(f"- Peer median 5d ({t['peer_median_basis']}): {_pct(t['peer_median_5d'])} vs {tk} "
                     f"{_pct(t['self_5d'])}")
        else:
            L += ["", "Peers: none found"]
        for w in t["warnings"]:
            L.append(f"- Warning: {w}")
        L.append("")
    L += ["## Notes", ""] + [f"- {n}" for n in snap["notes"]] + [""]
    md = OUT_DIR / f"{day}.md"
    md.write_text("\n".join(L), encoding="utf-8")
    return OUT_DIR / "latest.json", md


# ---------------------------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------------------------
def commodity_row(sym, name, theme, proxy, m):
    return {"symbol": sym, "name": name, "theme": theme, "last": m["last"], "chg_1d": m["chg_1d"],
            "chg_5d": m["chg_5d"], "chg_20d": m["chg_20d"], "z_1d": m["z_1d"],
            "unusual": m["z_1d"] is not None and abs(m["z_1d"]) >= UNUSUAL_Z, "thin": m["thin"],
            "as_of": m["as_of"], "proxy_note": proxy}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tickers", nargs="*", help="only these tickers (default: the full universe)")
    ap.add_argument("--no-sic", action="store_true", help="skip SEC lookups (curated peers only)")
    args = ap.parse_args()
    t0 = time.time()
    notes = ["No free tungsten, antimony, molybdenum or HF-1 price exists in this feed. Themes that need "
             "them point at labelled proxies (XME/REMX mining ETFs; HRC=F/SLX general steel), not prices.",
             "Futures (=F) are Yahoo's front-month continuous series; a contract roll can show as an "
             "artificial 1-day jump. ^TNX is the 10y yield in % points (chg is % change of the yield)."]
    failed = []

    # 1. commodities
    commodities = []
    for sym, name, theme, proxy in COMMODITIES:
        s = yahoo_series(sym)
        if not s:
            failed.append({"symbol": sym, "reason": _failed.get(sym, "no data"), "role": "commodity"})
            continue
        commodities.append(commodity_row(sym, name, theme, proxy, moves(s)))
    if commodities:
        newest = max(c["as_of"] for c in commodities)
        stale = [c["symbol"] for c in commodities
                 if (datetime.fromisoformat(newest) - datetime.fromisoformat(c["as_of"])).days > 4]
        if stale:
            notes.append(f"Stale (last bar >4 days older than newest): {', '.join(stale)}")
    known_commodities = {c["symbol"] for c in commodities}

    # 2-4. tickers
    sec = Sec(notes, enabled=not args.no_sic)
    universe = build_universe(notes, args.tickers)
    tickers, budget_hit = {}, False
    for tk, u in universe.items():
        info = sec.company(tk) if u["market"] == "US" else None
        texts = list(u["texts"])
        if info and info.get("sic_description"):
            texts.append(("sec_sic", info["sic_description"]))
        themes, theme_syms, matches = ticker_themes(texts)
        for sym in theme_syms:  # theme symbols outside the table still get a row
            if sym not in known_commodities and yahoo_series(sym):
                s = _series_cache[sym]
                commodities.append(commodity_row(sym, s["name"] or sym, "extra", None, moves(s)))
                known_commodities.add(sym)

        own = yahoo_series(tk)
        warnings = []
        if own:
            sm = moves(own)
            warnings += sm["warnings"]
        else:
            sm = {"last": None, "chg_1d": None, "chg_5d": None, "chg_20d": None, "z_1d": None, "as_of": None,
                  "corp_action": False}
            failed.append({"symbol": tk, "reason": _failed.get(tk, "no data"), "role": "ticker"})

        groups = curated_groups(tk)
        curated = {p for ps in groups.values() for p in ps}
        sic_list = []
        if info and info.get("sic"):
            sic_list = sec.sic_peers(tk, info["sic"], curated | {tk})
            if sic_list:
                groups[f"SIC {info['sic']}"] = [p for p, _ in sic_list]
        sic_names = dict(sic_list)

        peers, group_stats = [], {}
        for g, plist in groups.items():
            src = "sic" if g.startswith("SIC ") else "curated"
            rows = []
            for p in plist:
                if src == "sic" and len(rows) >= MAX_SIC_PEERS:
                    break
                if time.time() - t0 > TIME_BUDGET_S:
                    budget_hit = True
                    break
                s = yahoo_series(p)
                if not s:
                    if src == "curated" and not any(f["symbol"] == p for f in failed):
                        failed.append({"symbol": p, "reason": _failed.get(p, "no data"), "role": "peer"})
                    continue
                if src == "sic" and re.search(r"OTC|Pink|PNK", s.get("exchange", "")):
                    continue  # same SIC but an OTC line: not a useful comparable
                pm = moves(s)
                excluded = None
                if pm["corp_action"]:
                    excluded = "possible corporate action"
                elif pm["chg_5d"] is None:
                    excluded = "under 6 bars"
                rows.append({"ticker": p, "name": sic_names.get(p) or s["name"], "group": g, "source": src,
                             "chg_1d": pm["chg_1d"], "chg_5d": pm["chg_5d"], "chg_20d": pm["chg_20d"],
                             "excluded": excluded})
            peers += rows
            ok = [r for r in rows if not r["excluded"]]
            if ok:
                group_stats[g] = {"n": len(ok), "median_1d": median(r["chg_1d"] for r in ok),
                                  "median_5d": median(r["chg_5d"] for r in ok),
                                  "median_20d": median(r["chg_20d"] for r in ok)}

        cur_rows = [p for p in peers if p["source"] == "curated" and not p["excluded"]]
        sic_rows = [p for p in peers if p["source"] == "sic" and not p["excluded"]]
        basis_rows, basis = (cur_rows, "curated") if cur_rows else ((sic_rows, "sic") if sic_rows else ([], None))
        pmed = {k: median(p[k] for p in basis_rows) for k in ("chg_1d", "chg_5d", "chg_20d")}
        cur_groups = [g for g in group_stats if not g.startswith("SIC ")]
        group_checks = []
        if len(cur_groups) > 1:  # e.g. MTUS: steel vs defence metals tell different stories
            group_checks = [(g, group_stats[g]["median_5d"]) for g in cur_groups if group_stats[g]["n"] >= 2]
        flag = sympathy(tk, sm["chg_5d"], pmed["chg_5d"], group_checks, sm["corp_action"])

        tickers[tk] = {
            "name": (info or {}).get("name") or (own or {}).get("name"),
            "cik": (info or {}).get("cik"), "sic": (info or {}).get("sic"),
            "sic_description": (info or {}).get("sic_description"),
            "universe_sources": u["sources"],
            "last": sm["last"], "self_1d": sm["chg_1d"], "self_5d": sm["chg_5d"], "self_20d": sm["chg_20d"],
            "self_z_1d": sm["z_1d"], "as_of": sm["as_of"],
            "themes": themes, "theme_symbols": theme_syms, "theme_matches": matches,
            "peers": peers,
            "peer_median_1d": pmed["chg_1d"], "peer_median_5d": pmed["chg_5d"], "peer_median_20d": pmed["chg_20d"],
            "peer_median_basis": basis, "peer_groups": group_stats,
            "sic_peer_median_5d": median(p["chg_5d"] for p in sic_rows),
            "sympathy_flag": flag, "warnings": warnings,
        }
    if budget_hit:
        notes.append(f"Time budget ({TIME_BUDGET_S}s) reached; some peers were skipped this run")
    notes.append("Peer median uses curated peers when there are any, else same-SIC peers. SIC peers come "
                 "from EDGAR's company browse by SIC (largest listed first, max "
                 f"{MAX_SIC_PEERS}); they're a best-effort industry read, not hand-picked comparables.")
    notes.append("sympathy_flag: solo_move = ticker 5d move >2x its peer median and >=3%; missed_peer_move = "
                 "peer median beyond +-5% over 5d while the ticker did under half of it or went the other way.")
    sec.save()

    snap = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "runtime_s": round(time.time() - t0, 1),
            "commodities": commodities, "failed_symbols": failed, "no_direct_price": NO_DIRECT_PRICE,
            "tickers": tickers, "notes": notes}
    js, md = write_outputs(snap)
    worked = [c["symbol"] for c in commodities]
    print(f"commodities ok ({len(worked)}): {' '.join(worked)}")
    print(f"failed: {', '.join(f['symbol'] + ' (' + f['role'] + ')' for f in failed) or 'none'}")
    for tk, t in tickers.items():
        print(f"{tk}: 5d {_pct(t['self_5d'])} | peers {_pct(t['peer_median_5d'])} ({t['peer_median_basis']}) | "
              f"themes {', '.join(t['themes']) or '-'} | flag {t['sympathy_flag'] or '-'}")
    print(f"wrote {js.relative_to(ROOT)} and {md.relative_to(ROOT)} in {snap['runtime_s']}s")


if __name__ == "__main__":
    main()
