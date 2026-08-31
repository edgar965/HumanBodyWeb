/**
 * Viewer — Pattern Editor (2D canvas for garment panels/stitches + region generate).
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { bindSlider } from './utils.js';
import { removeClothRegion } from './cloth.js';
import './skinning.js';
import { veEnterEditMode, veExitEditMode, initVertexEditorBindings, isVeActive } from './vertex_editor.js';
import { Musterzustand } from './muster_zustand.js';
import { _peHitControlPoint, _peHitEdge, _peHitVertex, peRender } from './muster_zeichnen.js';
import { peGenerate3D, peLoadFromGarment, peRegionGenerate, peSaveToLibrary } from './muster_erzeugen.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Musterzeichenflaeche } from './muster_maus.js';

export const pePreviewKey = 'pe_preview';
export const PE_COLORS = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c'];

const PE_REGION_PRESETS = {
    custom:    {z_min: 60, z_max: 140, arms: false, grow: 2, looseness: 30},
    top:       {z_min: 80, z_max: 155, arms: true,  grow: 2, looseness: 30},
    pants:     {z_min: 0,  z_max: 105, arms: false, grow: 2, looseness: 30},
    skirt:     {z_min: 55, z_max: 100, arms: false, grow: 3, looseness: 40},
    full:      {z_min: 0,  z_max: 155, arms: true,  grow: 2, looseness: 30},
    underwear: {z_min: 55, z_max: 100, arms: false, grow: 1, looseness: 20},
    shoes:     {z_min: 0,  z_max: 15,  arms: false, grow: 2, looseness: 20},
};

export function peWorldToCanvas(wx, wy) { return [Musterzustand.pePan.x + wx * Musterzustand.peZoom,
    Musterzustand.pePan.y - wy * Musterzustand.peZoom]; }
export function peCanvasToWorld(cx, cy) { return [(cx - Musterzustand.pePan.x) / Musterzustand.peZoom,
    (Musterzustand.pePan.y - cy) / Musterzustand.peZoom]; }

function _peSetRegionMode(active) {
    const patternControls = document.getElementById('pe-pattern-controls');
    const regionControls = document.getElementById('pe-region-controls');
    const wrapSection = document.getElementById('pe-wrap-section');
    if (active) {
        if (patternControls) patternControls.style.display = 'none';
        if (wrapSection) wrapSection.style.display = 'none';
        if (regionControls) regionControls.style.display = '';
    }
    else { if (patternControls) patternControls.style.display = ''; if (wrapSection) wrapSection.style.display = '';
        if (regionControls) regionControls.style.display = 'none'; }
}

export function _peSetModeButtons() {
    document.querySelectorAll('#pe-mode-btns .btn-toggle').forEach(btn => { btn.classList.toggle('active',
        btn.dataset.mode === Musterzustand.peMode); });
    if (Musterzustand.peMode !== 'edit' && isVeActive()) veExitEditMode();
    if (Musterzustand.peMode === 'edit') veEnterEditMode();
    else _peSetRegionMode(Musterzustand.peMode === 'region');
}

function peSetMode(mode) { Musterzustand.peMode = mode; _peSetModeButtons(); }

export function peUpdatePanelList() {
    const list = document.getElementById('pe-panel-list');
    if (!list) return;
    const names = Object.keys(Musterzustand.pePattern.panels);
    const PLACEMENT_BADGES = {flat:'',front:'[F]',back:'[B]',left:'[L]',right:'[R]',sleeve_L:'[SL]',sleeve_R:'[SR]'};
    list.innerHTML = names.map((name, i) => {
        const color = PE_COLORS[i % PE_COLORS.length]; const active = name === Musterzustand.peActivePanel;
        const p = Musterzustand.pePattern.panels[name];
        const nv = p.vertices.length;
        const closed = p.closed ? 'closed' : 'open';
        const badge = PLACEMENT_BADGES[p.placement || 'flat'] || '';
        // Nur die Musterfarbe haengt am Eintrag; alles Uebrige steht als
        // `.pe-panel-item` im Stilblock von `character_viewer.html`.
        return `<div class="pe-panel-item${active ? ' active' : ''}" data-name="${name}"
            style="border-left-color:${color};"><span
            style="color:${color};">&#9679;</span> ${name} ${badge
            ? `<span class="muster-marke">${badge}</span> ` : ''}<span
            class="muster-anzahl">(${nv}v, ${closed})</span></div>`;
    }).join('');
    list.querySelectorAll('.pe-panel-item').forEach(el => {
        el.addEventListener('click', () => { Musterzustand.peActivePanel = el.dataset.name;
            Musterzustand.peSelectedVertex = null; Musterzustand.peSelectedEdge = null; peUpdatePanelList();
                _peSyncPlacementDropdown(); peRender(); });
    });
}

export function peUpdateStitchList() {
    const list = document.getElementById('pe-stitch-list'); const countEl = document.getElementById('pe-stitch-count');
    if (!list) return;
    if (countEl) countEl.textContent = `(${Musterzustand.pePattern.stitches.length})`;
    list.innerHTML = Musterzustand.pePattern.stitches.map((st,
        i) => `<div class="naht-zeile">${st.panelA}.e${st.edgeA} \u2194 ${st.panelB}.e${st.edgeB} <span
            class="pe-stitch-del" title="Remove">\u2715</span></div>`).join('');
    list.querySelectorAll('.pe-stitch-del').forEach(el => { el.addEventListener('click',
        () => { Musterzustand.pePattern.stitches.splice(parseInt(el.dataset.idx), 1); peUpdateStitchList(); peRender();
            }); });
}

function _peSyncPlacementDropdown() { const dd = document.getElementById('pe-placement'); if (!dd
    || !Musterzustand.peActivePanel) return; const p = Musterzustand.pePattern.panels[Musterzustand.peActivePanel];
        dd.value = (p && p.placement) || 'flat'; }

export function _peAutoFit() {
    const canvas = document.getElementById('pe-canvas'); if (!canvas) return;
    const W = canvas.width, H = canvas.height; const allVerts = [];
    for (const panel of Object.values(Musterzustand.pePattern.panels || {})) for (const v of (panel.vertices
        || [])) allVerts.push(v);
    if (allVerts.length === 0) { Musterzustand.pePan = {x: W/2, y: H/2}; Musterzustand.peZoom = 2.0; return; }
    const xs = allVerts.map(v => v[0]), ys = allVerts.map(v => v[1]);
    const xMin = Math.min(...xs), xMax = Math.max(...xs), yMin = Math.min(...ys), yMax = Math.max(...ys);
    const pw = xMax - xMin || 20, ph = yMax - yMin || 20;
    const margin = 0.15; const zoomX = W * (1 - 2 * margin) / pw; const zoomY = H * (1 - 2 * margin) / ph;
    Musterzustand.peZoom = Math.min(zoomX, zoomY);
    Musterzustand.peZoom = Math.max(0.5, Math.min(20, Musterzustand.peZoom));
    const cx = (xMin + xMax) / 2; const cy = (yMin + yMax) / 2;
    Musterzustand.pePan.x = W / 2 - cx * Musterzustand.peZoom;
        Musterzustand.pePan.y = H / 2 + cy * Musterzustand.peZoom;
}

export function initPatternEditor() {
    const canvas = document.getElementById('pe-canvas'); if (!canvas) return;
    Musterzeichenflaeche.binden(canvas);
    document.querySelectorAll('#pe-mode-btns .btn-toggle').forEach(btn => { btn.addEventListener('click',
        () => { Musterzustand.peMode = btn.dataset.mode; Musterzustand.peStitchFirst = null; _peSetModeButtons(); });
            });
    document.getElementById('pe-add-panel')?.addEventListener('click', () => {
        const names = Object.keys(Musterzustand.pePattern.panels); const defaultName = `Panel${names.length + 1}`;
        const name = prompt('Panel name:', defaultName); if (!name || !name.trim()) return; const trimmed = name.trim();
        if (Musterzustand.pePattern.panels[trimmed]) { alert('Panel already exists'); return; }
        Musterzustand.pePattern.panels[trimmed] = {vertices: [], edges: [], closed: false};
            Musterzustand.peActivePanel = trimmed; Musterzustand.peMode = 'draw'; _peSetModeButtons();
                peUpdatePanelList(); peRender();
    });
    document.getElementById('pe-del-panel')?.addEventListener('click', () => {
        if (!Musterzustand.peActivePanel) return;
            Musterzustand.pePattern.stitches = Musterzustand.pePattern.stitches.filter(s => s.panelA
                !== Musterzustand.peActivePanel && s.panelB !== Musterzustand.peActivePanel);
        delete Musterzustand.pePattern.panels[Musterzustand.peActivePanel];
        const names = Object.keys(Musterzustand.pePattern.panels);
        Musterzustand.peActivePanel = names.length > 0 ? names[0] : null;
        Musterzustand.peSelectedVertex = null;
        Musterzustand.peSelectedEdge = null;
        peUpdatePanelList();
        peUpdateStitchList();
        peRender();
    });
    document.getElementById('pe-placement')?.addEventListener('change', (e) => {
        const teil = Musterzustand.pePattern.panels[Musterzustand.peActivePanel];
        if (!Musterzustand.peActivePanel || !teil) return;
        teil.placement = e.target.value;
        peUpdatePanelList();
    });
    document.getElementById('pe-wrap')?.addEventListener('change',
        (e) => { const sliders = document.getElementById('pe-wrap-sliders');
            if (sliders) sliders.style.display = e.target.checked ? '' : 'none'; });
    bindSlider('pe-wrap-offset', 'pe-wrap-offset-val', v => v); bindSlider('pe-wrap-stiffness', 'pe-wrap-stiffness-val',
        v => (v / 100).toFixed(2));
    bindSlider('pe-region-zmin', 'pe-region-zmin-val', v => (v / 100).toFixed(2)); bindSlider('pe-region-zmax',
        'pe-region-zmax-val', v => (v / 100).toFixed(2));
    bindSlider('pe-region-grow', 'pe-region-grow-val', v => v); bindSlider('pe-region-looseness',
        'pe-region-looseness-val', v => (v / 100).toFixed(2));
    document.getElementById('pe-region-category')?.addEventListener('change', (e) => {
        const preset = PE_REGION_PRESETS[e.target.value]; if (!preset) return;
        const setS = (id, val) => { const el = document.getElementById(id); if (el) { el.value = val;
            el.dispatchEvent(new Event('input')); } };
        setS('pe-region-zmin', preset.z_min);
        setS('pe-region-zmax', preset.z_max);
        setS('pe-region-grow', preset.grow);
        setS('pe-region-looseness', preset.looseness);
        const armsEl = document.getElementById('pe-region-arms'); if (armsEl) armsEl.checked = preset.arms;
        if (Musterzustand.peMode === 'region') peRegionGenerate();
    });
    ['pe-region-zmin', 'pe-region-zmax', 'pe-region-grow',
        'pe-region-looseness'].forEach(id => { document.getElementById(id)?.addEventListener('change',
            () => { if (Musterzustand.peMode === 'region') peRegionGenerate(); }); });
    document.getElementById('pe-region-arms')?.addEventListener('change', () => { if (Musterzustand.peMode
        === 'region') peRegionGenerate(); });
    bindSlider('pe-roughness', 'pe-roughness-val', v => (v / 100).toFixed(2)); bindSlider('pe-metalness',
        'pe-metalness-val', v => (v / 100).toFixed(2));
    ['pe-color', 'pe-roughness', 'pe-metalness'].forEach(id => {
        const el = document.getElementById(id); if (!el) return;
        el.addEventListener('input', () => {
            const gewaehlt = state._selectedItem;
            let mesh = null;
            if (gewaehlt && (gewaehlt.type === 'cloth'
                             || gewaehlt.type === 'garment')) {
                mesh = state.clothMeshes[gewaehlt.id]
                    || state.garmentMeshes[gewaehlt.id];
            }
            if (!mesh) mesh = state.clothMeshes[pePreviewKey]; if (!mesh) return;
            if (id === 'pe-color') mesh.material.color.set(el.value); else if (id
                === 'pe-roughness') mesh.material.roughness = parseInt(el.value) / 100; else if (id
                    === 'pe-metalness') mesh.material.metalness = parseInt(el.value) / 100;
        });
    });
    document.getElementById('pe-generate')?.addEventListener('click', () => { if (Musterzustand.peMode
        === 'region') peRegionGenerate(); else peGenerate3D(); });
    document.getElementById('pe-delete')?.addEventListener('click', () => removeClothRegion(pePreviewKey));
    document.getElementById('pe-save')?.addEventListener('click', () => peSaveToLibrary());
    document.getElementById('garment-edit-pattern')?.addEventListener('click',
        () => { if (state.selectedGarmentId) peLoadFromGarment(state.selectedGarmentId); });

    initVertexEditorBindings();
    peRender();
    Protokoll.debug('Viewer', 'Pattern Editor initialized');
}

// Register
fn.peRegionGenerate = peRegionGenerate;
fn.peGenerate3D = peGenerate3D;
fn.peLoadFromGarment = peLoadFromGarment;
fn.peSetMode = peSetMode;
// Was `muster_maus.js` braucht — ueber das Register statt per Import, sonst
// entstuende der Kreis pattern_editor -> muster_maus -> pattern_editor.
fn.peUpdatePanelList = peUpdatePanelList;
fn.peUpdateStitchList = peUpdateStitchList;
fn.peSetModeButtons = _peSetModeButtons;
fn.peCanvasToWorld = peCanvasToWorld;
fn.peWorldToCanvas = peWorldToCanvas;
fn.getPeMode = () => Musterzustand.peMode;
fn.setPeMode = (v) => { Musterzustand.peMode = v; _peSetModeButtons(); };
