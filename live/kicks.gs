/**
 * On-time starts for the GitHub jobs. GitHub's own schedules are "best effort" and often start hours late
 * (6 Oct 2026: the 21:15 UTC recap started at 01:52, the morning briefing hadn't started by 08:40 UK). This runs on
 * Google Apps Script every 10 minutes and asks GitHub to start each job at the right London time:
 *
 *   morning-briefing   weekdays from 07:45 London (after the 06:30 research run), once a day
 *   alerts             every 30 minutes, 07:00-midnight London
 *   evening-recap      weekdays from 21:20 London (after the US close in every clock-change combination), once a day
 *   press-wires        every 30 minutes, 07:00-23:00 London
 *
 * The GitHub schedules stay on as a backup. Both jobs send to Discord once a day at most, so nothing is posted twice.
 *
 * Setup (in the same Apps Script project as all_live.gs: + next to Files -> Script -> name it "kicks" -> paste this):
 *   1. GitHub -> your avatar -> Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens ->
 *      Generate new token. Repository access: Only select repositories -> signal-research.
 *      Permissions -> Repository permissions -> Actions: Read and write. Expiration: up to a year. Generate, copy.
 *   2. Apps Script -> Project Settings -> Script properties -> Add: GITHUB_TOKEN = the token.
 *   3. Pick "setupKicks" in the function dropdown -> Run -> allow. It creates the 10-minute trigger.
 *   To stop it: run "teardownKicks".
 */
var GH_REPO = 'astonmonnach/signal-research';
var KICKS = [
  { workflow: 'morning-briefing.yml', days: [1, 2, 3, 4, 5], from: 7 * 60 + 45, to: 12 * 60, every: 'day' },
  { workflow: 'alerts.yml', days: [1, 2, 3, 4, 5, 6, 7], from: 7 * 60, to: 23 * 60 + 59, every: 30 },
  { workflow: 'evening-recap.yml', days: [1, 2, 3, 4, 5], from: 21 * 60 + 20, to: 23 * 60 + 59, every: 'day' },
  { workflow: 'press-wires.yml', days: [1, 2, 3, 4, 5, 6, 7], from: 7 * 60, to: 23 * 60, every: 30 }
];

function setupKicks() {
  teardownKicks();
  ScriptApp.newTrigger('kicks').timeBased().everyMinutes(10).create();
  kicks();
}

function teardownKicks() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'kicks') ScriptApp.deleteTrigger(t);
  });
}

function londonNow_() {
  var d = new Date();
  return {
    day: Number(Utilities.formatDate(d, 'Europe/London', 'u')),
    mins: Number(Utilities.formatDate(d, 'Europe/London', 'H')) * 60 + Number(Utilities.formatDate(d, 'Europe/London', 'm')),
    date: Utilities.formatDate(d, 'Europe/London', 'yyyy-MM-dd'),
    ms: d.getTime()
  };
}

function kicks() {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('Add the GITHUB_TOKEN script property first (Project Settings -> Script properties).');
  var now = londonNow_();
  KICKS.forEach(function (k) {
    if (k.days.indexOf(now.day) < 0 || now.mins < k.from || now.mins > k.to) return;
    var key = 'KICKED_' + k.workflow;
    var last = props.getProperty(key) || '';
    if (k.every === 'day' ? last === now.date : (last && now.ms - Number(last) < k.every * 60 * 1000 - 60 * 1000)) return;
    var r = UrlFetchApp.fetch('https://api.github.com/repos/' + GH_REPO + '/actions/workflows/' + k.workflow + '/dispatches', {
      method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' },
      payload: JSON.stringify({ ref: 'main' })
    });
    if (r.getResponseCode() === 204) props.setProperty(key, k.every === 'day' ? now.date : String(now.ms));
    else console.log(k.workflow + ': GitHub said ' + r.getResponseCode() + ' ' + r.getContentText().slice(0, 200));
  });
}
