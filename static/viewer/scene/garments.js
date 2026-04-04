/**
 * Scene Editor -- Garment region weights + garment fit UI.
 */
import { THREE } from './state.js';
import { state, REGION_DEFS, REGION_RADIUS, REGION_IDS } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, escapeHtml, _selectedInst, _charQueryParams, _bindSlider, _sliderVal } from './utils.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { markDirty } from './undo.js';

/** Compute per-vertex cosine-blended region weights for a garment. */
export function _computeGarmentRegionWeights(inst, key) {
    const orig = inst.garmentOrigPositions[key];
    if (!orig) return;
    const n = orig.length / 3;
    let yMin = Infinity, yMax = -Infinity;
    for (let i = 0; i < n; i++) {
        const y = orig[i * 3 + 1];
        if (y < yMin) yMin = y;
        if (y > yMax) yMax = y;
    }
    const yRange = yMax - yMin || 1e-6;
    const weights = {};
    for (const def of REGION_DEFS) weights[def.id] = new Float32Array(n);
    for (let i = 0; i < n; i++) {
        const t = (orig[i * 3 + 1] - yMin) / yRange;
        for (const def of REGION_DEFS) {
            const dist = Math.abs(t - def.center);
            if (dist < REGION_RADIUS) {
                weights[def.id][i] = 0.5 * (1 + Math.cos(Math.PI * dist / REGION_RADIUS));
            }
        }
    }
    inst.garmentRegionWeights[key] = weights;
}

/** Apply per-region Y-offsets to a garment mesh using cosine-blended weights. */
export function _applyGarmentRegionOffsets(inst, key) {
    const mesh = inst.clothMeshes[key];
    const orig = inst.garmentOrigPositions[key];
    const rw = inst.garmentRegionWeights[key];
    const st = inst.garmentState[key];
    if (!mesh || !orig || !rw || !st) return;
    const positions = mesh.geometry.attributes.position.array;
    const n = orig.length / 3;
    positions.set(orig);
    for (const def of REGION_DEFS) {
        const stKey = 'region' + def.id[0].toUpperCase() + def.id.slice(1);
        const offset = st[stKey] || 0;
        if (Math.abs(offset) < 1e-6) continue;
        const w = rw[def.id];
        for (let i = 0; i < n; i++) {
            positions[i * 3 + 1] += offset * w[i];
        }
    }
    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.computeBoundingSphere();
}

/** Get the mesh+inst for the currently selected garment sub-mesh. */
export function _selectedGarmentMesh() {
    if (!state._selectedSubMesh || state._selectedSubMesh.type !== 'cloth') return null;
    const inst = state.characters.get(state._selectedSubMesh.charId);
    if (!inst) return null;
    const key = state._selectedSubMesh.key;
    const mesh = inst.clothMeshes[key];
    if (!mesh) return null;
    return { inst, key, mesh };
}

/** Save slider state back into garmentState for the selected garment. */
export function _saveSelectedGarmentState() {
    const sel = _selectedGarmentMesh();
    if (!sel) return;
    const st = sel.inst.garmentState[sel.key];
    if (!st) return;
    st.offset = _sliderVal('garment-offset') / 1000;
    st.stiffness = _sliderVal('garment-stiffness') / 100;
    st.minDist = _sliderVal('garment-min-dist');
    st.crotchFloor = _sliderVal('garment-crotch-floor');
    st.lift = _sliderVal('garment-lift');
    st.crotchDepth = _sliderVal('garment-crotch-depth');
    st.roughness = _sliderVal('garment-roughness') / 100;
    st.metalness = _sliderVal('garment-metalness') / 100;
    for (const rid of REGION_IDS) {
        const stKey = 'region' + rid[0].toUpperCase() + rid.slice(1);
        st[stKey] = _sliderVal(`garment-region-${rid}`) / 100;
    }
    const colorEl = document.getElementById('garment-color');
    if (colorEl) {
        const c = new THREE.Color(colorEl.value);
        st.color = [c.r, c.g, c.b];
    }
}

/** Sync garment sliders to selected garment state. */
export function _syncGarmentSliders() {
    if (!state._selectedSubMesh || state._selectedSubMesh.type !== 'cloth') return;
    const inst = state.characters.get(state._selectedSubMesh.charId);
    if (!inst) return;
    const key = state._selectedSubMesh.key;
    const st = inst.garmentState[key];
    if (!st) return;

    if (key.startsWith('gar_')) state._selectedGarmentId = key.slice(4);

    state._syncingSliders = true;
    const offEl = document.getElementById('garment-offset');
    if (offEl) { offEl.value = Math.round(st.offset * 1000); offEl.dispatchEvent(new Event('input')); }
    const stiffEl = document.getElementById('garment-stiffness');
    if (stiffEl) { stiffEl.value = Math.round(st.stiffness * 100); stiffEl.dispatchEvent(new Event('input')); }
    const minDistEl = document.getElementById('garment-min-dist');
    if (minDistEl) { minDistEl.value = st.minDist !== undefined ? st.minDist : 3; minDistEl.dispatchEvent(new Event('input')); }
    const crotchFloorEl = document.getElementById('garment-crotch-floor');
    if (crotchFloorEl) { crotchFloorEl.value = st.crotchFloor !== undefined ? st.crotchFloor : 0; crotchFloorEl.dispatchEvent(new Event('input')); }
    const liftEl = document.getElementById('garment-lift');
    if (liftEl) { liftEl.value = st.lift !== undefined ? st.lift : 0; liftEl.dispatchEvent(new Event('input')); }
    const crotchDepthSyncEl = document.getElementById('garment-crotch-depth');
    if (crotchDepthSyncEl) { crotchDepthSyncEl.value = st.crotchDepth !== undefined ? st.crotchDepth : 0; crotchDepthSyncEl.dispatchEvent(new Event('input')); }
    const roughEl = document.getElementById('garment-roughness');
    if (roughEl) { roughEl.value = Math.round(st.roughness * 100); roughEl.dispatchEvent(new Event('input')); }
    const metalEl = document.getElementById('garment-metalness');
    if (metalEl) { metalEl.value = Math.round(st.metalness * 100); metalEl.dispatchEvent(new Event('input')); }
    const colorEl = document.getElementById('garment-color');
    if (colorEl && st.color) colorEl.value = '#' + new THREE.Color(st.color[0], st.color[1], st.color[2]).getHexString();
    for (const rid of REGION_IDS) {
        const stKey = 'region' + rid[0].toUpperCase() + rid.slice(1);
        const rEl = document.getElementById(`garment-region-${rid}`);
        if (rEl) { rEl.value = Math.round((st[stKey] || 0) * 100); rEl.dispatchEvent(new Event('input')); }
    }
    state._syncingSliders = false;
}

export async function _doGarmentFit() {
    if (!state._selectedGarmentId) return;
    const inst = _selectedInst();
    if (!inst) return;

    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }

    const selKey = (state._selectedSubMesh && state._selectedSubMesh.charId === inst.id)
        ? state._selectedSubMesh.key : null;

    state._refitting = true;

    const params = _charQueryParams(inst);
    params.set('garment_id', state._selectedGarmentId);
    params.set('offset', (_sliderVal('garment-offset') / 1000).toFixed(4));
    params.set('stiffness', (_sliderVal('garment-stiffness') / 100).toFixed(2));
    params.set('min_dist', _sliderVal('garment-min-dist'));
    params.set('crotch_floor', _sliderVal('garment-crotch-floor'));
    params.set('lift', _sliderVal('garment-lift'));
    params.set('crotch_depth', _sliderVal('garment-crotch-depth'));

    const colorHex = document.getElementById('garment-color')?.value || '#4d5980';
    const c = new THREE.Color(colorHex);
    params.set('color_r', c.r.toFixed(3));
    params.set('color_g', c.g.toFixed(3));
    params.set('color_b', c.b.toFixed(3));

    try {
        const resp = await fetch(`/api/character/garment/fit/?${params}`);
        const data = await resp.json();
        if (data.error) { console.warn('Garment fit error:', data.error); state._refitting = false; return; }

        const key = `gar_${state._selectedGarmentId}`;

        if (inst.clothMeshes[key]) {
            inst.group.remove(inst.clothMeshes[key]);
            inst.clothMeshes[key].geometry.dispose();
            inst.clothMeshes[key].material.dispose();
            delete inst.clothMeshes[key];
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        const roughness = _sliderVal('garment-roughness') / 100;
        const metalness = _sliderVal('garment-metalness') / 100;
        const mat = new THREE.MeshStandardMaterial({
            color: c, roughness, metalness, side: THREE.DoubleSide,
        });

        const mesh = _skinifyMesh(geo, mat, inst, data);
        inst.clothMeshes[key] = mesh;
        inst.group.add(mesh);

        inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
        _computeGarmentRegionWeights(inst, key);

        const prevSt = inst.garmentState[key];
        const gState = {
            offset: _sliderVal('garment-offset') / 1000,
            stiffness: _sliderVal('garment-stiffness') / 100,
            minDist: _sliderVal('garment-min-dist'),
            crotchFloor: _sliderVal('garment-crotch-floor'),
            lift: _sliderVal('garment-lift'),
            crotchDepth: _sliderVal('garment-crotch-depth'),
            color: [c.r, c.g, c.b],
            roughness, metalness,
            regionTop: prevSt?.regionTop || 0, regionUpper: prevSt?.regionUpper || 0,
            regionMid: prevSt?.regionMid || 0, regionLower: prevSt?.regionLower || 0,
            regionBottom: prevSt?.regionBottom || 0,
        };
        inst.garmentState[key] = gState;
        _applyGarmentRegionOffsets(inst, key);

        inst.garments = inst.garments.filter(g => g.id !== state._selectedGarmentId);
        inst.garments.push({ id: state._selectedGarmentId, ...gState });

        if (selKey === key) {
            state._selectedSubMesh = { type: 'cloth', key, label: state._selectedGarmentId, meshObj: mesh, charId: inst.id };
            fn._setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
            fn._syncPropGarmentControls();
        }

        state._refitting = false;
        fn.updateEquippedList(inst);
        fn.updateVertexCount();
    } catch (e) {
        state._refitting = false;
        console.error('Garment fit failed:', e);
    }
}

export async function loadGarmentUI() {
    _bindSlider('garment-offset', 'garment-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('garment-stiffness', 'garment-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-min-dist', 'garment-min-dist-val', v => v + ' mm');
    _bindSlider('garment-crotch-floor', 'garment-crotch-floor-val', v => v + ' mm');
    _bindSlider('garment-lift', 'garment-lift-val', v => v + ' mm');
    _bindSlider('garment-crotch-depth', 'garment-crotch-depth-val', v => v + ' mm');
    _bindSlider('garment-roughness', 'garment-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-metalness', 'garment-metalness-val', v => (v / 100).toFixed(2));

    const roughSlider = document.getElementById('garment-roughness');
    if (roughSlider) roughSlider.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.roughness = _sliderVal('garment-roughness') / 100; _saveSelectedGarmentState(); }
    });
    const metalSlider = document.getElementById('garment-metalness');
    if (metalSlider) metalSlider.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.metalness = _sliderVal('garment-metalness') / 100; _saveSelectedGarmentState(); }
    });
    const colorPicker = document.getElementById('garment-color');
    if (colorPicker) colorPicker.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.color.set(colorPicker.value); _saveSelectedGarmentState(); }
    });

    let _garmentRefitTimer = null;
    function _debouncedGarmentRefit() {
        if (state._syncingSliders) return;
        const sel = _selectedGarmentMesh();
        if (!sel || !sel.key.startsWith('gar_')) return;
        state._selectedGarmentId = sel.key.slice(4);
        clearTimeout(_garmentRefitTimer);
        _garmentRefitTimer = setTimeout(() => _doGarmentFit(), 400);
    }
    for (const id of ['garment-offset', 'garment-stiffness', 'garment-min-dist', 'garment-crotch-floor', 'garment-lift', 'garment-crotch-depth']) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', _debouncedGarmentRefit);
    }

    for (const rid of REGION_IDS) {
        _bindSlider(`garment-region-${rid}`, `garment-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
        const rEl = document.getElementById(`garment-region-${rid}`);
        if (rEl) rEl.addEventListener('input', () => {
            if (state._syncingSliders) return;
            const sel = _selectedGarmentMesh();
            if (!sel) return;
            _saveSelectedGarmentState();
            _applyGarmentRegionOffsets(sel.inst, sel.key);
        });
    }

    const catSelect = document.getElementById('garment-category');
    if (catSelect) catSelect.addEventListener('change', () => _renderGarmentList());
    const createBtn = document.getElementById('garment-create');
    if (createBtn) createBtn.addEventListener('click', () => _doGarmentFit());
    const removeBtn = document.getElementById('garment-remove');
    if (removeBtn) removeBtn.addEventListener('click', () => {
        if (state._selectedGarmentId && state._selectedSubMesh) fn._removeSubMesh(state._selectedSubMesh);
    });
    const removeAllBtn = document.getElementById('garment-remove-all');
    if (removeAllBtn) removeAllBtn.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const keys = Object.keys(inst.clothMeshes).filter(k => k.startsWith('gar_'));
        for (const key of keys) {
            const t = { type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id };
            fn._removeSubMesh(t);
        }
    });

    // Load garment library
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
                for (const g of data.garments[cat]) {
                    g._category = cat;
                    state._garmentCatalog.push(g);
                }
            }
        }
        _renderGarmentList();
    } catch (e) {
        const list = document.getElementById('garment-list');
        if (list) list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Garment-Library nicht verf\u00fcgbar</div>';
    }
}

function _renderGarmentList() {
    const list = document.getElementById('garment-list');
    if (!list) return;
    list.innerHTML = '';

    const catFilter = document.getElementById('garment-category')?.value || '';
    const filtered = catFilter
        ? state._garmentCatalog.filter(g => g._category === catFilter)
        : state._garmentCatalog;

    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garments gefunden</div>';
        return;
    }

    const byCategory = {};
    for (const g of filtered) {
        const cat = g._category || 'Other';
        if (!byCategory[cat]) byCategory[cat] = [];
        byCategory[cat].push(g);
    }

    for (const [cat, garments] of Object.entries(byCategory)) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-category';
        const header = document.createElement('div');
        header.className = 'anim-category-header';
        header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span>
            <span>${escapeHtml(cat)}</span>
            <span class="cat-count">${garments.length}</span>`;
        header.addEventListener('click', () => catDiv.classList.toggle('open'));
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'anim-category-body';
        for (const g of garments) {
            const item = document.createElement('div');
            item.className = 'anim-item garment-item' + (g.id === state._selectedGarmentId ? ' active' : '');
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/character/garment/thumb/${g.id}/`;
                img.alt = g.name;
                img.className = 'garment-thumb';
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;margin-right:6px;';
                item.appendChild(img);
            }
            const nameSpan = document.createElement('span');
            nameSpan.className = 'garment-name';
            nameSpan.textContent = g.name || g.id;
            nameSpan.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            item.appendChild(nameSpan);
            item.style.cssText += 'display:flex;align-items:center;padding:4px 12px 4px 28px;';
            item.addEventListener('click', () => {
                list.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                state._selectedGarmentId = g.id;
                if (g.offset !== undefined) {
                    const offEl = document.getElementById('garment-offset');
                    if (offEl) { offEl.value = Math.round(g.offset * 1000); offEl.dispatchEvent(new Event('input')); }
                }
                if (g.stiffness !== undefined) {
                    const stEl = document.getElementById('garment-stiffness');
                    if (stEl) { stEl.value = Math.round(g.stiffness * 100); stEl.dispatchEvent(new Event('input')); }
                }
                for (const id of ['garment-min-dist', 'garment-crotch-floor', 'garment-lift', 'garment-crotch-depth']) {
                    const el = document.getElementById(id);
                    if (el) { el.value = 0; el.dispatchEvent(new Event('input')); }
                }
                for (const rid of REGION_IDS) {
                    const rEl = document.getElementById(`garment-region-${rid}`);
                    if (rEl) { rEl.value = 0; rEl.dispatchEvent(new Event('input')); }
                }
            });
            item.addEventListener('dblclick', () => _doGarmentFit());
            body.appendChild(item);
        }
        catDiv.appendChild(body);
        list.appendChild(catDiv);
    }
}

// Register
fn._computeGarmentRegionWeights = _computeGarmentRegionWeights;
fn._applyGarmentRegionOffsets = _applyGarmentRegionOffsets;
fn._selectedGarmentMesh = _selectedGarmentMesh;
fn._saveSelectedGarmentState = _saveSelectedGarmentState;
fn._syncGarmentSliders = _syncGarmentSliders;
fn._doGarmentFit = _doGarmentFit;
fn.loadGarmentUI = loadGarmentUI;
