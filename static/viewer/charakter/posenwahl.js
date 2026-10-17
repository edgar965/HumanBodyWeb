import { _selectedInst } from './utils.js';
import { markDirty } from './undo.js';
import { Posenanwendung } from './posenanwendung.js';
import { Genesis9lauf } from './genesis9/genesis9lauf.js';
import { Genesis9posen } from './genesis9/genesis9posen.js';

/**
 * Posenwahl — eine Pose aus dem Reiter „Posen" auf die gewählte Figur legen,
 * je nach Bestand auf ihrem eigenen Weg (17.10.2026).
 *
 * Edgar, 17.10.2026: „mache alle vorhandenen Poses aus allen Modellen in Ordner
 * bei Poses (auch valkyrie, HumanBody usw)". Der Reiter zeigt jetzt zwei
 * Bestände (`Posenbaum` auf dem Server), und sie werden verschieden angewendet:
 *
 * - **HumanBody** (`quelle: 'modell'`): Quaternionen je Rigify-Knochen, im
 *   Browser auf das Skelett gelegt (`Posenanwendung.vomServer`).
 * - **Genesis 9** (`quelle: 'genesis9'`): Daz-Winkel und Regler, auf dem Server
 *   ins Netz gebacken (`Genesis9Modell.poseSetzen`) — derselbe Weg wie die
 *   Auswahl „Pose"/„Ausdruck" in den Eigenschaften der Figur (`Genesis9posen`),
 *   entprellt über `Genesis9lauf`. Ein Ausdruck (`art: 'ausdruck'`) setzt den
 *   Ausdruck, nicht die Pose.
 *
 * Die Formate sind nicht austauschbar. Passt die Figur nicht, sagt der Befund
 * es — ein Klick, der nichts bewirkt, muss sagen warum (Edgar, 09.09.2026).
 */
export class Posenwahl {

    /**
     * @param pose    `{id, name, art?}`
     * @param bestand `{kennung, titel, quelle}` aus dem Baum
     * @returns `{ok, text}` oder `{ok: false, grund}`
     */
    static async anwenden(pose, bestand, figur = _selectedInst()) {
        if (!pose) return { ok: false, grund: 'Keine Pose gewählt.' };
        if (!figur) return { ok: false, grund: 'Keine Figur gewählt.' };
        if (bestand?.quelle === 'genesis9') return Posenwahl._genesis9(pose, figur);
        const befund = await Posenanwendung.vomServer(pose.id, figur);
        return befund.ok
            ? { ok: true, text: `„${pose.name}" liegt an (${befund.gesetzt} Knochen).` }
            : befund;
    }

    static _genesis9(pose, figur) {
        if (figur.quelle !== 'genesis9') {
            return { ok: false,
                     grund: `„${pose.name}" ist eine Daz-Pose für Genesis-9-Figuren; die gewählte `
                            + `Figur kommt von ${figur.quelle || 'HumanBody'}.` };
        }
        const feld = pose.art === 'ausdruck' ? 'ausdruck' : 'pose';
        // `danach`: die Auswahl in den Eigenschaften der Figur zeigt dann dieselbe Pose.
        Genesis9lauf.planen(figur, () => figur.poseSetzen(feld, pose.id),
                            () => Genesis9posen.fuellen(figur), `pose:${feld}`);
        markDirty();
        return { ok: true,
                 text: `„${pose.name}" wird gestellt (${feld === 'ausdruck' ? 'Ausdruck' : 'Pose'}) — `
                       + 'der Server backt sie ins Netz.' };
    }

    /** Die Daz-Liste der Eigenschaften neu holen lassen — nach Verschieben oder Löschen. */
    static genesis9Vergessen() {
        Genesis9posen._liste = null;
        const figur = _selectedInst();
        if (figur?.quelle === 'genesis9') Genesis9posen.fuellen(figur);
    }
}
