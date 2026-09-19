/**
 * Reihenfolge — welches Skelett auf welchem Platz der Vergleichsansicht steht.
 *
 * Auftrag Edgar (19.09.2026): „eine Spalte mit der Nummer, was die
 * Reihenfolge der Anzeige sein soll. Wenn ich die Nummer ändere, ändern sich
 * alle anderen entsprechend nach hinten. DEF ist immer das erste."
 *
 * Die Plätze sind die bisherigen: sechs vorn (x −3 … 4,5), drei dahinter
 * (z −2). Eine Folge ist die Liste der Schlüssel in Platzreihenfolge; Platz 1
 * gehört immer `def`. Kein Import — der Sichtschalter legt die Folge an die
 * Szene, dieses Modul rechnet nur (Node-Test `test_js_reihenfolge`).
 */
export class Reihenfolge {
    /** Platz i (0-basiert) -> [x, z] in Metern. */
    static PLAETZE = [[-3.0, 0], [-1.5, 0], [0.0, 0], [1.5, 0], [3.0, 0], [4.5, 0],
                      [-3.0, -2], [-1.5, -2], [0.0, -2]];

    /** Die Folge beim ersten Öffnen — die Aufstellung, wie sie bis heute stand. */
    static VORGABE = ['def', 'cmu', 'mixamo', 'mocapnet', 'bandai', 'openpose',
                      'smpl', 'uma', 'genesis9'];

    static ERSTER = 'def';

    /** Schlüssel im Browserspeicher. */
    static SCHLUESSEL = 'skelettTest_reihenfolge';

    /**
     * `schluessel` auf Platz `nummer` (1-basiert); wer dort und dahinter
     * stand, rückt um eins nach hinten. `def` bleibt auf 1, egal was verlangt
     * wird — und niemand kann vor ihn.
     */
    static verschoben(folge, schluessel, nummer) {
        if (schluessel === Reihenfolge.ERSTER || !folge.includes(schluessel)) {
            return [...folge];
        }
        const rest = folge.filter(k => k !== schluessel && k !== Reihenfolge.ERSTER);
        const ziel = Number.isFinite(nummer) ? Math.round(nummer) : folge.length;
        const platz = Math.min(Math.max(ziel - 2, 0), rest.length);
        rest.splice(platz, 0, schluessel);
        return [Reihenfolge.ERSTER, ...rest];
    }

    /** Gültig = dieselben Schlüssel wie die Vorgabe, `def` vorn. */
    static gueltig(folge) {
        if (!Array.isArray(folge) || folge.length !== Reihenfolge.VORGABE.length) {
            return false;
        }
        const menge = new Set(folge);
        return folge[0] === Reihenfolge.ERSTER
            && Reihenfolge.VORGABE.every(k => menge.has(k));
    }

    /** `{schluessel: {nummer, x, z}}` — die Plätze dieser Folge. */
    static plaetze(folge) {
        const aus = {};
        folge.forEach((schluessel, i) => {
            const [x, z] = Reihenfolge.PLAETZE[i] || [0, 0];
            aus[schluessel] = { nummer: i + 1, x, z };
        });
        return aus;
    }

    /** Die gemerkte Folge aus einem Text (JSON) — oder die Vorgabe. */
    static ausText(text) {
        try {
            const folge = JSON.parse(text);
            return Reihenfolge.gueltig(folge) ? folge : [...Reihenfolge.VORGABE];
        } catch (_fehler) {
            return [...Reihenfolge.VORGABE];
        }
    }
}
