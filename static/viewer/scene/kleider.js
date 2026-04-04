/**
 * Scene Editor -- Kleider tab (2-stage fitting: Rig -> Mesh).
 * Extracted from scene_config.js lines 5902-6411.
 */
import { THREE } from './state.js';
import { state, REGION_IDS } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, _selectedInst, _charQueryParams, _bindSlider, _sliderVal } from './utils.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { _computeGarmentRegionWeights, _applyGarmentRegionOffsets } from './garments.js';
import {
    generateModelMesh, generateRigBoneMesh,
} from './state.js';

async function loadKleiderUI() {
    _bindSlider('kleider-bone-radius', 'kleider-bone-radius-val', v => parseFloat(v).toFixed(1) + 'x');
    _bindSlider('kleider-offset', 'kleider-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('kleider-stiffness', 'kleider-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('kleider-min-dist', 'kleider-min-dist-val', v => v + ' mm');
    _bindSlider('kleider-crotch-floor', 'kleider-crotch-floor-val', v => v + ' mm');
    _bindSlider('kleider-lift', 'kleider-lift-val', v => v + ' mm');
    _bindSlider('kleider-crotch-depth', 'kleider-crotch-depth-val', v => v + ' mm');
    _bindSlider('kleider-roughness', 'kleider-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('kleider-metalness', 'kleider-metalness-val', v => (v / 100).toFixed(2));

    // Material: real-time client-side updates
    const kRough = document.getElementById('kleider-roughness');
    if (kRough) kRough.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedKleiderMesh();
        if (sel) { sel.mesh.material.roughness = _sliderVal('kleider-roughness') / 100; }
    });
    const kMetal = document.getElementById('kleider-metalness');
    if (kMetal) kMetal.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedKleiderMesh();
        if (sel) { sel.mesh.material.metalness = _sliderVal('kleider-metalness') / 100; }
    });
    const kColor = document.getElementById('kleider-color');
    if (kColor) kColor.addEventListener('input', () => {
        if (state._syncingSliders) return;
        const sel = _selectedKleiderMesh();
        if (sel) { sel.mesh.material.color.set(kColor.value); }
    });

    // Fit sliders: debounced refit
    let _kleiderRefitTimer = null;
    function _debouncedKleiderRefit() {
        if (state._syncingSliders) return;
        const sel = _selectedKleiderMesh();
        if (!sel || !sel.key.startsWith('kld_')) return;
        state._selectedKleiderId = sel.key.slice(4);
        clearTimeout(_kleiderRefitTimer);
        _kleiderRefitTimer = setTimeout(() => _doKleiderFit(), 400);
    }
    for (const id of ['kleider-offset', 'kleider-stiffness', 'kleider-min-dist',
                       'kleider-crotch-floor', 'kleider-lift', 'kleider-crotch-depth']) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', _debouncedKleiderRefit);
    }

    // Region sliders
    for (const rid of REGION_IDS) {
        _bindSlider(`kleider-region-${rid}`, `kleider-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
        const rEl = document.getElementById(`kleider-region-${rid}`);
        if (rEl) rEl.addEventListener('input', () => {
            if (state._syncingSliders) return;
            const sel = _selectedKleiderMesh();
            if (!sel) return;
            _applyGarmentRegionOffsets(sel.inst, sel.key);
        });
    }

    const catSelect = document.getElementById('kleider-category');
    if (catSelect) catSelect.addEventListener('change', () => _renderKleiderList());

    const stage1Btn = document.getElementById('kleider-stage1');
    if (stage1Btn) stage1Btn.addEventListener('click', () => _doKleiderStage1());
    const stage2Btn = document.getElementById('kleider-stage2');
    if (stage2Btn) stage2Btn.addEventListener('click', () => _doKleiderFit('rig_hull'));
    const stage3Btn = document.getElementById('kleider-stage3');
    if (stage3Btn) stage3Btn.addEventListener('click', () => _doKleiderFit('body_refine'));

    const removeBtn = document.getElementById('kleider-remove');
    if (removeBtn) removeBtn.addEventListener('click', () => {
        if (state._selectedKleiderId && state._selectedSubMesh) fn._removeSubMesh(state._selectedSubMesh);
    });

    const removeAllBtn = document.getElementById('kleider-remove-all');
    if (removeAllBtn) removeAllBtn.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const keys = Object.keys(inst.clothMeshes).filter(k => k.startsWith('kld_'));
        for (const key of keys) {
            const t = { type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id };
            fn._removeSubMesh(t);
        }
    });

    // Load garment catalog if not already loaded, then populate Kleider list
    async function _ensureKleiderCatalog() {
        if (state._garmentCatalog.length === 0) {
            try {
                const resp = await fetch('/api/character/garment/library/');
                const data = await resp.json();
                if (data.garments) {
                    for (const cat of Object.keys(data.garments)) {
                        for (const g of data.garments[cat]) {
                            g._category = cat;
                            state._garmentCatalog.push(g);
                        }
                    }
                }
            } catch(e) { console.warn('Kleider: failed to load catalog', e); }
        }
    }
    const waitForCatalog = setInterval(async () => {
        await _ensureKleiderCatalog();
        if (state._garmentCatalog.length > 0) {
            clearInterval(waitForCatalog);
            // Populate category select
            if (catSelect) {
                const cats = [...new Set(state._garmentCatalog.map(g => g._category))];
                cats.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat;
                    opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                    catSelect.appendChild(opt);
                });
            }
            _renderKleiderList();

            // Restore last selected garment from settings
            const _klog = [];
            fetch('/api/settings/humanbody/').then(r => r.json()).then(s => {
                const lastId = s.ui_prefs?.last_kleider_id;
                _klog.push(`lastId=${lastId}`);
                if (!lastId) { _klog.push('no lastId, skip'); _sendKlog(_klog); return; }

                function _trySelect(attempt) {
                    const list = document.getElementById('kleider-list');
                    const items = list ? list.querySelectorAll('.anim-item') : [];
                    const ids = [...items].map(el => el.dataset.kleiderId).filter(Boolean);
                    const match = ids.includes(lastId);
                    _klog.push(`attempt=${attempt} items=${items.length} ids=${ids.slice(0,5).join(',')} match=${match}`);
                    if (match) {
                        _kleiderSelectById(lastId);
                        _klog.push('selected!');
                        _sendKlog(_klog);
                    } else if (attempt < 10) {
                        setTimeout(() => _trySelect(attempt + 1), 300);
                    } else {
                        _klog.push('gave up after 10 attempts');
                        _sendKlog(_klog);
                    }
                }
                _trySelect(0);
            }).catch(e => { _klog.push('fetch error: ' + e); _sendKlog(_klog); });

            function _sendKlog(log) {
                fetch('/api/ui-pref/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: '_kleider_debug_log', value: log }),
                }).catch(() => {});
            }
        }
    }, 200);

    // Show/hide content based on character selection — check immediately and on tab switch
    function _updateKleiderVisibility() {
        const emptyEl = document.getElementById('kleider-empty');
        const contentEl = document.getElementById('kleider-content');
        if (!emptyEl || !contentEl) return;
        const inst = _selectedInst();
        if (inst) { emptyEl.style.display = 'none'; contentEl.style.display = ''; }
        else { emptyEl.style.display = ''; contentEl.style.display = 'none'; }
    }
    _updateKleiderVisibility();
    window._updateKleiderVisibility = _updateKleiderVisibility;
    // Also check when a character is selected or tab switches
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            setTimeout(_updateKleiderVisibility, 50);
            // When switching TO Kleider tab, scroll selected item into view
            if (tab.dataset.tab === 'kleider' && state._selectedKleiderId) {
                setTimeout(() => {
                    const list = document.getElementById('kleider-list');
                    if (!list) return;
                    const sel = list.querySelector('.anim-item.selected');
                    if (sel) sel.scrollIntoView({ block: 'center' });
                }, 100);
            }
        });
    });
    // Fallback interval for edge cases
    setInterval(_updateKleiderVisibility, 1000);
}

function _kleiderSelectById(id) {
    state._selectedKleiderId = id;
    const list = document.getElementById('kleider-list');
    if (!list) return;

    // 1. Collapse ALL folders first
    list.querySelectorAll('.anim-folder').forEach(folder => {
        const body = folder.querySelector('.anim-folder-body');
        if (body) body.style.display = 'none';
        const chev = folder.querySelector('.chevron');
        if (chev) chev.textContent = '\u25B6';
    });

    // 2. Find the item, expand its parent folder, select it
    list.querySelectorAll('.anim-item').forEach(el => {
        if (el.dataset.kleiderId === id) {
            // Expand parent folder
            const folder = el.closest('.anim-folder');
            if (folder) {
                const body = folder.querySelector('.anim-folder-body');
                if (body) body.style.display = '';
                const chev = folder.querySelector('.chevron');
                if (chev) chev.textContent = '\u25BC';
            }
            // Select + highlight
            list.querySelectorAll('.anim-item').forEach(e => e.classList.remove('selected'));
            el.classList.add('selected');
            state._selectedKleiderId = id;

            // 3. Set category dropdown to match
            const catSelect = document.getElementById('kleider-category');
            if (catSelect && folder) {
                const g = state._garmentCatalog.find(g => g.id === id);
                if (g && g._category) catSelect.value = g._category;
            }
        }
    });
}

function _selectedKleiderMesh() {
    if (!state._selectedSubMesh || !state._selectedSubMesh.key.startsWith('kld_')) return null;
    const inst = state.characters.get(state._selectedSubMesh.charId);
    if (!inst) return null;
    return { inst, key: state._selectedSubMesh.key, mesh: inst.clothMeshes[state._selectedSubMesh.key] };
}

function _renderKleiderList() {
    const list = document.getElementById('kleider-list');
    if (!list) return;
    list.innerHTML = '';

    const catFilter = document.getElementById('kleider-category')?.value || '';
    const filtered = catFilter
        ? state._garmentCatalog.filter(g => g._category === catFilter)
        : state._garmentCatalog;

    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Kleider gefunden</div>';
        return;
    }

    // Group by category
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
        for (const g of items) {
            const row = document.createElement('div');
            row.className = 'anim-item';
            row.style.cssText = 'display:flex;align-items:center;gap:6px;padding:4px 8px;cursor:pointer;';
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
            row.dataset.kleiderId = g.id;
            row.addEventListener('click', () => {
                state._selectedKleiderId = g.id;
                list.querySelectorAll('.anim-item').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');
                // Apply garment defaults to sliders
                const offEl = document.getElementById('kleider-offset');
                if (offEl && g.offset != null) offEl.value = Math.round(g.offset * 1000);
                const stEl = document.getElementById('kleider-stiffness');
                if (stEl && g.stiffness != null) stEl.value = Math.round(g.stiffness * 100);
                // Save to DB
                fetch('/api/ui-pref/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: 'last_kleider_id', value: g.id }),
                }).catch(() => {});
            });
            body.appendChild(row);
        }
        catDiv.appendChild(body);
        const header = catDiv.querySelector('.anim-folder-header');
        header.addEventListener('click', () => {
            body.style.display = body.style.display === 'none' ? '' : 'none';
            header.querySelector('.chevron').textContent = body.style.display === 'none' ? '\u25B6' : '\u25BC';
        });
        list.appendChild(catDiv);
    }
}

// Cached stage1 hull vertices (Blender coords) for stage 2 fitting

async function _doKleiderStage1() {
    // Load the configured bone model (from Settings -> Szene -> Kleider)
    // and display it as the "kld_hull" submesh
    const inst = _selectedInst();
    if (!inst) return;

    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }

    // Get bone model name from settings
    let boneModelName = 'Rig1';
    try {
        const settingsResp = await fetch('/api/settings/humanbody/');
        const settings = await settingsResp.json();
        boneModelName = settings.ui_prefs?.kleider_bone_model || 'Rig1';
    } catch(e) {}

    // Load the model preset
    let preset;
    try {
        const resp = await fetch(`/api/character/model/${encodeURIComponent(boneModelName)}/`);
        preset = await resp.json();
    } catch(e) {
        console.error('Stage 1: Failed to load bone model preset:', boneModelName, e);
        return;
    }

    // Generate the mesh using model_generator
    const config = preset;
    const radiusMul = parseFloat(document.getElementById('kleider-bone-radius')?.value || '1.3');
    if (config.bone_parts) {
        for (const part of Object.values(config.bone_parts)) {
            if (part.visible) {
                part.radius = (part.radius || 0.03) * radiusMul;
            }
        }
    }

    let result;
    if (config.skeleton_type === 'rig' || preset.type === 'generated_model') {
        const { generateRigBoneMesh: genRigMesh } = await import('../model_generator.js');
        let rigData = null;
        try {
            const r = await fetch('/api/character/rig/');
            rigData = await r.json();
        } catch(e) {}
        result = genRigMesh(rigData, config, state.rigifySkeletonData, state.skinWeightData);
    } else {
        result = generateModelMesh(state.rigifySkeletonData, state.skinWeightData, config);
    }

    if (!result || !result.mesh) {
        console.warn('Stage 1: Failed to generate bone model from preset:', boneModelName);
        return;
    }

    const key = 'kld_hull';

    // Remove old hull if exists
    if (inst.clothMeshes[key]) {
        inst.group.remove(inst.clothMeshes[key]);
        inst.clothMeshes[key].geometry.dispose();
        inst.clothMeshes[key].material.dispose();
        delete inst.clothMeshes[key];
    }

    // Extract vertices in Three.js coords and convert to Blender for server
    const posAttr = result.mesh.geometry.getAttribute('position');
    const threeVerts = new Float32Array(posAttr.array);

    // Store Blender-coords version for server (Three->Blender: x,y,z -> x,-z,y)
    state._kleiderHullVertices = new Float32Array(threeVerts.length);
    for (let i = 0; i < threeVerts.length; i += 3) {
        state._kleiderHullVertices[i]     = threeVerts[i];      // X
        state._kleiderHullVertices[i + 1] = -threeVerts[i + 2]; // -Z -> Y
        state._kleiderHullVertices[i + 2] = threeVerts[i + 1];  // Y -> Z
    }

    // Display the generated mesh (semi-transparent)
    const mat = new THREE.MeshStandardMaterial({
        color: 0x44aaff, roughness: 0.5, metalness: 0.1,
        transparent: true, opacity: 0.5, side: THREE.DoubleSide,
    });
    const mesh = result.mesh;
    mesh.material = mat;

    // Apply current pose (T-pose etc.) to hull's own skeleton
    if (mesh.isSkinnedMesh && mesh.skeleton && inst.bodyMesh?.isSkinnedMesh && inst.bodyMesh.skeleton) {
        const bodySkel = inst.bodyMesh.skeleton;
        const hullSkel = mesh.skeleton;
        let copied = 0;
        for (const hullBone of hullSkel.bones) {
            const bodyBone = bodySkel.getBoneByName(hullBone.name);
            if (bodyBone) {
                hullBone.quaternion.copy(bodyBone.quaternion);
                copied++;
            }
        }
        const hullRoot = hullSkel.bones.find(b => !b.parent || b.parent === mesh);
        if (hullRoot) hullRoot.updateWorldMatrix(true, true);
        console.log(`[Hull] Copied ${copied} bone quaternions from body pose`);
    }

    inst.clothMeshes[key] = mesh;
    inst.group.add(mesh);

    console.log(`Stage 1: Bone model '${boneModelName}' loaded (${posAttr.count} verts)`);
    fn.updateEquippedList(inst);
    fn.updateVertexCount();
}

async function _doKleiderFit(fitMode) {
    if (!state._selectedKleiderId) return;
    const inst = _selectedInst();
    if (!inst) return;

    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }

    state._refitting = true;

    const params = _charQueryParams(inst);
    params.set('garment_id', state._selectedKleiderId);
    params.set('offset', (_sliderVal('kleider-offset') / 1000).toFixed(4));
    params.set('stiffness', (_sliderVal('kleider-stiffness') / 100).toFixed(2));
    params.set('min_dist', _sliderVal('kleider-min-dist'));
    params.set('crotch_floor', _sliderVal('kleider-crotch-floor'));
    params.set('lift', _sliderVal('kleider-lift'));
    params.set('crotch_depth', _sliderVal('kleider-crotch-depth'));
    params.set('fit_mode', fitMode || 'rig_hull');

    const colorHex = document.getElementById('kleider-color')?.value || '#4d5980';
    const c = new THREE.Color(colorHex);
    params.set('color_r', c.r.toFixed(3));
    params.set('color_g', c.g.toFixed(3));
    params.set('color_b', c.b.toFixed(3));

    try {
        let resp;
        if (fitMode === 'rig_hull' && state._kleiderHullVertices) {
            // Stage 2: Send hull vertices to server via POST
            const hullB64 = btoa(String.fromCharCode(...new Uint8Array(state._kleiderHullVertices.buffer)));
            resp = await fetch(`/api/character/garment/fit/?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hull_vertices: hullB64 }),
            });
        } else {
            resp = await fetch(`/api/character/garment/fit/?${params}`);
        }
        const data = await resp.json();
        if (data.error) { console.warn('Kleider fit error:', data.error); state._refitting = false; return; }

        const key = `kld_${state._selectedKleiderId}`;

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

        const roughness = _sliderVal('kleider-roughness') / 100;
        const metalness = _sliderVal('kleider-metalness') / 100;
        const mat = new THREE.MeshStandardMaterial({
            color: c, roughness, metalness, side: THREE.DoubleSide,
        });

        const mesh = _skinifyMesh(geo, mat, inst, data);
        inst.clothMeshes[key] = mesh;
        inst.group.add(mesh);

        inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
        _computeGarmentRegionWeights(inst, key);

        const prevSt = inst.garmentState[key];
        inst.garmentState[key] = {
            offset: _sliderVal('kleider-offset') / 1000,
            stiffness: _sliderVal('kleider-stiffness') / 100,
            minDist: _sliderVal('kleider-min-dist'),
            crotchFloor: _sliderVal('kleider-crotch-floor'),
            lift: _sliderVal('kleider-lift'),
            crotchDepth: _sliderVal('kleider-crotch-depth'),
            color: [c.r, c.g, c.b],
            roughness, metalness,
            regionTop: prevSt?.regionTop || 0,
            regionUpper: prevSt?.regionUpper || 0,
            regionMid: prevSt?.regionMid || 0,
            regionLower: prevSt?.regionLower || 0,
            regionBottom: prevSt?.regionBottom || 0,
        };

        _applyGarmentRegionOffsets(inst, key);

        state._refitting = false;
        fn.updateEquippedList(inst);
        fn.updateVertexCount();
    } catch (e) {
        state._refitting = false;
        console.error('Kleider fit failed:', e);
    }
}

export { loadKleiderUI, _kleiderSelectById, _selectedKleiderMesh, _renderKleiderList, _doKleiderStage1, _doKleiderFit };

fn.loadKleiderUI = loadKleiderUI;
fn._kleiderSelectById = _kleiderSelectById;
fn._selectedKleiderMesh = _selectedKleiderMesh;
fn._renderKleiderList = _renderKleiderList;
fn._doKleiderStage1 = _doKleiderStage1;
fn._doKleiderFit = _doKleiderFit;
