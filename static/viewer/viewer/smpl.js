/**
 * Viewer — SMPL Body + SMPL Garment Library + Scene UI (Szene tab).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, bindSlider, sliderVal, setSlider } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { buildBodyFitQueryString } from './garment.js';
import { VIEWER_TONE_MAPPINGS } from './scene_settings.js';

// =========================================================================
// SMPL Garment Library
// =========================================================================
export async function loadSmplGarmentUI() {
    const panel = document.getElementById('garment-smpl-panel');
    if (!panel) return;
    bindSlider('smpl-garment-roughness', 'smpl-garment-roughness-val', v => (v / 100).toFixed(2));
    const colorEl = document.getElementById('smpl-garment-color');
    if (colorEl) colorEl.addEventListener('input', () => { if (!state._smplSelectedId || !state.smplGarmentMeshes[state._smplSelectedId]) return; state.smplGarmentMeshes[state._smplSelectedId].material.color.set(colorEl.value); });
    const roughEl = document.getElementById('smpl-garment-roughness');
    if (roughEl) roughEl.addEventListener('input', () => { if (!state._smplSelectedId || !state.smplGarmentMeshes[state._smplSelectedId]) return; state.smplGarmentMeshes[state._smplSelectedId].material.roughness = roughEl.value / 100; });
    const loadBtn = document.getElementById('smpl-garment-load');
    if (loadBtn) loadBtn.addEventListener('click', () => { if (!state._smplSelectedId) return; loadSmplGarment(state._smplSelectedId); });
    const removeBtn = document.getElementById('smpl-garment-remove');
    if (removeBtn) removeBtn.addEventListener('click', () => { if (state._smplSelectedId && state.smplGarmentMeshes[state._smplSelectedId]) removeSmplGarment(state._smplSelectedId); });
    const removeAllBtn = document.getElementById('smpl-garment-remove-all');
    if (removeAllBtn) removeAllBtn.addEventListener('click', removeAllSmplGarments);
    const catSelect = document.getElementById('smpl-garment-category');
    if (catSelect) catSelect.addEventListener('change', () => _renderSmplGarmentList());
    try {
        const resp = await fetch('/api/smpl/garment/library/'); const data = await resp.json(); state._smplCatalog = [];
        if (catSelect && data.categories) data.categories.forEach(cat => { const opt = document.createElement('option'); opt.value = cat; opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1); catSelect.appendChild(opt); });
        if (data.garments) { for (const cat of Object.keys(data.garments)) for (const g of data.garments[cat]) state._smplCatalog.push(g); }
        _renderSmplGarmentList();
    } catch (e) { console.error('[SMPL] Error loading library:', e); }
}

function _renderSmplGarmentList() {
    const listEl = document.getElementById('smpl-garment-list'); const catSelect = document.getElementById('smpl-garment-category'); if (!listEl) return;
    const filterCat = catSelect ? catSelect.value : ''; const filtered = filterCat ? state._smplCatalog.filter(g => g.category === filterCat) : state._smplCatalog;
    if (filtered.length === 0) { listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine SMPL-Garments gefunden</div>'; return; }
    const byCat = {}; for (const g of filtered) { if (!byCat[g.category]) byCat[g.category] = []; byCat[g.category].push(g); }
    listEl.innerHTML = '';
    for (const cat of Object.keys(byCat).sort()) {
        const catDiv = document.createElement('div'); catDiv.className = 'anim-category';
        const header = document.createElement('div'); header.className = 'anim-category-header';
        header.innerHTML = `<span class="cat-chevron">&#9654;</span> ${cat.toUpperCase()} <span class="cat-count">${byCat[cat].length}</span>`;
        header.addEventListener('click', () => catDiv.classList.toggle('open')); catDiv.appendChild(header);
        const body = document.createElement('div'); body.className = 'anim-category-body';
        for (const g of byCat[cat]) {
            const item = document.createElement('div'); item.className = 'anim-item'; if (g.id === state._smplSelectedId) item.classList.add('active');
            if (g.has_thumb) { const img = document.createElement('img'); img.src = `/api/smpl/garment/thumb/${g.id}/`; img.alt = g.name; img.loading = 'lazy'; img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;margin-right:6px;'; item.appendChild(img); }
            const nameSpan = document.createElement('span'); nameSpan.textContent = g.name; nameSpan.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'; item.appendChild(nameSpan);
            if (state.smplGarmentMeshes[g.id]) { const badge = document.createElement('span'); badge.textContent = '\u2713'; badge.style.cssText = 'color:var(--success);margin-left:4px;'; item.appendChild(badge); }
            item.style.cssText += 'display:flex;align-items:center;padding:4px 12px 4px 28px;';
            item.addEventListener('click', () => { state._smplSelectedId = g.id; listEl.querySelectorAll('.anim-item').forEach(el => el.classList.remove('active')); item.classList.add('active'); if (state.smplGarmentMeshes[g.id]) { const mat = state.smplGarmentMeshes[g.id].material; const c = '#' + mat.color.getHexString(); const cp = document.getElementById('smpl-garment-color'); if (cp) cp.value = c; setSlider('smpl-garment-roughness', Math.round(mat.roughness * 100), v => (v / 100).toFixed(2)); } });
            item.addEventListener('dblclick', () => { state._smplSelectedId = g.id; loadSmplGarment(g.id); });
            body.appendChild(item);
        }
        catDiv.appendChild(body); listEl.appendChild(catDiv);
    }
}

async function loadSmplGarment(garmentId) {
    const loadBtn = document.getElementById('smpl-garment-load'); if (loadBtn) { loadBtn.disabled = true; loadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Laden...'; }
    try {
        const resp = await fetch(`/api/smpl/garment/mesh/?garment_id=${encodeURIComponent(garmentId)}`); const data = await resp.json();
        if (data.error) { console.error('SMPL garment load error:', data.error); return; }
        removeSmplGarment(garmentId);
        const vertBuf = base64ToFloat32(data.vertices); const faceBuf = base64ToUint32(data.faces); const normBuf = base64ToFloat32(data.normals);
        const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3)); geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.setAttribute('normal', new THREE.BufferAttribute(normBuf, 3));
        const colorEl = document.getElementById('smpl-garment-color'); const roughEl = document.getElementById('smpl-garment-roughness');
        const color = colorEl ? colorEl.value : '#4d8066'; const roughness = roughEl ? roughEl.value / 100 : 0.8;
        const mat = new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.0, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnit: -1 });
        const mesh = new THREE.Mesh(geo, mat); mesh.name = `smpl_garment_${garmentId}`;
        if (state.smplBodyMesh) { mesh.position.copy(state.smplBodyMesh.position); mesh.rotation.copy(state.smplBodyMesh.rotation); const posAttr = state.smplBodyMesh.geometry.getAttribute('position'); let sumY = 0; for (let i = 0; i < posAttr.count; i++) sumY += posAttr.getY(i); mesh.position.y = sumY / posAttr.count; }
        else { const xOffsetEl = document.getElementById('smpl-body-xoffset'); mesh.position.x = xOffsetEl ? xOffsetEl.value / 100 : 1.0; mesh.position.y = 0.86; mesh.rotation.y = Math.PI; }
        state.smplGarmentMeshes[garmentId] = mesh; state.scene.add(mesh);
        console.log(`SMPL garment loaded: ${garmentId} (${data.vertex_count} verts)`);
        _renderSmplGarmentList();
        if (state.bodyMesh && state.rigifySkeleton) _fitSmplGarmentToBody(garmentId);
    } catch (e) { console.error('Failed to load SMPL garment:', e); }
    finally { if (loadBtn) { loadBtn.disabled = false; loadBtn.innerHTML = '<i class="fas fa-plus"></i> Laden'; } }
}

async function _fitSmplGarmentToBody(garmentId) {
    const fitKey = 'smpl:' + garmentId;
    try {
        ensureSkinned();
        const bodySelect = document.getElementById('body-type-select'); const bodyType = bodySelect ? bodySelect.value : 'Female_Caucasian';
        let bodyQs;
        if (document.getElementById('garment-offset')) bodyQs = buildBodyFitQueryString();
        else { bodyQs = `body_type=${encodeURIComponent(bodyType)}`; document.querySelectorAll('#morphs-panel input[type="range"]').forEach(slider => { const mName = slider.dataset.morph || slider.dataset.morphName || slider.id.replace('morph-', ''); if (mName && slider.value !== undefined) bodyQs += `&morph_${mName}=${slider.value / 100}`; }); ['age','mass','tone','height'].forEach(m => { const el = document.getElementById(`meta-${m}`); if (el) { const dv = parseInt(el.value); const mn = parseInt(el.min), mx = parseInt(el.max); const neutral = (mn + mx) / 2; const half = (mx - mn) / 2; const internal = half ? (dv - neutral) / half : 0; bodyQs += `&meta_${m}=${internal}`; } }); }
        const colorEl = document.getElementById('smpl-garment-color'); const colorHex = colorEl ? colorEl.value : '#4d8066';
        const cr = parseInt(colorHex.slice(1, 3), 16) / 255; const cg = parseInt(colorHex.slice(3, 5), 16) / 255; const cb = parseInt(colorHex.slice(5, 7), 16) / 255;
        const qs = `garment_id=${encodeURIComponent(garmentId)}&${bodyQs}&color_r=${cr.toFixed(3)}&color_g=${cg.toFixed(3)}&color_b=${cb.toFixed(3)}`;
        const resp = await fetch(`/api/smpl/garment/fit/?${qs}`); const data = await resp.json();
        if (data.error) { console.error('SMPL garment fit error:', data.error); return; }
        const prev = state.garmentMeshes[fitKey]; if (prev) { state.scene.remove(prev); prev.geometry.dispose(); prev.material.dispose(); delete state.garmentMeshes[fitKey]; }
        const vertBuf = base64ToFloat32(data.vertices); blenderToThreeCoords(vertBuf); const faceBuf = base64ToUint32(data.faces);
        const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3)); geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.computeVertexNormals();
        const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
        const mat = new THREE.MeshStandardMaterial({ color: matColor, roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnit: -1 });
        let mesh;
        if (state.isSkinned && state.rigifySkeleton && data.skin_indices && data.skin_weights) { const siBuf = base64ToFloat32(data.skin_indices); const swBuf = base64ToFloat32(data.skin_weights); geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4)); geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4)); mesh = new THREE.SkinnedMesh(geo, mat); mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix); }
        else { mesh = new THREE.Mesh(geo, mat); }
        mesh.name = `smpl_garment_fit_${garmentId}`; state.garmentMeshes[fitKey] = mesh; state.scene.add(mesh);
    } catch (e) { console.error('Failed to fit SMPL garment to body:', e); }
}

export function removeSmplGarment(garmentId) {
    const mesh = state.smplGarmentMeshes[garmentId]; if (mesh) { state.scene.remove(mesh); mesh.geometry.dispose(); mesh.material.dispose(); delete state.smplGarmentMeshes[garmentId]; }
    const fitKey = 'smpl:' + garmentId; const fitMesh = state.garmentMeshes[fitKey]; if (fitMesh) { state.scene.remove(fitMesh); fitMesh.geometry.dispose(); fitMesh.material.dispose(); delete state.garmentMeshes[fitKey]; }
}

function removeAllSmplGarments() { for (const id of Object.keys(state.smplGarmentMeshes)) removeSmplGarment(id); _renderSmplGarmentList(); }

// =========================================================================
// SMPL Body UI
// =========================================================================
let _smplBodyUpdateTimer = null;

function _getSmplBetas() { const sliders = document.querySelectorAll('.smpl-beta-slider'); const betas = []; sliders.forEach(s => { betas[parseInt(s.dataset.index)] = s.value / 100; }); return betas; }
function _getSmplGender() { const sel = document.getElementById('smpl-body-gender'); return sel ? sel.value : 'female'; }
function _scheduleSmplBodyUpdate() { if (_smplBodyUpdateTimer) clearTimeout(_smplBodyUpdateTimer); _smplBodyUpdateTimer = setTimeout(() => { _smplBodyUpdateTimer = null; loadSmplBody(); }, 100); }

function _updateSmplBodyInfo() {
    const infoSection = document.getElementById('smpl-body-info-section'); const infoDiv = document.getElementById('smpl-body-info');
    if (!infoSection || !infoDiv) return;
    if (!state.smplBodyMesh) { infoSection.style.display = 'none'; return; }
    infoSection.style.display = ''; const gender = _getSmplGender(); const betas = _getSmplBetas();
    const geo = state.smplBodyMesh.geometry; const vCount = geo.getAttribute('position').count; const fCount = geo.index ? geo.index.count / 3 : 0;
    const betaNames = ['Height','Weight','Proportions','Torso','Chest','Hips','Waist','Limbs','Arms','Legs'];
    const nonZero = betas.filter(b => Math.abs(b) > 0.005);
    const betaStr = nonZero.length > 0 ? betas.map((b, i) => Math.abs(b) > 0.005 ? `${betaNames[i]}=${b.toFixed(2)}` : null).filter(Boolean).join(', ') : 'Default shape';
    infoDiv.innerHTML = `Gender: <b>${gender}</b> | Vertices: <b>${vCount.toLocaleString()}</b> | Faces: <b>${fCount.toLocaleString()}</b><br>${betaStr}`;
}

export async function initSmplBodyUI() {
    const panel = document.getElementById('smpl-body-panel'); if (!panel) return;
    const betaSliders = document.querySelectorAll('.smpl-beta-slider'); const betaVals = document.querySelectorAll('.smpl-beta-val');
    betaSliders.forEach((slider, i) => { slider.addEventListener('input', () => { betaVals[i].textContent = (slider.value / 100).toFixed(2); _scheduleSmplBodyUpdate(); }); });
    const genderSel = document.getElementById('smpl-body-gender'); if (genderSel) genderSel.addEventListener('change', () => loadSmplBody());
    const resetBtn = document.getElementById('smpl-beta-reset');
    if (resetBtn) resetBtn.addEventListener('click', () => { betaSliders.forEach((s, i) => { s.value = 0; betaVals[i].textContent = '0.00'; }); _scheduleSmplBodyUpdate(); });
    const opacityEl = document.getElementById('smpl-body-opacity'); const opacityVal = document.getElementById('smpl-body-opacity-val');
    if (opacityEl) opacityEl.addEventListener('input', () => { const v = opacityEl.value / 100; if (opacityVal) opacityVal.textContent = v.toFixed(2); if (state.smplBodyMesh) state.smplBodyMesh.material.opacity = v; });
    const colorEl = document.getElementById('smpl-body-color'); if (colorEl) colorEl.addEventListener('input', () => { if (state.smplBodyMesh) state.smplBodyMesh.material.color.set(colorEl.value); });
    const wireEl = document.getElementById('smpl-body-wireframe'); if (wireEl) wireEl.addEventListener('change', () => { if (state.smplBodyMesh) { state.smplBodyMesh.material.wireframe = wireEl.checked; state.smplBodyMesh.material.depthWrite = !wireEl.checked; } });
    const xOffsetEl = document.getElementById('smpl-body-xoffset'); const xOffsetVal = document.getElementById('smpl-body-xoffset-val');
    if (xOffsetEl) xOffsetEl.addEventListener('input', () => { const v = xOffsetEl.value / 100; if (xOffsetVal) xOffsetVal.textContent = v.toFixed(2) + ' m'; if (state.smplBodyMesh) state.smplBodyMesh.position.x = v; for (const m of Object.values(state.smplGarmentMeshes)) m.position.x = v; });
    const toggle = document.getElementById('smpl-body-toggle');
    if (toggle) toggle.addEventListener('click', () => { if (!state.smplBodyMesh) return; state.smplBodyVisible = !state.smplBodyVisible; state.smplBodyMesh.visible = state.smplBodyVisible; toggle.classList.toggle('active', state.smplBodyVisible); });

    try {
        const resp = await fetch('/api/settings/smpl/'); const cfg = await resp.json();
        if (genderSel && cfg.gender) genderSel.value = cfg.gender;
        if (cfg.betas && cfg.betas.length === 10) betaSliders.forEach((s, i) => { s.value = Math.round(cfg.betas[i] * 100); betaVals[i].textContent = cfg.betas[i].toFixed(2); });
        if (opacityEl && cfg.opacity != null) { opacityEl.value = Math.round(cfg.opacity * 100); if (opacityVal) opacityVal.textContent = cfg.opacity.toFixed(2); }
        if (colorEl && cfg.color) colorEl.value = cfg.color;
        if (wireEl && cfg.wireframe != null) wireEl.checked = cfg.wireframe;
        if (xOffsetEl && cfg.xoffset != null) { xOffsetEl.value = Math.round(cfg.xoffset * 100); if (xOffsetVal) xOffsetVal.textContent = cfg.xoffset.toFixed(2) + ' m'; }
        if (cfg.scene) _applySmplSceneSettings(cfg.scene);
    } catch (e) { console.warn('Could not load SMPL defaults:', e); }
    initSceneUI();
    const saveBtn = document.getElementById('smpl-save-settings'); if (saveBtn) saveBtn.addEventListener('click', () => _saveSmplSettings());
    loadSmplBody();
}

async function loadSmplBody() {
    const gender = _getSmplGender(); const betas = _getSmplBetas(); const betaStr = betas.join(',');
    try {
        const resp = await fetch(`/api/smpl/body/?gender=${gender}&betas=${betaStr}`); const data = await resp.json();
        if (data.error) { console.warn('SMPL body error:', data.error); return; }
        const vertBuf = base64ToFloat32(data.vertices); const normBuf = base64ToFloat32(data.normals);
        if (state.smplBodyMesh) {
            const posAttr = state.smplBodyMesh.geometry.getAttribute('position'); posAttr.array.set(vertBuf); posAttr.needsUpdate = true;
            const normAttr = state.smplBodyMesh.geometry.getAttribute('normal'); normAttr.array.set(normBuf); normAttr.needsUpdate = true; state.smplBodyMesh.geometry.computeBoundingSphere();
        } else {
            const faceBuf = base64ToUint32(data.faces); const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3)); geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.setAttribute('normal', new THREE.BufferAttribute(normBuf, 3));
            const opacityEl = document.getElementById('smpl-body-opacity'); const colorEl = document.getElementById('smpl-body-color'); const wireEl = document.getElementById('smpl-body-wireframe'); const xOffsetEl = document.getElementById('smpl-body-xoffset');
            const isWire = wireEl ? wireEl.checked : false;
            const mat = new THREE.MeshStandardMaterial({ color: colorEl ? colorEl.value : 0x88aaff, transparent: true, opacity: opacityEl ? opacityEl.value / 100 : 1.0, wireframe: isWire, side: THREE.DoubleSide, depthWrite: !isWire });
            state.smplBodyMesh = new THREE.Mesh(geo, mat); state.smplBodyMesh.name = 'smpl_body'; state.smplBodyMesh.rotation.y = Math.PI;
            state.smplBodyMesh.position.x = xOffsetEl ? xOffsetEl.value / 100 : 1.0; state.smplBodyVisible = true; state.scene.add(state.smplBodyMesh);
            const toggle = document.getElementById('smpl-body-toggle'); if (toggle) toggle.classList.add('active');
        }
        _updateSmplBodyInfo();
    } catch (e) { console.error('Failed to load SMPL body:', e); }
}

// =========================================================================
// Scene UI
// =========================================================================
const SMPL_LIGHT_PRESETS = {
    studio:   { key: {intensity:3.0,color:'#ffffff',pos:[2,4,-5]}, fill: {intensity:2.0,color:'#eeeeff',pos:[-3,3,-4]}, back: {intensity:2.5,color:'#ffeedd',pos:[0,4,5]}, ambient: {intensity:0.8,color:'#ffffff'}, exposure:1.6 },
    outdoor:  { key: {intensity:4.0,color:'#fff5e0',pos:[5,8,-2]}, fill: {intensity:1.5,color:'#8899cc',pos:[-4,2,-3]}, back: {intensity:1.0,color:'#ffeedd',pos:[-2,3,4]}, ambient: {intensity:1.2,color:'#ddeeff'}, exposure:1.8 },
    dramatic: { key: {intensity:4.5,color:'#ffddaa',pos:[4,3,-3]}, fill: {intensity:0.5,color:'#4444aa',pos:[-3,1,-2]}, back: {intensity:3.0,color:'#ff8844',pos:[0,3,5]}, ambient: {intensity:0.3,color:'#222244'}, exposure:1.4 },
    neutral:  { key: {intensity:2.5,color:'#ffffff',pos:[3,5,-4]}, fill: {intensity:2.5,color:'#ffffff',pos:[-3,5,-4]}, back: {intensity:2.0,color:'#ffffff',pos:[0,4,5]}, ambient: {intensity:1.0,color:'#ffffff'}, exposure:1.6 }
};

function _applyLightPreset(preset) {
    if (preset.key) { state.keyLight.intensity = preset.key.intensity; state.keyLight.color.set(preset.key.color); state.keyLight.position.set(...preset.key.pos); }
    if (preset.fill) { state.fillLight.intensity = preset.fill.intensity; state.fillLight.color.set(preset.fill.color); state.fillLight.position.set(...preset.fill.pos); }
    if (preset.back) { state.backLight.intensity = preset.back.intensity; state.backLight.color.set(preset.back.color); state.backLight.position.set(...preset.back.pos); }
    if (preset.ambient) { state.ambient.intensity = preset.ambient.intensity; state.ambient.color.set(preset.ambient.color); }
    if (preset.exposure !== undefined) state.renderer.toneMappingExposure = preset.exposure;
}

function _syncSceneUI() {
    _syncLightGroupUI('key', state.keyLight); _syncLightGroupUI('fill', state.fillLight); _syncLightGroupUI('back', state.backLight);
    const ambInt = document.getElementById('scene-ambient-intensity'); const ambCol = document.getElementById('scene-ambient-color');
    if (ambInt) { ambInt.value = Math.round(state.ambient.intensity * 100); const v = document.getElementById('scene-ambient-intensity-val'); if (v) v.textContent = state.ambient.intensity.toFixed(2); }
    if (ambCol) ambCol.value = '#' + state.ambient.color.getHexString();
    const tmSel = document.getElementById('scene-tonemapping'); if (tmSel) { for (const [name, val] of Object.entries(VIEWER_TONE_MAPPINGS)) { if (state.renderer.toneMapping === val) { tmSel.value = name; break; } } }
    const expEl = document.getElementById('scene-exposure'); if (expEl) { expEl.value = Math.round(state.renderer.toneMappingExposure * 100); const v = document.getElementById('scene-exposure-val'); if (v) v.textContent = state.renderer.toneMappingExposure.toFixed(2); }
    const bgEl = document.getElementById('scene-background'); if (bgEl && state.scene.background) bgEl.value = '#' + state.scene.background.getHexString();
    const fovEl = document.getElementById('scene-fov'); if (fovEl) { fovEl.value = state.camera.fov; const v = document.getElementById('scene-fov-val'); if (v) v.textContent = Math.round(state.camera.fov) + '\u00B0'; }
}

function _syncLightGroupUI(name, light) {
    const intEl = document.getElementById(`scene-${name}-intensity`); const colEl = document.getElementById(`scene-${name}-color`);
    if (intEl) { intEl.value = Math.round(light.intensity * 100); const v = document.getElementById(`scene-${name}-intensity-val`); if (v) v.textContent = light.intensity.toFixed(2); }
    if (colEl) colEl.value = '#' + light.color.getHexString();
    ['x','y','z'].forEach(axis => { const el = document.getElementById(`scene-${name}-pos-${axis}`); if (el) { el.value = light.position[axis]; const v = document.getElementById(`scene-${name}-pos-${axis}-val`); if (v) v.textContent = light.position[axis].toFixed(1); } });
}

function _bindLightGroup(name, light) {
    const intEl = document.getElementById(`scene-${name}-intensity`); const colEl = document.getElementById(`scene-${name}-color`);
    if (intEl) intEl.addEventListener('input', () => { const v = intEl.value / 100; light.intensity = v; const valEl = document.getElementById(`scene-${name}-intensity-val`); if (valEl) valEl.textContent = v.toFixed(2); });
    if (colEl) colEl.addEventListener('input', () => light.color.set(colEl.value));
    ['x','y','z'].forEach(axis => { const el = document.getElementById(`scene-${name}-pos-${axis}`); if (el) el.addEventListener('input', () => { const v = parseFloat(el.value); light.position[axis] = v; const valEl = document.getElementById(`scene-${name}-pos-${axis}-val`); if (valEl) valEl.textContent = v.toFixed(1); }); });
}

function initSceneUI() {
    const pane = document.getElementById('tab-szene'); if (!pane) return;
    const presetSel = document.getElementById('scene-light-preset'); if (presetSel) presetSel.addEventListener('change', () => { const preset = SMPL_LIGHT_PRESETS[presetSel.value]; if (preset) { _applyLightPreset(preset); _syncSceneUI(); } });
    _bindLightGroup('key', state.keyLight); _bindLightGroup('fill', state.fillLight); _bindLightGroup('back', state.backLight);
    const ambIntEl = document.getElementById('scene-ambient-intensity'); if (ambIntEl) ambIntEl.addEventListener('input', () => { const v = ambIntEl.value / 100; state.ambient.intensity = v; const valEl = document.getElementById('scene-ambient-intensity-val'); if (valEl) valEl.textContent = v.toFixed(2); });
    const ambColEl = document.getElementById('scene-ambient-color'); if (ambColEl) ambColEl.addEventListener('input', () => state.ambient.color.set(ambColEl.value));
    const tmSel = document.getElementById('scene-tonemapping'); if (tmSel) tmSel.addEventListener('change', () => { if (VIEWER_TONE_MAPPINGS[tmSel.value] !== undefined) state.renderer.toneMapping = VIEWER_TONE_MAPPINGS[tmSel.value]; });
    const expEl = document.getElementById('scene-exposure'); if (expEl) expEl.addEventListener('input', () => { const v = expEl.value / 100; state.renderer.toneMappingExposure = v; const valEl = document.getElementById('scene-exposure-val'); if (valEl) valEl.textContent = v.toFixed(2); });
    const bgEl = document.getElementById('scene-background'); if (bgEl) bgEl.addEventListener('input', () => state.scene.background.set(bgEl.value));
    const fovEl = document.getElementById('scene-fov'); if (fovEl) fovEl.addEventListener('input', () => { state.camera.fov = parseFloat(fovEl.value); state.camera.updateProjectionMatrix(); const valEl = document.getElementById('scene-fov-val'); if (valEl) valEl.textContent = fovEl.value + '\u00B0'; });
    const resetBtn = document.getElementById('scene-reset-lighting');
    if (resetBtn) resetBtn.addEventListener('click', () => { _applyLightPreset(SMPL_LIGHT_PRESETS.studio); state.renderer.toneMapping = THREE.ACESFilmicToneMapping; state.renderer.toneMappingExposure = 1.6; state.scene.background.set(0x1a1a2e); state.camera.fov = 35; state.camera.updateProjectionMatrix(); _syncSceneUI(); if (presetSel) presetSel.value = 'studio'; });
    _syncSceneUI();
}

function _gatherSceneSettings() {
    return { lighting: { key: {intensity:state.keyLight.intensity,color:'#'+state.keyLight.color.getHexString(),pos:[state.keyLight.position.x,state.keyLight.position.y,state.keyLight.position.z]}, fill: {intensity:state.fillLight.intensity,color:'#'+state.fillLight.color.getHexString(),pos:[state.fillLight.position.x,state.fillLight.position.y,state.fillLight.position.z]}, back: {intensity:state.backLight.intensity,color:'#'+state.backLight.color.getHexString(),pos:[state.backLight.position.x,state.backLight.position.y,state.backLight.position.z]}, ambient: {intensity:state.ambient.intensity,color:'#'+state.ambient.color.getHexString()} }, renderer: { toneMapping: (() => { for (const [name, val] of Object.entries(VIEWER_TONE_MAPPINGS)) { if (state.renderer.toneMapping === val) return name; } return 'ACESFilmic'; })(), exposure: state.renderer.toneMappingExposure, background: '#' + (state.scene.background ? state.scene.background.getHexString() : '1a1a2e') }, camera: { fov: state.camera.fov } };
}

function _applySmplSceneSettings(s) {
    if (!s || typeof s !== 'object') return;
    if (s.lighting) { if (s.lighting.key) { state.keyLight.intensity = s.lighting.key.intensity; state.keyLight.color.set(s.lighting.key.color); state.keyLight.position.set(...s.lighting.key.pos); } if (s.lighting.fill) { state.fillLight.intensity = s.lighting.fill.intensity; state.fillLight.color.set(s.lighting.fill.color); state.fillLight.position.set(...s.lighting.fill.pos); } if (s.lighting.back) { state.backLight.intensity = s.lighting.back.intensity; state.backLight.color.set(s.lighting.back.color); state.backLight.position.set(...s.lighting.back.pos); } if (s.lighting.ambient) { state.ambient.intensity = s.lighting.ambient.intensity; state.ambient.color.set(s.lighting.ambient.color); } }
    if (s.renderer) { if (s.renderer.toneMapping && VIEWER_TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) state.renderer.toneMapping = VIEWER_TONE_MAPPINGS[s.renderer.toneMapping]; if (s.renderer.exposure !== undefined) state.renderer.toneMappingExposure = s.renderer.exposure; if (s.renderer.background) state.scene.background.set(s.renderer.background); }
    if (s.camera && s.camera.fov) { state.camera.fov = s.camera.fov; state.camera.updateProjectionMatrix(); }
    _syncSceneUI();
}

async function _saveSmplSettings() {
    const btn = document.getElementById('smpl-save-settings'); const genderSel = document.getElementById('smpl-body-gender');
    const opacityEl = document.getElementById('smpl-body-opacity'); const colorEl = document.getElementById('smpl-body-color');
    const wireEl = document.getElementById('smpl-body-wireframe'); const xOffsetEl = document.getElementById('smpl-body-xoffset');
    const body = { gender: genderSel ? genderSel.value : 'female', betas: _getSmplBetas(), opacity: opacityEl ? opacityEl.value / 100 : 1.0, color: colorEl ? colorEl.value : '#88aaff', wireframe: wireEl ? wireEl.checked : false, xoffset: xOffsetEl ? xOffsetEl.value / 100 : 1.0, scene: _gatherSceneSettings() };
    try {
        if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Speichern...'; }
        const resp = await fetch('/api/settings/smpl/save/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const data = await resp.json();
        if (data.ok) { if (btn) { btn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!'; btn.style.borderColor = 'var(--success)'; } setTimeout(() => { if (btn) { btn.innerHTML = '<i class="fas fa-save"></i> Einstellungen speichern'; btn.style.borderColor = ''; btn.disabled = false; } }, 2000); }
        else throw new Error(data.error || 'Save failed');
    } catch (e) { console.error('Failed to save SMPL settings:', e); if (btn) { btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Fehler!'; btn.disabled = false; } setTimeout(() => { if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Einstellungen speichern'; }, 2000); }
}

fn.loadSmplGarmentUI = loadSmplGarmentUI;
fn.initSmplBodyUI = initSmplBodyUI;
fn.removeSmplGarment = removeSmplGarment;
