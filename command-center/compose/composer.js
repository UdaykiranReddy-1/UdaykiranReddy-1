import { defaultPanelRegistry } from "./registry.js";

/**
 * @typedef {import('../domain/document.js').CommandCenterDocument} CommandCenterDocument
 * @typedef {import('../fetch/morning-cache.js').ComposeContext} ComposeContext
 */

/**
 * @typedef {{
 *   readonly composedAtIso: string;
 *   readonly slots: readonly PanelSlot[];
 * }} MorningLayoutPlan
 */

/**
 * @typedef {{
 *   readonly panelId: import('../domain/document.js').PanelId;
 *   readonly slotId: string;
 *   readonly title: string;
 *   readonly payload: import('./registry.js').PanelPayload;
 * }} PanelSlot
 */

/**
 * @param {CommandCenterDocument} doc
 * @param {ComposeContext} ctx
 * @param {Pick<CommandCenterDocument, 'morningCache'>} [cache]
 * @returns {MorningLayoutPlan}
 */
export function composeMorningLayout(doc, ctx, cache) {
  const docForProject =
    cache != null ? { ...doc, morningCache: cache.morningCache } : doc;
  const registry = [...defaultPanelRegistry()].sort(
    (a, b) => a.order - b.order
  );
  const slots = registry.map((c) => ({
    panelId: c.panelId,
    slotId: c.slotId,
    title: c.title,
    payload: c.project(docForProject, ctx, cache),
  }));
  return {
    composedAtIso: ctx.now.toISOString(),
    slots,
  };
}
