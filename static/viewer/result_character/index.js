/**
 * Result Character — Einstiegspunkt der Ergebnisseite.
 *
 * Die Figur selbst steckt in `Ergebnisfigur` (ergebnisfigur.js), die
 * Renderschleife in `Videoschleife`, die Kopfzeile in `Kopfbedienung`. Hier
 * bleibt nur der Aufruf, den das Seitentemplate kennt. Vorher standen an
 * dieser Stelle 216 Zeilen in einer Funktion.
 */
import { Ergebnisfigur } from './ergebnisfigur.js';

/**
 * @param {Object} werte
 * @param {string} werte.canvasId       — id der <canvas>
 * @param {string} werte.videoId        — id des <video> (gibt den Takt vor)
 * @param {string} werte.bvhUrl         — BVH des Auftrags
 * @param {string} werte.panelId        — id des Seitenfelds
 * @param {string} werte.modelSelectId  — id der Modellauswahl in der Kopfzeile
 */
export async function initResultCharacter(werte) {
    return new Ergebnisfigur(werte).starten();
}
