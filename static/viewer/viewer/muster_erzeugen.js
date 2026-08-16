/**
 * Aus dem Schnittmuster ein Netz erzeugen, speichern, laden.
 *
 * Aus pattern_editor.js herausgeloest (Umbau 16.08.2026).
 */
import { Musterzustand } from './muster_zustand.js';
import * as THREE from 'three';
import { _peAutoFit, _peSetModeButtons, pePreviewKey, peUpdatePanelList } from './pattern_editor.js';
import { buildBodyQueryString, sliderVal } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { fn } from '../gemeinsam/registrierung.js';
import { peRender } from './muster_zeichnen.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { peUpdateStitchList } from './pattern_editor.js';
import { removeClothRegion } from './cloth.js';
import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


export async function peRegionGenerate() {
    const genBtn = document.getElementById('pe-generate'); if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status'); if (statusEl) statusEl.textContent = 'Generating region...';
    ensureSkinned();
    const bodyQs = buildBodyQueryString();
    const zMin = (sliderVal('pe-region-zmin') / 100).toFixed(3); const zMax = (sliderVal('pe-region-zmax') / 100).toFixed(3);
    const arms = document.getElementById('pe-region-arms')?.checked ? '1' : '0'; const grow = sliderVal('pe-region-grow');
    const looseness = (sliderVal('pe-region-looseness') / 100).toFixed(3); const category = document.getElementById('pe-region-category')?.value || 'custom';
    const regionQs = `z_min=${zMin}&z_max=${zMax}&include_arms=${arms}&grow=${grow}&looseness=${looseness}&category=${category}`;
    try {
        const data = await Serverabruf.json(
            `/api/character/pattern/region/generate/?${bodyQs}&${regionQs}`);
        if (data.error) { if (statusEl) statusEl.textContent = `Error: ${data.error}`; if (genBtn) genBtn.disabled = false; return; }
        removeClothRegion(pePreviewKey);
        const vertBuf = base64ToFloat32(data.vertices); blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces); const normalBuf = base64ToFloat32(data.normals); blenderToThreeCoords(normalBuf);
        const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3)); geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        const colorPicker = document.getElementById('pe-color'); const matColor = colorPicker ? new THREE.Color(colorPicker.value) : new THREE.Color(0.3, 0.35, 0.5);
        const roughness = (sliderVal('pe-roughness') / 100); const metalness = (sliderVal('pe-metalness') / 100);
        const mat = new THREE.MeshStandardMaterial({ color: matColor, roughness, metalness, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
        let mesh;
        if (state.isSkinned && state.rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices); const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4)); geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat); mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        } else { mesh = new THREE.Mesh(geo, mat); }
        state.clothMeshes[pePreviewKey] = mesh; state.clothParams[pePreviewKey] = {params: {}, color: '#' + mesh.material.color.getHexString()};
        state.scene.add(mesh); fn.updateEquippedList();
        if (statusEl) statusEl.textContent = `Region: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
    if (genBtn) genBtn.disabled = false;
}

export async function peGenerate3D() {
    const genBtn = document.getElementById('pe-generate'); if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status'); if (statusEl) statusEl.textContent = 'Generating...';
    ensureSkinned();
    const bodyQs = buildBodyQueryString();
    try {
        const wrapCb = document.getElementById('pe-wrap'); const wrap = wrapCb ? wrapCb.checked : false;
        const wrapOffset = (sliderVal('pe-wrap-offset') || 6) / 1000; const wrapStiffness = (sliderVal('pe-wrap-stiffness') ?? 50) / 100;
        const data = await Serverabruf.senden(
            `/api/character/pattern/generate/?${bodyQs}`,
            { pattern: Musterzustand.pePattern, wrap, offset: wrapOffset,
              stiffness: wrapStiffness });
        if (data.error) { if (statusEl) statusEl.textContent = `Error: ${data.error}`; if (genBtn) genBtn.disabled = false; return; }
        removeClothRegion(pePreviewKey);
        const vertBuf = base64ToFloat32(data.vertices); blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces); const normalBuf = base64ToFloat32(data.normals); blenderToThreeCoords(normalBuf);
        const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3)); geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        const colorPicker = document.getElementById('pe-color'); const matColor = colorPicker ? new THREE.Color(colorPicker.value) : new THREE.Color(0.3, 0.35, 0.5);
        const roughness = (sliderVal('pe-roughness') / 100); const metalness = (sliderVal('pe-metalness') / 100);
        const mat = new THREE.MeshStandardMaterial({ color: matColor, roughness, metalness, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
        let mesh;
        if (state.isSkinned && state.rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices); const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4)); geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat); mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        } else { mesh = new THREE.Mesh(geo, mat); }
        state.clothMeshes[pePreviewKey] = mesh; state.clothParams[pePreviewKey] = {params: {}, color: '#' + mesh.material.color.getHexString()};
        state.scene.add(mesh); fn.updateEquippedList();
        if (statusEl) statusEl.textContent = `Generated: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
    if (genBtn) genBtn.disabled = false;
}

export async function peSaveToLibrary() {
    const name = document.getElementById('pe-save-name')?.value?.trim(); const category = document.getElementById('pe-save-category')?.value || 'custom';
    const statusEl = document.getElementById('pe-save-status'); if (!name) { if (statusEl) statusEl.textContent = 'Name is required'; return; }
    if (statusEl) statusEl.textContent = 'Saving...';
    const colorPicker = document.getElementById('pe-color'); const colorHex = colorPicker ? colorPicker.value : '#404870';
    const cr = parseInt(colorHex.slice(1, 3), 16) / 255; const cg = parseInt(colorHex.slice(3, 5), 16) / 255; const cb = parseInt(colorHex.slice(5, 7), 16) / 255;
    const bodyQs = buildBodyQueryString();
    try {
        const data = await Serverabruf.json(`/api/character/pattern/save/?${bodyQs}`, { method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pattern: Musterzustand.pePattern, name, category, color: [cr, cg, cb], roughness: sliderVal('pe-roughness') / 100, metalness: sliderVal('pe-metalness') / 100, wrap: document.getElementById('pe-wrap')?.checked || false, offset: (sliderVal('pe-wrap-offset') || 6) / 1000, stiffness: (sliderVal('pe-wrap-stiffness') ?? 50) / 100 }) });
        if (data.ok) { if (statusEl) statusEl.textContent = `Saved: ${data.garment_id}`; } else { if (statusEl) statusEl.textContent = `Error: ${data.error || 'Unknown'}`; }
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
}

export async function peLoadFromGarment(garmentId) {
    try {
        const data = await Serverabruf.json(`/api/character/pattern/specification/?garment_id=${encodeURIComponent(garmentId)}`);
        if (!data.ok || !data.pattern) { console.warn('No specification found for', garmentId, data.error); return false; }
        Musterzustand.pePattern = data.pattern; if (!Musterzustand.pePattern.stitches) Musterzustand.pePattern.stitches = [];
        const names = Object.keys(Musterzustand.pePattern.panels || {}); Musterzustand.peActivePanel = names.length > 0 ? names[0] : null;
        Musterzustand.peSelectedVertex = null; Musterzustand.peSelectedEdge = null; Musterzustand.peStitchFirst = null; Musterzustand.peMode = 'select'; _peSetModeButtons(); _peAutoFit();
        peUpdatePanelList(); peUpdateStitchList(); peRender();
        const tabBtn = document.querySelector('.panel-tab[data-tab="tab-creator"]'); if (tabBtn) tabBtn.click();
        const nameEl = document.getElementById('pe-save-name'); if (nameEl) { const parts = garmentId.split('/'); nameEl.value = parts[parts.length - 1]; }
        const catEl = document.getElementById('pe-save-category');
        if (catEl) { const parts = garmentId.split('/'); if (parts.length > 1) { const cat = parts[0]; for (const opt of catEl.options) { if (opt.value === cat) { catEl.value = cat; break; } } } }
        Protokoll.debug('Viewer', `Pattern loaded from ${garmentId}: ${names.length} panels`); return true;
    } catch (e) { console.error('Failed to load pattern:', e); return false; }
}
