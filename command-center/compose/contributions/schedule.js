/** @typedef {import('../../domain/document.js').CommandCenterDocument} CommandCenterDocument */
/** @typedef {import('../../fetch/morning-cache.js').ComposeContext} ComposeContext */

/**
 * @param {string} iso
 * @param {'Asia/Calcutta'} timezone
 */
function formatTimeLabel(iso, timezone) {
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: timezone,
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(new Date(iso));
}

/** @type {import('../registry.js').PanelContribution} */
export const scheduleContribution = {
  panelId: "schedule",
  order: 2,
  slotId: "panel-schedule",
  title: "Schedule",
  /**
   * @param {CommandCenterDocument} doc
   * @param {ComposeContext} ctx
   */
  project(doc, ctx) {
    const sorted = [...doc.schedule.events].sort(
      (a, b) =>
        new Date(a.startsAtIso).getTime() - new Date(b.startsAtIso).getTime()
    );
    const nextEvents = sorted.slice(0, 4).map((ev) => ({
      title: ev.title,
      timeLabel: formatTimeLabel(ev.startsAtIso, ctx.timezone),
    }));
    return {
      kind: "schedule",
      nextEvents,
    };
  },
};
