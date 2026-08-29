/**
 * Aus dem Schnittmuster ein Netz erzeugen, speichern, laden.
 *
 * Aus pattern_editor.js herausgeloest (Umbau 16.08.2026).
 */
import { Musterzustand } from './muster_zustand.js';
import { _peAutoFit, _peSetModeButtons, pePreviewKey, peUpdatePanelList } from './pattern_editor.js';
import { buildBodyQueryString, sliderVal } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { peRender } from './muster_zeichnen.js';
import { peUpdateStitchList } from './pattern_editor.js';
import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Musternetz } from './musternetz.js';


export async function peRegionGenerate() {
    const genBtn = document.getElementById('pe-generate'); if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status');
    if (statusEl) statusEl.textContent = 'Generating region...';
    ensureSkinned();
    const bodyQs = buildBodyQueryString();
    const zMin = (sliderVal('pe-region-zmin') / 100).toFixed(3); const zMax = (sliderVal('pe-region-zmax') / 100).toFixed(3);
    const arms = document.getElementById('pe-region-arms')?.checked ? '1' : '0';
    const grow = sliderVal('pe-region-grow');
    const looseness = (sliderVal('pe-region-looseness') / 100).toFixed(3); const category = document.getElementById('pe-region-category')?.value || 'custom';
    const regionQs = `z_min=${zMin}&z_max=${zMax}&include_arms=${arms}&grow=${grow}&looseness=${looseness}&category=${category}`;
    try {
        const data = await Serverabruf.json(
            `/api/character/pattern/region/generate/?${bodyQs}&${regionQs}`);
        if (data.error) { if (statusEl) statusEl.textContent = `Error: ${data.error}`; if (genBtn) genBtn.disabled = false; return; }
        Musternetz.einsetzen(data);
        if (statusEl) statusEl.textContent = `Region: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
    if (genBtn) genBtn.disabled = false;
}

export async function peGenerate3D() {
    const genBtn = document.getElementById('pe-generate'); if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status'); if (statusEl) statusEl.textContent = 'Generating...';
    ensureSkinned();
    const bodyQs = buildBodyQueryString();
    try {
        const wrapCb = document.getElementById('pe-wrap'); const wrap = wrapCb ? wrapCb.checked : false;
        const wrapOffset = (sliderVal('pe-wrap-offset') || 6) / 1000; const wrapStiffness = (sliderVal('pe-wrap-stiffness') ?? 50) / 100;
        const data = await Serverabruf.senden(
            `/api/character/pattern/generate/?${bodyQs}`,
            { pattern: Musterzustand.pePattern, wrap, offset: wrapOffset,
              stiffness: wrapStiffness });
        if (data.error) { if (statusEl) statusEl.textContent = `Error: ${data.error}`; if (genBtn) genBtn.disabled = false; return; }
        Musternetz.einsetzen(data);
        if (statusEl) statusEl.textContent = `Generated: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
    if (genBtn) genBtn.disabled = false;
}

export async function peSaveToLibrary() {
    const name = document.getElementById('pe-save-name')?.value?.trim();
    const category = document.getElementById('pe-save-category')?.value || 'custom';
    const statusEl = document.getElementById('pe-save-status'); if (!name) { if (statusEl) statusEl.textContent = 'Name is required'; return; }
    if (statusEl) statusEl.textContent = 'Saving...';
    const colorPicker = document.getElementById('pe-color');
    const colorHex = colorPicker ? colorPicker.value : '#404870';
    const cr = parseInt(colorHex.slice(1, 3), 16) / 255; const cg = parseInt(colorHex.slice(3, 5), 16) / 255; const cb = parseInt(colorHex.slice(5, 7), 16) / 255;
    const bodyQs = buildBodyQueryString();
    try {
        const data = await Serverabruf.json(`/api/character/pattern/save/?${bodyQs}`, { method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pattern: Musterzustand.pePattern, name, category, color: [cr, cg, cb], roughness: sliderVal('pe-roughness') / 100, metalness: sliderVal('pe-metalness') / 100, wrap: document.getElementById('pe-wrap')?.checked || false, offset: (sliderVal('pe-wrap-offset') || 6) / 1000, stiffness: (sliderVal('pe-wrap-stiffness') ?? 50) / 100 }) });
        if (data.ok) { if (statusEl) statusEl.textContent = `Saved: ${data.garment_id}`; } else { if (statusEl) statusEl.textContent = `Error: ${data.error || 'Unknown'}`; }
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
}

export async function peLoadFromGarment(garmentId) {
    try {
        const data = await Serverabruf.json(`/api/character/pattern/specification/?garment_id=${encodeURIComponent(garmentId)}`);
        if (!data.ok || !data.pattern) {
            Protokoll.warnung('muster_erzeugen', 'No specification found for', garmentId, data.error);
            return false;
        }
        Musterzustand.pePattern = data.pattern;
        if (!Musterzustand.pePattern.stitches) Musterzustand.pePattern.stitches = [];
        const names = Object.keys(Musterzustand.pePattern.panels || {}); Musterzustand.peActivePanel = names.length > 0 ? names[0] : null;
        Musterzustand.peSelectedVertex = null;
        Musterzustand.peSelectedEdge = null;
        Musterzustand.peStitchFirst = null;
        Musterzustand.peMode = 'select';
        _peSetModeButtons();
        _peAutoFit();
        peUpdatePanelList(); peUpdateStitchList(); peRender();
        const tabBtn = document.querySelector('.panel-tab[data-tab="tab-creator"]'); if (tabBtn) tabBtn.click();
        const nameEl = document.getElementById('pe-save-name'); if (nameEl) { const parts = garmentId.split('/'); nameEl.value = parts[parts.length - 1]; }
        const catEl = document.getElementById('pe-save-category');
        if (catEl) { const parts = garmentId.split('/'); if (parts.length > 1) { const cat = parts[0]; for (const opt of catEl.options) { if (opt.value === cat) { catEl.value = cat; break; } } } }
        Protokoll.debug('Viewer', `Pattern loaded from ${garmentId}: ${names.length} panels`); return true;
    } catch (e) { console.error('Failed to load pattern:', e); return false; }
}
