/**
 * Touchline → Kindle mailer.
 *
 * A Google Apps Script web app. The website's "Send to Kindle" button calls it with
 * ?issue=001 (Touchline) or ?issue=cj001 (The Chug Jug); it downloads that issue's
 * .epub from the public site and emails it to ONE fixed Kindle address. It can't be used to email anyone else, and it is
 * rate-limited, so the public URL is safe to embed in the site.
 *
 * Setup: see kindle/SETUP.md.
 */

// Your Send-to-Kindle address (Amazon → Manage Content & Devices → Preferences →
// Personal Document Settings). Kept here, not in the public website repo.
const KINDLE_EMAIL = 'PASTE-YOUR-KINDLE-ADDRESS@kindle.com';

const SITE = 'https://utx.github.io/sportmag/';
// Each magazine: issue-code prefix -> where its Kindle files live on the site, and its name.
const MAGAZINES = {
  '':   { path: 'issues/',         file: 'touchline-', name: 'Touchline' },
  'cj': { path: 'chugjug/issues/', file: 'chugjug-',   name: 'The Chug Jug' },
};
const COOLDOWN_SECONDS = 300;   // ignore repeat taps for the same issue for 5 minutes
const DAILY_LIMIT = 10;         // never send more than this many emails per day

function doGet(e) {
  const code = String((e && e.parameter && e.parameter.issue) || '');
  const m = /^([a-z]*)(\d{3})$/.exec(code);
  if (!m || !Object.prototype.hasOwnProperty.call(MAGAZINES, m[1])) return json_({ ok: false, error: 'bad-issue' });
  const mag = MAGAZINES[m[1]];
  const issue = m[2];

  const cache = CacheService.getScriptCache();
  if (cache.get('sent-' + code)) return json_({ ok: false, error: 'too-soon' });

  const props = PropertiesService.getScriptProperties();
  const today = Utilities.formatDate(new Date(), 'Australia/Sydney', 'yyyy-MM-dd');
  const countKey = 'count-' + today;
  const count = Number(props.getProperty(countKey) || 0);
  if (count >= DAILY_LIMIT) return json_({ ok: false, error: 'daily-limit' });

  const url = SITE + mag.path + issue + '/' + mag.file + issue + '.epub';
  const res = UrlFetchApp.fetch(url, { muteHttpExceptions: true, followRedirects: true });
  if (res.getResponseCode() !== 200) return json_({ ok: false, error: 'not-found' });

  const blob = res.getBlob()
    .setName(mag.name + ' - Issue ' + Number(issue) + '.epub')
    .setContentType('application/epub+zip');

  MailApp.sendEmail({
    to: KINDLE_EMAIL,
    subject: mag.name + ' - Issue ' + Number(issue),
    body: 'Your new issue of ' + mag.name + ' is attached.',
    attachments: [blob],
  });

  cache.put('sent-' + code, '1', COOLDOWN_SECONDS);
  props.setProperty(countKey, String(count + 1));
  return json_({ ok: true });
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/** Run this once from the editor to grant permissions and send a test copy of issue 1. */
function testSend() {
  Logger.log(doGet({ parameter: { issue: '001' } }).getContent());
}

/** Sends a test copy of The Chug Jug issue 1. */
function testSendChugJug() {
  Logger.log(doGet({ parameter: { issue: 'cj001' } }).getContent());
}
