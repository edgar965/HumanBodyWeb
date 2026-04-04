/**
 * Viewer — Cloth UI (template/builder/primitive cloth generation).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, bindSlider, sliderVal } from './utils.js';
import { ensureSkinned } from './skinning.js';

export async function loadClothUI() {
    try {
        const resp = await fetch('/api/character/cloth/regions/');
        const data = await resp.json();

        // --- Template UI ---
        const tplSelect = document.getElementById('cloth-tpl-type');
        if (tplSelect) {
            (data.templates || []).forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.key;
                opt.textContent = t.label;
                tplSelect.appendChild(opt);
            });
        }

        bindSlider('cloth-tpl-segments', 'cloth-tpl-segments-val', v => v);
        bindSlider('cloth-tpl-tightness', 'cloth-tpl-tightness-val', v => (v / 100).toFixed(2));
        bindSlider('cloth-tpl-top-ext', 'cloth-tpl-top-ext-val', v => (v / 100).toFixed(2) + ' m');
        bindSlider('cloth-tpl-bot-ext', 'cloth-tpl-bot-ext-val', v => (v / 100).toFixed(2) + ' m');

        function _tplParams() {
            const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
            return {
                key: `tpl_${tpl}`,
                params: {
                    method: 'template', template: tpl,
                    segments: sliderVal('cloth-tpl-segments'),
                    tightness: sliderVal('cloth-tpl-tightness') / 100,
                    top_extend: sliderVal('cloth-tpl-top-ext') / 100,
                    bottom_extend: sliderVal('cloth-tpl-bot-ext') / 100,
                },
            };
        }

        // --- Template Preset UI ---
        const TPL_CATEGORY = {
            TPL_TSHIRT: 'Top', TPL_DRESS: 'Top',
            TPL_PANTS: 'Pants', TPL_SKIRT: 'Pants',
        };
        const presetSelect = document.getElementById('cloth-tpl-preset');

        async function refreshClothPresets() {
            if (!presetSelect || !tplSelect) return;
            const cat = TPL_CATEGORY[tplSelect.value] || 'Top';
            try {
                const r = await fetch(`/api/character/cloth/presets/?category=${cat}`);
                const d = await r.json();
                while (presetSelect.options.length > 1) presetSelect.remove(1);
                (d.presets || []).forEach(p => {
                    const o = document.createElement('option');
                    o.value = p.name;
                    o.textContent = p.name;
                    presetSelect.appendChild(o);
                });
            } catch (e) {
                console.warn('Failed to load cloth presets:', e);
            }
        }

        if (tplSelect) {
            tplSelect.addEventListener('change', () => refreshClothPresets());
            refreshClothPresets();
        }

        async function _saveClothPreset(name) {
            const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
            const colorPicker = document.getElementById('cloth-color');
            const presetData = {
                template: tpl,
                segments: sliderVal('cloth-tpl-segments'),
                tightness: sliderVal('cloth-tpl-tightness') / 100,
                top_extend: sliderVal('cloth-tpl-top-ext') / 100,
                bottom_extend: sliderVal('cloth-tpl-bot-ext') / 100,
                color: colorPicker ? colorPicker.value : '#404870',
            };
            try {
                const r = await fetch('/api/character/cloth/presets/save/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, data: presetData }),
                });
                const res = await r.json();
                if (res.ok) {
                    await refreshClothPresets();
                    const safeName = res.filename.replace('.json', '');
                    if (presetSelect) presetSelect.value = safeName;
                    console.log('Cloth preset saved:', res.filename);
                    return true;
                } else {
                    alert('Fehler: ' + (res.error || 'Unbekannt'));
                }
            } catch (e) {
                alert('Fehler: ' + e.message);
            }
            return false;
        }

        const presetSaveBtn = document.getElementById('cloth-tpl-preset-save');
        if (presetSaveBtn) {
            presetSaveBtn.addEventListener('click', async () => {
                let name = presetSelect ? presetSelect.value : '';
                if (!name) {
                    name = prompt('Preset-Name:');
                    if (!name || !name.trim()) return;
                    name = name.trim();
                }
                await _saveClothPreset(name);
            });
        }

        const presetSaveAsBtn = document.getElementById('cloth-tpl-preset-saveas');
        if (presetSaveAsBtn) {
            presetSaveAsBtn.addEventListener('click', async () => {
                const suggested = presetSelect ? presetSelect.value : '';
                const name = prompt('Preset-Name:', suggested);
                if (!name || !name.trim()) return;
                await _saveClothPreset(name.trim());
            });
        }

        const presetLoadBtn = document.getElementById('cloth-tpl-preset-load');
        if (presetLoadBtn) {
            presetLoadBtn.addEventListener('click', async () => {
                if (!presetSelect || !presetSelect.value) return;
                const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
                const cat = TPL_CATEGORY[tpl] || 'Top';
                try {
                    const r = await fetch(`/api/character/cloth/presets/${cat}/${encodeURIComponent(presetSelect.value)}/`);
                    const d = await r.json();
                    if (d.error) { alert(d.error); return; }
                    if (d.template && tplSelect) tplSelect.value = d.template;
                    const seg = document.getElementById('cloth-tpl-segments');
                    const segVal = document.getElementById('cloth-tpl-segments-val');
                    if (seg && d.segments !== undefined) { seg.value = d.segments; if (segVal) segVal.textContent = d.segments; }
                    const tight = document.getElementById('cloth-tpl-tightness');
                    const tightVal = document.getElementById('cloth-tpl-tightness-val');
                    if (tight && d.tightness !== undefined) { tight.value = Math.round(d.tightness * 100); if (tightVal) tightVal.textContent = d.tightness.toFixed(2); }
                    const topExt = document.getElementById('cloth-tpl-top-ext');
                    const topExtVal = document.getElementById('cloth-tpl-top-ext-val');
                    if (topExt && d.top_extend !== undefined) { topExt.value = Math.round(d.top_extend * 100); if (topExtVal) topExtVal.textContent = d.top_extend.toFixed(2) + ' m'; }
                    const botExt = document.getElementById('cloth-tpl-bot-ext');
                    const botExtVal = document.getElementById('cloth-tpl-bot-ext-val');
                    if (botExt && d.bottom_extend !== undefined) { botExt.value = Math.round(d.bottom_extend * 100); if (botExtVal) botExtVal.textContent = d.bottom_extend.toFixed(2) + ' m'; }
                    const colorPicker = document.getElementById('cloth-color');
                    if (colorPicker && d.color) colorPicker.value = d.color;
                    console.log('Cloth preset loaded:', presetSelect.value);
                } catch (e) {
                    alert('Fehler beim Laden: ' + e.message);
                }
            });
        }

        const tplCreate = document.getElementById('cloth-tpl-create');
        if (tplCreate) {
            tplCreate.addEventListener('click', () => {
                const { key, params } = _tplParams();
                loadCloth(key, params);
            });
        }

        const tplUpdate = document.getElementById('cloth-tpl-update');
        if (tplUpdate) {
            tplUpdate.addEventListener('click', () => {
                const { key, params } = _tplParams();
                if (!state.clothMeshes[key]) {
                    console.warn(`No cloth "${key}" to update — use Create first`);
                    return;
                }
                loadCloth(key, params);
            });
        }

        const tplDelete = document.getElementById('cloth-tpl-delete');
        if (tplDelete) {
            tplDelete.addEventListener('click', () => {
                const tpl = tplSelect ? tplSelect.value : 'TPL_TSHIRT';
                const key = `tpl_${tpl}`;
                if (state.clothMeshes[key]) {
                    removeClothRegion(key);
                    console.log(`Cloth "${key}" removed`);
                }
            });
        }

        // --- Builder UI ---
        const bldSelect = document.getElementById('cloth-bld-region');
        if (bldSelect) {
            (data.builder_regions || []).forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.key;
                opt.textContent = r.label;
                bldSelect.appendChild(opt);
            });
        }
        bindSlider('cloth-bld-looseness', 'cloth-bld-looseness-val', v => (v / 100).toFixed(2));

        const bldCreate = document.getElementById('cloth-bld-create');
        if (bldCreate) {
            bldCreate.addEventListener('click', () => {
                const region = bldSelect ? bldSelect.value : 'TOP';
                const loose = sliderVal('cloth-bld-looseness') / 100;
                loadCloth(`bld_${region}`, { method: 'builder', region: region, looseness: loose });
            });
        }

        // --- Primitive UI ---
        const primSelect = document.getElementById('cloth-prim-type');
        if (primSelect) {
            (data.primitives || []).forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.key;
                opt.textContent = p.label;
                primSelect.appendChild(opt);
            });
            primSelect.addEventListener('change', () => {
                const flareRow = document.getElementById('cloth-prim-flare-row');
                if (flareRow) flareRow.style.display = primSelect.value === 'PRIM_SKIRT' ? 'flex' : 'none';
            });
        }
        bindSlider('cloth-prim-segments', 'cloth-prim-segments-val', v => v);
        bindSlider('cloth-prim-length', 'cloth-prim-length-val', v => (v / 100).toFixed(2));
        bindSlider('cloth-prim-flare', 'cloth-prim-flare-val', v => (v / 100).toFixed(2));

        const primCreate = document.getElementById('cloth-prim-create');
        if (primCreate) {
            primCreate.addEventListener('click', () => {
                const pt = primSelect ? primSelect.value : 'PRIM_SKIRT';
                const segs = sliderVal('cloth-prim-segments');
                const len = sliderVal('cloth-prim-length') / 100;
                const flare = sliderVal('cloth-prim-flare') / 100;
                loadCloth(`prim_${pt}`, { method: 'primitive', prim_type: pt, segments: segs, length: len, flare: flare });
            });
        }

        // --- Remove All button ---
        const removeBtn = document.getElementById('cloth-remove-all');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => removeAllCloth());
        }
    } catch (e) {
        console.warn('Cloth UI not available:', e);
    }
}

export async function loadCloth(key, params, color) {
    const createBtns = document.querySelectorAll('#cloth-tpl-create, #cloth-bld-create, #cloth-prim-create');
    createBtns.forEach(b => b.disabled = true);

    ensureSkinned();

    try {
        const qs = Object.entries(params)
            .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        const resp = await fetch(`/api/character/cloth/?${qs}`);
        const data = await resp.json();
        if (data.error) { console.error('Cloth error:', data.error); return; }

        removeClothRegion(key);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        let matColor;
        if (color) {
            matColor = new THREE.Color(color);
        } else {
            const colorPicker = document.getElementById('cloth-color');
            matColor = colorPicker
                ? new THREE.Color(colorPicker.value)
                : new THREE.Color(data.color[0], data.color[1], data.color[2]);
        }

        const mat = new THREE.MeshStandardMaterial({ color: matColor, roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide });

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

        state.clothMeshes[key] = mesh;
        state.clothParams[key] = { params, color: '#' + mesh.material.color.getHexString() };
        state.scene.add(mesh);

        console.log(`Cloth ${key}: ${data.vertex_count} verts, ${data.face_count} tris, skinned=${mesh.isSkinnedMesh || false}`);
        fn.updateEquippedList();
    } catch (e) {
        console.error('Failed to load cloth:', e);
    }
    createBtns.forEach(b => b.disabled = false);
}

export function removeClothRegion(key) {
    const m = state.clothMeshes[key];
    if (m) {
        state.scene.remove(m);
        m.geometry.dispose();
        m.material.dispose();
        delete state.clothMeshes[key];
        delete state.clothParams[key];
        fn.updateEquippedList();
    }
}

export function removeAllCloth() {
    for (const key of Object.keys(state.clothMeshes)) {
        removeClothRegion(key);
    }
}

// Register
fn.loadClothUI = loadClothUI;
fn.loadCloth = loadCloth;
fn.removeClothRegion = removeClothRegion;
fn.removeAllCloth = removeAllCloth;
