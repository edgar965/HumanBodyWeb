/**
 * Scene Editor -- Garment region weights + garment fit UI.
 */
import './state.js';
import { state, REGION_IDS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { escapeHtml, _selectedInst, _bindSlider, _sliderVal } from './utils.js';
import './skeleton.js';
import { _applyGarmentRegionOffsets, _computeGarmentRegionWeights, _doGarmentFit, _saveSelectedGarmentState, _syncGarmentSliders } from './kleidung_anpassen.js';



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

export function _renderGarmentList() {
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
