import { assertDocumentInvariant, seedSampleDocument } from "../domain/document.js";

export const STORAGE_KEY = "command-center";

/**
 * @param {typeof STORAGE_KEY} key
 * @returns {import('../domain/document.js').CommandCenterDocument}
 */
export function loadDocument(key) {
  if (typeof localStorage === "undefined") {
    return seedSampleDocument();
  }
  const raw = localStorage.getItem(key);
  if (!raw) {
    const seeded = seedSampleDocument();
    saveDocument(key, seeded);
    return seeded;
  }
  try {
    const parsed = JSON.parse(raw);
    assertDocumentInvariant(parsed);
    return /** @type {import('../domain/document.js').CommandCenterDocument} */ (
      parsed
    );
  } catch {
    const seeded = seedSampleDocument();
    saveDocument(key, seeded);
    return seeded;
  }
}

/**
 * @param {typeof STORAGE_KEY} key
 * @param {import('../domain/document.js').CommandCenterDocument} doc
 */
export function saveDocument(key, doc) {
  assertDocumentInvariant(doc);
  localStorage.setItem(key, JSON.stringify(doc));
}
