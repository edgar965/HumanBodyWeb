/**
 * Scene Editor -- Garment region weights + garment fit UI.
 */
import './state.js';
import { state, REGION_IDS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { escapeHtml, _selectedInst, _bindSlider, _sliderVal } from './utils.js';
import './skeleton.js';
import { _applyGarmentRegionOffsets, _computeGarmentRegionWeights, _doGarmentFit, _saveSelectedGarmentState, _syncGarmentSliders } from './kleidung_anpassen.js';
import { Assetsbedienung } from './assetsbedienung.js';
import { Bildnachlader } from '../gemeinsam/bildnachlader.js';
import { Kategoriekasten } from '../gemeinsam/kategoriekasten.js';

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
    // Die Bedienung steckt in `Assetsbedienung`, ihr gemeinsamer Teil mit dem
    // Kleider-Reiter in `Stueckbedienung` — vorher standen hier 101 Zeilen, die
    // dieselben Elemente unter anderer Vorsilbe verdrahteten.
    return new Assetsbedienung().verdrahten();
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
        list.innerHTML = '<div class="leer-hinweis">Keine Garments gefunden</div>';
        return;
    }

    const byCategory = {};
    for (const g of filtered) {
        const cat = g._category || 'Other';
        if (!byCategory[cat]) byCategory[cat] = [];
        byCategory[cat].push(g);
    }

    for (const [cat, garments] of Object.entries(byCategory)) {
        const {kasten: catDiv, koerper: body} =
            Kategoriekasten.bauen(cat, garments.length);
        for (const g of garments) {
            const item = document.createElement('div');
            item.className = 'anim-item garment-item' + (g.id === state._selectedGarmentId ? ' active' : '');
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.alt = g.name;
                // Erst laden, wenn die Kategorie aufgeklappt ist.
                //
                // GEMESSEN auf /humanbody/scene/ (17.08.2026): 253 Dateien,
                // 14,1 MB — davon 125 Vorschaubilder mit 4,77 MB fuer Bilder,
                // die in `display:none` stehen und niemand sieht. `loading="lazy"`
                // hilft dort NICHT (nachgemessen: 127 → 125), Chrome laedt Bilder
                // ohne Layout-Box sofort. Begruendung in der Klasse.
                Bildnachlader.vormerken(img, `/api/character/garment/thumb/${g.id}/`);
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
        list.appendChild(catDiv);
    }
}

// Register
fn._syncGarmentSliders = _syncGarmentSliders;
fn.loadGarmentUI = loadGarmentUI;
