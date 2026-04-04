/**
 * Scene Editor -- Shared utility functions.
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';

export function base64ToFloat32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Float32Array(bytes.buffer);
}

export function base64ToUint32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Uint32Array(bytes.buffer);
}

export function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

export function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

export function generateCharacterId() {
    return `char_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function getCSRFToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

/** Get the currently selected character instance. */
export function _selectedInst() {
    return state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
}

/** Build morph+meta query params for a character. */
export function _charQueryParams(inst) {
    const params = new URLSearchParams();
    params.set('body_type', inst.bodyType);
    for (const [k, v] of Object.entries(inst.morphs || {})) {
        if (v !== 0) params.set(`morph_${k}`, v);
    }
    for (const [k, v] of Object.entries(inst.meta || {})) {
        if (v !== 0) params.set(`meta_${k}`, v);
    }
    return params;
}

/** Bind a slider to its display element. */
export function _bindSlider(id, valId, fmt) {
    const slider = document.getElementById(id);
    const val = document.getElementById(valId);
    if (slider && val) {
        slider.addEventListener('input', () => {
            val.textContent = fmt(parseInt(slider.value));
        });
    }
}

export function _sliderVal(id) {
    const el = document.getElementById(id);
    return el ? parseInt(el.value) : 0;
}

/** Returns the max Y coordinate from a character's body mesh positions. */
export function _getBodyTop(inst) {
    if (!inst.bodyMesh || !inst.bodyMesh.geometry.attributes.position) return 1.0;
    const pos = inst.bodyMesh.geometry.attributes.position.array;
    let maxY = -Infinity;
    for (let i = 1; i < pos.length; i += 3) {
        if (pos[i] > maxY) maxY = pos[i];
    }
    return maxY > 0 ? maxY : 1.0;
}

// Dialog helpers
export function openDialog(overlay) {
    overlay.classList.add('visible');
}

export function closeDialog(overlay) {
    overlay.classList.remove('visible');
}

export function closeAllDialogs() {
    document.querySelectorAll('.scene-modal-overlay.visible').forEach(d => closeDialog(d));
}

// Bind close buttons and overlay click for all dialogs
export function initDialogCloseHandlers() {
    document.querySelectorAll('.scene-modal-overlay').forEach(overlay => {
        overlay.querySelectorAll('[data-close]').forEach(btn => {
            btn.addEventListener('click', () => closeDialog(overlay));
        });
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeDialog(overlay);
        });
    });
}

// Register shared utils
fn.escapeHtml = escapeHtml;
fn.generateCharacterId = generateCharacterId;
fn.getCSRFToken = getCSRFToken;
fn._selectedInst = _selectedInst;
fn._charQueryParams = _charQueryParams;
fn._bindSlider = _bindSlider;
fn._sliderVal = _sliderVal;
fn._getBodyTop = _getBodyTop;
fn.openDialog = openDialog;
fn.closeDialog = closeDialog;
fn.closeAllDialogs = closeAllDialogs;
fn.initDialogCloseHandlers = initDialogCloseHandlers;
fn.base64ToFloat32 = base64ToFloat32;
fn.base64ToUint32 = base64ToUint32;
fn.blenderToThreeCoords = blenderToThreeCoords;
