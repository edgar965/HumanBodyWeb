import { closeDialog, escapeHtml, generateCharacterId, openDialog } from './utils.js';
import { doSaveScene, loadModelFile, loadSceneFromData } from './save_load.js';
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';
import { markDirty } from './undo.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
/**
 * Die Dialoge zum Speichern, Laden und Charakter-Hinzufuegen.
 *
 * Aus save_load.js herausgeloest (Umbau 16.08.2026).
 */


// File picker helpers
export async function _openJsonFilePicker() {
    if (window.showOpenFilePicker) {
        try {
            const [handle] = await window.showOpenFilePicker({ types: [{ description: 'JSON',
                accept: { 'application/json': ['.json'] } }], multiple: false });
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
            const handle = await window.showSaveFilePicker({ suggestedName: defaultName, types: [{ description: 'JSON',
                accept: { 'application/json': ['.json'] } }] });
            const writable = await handle.createWritable();
            await writable.write(content); await writable.close();
            return handle.name;
        } catch (e) { if (e.name === 'AbortError') return null; }
    }
    // Rückfall ohne Dateiauswahl-API (Firefox): Der Link MUSS im Dokument
    // hängen, und der Objekt-URL darf erst nach dem Start des Downloads
    // freigegeben werden (Review 15.08.2026). Vorher stand `click()` auf einem
    // Element, das nie im DOM war, und `revokeObjectURL` direkt danach —
    // in Firefox kam so keine Datei an, und auch in Chrome ist das ein Rennen.
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = defaultName; a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, Zeiten.DOWNLOAD_MS);
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

// Scene dialogs
export function initCharacterDialog() {
    const addBtn = document.getElementById('add-character-btn');
    const dialog = document.getElementById('add-char-dialog');
    const confirmBtn = document.getElementById('add-char-confirm');
    addBtn.addEventListener('click', () => openAddCharacterDialog());
    confirmBtn.addEventListener('click', async () => {
        if (!state._addCharSelectedPreset) return;
        closeDialog(dialog);
        try { await fn.addCharacterFromPreset(state._addCharSelectedPreset);
            } catch (e) { alert(`Fehler: ${e.message}`); }
    });
}

export async function openAddCharacterDialog() {
    const dialog = document.getElementById('add-char-dialog');
    const confirmBtn = document.getElementById('add-char-confirm');
    const presetList = document.getElementById('preset-list');
    openDialog(dialog);
    state._addCharSelectedPreset = null;
    confirmBtn.disabled = true;
    presetList.innerHTML = '<li class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade Presets...</li>';
    try {
        const data = await Serverabruf.json('/api/character/models/');
        presetList.innerHTML = '';
        if (!data.presets || data.presets.length
            === 0) { presetList.innerHTML = '<li class="gedaempft">Keine Presets vorhanden.</li>'; return; }
        for (const p of data.presets) {
            const li = document.createElement('li'); li.textContent = p.label || p.name; li.dataset.presetName = p.name;
            li.addEventListener('click',
                () => { presetList.querySelectorAll('li').forEach(x => x.classList.remove('selected'));
                    li.classList.add('selected'); state._addCharSelectedPreset = p.name; confirmBtn.disabled = false;
                        });
            li.addEventListener('dblclick', async () => { state._addCharSelectedPreset = p.name; closeDialog(dialog);
                try { await fn.addCharacterFromPreset(p.name); } catch (e) { alert(`Fehler: ${e.message}`); } });
            presetList.appendChild(li);
        }
    } catch (e) { presetList.innerHTML = `<li class="fehlertext">Fehler: ${e.message}</li>`; }
}

export function initSceneDialogs() {
    const saveDialog = document.getElementById('save-scene-dialog');
    const saveNameInput = document.getElementById('save-scene-name');
    const saveConfirm = document.getElementById('save-scene-confirm');
    saveConfirm.addEventListener('click', async () => {
        const name = saveNameInput.value.trim();
        if (!name) { saveNameInput.focus(); return; }
        closeDialog(saveDialog);
        await doSaveScene(name);
    });
    saveNameInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') saveConfirm.click(); });
    const loadDialog = document.getElementById('load-scene-dialog');
    const loadConfirm = document.getElementById('load-scene-confirm');
    loadConfirm.addEventListener('click', async () => {
        if (!state._selectedFileToLoad) return;
        closeDialog(loadDialog);
        // Der Ladeweg wirft bei einem Fehlerstatus (`Serverabruf.json`) — ohne
        // dieses `catch` bliebe der Dialog zu und nichts würde passieren.
        try {
            await loadModelFile(state._selectedFileToLoad);
        } catch (fehler) {
            alert(`Fehler: ${fehler.message}`);
        }
    });
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
    tbody.innerHTML = '<tr><td colspan="3" class="leer-hinweis-mitte"><i class="fas fa-spinner fa-spin"></i> Lade...</td></tr>';
    try {
        const data = await Serverabruf.json('/api/character/model-files/');
        tbody.innerHTML = '';
        const files = data.files || [];
        if (files.length
            === 0) { tbody.innerHTML = '<tr><td colspan="3" class="leer-hinweis-mitte">Keine Dateien.</td></tr>';
                return; }
        for (const f of files) {
            const tr = document.createElement('tr');
            const isScene = f.type === 'scene';
            const icon = isScene ? 'fa-film' : 'fa-user';
            const typeBadge = isScene ? '<span class="file-type-scene">Szene</span>' : '<span class="file-type-model">Modell</span>';
            const dateStr = f.modified ? new Date(f.modified * 1000).toLocaleDateString('de-DE') : '';
            tr.innerHTML = `<td class="dateizelle"><i class="fas ${icon} dateisymbol"></i>${escapeHtml(f.label || f.name)}</td><td class="dateizelle mittig">${typeBadge}</td><td class="dateizelle datumszelle">${dateStr}</td>`;
            tr.style.cursor = 'pointer';
            tr.addEventListener('click',
                () => { tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
                    tr.classList.add('selected'); state._selectedFileToLoad = f; loadConfirm.disabled = false; });
            tr.addEventListener('dblclick', () => {
                state._selectedFileToLoad = f;
                closeDialog(loadDialog);
                loadModelFile(f).catch(
                    fehler => alert(`Fehler: ${fehler.message}`));
            });
            tbody.appendChild(tr);
        }
    } catch (e) { tbody.innerHTML = `<tr><td colspan="3" class="leer-hinweis-mitte fehlertext">Fehler: ${e.message}</td></tr>`; }
}

export async function loadSceneListInto(listEl, onSelect) {
    listEl.innerHTML = '<li class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade...</li>';
    try {
        const data = await Serverabruf.json('/api/character/scenes/');
        listEl.innerHTML = '';
        if (!data.scenes || data.scenes.length === 0) { listEl.innerHTML = '<li class="gedaempft">Keine Szenen.</li>';
            return; }
        for (const s of data.scenes) {
            const li = document.createElement('li');
            li.innerHTML = `${escapeHtml(s.label || s.name)} <span class="preset-sub">${s.character_count} Charakter(e)</span>`;
            li.addEventListener('click',
                () => { listEl.querySelectorAll('li').forEach(x => x.classList.remove('selected'));
                    li.classList.add('selected'); onSelect(s.name); });
            listEl.appendChild(li);
        }
    } catch (e) { listEl.innerHTML = `<li class="fehlertext">Fehler: ${e.message}</li>`; }
}
