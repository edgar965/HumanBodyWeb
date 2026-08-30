/**
 * Scene Editor -- sessionStorage persistence.
 */
import { state, SESSION_KEY } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { szenenteile } from './szenenteile.js';
import { Szenenzustand } from './szenenzustand.js';

// =========================================================================
// Save session state to sessionStorage
// =========================================================================
export function saveSessionState() {
    try {
        if (!fn.gatherSceneState) return;
        const sceneData = fn.gatherSceneState();
        sceneData._defaultPresetSnapshot = state.defaultPresetName;
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(sceneData));
    } catch (e) {
        Protokoll.warnung('session', 'Failed to save session state:', e);
    }
}

// =========================================================================
// Restore session state from sessionStorage
// =========================================================================
export async function restoreSessionState() {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return false;
    try {
        const data = JSON.parse(raw);
        sessionStorage.removeItem(SESSION_KEY);

        if (data._defaultPresetSnapshot && data._defaultPresetSnapshot !== state.defaultPresetName) {
            Protokoll.debug('Scene', 'Default model changed from', data._defaultPresetSnapshot, 'to',
                state.defaultPresetName, '— discarding session.');
            return false;
        }

        // Restore characters
        if (data.characters && data.characters.length > 0) {
            fn.clearAllCharacters();
            for (const charData of data.characters) {
                try {
                    const CharacterInstance = fn.CharacterInstance;
                    const inst = await CharacterInstance.fromJSON(charData);
                    state.characters.set(inst.id, inst);
                    state.scene.add(inst.group);
                } catch (e) {
                    console.error(`Failed to restore character ${charData.presetName}:`, e);
                }
            }
        }

        // Licht, Bild und Kamera: dieselbe Rechnung wie beim Laden einer
        // Szene und beim localStorage-Eintrag — sie steht in
        // `gemeinsam/szeneneinstellungen.js` (Umbau 28.08.2026, `doppelcode`).
        szenenteile('session').uebernehmen(data);

        Szenenzustand.oberflaecheAngleichen();
        return true;
    } catch (e) {
        console.error('Failed to restore session state:', e);
        return false;
    }
}

// Register
fn.saveSessionState = saveSessionState;
fn.restoreSessionState = restoreSessionState;
