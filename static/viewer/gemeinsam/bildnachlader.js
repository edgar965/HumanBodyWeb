/**
 * Bildnachlader — Weiterleitung auf die kanonische Fassung in djangoBase.
 *
 * Wie `serverabruf.js` und `protokoll.js`: die Logik steht an EINER Stelle
 * (`djangobase/static/djangobase/js/bildnachlader.js`), die Module hier behalten
 * ihren kurzen relativen Import.
 */
export { Bildnachlader } from '/static/djangobase/js/bildnachlader.js';
