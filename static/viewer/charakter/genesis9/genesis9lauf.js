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
 * EIN LAUF, DESSEN FIGUR NICHT MEHR IN DER SZENE IST, MELDET NICHTS (Edgar,
 * 20.09.2026: „undo funktioniert nicht bei den HB Morphs"): Rückgängig
 * während der Server noch rechnet baut die Szene aus dem Schnappschuss neu —
 * die Figur ist dann eine ANDERE Instanz. Kam der alte Lauf danach zurück,
 * schrieb `danach` (`nachziehen`) die Werte der verwaisten Instanz in die
 * Schieber (100 % am Regler, 0 in der Figur) und `markDirty` legte einen
 * Rückgängig-Stand davon an. Gemessen im Chrome: Regler „1", Figur ohne den
 * Morph. Jetzt: verwaist → weder Schieber noch Stapel anfassen.
 */
export class Genesis9lauf {

    static RUHE_MS = 200;
    static _laeufe = new Map();

    /**
     * @param inst     die Figur
     * @param aktion   () => Promise — was zu tun ist (z. B. `inst.reglerSetzen`)
     * @param danach   () => void — nach jedem gelungenen Lauf (Kopfzeile)
     */
    static planen(inst, aktion, danach = null) {
        const lauf = Genesis9lauf._lauf(inst);
        clearTimeout(lauf.zeitgeber);
        lauf.zeitgeber = setTimeout(
            () => Genesis9lauf._ausfuehren(inst, aktion, danach), Genesis9lauf.RUHE_MS);
    }

    static _lauf(inst) {
        let lauf = Genesis9lauf._laeufe.get(inst.id);
        if (!lauf) {
            lauf = { zeitgeber: null, laeuft: false, nachholen: null };
            Genesis9lauf._laeufe.set(inst.id, lauf);
        }
        return lauf;
    }

    static async _ausfuehren(inst, aktion, danach) {
        const lauf = Genesis9lauf._lauf(inst);
        if (lauf.laeuft) {
            lauf.nachholen = [aktion, danach];
            return;
        }
        lauf.laeuft = true;
        // Sanduhr, solange der Server rechnet (Edgar, 18.09.2026: „damit ich
        // weiss, wann die Property geändert wird").
        Sanduhr.an('Figur wird neu gerechnet …');
        try {
            await aktion();
            if (!Genesis9lauf.inSzene(inst)) { lauf.nachholen = null; return; }
            markDirty();
            danach?.();
        } catch (fehler) {
            const feld = document.getElementById('prop-genesis9-kopf');
            if (feld) feld.textContent = `Fehler: ${fehler.message}`;
        } finally {
            Sanduhr.aus();
            lauf.laeuft = false;
            const offen = lauf.nachholen;
            lauf.nachholen = null;
            if (offen) Genesis9lauf._ausfuehren(inst, ...offen);
        }
    }

    /** Ist diese Instanz noch die Figur der Szene (nicht durch Rückgängig ersetzt, nicht gelöscht)? */
    static inSzene(inst) {
        return state.characters.get(inst.id) === inst;
    }

    static vergessen(inst) {
        Genesis9lauf._laeufe.delete(inst.id);
    }
}
