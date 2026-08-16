/**
 * scene_charmorph.js — CharMorph asset browser for the Scene Editor.
 */
import { serverLog } from './scene_state.js?v=1';

// =========================================================================
// CharMorph assets state
// =========================================================================
export let _charmorphAssets = [];

// =========================================================================
// Load + render CharMorph assets
// =========================================================================
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
            for (const c of cats) {
                catSel.innerHTML += `<option value="${c}">${c}</option>`;
            }
            catSel.addEventListener('change', renderCharmorphList);
        }

        renderCharmorphList();

        // Bind sliders
        const offsetSlider = document.getElementById('cm-offset');
        const offsetVal = document.getElementById('cm-offset-val');
        if (offsetSlider) offsetSlider.addEventListener('input', () => {
            if (offsetVal) offsetVal.textContent = parseFloat(offsetSlider.value).toFixed(3);
        });
        const smoothSlider = document.getElementById('cm-smooth');
        const smoothVal = document.getElementById('cm-smooth-val');
        if (smoothSlider) smoothSlider.addEventListener('input', () => {
            if (smoothVal) smoothVal.textContent = parseFloat(smoothSlider.value).toFixed(2);
        });

        console.log(`[Scene] CharMorph assets loaded: ${_charmorphAssets.length}`);
    } catch (e) {
        console.error('[Scene] CharMorph assets load failed:', e);
    }
}

export function renderCharmorphList() {
    const list = document.getElementById('cm-asset-list');
    const catSel = document.getElementById('cm-category');
    if (!list) return;

    const cat = catSel?.value || '';
    const filtered = cat ? _charmorphAssets.filter(a => a.category === cat) : _charmorphAssets;

    list.innerHTML = '';
    for (const asset of filtered) {
        const item = document.createElement('div');
        item.style.cssText = 'padding:3px 6px;font-size:0.78rem;cursor:pointer;border-radius:3px;color:var(--text);';
        item.textContent = asset.name.replace(/_/g, ' ');
        item.dataset.name = asset.name;
        item.addEventListener('click', () => {
            list.querySelectorAll('div').forEach(d => d.style.background = '');
            item.style.background = 'rgba(124,92,191,0.3)';
            // Update material presets dropdown
            const matSel = document.getElementById('cm-material');
            if (matSel) {
                matSel.innerHTML = '<option value="">Standard</option>';
                for (const mp of (asset.material_presets || [])) {
                    matSel.innerHTML += `<option value="${mp}">${mp}</option>`;
                }
            }
        });
        item.addEventListener('dblclick', () => {
            serverLog('charmorph_asset_select', asset.name);
            alert(`Asset "${asset.name}" ausgewaehlt.\n\nHinweis: .blend Assets muessen erst nach GLB exportiert werden.\nDiese Funktion ist noch in Entwicklung.`);
        });
        list.appendChild(item);
    }
    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:6px;font-size:0.75rem;color:var(--text-muted);">Keine Assets gefunden</div>';
    }
}
