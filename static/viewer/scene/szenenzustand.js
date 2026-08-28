import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { szenenteile } from './szenenteile.js';

/**
 * Szenenzustand — eine Szene einsammeln und wieder herstellen.
 *
 * Herausgelöst aus `save_load.js` (208 Zeilen). Die zwei Richtungen gehören
 * zusammen und müssen zueinander passen: Was `einsammeln()` schreibt, muss
 * `herstellen()` lesen können. Standen sie in einer Datei zwischen Dialogen und
 * Menübefehlen, war das leicht zu übersehen.
 *
 * DIE VIER LICHTER STANDEN VIERMAL DA
 * ===================================
 * Key, Fill, Back und Ambient wurden je einzeln ausgeschrieben — beim Einsammeln
 * und beim Herstellen, also achtmal fast derselbe Block. Jetzt steht die Zuordnung
 * einmal als Tabelle (`LICHTER`). Ambient hat keine Position; das ist der einzige
 * Unterschied und steht als Feld in der Tabelle.
 *
 * WAS BEIM HERSTELLEN NICHT PASSIEREN DARF
 * ========================================
 * Ein Charakter, der nicht lädt, darf die übrigen nicht mitnehmen — deshalb wird
 * je Charakter gefangen und protokolliert. Eine Szene mit drei von vier Figuren
 * ist brauchbar, eine Fehlerseite nicht.
 */
export class Szenenzustand {

    /** Format-Version der gespeicherten Szene. */
    static VERSION = 1;

    /** Lichtname in der Datei -> Feld im Zustand (+ hat es eine Position?). */
    static LICHTER = [
        { schluessel: 'key', feld: 'keyLight', mitOrt: true },
        { schluessel: 'fill', feld: 'fillLight', mitOrt: true },
        { schluessel: 'back', feld: 'backLight', mitOrt: true },
        { schluessel: 'ambient', feld: 'ambientLight', mitOrt: false },
    ];

    // ------------------------------------------------------------- Einsammeln

    /** Die ganze Szene als JSON-taugliches Objekt. */
    static einsammeln() {
        const figuren = [];
        state.characters.forEach(figur => figuren.push(figur.toJSON()));
        return {
            version: Szenenzustand.VERSION,
            name: state.currentSceneName || 'Unnamed',
            characters: figuren,
            lighting: Szenenzustand._lichter(),
            renderer: {
                toneMapping: document.getElementById('tone-mapping').value,
                exposure: state.renderer.toneMappingExposure,
                background: '#' + state.scene.background.getHexString(),
            },
            camera: {
                fov: state.camera.fov,
                position: state.camera.position.toArray(),
                target: state.controls.target.toArray(),
            },
        };
    }

    static _lichter() {
        const werte = {};
        for (const { schluessel, feld, mitOrt } of Szenenzustand.LICHTER) {
            const licht = state[feld];
            werte[schluessel] = {
                intensity: licht.intensity,
                color: '#' + licht.color.getHexString(),
            };
            if (mitOrt) {
                werte[schluessel].pos = [licht.position.x, licht.position.y,
                                         licht.position.z];
            }
        }
        return werte;
    }

    // -------------------------------------------------------------- Herstellen

    /** Eine gespeicherte Szene übernehmen. */
    static async herstellen(daten, szenenname) {
        fn.clearAllCharacters();
        state.currentSceneName = szenenname || daten.name || '';
        await Szenenzustand._figuren(daten.characters);
        Szenenzustand._uebernehmen(daten);
        Szenenzustand._oberflaeche();
    }

    static async _figuren(figuren) {
        if (!figuren) return;
        for (const daten of figuren) {
            try {
                const figur = await fn.CharacterInstance.fromJSON(daten);
                state.characters.set(figur.id, figur);
                state.scene.add(figur.group);
            } catch (fehler) {
                // Eine Figur, die nicht laedt, darf die anderen nicht mitnehmen.
                Protokoll.fehler('Szene',
                                 `Charakter ${daten.presetName} nicht geladen`,
                                 fehler);
            }
        }
    }

    /**
     * Licht, Bild und Kamera einer gespeicherten Szene setzen.
     *
     * Die Rechnung steht in `gemeinsam/szeneneinstellungen.js` (Umbau
     * 28.08.2026, Befund `doppelcode`): Sie stand hier, in `session.js`, in
     * `lighting.js` und in drei Betrachter-Modulen — sechsmal dasselbe, nur
     * mit anderer Herkunft der Teile. Die Herkunft steht jetzt hier, die
     * Rechnung dort.
     */
    static _uebernehmen(daten) {
        szenenteile('Szenenzustand').uebernehmen(daten);
    }

    static _oberflaeche() {
        fn.syncUIFromState();
        fn.updateCharacterListUI();
        fn.updateVertexCount();
        if (state.characters.size > 0 && !state.selectedCharacterId) {
            fn.selectCharacter(state.characters.keys().next().value);
        }
        fn.captureInitial?.();
    }

    // ------------------------------------------------------------ Zurücksetzen

    /** Alles auf Anfang — Lichter, Kamera, Hintergrund, Grundfigur. */
    static zuruecksetzen() {
        fn.clearAllCharacters();
        state.currentSceneName = '';
        fn.resetLighting();
        fn.resetCamera();
        state.scene.background.set(0x1a1a2e);
        state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        fn.syncUIFromState();
        fn.loadDefaultCharacter();
    }
}
