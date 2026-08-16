/**
 * Scene Editor -- MakeHuman Proxy Fit UI.
 * Extracted from scene_config.js lines 4886-5322.
 */
import './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32, blenderToThreeCoords, _selectedInst, _charQueryParams, _bindSlider, _sliderVal } from './utils.js';
import './skeleton.js';
import { _doMHProxyFit, _fitMHProxyOnInst, _initPropMHControls, _syncPropMHControls } from './mhproxy_anpassen.js';
import { _renderMHList } from './mhproxy_liste.js';

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
        // Find selected MH ID from garment list or from existing cloth mesh
        if (!state._selectedMHId) {
            // Try selected character first, then any character
            let inst = _selectedInst();
            if (!inst) {
                const chars = state.characters;
                if (chars?.size > 0) inst = chars.values().next().value;
            }
            if (inst) {
                const key = Object.keys(inst.clothMeshes || {}).find(k => k.startsWith('mh_'));
                if (key) state._selectedMHId = key.slice(3);
            }
        }
        if (!state._selectedMHId) return;
        clearTimeout(_mhRefitTimer);
        _mhRefitTimer = setTimeout(() => _doMHProxyFit(), 400);
    }
    for (const id of ['mh-stiffness', 'mh-offset', 'mh-scale', 'mh-y-offset', 'mh-push-dist']) {
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











export { loadMHProxyUI, _selectedMHMesh };

fn.loadMHProxyUI = loadMHProxyUI;
fn._selectedMHMesh = _selectedMHMesh;
fn._renderMHList = _renderMHList;
fn._doMHProxyFit = _doMHProxyFit;
fn._fitMHProxyOnInst = _fitMHProxyOnInst;
fn._syncPropMHControls = _syncPropMHControls;
fn._initPropMHControls = _initPropMHControls;
