import { CharacterInstance } from './character.js';
import { Modellbauzustand } from './modellgenerator/zustand.js';
import * as THREE from 'three';
import { escapeHtml, generateCharacterId } from './utils.js';
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';
import { markDirty } from './undo.js';
/**
 * Charakterliste der Szene: anzeigen, auswaehlen, entfernen, anfliegen.
 *
 * Aus character.js herausgeloest (Umbau 16.08.2026) — die Klasse
 * CharacterInstance und die Verwaltung der Liste sind zwei Themen.
 */


// =========================================================================
// Character management functions
// =========================================================================
export async function addCharacterFromPreset(presetName) {
    const resp = await fetch(`/api/character/model/${encodeURIComponent(presetName)}/`);
    if (!resp.ok) throw new Error(`Preset not found: ${presetName}`);
    const presetData = await resp.json();

    const id = generateCharacterId();
    const inst = new CharacterInstance(id, presetData);

    const xOffset = state.characters.size * 0.8;
    inst.group.position.set(xOffset, 0, 0);

    inst.presetKey = presetName;
    inst.presetName = presetName;
    await inst.load();
    state.characters.set(id, inst);
    state.scene.add(inst.group);

    fn.updateCharacterListUI();
    fn.updateVertexCount();
    fn.selectCharacter(id);
    markDirty();

    return inst;
}

export async function loadDefaultCharacter() {
    try {
        await addCharacterFromPreset(state.defaultPresetName);
    } catch (e) {
        console.warn('Failed to load default character:', e);
    }
}

export function selectCharacter(id) {
    if (state.selectedCharacterId && state.characters.has(state.selectedCharacterId)) {
        const prev = state.characters.get(state.selectedCharacterId);
        prev.selected = false;
        fn._setBodyEmissive(prev, state._ZERO_EMISSIVE);
    }

    state.selectedCharacterId = id;
    const inst = state.characters.get(id);
    if (!inst) {
        deselectCharacter();
        return;
    }

    inst.selected = true;
    if (!state._selectedSubMesh) {
        fn._setBodyEmissive(inst, state._SELECT_EMISSIVE);
    }
    state.transformControls.attach(inst.group);
    state.transformHelper.visible = true;
    state.transformControls.enabled = true;

    fn.updateCharacterListUI();
    fn.populateProperties(id);
    // Der Kleider-Reiter zeigt ohne Figur nur einen Hinweis. Vorher prüfte er
    // das mit einem Sekundenintervall selbst nach.
    fn.kleiderSichtbarkeit?.();
}

export function deselectCharacter() {
    if (state.selectedCharacterId && state.characters.has(state.selectedCharacterId)) {
        const prev = state.characters.get(state.selectedCharacterId);
        prev.selected = false;
        fn._setBodyEmissive(prev, state._ZERO_EMISSIVE);
    }
    fn.clearSubMeshSelection();
    state.selectedCharacterId = null;
    state.transformControls.detach();
    state.transformHelper.visible = false;
    state.transformControls.enabled = false;
    fn.updateCharacterListUI();
    fn.clearProperties();
    fn.kleiderSichtbarkeit?.();
}

export function deleteCharacter(id) {
    const inst = state.characters.get(id);
    if (!inst) return;

    if (state.selectedCharacterId === id) {
        deselectCharacter();
    }

    if (Modellbauzustand.charakterId === id) {
        fn._clearBoneHighlightCache();
        Modellbauzustand.charakterId = null;
    }

    inst.dispose();
    state.characters.delete(id);
    fn.updateCharacterListUI();
    fn.updateVertexCount();
    markDirty();
}

export function focusCharacter(id) {
    const inst = state.characters.get(id);
    if (!inst) return;
    const box = new THREE.Box3().setFromObject(inst.group);
    const center = box.getCenter(new THREE.Vector3());
    state.controls.target.copy(center);
    state.controls.update();
}

export function updateCharacterListUI() {
    const list = document.getElementById('character-list');
    const countEl = document.getElementById('char-count');
    if (countEl) countEl.textContent = state.characters.size;

    list.innerHTML = '';
    state.characters.forEach((inst, id) => {
        const li = document.createElement('li');
        li.className = 'character-item' + (id === state.selectedCharacterId ? ' selected' : '');
        li.dataset.charId = id;

        const pos = inst.group.position;
        const posStr = `${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}, ${pos.z.toFixed(1)}`;

        const icon = inst.generatedConfig ? 'fa-robot' : 'fa-user';
        li.innerHTML = `
            <span class="character-item-icon"><i class="fas ${icon}"></i></span>
            <div class="character-item-info">
                <div class="character-item-name">${escapeHtml(inst.presetName)}</div>
                <div class="character-item-detail">${escapeHtml(inst.bodyType)} &bull; (${posStr})</div>
            </div>
            <div class="character-item-actions">
                <button class="btn-focus" title="Fokussieren"><i class="fas fa-crosshairs"></i></button>
                <button class="btn-delete" title="L\u00f6schen"><i class="fas fa-trash"></i></button>
            </div>
        `;

        li.addEventListener('click', (e) => {
            if (e.target.closest('.character-item-actions')) return;
            selectCharacter(id);
        });

        li.querySelector('.btn-focus').addEventListener('click', (e) => {
            e.stopPropagation();
            selectCharacter(id);
            focusCharacter(id);
        });

        li.querySelector('.btn-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteCharacter(id);
        });

        list.appendChild(li);
    });

    if (state.currentPropsCharId && state.currentPropsCharId === state.selectedCharacterId) {
        fn.syncTransformInputs();
    }
}

export function updateVertexCount() {
    let total = 0;
    state.characters.forEach(inst => {
        if (inst.bodyMesh) total += inst.bodyMesh.geometry.attributes.position.count;
        for (const m of Object.values(inst.clothMeshes)) {
            if (m && m.geometry) total += m.geometry.attributes.position.count;
        }
        if (inst.hairMesh) {
            inst.hairMesh.traverse(child => {
                if (child.isMesh && child.geometry) total += child.geometry.attributes.position.count;
            });
        }
    });
    document.getElementById('vertex-count').textContent = total.toLocaleString();
}

export function clearAllCharacters() {
    deselectCharacter();
    state.characters.forEach(inst => inst.dispose());
    state.characters.clear();
    updateCharacterListUI();
    updateVertexCount();
}

export function setTransformMode(mode) {
    state.currentTransformMode = mode;
    state.transformControls.setMode(mode);
    document.querySelectorAll('.transform-btn[data-mode]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
}
