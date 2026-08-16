/**
 * scene_rigging.js — Rigging tab UI bindings for the Scene Editor.
 */
import { state } from './scene_state.js?v=1';
import { markDirty } from './scene_undo.js?v=1';

// =========================================================================
// Default rig parameters
// =========================================================================
export const _defaultRigParams = {
    ikNoStretch: true, ikLimit: true, ikMin: -10, ikMax: 160,
    fingerIk: false, spinePivot: false,
    slideElbow: 0.08, slideKnee: 0.05, rigVisible: false,
};

// =========================================================================
// initRiggingTab — bind DOM elements to rig params
// =========================================================================
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

    // Get rig params from selected character or defaults
    function getRigParams() {
        const inst = state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
        if (inst && inst._rigParams) return inst._rigParams;
        return { ..._defaultRigParams };
    }

    function setRigParam(key, val) {
        const inst = state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
        if (inst) {
            if (!inst._rigParams) inst._rigParams = { ..._defaultRigParams };
            inst._rigParams[key] = val;
            markDirty('Rigging');
        }
        // Special handling for rig visibility
        if (key === 'rigVisible') {
            const toggle = document.getElementById('rig-toggle');
            if (toggle && state.rigVisible !== val) {
                state.rigVisible = val;
                toggleRigVisibility();
            }
        }
    }

    for (const [id, cfg] of Object.entries(ids)) {
        const el = document.getElementById(id);
        if (!el) continue;
        const params = getRigParams();
        // Set initial value
        if (cfg.type === 'check') el.checked = params[cfg.key];
        else el.value = params[cfg.key];
        if (cfg.valId) {
            const valEl = document.getElementById(cfg.valId);
            if (valEl) valEl.textContent = params[cfg.key];
        }
        // Bind change
        el.addEventListener(cfg.type === 'range' ? 'input' : 'change', () => {
            const v = cfg.type === 'check' ? el.checked : parseFloat(el.value);
            setRigParam(cfg.key, v);
            if (cfg.valId) {
                const valEl = document.getElementById(cfg.valId);
                if (valEl) valEl.textContent = v;
            }
        });
    }
}
