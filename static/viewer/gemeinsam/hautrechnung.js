import { Hautmaske } from './hautmaske.js';
import { Hautmaskegeometrie } from './hautmaskegeometrie.js';
import { Hauteinzugrechnung } from './hauteinzugrechnung.js';
import { Saumschnitt } from './saumschnitt.js';

/**
 * Hautrechnung — der Zahlenteil von `Hautverdeckung.anwenden`: welche Körperpunkte unter der Kleidung liegen und wohin die
 * verdeckten Ecken wandern. Ohne Three.js und ohne DOM, damit dieselbe Rechnung auf dem Hauptfaden (Rückfall, Konsole, Tests)
 * und im Web Worker (`hautarbeiter.js`) läuft — es ist derselbe Code, also dasselbe Ergebnis, Bit für Bit.
 *
 * WARUM EIN WORKER (09.10.2026, Edgar: „warum dauert laden des Characters ewig … ich brauche schnelles Anzeigen damit ich drehen
 * und vergrößern kann"): Am feinen Körper (104.480 Punkte, 7 Stücke) stand der Hauptfaden dafür 2,8 s im Leerlauf, 11–14 s bei
 * belasteter CPU, auf der Filmstufe (410.000 Punkte) bis 19 s — am Stück, in dieser Zeit ließ sich nichts drehen. Gemessen im
 * Leerlauf (ms, Chrome, 09.10.2026): alle Stücke gegen den Körper 1.460 (`Hautmaske._einStueck`, davon Ränder und Gitter 570),
 * Inseln 260, Normalen 270 (zweimal gerechnet, jetzt einmal), Wege auf der Haut 540, Dicke 540 (nur beim ersten Lauf je Körper),
 * Kanten 140 — zusammen 2.827 (`Hautverdeckung.anwenden`). Der Hauptfaden bekommt nur noch das Ergebnis und schreibt es ins Netz.
 */
export class Hautrechnung {

    /**
     * @param pos     Punkte des Körpers (Ruhelage), xyz
     * @param index   der VOLLE Index des Körpers (nie der gekürzte)
     * @param stoffe  Stücke `{schluessel, punkte, dreiecke, tiefe, starr, nahe, ersatz}` in der Lage des Körpers — nichts
     *                Three.js (der Worker bekommt eine Kopie)
     * @returns {{maske: Uint8Array, ersatz: Uint8Array, hoehe: Float32Array, rand: Float32Array, normalen: Float64Array,
     *            einzug: object, randabstaende: Array<Float64Array|null>, ms: number}}
     *   `randabstaende[i]` gehört zum Stück `stoffe[i]` (nur Ersatzstücke haben einen); `Hautmaskeersatz.maskieren` hängt ihn
     *   sonst an das Stück selbst, und das bleibt im Worker zurück.
     */
    static rechnen(pos, index, stoffe) {
        const t0 = performance.now();
        const n = pos.length / 3;
        const ersatz = new Uint8Array(n);
        const hoehe = new Float32Array(n).fill(-Infinity);
        const rand = new Float32Array(n).fill(Infinity);
        const normalen = Hautmaskegeometrie.normalen(pos, index);
        const maske = Hautmaske.verdeckt(pos, index, stoffe, { ersatz, hoehe, rand, normalen });
        // Die eigenen Ruhenormalen des Körpers gelten auch für den Einzug — nicht ein zweites Mal gerechnet (270 ms).
        const einzug = Hauteinzugrechnung.rechnen(pos, maske, index,
                                                  { kanten: Saumschnitt.kanten(stoffe), hautnormalen: normalen });
        return { maske, ersatz, hoehe, rand, normalen, einzug, randabstaende: stoffe.map((s) => s.randabstand || null),
                 ms: Math.round(performance.now() - t0) };
    }
}
