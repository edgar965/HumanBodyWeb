/**
 * charmorph_hair.js — CharMorph hairstyle browser + hair colors in Assets tab.
 *
 * CharMorph hairstyles are NPZ particle data (Blender-only).
 * For web we load our GLB hairstyles but add CharMorph hair colors.
 * Also provides the CharMorph hair color preset dropdown.
 */
import { state } from './state.js';
import { fn } from './registry.js';

let _cmHairColors = {};  // name -> {viewport_color: [r,g,b], melanin, ...}

export async function loadCharmorphHairUI() {
    const sel = document.getElementById('cm-hairstyle');
    if (!sel) return;

    // Load CharMorph hairstyles (NPZ - info only, can't render in web)
    try {
        const resp = await fetch('/api/character/charmorph-hairstyles/');
        const data = await resp.json();
        sel.innerHTML = '<option value="">-- Kein Haar --</option>';
        for (const h of (data.hairstyles || [])) {
            const opt = document.createElement('option');
            opt.value = h.name;
            opt.textContent = h.label || h.name;
            sel.appendChild(opt);
        }
        // Also load hair colors
        _cmHairColors = data.colors || {};
        const colorSel = document.getElementById('cm-hair-color-preset');
        if (colorSel) {
            colorSel.innerHTML = '<option value="">-- Manuelle Farbe --</option>';
            for (const name of Object.keys(_cmHairColors)) {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name.replace('CY ', '');
                const vc = _cmHairColors[name].viewport_color;
                if (vc) opt.style.color = `rgb(${Math.round(vc[0]*255)},${Math.round(vc[1]*255)},${Math.round(vc[2]*255)})`;
                colorSel.appendChild(opt);
            }
        }
    } catch (e) {
        console.error('[CharMorph Hair] Load failed:', e);
    }

    // Color preset select -> apply to color picker and to active hair
    const colorPreset = document.getElementById('cm-hair-color-preset');
    const colorInput = document.getElementById('cm-hair-color');
    if (colorPreset) {
        colorPreset.addEventListener('change', () => {
            const c = _cmHairColors[colorPreset.value];
            if (c && c.viewport_color && colorInput) {
                const [r, g, b] = c.viewport_color;
                const hex = '#' + [r, g, b].map(v => Math.round(v * 255).toString(16).padStart(2, '0')).join('');
                colorInput.value = hex;
                _applyHairColor(hex);
            }
        });
    }

    // Manual color picker
    if (colorInput) {
        colorInput.addEventListener('input', () => _applyHairColor(colorInput.value));
    }

    // Shrinkwrap checkbox
    const shrinkwrap = document.getElementById('cm-hair-shrinkwrap');
    if (shrinkwrap) {
        shrinkwrap.addEventListener('change', () => {
            if (fn.serverLog) fn.serverLog('hair_shrinkwrap', `${shrinkwrap.checked}`);
        });
    }

    // Offset slider
    const offsetSlider = document.getElementById('cm-hair-offset');
    const offsetVal = document.getElementById('cm-hair-offset-val');
    if (offsetSlider) {
        offsetSlider.addEventListener('input', () => {
            if (offsetVal) offsetVal.textContent = parseFloat(offsetSlider.value).toFixed(4);
        });
    }

    // Hairstyle select (NPZ info only)
    sel.addEventListener('change', () => {
        if (!sel.value) return;
        if (fn.serverLog) fn.serverLog('charmorph_hair', sel.value);
    });

    fn.loadCharmorphHairUI = loadCharmorphHairUI;
}

function _applyHairColor(hex) {
    const inst = state.selectedCharacterId ? state.characters.get(state.selectedCharacterId) : null;
    if (!inst || !inst.hairMesh) return;
    const color = new state.THREE.Color(hex);
    inst.hairMesh.traverse(c => {
        if (c.isMesh && c.material) {
            (Array.isArray(c.material) ? c.material : [c.material]).forEach(m => m.color.copy(color));
        }
    });
}
