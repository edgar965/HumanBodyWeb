import { renderWizardCanvas } from './wizard_zeichnen.js';
import { inverseTransformPt, transformPtGlobal } from './wizard_umrechnung.js';
import { _wizardEditParams } from './wizard.js';
import { wizardState } from './wizard.js';
/**
 * Ziehen, Drehen und Zoomen im Ausricht-Assistenten.
 *
 * Aus wizard.js herausgeloest (Umbau 16.08.2026).
 */

/**
 * Verschiebung des aktuellen Schritts: Schritt 0 richtet den Körper aus, alles
 * danach das Gesicht. Diese Abfrage stand fünfmal in dieser Datei.
 */
function verschiebung() {
    return wizardState.step === 0 ? wizardState.bodyTransform
                                  : wizardState.faceTransform;
}

/** Startwerte für das Ziehen merken — für Maus und Finger gleich. */
function ziehenBeginnen(x, y) {
    const t = verschiebung();
    wizardState.isDragging = true;
    wizardState.dragStartX = x;
    wizardState.dragStartY = y;
    wizardState.dragStartCx = t.center_x;
    wizardState.dragStartCy = t.center_y;
}

/** Verschiebung aus der Zeigerbewegung — für Maus und Finger gleich. */
function ziehen(x, y) {
    const maszstab = wizardState.canvasScale;
    const t = verschiebung();
    t.center_x = wizardState.dragStartCx + (x - wizardState.dragStartX) / maszstab;
    t.center_y = wizardState.dragStartCy + (y - wizardState.dragStartY) / maszstab;
    renderWizardCanvas();
}

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

    ziehenBeginnen(e.clientX, e.clientY);
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
    ziehen(e.clientX, e.clientY);
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
        ziehenBeginnen(e.touches[0].clientX, e.touches[0].clientY);
    }
}

export function wizardTouchMove(e) {
    e.preventDefault();
    if (!wizardState.isDragging || e.touches.length !== 1) return;
    ziehen(e.touches[0].clientX, e.touches[0].clientY);
}

export function wizardWheel(e) {
    e.preventDefault();
    const t = verschiebung();
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
