/**
 * Render each link-chip SVG in Chrome at 4× device scale (height=24 CSS px).
 */
import puppeteer from "puppeteer-core";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const chromePath = process.env.CHROME_PATH || "/opt/google/chrome/chrome";
const artifactDir = process.env.ARTIFACT_DIR || "/opt/cursor/artifacts";
const scale = 4;

const chips = [
  ["linkedin", "assets/link-linkedin.svg"],
  ["email", "assets/link-email.svg"],
  ["medium", "assets/link-medium.svg"],
];

fs.mkdirSync(artifactDir, { recursive: true });

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

for (const [name, rel] of chips) {
  const svgB64 = fs.readFileSync(path.join(repoRoot, rel)).toString("base64");
  const uri = `data:image/svg+xml;base64,${svgB64}`;
  const htmlPath = path.join(repoRoot, `_link_icon_${name}.html`);
  const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<style>html,body{margin:0;background:#0d1117}</style>
</head><body>
<img id="chip" src="${uri}" height="24" alt=""/>
</body></html>`;
  fs.writeFileSync(htmlPath, html, "utf8");

  const page = await browser.newPage();
  await page.setViewport({
    width: 420,
    height: 120,
    deviceScaleFactor: scale,
  });
  const fileUrl =
    "file://" + encodeURI(path.resolve(htmlPath).replace(/\\/g, "/"));
  await page.goto(fileUrl, { waitUntil: "load", timeout: 60000 });
  await page.waitForFunction(
    () => {
      const img = document.getElementById("chip");
      return img && img.complete && img.naturalHeight > 0;
    },
    { timeout: 60000 },
  );
  const out = path.join(artifactDir, `link-icon-${name}-${scale}x.png`);
  const el = await page.$("#chip");
  await el.screenshot({ path: out, type: "png" });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log(`wrote ${out}`);
}

await browser.close();
