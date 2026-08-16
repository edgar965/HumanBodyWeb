/**
 * Ausgewaehlte Punkte bewegen, glaetten, nach aussen druecken.
 *
 * Aus vertex_editor.js herausgeloest (Umbau 16.08.2026).
 */
import { Vertexzustand } from './vertex_zustand.js';
import * as THREE from 'three';
import { _veUpdateSelectionInfo } from './vertex_auswahl.js';
import { buildBodyQueryString, float32ToBase64, threeToBlenderCoords, uint32ToBase64 } from './utils.js';
import { base64ToFloat32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/** Laplace-Glaettung: Schritte und Staerke je Aufruf des Knopfes. */
const GLAETTUNG_SCHRITTE = 3;
const GLAETTUNG_STAERKE = 0.3;


export function _veUpdatePosInputs() {
    if (!Vertexzustand.veTargetMesh || Vertexzustand.veSelectedIndices.size === 0) return;
    const posAttr = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
    let cx = 0, cy = 0, cz = 0;
    for (const idx of Vertexzustand.veSelectedIndices) { cx += posAttr.getX(idx); cy += posAttr.getY(idx); cz += posAttr.getZ(idx); }
    const n = Vertexzustand.veSelectedIndices.size;
    const px = document.getElementById('ve-pos-x'); const py = document.getElementById('ve-pos-y'); const pz = document.getElementById('ve-pos-z');
    if (px) px.value = (cx / n).toFixed(4); if (py) py.value = (cy / n).toFixed(4); if (pz) pz.value = (cz / n).toFixed(4);
}

export function _veMoveSelectedByDelta(dx, dy, dz) {
    if (!Vertexzustand.veTargetMesh || !Vertexzustand.vePointsOverlay) return;
    const meshPos = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
    const overlayPos = Vertexzustand.vePointsOverlay.geometry.getAttribute('position');
    for (const idx of Vertexzustand.veSelectedIndices) {
        meshPos.setXYZ(idx, meshPos.getX(idx) + dx, meshPos.getY(idx) + dy, meshPos.getZ(idx) + dz);
        overlayPos.setXYZ(idx, overlayPos.getX(idx) + dx, overlayPos.getY(idx) + dy, overlayPos.getZ(idx) + dz);
    }
    meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
    Vertexzustand.veTargetMesh.geometry.computeVertexNormals(); Vertexzustand.veTargetMesh.geometry.computeBoundingSphere();
}

export function _veApplyGizmoDelta() {
    if (!Vertexzustand.veGizmoHelper || !Vertexzustand.veTargetMesh || Vertexzustand.veSelectedIndices.size === 0) return;
    const newPos = Vertexzustand.veGizmoHelper.position.clone();
    const worldDelta = newPos.clone().sub(Vertexzustand.veGizmoLastPos);
    Vertexzustand.veGizmoLastPos.copy(newPos);
    const invMat = new THREE.Matrix4().copy(Vertexzustand.veTargetMesh.matrixWorld).invert();
    const localDelta = worldDelta.applyMatrix4(new THREE.Matrix4().extractRotation(invMat));
    _veMoveSelectedByDelta(localDelta.x, localDelta.y, localDelta.z);
    _veUpdatePosInputs();
}

export function _veUpdateGizmo() {
    if (!Vertexzustand.veGizmo || !Vertexzustand.veGizmoHelper || !Vertexzustand.veTargetMesh) return;
    if (Vertexzustand.veSelectedIndices.size === 0) { Vertexzustand.veGizmo.visible = false; Vertexzustand.veGizmo.enabled = false; return; }
    const posAttr = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
    let cx = 0, cy = 0, cz = 0;
    for (const idx of Vertexzustand.veSelectedIndices) { cx += posAttr.getX(idx); cy += posAttr.getY(idx); cz += posAttr.getZ(idx); }
    const n = Vertexzustand.veSelectedIndices.size;
    const localCentroid = new THREE.Vector3(cx / n, cy / n, cz / n);
    const worldCentroid = localCentroid.applyMatrix4(Vertexzustand.veTargetMesh.matrixWorld);
    Vertexzustand.veGizmoHelper.position.copy(worldCentroid); Vertexzustand.veGizmoLastPos.copy(worldCentroid);
    Vertexzustand.veGizmo.visible = true; Vertexzustand.veGizmo.enabled = true;
}

export async function _veSmooth() {
    if (!Vertexzustand.veActive || !Vertexzustand.veTargetMesh || Vertexzustand.veSelectedIndices.size === 0) return;
    const meshPos = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
    const posArr = new Float32Array(meshPos.array);
    const blenderVerts = threeToBlenderCoords(posArr);
    const indexAttr = Vertexzustand.veTargetMesh.geometry.getIndex();
    if (!indexAttr) return;
    const facesArr = new Uint32Array(indexAttr.array);
    const selected = Array.from(Vertexzustand.veSelectedIndices);
    const statusEl = document.getElementById('ve-selection-info');
    if (statusEl) statusEl.textContent = 'Smoothing...';
    try {
        const data = await Serverabruf.senden(
            '/api/character/vertex-edit/smooth/',
            { vertices: float32ToBase64(blenderVerts),
              faces: uint32ToBase64(facesArr), selected,
              iterations: GLAETTUNG_SCHRITTE, factor: GLAETTUNG_STAERKE });
        if (data.error) { console.error(data.error); return; }
        const updatedBlender = base64ToFloat32(data.vertices);
        blenderToThreeCoords(updatedBlender);
        const overlayPos = Vertexzustand.vePointsOverlay.geometry.getAttribute('position');
        for (const idx of selected) { const x = updatedBlender[idx*3]; const y = updatedBlender[idx*3+1]; const z = updatedBlender[idx*3+2]; meshPos.setXYZ(idx, x, y, z); overlayPos.setXYZ(idx, x, y, z); }
        meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
        Vertexzustand.veTargetMesh.geometry.computeVertexNormals(); Vertexzustand.veTargetMesh.geometry.computeBoundingSphere();
    } catch (err) { console.error('Smooth failed:', err); }
    _veUpdateGizmo(); _veUpdateSelectionInfo();
}

export async function _vePushOutside() {
    if (!Vertexzustand.veActive || !Vertexzustand.veTargetMesh || Vertexzustand.veSelectedIndices.size === 0) return;
    const meshPos = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
    const posArr = new Float32Array(meshPos.array);
    const blenderVerts = threeToBlenderCoords(posArr);
    const selected = Array.from(Vertexzustand.veSelectedIndices);
    const bodyQs = buildBodyQueryString();
    const statusEl = document.getElementById('ve-selection-info');
    if (statusEl) statusEl.textContent = 'Pushing outside...';
    try {
        const data = await Serverabruf.json(`/api/character/vertex-edit/push-outside/?${bodyQs}`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ vertices: float32ToBase64(blenderVerts), selected, min_dist: 0.006 })
        });
        if (data.error) { console.error(data.error); return; }
        const updatedBlender = base64ToFloat32(data.vertices);
        blenderToThreeCoords(updatedBlender);
        const overlayPos = Vertexzustand.vePointsOverlay.geometry.getAttribute('position');
        for (const idx of selected) { const x = updatedBlender[idx*3]; const y = updatedBlender[idx*3+1]; const z = updatedBlender[idx*3+2]; meshPos.setXYZ(idx, x, y, z); overlayPos.setXYZ(idx, x, y, z); }
        meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
        Vertexzustand.veTargetMesh.geometry.computeVertexNormals(); Vertexzustand.veTargetMesh.geometry.computeBoundingSphere();
    } catch (err) { console.error('Push outside failed:', err); }
    _veUpdateGizmo(); _veUpdateSelectionInfo();
}

export function _veReset() {
    if (!Vertexzustand.veActive || !Vertexzustand.veTargetMesh || !Vertexzustand.veOrigPositions) return;
    const meshPos = Vertexzustand.veTargetMesh.geometry.getAttribute('position');
    const overlayPos = Vertexzustand.vePointsOverlay.geometry.getAttribute('position');
    const indices = Vertexzustand.veSelectedIndices.size > 0 ? Vertexzustand.veSelectedIndices : null;
    if (indices) {
        for (const idx of indices) { const x = Vertexzustand.veOrigPositions[idx*3]; const y = Vertexzustand.veOrigPositions[idx*3+1]; const z = Vertexzustand.veOrigPositions[idx*3+2]; meshPos.setXYZ(idx, x, y, z); overlayPos.setXYZ(idx, x, y, z); }
    } else { meshPos.array.set(Vertexzustand.veOrigPositions); overlayPos.array.set(Vertexzustand.veOrigPositions); }
    meshPos.needsUpdate = true; overlayPos.needsUpdate = true;
    Vertexzustand.veTargetMesh.geometry.computeVertexNormals(); Vertexzustand.veTargetMesh.geometry.computeBoundingSphere();
    _veUpdateGizmo(); _veUpdatePosInputs();
}
