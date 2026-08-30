import { REGION_DEFS, REGION_RADIUS } from './kleiderregionen.js';

/**
 * Bereichsgewichte — wie stark jeder Punkt eines Kleidungsstücks zu welchem
 * der fünf Bänder gehört.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Dieselbe Rechnung stand zweimal —
 * `scene/kleidung_anpassen.js` (auf `inst.*`) und `viewer/garment.js` (auf
 * `state.*`). Gleiche Formel, gleiche Konstanten, zwei Fassungen: einmal
 * ausgeschrieben mit Klammern, einmal auf eine Zeile gedrückt. Die Tabelle
 * dahinter (`kleiderregionen.js`) war am 28.08.2026 schon aus demselben Grund
 * zusammengelegt worden — die Rechnung blieb liegen.
 *
 * WAS HIER PASSIERT: Jeder Punkt bekommt seine relative Höhe `t` im
 * Kleidungsstück (0 unten, 1 oben). Je Band wird der Abstand zu dessen Mitte
 * gemessen; innerhalb des Radius fällt das Gewicht als halbe Kosinuswelle von
 * 1 auf 0 ab. Ein harter Schnitt (drin = 1, draußen = 0) ergäbe an den
 * Bandgrenzen sichtbare Stufen im Netz.
 *
 * DER RADIUS IST NICHT FREI: Bei Mitten im Abstand 0,20 und Radius 0,20
 * berühren sich die Bänder genau, und jeder Punkt liegt in höchstens zwei. Wer
 * den Radius ändert, verschiebt damit auch, wie stark benachbarte Regler
 * zusammenwirken.
 *
 * AN DEN ENDEN WIRKEN DIE REGLER NUR HALB. Gemessen über 1.001 Punkte:
 * zwischen den äußersten Mitten (0,10 bis 0,90) ist die Summe der fünf
 * Gewichte exakt 1, ganz unten und ganz oben aber **0,5** — dort gibt es kein
 * Nachbarband, das die zweite Hälfte beiträgt. Der Saum eines Rocks bewegt
 * sich also nur halb so weit wie seine Mitte, wenn man am Regler „bottom"
 * zieht. Das ist gewollt (der Rand soll nicht abreißen), sieht aber wie ein
 * schwacher Regler aus.
 *
 * DAS IST DIE STELLE, an der ein Regler „nichts tut": Sind die Gewichte für
 * ein Band überall 0 — etwa weil das Kleidungsstück flach ist und `yRange`
 * gegen null geht —, bewegt der zugehörige Schieber nichts. Kein Fehler, kein
 * Eintrag in der Konsole, das Netz steht nur still.
 */
export class Bereichsgewichte {
    /**
     * @param {Float32Array|Array} punkte Ruhelage des Netzes, x/y/z je Punkt
     * @returns {Object|null} {bandId: Float32Array} — null ohne Punkte
     */
    static rechnen(punkte) {
        if (!punkte) return null;
        const anzahl = punkte.length / 3;
        let yMin = Infinity, yMax = -Infinity;
        for (let i = 0; i < anzahl; i++) {
            const y = punkte[i * 3 + 1];
            if (y < yMin) yMin = y;
            if (y > yMax) yMax = y;
        }
        // Ein flaches Kleidungsstück hätte sonst eine Division durch null; mit
        // dieser Untergrenze landet jeder Punkt bei t = 0 statt bei NaN.
        const spanne = yMax - yMin || 1e-6;
        const gewichte = {};
        for (const band of REGION_DEFS) gewichte[band.id] = new Float32Array(anzahl);
        for (let i = 0; i < anzahl; i++) {
            const t = (punkte[i * 3 + 1] - yMin) / spanne;
            for (const band of REGION_DEFS) {
                const abstand = Math.abs(t - band.center);
                if (abstand < REGION_RADIUS) {
                    gewichte[band.id][i] =
                        0.5 * (1 + Math.cos(Math.PI * abstand / REGION_RADIUS));
                }
            }
        }
        return gewichte;
    }
}
