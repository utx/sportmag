# One-tap "Send to Kindle" — setup (about 10 minutes, once)

The button on the site calls a tiny Google Apps Script that emails the issue's
`.epub` to your Kindle. It's free, runs in your own Google account, and your
Kindle address never appears on the public website.

You need: a Google account (any Gmail works) and your Amazon login.

## 1. Let Amazon accept emails from your Google account

1. Go to **amazon.com.au → Account → Manage Content and Devices → Preferences →
   Personal Document Settings**.
2. Under **Approved Personal Document E-mail List**, click **Add a new approved
   e-mail address** and add the Gmail address you'll use in step 2.

(Amazon silently ignores emails from senders that aren't on this list.)

## 2. Create the script

1. Open <https://script.google.com> while signed in to that Google account and click **New project**.
2. Delete the sample code and paste in everything from `kindle/Code.gs`.
3. On the `KINDLE_EMAIL` line, replace the placeholder with your Send-to-Kindle address.
4. Click the save icon and name the project **Touchline Kindle**.

## 3. Test it

1. Make sure the website is live first (the script downloads the issue from it).
2. In the function dropdown at the top, choose **testSend**, then click **Run**.
3. Google will ask for permission (to send email as you and fetch web pages).
   Click through **Advanced → Go to Touchline Kindle (unsafe)**. It's "unsafe" only
   because you wrote it yourself and Google hasn't reviewed it.
4. Within a few minutes, Issue 1 should appear on the Kindle (Wi-Fi on).

## 4. Publish it as a web app

1. Click **Deploy → New deployment**, then the gear icon → **Web app**.
2. **Execute as:** Me. **Who has access:** Anyone.
3. Click **Deploy** and copy the **Web app URL** (it ends in `/exec`).

## 5. Connect the button

Paste that URL into `src/assets/js/config.js`:

```js
window.TOUCHLINE_CONFIG = { kindleEndpoint: "https://script.google.com/macros/s/…/exec" };
```

…then rebuild (`build/build.sh`) and push. (Or just send the URL to Claude and it'll do this bit.)

Until this is done, the button falls back to downloading the `.epub`, which you
can send with Amazon's Send to Kindle app or <https://www.amazon.com.au/sendtokindle>.

### Safety notes

- The script only ever emails the one Kindle address in `KINDLE_EMAIL`, and only
  attaches files from the Touchline site.
- Repeat taps for the same issue within 5 minutes are ignored, and it stops after
  10 emails a day.
- If you ever change the code, use **Deploy → Manage deployments → Edit → New version**
  so the URL stays the same.
