/**
 * Viewer — Vertex Editor (3D) — BVH raycast + TransformControls gizmo.
 */
import * as THREE from 'three';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { state, acceleratedRaycast } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import './utils.js';
import { Vertexzustand } from './vertex_zustand.js';
import { _veApplyGizmoDelta, _veMoveSelectedByDelta, _vePushOutside, _veReset, _veSmooth, _veUpdateGizmo } from './vertex_verschieben.js';
import { _veUpdateAllColors, _veUpdateSelectionInfo, veBoxSelectEnd, veBoxSelectMove, veBoxSelectStart, veHandleClick } from './vertex_auswahl.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

// Vertex editor state
export const VE_COLOR_DEFAULT  = new THREE.Color(0.35, 0.45, 0.65);
export const VE_COLOR_SELECTED = new THREE.Color(1.0, 0.9, 0.2);

export function veEnterEditMode() {
    let mesh = null;
    let key = null;
    if (state._selectedItem && (state._selectedItem.type === 'cloth' || state._selectedItem.type === 'garment')) {
        mesh = state.clothMeshes[state._selectedItem.id] || state.garmentMeshes[state._selectedItem.id];
        key = state._selectedItem.id;
    }
    if (!mesh) { mesh = state.clothMeshes['pe_preview']; key = 'pe_preview'; }
    if (!mesh) { Protokoll.warnung('vertex_editor', 'Vertex Edit: no cloth/garment mesh found'); return; }

    Vertexzustand.veActive = true;
    Vertexzustand.veTargetMesh = mesh;
    Vertexzustand.veTargetKey = key;
    Vertexzustand.veSelectedIndices.clear();

    const posAttr = mesh.geometry.getAttribute('position');
    posAttr.setUsage(THREE.DynamicDrawUsage);
    Vertexzustand.veOrigPositions = new Float32Array(posAttr.array);

    mesh.geometry.computeBoundsTree();
    Vertexzustand.veOrigRaycast = mesh.raycast;
    mesh.raycast = acceleratedRaycast;

    const pointsGeo = new THREE.BufferGeometry();
    const count = posAttr.count;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
        positions[i * 3]     = posAttr.getX(i);
        positions[i * 3 + 1] = posAttr.getY(i);
        positions[i * 3 + 2] = posAttr.getZ(i);
        colors[i * 3]     = VE_COLOR_DEFAULT.r;
        colors[i * 3 + 1] = VE_COLOR_DEFAULT.g;
        colors[i * 3 + 2] = VE_COLOR_DEFAULT.b;
    }
    pointsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    pointsGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const pointSize = parseFloat(document.getElementById('ve-point-size')?.value || '5');
    const pointsMat = new THREE.PointsMaterial({
        size: pointSize, sizeAttenuation: false, vertexColors: true, depthTest: true, depthWrite: false,
    });
    Vertexzustand.vePointsOverlay = new THREE.Points(pointsGeo, pointsMat);
    Vertexzustand.vePointsOverlay.matrixAutoUpdate = false;
    Vertexzustand.vePointsOverlay.matrix.copy(mesh.matrixWorld);
    Vertexzustand.vePointsOverlay.matrixWorld.copy(mesh.matrixWorld);
    Vertexzustand.vePointsOverlay.renderOrder = 999;
    state.scene.add(Vertexzustand.vePointsOverlay);

    Vertexzustand.veGizmoHelper = new THREE.Object3D();
    state.scene.add(Vertexzustand.veGizmoHelper);
    Vertexzustand.veGizmo = new TransformControls(state.camera, state.renderer.domElement);
    Vertexzustand.veGizmo.attach(Vertexzustand.veGizmoHelper);
    Vertexzustand.veGizmo.setMode('translate');
    Vertexzustand.veGizmo.setSize(0.6);
    Vertexzustand.veGizmo.visible = false;
    Vertexzustand.veGizmo.enabled = false;
    state.scene.add(Vertexzustand.veGizmo.getHelper());

    Vertexzustand.veGizmo.addEventListener('dragging-changed', (ev) => { state.controls.enabled = !ev.value; });
    Vertexzustand.veGizmo.addEventListener('objectChange', () => { _veApplyGizmoDelta(); });

    const editCtrl = document.getElementById('pe-edit-controls');
    if (editCtrl) editCtrl.style.display = '';
    const patternCtrl = document.getElementById('pe-pattern-controls');
    if (patternCtrl) patternCtrl.style.display = 'none';
    const regionCtrl = document.getElementById('pe-region-controls');
    if (regionCtrl) regionCtrl.style.display = 'none';
    const wrapSection = document.getElementById('pe-wrap-section');
    if (wrapSection) wrapSection.style.display = 'none';

    _veUpdateSelectionInfo();
}

export function veExitEditMode() {
    if (Vertexzustand.veTargetMesh && Vertexzustand.veOrigRaycast) {
        Vertexzustand.veTargetMesh.raycast = Vertexzustand.veOrigRaycast;
        Vertexzustand.veOrigRaycast = null;
    }
    if (Vertexzustand.veTargetMesh?.geometry?.disposeBoundsTree) Vertexzustand.veTargetMesh.geometry.disposeBoundsTree();
    if (Vertexzustand.veGizmo) {
        state.scene.remove(Vertexzustand.veGizmo.getHelper());
        Vertexzustand.veGizmo.detach();
        Vertexzustand.veGizmo.dispose();
        Vertexzustand.veGizmo = null;
    }
    if (Vertexzustand.veGizmoHelper) {
        state.scene.remove(Vertexzustand.veGizmoHelper);
        Vertexzustand.veGizmoHelper = null;
    }
    if (Vertexzustand.vePointsOverlay) {
        state.scene.remove(Vertexzustand.vePointsOverlay);
        Vertexzustand.vePointsOverlay.geometry.dispose();
        Vertexzustand.vePointsOverlay.material.dispose();
        Vertexzustand.vePointsOverlay = null;
    }
    Vertexzustand.veActive = false;
    Vertexzustand.veTargetMesh = null;
    Vertexzustand.veTargetKey = null;
    Vertexzustand.veSelectedIndices.clear();
    Vertexzustand.veOrigPositions = null;
    Vertexzustand.veBoxSelecting = false;
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) boxEl.style.display = 'none';
    const editCtrl = document.getElementById('pe-edit-controls');
    if (editCtrl) editCtrl.style.display = 'none';
}

export function veHandleKeydown(e) {
    if (e.key === 'Escape') { fn.peSetMode('select'); return; }
    if (e.key === 'a' || e.key === 'A') {
        if (Vertexzustand.veSelectedIndices.size > 0 && Vertexzustand.vePointsOverlay) Vertexzustand.veSelectedIndices.clear();
        else if (Vertexzustand.vePointsOverlay) { const count = Vertexzustand.vePointsOverlay.geometry.getAttribute('position').count; for (let i = 0; i < count; i++) Vertexzustand.veSelectedIndices.add(i); }
        _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
    }
}

export function initVertexEditorBindings() {
    document.getElementById('ve-select-all')?.addEventListener('click', () => {
        if (!Vertexzustand.veActive || !Vertexzustand.vePointsOverlay) return;
        const count = Vertexzustand.vePointsOverlay.geometry.getAttribute('position').count;
        for (let i = 0; i < count; i++) Vertexzustand.veSelectedIndices.add(i);
        _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
    });
    document.getElementById('ve-deselect-all')?.addEventListener('click', () => {
        if (!Vertexzustand.veActive) return;
        Vertexzustand.veSelectedIndices.clear();
        _veUpdateAllColors();
        _veUpdateGizmo();
        _veUpdateSelectionInfo();
    });
    document.getElementById('ve-smooth')?.addEventListener('click', () => _veSmooth());
    document.getElementById('ve-push-outside')?.addEventListener('click', () => _vePushOutside());
    document.getElementById('ve-reset')?.addEventListener('click', () => _veReset());

    const veSizeSlider = document.getElementById('ve-point-size');
    const veSizeVal = document.getElementById('ve-point-size-val');
    if (veSizeSlider) {
        veSizeSlider.addEventListener('input', () => {
            const sz = parseInt(veSizeSlider.value); if (veSizeVal) veSizeVal.textContent = sz;
            if (Vertexzustand.vePointsOverlay) Vertexzustand.vePointsOverlay.material.size = sz;
        });
    }

    ['ve-pos-x', 've-pos-y', 've-pos-z'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', () => {
            if (!Vertexzustand.veActive || !Vertexzustand.veTargetMesh || Vertexzustand.veSelectedIndices.size === 0) return;
            const posAttr = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
            let cx = 0, cy = 0, cz = 0;
            for (const idx of Vertexzustand.veSelectedIndices) { cx += posAttr.getX(idx); cy += posAttr.getY(idx); cz += posAttr.getZ(idx); }
            const n = Vertexzustand.veSelectedIndices.size;
            const newX = parseFloat(document.getElementById('ve-pos-x')?.value || 0);
            const newY = parseFloat(document.getElementById('ve-pos-y')?.value || 0);
            const newZ = parseFloat(document.getElementById('ve-pos-z')?.value || 0);
            _veMoveSelectedByDelta(newX - cx / n, newY - cy / n, newZ - cz / n);
            _veUpdateGizmo();
        });
    });
}

// Expose state getters
export function isVeActive() { return Vertexzustand.veActive; }
export function isVeBoxSelecting() { return Vertexzustand.veBoxSelecting; }
export function getVeTargetMesh() { return Vertexzustand.veTargetMesh; }
export function getVeSelectedIndices() { return Vertexzustand.veSelectedIndices; }

// Register
fn.veEnterEditMode = veEnterEditMode;
fn.veExitEditMode = veExitEditMode;
fn.getVeTargetMesh = getVeTargetMesh;
fn.getVeSelectedIndices = getVeSelectedIndices;
