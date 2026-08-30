/**
 * Schnittmuster zeichnen und Treffer darin finden.
 *
 * Aus pattern_editor.js herausgeloest (Umbau 16.08.2026).
 */
import { Musterzustand } from './muster_zustand.js';
import { PE_COLORS, peCanvasToWorld, peWorldToCanvas } from './pattern_editor.js';


export function peRender() {
    const canvas = document.getElementById('pe-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    ctx.strokeStyle = '#333'; ctx.lineWidth = 0.5;
    const step = Musterzustand.peZoom;
    const ox = Musterzustand.pePan.x % step, oy = Musterzustand.pePan.y % step;
    for (let x = ox; x < W; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = oy; y < H; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    ctx.strokeStyle = '#555'; ctx.lineWidth = 1;
    const step10 = Musterzustand.peZoom * 10;
    const ox10 = Musterzustand.pePan.x % step10, oy10 = Musterzustand.pePan.y % step10;
    for (let x = ox10; x < W; x += step10) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = oy10; y < H; y += step10) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    const [zx, zy] = peWorldToCanvas(0, 0);
    ctx.strokeStyle = '#666'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(zx - 8, zy); ctx.lineTo(zx + 8, zy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(zx, zy - 8); ctx.lineTo(zx, zy + 8); ctx.stroke();

    const panelNames = Object.keys(Musterzustand.pePattern.panels);
    panelNames.forEach((name, pi) => {
        const panel = Musterzustand.pePattern.panels[name];
        const color = PE_COLORS[pi % PE_COLORS.length];
        const isActive = (name === Musterzustand.peActivePanel);
        panel.edges.forEach((edge, ei) => {
            const p0 = peWorldToCanvas(...panel.vertices[edge.endpoints[0]]);
            const p1 = peWorldToCanvas(...panel.vertices[edge.endpoints[1]]);
            ctx.strokeStyle = (isActive && Musterzustand.peSelectedEdge && Musterzustand.peSelectedEdge.panel
                === name && Musterzustand.peSelectedEdge.index === ei) ? '#fff' : color;
            ctx.lineWidth = isActive ? 2.5 : 1.5;
            ctx.beginPath();
            if (edge.curvature) {
                const cp = peWorldToCanvas(...edge.curvature);
                ctx.moveTo(p0[0], p0[1]);
                ctx.quadraticCurveTo(cp[0], cp[1], p1[0], p1[1]);
            }
            else { ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); }
            ctx.stroke();
        });
        panel.vertices.forEach((v, vi) => {
            const [cx, cy] = peWorldToCanvas(v[0], v[1]);
            const isSel = isActive && Musterzustand.peSelectedVertex && Musterzustand.peSelectedVertex.panel === name && Musterzustand.peSelectedVertex.index === vi;
            ctx.fillStyle = isSel ? '#fff' : color;
            ctx.beginPath(); ctx.arc(cx, cy, isSel ? 5 : 3.5, 0, Math.PI * 2); ctx.fill();
        });
        panel.edges.forEach((edge) => {
            if (!edge.curvature) return;
            const cp = peWorldToCanvas(...edge.curvature);
            ctx.fillStyle = '#888'; ctx.beginPath(); ctx.arc(cp[0], cp[1], 3, 0, Math.PI * 2); ctx.fill();
        });
    });

    Musterzustand.pePattern.stitches.forEach((st) => {
        const pA = Musterzustand.pePattern.panels[st.panelA]; const pB = Musterzustand.pePattern.panels[st.panelB];
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
    if (statusEl) { const [wx, wy] = peCanvasToWorld(Musterzustand.peLastMouse.x, Musterzustand.peLastMouse.y);
        statusEl.textContent = `${wx.toFixed(1)}, ${wy.toFixed(1)} cm    ${Math.round(Musterzustand.peZoom / 2 * 100)}%`; }
}

export function _peMidpoint(panel, edge) { const v0 = panel.vertices[edge.endpoints[0]];
    const v1 = panel.vertices[edge.endpoints[1]]; return [(v0[0] + v1[0]) / 2, (v0[1] + v1[1]) / 2]; }

export function _peHitVertex(cx, cy, threshold) {
    const thr = threshold || 8;
    for (const name of Object.keys(Musterzustand.pePattern.panels)) {
        const panel = Musterzustand.pePattern.panels[name];
        for (let i = 0; i < panel.vertices.length; i++) { const [vx, vy] = peWorldToCanvas(...panel.vertices[i]);
            if (Math.hypot(cx - vx, cy - vy) < thr) return {panel: name, index: i}; }
    }
    return null;
}

export function _peHitEdge(cx, cy, threshold) {
    const thr = threshold || 6;
    for (const name of Object.keys(Musterzustand.pePattern.panels)) {
        const panel = Musterzustand.pePattern.panels[name];
        for (let i = 0; i < panel.edges.length; i++) { const edge = panel.edges[i];
            const p0 = peWorldToCanvas(...panel.vertices[edge.endpoints[0]]);
                const p1 = peWorldToCanvas(...panel.vertices[edge.endpoints[1]]); const dist = _pePointToSegDist(cx, cy,
                    p0[0], p0[1], p1[0], p1[1]); if (dist < thr) return {panel: name, index: i}; }
    }
    return null;
}

export function _pePointToSegDist(px, py, x1, y1, x2, y2) { const dx = x2 - x1, dy = y2 - y1; const lenSq = dx * dx
    + dy * dy; if (lenSq < 1e-6) return Math.hypot(px - x1, py - y1); let t = ((px - x1) * dx + (py - y1) * dy) / lenSq;
        t = Math.max(0, Math.min(1, t)); return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)); }

export function _peHitControlPoint(cx, cy, threshold) {
    const thr = threshold || 8;
    for (const name of Object.keys(Musterzustand.pePattern.panels)) {
        const panel = Musterzustand.pePattern.panels[name];
        for (let i = 0; i < panel.edges.length; i++) { const edge = panel.edges[i]; if (!edge.curvature) continue;
            const cp = peWorldToCanvas(...edge.curvature); if (Math.hypot(cx - cp[0], cy
                - cp[1]) < thr) return {panel: name, edgeIndex: i}; }
    }
    return null;
}
