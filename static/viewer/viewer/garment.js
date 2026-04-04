/**
 * Viewer — Garment Fitter UI (catalog, fitting, region transforms).
 */
import * as THREE from 'three';
import { state, REGION_DEFS, REGION_RADIUS } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, bindSlider, sliderVal, setSlider } from './utils.js';
import { ensureSkinned } from './skinning.js';

export async function loadGarmentUI() {
    // Slider display bindings
    bindSlider('garment-offset', 'garment-offset-val', v => (v / 1000).toFixed(3));
    bindSlider('garment-stiffness', 'garment-stiffness-val', v => (v / 100).toFixed(2));
    bindSlider('garment-min-dist', 'garment-min-dist-val', v => v + ' mm');
    bindSlider('garment-crotch-floor', 'garment-crotch-floor-val', v => v + ' mm');
    bindSlider('garment-lift', 'garment-lift-val', v => v + ' mm');
    bindSlider('garment-crotch-depth', 'garment-crotch-depth-val', v => v + ' mm');
    bindSlider('garment-roughness', 'garment-roughness-val', v => (v / 100).toFixed(2));
    bindSlider('garment-metalness', 'garment-metalness-val', v => (v / 100).toFixed(2));
    bindSlider('garment-pos-x', 'garment-pos-x-val', v => (v / 100).toFixed(2) + ' m');
    bindSlider('garment-pos-y', 'garment-pos-y-val', v => (v / 100).toFixed(2) + ' m');
    bindSlider('garment-pos-z', 'garment-pos-z-val', v => (v / 100).toFixed(2) + ' m');
    bindSlider('garment-scale-x', 'garment-scale-x-val', v => (v / 100).toFixed(2));
    bindSlider('garment-scale-y', 'garment-scale-y-val', v => (v / 100).toFixed(2));
    bindSlider('garment-scale-z', 'garment-scale-z-val', v => (v / 100).toFixed(2));
    for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
        bindSlider(`garment-region-${rid}`, `garment-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
    }

    // Live garment sliders
    _garmentLiveSlider('garment-pos-x'); _garmentLiveSlider('garment-pos-y'); _garmentLiveSlider('garment-pos-z');
    _garmentLiveSlider('garment-scale-x'); _garmentLiveSlider('garment-scale-y'); _garmentLiveSlider('garment-scale-z');
    _garmentLiveSlider('garment-roughness'); _garmentLiveSlider('garment-metalness');
    for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) _garmentLiveSlider(`garment-region-${rid}`);

    // Server re-fit sliders
    _garmentRefitSlider('garment-offset'); _garmentRefitSlider('garment-stiffness');
    _garmentRefitSlider('garment-min-dist'); _garmentRefitSlider('garment-crotch-floor');
    _garmentRefitSlider('garment-lift'); _garmentRefitSlider('garment-crotch-depth');

    // Color picker
    const garmentColorEl = document.getElementById('garment-color');
    if (garmentColorEl) {
        garmentColorEl.addEventListener('input', () => {
            if (!state.selectedGarmentId || !state.garmentMeshes[state.selectedGarmentId]) return;
            state.garmentMeshes[state.selectedGarmentId].material.color.set(garmentColorEl.value);
            _saveGarmentState(state.selectedGarmentId);
        });
    }

    // Buttons
    const createBtn = document.getElementById('garment-create');
    if (createBtn) createBtn.addEventListener('click', () => {
        if (!state.selectedGarmentId) { console.warn('No garment selected'); return; }
        loadGarment(state.selectedGarmentId);
    });

    const updateBtn = document.getElementById('garment-update');
    if (updateBtn) updateBtn.addEventListener('click', () => {
        if (!state.selectedGarmentId || !state.garmentMeshes[state.selectedGarmentId]) return;
        _saveGarmentState(state.selectedGarmentId);
        loadGarment(state.selectedGarmentId);
    });

    const refitAllBtn = document.getElementById('garment-refit-all');
    if (refitAllBtn) refitAllBtn.addEventListener('click', async () => {
        const ids = Object.keys(state.garmentMeshes);
        if (ids.length === 0) return;
        refitAllBtn.disabled = true;
        refitAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...';
        for (const gid of ids) _saveGarmentState(gid);
        for (const gid of ids) await loadGarment(gid);
        refitAllBtn.disabled = false;
        refitAllBtn.innerHTML = '<i class="fas fa-sync"></i> Refit';
    });

    const removeBtn = document.getElementById('garment-remove');
    if (removeBtn) removeBtn.addEventListener('click', () => {
        if (state.selectedGarmentId && state.garmentMeshes[state.selectedGarmentId]) removeGarment(state.selectedGarmentId);
    });

    const removeAllBtn = document.getElementById('garment-remove-all');
    if (removeAllBtn) removeAllBtn.addEventListener('click', () => removeAllGarments());

    const catSelect = document.getElementById('garment-category');
    if (catSelect) catSelect.addEventListener('change', () => _renderGarmentList());

    // Download panel
    const dlBtn = document.getElementById('garment-download-btn');
    const dlPanel = document.getElementById('garment-download-panel');
    if (dlBtn && dlPanel) {
        dlBtn.addEventListener('click', async () => {
            const isOpen = dlPanel.style.display !== 'none';
            dlPanel.style.display = isOpen ? 'none' : 'block';
            if (!isOpen) await _loadDownloadPacks();
        });
    }
    const packDlBtn = document.getElementById('garment-pack-download');
    if (packDlBtn) packDlBtn.addEventListener('click', () => _downloadPack());

    // Edit Pattern button
    document.getElementById('garment-edit-pattern')?.addEventListener('click', () => {
        if (state.selectedGarmentId && fn.peLoadFromGarment) fn.peLoadFromGarment(state.selectedGarmentId);
    });

    // --- API catalog ---
    try {
        const resp = await fetch('/api/character/garment/library/');
        const data = await resp.json();
        state._garmentCatalog = [];

        if (catSelect && data.categories) {
            data.categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                catSelect.appendChild(opt);
            });
        }

        if (data.garments) {
            for (const cat of Object.keys(data.garments)) {
                for (const g of data.garments[cat]) state._garmentCatalog.push(g);
            }
        }

        _renderGarmentList();
    } catch (e) {
        console.warn('Garment UI not available:', e);
        const listEl = document.getElementById('garment-list');
        if (listEl) listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garment-Library</div>';
    }
}

function _renderGarmentList() {
    const listEl = document.getElementById('garment-list');
    const catSelect = document.getElementById('garment-category');
    if (!listEl) return;

    const filterCat = catSelect ? catSelect.value : '';
    const filtered = filterCat ? state._garmentCatalog.filter(g => g.category === filterCat) : state._garmentCatalog;

    if (filtered.length === 0) {
        listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garments gefunden</div>';
        return;
    }

    const byCat = {};
    for (const g of filtered) { if (!byCat[g.category]) byCat[g.category] = []; byCat[g.category].push(g); }

    listEl.innerHTML = '';
    for (const cat of Object.keys(byCat).sort()) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-category open';
        const header = document.createElement('div');
        header.className = 'anim-category-header';
        header.innerHTML = `<span class="cat-chevron">&#9654;</span> ${cat.toUpperCase()} <span class="cat-count">${byCat[cat].length}</span>`;
        header.addEventListener('click', () => catDiv.classList.toggle('open'));
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'anim-category-body';
        for (const g of byCat[cat]) {
            const item = document.createElement('div');
            item.className = 'anim-item garment-item';
            if (g.id === state.selectedGarmentId) item.classList.add('active');
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/character/garment/thumb/${g.id}/`;
                img.alt = g.name;
                img.className = 'garment-thumb';
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;margin-right:6px;';
                item.appendChild(img);
            }
            const nameSpan = document.createElement('span');
            nameSpan.textContent = g.name;
            nameSpan.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            item.appendChild(nameSpan);
            item.style.cssText += 'display:flex;align-items:center;padding:4px 12px 4px 28px;';
            item.dataset.garmentId = g.id;
            item.addEventListener('click', () => _onGarmentItemClick(g, item, listEl));
            body.appendChild(item);
        }
        catDiv.appendChild(body);
        listEl.appendChild(catDiv);
    }
}

function _onGarmentItemClick(g, item, listEl) {
    state.selectedGarmentId = g.id;
    listEl.querySelectorAll('.anim-item').forEach(el => el.classList.remove('active'));
    item.classList.add('active');

    const st = state.garmentState[g.id];
    if (st && state.garmentMeshes[g.id]) {
        setSlider('garment-color', st.color);
        setSlider('garment-offset', Math.round(st.offset * 1000), v => (v / 1000).toFixed(3));
        setSlider('garment-stiffness', Math.round(st.stiffness * 100), v => (v / 100).toFixed(2));
        setSlider('garment-min-dist', st.minDist !== undefined ? st.minDist : 3, v => v + ' mm');
        setSlider('garment-crotch-floor', st.crotchFloor !== undefined ? st.crotchFloor : 0, v => v + ' mm');
        setSlider('garment-lift', st.lift !== undefined ? st.lift : 0, v => v + ' mm');
        setSlider('garment-crotch-depth', st.crotchDepth !== undefined ? st.crotchDepth : 0, v => v + ' mm');
        setSlider('garment-roughness', Math.round(st.roughness * 100), v => (v / 100).toFixed(2));
        setSlider('garment-metalness', Math.round(st.metalness * 100), v => (v / 100).toFixed(2));
        setSlider('garment-pos-x', Math.round(st.posX * 100), v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-y', Math.round(st.posY * 100), v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-z', Math.round(st.posZ * 100), v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-scale-x', Math.round(st.scaleX * 100), v => (v / 100).toFixed(2));
        setSlider('garment-scale-y', Math.round(st.scaleY * 100), v => (v / 100).toFixed(2));
        setSlider('garment-scale-z', Math.round(st.scaleZ * 100), v => (v / 100).toFixed(2));
        for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
            const key = 'region' + rid[0].toUpperCase() + rid.slice(1);
            setSlider(`garment-region-${rid}`, Math.round((st[key] || 0) * 100), v => (v / 100).toFixed(2) + ' m');
        }
    } else {
        // Catalog defaults
        const colorPicker = document.getElementById('garment-color');
        if (colorPicker && g.color) {
            const hex = '#' + g.color.map(c => Math.round(c * 255).toString(16).padStart(2, '0')).join('');
            colorPicker.value = hex;
        }
        const offSlider = document.getElementById('garment-offset');
        const stiffSlider = document.getElementById('garment-stiffness');
        if (offSlider && g.offset !== undefined) { offSlider.value = Math.round(g.offset * 1000); const v = document.getElementById('garment-offset-val'); if (v) v.textContent = g.offset.toFixed(3); }
        if (stiffSlider && g.stiffness !== undefined) { stiffSlider.value = Math.round(g.stiffness * 100); const v = document.getElementById('garment-stiffness-val'); if (v) v.textContent = g.stiffness.toFixed(2); }
        setSlider('garment-min-dist', 3, v => v + ' mm');
        setSlider('garment-crotch-floor', 0, v => v + ' mm');
        setSlider('garment-lift', 0, v => v + ' mm');
        setSlider('garment-crotch-depth', 0, v => v + ' mm');
        setSlider('garment-roughness', 80, v => (v / 100).toFixed(2));
        setSlider('garment-metalness', 0, v => (v / 100).toFixed(2));
        setSlider('garment-pos-x', 0, v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-y', 0, v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-z', 0, v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-scale-x', 100, v => (v / 100).toFixed(2));
        setSlider('garment-scale-y', 100, v => (v / 100).toFixed(2));
        setSlider('garment-scale-z', 100, v => (v / 100).toFixed(2));
        for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) setSlider(`garment-region-${rid}`, 0, v => (v / 100).toFixed(2) + ' m');
    }

    const editBtn = document.getElementById('garment-edit-pattern');
    if (editBtn) editBtn.style.display = (g.source === 'pattern-editor') ? '' : 'none';
}

function _garmentLiveSlider(sliderId) {
    const el = document.getElementById(sliderId);
    if (!el) return;
    el.addEventListener('input', () => {
        if (!state.selectedGarmentId || !state.garmentMeshes[state.selectedGarmentId]) return;
        _saveGarmentState(state.selectedGarmentId);
        _applyGarmentState(state.selectedGarmentId);
    });
}

function _garmentRefitSlider(sliderId) {
    const el = document.getElementById(sliderId);
    if (!el) return;
    el.addEventListener('change', () => {
        if (!state.selectedGarmentId || !state.garmentMeshes[state.selectedGarmentId]) return;
        _saveGarmentState(state.selectedGarmentId);
        loadGarment(state.selectedGarmentId);
    });
}

export function _saveGarmentState(gid) {
    const colorPicker = document.getElementById('garment-color');
    state.garmentState[gid] = {
        posX: sliderVal('garment-pos-x') / 100, posY: sliderVal('garment-pos-y') / 100, posZ: sliderVal('garment-pos-z') / 100,
        scaleX: sliderVal('garment-scale-x') / 100, scaleY: sliderVal('garment-scale-y') / 100, scaleZ: sliderVal('garment-scale-z') / 100,
        color: colorPicker ? colorPicker.value : '#4d5980',
        roughness: sliderVal('garment-roughness') / 100, metalness: sliderVal('garment-metalness') / 100,
        offset: sliderVal('garment-offset') / 1000, stiffness: sliderVal('garment-stiffness') / 100,
        minDist: sliderVal('garment-min-dist'), crotchFloor: sliderVal('garment-crotch-floor'),
        lift: sliderVal('garment-lift'), crotchDepth: sliderVal('garment-crotch-depth'),
        regionTop: sliderVal('garment-region-top') / 100, regionUpper: sliderVal('garment-region-upper') / 100,
        regionMid: sliderVal('garment-region-mid') / 100, regionLower: sliderVal('garment-region-lower') / 100,
        regionBottom: sliderVal('garment-region-bottom') / 100,
    };
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

function _applyGarmentState(gid) {
    const mesh = state.garmentMeshes[gid];
    const st = state.garmentState[gid];
    const orig = state.garmentOrigPositions[gid];
    if (!mesh || !st || !orig) return;

    mesh.material.color.set(st.color);
    mesh.material.roughness = st.roughness;
    mesh.material.metalness = st.metalness;

    const positions = mesh.geometry.attributes.position.array;
    const n = orig.length / 3;
    let cx = 0, cy = 0, cz = 0;
    for (let i = 0; i < orig.length; i += 3) { cx += orig[i]; cy += orig[i + 1]; cz += orig[i + 2]; }
    cx /= n; cy /= n; cz /= n;

    for (let i = 0; i < orig.length; i += 3) {
        positions[i]     = (orig[i]     - cx) * st.scaleX + cx + st.posX;
        positions[i + 1] = (orig[i + 1] - cy) * st.scaleY + cy + st.posY;
        positions[i + 2] = (orig[i + 2] - cz) * st.scaleZ + cz + st.posZ;
    }

    const rw = state.garmentRegionWeights[gid];
    if (rw) {
        for (const def of REGION_DEFS) {
            const key = 'region' + def.id[0].toUpperCase() + def.id.slice(1);
            const offset = st[key] || 0;
            if (Math.abs(offset) < 1e-6) continue;
            const w = rw[def.id];
            for (let i = 0; i < n; i++) positions[i * 3 + 1] += offset * w[i];
        }
    }

    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.computeBoundingSphere();
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
        const resp = await fetch(`/api/character/garment/fit/?${qs}`);
        const data = await resp.json();
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

        console.log(`Garment ${garmentId}: ${data.vertex_count} verts, skinned=${mesh.isSkinnedMesh || false}`);

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

async function _loadDownloadPacks() {
    const packSelect = document.getElementById('garment-pack-select');
    if (!packSelect) return;
    try {
        const resp = await fetch('/api/character/garment/download/available/');
        const data = await resp.json();
        packSelect.innerHTML = '';
        (data.packs || []).forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.name;
            opt.textContent = `${p.label} (${p.category})`;
            packSelect.appendChild(opt);
        });
    } catch (e) { console.warn('Failed to load download packs:', e); }
}

async function _downloadPack() {
    const packSelect = document.getElementById('garment-pack-select');
    const statusEl = document.getElementById('garment-download-status');
    const dlBtn = document.getElementById('garment-pack-download');
    if (!packSelect || !packSelect.value) return;
    const packName = packSelect.value;
    if (dlBtn) dlBtn.disabled = true;
    if (statusEl) statusEl.textContent = `Lade ${packName}...`;
    try {
        const resp = await fetch('/api/character/garment/download/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pack_name: packName }),
        });
        const data = await resp.json();
        if (data.ok) {
            if (statusEl) statusEl.textContent = `${data.count} Garments installiert!`;
            const resp2 = await fetch('/api/character/garment/library/');
            const lib = await resp2.json();
            state._garmentCatalog = [];
            if (lib.garments) { for (const cat of Object.keys(lib.garments)) for (const g of lib.garments[cat]) state._garmentCatalog.push(g); }
            const catSelect = document.getElementById('garment-category');
            if (catSelect && lib.categories) {
                while (catSelect.options.length > 1) catSelect.remove(1);
                lib.categories.forEach(cat => { const opt = document.createElement('option'); opt.value = cat; opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1); catSelect.appendChild(opt); });
            }
            _renderGarmentList();
        } else {
            if (statusEl) statusEl.textContent = `Fehler: ${data.error || 'Unbekannt'}`;
        }
    } catch (e) { if (statusEl) statusEl.textContent = `Fehler: ${e.message}`; }
    if (dlBtn) dlBtn.disabled = false;
}

// Register
fn.loadGarmentUI = loadGarmentUI;
fn.loadGarment = loadGarment;
fn.removeGarment = removeGarment;
fn.removeAllGarments = removeAllGarments;
fn._saveGarmentState = _saveGarmentState;
fn.buildBodyFitQueryString = buildBodyFitQueryString;
