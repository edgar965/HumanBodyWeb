/**
 * Hilfetexte des BVH-Studios.
 *
 * Aus tools.js herausgeloest (Umbau 15.08.2026): Von den 1012 Zeilen dieser
 * Datei waren 845 Hilfetexte — die Werkzeuge selbst standen davor und dahinter.
 *
 * UMBAU 18.08.2026: 329 Zeilen reiner Text. Geteilt nach Thema:
 *
 *     hilfetexte_spuren.js     Animation, Kamera, Licht, Audio
 *     hilfetexte_bedienung.js  Tastenkuerzel, Animationen, Export
 *
 * `HELP_CONTENT` bleibt die eine Anlaufstelle — `hilfefenster.js` schlaegt
 * darin nach.
 */
import { HILFE_SPUREN } from './hilfetexte_spuren.js';
import { HILFE_BEDIENUNG } from './hilfetexte_bedienung.js';

export const HELP_CONTENT = { ...HILFE_SPUREN, ...HILFE_BEDIENUNG };
