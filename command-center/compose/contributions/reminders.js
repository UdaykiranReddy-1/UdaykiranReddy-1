/** @typedef {import('../../domain/document.js').CommandCenterDocument} CommandCenterDocument */
/** @typedef {import('../../fetch/morning-cache.js').ComposeContext} ComposeContext */

/** @type {import('../registry.js').PanelContribution} */
export const remindersContribution = {
  panelId: "reminders",
  order: 3,
  slotId: "panel-reminders",
  title: "Reminders",
  /**
   * @param {CommandCenterDocument} doc
   */
  project(doc) {
    const dueToday = doc.reminders.items
      .filter((r) => (r.due === "today" || r.due === "overdue") && !r.completed)
      .map((r) => ({ id: r.id, text: r.text }));
    return {
      kind: "reminders",
      dueToday,
      canQuickAdd: true,
    };
  },
};
