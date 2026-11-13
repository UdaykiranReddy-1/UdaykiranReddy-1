/** @typedef {import('../domain/document.js').CommandCenterDocument} CommandCenterDocument */

/** @type {Set<(doc: CommandCenterDocument) => void>} */
const listeners = new Set();

/** @typedef {() => void} Unsubscribe */

/**
 * @param {(doc: CommandCenterDocument) => void} handler
 * @returns {Unsubscribe}
 */
export function onDocumentChanged(handler) {
  listeners.add(handler);
  return () => listeners.delete(handler);
}

/**
 * @param {CommandCenterDocument} doc
 */
export function emitDocumentChanged(doc) {
  for (const h of listeners) {
    h(doc);
  }
}
