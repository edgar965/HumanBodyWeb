/**
 * Scene Editor -- CharMorph wardrobe/asset browser with fitting parameters.
 * Lists assets from CharMorphPlugin, shows configs, material presets.
 */
import { serverLog } from './state.js';
import { fn } from './registry.js';

let _charmorphAssets = [];
let _selectedAsset = null;

export async function loadCharmorphAssets() {
    try {
        const resp = await fetch('/api/character/charmorph-assets/');
        const data = await resp.json();
        _charmorphAssets = data.assets || [];

        // Populate category dropdown
        const catSel = document.getElementById('cm-category');
        if (catSel) {
            const cats = [...new Set(_charmorphAssets.map(a => a.category))].sort();
            catSel.innerHTML = '<option value="">Alle</option>';
            for (const c of cats) catSel.innerHTML += `<option value="${c}">${c}</option>`;
            catSel.addEventListener('change', renderCharmorphList);
        }

        renderCharmorphList();
        _bindControls();

        console.log(`[CharMorph] ${_charmorphAssets.length} assets loaded`);
    } catch (e) {
        console.error('[CharMorph] Asset load failed:', e);
    }
}

function _bindControls() {
    // Offset slider
    const offsetSlider = document.getElementById('cm-offset');
    const offsetVal = document.getElementById('cm-offset-val');
    if (offsetSlider) offsetSlider.addEventListener('input', () => {
        if (offsetVal) offsetVal.textContent = parseFloat(offsetSlider.value).toFixed(3);
    });

    // Smoothing slider
    const smoothSlider = document.getElementById('cm-smooth');
    const smoothVal = document.getElementById('cm-smooth-val');
    if (smoothSlider) smoothSlider.addEventListener('input', () => {
        if (smoothVal) smoothVal.textContent = parseFloat(smoothSlider.value).toFixed(2);
    });

    // Add button
    document.getElementById('cm-add')?.addEventListener('click', () => {
        if (!_selectedAsset) { alert('Bitte zuerst ein Asset auswaehlen.'); return; }
        serverLog('charmorph_add', _selectedAsset.name);
        alert(`Asset "${_selectedAsset.name}" hinzufuegen.\n\nCharMorph Assets sind .blend Dateien.\nFuer Web-Anzeige muessen sie erst nach GLB exportiert werden.\n\nVerwende: Blender > File > Export > GLB`);
    });

    // Remove button
    document.getElementById('cm-remove')?.addEventListener('click', () => {
        if (!_selectedAsset) { alert('Bitte zuerst ein Asset auswaehlen.'); return; }
        serverLog('charmorph_remove', _selectedAsset.name);
    });
}

export function renderCharmorphList() {
    const list = document.getElementById('cm-asset-list');
    const catSel = document.getElementById('cm-category');
    if (!list) return;

    const cat = catSel?.value || '';
    const filtered = cat ? _charmorphAssets.filter(a => a.category === cat) : _charmorphAssets;

    list.innerHTML = '';
    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:6px;font-size:0.75rem;color:var(--text-muted);">Keine Assets</div>';
        return;
    }

    for (const asset of filtered) {
        const item = document.createElement('div');
        item.style.cssText = 'padding:4px 8px;cursor:pointer;font-size:0.78rem;border-radius:3px;display:flex;justify-content:space-between;';
        item.innerHTML = `<span>${asset.name.replace(/_/g, ' ')}</span><span style="font-size:0.65rem;color:var(--text-muted);">${asset.category || ''}</span>`;

        item.addEventListener('click', () => {
            // Deselect all
            list.querySelectorAll('div').forEach(d => d.style.background = '');
            item.style.background = 'rgba(124,92,191,0.3)';
            _selectedAsset = asset;
            _showAssetParams(asset);
        });

        list.appendChild(item);
    }
}

function _showAssetParams(asset) {
    // Update material presets dropdown
    const matSel = document.getElementById('cm-material');
    if (matSel) {
        matSel.innerHTML = '<option value="">Standard</option>';
        for (const name of (asset.material_presets || [])) {
            matSel.innerHTML += `<option value="${name}">${name}</option>`;
        }
    }

    // Update offset/smoothing defaults from asset parameters
    const params = asset.parameters || {};
    if (params.offset) {
        const sl = document.getElementById('cm-offset');
        const val = document.getElementById('cm-offset-val');
        if (sl) { sl.value = params.offset.default || 0.001; sl.min = params.offset.min || -0.005; sl.max = params.offset.max || 0.02; }
        if (val) val.textContent = (params.offset.default || 0.001).toFixed(3);
    }
    if (params.smoothing) {
        const sl = document.getElementById('cm-smooth');
        const val = document.getElementById('cm-smooth-val');
        if (sl) { sl.value = params.smoothing.default || 0; sl.min = params.smoothing.min || 0; sl.max = params.smoothing.max || 1; }
        if (val) val.textContent = (params.smoothing.default || 0).toFixed(2);
    }

    // Update fitting mode from asset config
    const fitSel = document.getElementById('cm-fitting');
    if (fitSel && asset.fitting) fitSel.value = asset.fitting;

    // Show tags
    if (asset.tags && asset.tags.length > 0) {
        console.log(`[CharMorph] ${asset.name}: tags=[${asset.tags.join(', ')}]`);
    }
}

fn.loadCharmorphAssets = loadCharmorphAssets;
fn.renderCharmorphList = renderCharmorphList;
