import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _saveJsonWithPicker } from './szene_dialoge.js';
import { Szenenzustand } from './szenenzustand.js';
import { GarmentcodeAblage } from './garmentcode_ablage.js';
import { Koerperdetails } from '../gemeinsam/koerperdetails.js';
import { Garderobenstand } from './garderobenstand.js';

/**
 * Szenenausgabe — Szene oder Figur als JSON-Datei schreiben.
 *
 * Herausgelöst aus `save_load.js` (208 Zeilen).
 *
 * ZWEI FORMEN EINER FIGUR
 * =======================
 * * **Erzeugt** (`generatedConfig`): Die Figur kam aus dem Modellbauer; ihre
 *   Beschreibung IST die Konfiguration. Sie wird durchgereicht und nur um
 *   Anzeigefelder ergänzt.
 * * **Zusammengestellt**: Körpertyp, Morphwerte, Kleidung, Haare, Zubehör.
 *
 * Beim Speichern über den Dateidialog kann der Nutzer den Namen ändern. Der neue
 * Name wird zurück in die Figur geschrieben — sonst zeigt die Liste weiter den
 * alten, und das nächste Speichern legt eine zweite Datei an.
 */
export class Szenenausgabe {

    /** Die ganze Szene als `<name>.json`. */
    static async szene() {
        const daten = Szenenzustand.einsammeln();
        await _saveJsonWithPicker(daten,
                                  (state.currentSceneName || 'scene') + '.json');
    }

    /** Die ausgewählte Figur als `<name>.json`. */
    static async figur() {
        if (!state.selectedCharacterId) {
            alert('Bitte zuerst einen Charakter auswählen.');
            return;
        }
        const figur = state.characters.get(state.selectedCharacterId);
        if (!figur) return;
        const daten = Szenenausgabe.modelldaten(figur);
        const name = await _saveJsonWithPicker(
            daten, (figur.presetName || 'model') + '.json');
        if (name) Szenenausgabe._umbenennen(figur, name);
    }

    /**
     * Die Beschreibung EINER Figur — fuer Datei und Server gleich.
     *
     * Herausgezogen am 08.09.2026, als „Modell speichern" in den
     * Serverkatalog dazukam (`Speichernmenue`). Zwei Fassungen dieser
     * Fallunterscheidung hiessen: Wer eine Datei speichert, bekommt etwas
     * anderes als wer in den Katalog speichert — und niemand sieht, welche.
     */
    static modelldaten(figur) {
        const daten = figur.generatedConfig
            ? Szenenausgabe._erzeugt(figur)
            : Szenenausgabe._zusammengestellt(figur);
        // HIER und nicht in einem der beiden Zweige: Eine erzeugte Figur
        // kann genauso ein GarmentCode-Stueck tragen (08.09.2026: „habe
        // gerade das Modell gespeichert mit GarmentCode, neu laden
        // funktioniert nicht").
        daten[GarmentcodeAblage.FELD] = GarmentcodeAblage.toJSON(figur);
        if (figur.details) daten[Koerperdetails.FELD] = { ...figur.details };
        return daten;
    }

    static _erzeugt(figur) {
        const bauart = figur.generatedConfig.skeleton_type === 'rig'
            ? 'Rig Bones' : 'DEF Skeleton';
        return {
            ...figur.generatedConfig,
            type: 'generated_model',
            name: figur.presetName || 'Generiertes Modell',
            body_type: bauart,
            skeleton_type: figur.generatedConfig.skeleton_type || 'def',
        };
    }

    static _zusammengestellt(figur) {
        return {
            name: figur.presetName,
            body_type: figur.bodyType,
            morphs: figur.morphs || {},
            meta: figur.meta || {},
            cloth: figur.cloth || [],
            hair_style: figur.hairStyle || null,
            garments: Garderobenstand.liste(figur),
            mh_proxy: Object.values(figur.mhProxies || {}),
        };
    }

    static _umbenennen(figur, dateiname) {
        const name = dateiname.replace(/\.json$/i, '');
        figur.presetName = name;
        figur.presetKey = name;
        fn.updateCharacterListUI?.();
    }
}
