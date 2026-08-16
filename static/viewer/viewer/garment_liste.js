import { setSlider, sliderVal } from './utils.js';
import { state, REGION_DEFS } from './state.js';
/**
 * Kleidungsliste und Downloadpakete der Modellseite.
 *
 * Aus garment.js herausgeloest (Umbau 16.08.2026).
 */


export function _renderGarmentList() {
    const listEl = document.getElementById('garment-list');
    const catSelect = document.getElementById('garment-category');
    if (!listEl) return;

    const filterCat = catSelect ? catSelect.value : '';
    const filtered = filterCat ? state._garmentCatalog.filter(g => g.category === filterCat) : state._garmentCatalog;

    if (filtered.length === 0) {
        listEl.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garments gefunden</div>';
        return;
    }

    const byCat = {};
    for (const g of filtered) { if (!byCat[g.category]) byCat[g.category] = []; byCat[g.category].push(g); }

    listEl.innerHTML = '';
    for (const cat of Object.keys(byCat).sort()) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-category open';
        const header = document.createElement('div');
        header.className = 'anim-category-header';
        header.innerHTML = `<span class="cat-chevron">&#9654;</span> ${cat.toUpperCase()} <span class="cat-count">${byCat[cat].length}</span>`;
        header.addEventListener('click', () => catDiv.classList.toggle('open'));
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'anim-category-body';
        for (const g of byCat[cat]) {
            const item = document.createElement('div');
            item.className = 'anim-item garment-item';
            if (g.id === state.selectedGarmentId) item.classList.add('active');
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/character/garment/thumb/${g.id}/`;
                img.alt = g.name;
                img.className = 'garment-thumb';
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;margin-right:6px;';
                item.appendChild(img);
            }
            const nameSpan = document.createElement('span');
            nameSpan.textContent = g.name;
            nameSpan.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            item.appendChild(nameSpan);
            item.style.cssText += 'display:flex;align-items:center;padding:4px 12px 4px 28px;';
            item.dataset.garmentId = g.id;
            item.addEventListener('click', () => _onGarmentItemClick(g, item, listEl));
            body.appendChild(item);
        }
        catDiv.appendChild(body);
        listEl.appendChild(catDiv);
    }
}

export function _onGarmentItemClick(g, item, listEl) {
    state.selectedGarmentId = g.id;
    listEl.querySelectorAll('.anim-item').forEach(el => el.classList.remove('active'));
    item.classList.add('active');

    const st = state.garmentState[g.id];
    if (st && state.garmentMeshes[g.id]) {
        setSlider('garment-color', st.color);
        setSlider('garment-offset', Math.round(st.offset * 1000), v => (v / 1000).toFixed(3));
        setSlider('garment-stiffness', Math.round(st.stiffness * 100), v => (v / 100).toFixed(2));
        setSlider('garment-min-dist', st.minDist !== undefined ? st.minDist : 3, v => v + ' mm');
        setSlider('garment-crotch-floor', st.crotchFloor !== undefined ? st.crotchFloor : 0, v => v + ' mm');
        setSlider('garment-lift', st.lift !== undefined ? st.lift : 0, v => v + ' mm');
        setSlider('garment-crotch-depth', st.crotchDepth !== undefined ? st.crotchDepth : 0, v => v + ' mm');
        setSlider('garment-roughness', Math.round(st.roughness * 100), v => (v / 100).toFixed(2));
        setSlider('garment-metalness', Math.round(st.metalness * 100), v => (v / 100).toFixed(2));
        setSlider('garment-pos-x', Math.round(st.posX * 100), v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-y', Math.round(st.posY * 100), v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-z', Math.round(st.posZ * 100), v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-scale-x', Math.round(st.scaleX * 100), v => (v / 100).toFixed(2));
        setSlider('garment-scale-y', Math.round(st.scaleY * 100), v => (v / 100).toFixed(2));
        setSlider('garment-scale-z', Math.round(st.scaleZ * 100), v => (v / 100).toFixed(2));
        for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) {
            const key = 'region' + rid[0].toUpperCase() + rid.slice(1);
            setSlider(`garment-region-${rid}`, Math.round((st[key] || 0) * 100), v => (v / 100).toFixed(2) + ' m');
        }
    } else {
        // Catalog defaults
        const colorPicker = document.getElementById('garment-color');
        if (colorPicker && g.color) {
            const hex = '#' + g.color.map(c => Math.round(c * 255).toString(16).padStart(2, '0')).join('');
            colorPicker.value = hex;
        }
        const offSlider = document.getElementById('garment-offset');
        const stiffSlider = document.getElementById('garment-stiffness');
        if (offSlider && g.offset !== undefined) { offSlider.value = Math.round(g.offset * 1000); const v = document.getElementById('garment-offset-val'); if (v) v.textContent = g.offset.toFixed(3); }
        if (stiffSlider && g.stiffness !== undefined) { stiffSlider.value = Math.round(g.stiffness * 100); const v = document.getElementById('garment-stiffness-val'); if (v) v.textContent = g.stiffness.toFixed(2); }
        setSlider('garment-min-dist', 3, v => v + ' mm');
        setSlider('garment-crotch-floor', 0, v => v + ' mm');
        setSlider('garment-lift', 0, v => v + ' mm');
        setSlider('garment-crotch-depth', 0, v => v + ' mm');
        setSlider('garment-roughness', 80, v => (v / 100).toFixed(2));
        setSlider('garment-metalness', 0, v => (v / 100).toFixed(2));
        setSlider('garment-pos-x', 0, v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-y', 0, v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-pos-z', 0, v => (v / 100).toFixed(2) + ' m');
        setSlider('garment-scale-x', 100, v => (v / 100).toFixed(2));
        setSlider('garment-scale-y', 100, v => (v / 100).toFixed(2));
        setSlider('garment-scale-z', 100, v => (v / 100).toFixed(2));
        for (const rid of ['top', 'upper', 'mid', 'lower', 'bottom']) setSlider(`garment-region-${rid}`, 0, v => (v / 100).toFixed(2) + ' m');
    }

    const editBtn = document.getElementById('garment-edit-pattern');
    if (editBtn) editBtn.style.display = (g.source === 'pattern-editor') ? '' : 'none';
}

export function _saveGarmentState(gid) {
    const colorPicker = document.getElementById('garment-color');
    state.garmentState[gid] = {
        posX: sliderVal('garment-pos-x') / 100, posY: sliderVal('garment-pos-y') / 100, posZ: sliderVal('garment-pos-z') / 100,
        scaleX: sliderVal('garment-scale-x') / 100, scaleY: sliderVal('garment-scale-y') / 100, scaleZ: sliderVal('garment-scale-z') / 100,
        color: colorPicker ? colorPicker.value : '#4d5980',
        roughness: sliderVal('garment-roughness') / 100, metalness: sliderVal('garment-metalness') / 100,
        offset: sliderVal('garment-offset') / 1000, stiffness: sliderVal('garment-stiffness') / 100,
        minDist: sliderVal('garment-min-dist'), crotchFloor: sliderVal('garment-crotch-floor'),
        lift: sliderVal('garment-lift'), crotchDepth: sliderVal('garment-crotch-depth'),
        regionTop: sliderVal('garment-region-top') / 100, regionUpper: sliderVal('garment-region-upper') / 100,
        regionMid: sliderVal('garment-region-mid') / 100, regionLower: sliderVal('garment-region-lower') / 100,
        regionBottom: sliderVal('garment-region-bottom') / 100,
    };
}

export function _applyGarmentState(gid) {
    const mesh = state.garmentMeshes[gid];
    const st = state.garmentState[gid];
    const orig = state.garmentOrigPositions[gid];
    if (!mesh || !st || !orig) return;

    mesh.material.color.set(st.color);
    mesh.material.roughness = st.roughness;
    mesh.material.metalness = st.metalness;

    const positions = mesh.geometry.attributes.position.array;
    const n = orig.length / 3;
    let cx = 0, cy = 0, cz = 0;
    for (let i = 0; i < orig.length; i += 3) { cx += orig[i]; cy += orig[i + 1]; cz += orig[i + 2]; }
    cx /= n; cy /= n; cz /= n;

    for (let i = 0; i < orig.length; i += 3) {
        positions[i]     = (orig[i]     - cx) * st.scaleX + cx + st.posX;
        positions[i + 1] = (orig[i + 1] - cy) * st.scaleY + cy + st.posY;
        positions[i + 2] = (orig[i + 2] - cz) * st.scaleZ + cz + st.posZ;
    }

    const rw = state.garmentRegionWeights[gid];
    if (rw) {
        for (const def of REGION_DEFS) {
            const key = 'region' + def.id[0].toUpperCase() + def.id.slice(1);
            const offset = st[key] || 0;
            if (Math.abs(offset) < 1e-6) continue;
            const w = rw[def.id];
            for (let i = 0; i < n; i++) positions[i * 3 + 1] += offset * w[i];
        }
    }

    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.computeBoundingSphere();
}

export async function _loadDownloadPacks() {
    const packSelect = document.getElementById('garment-pack-select');
    if (!packSelect) return;
    try {
        const resp = await fetch('/api/character/garment/download/available/');
        const data = await resp.json();
        packSelect.innerHTML = '';
        (data.packs || []).forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.name;
            opt.textContent = `${p.label} (${p.category})`;
            packSelect.appendChild(opt);
        });
    } catch (e) { console.warn('Failed to load download packs:', e); }
}

export async function _downloadPack() {
    const packSelect = document.getElementById('garment-pack-select');
    const statusEl = document.getElementById('garment-download-status');
    const dlBtn = document.getElementById('garment-pack-download');
    if (!packSelect || !packSelect.value) return;
    const packName = packSelect.value;
    if (dlBtn) dlBtn.disabled = true;
    if (statusEl) statusEl.textContent = `Lade ${packName}...`;
    try {
        const resp = await fetch('/api/character/garment/download/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pack_name: packName }),
        });
        const data = await resp.json();
        if (data.ok) {
            if (statusEl) statusEl.textContent = `${data.count} Garments installiert!`;
            const resp2 = await fetch('/api/character/garment/library/');
            const lib = await resp2.json();
            state._garmentCatalog = [];
            if (lib.garments) { for (const cat of Object.keys(lib.garments)) for (const g of lib.garments[cat]) state._garmentCatalog.push(g); }
            const catSelect = document.getElementById('garment-category');
            if (catSelect && lib.categories) {
                while (catSelect.options.length > 1) catSelect.remove(1);
                lib.categories.forEach(cat => { const opt = document.createElement('option'); opt.value = cat; opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1); catSelect.appendChild(opt); });
            }
            _renderGarmentList();
        } else {
            if (statusEl) statusEl.textContent = `Fehler: ${data.error || 'Unbekannt'}`;
        }
    } catch (e) { if (statusEl) statusEl.textContent = `Fehler: ${e.message}`; }
    if (dlBtn) dlBtn.disabled = false;
}
