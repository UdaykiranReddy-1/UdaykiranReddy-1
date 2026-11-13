import { todayContribution } from "./contributions/today.js";
import { scheduleContribution } from "./contributions/schedule.js";
import { remindersContribution } from "./contributions/reminders.js";
import { commuteContribution } from "./contributions/commute.js";
import { quickLinksContribution } from "./contributions/quick-links.js";
import { focusContribution } from "./contributions/focus.js";

/**
 * @typedef {import('../domain/document.js').CommandCenterDocument} CommandCenterDocument
 * @typedef {import('../fetch/morning-cache.js').ComposeContext} ComposeContext
 * @typedef {import('../domain/document.js').PanelId} PanelId
 */

/**
 * @typedef {object} PanelPayload
 * @property {string} kind
 */

/**
 * @template {PanelPayload} P
 * @typedef {{
 *   readonly panelId: PanelId;
 *   readonly order: number;
 *   readonly slotId: string;
 *   readonly title: string;
 *   project: (
 *     doc: CommandCenterDocument,
 *     ctx: ComposeContext,
 *     cache?: Pick<CommandCenterDocument, 'morningCache'>
 *   ) => P;
 * }} PanelContribution
 */

export function defaultPanelRegistry() {
  return [
    todayContribution,
    scheduleContribution,
    remindersContribution,
    commuteContribution,
    quickLinksContribution,
    focusContribution,
  ];
}

/**
 * @param {readonly PanelContribution[]} base
 * @param {PanelContribution} contribution
 */
export function registerPanelContribution(base, contribution) {
  const without = base.filter((c) => c.panelId !== contribution.panelId);
  return [...without, contribution].sort((a, b) => a.order - b.order);
}
