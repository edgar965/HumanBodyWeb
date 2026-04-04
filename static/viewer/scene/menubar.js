/**
 * Scene Editor -- Menubar, keyboard shortcuts.
 */
import { THREE, SESSION_KEY } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { sceneUndo } from './undo.js';
import { closeAllDialogs } from './utils.js';

export function closeAllMenus() {
    document.querySelectorAll('.menu.open').forEach(m => m.classList.remove('open'));
}

export function bindMenubar() {
    document.querySelectorAll('.menu-title').forEach(title => {
        title.addEventListener('click', (e) => {
            const menu = title.parentElement;
            const wasOpen = menu.classList.contains('open');
            closeAllMenus();
            if (!wasOpen) { updateMenuChecks(); menu.classList.add('open'); }
            e.stopPropagation();
        });
        title.addEventListener('mouseenter', () => {
            if (document.querySelector('.menu.open')) {
                closeAllMenus(); updateMenuChecks(); title.parentElement.classList.add('open');
            }
        });
    });
    document.addEventListener('click', () => closeAllMenus());
    document.querySelectorAll('.menu-dropdown').forEach(dd => {
        dd.addEventListener('click', (e) => e.stopPropagation());
    });
    document.querySelectorAll('.menu-item[data-action]').forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains('disabled')) return;
            closeAllMenus();
            handleMenuAction(item.dataset.action);
        });
    });
    document.querySelectorAll('.transform-btn[data-mode]').forEach(btn => {
        btn.addEventListener('click', () => fn.setTransformMode(btn.dataset.mode));
    });
}

export function handleMenuAction(action) {
    switch (action) {
        case 'new': fn.newScene(); break;
        case 'load': fn.loadFromFilePicker(); break;
        case 'save': fn.quickSave(); break;
        case 'save-as': fn.openSaveDialog(); break;
        case 'default-scene':
            sessionStorage.removeItem(SESSION_KEY);
            window.location.reload();
            break;
        case 'import-model': fn.importModelFromFilePicker(); break;
        case 'export-scene-json': fn.exportSceneJSON(); break;
        case 'export-model-json': fn.exportModelJSON(); break;
        case 'deselect': fn.deselectCharacter(); break;
        case 'delete':
            if (state._selectedSubMesh) { fn._removeSubMesh(state._selectedSubMesh); }
            else { fn.deleteSelectedCharacter(); }
            break;
        case 'clear-all':
            if (state.characters.size === 0) return;
            if (confirm('Alle Charaktere l\u00f6schen?')) fn.clearAllCharacters();
            break;
        case 'pose-tpose': fn.applyPoseFromServer('rest_poses/t-pose'); break;
        case 'pose-apose': {
            const inst = fn._selectedInst();
            if (inst?.isSkinned && inst._aPoseBones) {
                let skel = null;
                inst.group.traverse(child => { if (!skel && child.isSkinnedMesh && child.skeleton) skel = child.skeleton; });
                if (skel) { for (const bone of skel.bones) { const saved = inst._aPoseBones[bone.name]; if (saved) bone.quaternion.copy(saved); } }
            }
            break;
        }
        case 'add-character': fn.openAddCharacterDialog(); break;
        case 'toggle-model': fn.toggleModelVisibility(); document.getElementById('model-toggle')?.classList.toggle('active', state.modelVisible); break;
        case 'toggle-rig': fn.toggleRigVisibility(); document.getElementById('rig-toggle')?.classList.toggle('active', state.rigVisible); break;
        case 'mode-translate': fn.setTransformMode('translate'); break;
        case 'mode-rotate': fn.setTransformMode('rotate'); break;
        case 'mode-scale': fn.setTransformMode('scale'); break;
        case 'focus-char': if (state.selectedCharacterId) fn.focusCharacter(state.selectedCharacterId); break;
        case 'model-generator': fn.switchTab('modell'); fn.initModelGenerator(); break;
        case 'reset-scene': fn.resetScene(); break;
        case 'reset-lighting': fn.resetLighting(); break;
        case 'reset-camera': fn.resetCamera(); break;
        case 'anim-ground-fix': fn.applyGroundLevelFix(); break;
        case 'anim-save': fn.openSaveAnimDialog(); break;
    }
}

export function updateMenuChecks() {
    const modelItem = document.querySelector('[data-action="toggle-model"]');
    if (modelItem) modelItem.classList.toggle('checked', state.modelVisible);
    const rigItem = document.querySelector('[data-action="toggle-rig"]');
    if (rigItem) rigItem.classList.toggle('checked', state.rigVisible);
    document.querySelectorAll('.menu-item.radio[data-action^="mode-"]').forEach(item => {
        const mode = item.dataset.action.replace('mode-', '');
        item.classList.toggle('checked', mode === state.currentTransformMode);
    });
}

export function bindKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 's': e.preventDefault(); if (e.shiftKey) fn.openSaveDialog(); else fn.quickSave(); return;
                case 'o': e.preventDefault(); fn.openLoadDialog(); return;
                case 'n': e.preventDefault(); fn.newScene(); return;
            }
        }
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
        switch (e.key.toLowerCase()) {
            case 'g': fn.setTransformMode('translate'); break;
            case 'r': fn.setTransformMode('rotate'); break;
            case 's': fn.setTransformMode('scale'); break;
            case 'delete':
                if (state._selectedSubMesh) fn._removeSubMesh(state._selectedSubMesh);
                else fn.deleteSelectedCharacter();
                break;
            case 'escape': fn.deselectCharacter(); closeAllMenus(); closeAllDialogs(); break;
        }
    });
}

export function bindVisibilityToggles() {
    const modelToggle = document.getElementById('model-toggle');
    if (modelToggle) {
        modelToggle.addEventListener('click', () => {
            fn.toggleModelVisibility();
            modelToggle.classList.toggle('active', state.modelVisible);
        });
    }
    const clothesToggle = document.getElementById('clothes-toggle');
    if (clothesToggle) {
        clothesToggle.addEventListener('click', () => {
            state.clothesVisible = !state.clothesVisible;
            state.characters.forEach(inst => {
                for (const m of Object.values(inst.clothMeshes)) { if (m) m.visible = state.clothesVisible; }
                if (inst.hairMesh) inst.hairMesh.visible = state.clothesVisible;
            });
            clothesToggle.classList.toggle('active', state.clothesVisible);
        });
    }
    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            fn.toggleRigVisibility();
            rigToggle.classList.toggle('active', state.rigVisible);
        });
    }
}

export function toggleModelVisibility() {
    state.modelVisible = !state.modelVisible;
    state.characters.forEach(c => { if (c.bodyMesh) c.bodyMesh.visible = state.modelVisible; });
}

export function toggleRigVisibility() {
    state.rigVisible = !state.rigVisible;
    if (state.rigVisible) {
        const inst = fn._selectedInst();
        let skel = (inst && inst.rigifySkeleton) ? inst.rigifySkeleton : state.rigifySkeleton;
        if (!skel && state.rigifySkeletonData && state.skinWeightData) {
            const { buildRigifySkeleton } = fn;
            if (inst) { fn.convertInstToSkinned(inst); skel = inst.rigifySkeleton; }
            else { state.rigifySkeleton = buildRigifySkeleton(state.rigifySkeletonData, state.skinWeightData); state.scene.add(state.rigifySkeleton.rootBone); skel = state.rigifySkeleton; }
        }
        if (!state.skeletonHelper && skel) {
            state.skeletonHelper = new THREE.SkeletonHelper(skel.rootBone);
            state.skeletonHelper.material.depthTest = false;
            state.skeletonHelper.material.depthWrite = false;
            state.skeletonHelper.material.transparent = true;
            state.skeletonHelper.material.color.set(0x00ffaa);
            state.skeletonHelper.material.linewidth = 2;
            state.skeletonHelper.renderOrder = 999;
            state.scene.add(state.skeletonHelper);
        }
        if (state.skeletonHelper) state.skeletonHelper.visible = true;
    } else {
        if (state.skeletonHelper) state.skeletonHelper.visible = false;
    }
}

export function deleteSelectedCharacter() {
    if (!state.selectedCharacterId) return;
    fn.deleteCharacter(state.selectedCharacterId);
}

// Register
fn.closeAllMenus = closeAllMenus;
fn.bindMenubar = bindMenubar;
fn.handleMenuAction = handleMenuAction;
fn.bindKeyboardShortcuts = bindKeyboardShortcuts;
fn.bindVisibilityToggles = bindVisibilityToggles;
fn.toggleModelVisibility = toggleModelVisibility;
fn.toggleRigVisibility = toggleRigVisibility;
fn.deleteSelectedCharacter = deleteSelectedCharacter;
