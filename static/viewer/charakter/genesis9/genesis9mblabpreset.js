import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';

/**
 * Genesis9mblabpreset — die Auswahl „Preset“ oben im Abschnitt „HumanBody (MB-Lab)“ der Genesis-Regler (23.11.2026).
 *
 * MB-Labs Körpertypen und Phänotypen standen bis 23.11.2026 als 112 Einträge im Katalog „Charakter hinzufügen“; Edgar: „diese MBLab kann man doch aus den Haupttypen per
 * Toolbar auch erzeugen … dann entferne sie“. Bei der HumanBody-Figur gibt es dafür die Auswahl „Preset“ unter „Body Type“ (`properties.js`, `populatePresets`): sie setzt
 * die Morphs der Vorlage, der Körpertyp bleibt. Hier dasselbe für Genesis: die `hb:`-Regler der Vorlage (`G9mblabvorlagen`, Server `G9reglerapi.mblab_vorlagen`), die
 * Grundfigur und alle anderen Regler bleiben. Die Liste kommt erst beim ersten Öffnen der Auswahl (der Reglerplan jeder Ladung bleibt so klein wie vorher).
 */
export class Genesis9mblabpreset {

    static ABSCHNITT = 'herkunft_hb';
    static ADRESSE = '/api/character/genesis9-figur/mblab-vorlagen/';
    static _vorlagen = null;

    /** Für `Genesis9reglerliste.fuellen` (`anhaengen`): nur am Abschnitt HumanBody. `nachher` zieht nach dem Lauf Kopf und Schieber nach. */
    static anhaengen(kasten, bereich, inst, nachher) {
        if (bereich?.schluessel !== Genesis9mblabpreset.ABSCHNITT) return;
        const zeile = document.createElement('div');
        zeile.className = 'prop-row g9-mblabpreset';
        zeile.innerHTML = `
            <label title="MB-Labs Körpertypen und Phänotypen: setzt die HB-Regler der Vorlage, Grundfigur und übrige Regler bleiben">Preset</label>
            <select class="viewer-select hb-dehnt"><option value="">— MB-Lab-Vorlage wählen —</option></select>`;
        const feld = zeile.querySelector('select');
        const fuellen = () => Genesis9mblabpreset._fuellen(feld);
        feld.addEventListener('focus', fuellen, { once: true });
        feld.addEventListener('pointerdown', fuellen, { once: true });
        feld.addEventListener('change', () => Genesis9mblabpreset._anwenden(feld, inst, nachher));
        kasten.querySelector('summary')?.after(zeile);
    }

    static async _fuellen(feld) {
        if (feld.dataset.gefuellt) return;
        feld.dataset.gefuellt = '1';
        try {
            Genesis9mblabpreset._vorlagen ??= (await Serverabruf.json(Genesis9mblabpreset.ADRESSE)).vorlagen || [];
        } catch (fehler) {
            delete feld.dataset.gefuellt;
            feld.options[0].textContent = `Vorlagen nicht geladen: ${fehler.message}`;
            return;
        }
        const gruppen = new Map();
        for (const v of Genesis9mblabpreset._vorlagen) {
            if (!gruppen.has(v.gruppe)) gruppen.set(v.gruppe, []);
            gruppen.get(v.gruppe).push(v);
        }
        // Gruppen und Einträge stellt `Combosortierung` alphabetisch (Edgar, 10.10.2026: alle Combo-Boxen alphabetisch)
        feld.insertAdjacentHTML('beforeend', [...gruppen].map(([gruppe, liste]) => `<optgroup label="${escapeHtml(gruppe)}">${
            liste.map(v => `<option value="${escapeHtml(v.name)}">${escapeHtml(v.titel)}</option>`).join('')}</optgroup>`).join(''));
    }

    static _anwenden(feld, inst, nachher) {
        const v = (Genesis9mblabpreset._vorlagen || []).find(x => x.name === feld.value);
        if (!v || !inst) return;
        Genesis9lauf.planen(inst, () => {
            inst.regler = inst.regler || {};
            for (const [name, wert] of Object.entries(v.regler)) {
                if (Math.abs(wert) < 1e-6) delete inst.regler[name];
                else inst.regler[name] = wert;
            }
            return inst.neuFormen();
        }, nachher, 'regler:mblab-preset');
        markDirty();
    }
}
