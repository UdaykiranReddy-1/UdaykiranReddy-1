/**
 * Capture profile-main.svg via <img> + real Chrome + real-time waits (GitHub-like SMIL).
 */
import puppeteer from "puppeteer-core";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const chromePath = process.env.CHROME_PATH || "/opt/google/chrome/chrome";
const svgPath = path.join(repoRoot, "assets", "profile-main.svg");
const artifactDir = process.env.ARTIFACT_DIR || "/opt/cursor/artifacts";
const width = 992;
const delays = process.env.PROFILE_SMIL_DELAYS
  ? process.env.PROFILE_SMIL_DELAYS.split(",").map((s) => Number(s.trim()))
  : [100, 250, 400, 600, 900, 3000];

fs.mkdirSync(artifactDir, { recursive: true });

const htmlPath = path.join(repoRoot, "_profile_smil_verify.html");
const svgB64 = fs.readFileSync(svgPath).toString("base64");
const svgUri = `data:image/svg+xml;base64,${svgB64}`;

const html = `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<style>html,body{margin:0;background:#0d1117}</style>
</head>
<body>
<img id="profile" src="${svgUri}" width="${width}" alt="" />
</body></html>`;

fs.writeFileSync(htmlPath, html, "utf8");

function pathToFileURL(p) {
  let resolved = path.resolve(p).replace(/\\/g, "/");
  if (!resolved.startsWith("/")) resolved = "/" + resolved;
  return "file://" + encodeURI(resolved);
}

const browser = await puppeteer.launch({
  executablePath: chromePath,
  headless: true,
  args: [
    "--no-sandbox",
    "--disable-gpu",
    "--allow-file-access-from-files",
    "--hide-scrollbars",
  ],
});

async function captureAt(delayMs) {
  const page = await browser.newPage();
  await page.setViewport({
    width: width + 32,
    height: 820,
    deviceScaleFactor: 2,
  });
  await page.goto(pathToFileURL(htmlPath), { waitUntil: "load", timeout: 60000 });
  await page.waitForFunction(
    () => {
      const img = document.getElementById("profile");
      return img && img.complete && img.naturalWidth > 0;
    },
    { timeout: 60000 },
  );
  // t=0 is first paint after load; additional wait is elapsed animation time.
  if (delayMs > 0) {
    await new Promise((r) => setTimeout(r, delayMs));
  }
  const out = path.join(artifactDir, `profile-name-img-${delayMs}ms.png`);
  const el = await page.$("#profile");
  const box = await el.boundingBox();
  if (!box || box.width < 1) {
    await page.screenshot({ path: out, type: "png" });
  } else {
    await el.screenshot({ path: out, type: "png" });
  }
  await page.close();
  console.log(`wrote ${out}`);
}

for (const d of delays) {
  await captureAt(d);
}

await browser.close();
fs.unlinkSync(htmlPath);
