/**
 * Was sich die Oberfläche merken darf — und was nicht.
 *
 * AUFTRAG (Edgar, 09.09.2026): „merke dir die letzten Einstellungen auf allen
 * Tabs, z.B. GarmentCode, so dass sie beim nächsten Aufruf angeklickt sind."
 *
 * DIE GRENZE IST NICHT „ALLE FELDER", UND DAS HAT EINEN GRUND
 * ===========================================================
 * Im Bedienfeld stehen zwei Sorten Regler, und sie sehen gleich aus:
 *
 *   Einstellung    gehört zur OBERFLÄCHE. Welches Kleidungsstück gebaut
 *                  wird, wie weit der Ärmel sitzt, welche Ausgabe Finalize
 *                  schreibt. Beim nächsten Aufruf soll sie wieder so stehen.
 *   Objektzustand  gehört zur FIGUR, zum gewählten Netz oder zur Szene.
 *                  Die 289 Morphschieber im Reiter „Eigenschaften" zeigen die
 *                  Form DIESER Figur, `prop-garment-*` die Passung DIESES
 *                  Kleides, der Reiter „Szene" Licht und Kamera — die liegen
 *                  in der Szenendatei.
 *
 * Einen Objektzustand beim Start aus dem Gedächtnis zu setzen wäre der
 * schlimmere Fehler von beiden: Der Schieber behauptet dann etwas über das
 * Objekt, das nicht stimmt, und der erste Zug daran verformt es. Deshalb ist
 * dies eine POSITIVLISTE — ein neuer Reiter merkt zunächst nichts, statt
 * womöglich Zustand zu überschreiben.
 *
 * Gemessen am 09.09.2026 (Felder je Reiter, im Browser gezählt):
 *
 *     tab-eigenschaften  304   davon 289 Morphschieber ohne Kennung
 *     tab-garmentcode     81   71 Regler mit `data-pfad`, dazu Vorlage
 *     tab-modell          55   45 Knochenregler des Generators
 *     tab-assets          49   Regler des GEWÄHLTEN Zubehörs
 *     tab-szene           22   Licht, Boden, Kamera
 *     tab-kleider         16   Regler des GEWÄHLTEN Kleides
 *     tab-finalize        10   Ausgabeoptionen
 *     tab-rigging          9
 *     tab-animation        5
 *
 * Ohne Three.js und ohne DOM, damit die Entscheidung prüfbar ist
 * (`core/tests/unit/test_js_gedaechtniswahl.py`) — dasselbe Muster wie
 * `greifrechnung` und `fortschrittsrechnung`.
 */
export class Gedaechtniswahl {

    /**
     * Die Reiter, deren Felder Einstellungen sind.
     *
     * Nicht dabei und warum:
     *   eigenschaften  Morphs, Formregler, `prop-*` — Zustand des Objekts
     *   kleider        Regler des gewählten Kleidungsstücks
     *   assets         Regler des gewählten Zubehörs
     *   szene          Licht/Boden/Kamera stehen in der Szenendatei; ein
     *                  zweites Gedächtnis daneben läuft auseinander
     *   modell         der Generator führt seinen eigenen Zustand
     *                  (`Modellbauzustand`) und liest ihn aus der Figur
     */
    static REITER = ['garmentcode', 'animation', 'rigging', 'finalize'];

    /** Feldarten, die sich nicht wiederherstellen lassen oder Inhalte
     *  verstecken würden (ein gesetzter Suchfilter sieht aus wie eine leere
     *  Liste — dieselbe Falle wie zugeklappte Bereiche, 08.09.2026). */
    static ARTEN_AUS = ['file', 'search', 'password', 'hidden',
                        'submit', 'button', 'reset'];

    /** Kennungen, die trotz erlaubtem Reiter Objektzustand tragen. */
    static KENNUNG_AUS = ['prop-'];

    /** Trennzeichen im Ablageschlüssel. */
    static TRENNER = '/';

    /**
     * Darf dieses Feld gemerkt werden?
     *
     * @param feld `{reiter, kennung, art}` — `reiter` ohne `tab-`-Präfix,
     *   `kennung` die `id` oder der `data-pfad`, `art` der `type`.
     */
    static merkbar(feld) {
        const { reiter, kennung, art } = feld || {};
        if (!reiter || !kennung) return false;
        if (!Gedaechtniswahl.REITER.includes(reiter)) return false;
        if (Gedaechtniswahl.ARTEN_AUS.includes(art)) return false;
        return !Gedaechtniswahl.KENNUNG_AUS.some((p) => kennung.startsWith(p));
    }

    /** Der Ablageschlüssel eines Feldes. */
    static schluessel(reiter, kennung) {
        return `${reiter}${Gedaechtniswahl.TRENNER}${kennung}`;
    }

    /** Reiter aus einer Element-Id wie `tab-garmentcode`. */
    static reiterName(paneId) {
        return (paneId || '').replace(/^tab-/, '');
    }
}
