/**
 * Photo To 3D — Alignment Wizard for manual texture alignment.
 */
import './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import './alignment_preview.js';
import { renderWizardCanvas } from './wizard_zeichnen.js';
import { wizardMouseDown, wizardMouseMove, wizardMouseUp, wizardReset, wizardTouchMove, wizardTouchStart,
    wizardWheel } from './wizard_maus.js';
import { saveAlignmentAndBake, startWizard, wizardNext } from './wizard_ablauf.js';

export let wizardState = {
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


export function showWizardModal() {
    const modal = document.getElementById('alignment-wizard');
    if (!modal) return;
    modal.style.display = 'flex';
    updateWizardUI();
    initWizardEvents();
}

export function hideWizardModal() {
    const modal = document.getElementById('alignment-wizard');
    if (modal) modal.style.display = 'none';
    wizardState.isDragging = false;
    wizardState.editMode = false;
    wizardState.editPointIdx = -1;
    const btn = document.getElementById('wizard-edit-points');
    if (btn) btn.classList.remove('active');
}

export function updateWizardUI() {
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

export function _wizardEditParams() {
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













fn.startWizard = startWizard;
