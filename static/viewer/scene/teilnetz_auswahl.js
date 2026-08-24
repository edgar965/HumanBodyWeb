import { fn } from '../gemeinsam/registrierung.js';
import { markDirty } from './undo.js';
import { state } from './state.js';
/**
 * Teilnetze eines Charakters auswaehlen und entfernen.
 *
 * Aus interaction.js herausgeloest (Umbau 16.08.2026).
 */


// =========================================================================
// Sub-mesh target helpers
// =========================================================================
export function getSelectableSubMeshes(charId) {
    const inst = state.characters.get(charId);
    if (!inst) return [];
    const targets = [];
    for (const [key, mesh] of Object.entries(inst.clothMeshes)) {
        if (mesh) {
            targets.push({ type: 'cloth', key, label: key, meshObj: mesh, charId });
        }
    }
    if (inst.hairMesh) {
        const hName = inst.hairStyle?.name || inst.hairStyle?.url?.split('/').pop() || 'Hair';
        targets.push({ type: 'hair', key: 'hair', label: `Hair (${hName})`, meshObj: inst.hairMesh, charId });
    }
    return targets;
}

export function getAllSubMeshTargets() {
    const targets = [];
    state.characters.forEach((inst, id) => { targets.push(...getSelectableSubMeshes(id)); });
    return targets;
}

export function _findSubMeshForObject(obj, targets) {
    for (const t of targets) {
        let cur = obj;
        while (cur) {
            if (cur === t.meshObj) return t;
            cur = cur.parent;
        }
    }
    return null;
}

export function _sameSubMesh(a, b) {
    if (!a || !b) return false;
    return a.type === b.type && a.key === b.key && a.charId === b.charId;
}

export function _getMeshesOf(root) {
    const meshes = [];
    if (root.isMesh) { meshes.push(root); } else { root.traverse(child => { if (child.isMesh) meshes.push(child); }); }
    return meshes;
}

export function _setSubMeshEmissive(target, color) {
    if (!target || !target.meshObj) return;
    for (const m of _getMeshesOf(target.meshObj)) {
        if (m.material) {
            const mats = Array.isArray(m.material) ? m.material : [m.material];
            for (const mat of mats) { if (mat.emissive) mat.emissive.copy(color); }
        }
    }
}

export function _setBodyEmissive(inst, color) {
    if (!inst || !inst.bodyMesh) return;
    const mats = Array.isArray(inst.bodyMesh.material) ? inst.bodyMesh.material : [inst.bodyMesh.material];
    for (const mat of mats) { if (mat.emissive) mat.emissive.copy(color); }
}

export function clearSubMeshSelection() {
    if (state._selectedSubMesh) {
        _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = null;
    }
    if (state._hoveredSubMesh) {
        _setSubMeshEmissive(state._hoveredSubMesh, state._ZERO_EMISSIVE);
        state._hoveredSubMesh = null;
    }
    fn._updatePropContext();
    const tooltip = document.getElementById('mesh-tooltip');
    if (tooltip) tooltip.style.display = 'none';
}

export function _doSubMeshClick(hitTarget) {
    const inst = state.characters.get(hitTarget.charId);
    if (_sameSubMesh(state._selectedSubMesh, hitTarget)) {
        _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = null;
        if (inst) _setBodyEmissive(inst, state._SELECT_EMISSIVE);
    } else {
        if (state._selectedSubMesh) _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = hitTarget;
        _setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
        if (inst) _setBodyEmissive(inst, state._ZERO_EMISSIVE);
    }
    fn._syncGarmentSliders();
    fn.switchTab('eigenschaften');
    fn._updatePropContext();
    if (state._selectedSubMesh && state._selectedSubMesh.type === 'cloth') {
        fn._syncPropGarmentControls();
    } else if (state._selectedSubMesh && state._selectedSubMesh.type === 'hair') {
        fn._syncPropHairControls();
    }
    if (inst) fn.updateEquippedList(inst);
}

export function _removeSubMesh(target) {
    if (!target) return;
    const inst = state.characters.get(target.charId);
    if (!inst) return;

    switch (target.type) {
        case 'cloth': {
            const mesh = inst.clothMeshes[target.key];
            if (mesh) {
                inst.group.remove(mesh);
                mesh.geometry.dispose();
                if (Array.isArray(mesh.material)) { mesh.material.forEach(m => m.dispose()); } else { mesh.material.dispose(); }
                delete inst.clothMeshes[target.key];
                if (target.key.startsWith('gar_')) {
                    const garId = target.key.slice(4);
                    inst.garments = (inst.garments || []).filter(g => g.id !== garId);
                    delete inst.garmentState[target.key];
                    delete inst.garmentOrigPositions[target.key];
                    delete inst.garmentRegionWeights[target.key];
                } else {
                    inst.cloth = (inst.cloth || []).filter(c => {
                        const m = c.method || 'template';
                        let ck;
                        if (m === 'builder') ck = `bld_${c.region || 'TOP'}`;
                        else if (m === 'primitive') ck = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
                        else ck = `tpl_${c.template || 'TPL_TSHIRT'}`;
                        return ck !== target.key;
                    });
                }
            }
            break;
        }
        case 'hair': {
            if (inst.hairMesh) {
                inst.group.remove(inst.hairMesh);
                inst.hairMesh.traverse(child => {
                    if (child.isMesh) {
                        child.geometry.dispose();
                        const mats = Array.isArray(child.material) ? child.material : [child.material];
                        mats.forEach(m => m.dispose());
                    }
                });
                inst.hairMesh = null;
                inst.hairStyle = null;
            }
            break;
        }
    }

    if (_sameSubMesh(state._selectedSubMesh, target)) state._selectedSubMesh = null;
    if (_sameSubMesh(state._hoveredSubMesh, target)) state._hoveredSubMesh = null;
    fn.updateEquippedList(inst);
    fn.updateVertexCount();
    markDirty();
}
