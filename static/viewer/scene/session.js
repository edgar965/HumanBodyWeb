/**
 * Scene Editor -- sessionStorage persistence.
 */
import { state, SESSION_KEY } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Startmessung } from '../gemeinsam/startmessung.js';
import { szenenteile } from './szenenteile.js';
import { Szenenzustand } from './szenenzustand.js';
import { Figurarten } from './figurarten.js';

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
                    // Welche Klasse zu `quelle` gehört, steht in
                    // `figurarten.js`: Eine UMA-Figur lädt ihre GLB, kein
                    // HumanBody-Netz — sonst fragte `CharacterInstance` den
                    // Server nach dem Körpertyp „UMA" und bekam eine 500.
                    // Jede Figur kommt auf die Buehne, sobald ihr Koerper
                    // steht — nicht erst, wenn auch Haare und Kleidung da
                    // sind. Bei mehreren Figuren zaehlt das doppelt: Sie
                    // werden nacheinander wiederhergestellt, und vorher
                    // wartete die erste auf ihr eigenes Zubehoer, bevor die
                    // zweite ueberhaupt begann.
                    // Beim zweiten Aufruf (dem Sicherheitsnetz unten)
                    // passiert nichts mehr — sonst stuende die Marke
                    // zweimal im Bericht und man wuesste nicht, welche
                    // gilt.
                    const zeigen = (fertig) => {
                        if (state.characters.has(fertig.id)) return;
                        state.characters.set(fertig.id, fertig);
                        state.scene.add(fertig.group);
                        Startmessung.eintragen('== FIGUR SICHTBAR ==',
                                               performance.now());
                    };
                    const inst = await Figurarten.ausJSON(charData, zeigen);
                    // Auch fuer die Figurarten, die den Rueckruf nicht
                    // kennen; Map und Gruppe nehmen denselben Eintrag nur
                    // einmal.
                    zeigen(inst);
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
