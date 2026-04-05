/**
 * Scene Editor -- MakeHuman Proxy Fit UI.
 * Extracted from scene_config.js lines 4886-5322.
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, _selectedInst, _charQueryParams, _bindSlider, _sliderVal } from './utils.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';

async function loadMHProxyUI() {
    _bindSlider('mh-stiffness', 'mh-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('mh-offset', 'mh-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('mh-scale', 'mh-scale-val', v => v + '%');
    _bindSlider('mh-y-offset', 'mh-y-offset-val', v => v + ' mm');
    _bindSlider('mh-roughness', 'mh-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('mh-metalness', 'mh-metalness-val', v => (v / 100).toFixed(2));
    _bindSlider('mh-opacity', 'mh-opacity-val', v => (v / 100).toFixed(2));

    // Material: real-time updates
    const mhRough = document.getElementById('mh-roughness');
    if (mhRough) mhRough.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedMHMesh();
        if (sel) sel.mesh.material.roughness = _sliderVal('mh-roughness') / 100;
    });
    const mhMetal = document.getElementById('mh-metalness');
    if (mhMetal) mhMetal.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedMHMesh();
        if (sel) sel.mesh.material.metalness = _sliderVal('mh-metalness') / 100;
    });
    // All fit parameters: debounced server refit on slider release
    let _mhRefitTimer = null;
    function _debouncedMHRefit() {
        if (state._syncingSliders) return;
        if (!state._selectedMHId) return;
        clearTimeout(_mhRefitTimer);
        _mhRefitTimer = setTimeout(() => _doMHProxyFit(), 400);
    }
    for (const id of ['mh-stiffness', 'mh-offset', 'mh-scale', 'mh-y-offset']) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', _debouncedMHRefit);
    }

    const mhColor = document.getElementById('mh-color');
    if (mhColor) mhColor.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedMHMesh();
        if (sel) sel.mesh.material.color.set(mhColor.value);
    });
    const mhOpacity = document.getElementById('mh-opacity');
    if (mhOpacity) mhOpacity.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedMHMesh();
        if (sel) {
            const v = _sliderVal('mh-opacity') / 100;
            sel.mesh.material.opacity = v;
            sel.mesh.material.transparent = v < 1;
        }
    });

    // Offset/Scale/Y-Offset: real-time client-side vertex transform
    function _applyMHTransform() {
        if (state._syncingSliders) return;
        const sel = _selectedMHMesh();
        if (!sel) return;
        const inst = sel.inst;
        const key = sel.key;
        const orig = inst.garmentOrigPositions?.[key];
        if (!orig) return;

        const offset = _sliderVal('mh-offset') / 1000;
        const scale = _sliderVal('mh-scale') / 100;
        const yOff = _sliderVal('mh-y-offset') / 1000;

        const pos = sel.mesh.geometry.getAttribute('position');
        const arr = pos.array;
        const n = orig.length / 3;

        // Compute centroid from originals
        let cx = 0, cy = 0, cz = 0;
        for (let i = 0; i < n; i++) {
            cx += orig[i * 3]; cy += orig[i * 3 + 1]; cz += orig[i * 3 + 2];
        }
        cx /= n; cy /= n; cz /= n;

        for (let i = 0; i < n; i++) {
            let x = orig[i * 3], y = orig[i * 3 + 1], z = orig[i * 3 + 2];
            // Scale from centroid
            x = (x - cx) * scale + cx;
            y = (y - cy) * scale + cy;
            z = (z - cz) * scale + cz;
            // Offset (push outward from centroid)
            if (offset > 0) {
                const dx = x - cx, dy = y - cy, dz = z - cz;
                const d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
                x += (dx / d) * offset;
                y += (dy / d) * offset;
                z += (dz / d) * offset;
            }
            // Y offset (Three.js Y = up)
            y += yOff;
            arr[i * 3] = x; arr[i * 3 + 1] = y; arr[i * 3 + 2] = z;
        }
        pos.needsUpdate = true;
        sel.mesh.geometry.computeBoundingSphere();
    }
    for (const id of ['mh-offset', 'mh-scale', 'mh-y-offset']) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', _applyMHTransform);
    }

    const catSelect = document.getElementById('mh-category');
    if (catSelect) catSelect.addEventListener('change', () => _renderMHList());

    const createBtn = document.getElementById('mh-create');
    if (createBtn) createBtn.addEventListener('click', () => _doMHProxyFit());

    const removeBtn = document.getElementById('mh-remove');
    if (removeBtn) removeBtn.addEventListener('click', () => {
        if (state._selectedMHId && state._selectedSubMesh) fn._removeSubMesh(state._selectedSubMesh);
    });

    _bindSlider('mh-push-dist', 'mh-push-dist-val', v => v + ' mm');

    const pushBtn = document.getElementById('mh-push');
    if (pushBtn) pushBtn.addEventListener('click', async () => {
        // Find MH garment mesh directly from selected character
        const inst = _selectedInst();
        if (!inst) return;
        const key = Object.keys(inst.clothMeshes || {}).find(k => k.startsWith('mh_'));
        if (!key) return;
        const sel = { inst, key, mesh: inst.clothMeshes[key] };
        if (!sel.mesh) return;

        // Save pre-push positions for undo (if not already saved)
        if (!inst._mhPrePush) inst._mhPrePush = {};
        if (!inst._mhPrePush[key]) {
            const pos = sel.mesh.geometry.getAttribute('position');
            inst._mhPrePush[key] = new Float32Array(pos.array);
        }

        // Get current garment positions in Blender coords
        const pos = sel.mesh.geometry.getAttribute('position');
        const threeVerts = new Float32Array(pos.array);
        // Three->Blender: (x, y, z) -> (x, -z, y)
        const blenderVerts = new Float32Array(threeVerts.length);
        for (let i = 0; i < threeVerts.length; i += 3) {
            blenderVerts[i] = threeVerts[i];
            blenderVerts[i+1] = -threeVerts[i+2];
            blenderVerts[i+2] = threeVerts[i+1];
        }

        const pushDist = _sliderVal('mh-push-dist');
        const params = _charQueryParams(inst);
        params.set('push_dist', pushDist);
        params.set('use_mh_body', '0');

        const b64 = btoa(String.fromCharCode(...new Uint8Array(blenderVerts.buffer)));
        try {
            const resp = await fetch(`/api/character/mh-push-outside/?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vertices: b64 }),
            });
            const data = await resp.json();
            if (data.error) { console.warn('Push failed:', data.error); return; }

            const newVerts = base64ToFloat32(data.vertices);
            blenderToThreeCoords(newVerts);
            pos.array.set(newVerts);
            pos.needsUpdate = true;
            sel.mesh.geometry.computeBoundingSphere();
            // Update originals for slider transforms
            inst.garmentOrigPositions[key] = new Float32Array(newVerts);
            console.log('Push outside done');
        } catch(e) { console.error('Push failed:', e); }
    });

    const pushUndoBtn = document.getElementById('mh-push-undo');
    if (pushUndoBtn) pushUndoBtn.addEventListener('click', () => {
        const sel = _selectedMHMesh();
        if (!sel) return;
        const inst = sel.inst;
        const key = sel.key;
        if (inst._mhPrePush && inst._mhPrePush[key]) {
            const pos = sel.mesh.geometry.getAttribute('position');
            pos.array.set(inst._mhPrePush[key]);
            pos.needsUpdate = true;
            sel.mesh.geometry.computeBoundingSphere();
            inst.garmentOrigPositions[key] = new Float32Array(inst._mhPrePush[key]);
            delete inst._mhPrePush[key];
            console.log('Push undone');
        }
    });

    const removeAllBtn = document.getElementById('mh-remove-all');
    if (removeAllBtn) removeAllBtn.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const keys = Object.keys(inst.clothMeshes).filter(k => k.startsWith('mh_'));
        for (const key of keys) {
            const t = { type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id };
            fn._removeSubMesh(t);
        }
    });

    // Load garment catalog (shared)
    const waitForCatalog = setInterval(async () => {
        if (state._garmentCatalog.length === 0) {
            try {
                const resp = await fetch('/api/character/garment/library/');
                const data = await resp.json();
                if (data.garments) {
                    for (const cat of Object.keys(data.garments)) {
                        for (const g of data.garments[cat]) {
                            g._category = cat;
                            if (!state._garmentCatalog.find(x => x.id === g.id))
                                state._garmentCatalog.push(g);
                        }
                    }
                }
            } catch(e) {}
        }
        if (state._garmentCatalog.length > 0) {
            clearInterval(waitForCatalog);
            if (catSelect) {
                const cats = [...new Set(state._garmentCatalog.map(g => g._category))];
                cats.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat;
                    opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                    catSelect.appendChild(opt);
                });
            }
            _renderMHList();
        }
    }, 200);
}

function _selectedMHMesh() {
    if (!state._selectedSubMesh || !state._selectedSubMesh.key.startsWith('mh_')) return null;
    const inst = state.characters.get(state._selectedSubMesh.charId);
    if (!inst) return null;
    return { inst, key: state._selectedSubMesh.key, mesh: inst.clothMeshes[state._selectedSubMesh.key] };
}

// Persist last open category + selected garment
const MH_STORAGE_KEY = 'mh_proxy_state';
function _saveMHState() {
    localStorage.setItem(MH_STORAGE_KEY, JSON.stringify({
        openCat: _mhOpenCat,
        selectedId: state._selectedMHId,
    }));
}
function _loadMHState() {
    try {
        const s = JSON.parse(localStorage.getItem(MH_STORAGE_KEY));
        if (s) { _mhOpenCat = s.openCat || ''; state._selectedMHId = s.selectedId || ''; }
    } catch(e) {}
}
let _mhOpenCat = '';

// Context menu for garment items
let _mhCtxTarget = null;
function _showMHCtx(x, y, garment) {
    _mhCtxTarget = garment;
    let menu = document.getElementById('mh-ctx-menu');
    if (!menu) {
        menu = document.createElement('div');
        menu.id = 'mh-ctx-menu';
        menu.className = 'ctx-menu';
        menu.style.cssText = 'position:fixed;z-index:9999;background:var(--bg-secondary);border:1px solid var(--border);border-radius:4px;padding:4px 0;min-width:140px;font-size:0.8rem;box-shadow:0 4px 12px rgba(0,0,0,.4);';
        menu.innerHTML = `
            <div class="ctx-item" data-action="rename" style="padding:4px 12px;cursor:pointer;">Umbenennen</div>
            <div class="ctx-item" data-action="move" style="padding:4px 12px;cursor:pointer;">Verschieben...</div>
            <div class="ctx-item" data-action="copy" style="padding:4px 12px;cursor:pointer;">Kopieren...</div>
            <div style="border-top:1px solid var(--border);margin:2px 0;"></div>
            <div class="ctx-item" data-action="delete" style="padding:4px 12px;cursor:pointer;color:#f44;">Löschen</div>
        `;
        menu.querySelectorAll('.ctx-item').forEach(item => {
            item.addEventListener('mouseenter', () => item.style.background = 'var(--accent)');
            item.addEventListener('mouseleave', () => item.style.background = '');
            item.addEventListener('click', () => _handleMHCtx(item.dataset.action));
        });
        document.body.appendChild(menu);
        document.addEventListener('click', () => { menu.style.display = 'none'; }, { capture: true });
    }
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    menu.style.display = 'block';
}

async function _handleMHCtx(action) {
    const g = _mhCtxTarget;
    if (!g) return;
    const menu = document.getElementById('mh-ctx-menu');
    if (menu) menu.style.display = 'none';

    if (action === 'rename') {
        const newName = prompt('Neuer Name:', g.name || g.id);
        if (newName && newName !== g.name) {
            try {
                await fetch('/api/character/garment/manage/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'rename', id: g.id, new_name: newName }),
                });
                g.name = newName;
                _renderMHList();
            } catch(e) { console.error('Rename failed:', e); }
        }
    } else if (action === 'move') {
        const cats = [...new Set(state._garmentCatalog.map(x => x._category))];
        const target = prompt('Verschieben nach Kategorie:\n' + cats.join(', '), g._category);
        if (target && target !== g._category) {
            try {
                await fetch('/api/character/garment/manage/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'move', id: g.id, target_category: target }),
                });
                g._category = target;
                _mhOpenCat = target;
                _renderMHList();
            } catch(e) { console.error('Move failed:', e); }
        }
    } else if (action === 'copy') {
        const newName = prompt('Kopie-Name:', (g.name || g.id) + '_copy');
        if (newName) {
            try {
                await fetch('/api/character/garment/manage/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'copy', id: g.id, new_name: newName }),
                });
                // Reload catalog
                state._garmentCatalog.length = 0;
                const resp = await fetch('/api/character/garment/library/');
                const data = await resp.json();
                if (data.garments) {
                    for (const cat of Object.keys(data.garments)) {
                        for (const gg of data.garments[cat]) {
                            gg._category = cat;
                            state._garmentCatalog.push(gg);
                        }
                    }
                }
                _renderMHList();
            } catch(e) { console.error('Copy failed:', e); }
        }
    } else if (action === 'delete') {
        if (!confirm(`"${g.name || g.id}" wirklich löschen?`)) return;
        try {
            await fetch('/api/character/garment/manage/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'delete', id: g.id }),
            });
            const idx = state._garmentCatalog.indexOf(g);
            if (idx >= 0) state._garmentCatalog.splice(idx, 1);
            if (state._selectedMHId === g.id) state._selectedMHId = '';
            _renderMHList();
        } catch(e) { console.error('Delete failed:', e); }
    }
}

function _renderMHList() {
    const list = document.getElementById('mh-list');
    if (!list) return;
    list.innerHTML = '';

    _loadMHState();

    const catFilter = document.getElementById('mh-category')?.value || '';
    const filtered = catFilter
        ? state._garmentCatalog.filter(g => g._category === catFilter)
        : state._garmentCatalog;

    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garments</div>';
        return;
    }

    const groups = {};
    for (const g of filtered) {
        if (!groups[g._category]) groups[g._category] = [];
        groups[g._category].push(g);
    }

    for (const [cat, items] of Object.entries(groups)) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-folder';
        catDiv.innerHTML = `<div class="anim-folder-header"><span class="chevron">&#9660;</span> ${cat} (${items.length})</div>`;
        const body = document.createElement('div');
        body.className = 'anim-folder-body';

        // Only open the last-used category, collapse all others
        const isOpen = _mhOpenCat === cat;
        body.style.display = isOpen ? '' : 'none';
        catDiv.querySelector('.chevron').textContent = isOpen ? '\u25BC' : '\u25B6';

        for (const g of items) {
            const row = document.createElement('div');
            row.className = 'anim-item';
            row.dataset.garmentId = g.id;
            row.style.cssText = 'display:flex;align-items:center;gap:6px;padding:4px 8px;cursor:pointer;';
            if (state._selectedMHId === g.id) row.classList.add('selected');
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/character/garment/thumb/${g.id}/`;
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;';
                row.appendChild(img);
            }
            const name = document.createElement('span');
            name.textContent = g.name || g.id;
            name.style.cssText = 'font-size:0.8rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            row.appendChild(name);
            row.addEventListener('click', () => {
                state._selectedMHId = g.id;
                _mhOpenCat = cat;
                _saveMHState();
                list.querySelectorAll('.anim-item').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');
            });
            row.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                state._selectedMHId = g.id;
                list.querySelectorAll('.anim-item').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');
                _showMHCtx(e.clientX, e.clientY, g);
            });
            body.appendChild(row);
        }
        catDiv.appendChild(body);
        const header = catDiv.querySelector('.anim-folder-header');
        header.addEventListener('click', () => {
            const opening = body.style.display === 'none';
            body.style.display = opening ? '' : 'none';
            header.querySelector('.chevron').textContent = opening ? '\u25BC' : '\u25B6';
            if (opening) {
                _mhOpenCat = cat;
                _saveMHState();
            }
        });
        list.appendChild(catDiv);
    }

    // Scroll to selected item
    if (state._selectedMHId) {
        const sel = list.querySelector(`[data-garment-id="${state._selectedMHId}"]`);
        if (sel) setTimeout(() => sel.scrollIntoView({ block: 'nearest' }), 50);
    }
}

async function _doMHProxyFit() {
    if (!state._selectedMHId) return;
    const inst = _selectedInst();
    if (!inst) return;

    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }

    const params = _charQueryParams(inst);
    params.set('garment_id', state._selectedMHId);

    const colorHex = document.getElementById('mh-color')?.value || '#4d5980';
    const c = new THREE.Color(colorHex);
    params.set('color_r', c.r.toFixed(3));
    params.set('color_g', c.g.toFixed(3));
    params.set('color_b', c.b.toFixed(3));
    params.set('offset', (_sliderVal('mh-offset') / 1000).toFixed(4));
    params.set('stiffness', (_sliderVal('mh-stiffness') / 100).toFixed(2));
    params.set('scale', (_sliderVal('mh-scale') / 100).toFixed(3));
    params.set('y_offset', (_sliderVal('mh-y-offset') / 1000).toFixed(4));
    // Fit to MH body (best quality), server transforms T→A to match bind pose
    params.set('use_mh_body', '1');

    try {
        const resp = await fetch(`/api/character/mh-proxy-fit/?${params}`);
        const data = await resp.json();
        if (data.error) { console.warn('MH proxy fit error:', data.error); return; }

        const key = `mh_${state._selectedMHId}`;

        // Remove old if exists
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

        const roughness = _sliderVal('mh-roughness') / 100;
        const metalness = _sliderVal('mh-metalness') / 100;
        const opacity = _sliderVal('mh-opacity') / 100;
        const mat = new THREE.MeshStandardMaterial({
            color: c, roughness, metalness, side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
            transparent: opacity < 1, opacity,
        });

        const mesh = _skinifyMesh(geo, mat, inst, data);
        console.log(`[MH] mesh type: ${mesh.type}, isSkinned: ${mesh.isSkinnedMesh}, hasSkeleton: ${!!mesh.skeleton}`);
        inst.clothMeshes[key] = mesh;
        inst.group.add(mesh);

        // Store original positions for real-time slider transforms
        inst.garmentOrigPositions[key] = new Float32Array(vertBuf);

        fn.updateEquippedList(inst);
        fn.updateVertexCount();
        console.log(`MH proxy fit: ${state._selectedMHId} (${data.vertex_count} verts)`);
    } catch (e) {
        console.error('MH proxy fit failed:', e);
    }
}

function _syncPropMHControls() {
    const sel = _selectedMHMesh();
    if (!sel) return;
    const mat = sel.mesh.material;
    // Sync material sliders
    const setV = (id, valId, v, fmt) => {
        const el = document.getElementById(id);
        const sp = document.getElementById(valId);
        if (el) el.value = v;
        if (sp) sp.textContent = fmt(v);
    };
    setV('prop-mh-roughness', 'prop-mh-roughness-val', Math.round(mat.roughness * 100), v => (v/100).toFixed(2));
    setV('prop-mh-metalness', 'prop-mh-metalness-val', Math.round(mat.metalness * 100), v => (v/100).toFixed(2));
    setV('prop-mh-opacity', 'prop-mh-opacity-val', Math.round(mat.opacity * 100), v => (v/100).toFixed(2));
    const colorEl = document.getElementById('prop-mh-color');
    if (colorEl) colorEl.value = '#' + mat.color.getHexString();
    // Sync transform sliders from asset tab values
    const syncFrom = (propId, srcId) => {
        const s = document.getElementById(srcId);
        const p = document.getElementById(propId);
        if (s && p) p.value = s.value;
    };
    syncFrom('prop-mh-stiffness', 'mh-stiffness');
    syncFrom('prop-mh-offset', 'mh-offset');
    syncFrom('prop-mh-scale', 'mh-scale');
    syncFrom('prop-mh-y-offset', 'mh-y-offset');
    // Update value displays
    _bindSlider('prop-mh-stiffness', 'prop-mh-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('prop-mh-offset', 'prop-mh-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('prop-mh-scale', 'prop-mh-scale-val', v => v + '%');
    _bindSlider('prop-mh-y-offset', 'prop-mh-y-offset-val', v => v + ' mm');
    _bindSlider('prop-mh-roughness', 'prop-mh-roughness-val', v => (v/100).toFixed(2));
    _bindSlider('prop-mh-metalness', 'prop-mh-metalness-val', v => (v/100).toFixed(2));
    _bindSlider('prop-mh-opacity', 'prop-mh-opacity-val', v => (v/100).toFixed(2));
}

function _initPropMHControls() {
    // Real-time material changes from Eigenschaften tab
    for (const [id, prop] of [['prop-mh-roughness', 'roughness'], ['prop-mh-metalness', 'metalness']]) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', () => {
            const sel = _selectedMHMesh();
            if (sel) sel.mesh.material[prop] = parseFloat(el.value) / 100;
        });
    }
    const opEl = document.getElementById('prop-mh-opacity');
    if (opEl) opEl.addEventListener('input', () => {
        const sel = _selectedMHMesh();
        if (sel) {
            const v = parseFloat(opEl.value) / 100;
            sel.mesh.material.opacity = v;
            sel.mesh.material.transparent = v < 1;
        }
    });
    const colEl = document.getElementById('prop-mh-color');
    if (colEl) colEl.addEventListener('input', () => {
        const sel = _selectedMHMesh();
        if (sel) sel.mesh.material.color.set(colEl.value);
    });
    // Transform sliders -- sync to asset tab + apply
    for (const [propId, srcId] of [['prop-mh-stiffness','mh-stiffness'],['prop-mh-offset','mh-offset'],['prop-mh-scale','mh-scale'],['prop-mh-y-offset','mh-y-offset']]) {
        const el = document.getElementById(propId);
        if (el) el.addEventListener('input', () => {
            const src = document.getElementById(srcId);
            if (src) { src.value = el.value; src.dispatchEvent(new Event('input')); }
        });
    }
}

export { loadMHProxyUI, _selectedMHMesh, _renderMHList, _doMHProxyFit, _syncPropMHControls, _initPropMHControls };

fn.loadMHProxyUI = loadMHProxyUI;
fn._selectedMHMesh = _selectedMHMesh;
fn._renderMHList = _renderMHList;
fn._doMHProxyFit = _doMHProxyFit;
fn._syncPropMHControls = _syncPropMHControls;
fn._initPropMHControls = _initPropMHControls;
