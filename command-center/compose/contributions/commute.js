/** @typedef {import('../../domain/document.js').CommandCenterDocument} CommandCenterDocument */

/** @type {import('../registry.js').PanelContribution} */
export const commuteContribution = {
  panelId: "commute",
  order: 4,
  slotId: "panel-commute",
  title: "Commute",
  /**
   * @param {CommandCenterDocument} doc
   */
  project(doc) {
    return {
      kind: "commute",
      mode: doc.commute.mode,
      display: doc.morningCache.commute,
    };
  },
};
