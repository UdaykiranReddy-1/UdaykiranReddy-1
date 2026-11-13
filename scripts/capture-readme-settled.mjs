/**
 * Full README preview via <img> tags + real Chrome; wait for name animation to settle.
 */
import puppeteer from "puppeteer-core";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const chromePath = process.env.CHROME_PATH || "/opt/google/chrome/chrome";
const artifactDir = process.env.ARTIFACT_DIR || "/opt/cursor/artifacts";
const settleMs = Number(process.env.README_SETTLE_MS || "3000");
const dest =
  process.env.README_VERIFY_PATH ||
  path.join(artifactDir, "readme-profile-verify.png");
const pageW = 1012;

fs.mkdirSync(artifactDir, { recursive: true });

function assetDataUri(rel) {
  const p = path.join(repoRoot, rel);
  const b64 = fs.readFileSync(p).toString("base64");
  const ext = path.extname(rel).toLowerCase();
  const mime = ext === ".svg" ? "image/svg+xml" : "image/png";
  return `data:${mime};base64,${b64}`;
}

let body = fs.readFileSync(path.join(repoRoot, "README.md"), "utf8");
for (const rel of [
  "assets/profile-main.svg",
  "assets/link-linkedin.svg",
  "assets/link-sep.svg",
  "assets/link-email.svg",
  "assets/link-medium.svg",
]) {
  const uri = assetDataUri(rel);
  body = body.replaceAll(`src="${rel}"`, `src="${uri}"`);
}

const htmlPath = path.join(repoRoot, "_readme_settled_verify.html");
const html = `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<style>
html,body{margin:0;padding:24px 0;background:#0d1117;width:${pageW}px}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}
div{text-align:center}
img{border:0;vertical-align:middle}
a img{border:0}
</style>
</head>
<body>${body}</body></html>`;
fs.writeFileSync(htmlPath, html, "utf8");

function pathToFileURL(p) {
  let resolved = path.resolve(p).replace(/\\/g, "/");
  if (!resolved.startsWith("/")) resolved = "/" + resolved;
  return "file://" + encodeURI(resolved);
}

const browser = await puppeteer.launch({
  executablePath: chromePath,
  headless: true,
  args: ["--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--hide-scrollbars"],
});

const page = await browser.newPage();
await page.setViewport({ width: pageW, height: 1200, deviceScaleFactor: 2 });
await page.goto(pathToFileURL(htmlPath), { waitUntil: "load", timeout: 60000 });
await page.waitForFunction(
  () => {
    const imgs = document.querySelectorAll("img");
    return imgs.length > 0 && [...imgs].every((i) => i.complete && i.naturalWidth > 0);
  },
  { timeout: 60000 },
);
await new Promise((r) => setTimeout(r, settleMs));
await page.screenshot({ path: dest, type: "png" });
await browser.close();
fs.unlinkSync(htmlPath);
console.log(`wrote ${dest}`);
