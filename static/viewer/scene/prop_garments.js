/**
 * Scene Editor -- Eigenschaften tab garment property controls.
 * (initPropGarmentControls, _syncPropGarmentControls, _refitAllForCurrentChar)
 */
import { THREE } from './state.js';
import { state, REGION_IDS } from './state.js';
import { fn } from './registry.js';
import { _bindSlider, _sliderVal, _selectedInst, _charQueryParams, _getBodyTop, base64ToFloat32, base64ToUint32, blenderToThreeCoords } from './utils.js';
import { _selectedGarmentMesh, _computeGarmentRegionWeights, _applyGarmentRegionOffsets, _syncGarmentSliders } from './garments.js';
import { _skinifyMesh, convertInstToSkinned, _skinifyHairGroup } from './skeleton.js';
import { markDirty } from './undo.js';

export function _syncPropGarmentControls() {
    const sel = _selectedGarmentMesh();
    const sec = document.getElementById('prop-garment-section');
    if (!sel || !sel.key.startsWith('gar_')) { if (sec) sec.style.display = 'none'; return; }
    if (sec) sec.style.display = '';
    const st = sel.inst.garmentState[sel.key]; if (!st) return;
    const _set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    const _setV = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
    _set('prop-garment-offset', Math.round(st.offset * 1000)); _setV('prop-garment-offset-val', st.offset.toFixed(3));
    _set('prop-garment-stiffness', Math.round(st.stiffness * 100)); _setV('prop-garment-stiffness-val', st.stiffness.toFixed(2));
    _set('prop-garment-min-dist', st.minDist ?? 3); _setV('prop-garment-min-dist-val', (st.minDist ?? 3) + ' mm');
    _set('prop-garment-crotch-floor', st.crotchFloor ?? 0); _setV('prop-garment-crotch-floor-val', (st.crotchFloor ?? 0) + ' mm');
    _set('prop-garment-lift', st.lift ?? 0); _setV('prop-garment-lift-val', (st.lift ?? 0) + ' mm');
    _set('prop-garment-crotch-depth', st.crotchDepth ?? 0); _setV('prop-garment-crotch-depth-val', (st.crotchDepth ?? 0) + ' mm');
    _set('prop-garment-roughness', Math.round(st.roughness * 100)); _setV('prop-garment-roughness-val', st.roughness.toFixed(2));
    _set('prop-garment-metalness', Math.round(st.metalness * 100)); _setV('prop-garment-metalness-val', st.metalness.toFixed(2));
    const colorEl = document.getElementById('prop-garment-color');
    if (colorEl && st.color) colorEl.value = '#' + new THREE.Color(st.color[0], st.color[1], st.color[2]).getHexString();
    for (const rid of REGION_IDS) {
        const stKey = 'region' + rid[0].toUpperCase() + rid.slice(1);
        const el = document.getElementById(`prop-garment-region-${rid}`); if (el) el.value = Math.round((st[stKey] || 0) * 100);
        const valEl = document.getElementById(`prop-garment-region-${rid}-val`); if (valEl) valEl.textContent = (st[stKey] || 0).toFixed(2) + ' m';
    }
}

export function initPropGarmentControls() {
    _bindSlider('prop-garment-offset', 'prop-garment-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('prop-garment-stiffness', 'prop-garment-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('prop-garment-min-dist', 'prop-garment-min-dist-val', v => v + ' mm');
    _bindSlider('prop-garment-crotch-floor', 'prop-garment-crotch-floor-val', v => v + ' mm');
    _bindSlider('prop-garment-lift', 'prop-garment-lift-val', v => v + ' mm');
    _bindSlider('prop-garment-crotch-depth', 'prop-garment-crotch-depth-val', v => v + ' mm');
    _bindSlider('prop-garment-roughness', 'prop-garment-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('prop-garment-metalness', 'prop-garment-metalness-val', v => (v / 100).toFixed(2));
    const roughSlider = document.getElementById('prop-garment-roughness');
    if (roughSlider) roughSlider.addEventListener('input', () => { const sel = _selectedGarmentMesh(); if (sel) sel.mesh.material.roughness = _sliderVal('prop-garment-roughness') / 100; });
    const metalSlider = document.getElementById('prop-garment-metalness');
    if (metalSlider) metalSlider.addEventListener('input', () => { const sel = _selectedGarmentMesh(); if (sel) sel.mesh.material.metalness = _sliderVal('prop-garment-metalness') / 100; });
    const colorPicker = document.getElementById('prop-garment-color');
    if (colorPicker) colorPicker.addEventListener('input', () => { const sel = _selectedGarmentMesh(); if (sel) sel.mesh.material.color.set(colorPicker.value); });
    for (const rid of REGION_IDS) {
        _bindSlider(`prop-garment-region-${rid}`, `prop-garment-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
    }
}

export async function _refitAllForCurrentChar() {
    const inst = state.characters.get(state.currentPropsCharId);
    if (!inst) return;
    const btn = document.getElementById('prop-refit-btn');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...'; }
    state._refitting = true;
    try {
        // Refit garments
        const garKeys = Object.keys(inst.clothMeshes).filter(k => k.startsWith('gar_'));
        for (const key of garKeys) {
            const garId = key.substring(4);
            const gState = inst.garmentState[key] || {};
            const params = _charQueryParams(inst);
            params.set('garment_id', garId);
            params.set('offset', (gState.offset || 0.006).toFixed(4));
            params.set('stiffness', (gState.stiffness || 0.5).toFixed(2));
            let color = gState.color;
            if (!color || !Array.isArray(color)) { const c = new THREE.Color(color || 0x4d5980); color = [c.r, c.g, c.b]; }
            params.set('color_r', Number(color[0]).toFixed(3)); params.set('color_g', Number(color[1]).toFixed(3)); params.set('color_b', Number(color[2]).toFixed(3));
            try {
                const resp = await fetch(`/api/character/garment/fit/?${params}`);
                const data = await resp.json(); if (data.error) continue;
                if (inst.clothMeshes[key]) { inst.group.remove(inst.clothMeshes[key]); inst.clothMeshes[key].geometry.dispose(); inst.clothMeshes[key].material.dispose(); }
                const vertBuf = base64ToFloat32(data.vertices); blenderToThreeCoords(vertBuf);
                const faceBuf = base64ToUint32(data.faces);
                const geo = new THREE.BufferGeometry();
                geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
                geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.computeVertexNormals();
                const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(color[0], color[1], color[2]), roughness: gState.roughness ?? 0.8, metalness: gState.metalness ?? 0.0, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnit: -1 });
                const mesh = _skinifyMesh(geo, mat, inst, data);
                inst.clothMeshes[key] = mesh; inst.group.add(mesh);
                inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
                _computeGarmentRegionWeights(inst, key); _applyGarmentRegionOffsets(inst, key);
            } catch (e) { console.log(`[Refit] ${key} failed: ${e.message}`); }
        }
        fn.updateEquippedList(inst); fn.updateVertexCount(); markDirty();
    } catch (e) { console.error('Refit all failed:', e); }
    finally { state._refitting = false; if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-sync"></i> Garments &amp; Haare anpassen'; } }
}

fn.initPropGarmentControls = initPropGarmentControls;
fn._syncPropGarmentControls = _syncPropGarmentControls;
fn._refitAllForCurrentChar = _refitAllForCurrentChar;
