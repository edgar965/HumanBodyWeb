import { fn } from '../gemeinsam/registrierung.js';
import { renderWizardCanvas } from './wizard_zeichnen.js';
import { wizardState } from './wizard.js';
import { state, API } from './state.js';
import { showWizardModal, hideWizardModal, updateWizardUI } from './wizard.js';
/**
 * Ablauf des Ausricht-Assistenten: starten, Schritte, Ergebnis backen.
 *
 * Aus wizard.js herausgeloest (Umbau 16.08.2026).
 */


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

export async function wizardNext() {
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

export async function saveAlignmentAndBake(region = 'all') {
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
