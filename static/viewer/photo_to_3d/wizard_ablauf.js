import { fn } from '../gemeinsam/registrierung.js';
import { renderWizardCanvas } from './wizard_zeichnen.js';
import { wizardState } from './wizard.js';
import { state, API } from './state.js';
import { hideWizardModal, updateWizardUI } from './wizard.js';
import { Ausrichtassistent } from './ausrichtassistent.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
/**
 * Ablauf des Ausricht-Assistenten: starten, Schritte, Ergebnis backen.
 *
 * Aus wizard.js herausgeloest (Umbau 16.08.2026).
 */


export async function startWizard() {
    // Der Ablauf steckt in `Ausrichtassistent` — vorher standen hier 104 Zeilen
    // mit fünf Fällen für die Anfangslage.
    return new Ausrichtassistent().starten();
}

/**
 * Weiter-Knopf: Bei einer posierten Figur gibt es nur einen Schritt, sonst geht
 * es vom Körper zum Gesicht und erst dann zum Backen.
 */
export async function wizardNext() {
    const nurEinSchritt = !!wizardState.data?.use_posed;
    if (wizardState.step === 0 && !nurEinSchritt) {
        wizardState.step = 1;
        updateWizardUI();
        renderWizardCanvas();
        return;
    }
    await saveAlignmentAndBake();
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
        const result = await Serverabruf.json(`${API}/photo-job/${state.currentJobId}/save-alignment/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(alignPayload),
        });
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
            setTimeout(() => fn.captureAndSaveScreenshot(state.currentJobId), Zeiten.FOTO_MS);
        } catch (e) {
            fn.showTextureProgress(true, `${regionLabel}: Fehler — ${e.message}`, 0);
        }
    } finally {
        if (activeBtn) { activeBtn.disabled = false; activeBtn.textContent = origText; }
    }
}
