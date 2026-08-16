/**
 * Serverabruf — Weiterleitung auf die kanonische Fassung in djangoBase.
 *
 * Umbau 16.08.2026: Die Klasse liegt seit heute in
 * `djangobase/static/djangobase/js/serverabruf.js` und wird von den Umstellern
 * unter `djangobase/umbau/` vorausgesetzt. Hier bleibt nur die Weiterleitung —
 * so behalten die rund 60 Module ihren kurzen relativen Import, und die Logik
 * steht an EINER Stelle (Punkt 6 und 8 des Auftrags: keine Duplikate).
 */
export { Serverabruf } from '/static/djangobase/js/serverabruf.js';
