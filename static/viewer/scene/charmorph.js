/**
 * Scene Editor -- CharMorph asset browser.
 */
import { serverLog } from './state.js';
import { fn } from './registry.js';

let _charmorphAssets = [];

export async function loadCharmorphAssets() {
    try {
        const resp = await fetch('/api/character/charmorph-assets/');
        const data = await resp.json();
        _charmorphAssets = data.assets || [];
        const catSel = document.getElementById('cm-category');
        if (catSel) {
            const cats = [...new Set(_charmorphAssets.map(a => a.category))].sort();
            catSel.innerHTML = '<option value="">Alle</option>';
            for (const c of cats) catSel.innerHTML += `<option value="${c}">${c}</option>`;
            catSel.addEventListener('change', renderCharmorphList);
        }
        renderCharmorphList();
        const offsetSlider = document.getElementById('cm-offset');
        const offsetVal = document.getElementById('cm-offset-val');
        if (offsetSlider) offsetSlider.addEventListener('input', () => { if (offsetVal) offsetVal.textContent = parseFloat(offsetSlider.value).toFixed(3); });
        const smoothSlider = document.getElementById('cm-smooth');
        const smoothVal = document.getElementById('cm-smooth-val');
        if (smoothSlider) smoothSlider.addEventListener('input', () => { if (smoothVal) smoothVal.textContent = parseFloat(smoothSlider.value).toFixed(2); });
    } catch (e) { console.error('[Scene] CharMorph assets load failed:', e); }
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
        item.className = 'anim-item';
        item.style.cssText = 'padding:4px 8px;cursor:pointer;font-size:0.8rem;';
        item.textContent = asset.name || asset.id;
        list.appendChild(item);
    }
}

fn.loadCharmorphAssets = loadCharmorphAssets;
fn.renderCharmorphList = renderCharmorphList;
