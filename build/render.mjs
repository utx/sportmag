// Renders every graphic (.g[data-epub]) and the cover to PNG with Chromium,
// so the Kindle edition gets real pictures instead of SVG it can't draw.
//
//   node build/render.mjs            -> build/out/<issue>/{cover.png, g-*.png}
//   node build/render.mjs --shots    -> also full-page screenshots into build/out/shots/
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require("playwright"); }
catch { playwright = require("/opt/node22/lib/node_modules/playwright"); }

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DOCS = path.join(ROOT, "docs");
const OUT = path.join(ROOT, "build", "out");
const SHOTS = process.argv.includes("--shots");

const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml",
  ".woff2": "font/woff2", ".png": "image/png", ".json": "application/json", ".epub": "application/epub+zip" };

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  let file = path.join(DOCS, url);
  if (!file.startsWith(DOCS)) { res.writeHead(403).end(); return; }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  if (!fs.existsSync(file)) { res.writeHead(404).end(); return; }
  res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const launchOpts = {};
if (fs.existsSync("/opt/pw-browsers/chromium")) {
  const dir = fs.readdirSync("/opt/pw-browsers").find((d) => /^chromium-\d+$/.test(d));
  const exe = dir && path.join("/opt/pw-browsers", dir, "chrome-linux", "chrome");
  if (exe && fs.existsSync(exe)) launchOpts.executablePath = exe;
}
const browser = await playwright.chromium.launch(launchOpts);

const issues = JSON.parse(fs.readFileSync(path.join(DOCS, "issues.json"), "utf8"));
for (const { slug } of issues) {
  const outDir = path.join(OUT, slug);
  fs.mkdirSync(outDir, { recursive: true });
  for (const f of fs.readdirSync(outDir)) if (f.endsWith(".png")) fs.unlinkSync(path.join(outDir, f));

  const ctx = await browser.newContext({ viewport: { width: 900, height: 1200 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  // hide the paper grain + sticky bar for clean captures
  const clean = "body::after{display:none!important} .toast{display:none!important} .topbar{position:static!important}";

  await page.goto(`${base}/issues/${slug}/index.html`, { waitUntil: "networkidle" });
  await page.addStyleTag({ content: clean + " .cover{box-shadow:none!important;border:0!important}" });
  await page.evaluate(() => document.fonts.ready);
  await page.locator("#cover").screenshot({ path: path.join(outDir, "cover.png") });
  if (SHOTS) {
    fs.mkdirSync(path.join(OUT, "shots"), { recursive: true });
    await page.screenshot({ path: path.join(OUT, "shots", `${slug}-index.png`), fullPage: true });
  }

  const pages = fs.readdirSync(path.join(DOCS, "issues", slug)).filter((f) => f.endsWith(".html") && f !== "index.html");
  let count = 0;
  for (const p of pages) {
    await page.goto(`${base}/issues/${slug}/${p}`, { waitUntil: "networkidle" });
    await page.addStyleTag({ content: clean });
    await page.evaluate(() => document.fonts.ready);
    const ids = await page.$$eval(".g[data-epub]", (els) => els.map((e) => e.dataset.epub));
    for (const id of ids) {
      await page.locator(`.g[data-epub="${id}"]`).screenshot({ path: path.join(outDir, `${id}.png`) });
      count++;
    }
    if (SHOTS) {
      for (const [w, tag] of [[1280, "desk"], [390, "phone"]]) {
        await page.setViewportSize({ width: w, height: 900 });
        await page.screenshot({ path: path.join(OUT, "shots", `${slug}-${p.replace(".html", "")}-${tag}.png`), fullPage: true });
      }
      await page.setViewportSize({ width: 900, height: 1200 });
    }
  }
  console.log(`render: issue ${slug} -> cover + ${count} graphics`);
  await ctx.close();
}
await browser.close();
server.close();
