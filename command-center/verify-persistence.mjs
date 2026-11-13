/**
 * Smoke test: load page, add reminder, set focus, reload, assert localStorage.
 */
import puppeteer from "puppeteer-core";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const chromePath = process.env.CHROME_PATH || "/opt/google/chrome/chrome";
const port = 9876;

const server = spawn(
  "python3",
  ["-m", "http.server", String(port), "--bind", "127.0.0.1"],
  { cwd: repoRoot, stdio: "pipe" }
);

await new Promise((r) => setTimeout(r, 400));

const browser = await puppeteer.launch({
  executablePath: chromePath,
  headless: true,
  args: ["--no-sandbox", "--disable-gpu"],
});

const page = await browser.newPage();
const url = `http://127.0.0.1:${port}/command-center/`;

await page.goto(url, { waitUntil: "networkidle0" });
const title = await page.title();
if (!title.includes("Morning Command Center")) {
  throw new Error(`Unexpected title: ${title}`);
}

const uniqueReminder = `agent-verify-${Date.now()}`;
const uniqueFocus = `Focus verify ${Date.now()}`;

await page.type('input[aria-label="Quick add reminder"]', uniqueReminder);
await page.click(".quick-add-row .btn:not(.btn-ghost)");
await page.waitForFunction(
  (text) => document.body.innerText.includes(text),
  {},
  uniqueReminder
);

const focusInput = await page.waitForSelector('input[aria-label="Today\'s focus"]');
await focusInput.click({ clickCount: 3 });
await focusInput.type(uniqueFocus);
await focusInput.evaluate((el) => el.blur());

await page.reload({ waitUntil: "networkidle0" });

const afterReload = await page.evaluate(() => {
  const raw = localStorage.getItem("command-center");
  return raw ? JSON.parse(raw) : null;
});

if (!afterReload) throw new Error("No localStorage document after reload");
const hasReminder = afterReload.reminders.items.some(
  (r) => r.text === uniqueReminder
);
const hasFocus = afterReload.focus.priority === uniqueFocus;

if (!hasReminder) throw new Error("Reminder not persisted");
if (!hasFocus) throw new Error("Focus not persisted");

const panelCount = await page.$$eval(".panel-slot h2", (els) => els.length);
if (panelCount !== 6) throw new Error(`Expected 6 panels, got ${panelCount}`);

console.log(
  JSON.stringify({
    ok: true,
    panels: panelCount,
    reminder: uniqueReminder,
    focus: uniqueFocus,
  })
);

await browser.close();
server.kill();
