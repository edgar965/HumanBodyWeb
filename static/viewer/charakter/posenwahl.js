import { _selectedInst } from './utils.js';
import { markDirty } from './undo.js';
import { Posenanwendung } from './posenanwendung.js';
import { Genesis9lauf } from './genesis9/genesis9lauf.js';
import { Genesis9posen } from './genesis9/genesis9posen.js';
import { Genesis9posenvorschau } from './genesis9/genesis9posenvorschau.js';

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
 * Eine HumanBody-Pose auf einer Genesis-9-Figur geht seit 17.10.2026 als
 * `hb:<id>` den Genesis-Weg: Der Server überträgt sie auf die Daz-Knochen
 * (`G9hbpose`). Daz-Posen auf HumanBody gibt es nicht. Passt die Figur nicht,
 * sagt der Befund es — ein Klick, der nichts bewirkt, muss sagen warum (Edgar,
 * 09.09.2026).
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
        // Eine HumanBody-Pose auf Genesis 9 (17.10.2026, Edgar: „baue die Übertragung"): als `hb:<id>` wie ein Daz-Preset —
        // der Server rechnet die Daz-Winkel (`G9hbpose`), Vorschau und Neubau laufen gleich.
        if (figur.quelle === 'genesis9') return Posenwahl._genesis9({ ...pose, id: `hb:${pose.id}`, art: 'pose' }, figur);
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
        // Sofort: das vorhandene Skelett in die Pose drehen; der genaue Neubau folgt (`Genesis9posenvorschau`).
        Genesis9posenvorschau.zeigen(figur, feld, pose.id);
        // `danach`: die Auswahl in den Eigenschaften der Figur zeigt dann dieselbe Pose.
        Genesis9lauf.planen(figur, () => figur.poseSetzen(feld, pose.id),
                            () => Genesis9posen.fuellen(figur), `pose:${feld}`);
        markDirty();
        return { ok: true,
                 text: `„${pose.name}" wird gestellt (${feld === 'ausdruck' ? 'Ausdruck' : 'Pose'}) — `
                       + 'der Server backt sie ins Netz.' };
    }

    /**
     * „A-Pose (Reset)" je Figurart (17.10.2026, Edgar: „A-Pose reset funktioniert auch nicht"): Der Knopf
     * kannte nur HumanBody (`Posenanwendung.zuruecksetzen`), eine Genesis-9-Figur bekam die Absage für
     * HumanBody-Posen. Genesis 9 steht ohne Daz-Pose in ihrer Ruhelage (A-Pose): die Pose leeren, der
     * Server backt neu. Der Ausdruck bleibt — er gehört zum Gesicht, nicht zur Haltung.
     */
    static zuruecksetzen(figur = _selectedInst()) {
        if (figur?.quelle !== 'genesis9') return Posenanwendung.zuruecksetzen();
        if (!figur.pose) return { ok: true, text: 'Die Figur steht schon in der Ruhelage.' };
        Genesis9posenvorschau.zeigen(figur, 'pose', '');
        Genesis9lauf.planen(figur, () => figur.poseSetzen('pose', ''),
                            () => Genesis9posen.fuellen(figur), 'pose:pose');
        markDirty();
        return { ok: true, text: 'Ruhelage — der Server backt die Figur neu.' };
    }

    /** Die Daz-Liste der Eigenschaften neu holen lassen — nach Verschieben oder Löschen. */
    static genesis9Vergessen() {
        Genesis9posen._liste = null;
        const figur = _selectedInst();
        if (figur?.quelle === 'genesis9') Genesis9posen.fuellen(figur);
    }
}
