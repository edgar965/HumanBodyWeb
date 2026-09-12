/**
 * Lagenmaske — welche Punkte eines Kleidungsstücks unter einem ANDEREN Stück
 * liegen.
 *
 * BEFUND (11.09.2026, Dance1, T-Shirt über Leggings): Der Bund der Leggings
 * drückte in Bewegung durch das T-Shirt — schwarze Flecken im roten Stoff.
 * Dieselbe Sache wie die Haut unter dem Stoff (`hautmaske.js`): zwei
 * getrennt gehäutete Flächen, wenige Millimeter auseinander, kommen sich an
 * jedem Gelenk nahe. Und dieselbe Lösung: Was unter einem anderen Stück
 * liegt, wird nicht gezeichnet.
 *
 * WER LIEGT AUSSEN, wird gemessen, nicht angenommen: Je Paar zählt, wie
 * viele Punkte von A ein Stück B mindestens `MINDEST_M` vor sich haben, und
 * umgekehrt; die Mehrheit entscheidet. Bei Hose über T-Shirt (Bund über den
 * Saum gebaut, 11.09.2026) gewinnt die Hose, bei T-Shirt über Leggings das
 * T-Shirt — die Reihenfolge des Anziehens sagt darüber nichts, und beim
 * Laden einer Szene gibt es sie gar nicht.
 *
 * DIE NORMALEN KOMMEN VON DER HAUT, nicht vom Stoffnetz: Jeder Stoffpunkt
 * bekommt die Normale des nächsten Körperpunkts (wie `hautmitstoff.py` auf
 * dem Server). Die Dreiecksorientierung eines Schnitts kann zum Körper
 * zeigen — das Vorzeichen daraus hat auf dem Server viermal in Folge das
 * Falsche gemeldet (CLAUDE.md, 07.–08.09.2026). Die Haut ist geschlossen,
 * ihr Vorzeichen steht fest.
 *
 * Die Maske selbst rechnet `Hautmaske.verdeckt` mit dem inneren Stück als
 * „Körper": Strahl entlang der Hautnormale, bis 25 mm darüber, 5 mm
 * Toleranz nach innen, freier Streifen nur an lockeren Kanten des äußeren
 * Stücks. OHNE THREE.JS — prüfbar in Node (`test_js_lagenmaske.py`).
 */
import { Hautmaske } from './hautmaske.js';
import { Hautmaskegeometrie as G } from './hautmaskegeometrie.js';

export class Lagenmaske {

    /** So weit muss das andere Stück mindestens VOR einem Punkt liegen,
     *  damit es für die Lagenfrage als „außen" zählt. */
    static MINDEST_M = 0.001;

    /**
     * Je Stück: `{maske, ueber}` — `maske` je Punkt 1, wenn ein anderes Stück
     * darüber liegt; `ueber` die Schlüssel dieser Stücke.
     *
     * @param koerper  punkte und dreiecke — die Haut in Ruhelage
     * @param stoffe   Liste von Stücken (schluessel, punkte, dreiecke) in derselben Lage
     * @param optionen wie bei `Hautmaske.verdeckt` (abstand, tiefe, randringe, eng)
     * @return Map schluessel → {maske, ueber}
     */
    static verdeckt(koerper, stoffe, optionen = {}) {
        const N = G.normalen(koerper.punkte, koerper.dreiecke);
        const gitter = G.punktgitter(koerper.punkte, G.ZELLE_M);
        const normalen = stoffe.map((s) => Lagenmaske.normalenVonHaut(s.punkte, koerper.punkte, N, gitter));
        const ergebnis = new Map(stoffe.map((s) => [
            s.schluessel, { maske: new Uint8Array(s.punkte.length / 3), ueber: [] }]));
        for (let a = 0; a < stoffe.length; a++) {
            for (let b = a + 1; b < stoffe.length; b++) {
                const lage = Lagenmaske.lage(stoffe[a], normalen[a], stoffe[b], normalen[b], optionen);
                if (lage === 0) continue;
                const [innen, aussen, nInnen] = lage > 0
                    ? [stoffe[a], stoffe[b], normalen[a]] : [stoffe[b], stoffe[a], normalen[b]];
                const m = Hautmaske.verdeckt(innen.punkte, innen.dreiecke, [aussen], { ...optionen, normalen: nInnen });
                const eintrag = ergebnis.get(innen.schluessel);
                for (let i = 0; i < m.length; i++) eintrag.maske[i] |= m[i];
                eintrag.ueber.push(aussen.schluessel);
            }
        }
        return ergebnis;
    }

    /**
     * +1: B liegt über A; −1: A liegt über B; 0: die beiden berühren sich
     * nicht. Gezählt werden Punkte, die das andere Stück mindestens
     * `MINDEST_M` vor sich haben (binnen `abstand`).
     */
    static lage(A, nA, B, nB, optionen = {}) {
        const o = { ...optionen, tiefe: -Lagenmaske.MINDEST_M, randringe: 0, inseln: 0,
                    suchweite: optionen.abstand ?? Hautmaske.ABSTAND_M };
        const bUeberA = Lagenmaske._summe(Hautmaske.verdeckt(A.punkte, null, [B], { ...o, normalen: nA }));
        const aUeberB = Lagenmaske._summe(Hautmaske.verdeckt(B.punkte, null, [A], { ...o, normalen: nB }));
        if (!bUeberA && !aUeberB) return 0;
        return bUeberA >= aUeberB ? 1 : -1;
    }

    /** Je Stoffpunkt die Normale des nächsten Körperpunkts — (0,0,0), wenn
     *  in drei Zellen (9 cm) keiner liegt; ein Nullstrahl trifft nichts. */
    static normalenVonHaut(P, koerperP, N, gitter) {
        const aus = new Float64Array(P.length);
        for (let i = 0; i < P.length / 3; i++) {
            const nah = G.naechsterPunkt(koerperP, gitter, G.ZELLE_M, P[3 * i], P[3 * i + 1], P[3 * i + 2]);
            if (!nah) continue;
            aus[3 * i] = N[3 * nah.j]; aus[3 * i + 1] = N[3 * nah.j + 1]; aus[3 * i + 2] = N[3 * nah.j + 2];
        }
        return aus;
    }

    static _summe(maske) {
        let s = 0;
        for (let i = 0; i < maske.length; i++) s += maske[i];
        return s;
    }
}
