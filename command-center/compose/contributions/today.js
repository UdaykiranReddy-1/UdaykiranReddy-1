/** @typedef {import('../../domain/document.js').CommandCenterDocument} CommandCenterDocument */
/** @typedef {import('../../fetch/morning-cache.js').ComposeContext} ComposeContext */

/**
 * @param {Date} now
 * @param {'Asia/Calcutta'} timezone
 */
function formatDateLabel(now, timezone) {
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: timezone,
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(now);
}

/** @type {import('../registry.js').PanelContribution} */
export const todayContribution = {
  panelId: "today",
  order: 1,
  slotId: "panel-today",
  title: "Today",
  /**
   * @param {CommandCenterDocument} doc
   * @param {ComposeContext} ctx
   */
  project(doc, ctx) {
    const cache = doc.morningCache;
    return {
      kind: "today",
      dateLabel: formatDateLabel(ctx.now, ctx.timezone),
      weather: cache.weather,
      dayNote: doc.today.dayNote,
    };
  },
};
