/**
 * Lipsynckurve — die Reglerstellung des Mundes an einer Zeit, aus Rhubarbs Cues.
 *
 * Ein Cue ist `{start, end, form}` (Sekunden, Form A–H/X); die Cues stoßen
 * aneinander und stehen in Zeitfolge. Rhubarb schaltet hart um — ein Mund,
 * der in einem Bild von D auf A springt, flackert. Deshalb läuft an jeder
 * Grenze ein Übergang von `UEBERGANG` Sekunden: die alte Form klingt aus, die
 * neue kommt, linear auf den Reglern gemischt (dieselbe Überlegung wie
 * `Mimikkurve.mischen`). Vor dem ersten und nach dem letzten Cue ist der
 * Mund in Ruhe (X). Die Tabellen Form -> Regler (`Lipsyncformen`) werden hier
 * mit ausgeführt, damit ein Test beides aus einem Modul liest
 * (`test_js_lipsynckurve` rechnet in Node).
 */
import { Lipsyncformen } from './lipsyncformen.js';

export { Lipsyncformen };

export class Lipsynckurve {

    /** Sekunden, über die eine Form in die nächste läuft (Rhubarb-Cues sind ≥ 0,05 s). */
    static UEBERGANG = 0.06;

    /** Stelle des Cues, in dem `t` liegt — oder −1. */
    static stelle(cues, t) {
        let lo = 0, hi = (cues?.length || 0) - 1;
        while (lo <= hi) {
            const m = (lo + hi) >> 1, c = cues[m];
            if (t < c.start) hi = m - 1;
            else if (t >= c.end) lo = m + 1;
            else return m;
        }
        return -1;
    }

    /** Die Form (Buchstabe) an `t` — `X` außerhalb. */
    static form(cues, t) {
        const i = Lipsynckurve.stelle(cues, t);
        return i < 0 ? 'X' : (cues[i].form || 'X');
    }

    /**
     * Gewichte an `t`: Tabelle[Form] der laufenden Form, in den ersten
     * `UEBERGANG` Sekunden gemischt mit der Form davor.
     * @param cues     Rhubarb-Cues
     * @param t        Sekunden ab Tonbeginn
     * @param tabelle  Form -> `{regler: gewicht}` (`Lipsyncformen`)
     */
    static gewichte(cues, t, tabelle, uebergang = Lipsynckurve.UEBERGANG) {
        const i = Lipsynckurve.stelle(cues, t);
        if (i < 0) return {};
        const jetzt = tabelle[cues[i].form] || {};
        const vorher = i > 0 ? (tabelle[cues[i - 1].form] || {}) : {};
        const u = uebergang > 0 ? Math.min(1, (t - cues[i].start) / uebergang) : 1;
        if (u >= 1) return { ...jetzt };
        /** @type {Object<string, number>} */
        const aus = {};
        for (const regler of new Set([...Object.keys(vorher), ...Object.keys(jetzt)])) {
            const w = (vorher[regler] || 0) * (1 - u) + (jetzt[regler] || 0) * u;
            if (w) aus[regler] = w;
        }
        return aus;
    }

    /** Zwei Gewichtssätze summieren, je Regler auf `max` gedeckelt. */
    static addieren(a, b, max = 1) {
        const aus = { ...(a || {}) };
        for (const [k, w] of Object.entries(b || {})) {
            aus[k] = Math.max(-max, Math.min(max, (aus[k] || 0) + w));
        }
        return aus;
    }
}
