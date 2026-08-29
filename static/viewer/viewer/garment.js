/**
 * Viewer — Garment Fitter UI (catalog, fitting, region transforms).
 */
import * as THREE from 'three';
import { state, REGION_DEFS, REGION_RADIUS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { sliderVal } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { _applyGarmentState, _saveGarmentState }
    from './garment_liste.js';
import { Kleiderbedienung } from './kleiderbedienung.js';
import { Metawerte } from './metawerte.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Werkstofffreigabe } from '../gemeinsam/werkstofffreigabe.js';
import { Netzgeometrie } from '../gemeinsam/netzgeometrie.js';
import { Hautnetz } from '../gemeinsam/hautnetz.js';

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
    qs += Metawerte.frage();   // Alter/Masse/Tonus/Größe, siehe metawerte.js
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

        // MIT den Normalen vom Server (28.08.2026). Diese Stelle war die
        // EINZIGE im Projekt, die sie verworfen und selbst gerechnet hat —
        // dasselbe Kleidungsstueck war im Betrachter anders beleuchtet als in
        // der Szene. Das war kein Entwurf, sondern eine Kopie, die
        // auseinandergelaufen ist.
        const geo = Netzgeometrie.bauen(data, THREE);

        const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnit: -1,
        });

        const mesh = Hautnetz.bauen(geo, mat, state, data);

        state.garmentMeshes[garmentId] = mesh;
        state.scene.add(mesh);
        // Die Ausgangslagen kommen aus dem Attribut, nicht aus einer
        // Zwischenvariablen: `vertBuf` gab es hier bis zum 28.08.2026, und
        // beim Zusammenziehen ist genau diese Zeile stehengeblieben —
        // gefunden von `Docu/umbau/kleidung_probe.mjs`, nicht vom Testlauf.
        state.garmentOrigPositions[garmentId] =
            new Float32Array(geo.getAttribute('position').array);
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
        Werkstofffreigabe.netz(m);   // samt Texturen
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
fn.removeAllGarments = removeAllGarments;
fn._saveGarmentState = _saveGarmentState;
