/**
 * Scene Editor -- Shared utility functions.
 */
import { state } from './state.js';
import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { fn } from '../gemeinsam/registrierung.js';
// Aus gemeinsam/kodierung.js — die Kopien hier sind am 15.08.2026 entfallen (sechsfach vorhanden).
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
export { base64ToFloat32, base64ToUint32, blenderToThreeCoords };

/**
 * Maskiert Fremdtext fuer `innerHTML`.
 *
 * Umbau 16.08.2026: Die Umsetzung steht jetzt in `Htmltext` (djangoBase) —
 * dieselbe Aufgabe stand hier und in der Auftragstabelle. Die alte Fassung
 * baute dafuer ein `<div>` und las `innerHTML`; das maskiert Anfuehrungszeichen
 * NICHT und war damit in Attributen (`title="…"`) unsicher.
 */
export function escapeHtml(str) {
    return Htmltext.maskieren(str);
}

export function generateCharacterId() {
    return `char_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/** Get the currently selected character instance. */
export function _selectedInst() {
    return state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
}

/**
 * Das gewählte MakeHuman-Kleidungsnetz, oder null.
 *
 * Stand bis zum Umbau am 16.08.2026 in `mh_proxy.js`. Von dort holte sich
 * `mhproxy_anpassen.js` die Funktion, und `mh_proxy.js` holte sich umgekehrt
 * `_doMHProxyFit` aus `mhproxy_anpassen.js` — ein Ringimport. Hier neben
 * `_selectedInst()`, wo die andere Auswahl-Hilfe schon liegt, ist der Ring weg.
 */
export function _selectedMHMesh() {
    const auswahl = state._selectedSubMesh;
    if (!auswahl?.key?.startsWith('mh_')) return null;
    const figur = state.characters.get(auswahl.charId);
    if (!figur) return null;
    return { inst: figur, key: auswahl.key, mesh: figur.clothMeshes[auswahl.key] };
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
fn._selectedInst = _selectedInst;
fn._getBodyTop = _getBodyTop;
fn.initDialogCloseHandlers = initDialogCloseHandlers;
