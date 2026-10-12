// Renders a book's cover and graphics to PNG with Chromium (Kindle can't draw SVG/CSS art).
//
//   node build/book-render.mjs <slug>            -> build/out/book/<slug>/g/{cover,g-*}.png
//   node build/book-render.mjs <slug> --kindle   -> page-by-page previews of the built EPUB at
//                                                   Kindle Paperwhite size, in greyscale:
//                                                   build/out/book/<slug>/kindle/*.png
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require("playwright"); }
catch { playwright = require("/opt/node22/lib/node_modules/playwright"); }

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const slug = process.argv[2];
if (!slug) throw new Error("usage: node build/book-render.mjs <slug> [--kindle]");
const OUT = path.join(ROOT, "build", "out", "book", slug);
const KINDLE = process.argv.includes("--kindle");

const TYPES = { ".html": "text/html", ".xhtml": "application/xhtml+xml", ".css": "text/css", ".svg": "image/svg+xml",
  ".woff2": "font/woff2", ".png": "image/png", ".jpg": "image/jpeg", ".json": "application/json" };
const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(req.url.split("?")[0]));
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404).end(); return; }
  res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const launchOpts = {};
if (fs.existsSync("/opt/pw-browsers")) {
  const dir = fs.readdirSync("/opt/pw-browsers").find((d) => /^chromium-\d+$/.test(d));
  const exe = dir && path.join("/opt/pw-browsers", dir, "chrome-linux", "chrome");
  if (exe && fs.existsSync(exe)) launchOpts.executablePath = exe;
}
const browser = await playwright.chromium.launch(launchOpts);

if (!KINDLE) {
  const gdir = path.join(OUT, "g");
  fs.rmSync(gdir, { recursive: true, force: true });
  fs.mkdirSync(gdir, { recursive: true });
  const jobs = JSON.parse(fs.readFileSync(path.join(OUT, "render.json"), "utf8"));
  const ctx = await browser.newContext({ viewport: { width: 800, height: 1280 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const failed = [];
  page.on("requestfailed", (r) => failed.push(r.url()));
  page.on("response", (r) => { if (r.status() >= 400) failed.push(r.url()); });
  let n = 0;
  for (const { page: p, ids } of jobs) {
    await page.goto(`${base}/build/out/book/${slug}/pages/${p}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    if (failed.length) throw new Error(`render: missing files on ${p}: ${[...new Set(failed)].join(", ")}`);
    for (const id of ids) {
      await page.locator(`#${id}`).screenshot({ path: path.join(gdir, `${id}.png`), omitBackground: false });
      n++;
    }
  }
  console.log(`render: ${n} images (cover + graphics) -> ${path.relative(ROOT, gdir)}`);
} else {
  // unpack the EPUB and show each chapter the way a 6" e-ink Kindle would (roughly)
  const kdir = path.join(OUT, "kindle");
  fs.rmSync(kdir, { recursive: true, force: true });
  fs.mkdirSync(path.join(kdir, "src"), { recursive: true });
  execFileSync("python3", ["-I", "-c", `import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])`,
    path.join(ROOT, "docs", "books", slug, `${slug}.epub`), path.join(kdir, "src")]);
  const opf = fs.readFileSync(path.join(kdir, "src", "OEBPS", "content.opf"), "utf8");
  const files = [...opf.matchAll(/href="([\w.-]+\.xhtml)"/g)].map((m) => m[1]).filter((f) => f !== "nav.xhtml");
  const ctx = await browser.newContext({ viewport: { width: 540, height: 720 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const kindleCss = `html{filter:grayscale(1)} body{font-family:Georgia,serif;font-size:17px;line-height:1.4;margin:28px 26px;background:#fff;color:#000}`;
  let i = 0;
  for (const f of files) {
    await page.goto(`${base}/build/out/book/${slug}/kindle/src/OEBPS/${f}`, { waitUntil: "networkidle" });
    await page.addStyleTag({ content: kindleCss });
    // Kindle caps images at one screen
    await page.addStyleTag({ content: "img{max-height:664px;object-fit:contain}" });
    const bad = await page.$$eval("img", (ims) => ims.filter((im) => !im.complete || im.naturalWidth === 0).map((im) => im.src));
    if (bad.length) throw new Error(`kindle preview: broken images in ${f}: ${bad.join(", ")}`);
    await page.screenshot({ path: path.join(kdir, `${String(i++).padStart(2, "0")}-${f.replace(".xhtml", "")}.png`), fullPage: true });
  }
  console.log(`kindle preview: ${i} files -> ${path.relative(ROOT, kdir)}`);
}
await browser.close();
server.close();
