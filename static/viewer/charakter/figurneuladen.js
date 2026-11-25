import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { markDirty } from './undo.js';
import { Charakterkoerper } from './charakter_koerper.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Sanduhr } from '../gemeinsam/sanduhr.js';

/**
 * Figurneuladen — das Netz einer HumanBody-Figur nach einem Reglerzug neu holen (25.11.2026 aus `properties.js` herausgelöst).
 *
 * EIN Neuladen zur Zeit, der letzte Wert gewinnt — ohne Ruhezeit (bis dahin 300 ms; Edgar: „die regler müssen alle viel schneller werden“). Gemessen an F1 (Chrome, fünf Züge): 126–160 ms
 * vom Zug bis zum neuen Bild. Die Sanduhr steht vom ersten Zug an, bis der letzte Wert zu sehen ist (Edgar: „Mach eine Sanduhr wenn ein regler nicht durch ist“).
 */
export class Figurneuladen {

    static _figur = null;
    static _laeuft = false;

    /** @param nachher  (figur) => void — die Anzeigen der Seite nachziehen, wenn die Figur gerade gezeigt wird */
    static planen(inst, nachher) {
        Figurneuladen._figur = inst;
        if (Figurneuladen._laeuft) return;
        Figurneuladen._laeuft = true;
        Sanduhr.an('Figur wird neu gerechnet …');
        setTimeout(() => Figurneuladen._laufen(nachher), 0);      // ein Preset stellt viele Regler auf einmal: erst danach
    }

    static async _laufen(nachher) {
        try {
            for (let figur = Figurneuladen._figur; figur; figur = Figurneuladen._figur) {
                Figurneuladen._figur = null;
                await Charakterkoerper.neuLaden(figur);
                fn.updateVertexCount();
                fn.updateCharacterListUI();
                if (state.currentPropsCharId === figur.id) nachher?.(figur);
            }
            markDirty();
        } catch (fehler) {
            Protokoll.fehler('properties', 'Netz nicht neu ladbar', fehler);
        } finally {
            Figurneuladen._laeuft = false;
            Sanduhr.aus();
        }
    }
}
