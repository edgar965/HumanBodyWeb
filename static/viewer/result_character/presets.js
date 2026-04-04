/**
 * Result Character — Preset loading and switching.
 */
import { state } from './state.js';
import { fn } from './registry.js';
import { sharedState, applyHairColor } from '../character_core.js?v=1';

const ss = sharedState;

/**
 * Load cloth, hair, and garments from a preset data object.
 */
export function loadPresetClothAndHair(preset) {
    fn.removeAllCloth();
    fn.removeAllGarments();
    fn.removeHair();

    // 1. Load cloth templates
    if (preset.cloth && preset.cloth.length > 0) {
        for (const c of preset.cloth) {
            const tpl = c.template || 'TPL_TSHIRT';
            const params = {
                method: 'template',
                template: tpl,
                segments: c.segments || 32,
                tightness: c.tightness !== undefined ? c.tightness : 0.5,
                top_extend: c.top_extend || 0,
                bottom_extend: c.bottom_extend || 0,
            };
            if (c.color) params.color = c.color;
            fn.loadCloth(`tpl_${tpl}`, params, c.color, true);
        }
    }

    // 2. Load hairstyle
    if (preset.hair_style && preset.hair_style.url) {
        fn.loadHair(preset.hair_style.url);
        if (preset.hair_style.color && ss.hairColorData[preset.hair_style.color]) {
            setTimeout(() => {
                if (state.hairMesh) applyHairColor(state.hairMesh, preset.hair_style.color, ss.hairColorData);
            }, 1000);
        }
    } else if (state.hairData && state.hairData.hairstyles) {
        const defaultHair = state.hairData.hairstyles.find(h => h.name === 'ballerina')
                         || state.hairData.hairstyles[0];
        if (defaultHair) fn.loadHair(defaultHair.url);
    }

    // 3. Load MH garments
    if (preset.garments && preset.garments.length > 0) {
        const loadGarments = async () => {
            for (const g of preset.garments) {
                await fn.loadGarment(g.id, {
                    offset: g.offset || 0.006,
                    stiffness: g.stiffness || 0.8,
                    color: g.color,
                    roughness: g.roughness,
                    metalness: g.metalness,
                });
            }
        };
        setTimeout(() => loadGarments(), 800);
    }
}

/**
 * Switch to a different model preset.
 */
export async function reloadForPreset(presetName) {
    if (presetName === state.currentPresetName) return;

    if (state.loadingEl) {
        state.loadingEl.style.display = '';
        state.loadingEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Lade Modell...';
    }

    try {
        const resp = await fetch(`/api/character/model/${encodeURIComponent(presetName)}/`);
        if (!resp.ok) {
            console.error('[result_character] Failed to load preset:', presetName);
            if (state.loadingEl) state.loadingEl.style.display = 'none';
            return;
        }
        const preset = await resp.json();
        state.currentPresetName = presetName;

        // Update header dropdown
        if (state.modelSelectId) {
            const extSelect = document.getElementById(state.modelSelectId);
            if (extSelect && extSelect.value !== presetName) extSelect.value = presetName;
        }
        // Update side panel dropdown
        const panelSelect = document.getElementById('rc-model-preset');
        if (panelSelect && panelSelect.value !== presetName) panelSelect.value = presetName;

        const newBodyType = preset.body_type || 'Female_Caucasian';

        // Update morph/meta state from new preset
        state.currentMorphs = preset.morphs || {};
        state.currentMeta = preset.meta || {};

        if (newBodyType !== state.currentBodyType) {
            await fn.reloadBodyMesh(newBodyType);
        } else {
            fn.removeAllCloth();
            fn.removeAllGarments();
            fn.removeHair();
        }

        // Send morphs + meta to server
        if (Object.keys(state.currentMorphs).length > 0) {
            fn.wsSend({ type: 'morph_batch', morphs: state.currentMorphs });
        }
        for (const [name, val] of Object.entries(state.currentMeta)) {
            if (Math.abs(val) > 0.001) {
                fn.wsSend({ type: 'meta', name, value: val });
            }
        }

        // Update morph sliders in UI
        document.querySelectorAll('#rc-panel input[type="range"][data-morph]').forEach(s => {
            const v = state.currentMorphs[s.dataset.morph] || 0;
            s.value = Math.round(v * 100);
            if (s.nextElementSibling) s.nextElementSibling.textContent = String(Math.round(v * 100));
        });

        // Load preset's cloth/hair/garments
        if (state.isSkinned) {
            loadPresetClothAndHair(preset);
        }
    } catch (e) {
        console.error('[result_character] Preset switch failed:', e);
    }

    if (state.loadingEl) state.loadingEl.style.display = 'none';
}

fn.loadPresetClothAndHair = loadPresetClothAndHair;
fn.reloadForPreset = reloadForPreset;
