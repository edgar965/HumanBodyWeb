/**
 * Viewer — Mesh loading, body materials, vertex updates.
 */
import * as THREE from 'three';
import { state, API, BODY_MATERIALS } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from './utils.js';
import { applySceneSkinSettings, applySkinColor } from './scene_settings.js';

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
        const resp = await fetch(`${API}/mesh/`);
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        state.vertexCount = data.vertex_count;
        { const el = document.getElementById('vertex-count'); if (el) el.textContent = state.vertexCount.toLocaleString(); }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            const faceBuf = base64ToUint32(data.faces);
            index = new THREE.BufferAttribute(faceBuf, 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            const uvBuf = base64ToFloat32(data.uvs);
            uvAttr = new THREE.BufferAttribute(uvBuf, 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        let geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];

        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            state.bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            state.bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

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
    console.log('Reloading mesh for', bodyType, '(gender:', gender, ')');
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
        const resp = await fetch(`${API}/mesh/?body_type=${encodeURIComponent(bodyType)}`);
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        state.vertexCount = data.vertex_count;
        { const el = document.getElementById('vertex-count'); if (el) el.textContent = state.vertexCount.toLocaleString(); }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            const faceBuf = base64ToUint32(data.faces);
            index = new THREE.BufferAttribute(faceBuf, 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            const uvBuf = base64ToFloat32(data.uvs);
            uvAttr = new THREE.BufferAttribute(uvBuf, 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        let geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];
        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            state.bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            state.bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        state.bodyGeometry = geo;
        state.scene.add(state.bodyMesh);
        state.initialBodyTop = _getBodyTop();

        { const el = document.getElementById('vertex-count'); if (el) el.textContent = geo.attributes.position.count.toLocaleString(); }

        applySceneSkinSettings();
        applySkinColor();

        const swResp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);
        state.skinWeightData = await swResp.json();

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
