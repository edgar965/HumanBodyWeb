/**
 * Scene Editor -- Scene save/load, file dialogs, gather/restore.
 *
 * UMBAU 17.08.2026: 208 Zeilen mit drei Themen. Jetzt:
 *
 *     szenenzustand.js   einsammeln / herstellen / zurücksetzen
 *     szenenausgabe.js   Szene oder Figur als JSON-Datei schreiben
 *
 * Hier bleiben die Befehle, die das Menü auslöst (speichern, neu, schnell
 * speichern, laden) und die Registrierung — die Menüleiste und die Dialoge rufen
 * die Namen über `fn`.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { markClean } from './undo.js';
import { _saveJsonWithPicker, importModelFromFilePicker, initCharacterDialog,
         initSceneDialogs, loadFromFilePicker, openAddCharacterDialog,
         openLoadDialog, openSaveDialog } from './szene_dialoge.js';
import { Knopfmeldung } from '../gemeinsam/knopfmeldung.js';
import { Szenenausgabe } from './szenenausgabe.js';
import { Szenenzustand } from './szenenzustand.js';

export function gatherSceneState() { return Szenenzustand.einsammeln(); }

export async function doSaveScene(name) {
    const daten = Szenenzustand.einsammeln();
    daten.name = name;
    try {
        const ergebnis = await Serverabruf.senden('/api/character/scene/save/',
                                                 { name, data: daten });
        if (!ergebnis.ok) {
            alert('Fehler: ' + (ergebnis.error || 'Unbekannt'));
            return;
        }
        state.currentSceneName = name;
        markClean();
        const titel = document.querySelector('.menu:first-child .menu-title');
        if (titel) {
            // `Knopfmeldung` setzt Text und Farbe und nimmt beides zurueck —
            // hier auf dem Menütitel statt auf einem Knopf.
            Knopfmeldung.zeigen(titel, 'Gespeichert!',
                                { symbol: null, farbe: 'var(--accent)' });
        }
    } catch (fehler) {
        alert('Fehler: ' + fehler.message);
    }
}

export async function loadSceneFromData(data, sceneName) {
    return Szenenzustand.herstellen(data, sceneName);
}

export async function loadSceneFromServer(name) {
    const daten = await Serverabruf.json(
        `/api/character/scene/${encodeURIComponent(name)}/`);
    await Szenenzustand.herstellen(daten, name);
}

export async function loadModelFile(fileEntry) {
    if (fileEntry.type === 'scene') {
        await loadSceneFromServer(fileEntry.name);
        return;
    }
    fn.clearAllCharacters();
    state.currentSceneName = '';
    await fn.addCharacterFromPreset(fileEntry.name);
}

export function newScene() {
    if (state.characters.size > 0
            && !confirm('Aktuelle Szene verwerfen und neue Szene erstellen?')) {
        return;
    }
    fn.clearAllCharacters();
    state.currentSceneName = '';
    fn.loadDefaultCharacter();
    // Eine neue Szene ist nicht „geändert" (Review 15.08.2026): `resetScene()`
    // ruft `markClean()`, `newScene()` tat es nicht. Folge: Der Änderungsstatus
    // und der Rückgängig-Stapel der VERWORFENEN Szene liefen weiter — die
    // Abfrage „ungespeicherte Änderungen" kam sofort nach dem Anlegen, und ein
    // Rückgängig griff in die alte Szene.
    markClean();
}

export function quickSave() {
    if (state.currentSceneName) doSaveScene(state.currentSceneName);
    else openSaveDialog();
}

export function resetScene() {
    if (!confirm('Szene komplett zurücksetzen? Alle Änderungen gehen verloren.')) {
        return;
    }
    Szenenzustand.zuruecksetzen();
    markClean();
}

export async function exportSceneJSON() { return Szenenausgabe.szene(); }
export async function exportModelJSON() { return Szenenausgabe.figur(); }

// Register
fn.gatherSceneState = gatherSceneState;
fn.loadSceneFromData = loadSceneFromData;
fn.newScene = newScene;
fn.quickSave = quickSave;
fn.resetScene = resetScene;
fn.loadFromFilePicker = loadFromFilePicker;
fn.importModelFromFilePicker = importModelFromFilePicker;
fn.exportSceneJSON = exportSceneJSON;
fn.exportModelJSON = exportModelJSON;
fn._saveJsonWithPicker = _saveJsonWithPicker;
fn.initCharacterDialog = initCharacterDialog;
fn.openAddCharacterDialog = openAddCharacterDialog;
fn.initSceneDialogs = initSceneDialogs;
fn.openSaveDialog = openSaveDialog;
fn.openLoadDialog = openLoadDialog;
