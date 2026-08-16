/**
 * Protokoll — Weiterleitung auf die kanonische Fassung in djangoBase.
 *
 * Umbau 16.08.2026: siehe serverabruf.js daneben. Der Debug-Schlüssel heißt in
 * djangoBase projektunabhängig `app.debug`; hier wird zusätzlich der bisherige
 * Schlüssel `humanbody.debug` gesetzt, damit ein gespeicherter Schalter
 * weiterwirkt.
 */
import { Protokoll } from '/static/djangobase/js/protokoll.js';

Protokoll.SCHLUESSEL = 'humanbody.debug';

export { Protokoll };
