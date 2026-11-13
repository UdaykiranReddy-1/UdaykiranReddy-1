/** @typedef {import('../../domain/document.js').CommandCenterDocument} CommandCenterDocument */

/** @type {import('../registry.js').PanelContribution} */
export const quickLinksContribution = {
  panelId: "quick-links",
  order: 5,
  slotId: "panel-quick-links",
  title: "Quick links",
  /**
   * @param {CommandCenterDocument} doc
   */
  project(doc) {
    return {
      kind: "quick-links",
      links: doc.quickLinks.links.map((l) => ({
        id: l.id,
        label: l.label,
        href: l.href,
      })),
    };
  },
};
