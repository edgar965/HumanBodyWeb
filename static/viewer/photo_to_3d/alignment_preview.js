/**
 * Photo To 3D — Alignment preview rendering (Textur tab visualization).
 */
import { state, API } from './state.js';
import { fn } from './registry.js';

/** Draw a smooth closed contour using quadratic curves through midpoints */
export function drawSmoothContour(ctx, pts) {
    if (pts.length < 3) return;
    const n = pts.length;
    ctx.beginPath();
    ctx.moveTo((pts[n-1][0] + pts[0][0]) / 2, (pts[n-1][1] + pts[0][1]) / 2);
    for (let i = 0; i < n; i++) {
        const next = (i + 1) % n;
        const mx = (pts[i][0] + pts[next][0]) / 2;
        const my = (pts[i][1] + pts[next][1]) / 2;
        ctx.quadraticCurveTo(pts[i][0], pts[i][1], mx, my);
    }
    ctx.closePath();
}

/** Draw a smooth closed contour with a per-point transform function */
export function drawSmoothContourTransformed(ctx, pts, transformFn) {
    if (pts.length < 3) return;
    const n = pts.length;
    const tpts = pts.map(([px, py]) => transformFn(px, py));
    ctx.beginPath();
    ctx.moveTo((tpts[n-1][0] + tpts[0][0]) / 2, (tpts[n-1][1] + tpts[0][1]) / 2);
    for (let i = 0; i < n; i++) {
        const next = (i + 1) % n;
        const mx = (tpts[i][0] + tpts[next][0]) / 2;
        const my = (tpts[i][1] + tpts[next][1]) / 2;
        ctx.quadraticCurveTo(tpts[i][0], tpts[i][1], mx, my);
    }
    ctx.closePath();
}

export async function renderAlignmentPreview() {
    const previewDiv = document.getElementById('alignment-preview');
    const origImg = document.getElementById('preview-original');
    const projCanvas = document.getElementById('preview-projection');
    if (!previewDiv || !projCanvas || !state.currentJobId) return;

    const photoSrc = document.getElementById('photo-img')?.src;
    if (!photoSrc) return;
    origImg.src = photoSrc;
    previewDiv.style.display = 'block';

    try {
        if (!state._previewDataCache || state._previewDataCache._jobId !== state.currentJobId) {
            const sResp = await fetch(`${API}/photo-job/${state.currentJobId}/silhouette/`);
            const sData = await sResp.json();
            state._previewDataCache = { ...sData, _jobId: state.currentJobId };
        }
        const sData = state._previewDataCache;
        if (!sData.ok) return;

        const img = new Image();
        img.crossOrigin = 'anonymous';
        await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
            img.src = photoSrc;
        });

        const cw = sData.photo_width;
        const ch = sData.photo_height;
        projCanvas.width = cw;
        projCanvas.height = ch;
        const ctx = projCanvas.getContext('2d');

        ctx.drawImage(img, 0, 0, cw, ch);

        const lw = Math.max(3, cw * 0.006);

        // Body contour
        if (sData.body_contour && sData.body_contour.length > 2) {
            ctx.save();
            ctx.fillStyle = 'rgba(233, 69, 96, 0.2)';
            ctx.strokeStyle = 'rgba(233, 69, 96, 0.7)';
            ctx.lineWidth = lw;
            drawSmoothContour(ctx, sData.body_contour);
            ctx.fill(); ctx.stroke();
            ctx.restore();
        }

        // Face contour
        if (sData.face_contour && sData.face_contour.length > 2) {
            ctx.save();
            ctx.fillStyle = 'rgba(155, 89, 182, 0.15)';
            ctx.strokeStyle = 'rgba(155, 89, 182, 0.6)';
            ctx.lineWidth = lw * 0.8;
            drawSmoothContour(ctx, sData.face_contour);
            ctx.fill(); ctx.stroke();
            ctx.restore();
        }

        // Mesh projection bbox
        const mb = sData.mesh_bbox;
        if (mb) {
            ctx.save();
            ctx.setLineDash([lw * 3, lw * 2]);
            ctx.strokeStyle = 'rgba(0, 102, 255, 0.5)';
            ctx.lineWidth = lw * 0.7;
            ctx.strokeRect(mb.x, mb.y, mb.w, mb.h);
            ctx.setLineDash([]);
            ctx.font = `bold ${Math.max(14, cw * 0.025)}px sans-serif`;
            ctx.fillStyle = 'rgba(0, 102, 255, 0.6)';
            ctx.fillText('SMPL-X Mesh', mb.x + 4, mb.y - 6);
            ctx.restore();
        }

        // Face bbox from mesh
        const fbm = sData.face_bbox_mesh;
        if (fbm) {
            ctx.save();
            ctx.setLineDash([lw * 2, lw * 2]);
            ctx.strokeStyle = 'rgba(204, 0, 0, 0.4)';
            ctx.lineWidth = lw * 0.6;
            ctx.strokeRect(fbm.x, fbm.y, fbm.w, fbm.h);
            ctx.setLineDash([]);
            ctx.font = `bold ${Math.max(11, cw * 0.018)}px sans-serif`;
            ctx.fillStyle = 'rgba(204, 0, 0, 0.5)';
            ctx.fillText('Gesicht (Mesh)', fbm.x + 3, fbm.y - 4);
            ctx.restore();
        }

        // MediaPipe face detection
        const fbd = sData.face_bbox_detected;
        if (fbd && fbd !== fbm) {
            ctx.save();
            ctx.setLineDash([lw * 3, lw * 2]);
            ctx.strokeStyle = 'rgba(204, 0, 204, 0.4)';
            ctx.lineWidth = lw * 0.6;
            ctx.strokeRect(fbd.x, fbd.y, fbd.w, fbd.h);
            ctx.setLineDash([]);
            ctx.font = `bold ${Math.max(11, cw * 0.018)}px sans-serif`;
            ctx.fillStyle = 'rgba(204, 0, 204, 0.5)';
            ctx.fillText('Gesicht (Foto)', fbd.x + 3, fbd.y - 4);
            ctx.restore();
        }

        // YOLO person bbox
        if (sData.yolo_bbox) {
            const [x1, y1, x2, y2] = sData.yolo_bbox;
            ctx.save();
            ctx.setLineDash([lw * 3, lw * 2]);
            ctx.strokeStyle = 'rgba(0, 204, 68, 0.4)';
            ctx.lineWidth = lw * 0.7;
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
            ctx.setLineDash([]);
            ctx.font = `bold ${Math.max(11, cw * 0.018)}px sans-serif`;
            ctx.fillStyle = 'rgba(0, 204, 68, 0.5)';
            ctx.fillText('YOLO Person', x1 + 3, y1 - 4);
            ctx.restore();
        }

        // Status text
        const infoEl = previewDiv.querySelector('.alignment-status');
        if (infoEl) {
            if (sData.has_alignment) {
                const method = sData.alignment_method || 'pipeline';
                infoEl.textContent = `Auto-Alignment aktiv (${method})`;
            } else {
                infoEl.textContent = 'Standard-Projektion (Bild-Mitte)';
            }
        }

        // Click handler for zoom dialog
        projCanvas.style.cursor = 'zoom-in';
        projCanvas.onclick = () => openPreviewDialog(projCanvas);

        // Save projection preview
        try {
            const dataUrl = projCanvas.toDataURL('image/jpeg', 0.85);
            await fetch(`${API}/photo-job/${state.currentJobId}/save-projection/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: dataUrl }),
            });
            console.log('[Photo->3D] Projection preview saved');
        } catch (saveErr) {
            console.warn('Failed to save projection preview:', saveErr);
        }

    } catch (e) {
        console.warn('Alignment preview failed:', e);
    }
}

/** Open a fullscreen dialog showing the projection canvas with mouse-wheel zoom. */
function openPreviewDialog(srcCanvas) {
    let old = document.getElementById('preview-zoom-dialog');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'preview-zoom-dialog';
    Object.assign(overlay.style, {
        position: 'fixed', inset: '0', zIndex: '11000',
        background: 'rgba(0,0,0,0.85)', display: 'flex',
        alignItems: 'center', justifyContent: 'center',
        backdropFilter: 'blur(4px)', cursor: 'zoom-out',
    });

    const wrap = document.createElement('div');
    Object.assign(wrap.style, {
        position: 'relative', overflow: 'hidden',
        maxWidth: '92vw', maxHeight: '90vh',
        borderRadius: '8px', border: '1px solid #444',
    });

    const c = document.createElement('canvas');
    c.width = srcCanvas.width;
    c.height = srcCanvas.height;
    const cCtx = c.getContext('2d');
    cCtx.drawImage(srcCanvas, 0, 0);

    let scale = 1;
    let tx = 0, ty = 0;
    let dragging = false, lastX = 0, lastY = 0;

    const vw = window.innerWidth * 0.92;
    const vh = window.innerHeight * 0.90;
    const fitScale = Math.min(vw / c.width, vh / c.height, 1);
    const dispW = Math.round(c.width * fitScale);
    const dispH = Math.round(c.height * fitScale);
    Object.assign(c.style, {
        width: dispW + 'px', height: dispH + 'px',
        transformOrigin: '0 0', display: 'block',
    });

    function applyTransform() {
        c.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
    }

    c.addEventListener('wheel', (e) => {
        e.preventDefault();
        const rect = c.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const oldScale = scale;
        scale *= e.deltaY < 0 ? 1.15 : 0.87;
        scale = Math.max(0.5, Math.min(scale, 10));
        tx -= mx * (scale - oldScale);
        ty -= my * (scale - oldScale);
        applyTransform();
    }, { passive: false });

    c.addEventListener('mousedown', (e) => {
        if (e.button === 0) { dragging = true; lastX = e.clientX; lastY = e.clientY; c.style.cursor = 'grabbing'; }
    });
    window.addEventListener('mousemove', function _move(e) {
        if (!dragging) return;
        tx += e.clientX - lastX;
        ty += e.clientY - lastY;
        lastX = e.clientX; lastY = e.clientY;
        applyTransform();
    });
    window.addEventListener('mouseup', function _up() {
        dragging = false; c.style.cursor = 'grab';
    });
    c.style.cursor = 'grab';

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.remove();
    });
    function _esc(e) { if (e.key === 'Escape') { overlay.remove(); window.removeEventListener('keydown', _esc); } }
    window.addEventListener('keydown', _esc);

    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    Object.assign(closeBtn.style, {
        position: 'absolute', top: '8px', right: '8px', zIndex: '1',
        background: 'rgba(0,0,0,0.7)', border: 'none', color: '#fff',
        width: '32px', height: '32px', borderRadius: '50%', fontSize: '1.2rem',
        cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
    });
    closeBtn.onclick = () => overlay.remove();

    wrap.appendChild(c);
    wrap.appendChild(closeBtn);
    overlay.appendChild(wrap);
    document.body.appendChild(overlay);
    applyTransform();
}

fn.renderAlignmentPreview = renderAlignmentPreview;
