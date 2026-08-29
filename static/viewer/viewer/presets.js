/**
 * Viewer — Model Presets (load/save dialogs, apply preset, gather state).
 *
 * UMBAU 18.08.2026: 352 Zeilen, darin 3.000 Zeichen CSS als Zeichenkette. Jetzt:
 *
 *     modellvorgabe.js   eine Vorgabe auf die Seite legen
 *     modellzustand.js   den Stand der Seite einsammeln und speichern
 *     modelldialog.js    „Laden" / „Speichern unter" (Stile: css/modelldialog.css)
 *     metawerte.js       Alter/Masse/Tonus/Größe umrechnen (war 4× kopiert)
 *
 * Hier bleibt der Seitenaufbau: die drei Knöpfe und die Startvorgabe.
 */
import { state } from './state.js';
import { Knopfmeldung } from '../gemeinsam/knopfmeldung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Modelldialog } from './modelldialog.js';
import { Modellvorgabe } from './modellvorgabe.js';
import { Modellzustand } from './modellzustand.js';
import { Startvorgabe } from './startvorgabe.js';

export function applyModelPreset(preset) {
    Modellvorgabe.anwenden(preset);
}

export function gatherModelState() {
    return Modellzustand.einsammeln();
}

export function initLoadPreset() {
    const knopf = document.getElementById('load-preset-btn');
    if (!knopf) return;
    knopf.addEventListener('click', async () => {
        const name = await Modelldialog.laden();
        if (!name) return;
        try {
            const vorgabe = await Serverabruf.json(
                `/api/character/model/${encodeURIComponent(name)}/`);
            applyModelPreset(vorgabe);
            state.currentPresetName = vorgabe.name || name;
            Knopfmeldung.fertig(knopf, 'Geladen!');
        } catch (fehler) {
            Protokoll.fehler('presets', 'Vorgabe nicht ladbar', fehler);
            alert('Fehler beim Laden: ' + fehler.message);
        }
    });
    new Startvorgabe().laden();
}

export function initSaveButtons() {
    _speicherknopf('save-model-btn', true);
    _speicherknopf('save-model-as-btn', false);
}

/**
 * „Speichern" nimmt den bekannten Namen, „Speichern unter" fragt immer.
 *
 * Beim ersten Mal hat auch „Speichern" keinen Namen — dann fragt es ebenfalls.
 */
function _speicherknopf(kennung, nameBehalten) {
    const knopf = document.getElementById(kennung);
    if (!knopf) return;
    knopf.addEventListener('click', async () => {
        let name = nameBehalten ? state.currentPresetName : '';
        if (!name) name = await Modelldialog.speichern();
        if (!name) return;
        if (await Modellzustand.speichern(name)) Knopfmeldung.fertig(knopf);
    });
}

