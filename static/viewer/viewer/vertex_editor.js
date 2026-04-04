/**
 * Viewer — Vertex Editor (3D) — BVH raycast + TransformControls gizmo.
 */
import * as THREE from 'three';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { state, acceleratedRaycast } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, blenderToThreeCoords, float32ToBase64, uint32ToBase64, threeToBlenderCoords, buildBodyQueryString } from './utils.js';

// Vertex editor state
let veActive = false;
let veTargetMesh = null;
let veTargetKey = null;
let vePointsOverlay = null;
let veSelectedIndices = new Set();
let veOrigPositions = null;
let veGizmo = null;
let veGizmoHelper = null;
let veGizmoLastPos = new THREE.Vector3();
let veBoxSelecting = false;
let veBoxStart = { x: 0, y: 0 };
let veBoxEnd = { x: 0, y: 0 };
let veOrigRaycast = null;
const VE_COLOR_DEFAULT  = new THREE.Color(0.35, 0.45, 0.65);
const VE_COLOR_SELECTED = new THREE.Color(1.0, 0.9, 0.2);

export function veEnterEditMode() {
    let mesh = null;
    let key = null;
    if (state._selectedItem && (state._selectedItem.type === 'cloth' || state._selectedItem.type === 'garment')) {
        mesh = state.clothMeshes[state._selectedItem.id] || state.garmentMeshes[state._selectedItem.id];
        key = state._selectedItem.id;
    }
    if (!mesh) { mesh = state.clothMeshes['pe_preview']; key = 'pe_preview'; }
    if (!mesh) { console.warn('Vertex Edit: no cloth/garment mesh found'); return; }

    veActive = true;
    veTargetMesh = mesh;
    veTargetKey = key;
    veSelectedIndices.clear();

    const posAttr = mesh.geometry.getAttribute('position');
    posAttr.setUsage(THREE.DynamicDrawUsage);
    veOrigPositions = new Float32Array(posAttr.array);

    mesh.geometry.computeBoundsTree();
    veOrigRaycast = mesh.raycast;
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
    vePointsOverlay = new THREE.Points(pointsGeo, pointsMat);
    vePointsOverlay.matrixAutoUpdate = false;
    vePointsOverlay.matrix.copy(mesh.matrixWorld);
    vePointsOverlay.matrixWorld.copy(mesh.matrixWorld);
    vePointsOverlay.renderOrder = 999;
    state.scene.add(vePointsOverlay);

    veGizmoHelper = new THREE.Object3D();
    state.scene.add(veGizmoHelper);
    veGizmo = new TransformControls(state.camera, state.renderer.domElement);
    veGizmo.attach(veGizmoHelper);
    veGizmo.setMode('translate');
    veGizmo.setSize(0.6);
    veGizmo.visible = false;
    veGizmo.enabled = false;
    state.scene.add(veGizmo.getHelper());

    veGizmo.addEventListener('dragging-changed', (ev) => { state.controls.enabled = !ev.value; });
    veGizmo.addEventListener('objectChange', () => { _veApplyGizmoDelta(); });

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
    if (veTargetMesh && veOrigRaycast) { veTargetMesh.raycast = veOrigRaycast; veOrigRaycast = null; }
    if (veTargetMesh?.geometry?.disposeBoundsTree) veTargetMesh.geometry.disposeBoundsTree();
    if (veGizmo) { state.scene.remove(veGizmo.getHelper()); veGizmo.detach(); veGizmo.dispose(); veGizmo = null; }
    if (veGizmoHelper) { state.scene.remove(veGizmoHelper); veGizmoHelper = null; }
    if (vePointsOverlay) { state.scene.remove(vePointsOverlay); vePointsOverlay.geometry.dispose(); vePointsOverlay.material.dispose(); vePointsOverlay = null; }
    veActive = false; veTargetMesh = null; veTargetKey = null; veSelectedIndices.clear(); veOrigPositions = null; veBoxSelecting = false;
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) boxEl.style.display = 'none';
    const editCtrl = document.getElementById('pe-edit-controls');
    if (editCtrl) editCtrl.style.display = 'none';
}

function _veUpdateAllColors() {
    if (!vePointsOverlay) return;
    const colorAttr = vePointsOverlay.geometry.getAttribute('color');
    const count = colorAttr.count;
    for (let i = 0; i < count; i++) {
        const c = veSelectedIndices.has(i) ? VE_COLOR_SELECTED : VE_COLOR_DEFAULT;
        colorAttr.setXYZ(i, c.r, c.g, c.b);
    }
    colorAttr.needsUpdate = true;
}

function _veUpdateSelectionInfo() {
    const info = document.getElementById('ve-selection-info');
    const posFields = document.getElementById('ve-pos-fields');
    if (!info) return;
    const n = veSelectedIndices.size;
    if (n === 0) { info.textContent = 'No vertices selected'; if (posFields) posFields.style.display = 'none'; }
    else { info.textContent = `${n} ${n === 1 ? 'vertex' : 'vertices'} selected`; if (posFields) { posFields.style.display = ''; _veUpdatePosInputs(); } }
}

function _veUpdatePosInputs() {
    if (!veTargetMesh || veSelectedIndices.size === 0) return;
    const posAttr = veTargetMesh.geometry.getAttribute('position');
    let cx = 0, cy = 0, cz = 0;
    for (const idx of veSelectedIndices) { cx += posAttr.getX(idx); cy += posAttr.getY(idx); cz += posAttr.getZ(idx); }
    const n = veSelectedIndices.size;
    const px = document.getElementById('ve-pos-x'); const py = document.getElementById('ve-pos-y'); const pz = document.getElementById('ve-pos-z');
    if (px) px.value = (cx / n).toFixed(4); if (py) py.value = (cy / n).toFixed(4); if (pz) pz.value = (cz / n).toFixed(4);
}

function _veMoveSelectedByDelta(dx, dy, dz) {
    if (!veTargetMesh || !vePointsOverlay) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const overlayPos = vePointsOverlay.geometry.getAttribute('position');
    for (const idx of veSelectedIndices) {
        meshPos.setXYZ(idx, meshPos.getX(idx) + dx, meshPos.getY(idx) + dy, meshPos.getZ(idx) + dz);
        overlayPos.setXYZ(idx, overlayPos.getX(idx) + dx, overlayPos.getY(idx) + dy, overlayPos.getZ(idx) + dz);
    }
    meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
    veTargetMesh.geometry.computeVertexNormals(); veTargetMesh.geometry.computeBoundingSphere();
}

function _veApplyGizmoDelta() {
    if (!veGizmoHelper || !veTargetMesh || veSelectedIndices.size === 0) return;
    const newPos = veGizmoHelper.position.clone();
    const worldDelta = newPos.clone().sub(veGizmoLastPos);
    veGizmoLastPos.copy(newPos);
    const invMat = new THREE.Matrix4().copy(veTargetMesh.matrixWorld).invert();
    const localDelta = worldDelta.applyMatrix4(new THREE.Matrix4().extractRotation(invMat));
    _veMoveSelectedByDelta(localDelta.x, localDelta.y, localDelta.z);
    _veUpdatePosInputs();
}

function _veUpdateGizmo() {
    if (!veGizmo || !veGizmoHelper || !veTargetMesh) return;
    if (veSelectedIndices.size === 0) { veGizmo.visible = false; veGizmo.enabled = false; return; }
    const posAttr = veTargetMesh.geometry.getAttribute('position');
    let cx = 0, cy = 0, cz = 0;
    for (const idx of veSelectedIndices) { cx += posAttr.getX(idx); cy += posAttr.getY(idx); cz += posAttr.getZ(idx); }
    const n = veSelectedIndices.size;
    const localCentroid = new THREE.Vector3(cx / n, cy / n, cz / n);
    const worldCentroid = localCentroid.applyMatrix4(veTargetMesh.matrixWorld);
    veGizmoHelper.position.copy(worldCentroid); veGizmoLastPos.copy(worldCentroid);
    veGizmo.visible = true; veGizmo.enabled = true;
}

export function veHandleClick(e) {
    if (!veActive || !veTargetMesh) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    state._mouseNDC.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    state._mouseNDC.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    state._raycaster.setFromCamera(state._mouseNDC, state.camera);
    const intersects = state._raycaster.intersectObject(veTargetMesh);
    if (intersects.length > 0) {
        const hit = intersects[0]; const face = hit.face;
        const posAttr = veTargetMesh.geometry.getAttribute('position');
        const hitLocal = hit.point.clone().applyMatrix4(new THREE.Matrix4().copy(veTargetMesh.matrixWorld).invert());
        let bestIdx = face.a, bestDist = Infinity;
        for (const vi of [face.a, face.b, face.c]) {
            const vp = new THREE.Vector3(posAttr.getX(vi), posAttr.getY(vi), posAttr.getZ(vi));
            const d = vp.distanceTo(hitLocal);
            if (d < bestDist) { bestDist = d; bestIdx = vi; }
        }
        if (e.shiftKey) { if (veSelectedIndices.has(bestIdx)) veSelectedIndices.delete(bestIdx); else veSelectedIndices.add(bestIdx); }
        else { veSelectedIndices.clear(); veSelectedIndices.add(bestIdx); }
    } else if (!e.shiftKey) { veSelectedIndices.clear(); }
    _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
}

export function veBoxSelectStart(e) {
    if (!veActive) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    veBoxSelecting = true;
    veBoxStart = { x: e.clientX - rect.left, y: e.clientY - rect.top }; veBoxEnd = { ...veBoxStart };
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) { boxEl.style.display = 'block'; boxEl.style.left = veBoxStart.x + 'px'; boxEl.style.top = veBoxStart.y + 'px'; boxEl.style.width = '0px'; boxEl.style.height = '0px'; }
    state.controls.enabled = false;
}

export function veBoxSelectMove(e) {
    if (!veBoxSelecting) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    veBoxEnd = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) {
        const x = Math.min(veBoxStart.x, veBoxEnd.x), y = Math.min(veBoxStart.y, veBoxEnd.y);
        const w = Math.abs(veBoxEnd.x - veBoxStart.x), h = Math.abs(veBoxEnd.y - veBoxStart.y);
        boxEl.style.left = x + 'px'; boxEl.style.top = y + 'px'; boxEl.style.width = w + 'px'; boxEl.style.height = h + 'px';
    }
}

export function veBoxSelectEnd(e) {
    if (!veBoxSelecting) return;
    veBoxSelecting = false; state.controls.enabled = true;
    const boxEl = document.getElementById('ve-box-select');
    if (boxEl) boxEl.style.display = 'none';
    if (!veTargetMesh || !vePointsOverlay) return;
    const canvas = state.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    const w = rect.width, h = rect.height;
    const minX = Math.min(veBoxStart.x, veBoxEnd.x), maxX = Math.max(veBoxStart.x, veBoxEnd.x);
    const minY = Math.min(veBoxStart.y, veBoxEnd.y), maxY = Math.max(veBoxStart.y, veBoxEnd.y);
    if ((maxX - minX) < 3 && (maxY - minY) < 3) return;
    if (!e.shiftKey) veSelectedIndices.clear();
    const posAttr = veTargetMesh.geometry.getAttribute('position');
    const count = posAttr.count;
    const v = new THREE.Vector3();
    for (let i = 0; i < count; i++) {
        v.set(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i));
        v.applyMatrix4(veTargetMesh.matrixWorld); v.project(state.camera);
        const sx = (v.x * 0.5 + 0.5) * w, sy = (-v.y * 0.5 + 0.5) * h;
        if (sx >= minX && sx <= maxX && sy >= minY && sy <= maxY && v.z > 0 && v.z < 1) veSelectedIndices.add(i);
    }
    _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
}

async function _veSmooth() {
    if (!veActive || !veTargetMesh || veSelectedIndices.size === 0) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const posArr = new Float32Array(meshPos.array);
    const blenderVerts = threeToBlenderCoords(posArr);
    const indexAttr = veTargetMesh.geometry.getIndex();
    if (!indexAttr) return;
    const facesArr = new Uint32Array(indexAttr.array);
    const selected = Array.from(veSelectedIndices);
    const statusEl = document.getElementById('ve-selection-info');
    if (statusEl) statusEl.textContent = 'Smoothing...';
    try {
        const resp = await fetch('/api/character/vertex-edit/smooth/', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ vertices: float32ToBase64(blenderVerts), faces: uint32ToBase64(facesArr), selected, iterations: 3, factor: 0.3 })
        });
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }
        const updatedBlender = base64ToFloat32(data.vertices);
        blenderToThreeCoords(updatedBlender);
        const overlayPos = vePointsOverlay.geometry.getAttribute('position');
        for (const idx of selected) { const x = updatedBlender[idx*3]; const y = updatedBlender[idx*3+1]; const z = updatedBlender[idx*3+2]; meshPos.setXYZ(idx, x, y, z); overlayPos.setXYZ(idx, x, y, z); }
        meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
        veTargetMesh.geometry.computeVertexNormals(); veTargetMesh.geometry.computeBoundingSphere();
    } catch (err) { console.error('Smooth failed:', err); }
    _veUpdateGizmo(); _veUpdateSelectionInfo();
}

async function _vePushOutside() {
    if (!veActive || !veTargetMesh || veSelectedIndices.size === 0) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const posArr = new Float32Array(meshPos.array);
    const blenderVerts = threeToBlenderCoords(posArr);
    const selected = Array.from(veSelectedIndices);
    const bodyQs = buildBodyQueryString();
    const statusEl = document.getElementById('ve-selection-info');
    if (statusEl) statusEl.textContent = 'Pushing outside...';
    try {
        const resp = await fetch(`/api/character/vertex-edit/push-outside/?${bodyQs}`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ vertices: float32ToBase64(blenderVerts), selected, min_dist: 0.006 })
        });
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }
        const updatedBlender = base64ToFloat32(data.vertices);
        blenderToThreeCoords(updatedBlender);
        const overlayPos = vePointsOverlay.geometry.getAttribute('position');
        for (const idx of selected) { const x = updatedBlender[idx*3]; const y = updatedBlender[idx*3+1]; const z = updatedBlender[idx*3+2]; meshPos.setXYZ(idx, x, y, z); overlayPos.setXYZ(idx, x, y, z); }
        meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
        veTargetMesh.geometry.computeVertexNormals(); veTargetMesh.geometry.computeBoundingSphere();
    } catch (err) { console.error('Push outside failed:', err); }
    _veUpdateGizmo(); _veUpdateSelectionInfo();
}

function _veReset() {
    if (!veActive || !veTargetMesh || !veOrigPositions) return;
    const meshPos = veTargetMesh.geometry.getAttribute('position');
    const overlayPos = vePointsOverlay.geometry.getAttribute('position');
    const indices = veSelectedIndices.size > 0 ? veSelectedIndices : null;
    if (indices) {
        for (const idx of indices) { const x = veOrigPositions[idx*3]; const y = veOrigPositions[idx*3+1]; const z = veOrigPositions[idx*3+2]; meshPos.setXYZ(idx, x, y, z); overlayPos.setXYZ(idx, x, y, z); }
    } else { meshPos.array.set(veOrigPositions); overlayPos.array.set(veOrigPositions); }
    meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
    veTargetMesh.geometry.computeVertexNormals(); veTargetMesh.geometry.computeBoundingSphere();
    _veUpdateGizmo(); _veUpdatePosInputs();
}

export function veHandleKeydown(e) {
    if (e.key === 'Escape') { fn.peSetMode('select'); return; }
    if (e.key === 'a' || e.key === 'A') {
        if (veSelectedIndices.size > 0 && vePointsOverlay) veSelectedIndices.clear();
        else if (vePointsOverlay) { const count = vePointsOverlay.geometry.getAttribute('position').count; for (let i = 0; i < count; i++) veSelectedIndices.add(i); }
        _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
    }
}

export function initVertexEditorBindings() {
    document.getElementById('ve-select-all')?.addEventListener('click', () => {
        if (!veActive || !vePointsOverlay) return;
        const count = vePointsOverlay.geometry.getAttribute('position').count;
        for (let i = 0; i < count; i++) veSelectedIndices.add(i);
        _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
    });
    document.getElementById('ve-deselect-all')?.addEventListener('click', () => {
        if (!veActive) return; veSelectedIndices.clear(); _veUpdateAllColors(); _veUpdateGizmo(); _veUpdateSelectionInfo();
    });
    document.getElementById('ve-smooth')?.addEventListener('click', () => _veSmooth());
    document.getElementById('ve-push-outside')?.addEventListener('click', () => _vePushOutside());
    document.getElementById('ve-reset')?.addEventListener('click', () => _veReset());

    const veSizeSlider = document.getElementById('ve-point-size');
    const veSizeVal = document.getElementById('ve-point-size-val');
    if (veSizeSlider) {
        veSizeSlider.addEventListener('input', () => {
            const sz = parseInt(veSizeSlider.value); if (veSizeVal) veSizeVal.textContent = sz;
            if (vePointsOverlay) vePointsOverlay.material.size = sz;
        });
    }

    ['ve-pos-x', 've-pos-y', 've-pos-z'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', () => {
            if (!veActive || !veTargetMesh || veSelectedIndices.size === 0) return;
            const posAttr = veTargetMesh.geometry.getAttribute('position');
            let cx = 0, cy = 0, cz = 0;
            for (const idx of veSelectedIndices) { cx += posAttr.getX(idx); cy += posAttr.getY(idx); cz += posAttr.getZ(idx); }
            const n = veSelectedIndices.size;
            const newX = parseFloat(document.getElementById('ve-pos-x')?.value || 0);
            const newY = parseFloat(document.getElementById('ve-pos-y')?.value || 0);
            const newZ = parseFloat(document.getElementById('ve-pos-z')?.value || 0);
            _veMoveSelectedByDelta(newX - cx / n, newY - cy / n, newZ - cz / n);
            _veUpdateGizmo();
        });
    });
}

// Expose state getters
export function isVeActive() { return veActive; }
export function isVeBoxSelecting() { return veBoxSelecting; }
export function getVeTargetMesh() { return veTargetMesh; }
export function getVeSelectedIndices() { return veSelectedIndices; }

// Register
fn.veEnterEditMode = veEnterEditMode;
fn.veExitEditMode = veExitEditMode;
fn.veHandleClick = veHandleClick;
fn.veBoxSelectStart = veBoxSelectStart;
fn.veBoxSelectMove = veBoxSelectMove;
fn.veBoxSelectEnd = veBoxSelectEnd;
fn.veHandleKeydown = veHandleKeydown;
fn.isVeActive = isVeActive;
fn.isVeBoxSelecting = isVeBoxSelecting;
fn.getVeTargetMesh = getVeTargetMesh;
fn.getVeSelectedIndices = getVeSelectedIndices;
