/**
 * Viewer — Scene settings (lighting, renderer, camera from localStorage).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';

export const VIEWER_TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping
};

export function applySceneSettings() {
    const saved = localStorage.getItem('humanbody_scene_settings');
    if (!saved) return;
    try {
        const s = JSON.parse(saved);
        if (s.lighting) {
            if (s.lighting.key) {
                state.keyLight.intensity = s.lighting.key.intensity;
                state.keyLight.color.set(s.lighting.key.color);
                state.keyLight.position.set(...s.lighting.key.pos);
            }
            if (s.lighting.fill) {
                state.fillLight.intensity = s.lighting.fill.intensity;
                state.fillLight.color.set(s.lighting.fill.color);
                state.fillLight.position.set(...s.lighting.fill.pos);
            }
            if (s.lighting.back) {
                state.backLight.intensity = s.lighting.back.intensity;
                state.backLight.color.set(s.lighting.back.color);
                state.backLight.position.set(...s.lighting.back.pos);
            }
            if (s.lighting.ambient) {
                state.ambient.intensity = s.lighting.ambient.intensity;
                state.ambient.color.set(s.lighting.ambient.color);
            }
        }
        if (s.renderer) {
            if (s.renderer.toneMapping && VIEWER_TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) {
                state.renderer.toneMapping = VIEWER_TONE_MAPPINGS[s.renderer.toneMapping];
            }
            if (s.renderer.exposure !== undefined) {
                state.renderer.toneMappingExposure = s.renderer.exposure;
            }
            if (s.renderer.background) {
                state.scene.background.set(s.renderer.background);
            }
        }
        if (s.camera && s.camera.fov) {
            state.camera.fov = s.camera.fov;
            state.camera.updateProjectionMatrix();
        }
    } catch (e) {
        console.warn('Failed to load scene settings:', e);
    }
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
    if (roughSlider) { roughSlider.value = Math.round(mat.roughness * 100); roughVal.textContent = mat.roughness.toFixed(2); }
    const metalSlider = document.getElementById('skin-metalness-viewer');
    const metalVal = document.getElementById('skin-metalness-viewer-val');
    if (metalSlider) { metalSlider.value = Math.round(mat.metalness * 100); metalVal.textContent = mat.metalness.toFixed(2); }
}

export function applySceneSkinSettings() {
    const saved = localStorage.getItem('humanbody_scene_settings');
    const mat = getSkinMat();
    if (!saved || !mat) return;
    try {
        const s = JSON.parse(saved);
        if (s.skin) {
            if (s.skin.roughness !== undefined) mat.roughness = s.skin.roughness;
            if (s.skin.metalness !== undefined) mat.metalness = s.skin.metalness;
            syncSkinUI(mat);
        }
    } catch (e) { /* ignore */ }
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
        .catch(() => {});
}

// Register
fn.applySceneSettings = applySceneSettings;
fn.applySceneSkinSettings = applySceneSkinSettings;
fn.applySkinColor = applySkinColor;
fn.getSkinMat = getSkinMat;
fn.syncSkinUI = syncSkinUI;
fn.applyExpandedPanels = applyExpandedPanels;
