/**
 * charmorph_hair.js — CharMorph hairstyle browser in Assets tab.
 */
import { state } from './state.js';
import { fn } from './registry.js';

export async function loadCharmorphHairUI() {
    const sel = document.getElementById('cm-hairstyle');
    if (!sel) return;

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
    } catch (e) {
        console.error('[CharMorph Hair] Load failed:', e);
    }

    // Color picker
    const colorInput = document.getElementById('cm-hair-color');
    if (colorInput) {
        colorInput.addEventListener('input', () => {
            console.log(`[CharMorph Hair] Color: ${colorInput.value}`);
        });
    }

    // Shrinkwrap checkbox
    const shrinkwrap = document.getElementById('cm-hair-shrinkwrap');
    if (shrinkwrap) {
        shrinkwrap.addEventListener('change', () => {
            console.log(`[CharMorph Hair] Shrinkwrap: ${shrinkwrap.checked}`);
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

    // Hairstyle select
    sel.addEventListener('change', () => {
        if (!sel.value) return;
        console.log(`[CharMorph Hair] Selected: ${sel.value}`);
        // TODO: Load hairstyle NPZ and apply to character
        alert(`Hairstyle "${sel.value}" ausgewaehlt.\n\nCharMorph Hairstyles sind NPZ-Dateien (Partikel-Daten).\nDiese muessen erst fuer Web konvertiert werden.`);
    });

    fn.loadCharmorphHairUI = loadCharmorphHairUI;
}
