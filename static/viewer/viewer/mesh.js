/**
 * Viewer — Mesh loading, body materials, vertex updates.
 */
import * as THREE from 'three';
import { state, API, BODY_MATERIALS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from './utils.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';
import { applySceneSkinSettings, applySkinColor } from './scene_settings.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

function _getBodyTop() {
    if (!state.bodyGeometry) return null;
    const pos = state.bodyGeometry.attributes.position.array;
    let maxY = -Infinity;
    for (let i = 1; i < pos.length; i += 3) {
        if (pos[i] > maxY) maxY = pos[i];
    }
    return maxY;
}

export function updateMeshVertices(float32Buffer) {
    if (!state.bodyGeometry) return;
    const positions = state.bodyGeometry.attributes.position;
    const newData = new Float32Array(float32Buffer);
    blenderToThreeCoords(newData);
    positions.array.set(newData);
    positions.needsUpdate = true;
    state.bodyGeometry.computeBoundingSphere();
    if (state.initialBodyTop === null) {
        state.initialBodyTop = _getBodyTop();
    }
}

export async function loadMesh() {
    try {
        const data = await Serverabruf.json(`${API}/mesh/`);
        if (data.error) { console.error(data.error); return; }

        state.vertexCount = data.vertex_count;
        { const el = document.getElementById('vertex-count'); if (el) el.textContent = state.vertexCount.toLocaleString(); }

        // Puffer, Normalen, Materialgruppen: siehe `Koerpernetz`. Diese dreissig
        // Zeilen standen fuenfmal im Projekt, zweimal in DIESER Datei
        // (Befund `doppelcode`, 17.08.2026).
        state.bodyMesh = Koerpernetz.netz(data, THREE);
        const geo = state.bodyMesh.geometry;


        state.bodyGeometry = geo;
        state.scene.add(state.bodyMesh);
        if (state.initialBodyTop === null) state.initialBodyTop = _getBodyTop();

        { const el = document.getElementById('vertex-count'); if (el) el.textContent = geo.attributes.position.count.toLocaleString(); }

        applySceneSkinSettings();
        applySkinColor();
        fn.onResize();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

export async function reloadMeshForBodyType(bodyType, gender) {
    Protokoll.debug('Viewer', 'Reloading mesh for', bodyType, '(gender:', gender, ')');
    if (state.bodyMesh) {
        state.scene.remove(state.bodyMesh);
        state.bodyMesh.geometry?.dispose();
        state.bodyMesh = null;
        state.bodyGeometry = null;
    }
    state.isSkinned = false;
    state.rigifySkeleton = null;
    state.skinWeightData = null;
    state.initialBodyTop = null;

    try {
        const data = await Serverabruf.json(`${API}/mesh/?body_type=${encodeURIComponent(bodyType)}`);
        if (data.error) { console.error(data.error); return; }

        state.vertexCount = data.vertex_count;
        { const el = document.getElementById('vertex-count'); if (el) el.textContent = state.vertexCount.toLocaleString(); }

        // Puffer, Normalen, Materialgruppen: siehe `Koerpernetz`. Diese dreissig
        // Zeilen standen fuenfmal im Projekt, zweimal in DIESER Datei
        // (Befund `doppelcode`, 17.08.2026).
        state.bodyMesh = Koerpernetz.netz(data, THREE);
        const geo = state.bodyMesh.geometry;


        state.bodyGeometry = geo;
        state.scene.add(state.bodyMesh);
        state.initialBodyTop = _getBodyTop();

        { const el = document.getElementById('vertex-count'); if (el) el.textContent = geo.attributes.position.count.toLocaleString(); }

        applySceneSkinSettings();
        applySkinColor();

        state.skinWeightData = await Serverabruf.json(
            `${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);

        if (typeof fn.removeAllCloth === 'function') fn.removeAllCloth();
    } catch (e) {
        console.error('Failed to reload mesh:', e);
    }
}

// Register
fn.loadMesh = loadMesh;
fn.reloadMeshForBodyType = reloadMeshForBodyType;
fn.updateMeshVertices = updateMeshVertices;
fn._getBodyTop = _getBodyTop;
