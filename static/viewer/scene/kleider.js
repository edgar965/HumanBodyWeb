/**
 * Scene Editor -- Kleider tab (2-stage fitting: Rig -> Mesh).
 * Extracted from scene_config.js lines 5902-6411.
 */
import './state.js';
import { state, REGION_IDS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _selectedInst, _bindSlider, _sliderVal } from './utils.js';
import './skeleton.js';
import { _applyGarmentRegionOffsets } from './kleidung_anpassen.js';
import { _doKleiderFit, _doKleiderStage1 } from './kleider_anpassen.js';
import { _kleiderSelectById, _renderKleiderList, _selectedKleiderMesh } from './kleider_liste.js';
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







// Cached stage1 hull vertices (Blender coords) for stage 2 fitting



export { loadKleiderUI };

fn.loadKleiderUI = loadKleiderUI;
fn._kleiderSelectById = _kleiderSelectById;
fn._selectedKleiderMesh = _selectedKleiderMesh;
fn._renderKleiderList = _renderKleiderList;
fn._doKleiderStage1 = _doKleiderStage1;
fn._doKleiderFit = _doKleiderFit;
