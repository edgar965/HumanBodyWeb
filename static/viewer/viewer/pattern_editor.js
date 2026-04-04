/**
 * Viewer — Pattern Editor (2D canvas for garment panels/stitches + region generate).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords, bindSlider, sliderVal, buildBodyQueryString } from './utils.js';
import { removeClothRegion } from './cloth.js';
import { ensureSkinned } from './skinning.js';
import { veEnterEditMode, veExitEditMode, initVertexEditorBindings, isVeActive } from './vertex_editor.js';

let pePattern = { panels: {}, stitches: [] };
let peActivePanel = null;
let peMode = 'select';
let peSelectedVertex = null;
let peSelectedEdge = null;
let peStitchFirst = null;
let pePan = {x: 144, y: 200};
let peZoom = 2.0;
const pePreviewKey = 'pe_preview';
let peDragging = null;
let pePanning = false;
let pePanStart = null;
const PE_COLORS = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c'];
let peLastMouse = {x: 0, y: 0};

const PE_REGION_PRESETS = {
    custom:    {z_min: 60, z_max: 140, arms: false, grow: 2, looseness: 30},
    top:       {z_min: 80, z_max: 155, arms: true,  grow: 2, looseness: 30},
    pants:     {z_min: 0,  z_max: 105, arms: false, grow: 2, looseness: 30},
    skirt:     {z_min: 55, z_max: 100, arms: false, grow: 3, looseness: 40},
    full:      {z_min: 0,  z_max: 155, arms: true,  grow: 2, looseness: 30},
    underwear: {z_min: 55, z_max: 100, arms: false, grow: 1, looseness: 20},
    shoes:     {z_min: 0,  z_max: 15,  arms: false, grow: 2, looseness: 20},
};

function peWorldToCanvas(wx, wy) { return [pePan.x + wx * peZoom, pePan.y - wy * peZoom]; }
function peCanvasToWorld(cx, cy) { return [(cx - pePan.x) / peZoom, (pePan.y - cy) / peZoom]; }

function peRender() {
    const canvas = document.getElementById('pe-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    ctx.strokeStyle = '#333'; ctx.lineWidth = 0.5;
    const step = peZoom;
    const ox = pePan.x % step, oy = pePan.y % step;
    for (let x = ox; x < W; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = oy; y < H; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    ctx.strokeStyle = '#555'; ctx.lineWidth = 1;
    const step10 = peZoom * 10;
    const ox10 = pePan.x % step10, oy10 = pePan.y % step10;
    for (let x = ox10; x < W; x += step10) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = oy10; y < H; y += step10) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    const [zx, zy] = peWorldToCanvas(0, 0);
    ctx.strokeStyle = '#666'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(zx - 8, zy); ctx.lineTo(zx + 8, zy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(zx, zy - 8); ctx.lineTo(zx, zy + 8); ctx.stroke();

    const panelNames = Object.keys(pePattern.panels);
    panelNames.forEach((name, pi) => {
        const panel = pePattern.panels[name];
        const color = PE_COLORS[pi % PE_COLORS.length];
        const isActive = (name === peActivePanel);
        panel.edges.forEach((edge, ei) => {
            const p0 = peWorldToCanvas(...panel.vertices[edge.endpoints[0]]);
            const p1 = peWorldToCanvas(...panel.vertices[edge.endpoints[1]]);
            ctx.strokeStyle = (isActive && peSelectedEdge && peSelectedEdge.panel === name && peSelectedEdge.index === ei) ? '#fff' : color;
            ctx.lineWidth = isActive ? 2.5 : 1.5;
            ctx.beginPath();
            if (edge.curvature) { const cp = peWorldToCanvas(...edge.curvature); ctx.moveTo(p0[0], p0[1]); ctx.quadraticCurveTo(cp[0], cp[1], p1[0], p1[1]); }
            else { ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); }
            ctx.stroke();
        });
        panel.vertices.forEach((v, vi) => {
            const [cx, cy] = peWorldToCanvas(v[0], v[1]);
            const isSel = isActive && peSelectedVertex && peSelectedVertex.panel === name && peSelectedVertex.index === vi;
            ctx.fillStyle = isSel ? '#fff' : color;
            ctx.beginPath(); ctx.arc(cx, cy, isSel ? 5 : 3.5, 0, Math.PI * 2); ctx.fill();
        });
        panel.edges.forEach((edge) => {
            if (!edge.curvature) return;
            const cp = peWorldToCanvas(...edge.curvature);
            ctx.fillStyle = '#888'; ctx.beginPath(); ctx.arc(cp[0], cp[1], 3, 0, Math.PI * 2); ctx.fill();
        });
    });

    pePattern.stitches.forEach((st) => {
        const pA = pePattern.panels[st.panelA]; const pB = pePattern.panels[st.panelB];
        if (!pA || !pB) return;
        const eA = pA.edges[st.edgeA]; const eB = pB.edges[st.edgeB];
        if (!eA || !eB) return;
        const midA = _peMidpoint(pA, eA); const midB = _peMidpoint(pB, eB);
        const cA = peWorldToCanvas(...midA); const cB = peWorldToCanvas(...midB);
        ctx.strokeStyle = '#f1c40f'; ctx.lineWidth = 1; ctx.setLineDash([4, 3]);
        ctx.beginPath(); ctx.moveTo(cA[0], cA[1]); ctx.lineTo(cB[0], cB[1]); ctx.stroke();
        ctx.setLineDash([]);
    });

    const statusEl = document.getElementById('pe-status');
    if (statusEl) { const [wx, wy] = peCanvasToWorld(peLastMouse.x, peLastMouse.y); statusEl.textContent = `${wx.toFixed(1)}, ${wy.toFixed(1)} cm    ${Math.round(peZoom / 2 * 100)}%`; }
}

function _peMidpoint(panel, edge) { const v0 = panel.vertices[edge.endpoints[0]]; const v1 = panel.vertices[edge.endpoints[1]]; return [(v0[0] + v1[0]) / 2, (v0[1] + v1[1]) / 2]; }

function _peHitVertex(cx, cy, threshold) {
    const thr = threshold || 8;
    for (const name of Object.keys(pePattern.panels)) {
        const panel = pePattern.panels[name];
        for (let i = 0; i < panel.vertices.length; i++) { const [vx, vy] = peWorldToCanvas(...panel.vertices[i]); if (Math.hypot(cx - vx, cy - vy) < thr) return {panel: name, index: i}; }
    }
    return null;
}

function _peHitEdge(cx, cy, threshold) {
    const thr = threshold || 6;
    for (const name of Object.keys(pePattern.panels)) {
        const panel = pePattern.panels[name];
        for (let i = 0; i < panel.edges.length; i++) { const edge = panel.edges[i]; const p0 = peWorldToCanvas(...panel.vertices[edge.endpoints[0]]); const p1 = peWorldToCanvas(...panel.vertices[edge.endpoints[1]]); const dist = _pePointToSegDist(cx, cy, p0[0], p0[1], p1[0], p1[1]); if (dist < thr) return {panel: name, index: i}; }
    }
    return null;
}

function _pePointToSegDist(px, py, x1, y1, x2, y2) { const dx = x2 - x1, dy = y2 - y1; const lenSq = dx * dx + dy * dy; if (lenSq < 1e-6) return Math.hypot(px - x1, py - y1); let t = ((px - x1) * dx + (py - y1) * dy) / lenSq; t = Math.max(0, Math.min(1, t)); return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)); }

function _peHitControlPoint(cx, cy, threshold) {
    const thr = threshold || 8;
    for (const name of Object.keys(pePattern.panels)) {
        const panel = pePattern.panels[name];
        for (let i = 0; i < panel.edges.length; i++) { const edge = panel.edges[i]; if (!edge.curvature) continue; const cp = peWorldToCanvas(...edge.curvature); if (Math.hypot(cx - cp[0], cy - cp[1]) < thr) return {panel: name, edgeIndex: i}; }
    }
    return null;
}

function _peSetRegionMode(active) {
    const patternControls = document.getElementById('pe-pattern-controls');
    const regionControls = document.getElementById('pe-region-controls');
    const wrapSection = document.getElementById('pe-wrap-section');
    if (active) { if (patternControls) patternControls.style.display = 'none'; if (wrapSection) wrapSection.style.display = 'none'; if (regionControls) regionControls.style.display = ''; }
    else { if (patternControls) patternControls.style.display = ''; if (wrapSection) wrapSection.style.display = ''; if (regionControls) regionControls.style.display = 'none'; }
}

function _peSetModeButtons() {
    document.querySelectorAll('#pe-mode-btns .btn-toggle').forEach(btn => { btn.classList.toggle('active', btn.dataset.mode === peMode); });
    if (peMode !== 'edit' && isVeActive()) veExitEditMode();
    if (peMode === 'edit') veEnterEditMode();
    else _peSetRegionMode(peMode === 'region');
}

function peSetMode(mode) { peMode = mode; _peSetModeButtons(); }

function peUpdatePanelList() {
    const list = document.getElementById('pe-panel-list');
    if (!list) return;
    const names = Object.keys(pePattern.panels);
    const PLACEMENT_BADGES = {flat:'',front:'[F]',back:'[B]',left:'[L]',right:'[R]',sleeve_L:'[SL]',sleeve_R:'[SR]'};
    list.innerHTML = names.map((name, i) => {
        const color = PE_COLORS[i % PE_COLORS.length]; const active = name === peActivePanel;
        const p = pePattern.panels[name]; const nv = p.vertices.length; const closed = p.closed ? 'closed' : 'open';
        const badge = PLACEMENT_BADGES[p.placement || 'flat'] || '';
        return `<div class="pe-panel-item${active ? ' active' : ''}" data-name="${name}" style="cursor:pointer;padding:3px 6px;border-left:3px solid ${color};margin-bottom:2px;background:${active ? 'var(--bg-highlight)' : 'transparent'};border-radius:2px;font-size:0.8rem;"><span style="color:${color};">&#9679;</span> ${name} ${badge ? `<span style="color:#f39c12;font-size:0.7rem;">${badge}</span> ` : ''}<span style="color:var(--text-muted);font-size:0.72rem;">(${nv}v, ${closed})</span></div>`;
    }).join('');
    list.querySelectorAll('.pe-panel-item').forEach(el => {
        el.addEventListener('click', () => { peActivePanel = el.dataset.name; peSelectedVertex = null; peSelectedEdge = null; peUpdatePanelList(); _peSyncPlacementDropdown(); peRender(); });
    });
}

function peUpdateStitchList() {
    const list = document.getElementById('pe-stitch-list'); const countEl = document.getElementById('pe-stitch-count');
    if (!list) return;
    if (countEl) countEl.textContent = `(${pePattern.stitches.length})`;
    list.innerHTML = pePattern.stitches.map((st, i) => `<div style="font-size:0.78rem;padding:2px 4px;color:var(--text-muted);">${st.panelA}.e${st.edgeA} \u2194 ${st.panelB}.e${st.edgeB} <span class="pe-stitch-del" data-idx="${i}" style="cursor:pointer;color:#e74c3c;margin-left:4px;" title="Remove">\u2715</span></div>`).join('');
    list.querySelectorAll('.pe-stitch-del').forEach(el => { el.addEventListener('click', () => { pePattern.stitches.splice(parseInt(el.dataset.idx), 1); peUpdateStitchList(); peRender(); }); });
}

function _peSyncPlacementDropdown() { const dd = document.getElementById('pe-placement'); if (!dd || !peActivePanel) return; const p = pePattern.panels[peActivePanel]; dd.value = (p && p.placement) || 'flat'; }

async function peRegionGenerate() {
    const genBtn = document.getElementById('pe-generate'); if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status'); if (statusEl) statusEl.textContent = 'Generating region...';
    ensureSkinned();
    const bodyQs = buildBodyQueryString();
    const zMin = (sliderVal('pe-region-zmin') / 100).toFixed(3); const zMax = (sliderVal('pe-region-zmax') / 100).toFixed(3);
    const arms = document.getElementById('pe-region-arms')?.checked ? '1' : '0'; const grow = sliderVal('pe-region-grow');
    const looseness = (sliderVal('pe-region-looseness') / 100).toFixed(3); const category = document.getElementById('pe-region-category')?.value || 'custom';
    const regionQs = `z_min=${zMin}&z_max=${zMax}&include_arms=${arms}&grow=${grow}&looseness=${looseness}&category=${category}`;
    try {
        const resp = await fetch(`/api/character/pattern/region/generate/?${bodyQs}&${regionQs}`);
        const data = await resp.json();
        if (data.error) { if (statusEl) statusEl.textContent = `Error: ${data.error}`; if (genBtn) genBtn.disabled = false; return; }
        removeClothRegion(pePreviewKey);
        const vertBuf = base64ToFloat32(data.vertices); blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces); const normalBuf = base64ToFloat32(data.normals); blenderToThreeCoords(normalBuf);
        const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3)); geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        const colorPicker = document.getElementById('pe-color'); const matColor = colorPicker ? new THREE.Color(colorPicker.value) : new THREE.Color(0.3, 0.35, 0.5);
        const roughness = (sliderVal('pe-roughness') / 100); const metalness = (sliderVal('pe-metalness') / 100);
        const mat = new THREE.MeshStandardMaterial({ color: matColor, roughness, metalness, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
        let mesh;
        if (state.isSkinned && state.rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices); const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4)); geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat); mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        } else { mesh = new THREE.Mesh(geo, mat); }
        state.clothMeshes[pePreviewKey] = mesh; state.clothParams[pePreviewKey] = {params: {}, color: '#' + mesh.material.color.getHexString()};
        state.scene.add(mesh); fn.updateEquippedList();
        if (statusEl) statusEl.textContent = `Region: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
    if (genBtn) genBtn.disabled = false;
}

async function peGenerate3D() {
    const genBtn = document.getElementById('pe-generate'); if (genBtn) genBtn.disabled = true;
    const statusEl = document.getElementById('pe-save-status'); if (statusEl) statusEl.textContent = 'Generating...';
    ensureSkinned();
    const bodyQs = buildBodyQueryString();
    try {
        const wrapCb = document.getElementById('pe-wrap'); const wrap = wrapCb ? wrapCb.checked : false;
        const wrapOffset = (sliderVal('pe-wrap-offset') || 6) / 1000; const wrapStiffness = (sliderVal('pe-wrap-stiffness') ?? 50) / 100;
        const resp = await fetch(`/api/character/pattern/generate/?${bodyQs}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({pattern: pePattern, wrap, offset: wrapOffset, stiffness: wrapStiffness}) });
        const data = await resp.json();
        if (data.error) { if (statusEl) statusEl.textContent = `Error: ${data.error}`; if (genBtn) genBtn.disabled = false; return; }
        removeClothRegion(pePreviewKey);
        const vertBuf = base64ToFloat32(data.vertices); blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces); const normalBuf = base64ToFloat32(data.normals); blenderToThreeCoords(normalBuf);
        const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3)); geo.setIndex(new THREE.BufferAttribute(faceBuf, 1)); geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        const colorPicker = document.getElementById('pe-color'); const matColor = colorPicker ? new THREE.Color(colorPicker.value) : new THREE.Color(0.3, 0.35, 0.5);
        const roughness = (sliderVal('pe-roughness') / 100); const metalness = (sliderVal('pe-metalness') / 100);
        const mat = new THREE.MeshStandardMaterial({ color: matColor, roughness, metalness, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
        let mesh;
        if (state.isSkinned && state.rigifySkeleton && data.skin_indices && data.skin_weights) {
            const siBuf = base64ToFloat32(data.skin_indices); const swBuf = base64ToFloat32(data.skin_weights);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4)); geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
            mesh = new THREE.SkinnedMesh(geo, mat); mesh.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        } else { mesh = new THREE.Mesh(geo, mat); }
        state.clothMeshes[pePreviewKey] = mesh; state.clothParams[pePreviewKey] = {params: {}, color: '#' + mesh.material.color.getHexString()};
        state.scene.add(mesh); fn.updateEquippedList();
        if (statusEl) statusEl.textContent = `Generated: ${data.vertex_count} verts, ${data.face_count} tris`;
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
    if (genBtn) genBtn.disabled = false;
}

async function peSaveToLibrary() {
    const name = document.getElementById('pe-save-name')?.value?.trim(); const category = document.getElementById('pe-save-category')?.value || 'custom';
    const statusEl = document.getElementById('pe-save-status'); if (!name) { if (statusEl) statusEl.textContent = 'Name is required'; return; }
    if (statusEl) statusEl.textContent = 'Saving...';
    const colorPicker = document.getElementById('pe-color'); const colorHex = colorPicker ? colorPicker.value : '#404870';
    const cr = parseInt(colorHex.slice(1, 3), 16) / 255; const cg = parseInt(colorHex.slice(3, 5), 16) / 255; const cb = parseInt(colorHex.slice(5, 7), 16) / 255;
    const bodyQs = buildBodyQueryString();
    try {
        const resp = await fetch(`/api/character/pattern/save/?${bodyQs}`, { method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pattern: pePattern, name, category, color: [cr, cg, cb], roughness: sliderVal('pe-roughness') / 100, metalness: sliderVal('pe-metalness') / 100, wrap: document.getElementById('pe-wrap')?.checked || false, offset: (sliderVal('pe-wrap-offset') || 6) / 1000, stiffness: (sliderVal('pe-wrap-stiffness') ?? 50) / 100 }) });
        const data = await resp.json();
        if (data.ok) { if (statusEl) statusEl.textContent = `Saved: ${data.garment_id}`; } else { if (statusEl) statusEl.textContent = `Error: ${data.error || 'Unknown'}`; }
    } catch (e) { if (statusEl) statusEl.textContent = `Error: ${e.message}`; }
}

async function peLoadFromGarment(garmentId) {
    try {
        const resp = await fetch(`/api/character/pattern/specification/?garment_id=${encodeURIComponent(garmentId)}`);
        const data = await resp.json();
        if (!data.ok || !data.pattern) { console.warn('No specification found for', garmentId, data.error); return false; }
        pePattern = data.pattern; if (!pePattern.stitches) pePattern.stitches = [];
        const names = Object.keys(pePattern.panels || {}); peActivePanel = names.length > 0 ? names[0] : null;
        peSelectedVertex = null; peSelectedEdge = null; peStitchFirst = null; peMode = 'select'; _peSetModeButtons(); _peAutoFit();
        peUpdatePanelList(); peUpdateStitchList(); peRender();
        const tabBtn = document.querySelector('.panel-tab[data-tab="tab-creator"]'); if (tabBtn) tabBtn.click();
        const nameEl = document.getElementById('pe-save-name'); if (nameEl) { const parts = garmentId.split('/'); nameEl.value = parts[parts.length - 1]; }
        const catEl = document.getElementById('pe-save-category');
        if (catEl) { const parts = garmentId.split('/'); if (parts.length > 1) { const cat = parts[0]; for (const opt of catEl.options) { if (opt.value === cat) { catEl.value = cat; break; } } } }
        console.log(`Pattern loaded from ${garmentId}: ${names.length} panels`); return true;
    } catch (e) { console.error('Failed to load pattern:', e); return false; }
}

function _peAutoFit() {
    const canvas = document.getElementById('pe-canvas'); if (!canvas) return;
    const W = canvas.width, H = canvas.height; const allVerts = [];
    for (const panel of Object.values(pePattern.panels || {})) for (const v of (panel.vertices || [])) allVerts.push(v);
    if (allVerts.length === 0) { pePan = {x: W/2, y: H/2}; peZoom = 2.0; return; }
    const xs = allVerts.map(v => v[0]), ys = allVerts.map(v => v[1]);
    const xMin = Math.min(...xs), xMax = Math.max(...xs), yMin = Math.min(...ys), yMax = Math.max(...ys);
    const pw = xMax - xMin || 20, ph = yMax - yMin || 20;
    const margin = 0.15; const zoomX = W * (1 - 2 * margin) / pw; const zoomY = H * (1 - 2 * margin) / ph;
    peZoom = Math.min(zoomX, zoomY); peZoom = Math.max(0.5, Math.min(20, peZoom));
    const cx = (xMin + xMax) / 2; const cy = (yMin + yMax) / 2;
    pePan.x = W / 2 - cx * peZoom; pePan.y = H / 2 + cy * peZoom;
}

function _peInitCanvas() {
    const canvas = document.getElementById('pe-canvas'); if (!canvas) return;
    canvas.addEventListener('mousedown', (e) => {
        const cx = e.offsetX, cy = e.offsetY;
        if (e.button === 1 || (e.button === 0 && e.ctrlKey)) { pePanning = true; pePanStart = {x: e.clientX, y: e.clientY, px: pePan.x, py: pePan.y}; e.preventDefault(); return; }
        if (e.button !== 0) return;
        if (peMode === 'select') {
            const cpHit = _peHitControlPoint(cx, cy); if (cpHit) { peDragging = {type: 'cp', panel: cpHit.panel, edgeIndex: cpHit.edgeIndex}; return; }
            const vHit = _peHitVertex(cx, cy); if (vHit) { peSelectedVertex = vHit; peSelectedEdge = null; peActivePanel = vHit.panel; peDragging = {type: 'vertex', panel: vHit.panel, index: vHit.index}; peRender(); peUpdatePanelList(); return; }
            const eHit = _peHitEdge(cx, cy); if (eHit) { peSelectedEdge = eHit; peSelectedVertex = null; peActivePanel = eHit.panel; peRender(); peUpdatePanelList(); return; }
            peSelectedVertex = null; peSelectedEdge = null; peRender();
        } else if (peMode === 'draw') {
            if (!peActivePanel || !pePattern.panels[peActivePanel]) return;
            const panel = pePattern.panels[peActivePanel]; const [wx, wy] = peCanvasToWorld(cx, cy);
            if (panel.vertices.length >= 3) { const [fx, fy] = peWorldToCanvas(...panel.vertices[0]); if (Math.hypot(cx - fx, cy - fy) < 10) { panel.edges.push({endpoints: [panel.vertices.length - 1, 0], curvature: null}); panel.closed = true; peMode = 'select'; _peSetModeButtons(); peRender(); peUpdatePanelList(); return; } }
            const vi = panel.vertices.length; panel.vertices.push([wx, wy]); if (vi > 0) panel.edges.push({endpoints: [vi - 1, vi], curvature: null}); peRender();
        } else if (peMode === 'stitch') {
            const eHit = _peHitEdge(cx, cy); if (!eHit) return;
            if (!peStitchFirst) { peStitchFirst = eHit; peSelectedEdge = eHit; peActivePanel = eHit.panel; peRender(); }
            else { if (eHit.panel !== peStitchFirst.panel) pePattern.stitches.push({panelA: peStitchFirst.panel, edgeA: peStitchFirst.index, panelB: eHit.panel, edgeB: eHit.index}); peUpdateStitchList(); peStitchFirst = null; peSelectedEdge = null; peRender(); }
        }
    });
    canvas.addEventListener('mousemove', (e) => {
        const cx = e.offsetX, cy = e.offsetY; peLastMouse = {x: cx, y: cy};
        if (pePanning && pePanStart) { pePan.x = pePanStart.px + (e.clientX - pePanStart.x); pePan.y = pePanStart.py + (e.clientY - pePanStart.y); peRender(); return; }
        if (peDragging) { const [wx, wy] = peCanvasToWorld(cx, cy); if (peDragging.type === 'vertex') pePattern.panels[peDragging.panel].vertices[peDragging.index] = [wx, wy]; else if (peDragging.type === 'cp') pePattern.panels[peDragging.panel].edges[peDragging.edgeIndex].curvature = [wx, wy]; peRender(); }
        const statusEl = document.getElementById('pe-status'); if (statusEl) { const [wx, wy] = peCanvasToWorld(cx, cy); statusEl.textContent = `${wx.toFixed(1)}, ${wy.toFixed(1)} cm    ${Math.round(peZoom / 2 * 100)}%`; }
    });
    canvas.addEventListener('mouseup', () => { peDragging = null; pePanning = false; pePanStart = null; });
    canvas.addEventListener('mouseleave', () => { peDragging = null; pePanning = false; pePanStart = null; });
    canvas.addEventListener('dblclick', (e) => {
        if (peMode !== 'select') return; const cx = e.offsetX, cy = e.offsetY; const eHit = _peHitEdge(cx, cy); if (eHit) {
            const edge = pePattern.panels[eHit.panel].edges[eHit.index]; if (edge.curvature) edge.curvature = null;
            else { const panel = pePattern.panels[eHit.panel]; const v0 = panel.vertices[edge.endpoints[0]]; const v1 = panel.vertices[edge.endpoints[1]]; const mx = (v0[0] + v1[0]) / 2, my = (v0[1] + v1[1]) / 2; const dx = v1[0] - v0[0], dy = v1[1] - v0[1]; const len = Math.hypot(dx, dy) || 1; edge.curvature = [mx + (-dy / len) * 5, my + (dx / len) * 5]; }
            peRender();
        }
    });
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault(); const cx = e.offsetX, cy = e.offsetY; const [wx, wy] = peCanvasToWorld(cx, cy);
        const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15; peZoom = Math.max(0.5, Math.min(20, peZoom * factor));
        pePan.x = cx - wx * peZoom; pePan.y = cy + wy * peZoom; peRender();
    }, {passive: false});
    canvas.addEventListener('contextmenu', e => e.preventDefault());
}

export function initPatternEditor() {
    const canvas = document.getElementById('pe-canvas'); if (!canvas) return;
    _peInitCanvas();
    document.querySelectorAll('#pe-mode-btns .btn-toggle').forEach(btn => { btn.addEventListener('click', () => { peMode = btn.dataset.mode; peStitchFirst = null; _peSetModeButtons(); }); });
    document.getElementById('pe-add-panel')?.addEventListener('click', () => {
        const names = Object.keys(pePattern.panels); const defaultName = `Panel${names.length + 1}`;
        const name = prompt('Panel name:', defaultName); if (!name || !name.trim()) return; const trimmed = name.trim();
        if (pePattern.panels[trimmed]) { alert('Panel already exists'); return; }
        pePattern.panels[trimmed] = {vertices: [], edges: [], closed: false}; peActivePanel = trimmed; peMode = 'draw'; _peSetModeButtons(); peUpdatePanelList(); peRender();
    });
    document.getElementById('pe-del-panel')?.addEventListener('click', () => {
        if (!peActivePanel) return; pePattern.stitches = pePattern.stitches.filter(s => s.panelA !== peActivePanel && s.panelB !== peActivePanel);
        delete pePattern.panels[peActivePanel]; const names = Object.keys(pePattern.panels); peActivePanel = names.length > 0 ? names[0] : null;
        peSelectedVertex = null; peSelectedEdge = null; peUpdatePanelList(); peUpdateStitchList(); peRender();
    });
    document.getElementById('pe-placement')?.addEventListener('change', (e) => { if (peActivePanel && pePattern.panels[peActivePanel]) { pePattern.panels[peActivePanel].placement = e.target.value; peUpdatePanelList(); } });
    document.getElementById('pe-wrap')?.addEventListener('change', (e) => { const sliders = document.getElementById('pe-wrap-sliders'); if (sliders) sliders.style.display = e.target.checked ? '' : 'none'; });
    bindSlider('pe-wrap-offset', 'pe-wrap-offset-val', v => v); bindSlider('pe-wrap-stiffness', 'pe-wrap-stiffness-val', v => (v / 100).toFixed(2));
    bindSlider('pe-region-zmin', 'pe-region-zmin-val', v => (v / 100).toFixed(2)); bindSlider('pe-region-zmax', 'pe-region-zmax-val', v => (v / 100).toFixed(2));
    bindSlider('pe-region-grow', 'pe-region-grow-val', v => v); bindSlider('pe-region-looseness', 'pe-region-looseness-val', v => (v / 100).toFixed(2));
    document.getElementById('pe-region-category')?.addEventListener('change', (e) => {
        const preset = PE_REGION_PRESETS[e.target.value]; if (!preset) return;
        const setS = (id, val) => { const el = document.getElementById(id); if (el) { el.value = val; el.dispatchEvent(new Event('input')); } };
        setS('pe-region-zmin', preset.z_min); setS('pe-region-zmax', preset.z_max); setS('pe-region-grow', preset.grow); setS('pe-region-looseness', preset.looseness);
        const armsEl = document.getElementById('pe-region-arms'); if (armsEl) armsEl.checked = preset.arms;
        if (peMode === 'region') peRegionGenerate();
    });
    ['pe-region-zmin', 'pe-region-zmax', 'pe-region-grow', 'pe-region-looseness'].forEach(id => { document.getElementById(id)?.addEventListener('change', () => { if (peMode === 'region') peRegionGenerate(); }); });
    document.getElementById('pe-region-arms')?.addEventListener('change', () => { if (peMode === 'region') peRegionGenerate(); });
    bindSlider('pe-roughness', 'pe-roughness-val', v => (v / 100).toFixed(2)); bindSlider('pe-metalness', 'pe-metalness-val', v => (v / 100).toFixed(2));
    ['pe-color', 'pe-roughness', 'pe-metalness'].forEach(id => {
        const el = document.getElementById(id); if (!el) return;
        el.addEventListener('input', () => {
            let mesh = null; if (state._selectedItem && (state._selectedItem.type === 'cloth' || state._selectedItem.type === 'garment')) mesh = state.clothMeshes[state._selectedItem.id] || state.garmentMeshes[state._selectedItem.id];
            if (!mesh) mesh = state.clothMeshes[pePreviewKey]; if (!mesh) return;
            if (id === 'pe-color') mesh.material.color.set(el.value); else if (id === 'pe-roughness') mesh.material.roughness = parseInt(el.value) / 100; else if (id === 'pe-metalness') mesh.material.metalness = parseInt(el.value) / 100;
        });
    });
    document.getElementById('pe-generate')?.addEventListener('click', () => { if (peMode === 'region') peRegionGenerate(); else peGenerate3D(); });
    document.getElementById('pe-delete')?.addEventListener('click', () => removeClothRegion(pePreviewKey));
    document.getElementById('pe-save')?.addEventListener('click', () => peSaveToLibrary());
    document.getElementById('garment-edit-pattern')?.addEventListener('click', () => { if (state.selectedGarmentId) peLoadFromGarment(state.selectedGarmentId); });

    initVertexEditorBindings();
    peRender();
    console.log('Pattern Editor initialized');
}

// Register
fn.initPatternEditor = initPatternEditor;
fn.peRegionGenerate = peRegionGenerate;
fn.peGenerate3D = peGenerate3D;
fn.peLoadFromGarment = peLoadFromGarment;
fn.peSetMode = peSetMode;
fn.getPeMode = () => peMode;
fn.setPeMode = (v) => { peMode = v; _peSetModeButtons(); };
