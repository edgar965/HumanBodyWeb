/**
 * Scene Editor -- Scene save/load, file dialogs, gather/restore.
 */
import { THREE, TONE_MAPPINGS } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { getCSRFToken } from './utils.js';
import { markClean } from './undo.js';
import { _saveJsonWithPicker, importModelFromFilePicker, initCharacterDialog, initSceneDialogs, loadFromFilePicker, openAddCharacterDialog, openLoadDialog, openSaveDialog } from './szene_dialoge.js';

export function gatherSceneState() {
    const chars = [];
    state.characters.forEach(inst => chars.push(inst.toJSON()));
    return {
        version: 1,
        name: state.currentSceneName || 'Unnamed',
        characters: chars,
        lighting: {
            key: { intensity: state.keyLight.intensity, color: '#' + state.keyLight.color.getHexString(), pos: [state.keyLight.position.x, state.keyLight.position.y, state.keyLight.position.z] },
            fill: { intensity: state.fillLight.intensity, color: '#' + state.fillLight.color.getHexString(), pos: [state.fillLight.position.x, state.fillLight.position.y, state.fillLight.position.z] },
            back: { intensity: state.backLight.intensity, color: '#' + state.backLight.color.getHexString(), pos: [state.backLight.position.x, state.backLight.position.y, state.backLight.position.z] },
            ambient: { intensity: state.ambientLight.intensity, color: '#' + state.ambientLight.color.getHexString() }
        },
        renderer: {
            toneMapping: document.getElementById('tone-mapping').value,
            exposure: state.renderer.toneMappingExposure,
            background: '#' + state.scene.background.getHexString()
        },
        camera: {
            fov: state.camera.fov,
            position: state.camera.position.toArray(),
            target: state.controls.target.toArray()
        }
    };
}

export async function doSaveScene(name) {
    const data = gatherSceneState();
    data.name = name;
    try {
        const resp = await fetch('/api/character/scene/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ name, data }),
        });
        const result = await resp.json();
        if (result.ok) {
            state.currentSceneName = name;
            markClean();
            const dateiTitle = document.querySelector('.menu:first-child .menu-title');
            if (dateiTitle) {
                const orig = dateiTitle.textContent;
                dateiTitle.textContent = 'Gespeichert!';
                dateiTitle.style.color = 'var(--accent)';
                setTimeout(() => { dateiTitle.textContent = orig; dateiTitle.style.color = ''; }, 1500);
            }
        } else { alert('Fehler: ' + (result.error || 'Unbekannt')); }
    } catch (e) { alert('Fehler: ' + e.message); }
}

export async function loadSceneFromData(data, sceneName) {
    fn.clearAllCharacters();
    state.currentSceneName = sceneName || data.name || '';
    if (data.characters) {
        for (const charData of data.characters) {
            try {
                const inst = await fn.CharacterInstance.fromJSON(charData);
                state.characters.set(inst.id, inst);
                state.scene.add(inst.group);
            } catch (e) { console.error(`Failed to load character ${charData.presetName}:`, e); }
        }
    }
    if (data.lighting) {
        if (data.lighting.key) { state.keyLight.intensity = data.lighting.key.intensity; state.keyLight.color.set(data.lighting.key.color); state.keyLight.position.set(...data.lighting.key.pos); }
        if (data.lighting.fill) { state.fillLight.intensity = data.lighting.fill.intensity; state.fillLight.color.set(data.lighting.fill.color); state.fillLight.position.set(...data.lighting.fill.pos); }
        if (data.lighting.back) { state.backLight.intensity = data.lighting.back.intensity; state.backLight.color.set(data.lighting.back.color); state.backLight.position.set(...data.lighting.back.pos); }
        if (data.lighting.ambient) { state.ambientLight.intensity = data.lighting.ambient.intensity; state.ambientLight.color.set(data.lighting.ambient.color); }
    }
    if (data.renderer) {
        if (data.renderer.toneMapping && TONE_MAPPINGS[data.renderer.toneMapping] !== undefined) state.renderer.toneMapping = TONE_MAPPINGS[data.renderer.toneMapping];
        if (data.renderer.exposure !== undefined) state.renderer.toneMappingExposure = data.renderer.exposure;
        if (data.renderer.background) state.scene.background.set(data.renderer.background);
    }
    if (data.camera) {
        if (data.camera.fov) { state.camera.fov = data.camera.fov; state.camera.updateProjectionMatrix(); }
        if (data.camera.position) state.camera.position.fromArray(data.camera.position);
        if (data.camera.target) state.controls.target.fromArray(data.camera.target);
        state.controls.update();
    }
    fn.syncUIFromState();
    fn.updateCharacterListUI();
    fn.updateVertexCount();
    if (state.characters.size > 0 && !state.selectedCharacterId) {
        fn.selectCharacter(state.characters.keys().next().value);
    }
    fn.captureInitial?.();
}

export async function loadSceneFromServer(name) {
    const resp = await fetch(`/api/character/scene/${encodeURIComponent(name)}/`);
    if (!resp.ok) throw new Error('Scene not found');
    const data = await resp.json();
    await loadSceneFromData(data, name);
}

export async function loadModelFile(fileEntry) {
    if (fileEntry.type === 'scene') { await loadSceneFromServer(fileEntry.name); }
    else { fn.clearAllCharacters(); state.currentSceneName = ''; await fn.addCharacterFromPreset(fileEntry.name); }
}

export function newScene() {
    if (state.characters.size > 0) {
        if (!confirm('Aktuelle Szene verwerfen und neue Szene erstellen?')) return;
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
    if (state.currentSceneName) { doSaveScene(state.currentSceneName); }
    else { openSaveDialog(); }
}

export function resetScene() {
    if (!confirm('Szene komplett zur\u00fccksetzen? Alle \u00c4nderungen gehen verloren.')) return;
    fn.clearAllCharacters();
    state.currentSceneName = '';
    fn.resetLighting();
    fn.resetCamera();
    state.scene.background.set(0x1a1a2e);
    state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    fn.syncUIFromState();
    fn.loadDefaultCharacter();
    markClean();
}





export async function exportSceneJSON() {
    const data = gatherSceneState();
    await _saveJsonWithPicker(data, (state.currentSceneName || 'scene') + '.json');
}

export async function exportModelJSON() {
    if (!state.selectedCharacterId) { alert('Bitte zuerst einen Charakter ausw\u00e4hlen.'); return; }
    const inst = state.characters.get(state.selectedCharacterId);
    if (!inst) return;
    let data;
    if (inst.generatedConfig) {
        data = { ...inst.generatedConfig, type: 'generated_model', name: inst.presetName || 'Generiertes Modell', body_type: inst.generatedConfig.skeleton_type === 'rig' ? 'Rig Bones' : 'DEF Skeleton', skeleton_type: inst.generatedConfig.skeleton_type || 'def' };
    } else {
        data = { name: inst.presetName, body_type: inst.bodyType, morphs: inst.morphs || {}, meta: inst.meta || {}, cloth: inst.cloth || [], hair_style: inst.hairStyle || null, garments: inst.garments || [], mh_proxy: Object.values(inst.mhProxies || {}) };
    }
    const savedName = await _saveJsonWithPicker(data, (inst.presetName || 'model') + '.json');
    if (savedName) {
        const newName = savedName.replace(/\.json$/i, '');
        inst.presetName = newName;
        inst.presetKey = newName;
        fn.updateCharacterListUI?.();
    }
}







// Register
fn.gatherSceneState = gatherSceneState;
fn.doSaveScene = doSaveScene;
fn.loadSceneFromData = loadSceneFromData;
fn.loadSceneFromServer = loadSceneFromServer;
fn.loadModelFile = loadModelFile;
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
