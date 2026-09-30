import { markDirty } from '../undo.js';
import { state } from '../state.js';
import { Sanduhr } from '../../gemeinsam/sanduhr.js';

/**
 * Genesis9lauf — entprellter Neubau der Figur nach einer Bedienung.
 *
 * Ein Regler-, Haut- oder Augenwechsel baut Körper, Anhänge und Kleidung
 * neu (`Genesis9Modell.neuFormen`). Das kostet 0,1 s auf dem Server plus
 * die Übertragung — bezahlbar, aber nicht bei jedem Pixel: Es wird
 * entprellt, und während ein Lauf unterwegs ist, wird nur der letzte
 * Wunsch gemerkt. Sonst überholten sich die Antworten und eine veraltete
 * Stellung bliebe stehen (Befund `garmentcode_live.js`, 08.09.2026;
 * dieselbe Bauart wie `umapythoneigenschaften.js`).
 *
 * Der Lauf ist JE FIGUR gemerkt: Zwei Genesis-9-Figuren in der Szene
 * dürfen sich nicht gegenseitig die Wünsche wegnehmen.
 *
 * DER LETZTE WUNSCH GILT JE SCHLÜSSEL, NICHT JE FIGUR (30.09.2026): Bis dahin
 * hielt eine Figur genau EINEN Wunsch. Zwei Häkchen in der Garderobe binnen
 * 200 ms — oder eines, während ein anderes Stück noch lud (Eirgrid: 101 s) —
 * und nur das letzte Stück kam; das erste Häkchen blieb stehen, das Stück
 * erschien nie und fehlte beim Speichern. Dasselbe für Haut gegen Augen: die
 * Setzer tragen ihren Wert erst IM Lauf ein, ein verworfener Wunsch verlor
 * die Einstellung. Jetzt nennt der Aufrufer, WORAUF sich der Wunsch bezieht
 * (`stueck:<kennung>`, `haut`, `regler:<name>` …): Derselbe Schlüssel
 * überschreibt sich wie früher (ein gezogener Schieber baut einmal), andere
 * Schlüssel laufen danach der Reihe nach. Ohne Schlüssel teilen sich alle
 * Aufrufer einen — das alte Verhalten.
 *
 * Zwei Stufen, damit ein laufender Neubau keinen Wunsch mitten im Ziehen
 * abholt: `wartend` (noch in der Ruhezeit) und `faellig` (Ruhezeit um).
 *
 * EIN LAUF, DESSEN FIGUR NICHT MEHR IN DER SZENE IST, MELDET NICHTS (Edgar,
 * 20.09.2026: „undo funktioniert nicht bei den HB Morphs"): Rückgängig
 * während der Server noch rechnet baut die Szene aus dem Schnappschuss neu —
 * die Figur ist dann eine ANDERE Instanz. Kam der alte Lauf danach zurück,
 * schrieb `danach` (`nachziehen`) die Werte der verwaisten Instanz in die
 * Schieber (100 % am Regler, 0 in der Figur) und `markDirty` legte einen
 * Rückgängig-Stand davon an. Gemessen im Chrome: Regler „1", Figur ohne den
 * Morph. Jetzt: verwaist → weder Schieber noch Stapel anfassen, offene
 * Wünsche verwerfen.
 */
export class Genesis9lauf {

    static RUHE_MS = 200;
    static _laeufe = new Map();

    /**
     * @param inst        die Figur
     * @param aktion      () => Promise — was zu tun ist (z. B. `inst.reglerSetzen`)
     * @param danach      () => void — nach jedem gelungenen Lauf (Kopfzeile)
     * @param schluessel  worauf sich der Wunsch bezieht; gleicher Schlüssel = der
     *                    spätere ersetzt den früheren, leer = der gemeinsame
     */
    static planen(inst, aktion, danach = null, schluessel = '') {
        const lauf = Genesis9lauf._lauf(inst);
        lauf.wartend.set(schluessel, [aktion, danach]);
        clearTimeout(lauf.zeitgeber);
        lauf.zeitgeber = setTimeout(() => {
            for (const [k, wunsch] of lauf.wartend) lauf.faellig.set(k, wunsch);
            lauf.wartend.clear();
            Genesis9lauf._abarbeiten(inst);
        }, Genesis9lauf.RUHE_MS);
    }

    static _lauf(inst) {
        let lauf = Genesis9lauf._laeufe.get(inst.id);
        if (!lauf) {
            lauf = { zeitgeber: null, laeuft: false, wartend: new Map(), faellig: new Map() };
            Genesis9lauf._laeufe.set(inst.id, lauf);
        }
        return lauf;
    }

    /** Die fälligen Wünsche der Reihe nach — ein laufender Durchgang nimmt neue mit. */
    static async _abarbeiten(inst) {
        const lauf = Genesis9lauf._lauf(inst);
        if (lauf.laeuft) return;
        lauf.laeuft = true;
        // Sanduhr, solange der Server rechnet (Edgar, 18.09.2026: „damit ich
        // weiss, wann die Property geändert wird").
        Sanduhr.an('Figur wird neu gerechnet …');
        try {
            while (lauf.faellig.size) {
                const [schluessel, [aktion, danach]] = lauf.faellig.entries().next().value;
                lauf.faellig.delete(schluessel);
                if (!await Genesis9lauf._ausfuehren(inst, aktion, danach)) {
                    lauf.faellig.clear();
                    lauf.wartend.clear();
                    return;
                }
            }
        } finally {
            Sanduhr.aus();
            lauf.laeuft = false;
        }
    }

    /** Ein Wunsch. `false`, wenn die Figur inzwischen nicht mehr in der Szene steht. */
    static async _ausfuehren(inst, aktion, danach) {
        try {
            await aktion();
            if (!Genesis9lauf.inSzene(inst)) return false;
            markDirty();
            danach?.();
        } catch (fehler) {
            const feld = document.getElementById('prop-genesis9-kopf');
            if (feld) feld.textContent = `Fehler: ${fehler.message}`;
        }
        return true;
    }

    /** Ist diese Instanz noch die Figur der Szene (nicht durch Rückgängig ersetzt, nicht gelöscht)? */
    static inSzene(inst) {
        return state.characters.get(inst.id) === inst;
    }

    static vergessen(inst) {
        Genesis9lauf._laeufe.delete(inst.id);
    }
}
