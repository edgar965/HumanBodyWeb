/**
 * Viewer — Garment Fitter UI (catalog, fitting, region transforms).
 */
import * as THREE from 'three';
import { state, REGION_DEFS, REGION_RADIUS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, bindSlider, sliderVal } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { _saveGarmentState } from './garment_liste.js';
import { _applyGarmentState, _downloadPack, _loadDownloadPacks, _renderGarmentList } from './garment_liste.js';
import { Kleiderbedienung } from './kleiderbedienung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export async function loadGarmentUI() {
    // Die Bedienung steckt in `Kleiderbedienung` (viewer/kleiderbedienung.js) —
    // vorher standen hier 124 Zeilen, davon 30 nur Reglerbindungen.
    return new Kleiderbedienung({
        anziehen: kennung => loadGarment(kennung),
        abziehen: kennung => removeGarment(kennung),
        alleAb: () => removeAllGarments(),
    }).verdrahten();
}


function _computeRegionWeights(gid) {
    const orig = state.garmentOrigPositions[gid];
    if (!orig) return;
    const n = orig.length / 3;
    let yMin = Infinity, yMax = -Infinity;
    for (let i = 0; i < n; i++) { const y = orig[i * 3 + 1]; if (y < yMin) yMin = y; if (y > yMax) yMax = y; }
    const yRange = yMax - yMin || 1e-6;
    const weights = {};
    for (const def of REGION_DEFS) weights[def.id] = new Float32Array(n);
    for (let i = 0; i < n; i++) {
        const t = (orig[i * 3 + 1] - yMin) / yRange;
        for (const def of REGION_DEFS) {
            const dist = Math.abs(t - def.center);
            if (dist < REGION_RADIUS) weights[def.id][i] = 0.5 * (1 + Math.cos(Math.PI * dist / REGION_RADIUS));
        }
    }
    state.garmentRegionWeights[gid] = weights;
}


export function buildBodyFitQueryString() {
    const bodySelect = document.getElementById('body-type-select');
    const bodyType = bodySelect ? bodySelect.value : 'Female_Caucasian';
    const offset = (sliderVal('garment-offset') / 1000);
    const stiffness = (sliderVal('garment-stiffness') / 100);
    const colorPicker = document.getElementById('garment-color');
    const colorHex = colorPicker ? colorPicker.value : '#4d5980';
    const cr = parseInt(colorHex.slice(1, 3), 16) / 255;
    const cg = parseInt(colorHex.slice(3, 5), 16) / 255;
    const cb = parseInt(colorHex.slice(5, 7), 16) / 255;

    let qs = `body_type=${encodeURIComponent(bodyType)}`;
    const minDist = sliderVal('garment-min-dist');
    const crotchFloor = sliderVal('garment-crotch-floor');
    const lift = sliderVal('garment-lift');
    const crotchDepth = sliderVal('garment-crotch-depth');
    qs += `&offset=${offset}&stiffness=${stiffness}&min_dist=${minDist}&crotch_floor=${crotchFloor}&lift=${lift}&crotch_depth=${crotchDepth}`;
    qs += `&color_r=${cr.toFixed(3)}&color_g=${cg.toFixed(3)}&color_b=${cb.toFixed(3)}`;

    document.querySelectorAll('#morphs-panel input[type="range"][data-morph]').forEach(slider => {
        const mName = slider.dataset.morph;
        if (mName) qs += `&morph_${mName}=${slider.value / 100}`;
    });
    ['age', 'mass', 'tone', 'height'].forEach(m => {
        const el = document.getElementById(`meta-${m}`);
        if (el) {
            const dv = parseInt(el.value);
            const mn = parseInt(el.min), mx = parseInt(el.max);
            const neutral = (mn + mx) / 2;
            const half = (mx - mn) / 2;
            const internal = half ? (dv - neutral) / half : 0;
            qs += `&meta_${m}=${internal}`;
        }
    });
    return qs;
}

export async function loadGarment(garmentId) {
    const createBtn = document.getElementById('garment-create');
    if (createBtn) createBtn.disabled = true;
    ensureSkinned();

    try {
        const bodyQs = buildBodyFitQueryString();
        let qs = `garment_id=${encodeURIComponent(garmentId)}&${bodyQs}`;
        const data = await Serverabruf.json(`/api/character/garment/fit/?${qs}`);
        if (data.error) { console.error('Garment fit error:', data.error); return; }

        removeGarment(garmentId, true);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.computeVertexNormals();

        const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnit: -1,
        });

        let mesh;
        if (state.isSkinned && state.rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices);
            const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat);
            mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        } else {
            mesh = new THREE.Mesh(geo, mat);
        }

        state.garmentMeshes[garmentId] = mesh;
        state.scene.add(mesh);
        state.garmentOrigPositions[garmentId] = new Float32Array(vertBuf);
        _computeRegionWeights(garmentId);
        _saveGarmentState(garmentId);
        _applyGarmentState(garmentId);

        Protokoll.debug('Viewer', `Garment ${garmentId}: ${data.vertex_count} verts, skinned=${mesh.isSkinnedMesh || false}`);

        // Auto-select
        if (state._selectedItem) fn._setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
        state._selectedItem = { root: mesh, type: 'garment', id: garmentId, label: garmentId.split('/').pop() };
        fn._setEmissiveOnItem(state._selectedItem, state._SELECT_EMISSIVE);
        const rb = document.getElementById('selection-remove-btn');
        if (rb) rb.style.display = '';

        fn.updateEquippedList();
    } catch (e) {
        console.error('Failed to load garment:', e);
    }
    if (createBtn) createBtn.disabled = false;
}

export function removeGarment(garmentId, keepState) {
    const m = state.garmentMeshes[garmentId];
    if (m) {
        state.scene.remove(m);
        m.geometry.dispose();
        m.material.dispose();
        delete state.garmentMeshes[garmentId];
        if (!keepState) {
            delete state.garmentState[garmentId];
            delete state.garmentOrigPositions[garmentId];
            delete state.garmentRegionWeights[garmentId];
        }
        fn.updateEquippedList();
    }
}

export function removeAllGarments() {
    for (const id of Object.keys(state.garmentMeshes)) removeGarment(id);
    fn.updateEquippedList();
}



// Register
fn.loadGarmentUI = loadGarmentUI;
fn.loadGarment = loadGarment;
fn.removeGarment = removeGarment;
fn.removeAllGarments = removeAllGarments;
fn._saveGarmentState = _saveGarmentState;
fn.buildBodyFitQueryString = buildBodyFitQueryString;
