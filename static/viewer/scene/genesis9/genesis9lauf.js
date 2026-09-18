import { markDirty } from '../undo.js';
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

    static vergessen(inst) {
        Genesis9lauf._laeufe.delete(inst.id);
    }
}
