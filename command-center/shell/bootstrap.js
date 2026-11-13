import { loadDocument, saveDocument, STORAGE_KEY } from "../storage/document-store.js";
import { composeMorningLayout } from "../compose/composer.js";
import { ensureMorningFetchCache } from "../fetch/morning-cache.js";
import {
  addReminder,
  setDayFocus,
  setDayNote,
  toggleReminderComplete,
} from "../commands/mutations.js";
import { mountLayoutPlan, setMountHandlers } from "./mount.js";
import { emitDocumentChanged, onDocumentChanged } from "./events.js";

/**
 * @typedef {{
 *   readonly storageKey: typeof STORAGE_KEY;
 *   readonly timezone: 'Asia/Calcutta';
 *   readonly slotRoot: HTMLElement;
 * }} BootstrapOptions
 */

/**
 * @param {BootstrapOptions} options
 * @returns {() => void}
 */
export function bootstrapMorningCommandCenter(options) {
  const { storageKey, timezone, slotRoot } = options;

  /** @type {import('../domain/document.js').CommandCenterDocument} */
  let currentDoc = loadDocument(storageKey);

  const ctx = () => ({
    now: new Date(),
    timezone,
  });

  const refreshView = () => {
    const plan = composeMorningLayout(currentDoc, ctx());
    mountLayoutPlan(plan, slotRoot);
  };

  const commit = (/** @type {import('../domain/document.js').CommandCenterDocument} */ next) => {
    currentDoc = next;
    saveDocument(storageKey, next);
    emitDocumentChanged(next);
    refreshView();
  };

  setMountHandlers({
    onDayNote: (note) => commit(setDayNote(currentDoc, note)),
    onAddReminder: (text) =>
      commit(addReminder(currentDoc, { text, due: "today" })),
    onToggleReminder: (id) => commit(toggleReminderComplete(currentDoc, id)),
    onFocusChange: (priority) => commit(setDayFocus(currentDoc, priority)),
  });

  const unsub = onDocumentChanged((doc) => {
    currentDoc = doc;
  });

  (async () => {
    const withCache = await ensureMorningFetchCache(currentDoc, ctx());
    if (withCache !== currentDoc) {
      saveDocument(storageKey, withCache);
      currentDoc = withCache;
    }
    refreshView();
  })();

  return () => {
    unsub();
    setMountHandlers({});
  };
}
