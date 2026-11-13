/** @typedef {import('../../domain/document.js').CommandCenterDocument} CommandCenterDocument */

/** @type {import('../registry.js').PanelContribution} */
export const focusContribution = {
  panelId: "focus",
  order: 6,
  slotId: "panel-focus",
  title: "Focus",
  /**
   * @param {CommandCenterDocument} doc
   */
  project(doc) {
    return {
      kind: "focus",
      priority: doc.focus.priority,
    };
  },
};
