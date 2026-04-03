/**
 * Scene Editor -- Scene save/load, file dialogs, gather/restore.
 */
import { THREE, TONE_MAPPINGS, SESSION_KEY } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { escapeHtml, generateCharacterId, getCSRFToken, openDialog, closeDialog } from './utils.js';
import { markDirty, markClean } from './undo.js';

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

// File picker helpers
async function _openJsonFilePicker() {
    if (window.showOpenFilePicker) {
        try {
            const [handle] = await window.showOpenFilePicker({ types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }], multiple: false });
            const file = await handle.getFile();
            return JSON.parse(await file.text());
        } catch (e) { if (e.name === 'AbortError') return null; throw e; }
    }
    return new Promise((resolve) => {
        const input = document.createElement('input');
        input.type = 'file'; input.accept = '.json,application/json'; input.style.display = 'none';
        input.addEventListener('change', async () => {
            const file = input.files[0];
            if (!file) { resolve(null); return; }
            try { resolve(JSON.parse(await file.text())); } catch (e) { alert('Fehler: ' + e.message); resolve(null); }
            input.remove();
        });
        input.addEventListener('cancel', () => { resolve(null); input.remove(); });
        document.body.appendChild(input); input.click();
    });
}

export async function _saveJsonWithPicker(jsonData, defaultName) {
    const content = JSON.stringify(jsonData, null, 2);
    if (window.showSaveFilePicker) {
        try {
            const handle = await window.showSaveFilePicker({ suggestedName: defaultName, types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }] });
            const writable = await handle.createWritable();
            await writable.write(content); await writable.close();
            return handle.name;
        } catch (e) { if (e.name === 'AbortError') return null; }
    }
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = defaultName; a.click();
    URL.revokeObjectURL(url);
    return defaultName;
}

export async function loadFromFilePicker() {
    try {
        const data = await _openJsonFilePicker();
        if (!data) return;
        if (data.characters || data.lighting || data.version) {
            await loadSceneFromData(data, data.name || '');
        } else if (data.body_type) {
            fn.clearAllCharacters(); state.currentSceneName = '';
            const id = generateCharacterId();
            const inst = new fn.CharacterInstance(id, data);
            await inst.load();
            state.characters.set(id, inst); state.scene.add(inst.group);
            fn.updateCharacterListUI(); fn.updateVertexCount(); fn.selectCharacter(id);
        } else { alert('Unbekanntes JSON-Format.'); }
    } catch (e) { alert(`Fehler beim Laden: ${e.message}`); }
}

export async function importModelFromFilePicker() {
    try {
        const data = await _openJsonFilePicker();
        if (!data) return;
        if (!data.body_type) { alert('Ung\u00fcltiges Modell-JSON.'); return; }
        const id = generateCharacterId();
        const inst = new fn.CharacterInstance(id, data);
        inst.group.position.set(state.characters.size * 0.8, 0, 0);
        await inst.load();
        state.characters.set(id, inst); state.scene.add(inst.group);
        fn.updateCharacterListUI(); fn.updateVertexCount(); fn.selectCharacter(id); markDirty();
    } catch (e) { alert(`Fehler: ${e.message}`); }
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
        data = { name: inst.presetName, body_type: inst.bodyType, morphs: inst.morphs || {}, meta: inst.meta || {}, cloth: inst.cloth || [], hair_style: inst.hairStyle || null, garments: inst.garments || [] };
    }
    await _saveJsonWithPicker(data, (inst.presetName || 'model') + '.json');
}

// Scene dialogs
export function initCharacterDialog() {
    const addBtn = document.getElementById('add-character-btn');
    const dialog = document.getElementById('add-char-dialog');
    const confirmBtn = document.getElementById('add-char-confirm');
    addBtn.addEventListener('click', () => openAddCharacterDialog());
    confirmBtn.addEventListener('click', async () => {
        if (!state._addCharSelectedPreset) return;
        closeDialog(dialog);
        try { await fn.addCharacterFromPreset(state._addCharSelectedPreset); } catch (e) { alert(`Fehler: ${e.message}`); }
    });
}

export async function openAddCharacterDialog() {
    const dialog = document.getElementById('add-char-dialog');
    const confirmBtn = document.getElementById('add-char-confirm');
    const presetList = document.getElementById('preset-list');
    openDialog(dialog);
    state._addCharSelectedPreset = null;
    confirmBtn.disabled = true;
    presetList.innerHTML = '<li style="color:var(--text-muted)"><i class="fas fa-spinner fa-spin"></i> Lade Presets...</li>';
    try {
        const resp = await fetch('/api/character/models/');
        const data = await resp.json();
        presetList.innerHTML = '';
        if (!data.presets || data.presets.length === 0) { presetList.innerHTML = '<li style="color:var(--text-muted)">Keine Presets vorhanden.</li>'; return; }
        for (const p of data.presets) {
            const li = document.createElement('li'); li.textContent = p.label || p.name; li.dataset.presetName = p.name;
            li.addEventListener('click', () => { presetList.querySelectorAll('li').forEach(x => x.classList.remove('selected')); li.classList.add('selected'); state._addCharSelectedPreset = p.name; confirmBtn.disabled = false; });
            li.addEventListener('dblclick', async () => { state._addCharSelectedPreset = p.name; closeDialog(dialog); try { await fn.addCharacterFromPreset(p.name); } catch (e) { alert(`Fehler: ${e.message}`); } });
            presetList.appendChild(li);
        }
    } catch (e) { presetList.innerHTML = `<li style="color:#ef4444">Fehler: ${e.message}</li>`; }
}

export function initSceneDialogs() {
    const saveDialog = document.getElementById('save-scene-dialog');
    const saveNameInput = document.getElementById('save-scene-name');
    const saveConfirm = document.getElementById('save-scene-confirm');
    saveConfirm.addEventListener('click', async () => { const name = saveNameInput.value.trim(); if (!name) { saveNameInput.focus(); return; } closeDialog(saveDialog); await doSaveScene(name); });
    saveNameInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') saveConfirm.click(); });
    const loadDialog = document.getElementById('load-scene-dialog');
    const loadConfirm = document.getElementById('load-scene-confirm');
    loadConfirm.addEventListener('click', async () => { if (!state._selectedFileToLoad) return; closeDialog(loadDialog); try { await loadModelFile(state._selectedFileToLoad); } catch (e) { alert(`Fehler: ${e.message}`); } });
}

export async function openSaveDialog() {
    const saveDialog = document.getElementById('save-scene-dialog');
    const saveNameInput = document.getElementById('save-scene-name');
    const saveList = document.getElementById('save-scene-list');
    openDialog(saveDialog);
    saveNameInput.value = state.currentSceneName || '';
    saveNameInput.focus();
    await loadSceneListInto(saveList, (name) => { saveNameInput.value = name; });
}

export async function openLoadDialog() {
    const loadDialog = document.getElementById('load-scene-dialog');
    const loadConfirm = document.getElementById('load-scene-confirm');
    const tbody = document.getElementById('load-file-tbody');
    openDialog(loadDialog);
    state._selectedFileToLoad = null;
    loadConfirm.disabled = true;
    tbody.innerHTML = '<tr><td colspan="3" style="padding:12px;color:var(--text-muted);text-align:center;"><i class="fas fa-spinner fa-spin"></i> Lade...</td></tr>';
    try {
        const resp = await fetch('/api/character/model-files/');
        const data = await resp.json();
        tbody.innerHTML = '';
        const files = data.files || [];
        if (files.length === 0) { tbody.innerHTML = '<tr><td colspan="3" style="padding:12px;color:var(--text-muted);text-align:center;">Keine Dateien.</td></tr>'; return; }
        for (const f of files) {
            const tr = document.createElement('tr');
            const isScene = f.type === 'scene';
            const icon = isScene ? 'fa-film' : 'fa-user';
            const typeBadge = isScene ? '<span class="file-type-scene">Szene</span>' : '<span class="file-type-model">Modell</span>';
            const dateStr = f.modified ? new Date(f.modified * 1000).toLocaleDateString('de-DE') : '';
            tr.innerHTML = `<td style="padding:4px 12px;"><i class="fas ${icon}" style="margin-right:6px;opacity:0.5;"></i>${escapeHtml(f.label || f.name)}</td><td style="padding:4px 12px;text-align:center;">${typeBadge}</td><td style="padding:4px 12px;text-align:right;color:var(--text-muted);font-size:0.7rem;">${dateStr}</td>`;
            tr.style.cursor = 'pointer';
            tr.addEventListener('click', () => { tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected')); tr.classList.add('selected'); state._selectedFileToLoad = f; loadConfirm.disabled = false; });
            tr.addEventListener('dblclick', () => { state._selectedFileToLoad = f; closeDialog(loadDialog); loadModelFile(f).catch(e => alert(`Fehler: ${e.message}`)); });
            tbody.appendChild(tr);
        }
    } catch (e) { tbody.innerHTML = `<tr><td colspan="3" style="padding:12px;color:#ef4444;text-align:center;">Fehler: ${e.message}</td></tr>`; }
}

async function loadSceneListInto(listEl, onSelect) {
    listEl.innerHTML = '<li style="color:var(--text-muted)"><i class="fas fa-spinner fa-spin"></i> Lade...</li>';
    try {
        const resp = await fetch('/api/character/scenes/');
        const data = await resp.json();
        listEl.innerHTML = '';
        if (!data.scenes || data.scenes.length === 0) { listEl.innerHTML = '<li style="color:var(--text-muted)">Keine Szenen.</li>'; return; }
        for (const s of data.scenes) {
            const li = document.createElement('li');
            li.innerHTML = `${escapeHtml(s.label || s.name)} <span class="preset-sub">${s.character_count} Charakter(e)</span>`;
            li.addEventListener('click', () => { listEl.querySelectorAll('li').forEach(x => x.classList.remove('selected')); li.classList.add('selected'); onSelect(s.name); });
            listEl.appendChild(li);
        }
    } catch (e) { listEl.innerHTML = `<li style="color:#ef4444">Fehler: ${e.message}</li>`; }
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
