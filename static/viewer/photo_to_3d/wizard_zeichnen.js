import { drawSmoothContourTransformed } from './alignment_preview.js';
import { wizardState } from './wizard.js';
/**
 * Die Leinwand des Ausricht-Assistenten zeichnen.
 *
 * Aus wizard.js herausgeloest (Umbau 16.08.2026).
 */


export function transformPtGlobal(px, py, bt, meshCx, meshCy, usePosed, ccx, ccy, canvasScale) {
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

export function inverseTransformPt(canvasX, canvasY, bt, meshCx, meshCy, usePosed, ccx, ccy, canvasScale) {
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

export function renderWizardCanvas() {
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
