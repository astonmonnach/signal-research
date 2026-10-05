/**
 * Live ALL watchlist in Discord: ONE message in #all, edited every 5 minutes while the US market is open.
 * Runs free on Google Apps Script (Google's servers, no PC needed). No emojis.
 *
 * Setup (about 5 minutes, once):
 *   1. script.google.com -> New project -> paste this whole file over the default code -> Save.
 *   2. Project Settings (gear) -> Script properties -> Add property:
 *        WEBHOOK_ALL = the #all channel's webhook URL
 *      (optional) TICKERS = MTUS,PUSA,...  to override the list read from the repo
 *   3. Back in the editor, choose the function "setup" in the toolbar -> Run -> allow the permissions.
 *      It posts the message and creates the 5-minute trigger. Pin the message in Discord.
 *   To stop it: run "teardown".
 *
 * The ticker list comes from watch/watchlist.json in the repo (the same list as IBKR "ALL"), so adding a
 * stock there adds it here. If the repo is private or unreachable, it falls back to DEFAULT_TICKERS.
 * Prices: Yahoo Finance chart API, which can be delayed by up to 15 minutes.
 */
var WATCHLIST_URL = 'https://raw.githubusercontent.com/astonmonnach/signal-research/main/watch/watchlist.json';
var DEFAULT_TICKERS = ['MTUS', 'PUSA', 'ELMT', 'HMH', 'VYLR', 'CTVA', 'THRM', 'MOD', 'TWST', 'WHF', 'CHDN', 'RYAM'];
var MARKET = ['SPY', 'IWM', 'QQQ'];

function setup() {
  teardown();
  ScriptApp.newTrigger('tick').timeBased().everyMinutes(5).create();
  tick(true);
}

function teardown() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'tick') ScriptApp.deleteTrigger(t);
  });
}

function nyNow_() {
  var d = new Date();
  return {
    day: Number(Utilities.formatDate(d, 'America/New_York', 'u')),       // 1 = Monday ... 7 = Sunday
    mins: Number(Utilities.formatDate(d, 'America/New_York', 'H')) * 60 + Number(Utilities.formatDate(d, 'America/New_York', 'm')),
    date: Utilities.formatDate(d, 'America/New_York', 'yyyy-MM-dd'),
    label: Utilities.formatDate(d, 'America/New_York', 'EEE dd MMM, HH:mm') + ' New York'
  };
}

function tick(force) {
  var props = PropertiesService.getScriptProperties();
  var now = nyNow_();
  var open = now.day <= 5 && now.mins >= 9 * 60 + 25 && now.mins <= 16 * 60 + 5;
  // Outside market hours: one final update after the close, then nothing until the next open.
  if (!open && force !== true) {
    if (now.day <= 5 && now.mins > 16 * 60 + 5 && props.getProperty('CLOSED_FOR') !== now.date) {
      update_(props, now, 'Closed. Final prices for ' + now.date);
      props.setProperty('CLOSED_FOR', now.date);
    }
    return;
  }
  update_(props, now, open ? 'Live, updated ' + now.label + ' (may be delayed up to 15 min)' : 'Market closed. Last prices as of ' + now.label);
}

function tickers_(props) {
  var override = props.getProperty('TICKERS');
  if (override) return override.split(',').map(function (s) { return s.trim().toUpperCase(); }).filter(String);
  try {
    var r = UrlFetchApp.fetch(WATCHLIST_URL, { muteHttpExceptions: true });
    if (r.getResponseCode() === 200) return JSON.parse(r.getContentText()).tickers;
  } catch (e) {}
  return DEFAULT_TICKERS;
}

function quotes_(symbols) {
  var reqs = symbols.map(function (s) {
    return { url: 'https://query1.finance.yahoo.com/v8/finance/chart/' + encodeURIComponent(s) + '?range=1d&interval=5m',
             muteHttpExceptions: true, headers: { 'User-Agent': 'Mozilla/5.0' } };
  });
  var out = {};
  UrlFetchApp.fetchAll(reqs).forEach(function (r, i) {
    try {
      var m = JSON.parse(r.getContentText()).chart.result[0].meta;
      var prev = m.chartPreviousClose || m.previousClose;
      out[symbols[i]] = { last: m.regularMarketPrice, day: prev ? (m.regularMarketPrice / prev - 1) * 100 : null };
    } catch (e) { out[symbols[i]] = null; }
  });
  return out;
}

function pct_(v) { return v === null || v === undefined ? 'n/a' : (v >= 0 ? '+' : '') + v.toFixed(1) + '%'; }
function pad_(s, n, left) { s = String(s); while (s.length < n) s = left ? s + ' ' : ' ' + s; return s; }

function update_(props, now, status) {
  var list = tickers_(props);
  var q = quotes_(list.concat(MARKET));
  var iwm = q.IWM && q.IWM.day;
  var rows = list.map(function (t) {
    var x = q[t];
    return { t: t, last: x ? x.last : null, day: x ? x.day : null, vs: x && x.day !== null && iwm !== null ? x.day - iwm : null };
  });
  rows.sort(function (a, b) { return (b.day === null ? -999 : b.day) - (a.day === null ? -999 : a.day); });
  var lines = ['**ALL (LIVE)** · ' + status,
               'Market: ' + MARKET.map(function (s) { return s + ' ' + pct_(q[s] && q[s].day); }).join(' · '),
               '```', pad_('Ticker', 7, true) + pad_('Last', 9) + pad_('Day', 8) + pad_('vs IWM', 8)];
  rows.forEach(function (r) {
    lines.push(pad_(r.t, 7, true) + pad_(r.last ? r.last.toFixed(r.last < 1 ? 3 : 2) : 'n/a', 9) + pad_(pct_(r.day), 8) +
               pad_(r.vs === null ? 'n/a' : (r.vs >= 0 ? '+' : '') + r.vs.toFixed(1), 8));
  });
  lines.push('```');
  lines.push('Same list as the IBKR ALL watchlist. Research log, not advice.');
  send_(props, lines.join('\n'));
}

function send_(props, content) {
  var hook = props.getProperty('WEBHOOK_ALL');
  if (!hook) throw new Error('Add the WEBHOOK_ALL script property first (Project Settings -> Script properties).');
  var payload = JSON.stringify({ content: content, flags: 4 });
  var id = props.getProperty('MESSAGE_ID');
  if (id) {
    var r = UrlFetchApp.fetch(hook + '/messages/' + id, { method: 'patch', contentType: 'application/json', payload: payload, muteHttpExceptions: true });
    if (r.getResponseCode() < 300) return;
    props.deleteProperty('MESSAGE_ID');                     // message was deleted: post a new one
  }
  var p = UrlFetchApp.fetch(hook + '?wait=true', { method: 'post', contentType: 'application/json', payload: payload, muteHttpExceptions: true });
  if (p.getResponseCode() < 300) props.setProperty('MESSAGE_ID', JSON.parse(p.getContentText()).id);
  else throw new Error('Discord said ' + p.getResponseCode() + ': ' + p.getContentText());
}
