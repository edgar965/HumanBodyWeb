/**
 * Punkte im Netz auswaehlen: Klick, Kastenauswahl, Farben.
 *
 * Aus vertex_editor.js herausgeloest (Umbau 16.08.2026).
 */
import { Vertexzustand } from './vertex_zustand.js';
import * as THREE from 'three';
import { _veUpdateGizmo, _veUpdatePosInputs } from './vertex_verschieben.js';
import { state } from './state.js';
import { VE_COLOR_DEFAULT } from './vertex_editor.js';
import { VE_COLOR_SELECTED } from './vertex_editor.js';


export function _veUpdateAllColors() {
    if (!Vertexzustand.vePointsOverlay) return;
    const colorAttr = Vertexzustand.vePointsOverlay.geometry.getAttribute('color');
    const count = colorAttr.count;
    for (let i = 0; i < count; i++) {
        const c = Vertexzustand.veSelectedIndices.has(i) ? VE_COLOR_SELECTED : VE_COLOR_DEFAULT;
        colorAttr.setXYZ(i, c.r, c.g, c.b);
    }
    colorAttr.needsUpdate = true;
}

export function _veUpdateSelectionInfo() {
    const info = document.getElementById('ve-selection-info');
    const posFields = document.getElementById('ve-pos-fields');
    if (!info) return;
    const n = Vertexzustand.veSelectedIndices.size;
    if (n === 0) { info.textContent = 'No vertices selected'; if (posFields) posFields.style.display = 'none'; }
    else { info.textContent = `${n} ${n === 1 ? 'vertex' : 'vertices'} selected`; if (posFields) { posFields.style.display = ''; _veUpdatePosInputs(); } }
}

export function veHandleClick(e) {
    if (!Vertexzustand.veActive || !Vertexzustand.veTargetMesh) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    state._mouseNDC.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    state._mouseNDC.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    state._raycaster.setFromCamera(state._mouseNDC, state.camera);
    const intersects = state._raycaster.intersectObject(Vertexzustand.veTargetMesh);
    if (intersects.length > 0) {
        const hit = intersects[0]; const face = hit.face;
        const posAttr = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
        const hitLocal = hit.point.clone().applyMatrix4(new THREE.Matrix4().copy(Vertexzustand.veTargetMesh.matrixWorld).invert());
        let bestIdx = face.a, bestDist = Infinity;
        for (const vi of [face.a, face.b, face.c]) {
            const vp = new THREE.Vector3(posAttr.getX(vi), posAttr.getY(vi), posAttr.getZ(vi));
            const d = vp.distanceTo(hitLocal);
            if (d < bestDist) { bestDist = d; bestIdx = vi; }
        }
        if (e.shiftKey) {
            if (Vertexzustand.veSelectedIndices.has(bestIdx)) Vertexzustand.veSelectedIndices.delete(bestIdx);
            else Vertexzustand.veSelectedIndices.add(bestIdx);
        }
        else { Vertexzustand.veSelectedIndices.clear(); Vertexzustand.veSelectedIndices.add(bestIdx); }
    } else if (!e.shiftKey) { Vertexzustand.veSelectedIndices.clear(); }
    _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
}

export function veBoxSelectStart(e) {
    if (!Vertexzustand.veActive) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    Vertexzustand.veBoxSelecting = true;
    Vertexzustand.veBoxStart = { x: e.clientX - rect.left, y: e.clientY - rect.top }; Vertexzustand.veBoxEnd = { ...veBoxStart };
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) {
        boxEl.style.display = 'block';
        boxEl.style.left = Vertexzustand.veBoxStart.x + 'px';
        boxEl.style.top = Vertexzustand.veBoxStart.y + 'px';
        boxEl.style.width = '0px';
        boxEl.style.height = '0px';
    }
    state.controls.enabled = false;
}

export function veBoxSelectMove(e) {
    if (!Vertexzustand.veBoxSelecting) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    Vertexzustand.veBoxEnd = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) {
        const x = Math.min(Vertexzustand.veBoxStart.x, Vertexzustand.veBoxEnd.x), y = Math.min(Vertexzustand.veBoxStart.y, Vertexzustand.veBoxEnd.y);
        const w = Math.abs(Vertexzustand.veBoxEnd.x - Vertexzustand.veBoxStart.x), h = Math.abs(Vertexzustand.veBoxEnd.y - Vertexzustand.veBoxStart.y);
        boxEl.style.left = x + 'px';
        boxEl.style.top = y + 'px';
        boxEl.style.width = w + 'px';
        boxEl.style.height = h + 'px';
    }
}

export function veBoxSelectEnd(e) {
    if (!Vertexzustand.veBoxSelecting) return;
    Vertexzustand.veBoxSelecting = false; state.controls.enabled = true;
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) boxEl.style.display = 'none';
    if (!Vertexzustand.veTargetMesh || !Vertexzustand.vePointsOverlay) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    const w = rect.width, h = rect.height;
    const minX = Math.min(Vertexzustand.veBoxStart.x, Vertexzustand.veBoxEnd.x), maxX = Math.max(Vertexzustand.veBoxStart.x, Vertexzustand.veBoxEnd.x);
    const minY = Math.min(Vertexzustand.veBoxStart.y, Vertexzustand.veBoxEnd.y), maxY = Math.max(Vertexzustand.veBoxStart.y, Vertexzustand.veBoxEnd.y);
    if ((maxX - minX) < 3 && (maxY - minY) < 3) return;
    if (!e.shiftKey) Vertexzustand.veSelectedIndices.clear();
    const posAttr = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
    const count = posAttr.count;
    const v = new THREE.Vector3();
    for (let i = 0; i < count; i++) {
        v.set(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i));
        v.applyMatrix4(Vertexzustand.veTargetMesh.matrixWorld); v.project(state.camera);
        const sx = (v.x * 0.5 + 0.5) * w, sy = (-v.y * 0.5 + 0.5) * h;
        if (sx >= minX && sx <= maxX && sy >= minY && sy <= maxY && v.z > 0 && v.z < 1) Vertexzustand.veSelectedIndices.add(i);
    }
    _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
}
