/**
 * @typedef {string & { readonly __brand: "ReminderId" }} ReminderId
 * @typedef {string & { readonly __brand: "QuickLinkId" }} QuickLinkId
 * @typedef {string & { readonly __brand: "ScheduleEventId" }} ScheduleEventId
 *
 * @typedef {'today' | 'schedule' | 'reminders' | 'commute' | 'quick-links' | 'focus'} PanelId
 *
 * @typedef {{
 *   readonly schemaVersion: 1;
 *   readonly user: { readonly timezone: 'Asia/Calcutta'; readonly displayName: string };
 *   readonly today: { readonly dayNote: string };
 *   readonly schedule: { readonly events: readonly ScheduleEvent[] };
 *   readonly reminders: { readonly items: readonly Reminder[] };
 *   readonly commute: {
 *     readonly mode: 'office' | 'wfh';
 *     readonly savedPlaceLabel: string | null;
 *     readonly savedPlaceQuery: string | null;
 *   };
 *   readonly quickLinks: { readonly links: readonly QuickLink[] };
 *   readonly focus: { readonly priority: string };
 *   readonly morningCache: {
 *     readonly weather: WeatherCache | null;
 *     readonly commute: CommuteCache | null;
 *     readonly fetchedAtIso: string | null;
 *   };
 * }} CommandCenterDocument
 */

/**
 * @typedef {{
 *   readonly id: ScheduleEventId;
 *   readonly title: string;
 *   readonly startsAtIso: string;
 *   readonly endsAtIso: string | null;
 * }} ScheduleEvent
 */

/**
 * @typedef {{
 *   readonly id: ReminderId;
 *   readonly text: string;
 *   readonly due: 'today' | 'overdue' | 'upcoming';
 *   readonly completed: boolean;
 * }} Reminder
 */

/**
 * @typedef {{
 *   readonly id: QuickLinkId;
 *   readonly label: string;
 *   readonly href: string;
 * }} QuickLink
 */

/**
 * @typedef {{
 *   readonly summary: string;
 *   readonly tempC: number;
 *   readonly locationLabel: string;
 * }} WeatherCache
 */

/**
 * @typedef {{
 *   readonly durationMinutes: number | null;
 *   readonly label: string;
 *   readonly stale: boolean;
 * }} CommuteCache
 */

import { makeId } from "./ids.js";

/** @param {unknown} doc */
export function assertDocumentInvariant(doc) {
  if (!doc || typeof doc !== "object") {
    throw new Error("Invalid command center document");
  }
  const d = /** @type {Record<string, unknown>} */ (doc);
  if (d.schemaVersion !== 1) {
    throw new Error("Unsupported schema version");
  }
  const user = /** @type {{ timezone?: string }} */ (d.user);
  if (!user || user.timezone !== "Asia/Calcutta") {
    throw new Error("Invalid timezone");
  }
}

/**
 * @param {CommandCenterDocument} doc
 * @param {CommandCenterDocument['morningCache']} cache
 * @returns {CommandCenterDocument}
 */
export function withMorningCache(doc, cache) {
  return { ...doc, morningCache: { ...cache } };
}

/**
 * Sample document — page is useful before any account exists.
 * @returns {CommandCenterDocument}
 */
export function seedSampleDocument() {
  const today = new Date();
  const y = today.getFullYear();
  const m = String(today.getMonth() + 1).padStart(2, "0");
  const d = String(today.getDate()).padStart(2, "0");

  /** @type {ScheduleEventId} */
  const ev1 = /** @type {ScheduleEventId} */ (makeId("evt"));
  /** @type {ScheduleEventId} */
  const ev2 = /** @type {ScheduleEventId} */ (makeId("evt"));
  /** @type {ScheduleEventId} */
  const ev3 = /** @type {ScheduleEventId} */ (makeId("evt"));

  /** @type {ReminderId} */
  const r1 = /** @type {ReminderId} */ (makeId("rem"));
  /** @type {ReminderId} */
  const r2 = /** @type {ReminderId} */ (makeId("rem"));

  /** @type {QuickLinkId} */
  const l1 = /** @type {QuickLinkId} */ (makeId("lnk"));
  /** @type {QuickLinkId} */
  const l2 = /** @type {QuickLinkId} */ (makeId("lnk"));
  /** @type {QuickLinkId} */
  const l3 = /** @type {QuickLinkId} */ (makeId("lnk"));

  return {
    schemaVersion: 1,
    user: {
      timezone: "Asia/Calcutta",
      displayName: "Uday Kiran Reddy",
    },
    today: {
      dayNote: "Standup at 10, ship the README tweak before lunch.",
    },
    schedule: {
      events: [
        {
          id: ev1,
          title: "Morning standup",
          startsAtIso: `${y}-${m}-${d}T04:30:00.000Z`,
          endsAtIso: `${y}-${m}-${d}T05:00:00.000Z`,
        },
        {
          id: ev2,
          title: "Deep work block",
          startsAtIso: `${y}-${m}-${d}T06:00:00.000Z`,
          endsAtIso: `${y}-${m}-${d}T08:00:00.000Z`,
        },
        {
          id: ev3,
          title: "Sync with design",
          startsAtIso: `${y}-${m}-${d}T09:30:00.000Z`,
          endsAtIso: null,
        },
      ],
    },
    reminders: {
      items: [
        {
          id: r1,
          text: "Call pharmacy",
          due: "today",
          completed: false,
        },
        {
          id: r2,
          text: "Reply to recruiter email",
          due: "today",
          completed: false,
        },
      ],
    },
    commute: {
      mode: "office",
      savedPlaceLabel: "Office — Koramangala",
      savedPlaceQuery: "Koramangala, Bengaluru",
    },
    quickLinks: {
      links: [
        {
          id: l1,
          label: "GitHub",
          href: "https://github.com/UdaykiranReddy-1",
        },
        {
          id: l2,
          label: "Calendar",
          href: "https://calendar.google.com",
        },
        {
          id: l3,
          label: "Notion",
          href: "https://notion.so",
        },
      ],
    },
    focus: {
      priority: "Ship profile-card README tweak",
    },
    morningCache: {
      weather: null,
      commute: null,
      fetchedAtIso: null,
    },
  };
}
