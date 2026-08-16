/**
 * Modellspeicher — das erzeugte Modell als Datei und im Servermodellordner
 * ablegen.
 *
 * Aus modellgenerator_ui.js herausgeloest (Umbau 16.08.2026). Dort standen zwei
 * Funktionen, `_mgSaveModel` und `_mgSaveModelToServer`, mit demselben
 * Nachzieh-Block (13 Zeilen, bis auf eine Konsolenausgabe buchstabengleich) und
 * demselben Aufbau der Daten. `_mgSaveModel` wurde von keinem Knopf und keinem
 * Modul aufgerufen — nur `_mgSaveModelToServer` haengt an "Speichern unter…" —
 * und ist ersatzlos entfallen.
 */
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { _selectedInst, getCSRFToken } from '../utils.js';
import { Modellbauzustand } from './zustand.js';

export class Modellspeicher {
    /**
     * Fehlende Konfiguration aus einem geladenen Charakter nachziehen.
     *
     * Noetig, wenn der Benutzer eine Szene laedt und direkt speichert, ohne den
     * Modell-Reiter geoeffnet zu haben.
     */
    static _konfigNachziehen() {
        if (Modellbauzustand.konfig) return true;
        let inst = _selectedInst();
        if (!inst?.generatedConfig) {
            inst = [...state.characters.values()].find(c => c.generatedConfig) || null;
        }
        if (!inst?.generatedConfig) return false;
        Modellbauzustand.ausCharakter(inst);
        console.log('[MG] Synced config from character:', inst.presetName);
        return true;
    }

    /** Modell als Charaktervorlage aufbereiten. */
    static _daten() {
        return {
            ...Modellbauzustand.konfig,
            type: 'generated_model',
            name: Modellbauzustand.konfig.name || 'Generiertes Modell',
            body_type: Modellbauzustand.skelettart === 'rig' ? 'Rig Bones'
                                                             : 'DEF Skeleton',
            skeleton_type: Modellbauzustand.skelettart,
        };
    }

    /** Datei schreiben und dieselbe Fassung im Servermodellordner ablegen. */
    static async speichern() {
        if (!Modellspeicher._konfigNachziehen()) {
            alert('Kein Modell vorhanden.');
            return;
        }
        const daten = Modellspeicher._daten();
        const inst = Modellbauzustand.charakterId
            ? state.characters.get(Modellbauzustand.charakterId) : null;
        const vorschlag = (inst?.presetKey || state.defaultPresetName
                           || Modellbauzustand.konfig.name || 'Neues Modell') + '.json';
        const gewaehlt = await fn._saveJsonWithPicker(daten, vorschlag);
        if (!gewaehlt) return;                       // Dialog abgebrochen

        // Zusaetzlich in den Servermodellordner, damit Theatre und die anderen
        // Seiten das Modell sehen.
        const name = gewaehlt.replace(/\.json$/i, '');
        try {
            await fetch('/api/character/model/save/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json',
                           'X-CSRFToken': getCSRFToken() },
                body: JSON.stringify({ name, data: daten }),
            });
            const ci = Modellbauzustand.charakterId
                ? state.characters.get(Modellbauzustand.charakterId) : null;
            if (ci) {
                ci.generatedConfig = JSON.parse(JSON.stringify(daten));
                ci.presetKey = name;
            }
            console.log(`[MG] Model saved as "${name}" (file + server)`);
        } catch (e) {
            console.warn('[MG] Server save failed:', e);
        }
    }
}
