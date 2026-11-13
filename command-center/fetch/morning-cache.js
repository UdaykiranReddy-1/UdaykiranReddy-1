import { withMorningCache } from "../domain/document.js";

/**
 * @typedef {import('../domain/document.js').CommandCenterDocument} CommandCenterDocument
 * @typedef {import('../domain/document.js').ComposeContext} ComposeContext
 */

/** @typedef {{ readonly now: Date; readonly timezone: 'Asia/Calcutta' }} ComposeContext */

/**
 * Start of local calendar day in Asia/Calcutta (UTC+5:30, no DST).
 * @param {Date} now
 */
function startOfCalcuttaDayIso(now) {
  const offsetMs = 5.5 * 60 * 60 * 1000;
  const local = new Date(now.getTime() + offsetMs);
  const y = local.getUTCFullYear();
  const m = local.getUTCMonth();
  const d = local.getUTCDate();
  const startUtc = Date.UTC(y, m, d) - offsetMs;
  return new Date(startUtc).toISOString();
}

/**
 * @param {CommandCenterDocument} doc
 * @param {ComposeContext} ctx
 */
export function needsMorningRefresh(doc, ctx) {
  if (!doc.morningCache.fetchedAtIso) {
    return true;
  }
  const dayStart = startOfCalcuttaDayIso(ctx.now);
  const fetched = doc.morningCache.fetchedAtIso;
  return fetched < dayStart;
}

/**
 * Sample morning fetch — no live API in v1.
 * @param {CommandCenterDocument} doc
 * @param {ComposeContext} ctx
 * @returns {Promise<CommandCenterDocument>}
 */
export async function ensureMorningFetchCache(doc, ctx) {
  if (!needsMorningRefresh(doc, ctx)) {
    return doc;
  }

  const weather = {
    summary: "Partly cloudy",
    tempC: 28,
    locationLabel: "Bengaluru",
  };

  let commute;
  if (doc.commute.mode === "wfh") {
    commute = {
      durationMinutes: null,
      label: "Working from home",
      stale: false,
    };
  } else {
    commute = {
      durationMinutes: 42,
      label: doc.commute.savedPlaceLabel ?? "Office",
      stale: false,
    };
  }

  return withMorningCache(doc, {
    weather,
    commute,
    fetchedAtIso: ctx.now.toISOString(),
  });
}
