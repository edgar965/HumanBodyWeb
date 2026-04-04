/**
 * Photo To 3D — Alignment Wizard for manual texture alignment.
 */
import { state, API } from './state.js';
import { fn } from './registry.js';
import { drawSmoothContourTransformed } from './alignment_preview.js';

let wizardState = {
    step: 0,
    data: null,
    bodyTransform: null,
    bodyTransformInit: null,
    faceTransform: null,
    faceTransformInit: null,
    photoImg: null,
    isDragging: false,
    dragStartX: 0,
    dragStartY: 0,
    dragStartCx: 0,
    dragStartCy: 0,
    canvasScale: 1,
    editMode: false,
    editPointIdx: -1,
    pointsEdited: false,
};

export async function startWizard() {
    if (!state.currentJobId) return;

    const wizBtn = document.getElementById('btn-start-wizard');
    if (wizBtn) { wizBtn.classList.add('loading'); wizBtn.disabled = true; }

    try {
        const resp = await fetch(`${API}/photo-job/${state.currentJobId}/silhouette/`);
        const sData = await resp.json();
        if (!sData.ok) { alert('Silhouette-Daten konnten nicht geladen werden: ' + (sData.error || '')); return; }

        wizardState.data = sData;

        const photoSrc = document.getElementById('photo-img')?.src;
        if (!photoSrc) { alert('Kein Foto geladen'); return; }

        const img = new Image();
        img.crossOrigin = 'anonymous';
        await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
            img.src = photoSrc;
        });
        wizardState.photoImg = img;

        const mb = sData.mesh_bbox;
        const meshCx = mb.x + mb.w / 2;
        const meshCy = mb.y + mb.h / 2;

        if (sData.use_posed) {
            wizardState.bodyTransform = { center_x: 0, center_y: 0, scale: 1.0 };
        } else if (sData.yolo_bbox) {
            const [x1, y1, x2, y2] = sData.yolo_bbox;
            const yoloCx = (x1 + x2) / 2;
            const yoloCy = (y1 + y2) / 2;
            const yoloW = x2 - x1;
            const yoloH = y2 - y1;
            const scaleW = mb.w > 0 ? yoloW / mb.w : 1;
            const scaleH = mb.h > 0 ? yoloH / mb.h : 1;
            const fitScale = Math.min(scaleW, scaleH) * 0.95;
            wizardState.bodyTransform = { center_x: yoloCx, center_y: yoloCy, scale: fitScale };
        } else {
            wizardState.bodyTransform = { center_x: meshCx, center_y: meshCy, scale: 1.0 };
        }
        wizardState.bodyTransformInit = { ...wizardState.bodyTransform };

        if (sData.use_posed) {
            wizardState.faceTransform = { center_x: 0, center_y: 0, scale: 1.0 };
        } else {
            const fb = sData.face_bbox_detected || sData.face_bbox_mesh;
            const fmb = sData.face_bbox_mesh;
            if (fb && fmb) {
                const fbCx = fb.x + fb.w / 2;
                const fbCy = fb.y + fb.h / 2;
                const fScaleW = fmb.w > 0 ? fb.w / fmb.w : 1;
                const fScaleH = fmb.h > 0 ? fb.h / fmb.h : 1;
                const fFitScale = Math.min(fScaleW, fScaleH);
                const fmOffX = (fmb.x + fmb.w / 2) - meshCx;
                const fmOffY = (fmb.y + fmb.h / 2) - meshCy;
                wizardState.faceTransform = {
                    center_x: fbCx - fmOffX * fFitScale,
                    center_y: fbCy - fmOffY * fFitScale,
                    scale: fFitScale,
                };
            } else {
                wizardState.faceTransform = { ...wizardState.bodyTransform };
            }
        }
        wizardState.faceTransformInit = { ...wizardState.faceTransform };

        const saved = sData.saved_alignment;
        if (saved) {
            if (sData.use_posed && saved.proj_2d_offset) {
                const off = saved.proj_2d_offset;
                wizardState.bodyTransform = { center_x: off.dx || 0, center_y: off.dy || 0, scale: off.scale || 1 };
            } else if (saved.body_transform) {
                wizardState.bodyTransform = { ...saved.body_transform };
            }
            if (saved.face_transform && !(saved.face_transform.center_x === 0 && saved.face_transform.center_y === 0 && saved.face_transform.scale === 1)) {
                wizardState.faceTransform = { ...saved.face_transform };
            }
            if (saved.body_contour_edited) {
                wizardState.data.body_contour = saved.body_contour_edited;
                wizardState.pointsEdited = true;
            }
            if (saved.face_contour_edited) {
                wizardState.data.face_contour = saved.face_contour_edited;
                wizardState.pointsEdited = true;
            }
            console.log('[Wizard] Loaded saved alignment');
        }

        wizardState.step = 0;
        showWizardModal();
        renderWizardCanvas();

    } catch (e) {
        console.error('Wizard start failed:', e);
        alert('Wizard konnte nicht gestartet werden: ' + e.message);
    } finally {
        if (wizBtn) { wizBtn.classList.remove('loading'); wizBtn.disabled = false; }
        fn.enableTextureButtons();
    }
}

function showWizardModal() {
    const modal = document.getElementById('alignment-wizard');
    if (!modal) return;
    modal.style.display = 'flex';
    updateWizardUI();
    initWizardEvents();
}

function hideWizardModal() {
    const modal = document.getElementById('alignment-wizard');
    if (modal) modal.style.display = 'none';
    wizardState.isDragging = false;
    wizardState.editMode = false;
    wizardState.editPointIdx = -1;
    const btn = document.getElementById('wizard-edit-points');
    if (btn) btn.classList.remove('active');
}

function updateWizardUI() {
    const title = document.getElementById('wizard-title');
    const info = document.getElementById('wizard-info');
    const backBtn = document.getElementById('wizard-back');
    const nextBtn = document.getElementById('wizard-next');

    if (wizardState.step === 0) {
        if (wizardState.data?.use_posed) {
            if (title) title.textContent = 'Posed Mesh ausrichten';
            if (info) info.textContent = 'Ziehen = Verschieben | Mausrad = Skalieren | Rote Kontur auf die Person legen';
            if (backBtn) backBtn.style.display = 'none';
            if (nextBtn) nextBtn.textContent = 'Textur erstellen';
        } else {
            if (title) title.textContent = 'Schritt 1: Koerper ausrichten';
            if (info) info.textContent = 'Ziehen = Verschieben | Mausrad = Skalieren | Rote Silhouette auf die Person legen';
            if (backBtn) backBtn.style.display = 'none';
            if (nextBtn) nextBtn.textContent = 'Weiter';
        }
    } else {
        if (title) title.textContent = 'Schritt 2: Gesicht ausrichten';
        if (info) info.textContent = 'Ziehen = Verschieben | Mausrad = Skalieren | Lila Kontur auf das Gesicht legen';
        if (backBtn) backBtn.style.display = '';
        if (nextBtn) nextBtn.textContent = 'Textur erstellen';
    }
}

function initWizardEvents() {
    const canvas = document.getElementById('wizard-canvas');
    if (!canvas || canvas._wizardBound) return;
    canvas._wizardBound = true;

    canvas.addEventListener('mousedown', wizardMouseDown);
    canvas.addEventListener('mousemove', wizardMouseMove);
    canvas.addEventListener('mouseup', wizardMouseUp);
    canvas.addEventListener('mouseleave', wizardMouseUp);
    canvas.addEventListener('wheel', wizardWheel, { passive: false });

    canvas.addEventListener('touchstart', wizardTouchStart, { passive: false });
    canvas.addEventListener('touchmove', wizardTouchMove, { passive: false });
    canvas.addEventListener('touchend', wizardMouseUp);

    const wrapEl = document.querySelector('.wizard-canvas-wrap');
    if (wrapEl && !wrapEl._wizardResizeObserver) {
        const ro = new ResizeObserver(() => renderWizardCanvas());
        ro.observe(wrapEl);
        wrapEl._wizardResizeObserver = ro;
    }

    document.getElementById('wizard-close')?.addEventListener('click', hideWizardModal);
    document.getElementById('wizard-reset')?.addEventListener('click', wizardReset);
    document.getElementById('wizard-back')?.addEventListener('click', () => {
        wizardState.step = 0;
        updateWizardUI();
        renderWizardCanvas();
    });
    document.getElementById('wizard-next')?.addEventListener('click', wizardNext);
    document.getElementById('wizard-bake-body')?.addEventListener('click', () => {
        if (wizardState.step !== 0) {
            wizardState.step = 0;
            updateWizardUI();
            renderWizardCanvas();
        }
        saveAlignmentAndBake('body');
    });
    document.getElementById('wizard-bake-face')?.addEventListener('click', () => {
        if (wizardState.step !== 1) {
            wizardState.step = 1;
            updateWizardUI();
            renderWizardCanvas();
        }
        saveAlignmentAndBake('face');
    });
    document.getElementById('wizard-edit-points')?.addEventListener('click', () => {
        wizardState.editMode = !wizardState.editMode;
        wizardState.editPointIdx = -1;
        const btn = document.getElementById('wizard-edit-points');
        if (wizardState.editMode) {
            btn.classList.add('active');
            canvas.style.cursor = 'crosshair';
        } else {
            btn.classList.remove('active');
            canvas.style.cursor = 'grab';
        }
        renderWizardCanvas();
    });
}

function _wizardEditParams() {
    const sd = wizardState.data;
    if (!sd) return null;
    const mb = sd.mesh_bbox;
    const meshCx = mb.x + mb.w / 2;
    const meshCy = mb.y + mb.h / 2;
    const usePosed = !!sd.use_posed;
    const isBody = wizardState.step === 0;
    const contour = isBody ? sd.body_contour : sd.face_contour;
    const bt = isBody ? wizardState.bodyTransform : wizardState.faceTransform;
    if (!contour || contour.length < 3 || !bt) return null;
    let ccx = 0, ccy = 0;
    if (usePosed) {
        for (const [px, py] of contour) { ccx += px; ccy += py; }
        ccx /= contour.length; ccy /= contour.length;
    }
    return { contour, bt, meshCx, meshCy, usePosed, ccx, ccy };
}

function transformPtGlobal(px, py, bt, meshCx, meshCy, usePosed, ccx, ccy, canvasScale) {
    if (usePosed) {
        const nx = (px - ccx) * bt.scale + ccx + bt.center_x;
        const ny = (py - ccy) * bt.scale + ccy + bt.center_y;
        return [nx * canvasScale, ny * canvasScale];
    } else {
        const dx = px - meshCx;
        const dy = py - meshCy;
        const nx = dx * bt.scale + bt.center_x;
        const ny = dy * bt.scale + bt.center_y;
        return [nx * canvasScale, ny * canvasScale];
    }
}

function inverseTransformPt(canvasX, canvasY, bt, meshCx, meshCy, usePosed, ccx, ccy, canvasScale) {
    const nx = canvasX / canvasScale;
    const ny = canvasY / canvasScale;
    if (usePosed) {
        return [(nx - ccx - bt.center_x) / bt.scale + ccx,
                (ny - ccy - bt.center_y) / bt.scale + ccy];
    } else {
        return [(nx - bt.center_x) / bt.scale + meshCx,
                (ny - bt.center_y) / bt.scale + meshCy];
    }
}

function wizardMouseDown(e) {
    const canvas = e.target;
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;

    if (wizardState.editMode) {
        const ep = _wizardEditParams();
        if (ep) {
            const cs = wizardState.canvasScale;
            let bestIdx = -1, bestDist = 10;
            for (let i = 0; i < ep.contour.length; i++) {
                const [tx, ty] = transformPtGlobal(ep.contour[i][0], ep.contour[i][1],
                    ep.bt, ep.meshCx, ep.meshCy, ep.usePosed, ep.ccx, ep.ccy, cs);
                const dist = Math.hypot(tx - cx, ty - cy);
                if (dist < bestDist) { bestDist = dist; bestIdx = i; }
            }
            wizardState.editPointIdx = bestIdx;
            if (bestIdx >= 0) return;
        }
    }

    wizardState.isDragging = true;
    const t = wizardState.step === 0 ? wizardState.bodyTransform : wizardState.faceTransform;
    wizardState.dragStartX = e.clientX;
    wizardState.dragStartY = e.clientY;
    wizardState.dragStartCx = t.center_x;
    wizardState.dragStartCy = t.center_y;
}

function wizardMouseMove(e) {
    if (wizardState.editMode && wizardState.editPointIdx >= 0) {
        const ep = _wizardEditParams();
        if (ep) {
            const canvas = e.target;
            const rect = canvas.getBoundingClientRect();
            const cx = e.clientX - rect.left;
            const cy = e.clientY - rect.top;
            const cs = wizardState.canvasScale;
            const [px, py] = inverseTransformPt(cx, cy,
                ep.bt, ep.meshCx, ep.meshCy, ep.usePosed, ep.ccx, ep.ccy, cs);
            ep.contour[wizardState.editPointIdx] = [px, py];
            wizardState.pointsEdited = true;
            renderWizardCanvas();
        }
        return;
    }

    if (!wizardState.isDragging) return;
    const cs = wizardState.canvasScale;
    const dx = (e.clientX - wizardState.dragStartX) / cs;
    const dy = (e.clientY - wizardState.dragStartY) / cs;
    const t = wizardState.step === 0 ? wizardState.bodyTransform : wizardState.faceTransform;
    t.center_x = wizardState.dragStartCx + dx;
    t.center_y = wizardState.dragStartCy + dy;
    renderWizardCanvas();
}

function wizardMouseUp() {
    if (wizardState.editMode && wizardState.editPointIdx >= 0) {
        wizardState.editPointIdx = -1;
        return;
    }
    wizardState.isDragging = false;
}

function wizardTouchStart(e) {
    e.preventDefault();
    if (e.touches.length === 1) {
        const touch = e.touches[0];
        wizardState.isDragging = true;
        const t = wizardState.step === 0 ? wizardState.bodyTransform : wizardState.faceTransform;
        wizardState.dragStartX = touch.clientX;
        wizardState.dragStartY = touch.clientY;
        wizardState.dragStartCx = t.center_x;
        wizardState.dragStartCy = t.center_y;
    }
}

function wizardTouchMove(e) {
    e.preventDefault();
    if (!wizardState.isDragging || e.touches.length !== 1) return;
    const touch = e.touches[0];
    const cs = wizardState.canvasScale;
    const dx = (touch.clientX - wizardState.dragStartX) / cs;
    const dy = (touch.clientY - wizardState.dragStartY) / cs;
    const t = wizardState.step === 0 ? wizardState.bodyTransform : wizardState.faceTransform;
    t.center_x = wizardState.dragStartCx + dx;
    t.center_y = wizardState.dragStartCy + dy;
    renderWizardCanvas();
}

function wizardWheel(e) {
    e.preventDefault();
    const t = wizardState.step === 0 ? wizardState.bodyTransform : wizardState.faceTransform;
    const factor = e.deltaY > 0 ? 0.95 : 1.05;
    t.scale = Math.max(0.3, Math.min(3.0, t.scale * factor));
    renderWizardCanvas();
}

function wizardReset() {
    if (wizardState.step === 0) {
        wizardState.bodyTransform = { ...wizardState.bodyTransformInit };
    } else {
        wizardState.faceTransform = { ...wizardState.faceTransformInit };
    }
    renderWizardCanvas();
}

async function wizardNext() {
    if (wizardState.step === 0) {
        if (wizardState.data?.use_posed) {
            await saveAlignmentAndBake();
        } else {
            wizardState.step = 1;
            updateWizardUI();
            renderWizardCanvas();
        }
    } else {
        await saveAlignmentAndBake();
    }
}

async function saveAlignmentAndBake(region = 'all') {
    const nextBtn = document.getElementById('wizard-next');
    const isRegion = region === 'body' || region === 'face';
    const activeBtn = isRegion
        ? document.getElementById(region === 'body' ? 'wizard-bake-body' : 'wizard-bake-face')
        : nextBtn;
    const origText = activeBtn?.textContent;
    if (activeBtn) { activeBtn.disabled = true; activeBtn.textContent = 'Speichern...'; }

    try {
        const alignPayload = wizardState.data?.use_posed ? {
            proj_2d_offset: {
                dx: wizardState.bodyTransform.center_x,
                dy: wizardState.bodyTransform.center_y,
                scale: wizardState.bodyTransform.scale,
            },
            face_transform: wizardState.faceTransform,
        } : {
            body_transform: wizardState.bodyTransform,
            face_transform: wizardState.faceTransform,
        };
        if (wizardState.pointsEdited) {
            if (wizardState.data?.body_contour) {
                alignPayload.body_contour_edited = wizardState.data.body_contour;
            }
            if (wizardState.data?.face_contour) {
                alignPayload.face_contour_edited = wizardState.data.face_contour;
            }
        }
        const resp = await fetch(`${API}/photo-job/${state.currentJobId}/save-alignment/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(alignPayload),
        });
        const result = await resp.json();
        if (!result.ok) {
            alert('Alignment konnte nicht gespeichert werden: ' + (result.error || ''));
            return;
        }

        state._previewDataCache = null;
        const regionLabel = region === 'body' ? 'Koerper' : region === 'face' ? 'Gesicht' : 'Wizard';

        if (!isRegion) {
            hideWizardModal();
        }

        if (activeBtn) activeBtn.textContent = 'Textur wird erstellt...';
        fn.showTextureProgress(true, `${regionLabel}: Textur wird erstellt...`, 10);
        const t0 = performance.now();
        try {
            await fn.loadSmplxTexture(state.currentJobId, 'orthographic', region);
            const dur = ((performance.now() - t0) / 1000).toFixed(1);
            fn.showTextureProgress(true, `${regionLabel}: Fertig (${dur}s)`, 100);
            const info = document.getElementById('texture-info');
            if (info) {
                info.style.display = 'block';
                info.textContent = `${regionLabel}-Textur auf SMPL-X Mesh angewendet`;
            }
            fn.renderAlignmentPreview();
            setTimeout(() => fn.captureAndSaveScreenshot(state.currentJobId), 500);
        } catch (e) {
            fn.showTextureProgress(true, `${regionLabel}: Fehler — ${e.message}`, 0);
        }
    } finally {
        if (activeBtn) { activeBtn.disabled = false; activeBtn.textContent = origText; }
    }
}

function renderWizardCanvas() {
    const canvas = document.getElementById('wizard-canvas');
    if (!canvas || !wizardState.data || !wizardState.photoImg) return;

    const ctx = canvas.getContext('2d');
    const img = wizardState.photoImg;
    const sd = wizardState.data;

    const wrap = canvas.parentElement;
    const maxW = Math.max(wrap.clientWidth - 24, 300);
    const maxH = Math.max(wrap.clientHeight - 24, 200);
    const scale = Math.min(maxW / img.naturalWidth, maxH / img.naturalHeight);
    const cw = Math.round(img.naturalWidth * scale);
    const ch = Math.round(img.naturalHeight * scale);
    canvas.width = cw;
    canvas.height = ch;
    wizardState.canvasScale = scale;

    ctx.drawImage(img, 0, 0, cw, ch);

    const mb = sd.mesh_bbox;
    const meshCx = mb.x + mb.w / 2;
    const meshCy = mb.y + mb.h / 2;

    function contourCenter(contour) {
        let sx = 0, sy = 0;
        for (const [px, py] of contour) { sx += px; sy += py; }
        return [sx / contour.length, sy / contour.length];
    }

    function transformPt(px, py, bt, _meshCx, _meshCy, usePosed, ccx, ccy) {
        if (usePosed) {
            const nx = (px - ccx) * bt.scale + ccx + bt.center_x;
            const ny = (py - ccy) * bt.scale + ccy + bt.center_y;
            return [nx * scale, ny * scale];
        } else {
            const dx = px - _meshCx;
            const dy = py - _meshCy;
            const nx = dx * bt.scale + bt.center_x;
            const ny = dy * bt.scale + bt.center_y;
            return [nx * scale, ny * scale];
        }
    }

    const usePosed = !!sd.use_posed;
    const bodyCC = (usePosed && sd.body_contour && sd.body_contour.length > 2)
        ? contourCenter(sd.body_contour) : [0, 0];

    if (wizardState.step === 0) {
        // === BODY STEP ===
        if (sd.yolo_bbox) {
            const [x1, y1, x2, y2] = sd.yolo_bbox;
            ctx.save();
            ctx.setLineDash([6, 4]);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(x1 * scale, y1 * scale, (x2 - x1) * scale, (y2 - y1) * scale);
            ctx.restore();
        }

        if (sd.body_contour && sd.body_contour.length > 2) {
            const bt = wizardState.bodyTransform;
            ctx.save();
            ctx.fillStyle = 'rgba(233, 69, 96, 0.25)';
            ctx.strokeStyle = 'rgba(233, 69, 96, 0.8)';
            ctx.lineWidth = 2;
            drawSmoothContourTransformed(ctx, sd.body_contour,
                (px, py) => transformPt(px, py, bt, meshCx, meshCy, usePosed, bodyCC[0], bodyCC[1]));
            ctx.fill();
            ctx.stroke();
            ctx.restore();
        }
    } else {
        // === FACE STEP ===
        if (sd.body_contour && sd.body_contour.length > 2) {
            const bt = wizardState.bodyTransform;
            ctx.save();
            ctx.fillStyle = 'rgba(150, 150, 150, 0.15)';
            ctx.strokeStyle = 'rgba(150, 150, 150, 0.3)';
            ctx.lineWidth = 1;
            drawSmoothContourTransformed(ctx, sd.body_contour,
                (px, py) => transformPt(px, py, bt, meshCx, meshCy, usePosed, bodyCC[0], bodyCC[1]));
            ctx.fill();
            ctx.stroke();
            ctx.restore();
        }

        if (sd.face_bbox_detected) {
            const fb = sd.face_bbox_detected;
            ctx.save();
            ctx.setLineDash([5, 3]);
            ctx.strokeStyle = 'rgba(46, 204, 113, 0.7)';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(fb.x * scale, fb.y * scale, fb.w * scale, fb.h * scale);
            ctx.restore();
        }

        if (sd.face_contour && sd.face_contour.length > 2) {
            const ft = wizardState.faceTransform;
            const faceCC = usePosed ? contourCenter(sd.face_contour) : [0, 0];
            ctx.save();
            ctx.fillStyle = 'rgba(155, 89, 182, 0.25)';
            ctx.strokeStyle = 'rgba(155, 89, 182, 0.8)';
            ctx.lineWidth = 2;
            drawSmoothContourTransformed(ctx, sd.face_contour,
                (px, py) => transformPt(px, py, ft, meshCx, meshCy, usePosed, faceCC[0], faceCC[1]));
            ctx.fill();
            ctx.stroke();
            ctx.restore();
        }
    }

    // Point handles in edit mode
    if (wizardState.editMode) {
        const isBody = wizardState.step === 0;
        const contour = isBody ? sd.body_contour : sd.face_contour;
        const bt = isBody ? wizardState.bodyTransform : wizardState.faceTransform;
        if (contour && contour.length > 2 && bt) {
            const cc = isBody ? bodyCC : (usePosed ? contourCenter(sd.face_contour) : [0, 0]);
            ctx.save();
            for (let i = 0; i < contour.length; i++) {
                const [tx, ty] = transformPt(contour[i][0], contour[i][1],
                    bt, meshCx, meshCy, usePosed, cc[0], cc[1]);
                ctx.beginPath();
                ctx.arc(tx, ty, 5, 0, Math.PI * 2);
                if (i === wizardState.editPointIdx) {
                    ctx.fillStyle = '#fff';
                    ctx.strokeStyle = '#e94560';
                    ctx.lineWidth = 2.5;
                } else {
                    ctx.fillStyle = 'rgba(255,255,255,0.7)';
                    ctx.strokeStyle = isBody ? 'rgba(233,69,96,0.9)' : 'rgba(155,89,182,0.9)';
                    ctx.lineWidth = 1.5;
                }
                ctx.fill();
                ctx.stroke();
            }
            ctx.restore();
        }
    }
}

fn.startWizard = startWizard;
