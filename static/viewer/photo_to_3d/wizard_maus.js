import { inverseTransformPt, renderWizardCanvas, transformPtGlobal } from './wizard_zeichnen.js';
import { _wizardEditParams } from './wizard.js';
import { wizardState } from './wizard.js';
/**
 * Ziehen, Drehen und Zoomen im Ausricht-Assistenten.
 *
 * Aus wizard.js herausgeloest (Umbau 16.08.2026).
 */


export function wizardMouseDown(e) {
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

export function wizardMouseMove(e) {
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

export function wizardMouseUp() {
    if (wizardState.editMode && wizardState.editPointIdx >= 0) {
        wizardState.editPointIdx = -1;
        return;
    }
    wizardState.isDragging = false;
}

export function wizardTouchStart(e) {
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

export function wizardTouchMove(e) {
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

export function wizardWheel(e) {
    e.preventDefault();
    const t = wizardState.step === 0 ? wizardState.bodyTransform : wizardState.faceTransform;
    const factor = e.deltaY > 0 ? 0.95 : 1.05;
    t.scale = Math.max(0.3, Math.min(3.0, t.scale * factor));
    renderWizardCanvas();
}

export function wizardReset() {
    if (wizardState.step === 0) {
        wizardState.bodyTransform = { ...wizardState.bodyTransformInit };
    } else {
        wizardState.faceTransform = { ...wizardState.faceTransformInit };
    }
    renderWizardCanvas();
}
