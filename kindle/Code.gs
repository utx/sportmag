/**
 * Touchline → Kindle mailer.
 *
 * A Google Apps Script web app. The website's "Send to Kindle" button calls it with
 * ?issue=001; it downloads that issue's .epub from the public site and emails it
 * to ONE fixed Kindle address. It can't be used to email anyone else, and it is
 * rate-limited, so the public URL is safe to embed in the site.
 *
 * Setup: see kindle/SETUP.md.
 */

// Your Send-to-Kindle address (Amazon → Manage Content & Devices → Preferences →
// Personal Document Settings). Kept here, not in the public website repo.
const KINDLE_EMAIL = 'PASTE-YOUR-KINDLE-ADDRESS@kindle.com';

const SITE = 'https://utx.github.io/sportmag/';
const COOLDOWN_SECONDS = 300;   // ignore repeat taps for the same issue for 5 minutes
const DAILY_LIMIT = 10;         // never send more than this many emails per day

function doGet(e) {
  const issue = String((e && e.parameter && e.parameter.issue) || '');
  if (!/^\d{3}$/.test(issue)) return json_({ ok: false, error: 'bad-issue' });

  const cache = CacheService.getScriptCache();
  if (cache.get('sent-' + issue)) return json_({ ok: false, error: 'too-soon' });

  const props = PropertiesService.getScriptProperties();
  const today = Utilities.formatDate(new Date(), 'Australia/Sydney', 'yyyy-MM-dd');
  const countKey = 'count-' + today;
  const count = Number(props.getProperty(countKey) || 0);
  if (count >= DAILY_LIMIT) return json_({ ok: false, error: 'daily-limit' });

  const url = SITE + 'issues/' + issue + '/touchline-' + issue + '.epub';
  const res = UrlFetchApp.fetch(url, { muteHttpExceptions: true, followRedirects: true });
  if (res.getResponseCode() !== 200) return json_({ ok: false, error: 'not-found' });

  const blob = res.getBlob()
    .setName('Touchline - Issue ' + Number(issue) + '.epub')
    .setContentType('application/epub+zip');

  MailApp.sendEmail({
    to: KINDLE_EMAIL,
    subject: 'Touchline - Issue ' + Number(issue),
    body: 'Your new issue of Touchline is attached.',
    attachments: [blob],
  });

  cache.put('sent-' + issue, '1', COOLDOWN_SECONDS);
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
