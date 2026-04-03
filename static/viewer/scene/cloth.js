/**
 * Scene Editor -- Cloth UI (Template, Builder, Primitive).
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, _selectedInst, _charQueryParams, _bindSlider, _sliderVal } from './utils.js';
import { markDirty } from './undo.js';

export async function loadClothUI() {
    _bindSlider('cloth-tpl-segments', 'cloth-tpl-segments-val', v => v);
    _bindSlider('cloth-tpl-tightness', 'cloth-tpl-tightness-val', v => (v / 100).toFixed(2));
    _bindSlider('cloth-tpl-top-ext', 'cloth-tpl-top-ext-val', v => (v / 100).toFixed(2) + ' m');
    _bindSlider('cloth-tpl-bot-ext', 'cloth-tpl-bot-ext-val', v => (v / 100).toFixed(2) + ' m');
    _bindSlider('cloth-bld-looseness', 'cloth-bld-looseness-val', v => (v / 100).toFixed(2));
    _bindSlider('cloth-prim-segments', 'cloth-prim-segments-val', v => v);
    _bindSlider('cloth-prim-length', 'cloth-prim-length-val', v => (v / 100).toFixed(2));
    _bindSlider('cloth-prim-flare', 'cloth-prim-flare-val', v => (v / 100).toFixed(2));
    try {
        const resp = await fetch('/api/character/cloth/regions/');
        state._clothRegionsData = await resp.json();
        const tplSelect = document.getElementById('cloth-tpl-type');
        if (tplSelect && state._clothRegionsData.templates) { for (const t of state._clothRegionsData.templates) { const opt = document.createElement('option'); opt.value = t.key; opt.textContent = t.label; tplSelect.appendChild(opt); } }
        const bldSelect = document.getElementById('cloth-bld-region');
        if (bldSelect && state._clothRegionsData.builder_regions) { for (const r of state._clothRegionsData.builder_regions) { const opt = document.createElement('option'); opt.value = r.key; opt.textContent = r.label; bldSelect.appendChild(opt); } }
        const primSelect = document.getElementById('cloth-prim-type');
        if (primSelect && state._clothRegionsData.primitives) {
            for (const p of state._clothRegionsData.primitives) { const opt = document.createElement('option'); opt.value = p.key; opt.textContent = p.label; primSelect.appendChild(opt); }
            primSelect.addEventListener('change', () => { const flareRow = document.getElementById('cloth-prim-flare-row'); if (flareRow) flareRow.style.display = primSelect.value === 'PRIM_SKIRT' ? 'flex' : 'none'; });
        }
    } catch (e) { console.warn('Cloth UI not available:', e); }
    const tplCreate = document.getElementById('cloth-tpl-create');
    if (tplCreate) tplCreate.addEventListener('click', () => _doClothFromTemplate(false));
    const tplUpdate = document.getElementById('cloth-tpl-update');
    if (tplUpdate) tplUpdate.addEventListener('click', () => _doClothFromTemplate(true));
    const tplDelete = document.getElementById('cloth-tpl-delete');
    if (tplDelete) tplDelete.addEventListener('click', () => { const inst = _selectedInst(); if (!inst) return; const tpl = document.getElementById('cloth-tpl-type')?.value; if (!tpl) return; const key = `tpl_${tpl}`; if (inst.clothMeshes[key]) fn._removeSubMesh({ type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id }); });
    const removeAll = document.getElementById('cloth-remove-all');
    if (removeAll) removeAll.addEventListener('click', () => { const inst = _selectedInst(); if (!inst) return; Object.keys(inst.clothMeshes).filter(k => k.startsWith('tpl_')).forEach(key => fn._removeSubMesh({ type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id })); });
    const bldCreate = document.getElementById('cloth-bld-create');
    if (bldCreate) bldCreate.addEventListener('click', () => { const inst = _selectedInst(); if (!inst) return; const region = document.getElementById('cloth-bld-region')?.value || 'TOP'; _loadClothForCharacter(inst, `bld_${region}`, { method: 'builder', region, looseness: _sliderVal('cloth-bld-looseness') / 100 }); });
    const primCreate = document.getElementById('cloth-prim-create');
    if (primCreate) primCreate.addEventListener('click', () => { const inst = _selectedInst(); if (!inst) return; const pt = document.getElementById('cloth-prim-type')?.value || 'PRIM_SKIRT'; _loadClothForCharacter(inst, `prim_${pt}`, { method: 'primitive', prim_type: pt, segments: _sliderVal('cloth-prim-segments'), length: _sliderVal('cloth-prim-length') / 100, flare: _sliderVal('cloth-prim-flare') / 100 }); });
}

function _doClothFromTemplate(isUpdate) {
    const inst = _selectedInst(); if (!inst) return;
    const tpl = document.getElementById('cloth-tpl-type')?.value; if (!tpl) return;
    const key = `tpl_${tpl}`;
    if (isUpdate && !inst.clothMeshes[key]) return;
    _loadClothForCharacter(inst, key, { method: 'template', template: tpl, segments: _sliderVal('cloth-tpl-segments'), tightness: _sliderVal('cloth-tpl-tightness') / 100, top_extend: _sliderVal('cloth-tpl-top-ext') / 100, bottom_extend: _sliderVal('cloth-tpl-bot-ext') / 100 });
}

export async function _loadClothForCharacter(inst, key, clothParams) {
    const params = _charQueryParams(inst);
    for (const [k, v] of Object.entries(clothParams)) params.set(k, v);
    const colorHex = document.getElementById('cloth-color')?.value || '#404870';
    const matColor = new THREE.Color(colorHex);
    try {
        const resp = await fetch(`/api/character/cloth/?${params}`);
        const data = await resp.json();
        if (data.error) { console.warn('Cloth error:', data.error); return; }
        if (inst.clothMeshes[key]) { inst.group.remove(inst.clothMeshes[key]); inst.clothMeshes[key].geometry.dispose(); inst.clothMeshes[key].material.dispose(); delete inst.clothMeshes[key]; }
        const vertBuf = base64ToFloat32(data.vertices); blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces); const normalBuf = base64ToFloat32(data.normals); blenderToThreeCoords(normalBuf);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: matColor, roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide }));
        inst.clothMeshes[key] = mesh; inst.group.add(mesh);
        const clothEntry = { ...clothParams, color: colorHex };
        if (!inst.cloth) inst.cloth = [];
        const idx = inst.cloth.findIndex(c => { const m = c.method || 'template'; let ck; if (m === 'builder') ck = `bld_${c.region || 'TOP'}`; else if (m === 'primitive') ck = `prim_${c.prim_type || 'PRIM_SKIRT'}`; else ck = `tpl_${c.template || 'TPL_TSHIRT'}`; return ck === key; });
        if (idx >= 0) inst.cloth[idx] = clothEntry; else inst.cloth.push(clothEntry);
        fn.updateEquippedList(inst); fn.updateVertexCount(); markDirty();
    } catch (e) { console.error('Cloth load failed:', e); }
}

fn.loadClothUI = loadClothUI;
fn._loadClothForCharacter = _loadClothForCharacter;
