/**
 * Viewer — Scene settings (lighting, renderer, camera from localStorage).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

// Die Tabelle stand hier als eine von vier Kopien, eine davon unter
// anderem Namen — jetzt an EINER Stelle (`gemeinsam/tonwerte.js`,
// Befunde `doppelcode` und `namensvarianten`, 17.08.2026).
import { tonwerte } from '../gemeinsam/tonwerte.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Szeneneinstellungen } from '../gemeinsam/szeneneinstellungen.js';
// Der alte Name bleibt, damit die Aufrufstellen dieser Seite
// unveraendert bleiben — inhaltlich WAR er dieselbe Tabelle.
export const VIEWER_TONE_MAPPINGS = tonwerte(THREE);

export function applySceneSettings() {
    new Szeneneinstellungen({
        keyLight: state.keyLight,
        fillLight: state.fillLight,
        backLight: state.backLight,
        ambient: state.ambient,
        renderer: state.renderer,
        scene: state.scene,
        camera: state.camera,
        tonwerte: VIEWER_TONE_MAPPINGS,
        woher: 'scene_settings',
    }).anwenden();
}

export function getSkinMat() {
    if (!state.bodyMesh || !state.bodyMesh.material) return null;
    return Array.isArray(state.bodyMesh.material) ? state.bodyMesh.material[0] : state.bodyMesh.material;
}

export function syncSkinUI(mat) {
    if (!mat) return;
    const colorInput = document.getElementById('skin-color-viewer');
    if (colorInput) colorInput.value = '#' + mat.color.getHexString();
    const roughSlider = document.getElementById('skin-roughness-viewer');
    const roughVal = document.getElementById('skin-roughness-viewer-val');
    if (roughSlider) {
        roughSlider.value = Math.round(mat.roughness * 100);
        roughVal.textContent = mat.roughness.toFixed(2);
    }
    const metalSlider = document.getElementById('skin-metalness-viewer');
    const metalVal = document.getElementById('skin-metalness-viewer-val');
    if (metalSlider) {
        metalSlider.value = Math.round(mat.metalness * 100);
        metalVal.textContent = mat.metalness.toFixed(2);
    }
}

export function applySceneSkinSettings() {
    const mat = getSkinMat();
    // Die Regler NUR nachziehen, wenn wirklich etwas uebernommen wurde —
    // sonst zeigten sie Werte an, die nirgends stehen.
    if (Szeneneinstellungen.hautWerte(mat)) syncSkinUI(mat);
}

export function applySkinColor() {
    const select = document.getElementById('body-type-select');
    const bodyType = select?.value || '';
    if (!bodyType || !Object.keys(state.skinColors).length) return;
    const parts = bodyType.split('_');
    const ethnicity = parts[1] || parts[0];
    const colors = state.skinColors[ethnicity];
    const mat = getSkinMat();
    if (colors && mat) {
        mat.color.setRGB(
            Math.pow(colors[0], 1/2.2),
            Math.pow(colors[1], 1/2.2),
            Math.pow(colors[2], 1/2.2)
        );
        syncSkinUI(mat);
    }
}

export function applyExpandedPanels() {
    fetch('/api/settings/humanbody/')
        .then(r => r.json())
        .then(s => {
            const expanded = s.expanded_panels_config;
            if (Array.isArray(expanded)) {
                document.querySelectorAll('.panel-section[data-panel-key]').forEach(panel => {
                    const key = panel.dataset.panelKey;
                    if (expanded.includes(key)) {
                        panel.classList.remove('collapsed');
                    } else {
                        panel.classList.add('collapsed');
                    }
                });
            }
            if (typeof s.selection_opacity === 'number') {
                const o = s.selection_opacity;
                state._SELECT_EMISSIVE = new THREE.Color(o * 0.267, o * 0.267, o * 0.667);
                state._HOVER_EMISSIVE = new THREE.Color(o * 0.133, o * 0.133, o * 0.333);
            }
        })
        .catch((e) => { Protokoll.debug('szeneneinstellungen', 'Hover-Farbe nicht abrufbar', e); });
}

// Register
fn.applySceneSkinSettings = applySceneSkinSettings;
