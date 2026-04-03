/**
 * Scene Editor -- Rigging tab UI bindings.
 */
import { state } from './state.js';
import { fn } from './registry.js';
import { markDirty } from './undo.js';

export const _defaultRigParams = {
    ikNoStretch: true, ikLimit: true, ikMin: -10, ikMax: 160,
    fingerIk: false, spinePivot: false,
    slideElbow: 0.08, slideKnee: 0.05, rigVisible: false,
};

export function initRiggingTab(toggleRigVisibility) {
    const ids = {
        'rig-ik-no-stretch': { key: 'ikNoStretch', type: 'check' },
        'rig-ik-limit':      { key: 'ikLimit', type: 'check' },
        'rig-ik-min':        { key: 'ikMin', type: 'number' },
        'rig-ik-max':        { key: 'ikMax', type: 'number' },
        'rig-finger-ik':     { key: 'fingerIk', type: 'check' },
        'rig-spine-pivot':   { key: 'spinePivot', type: 'check' },
        'rig-slide-elbow':   { key: 'slideElbow', type: 'range', valId: 'rig-slide-elbow-val' },
        'rig-slide-knee':    { key: 'slideKnee', type: 'range', valId: 'rig-slide-knee-val' },
        'rig-visible':       { key: 'rigVisible', type: 'check' },
    };
    function getRigParams() {
        const inst = state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
        if (inst && inst._rigParams) return inst._rigParams;
        return { ..._defaultRigParams };
    }
    function setRigParam(key, val) {
        const inst = state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
        if (inst) { if (!inst._rigParams) inst._rigParams = { ..._defaultRigParams }; inst._rigParams[key] = val; markDirty('Rigging'); }
        if (key === 'rigVisible') { state.rigVisible = val; if (toggleRigVisibility) toggleRigVisibility(); }
    }
    for (const [id, cfg] of Object.entries(ids)) {
        const el = document.getElementById(id); if (!el) continue;
        const params = getRigParams();
        if (cfg.type === 'check') { el.checked = params[cfg.key]; el.addEventListener('change', () => setRigParam(cfg.key, el.checked)); }
        else if (cfg.type === 'number') { el.value = params[cfg.key]; el.addEventListener('change', () => setRigParam(cfg.key, parseFloat(el.value))); }
        else if (cfg.type === 'range') { el.value = params[cfg.key]; const valEl = document.getElementById(cfg.valId); if (valEl) valEl.textContent = parseFloat(el.value).toFixed(2); el.addEventListener('input', () => { if (valEl) valEl.textContent = parseFloat(el.value).toFixed(2); setRigParam(cfg.key, parseFloat(el.value)); }); }
    }
}

fn.initRiggingTab = initRiggingTab;
fn._defaultRigParams = _defaultRigParams;
