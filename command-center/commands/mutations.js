import { makeId } from "../domain/ids.js";

/**
 * @typedef {import('../domain/document.js').CommandCenterDocument} CommandCenterDocument
 * @typedef {import('../domain/document.js').ReminderId} ReminderId
 * @typedef {import('../domain/document.js').QuickLinkId} QuickLinkId
 * @typedef {import('../domain/document.js').QuickLink} QuickLink
 * @typedef {import('../domain/document.js').Reminder} Reminder
 */

/**
 * @param {CommandCenterDocument} doc
 * @param {{ text: string; due: Reminder['due'] }} input
 * @returns {CommandCenterDocument}
 */
export function addReminder(doc, input) {
  /** @type {ReminderId} */
  const id = /** @type {ReminderId} */ (makeId("rem"));
  const item = {
    id,
    text: input.text.trim(),
    due: input.due,
    completed: false,
  };
  return {
    ...doc,
    reminders: {
      items: [...doc.reminders.items, item],
    },
  };
}

/**
 * @param {CommandCenterDocument} doc
 * @param {string} priority
 * @returns {CommandCenterDocument}
 */
export function setDayFocus(doc, priority) {
  return {
    ...doc,
    focus: { priority: priority.trim() },
  };
}

/**
 * @param {CommandCenterDocument} doc
 * @param {string} dayNote
 * @returns {CommandCenterDocument}
 */
export function setDayNote(doc, dayNote) {
  return {
    ...doc,
    today: { dayNote: dayNote.trim() },
  };
}

/**
 * @param {CommandCenterDocument} doc
 * @param {Omit<QuickLink, 'id'> & { id?: QuickLinkId }} link
 * @returns {CommandCenterDocument}
 */
export function upsertQuickLink(doc, link) {
  const id =
    link.id ??
    /** @type {QuickLinkId} */ (/** @type {QuickLinkId} */ (makeId("lnk")));
  const next = { id, label: link.label.trim(), href: link.href.trim() };
  const existing = doc.quickLinks.links.filter((l) => l.id !== id);
  return {
    ...doc,
    quickLinks: { links: [...existing, next] },
  };
}

/**
 * @param {CommandCenterDocument} doc
 * @param {ReminderId} id
 * @returns {CommandCenterDocument}
 */
export function toggleReminderComplete(doc, id) {
  return {
    ...doc,
    reminders: {
      items: doc.reminders.items.map((r) =>
        r.id === id ? { ...r, completed: !r.completed } : r
      ),
    },
  };
}
