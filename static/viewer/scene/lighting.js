/**
 * Scene Editor -- Lighting, renderer, camera UI bindings.
 */
import { THREE, LIGHT_PRESETS, TONE_MAPPINGS } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { markDirty, markClean } from './undo.js';

function autoSave() {
    clearTimeout(state.saveTimer);
    state.saveTimer = setTimeout(() => {
        const settings = gatherSettings();
        localStorage.setItem('humanbody_scene_settings', JSON.stringify(settings));
    }, 300);
    markDirty();
}

export function resetLighting() {
    const preset = LIGHT_PRESETS.studio;
    state.keyLight.intensity = preset.key.intensity;
    state.keyLight.color.set(preset.key.color);
    state.keyLight.position.set(...preset.key.pos);
    state.fillLight.intensity = preset.fill.intensity;
    state.fillLight.color.set(preset.fill.color);
    state.fillLight.position.set(...preset.fill.pos);
    state.backLight.intensity = preset.back.intensity;
    state.backLight.color.set(preset.back.color);
    state.backLight.position.set(...preset.back.pos);
    state.ambientLight.intensity = preset.ambient.intensity;
    state.ambientLight.color.set(preset.ambient.color);
    state.renderer.toneMappingExposure = preset.exposure;
    syncUIFromState();
    markDirty();
}

export function resetCamera() {
    state.camera.fov = 35;
    state.camera.position.set(0, 1.0, 3.5);
    state.camera.updateProjectionMatrix();
    state.controls.target.set(0, 0.9, 0);
    state.controls.update();
    markDirty();
}

function applyPreset(preset) {
    state.keyLight.intensity = preset.key.intensity;
    state.keyLight.color.setHex(preset.key.color);
    state.keyLight.position.set(...preset.key.pos);
    state.fillLight.intensity = preset.fill.intensity;
    state.fillLight.color.setHex(preset.fill.color);
    state.fillLight.position.set(...preset.fill.pos);
    state.backLight.intensity = preset.back.intensity;
    state.backLight.color.setHex(preset.back.color);
    state.backLight.position.set(...preset.back.pos);
    state.ambientLight.intensity = preset.ambient.intensity;
    state.ambientLight.color.setHex(preset.ambient.color);
    state.renderer.toneMappingExposure = preset.exposure;
    syncUIFromState();
}

export function syncUIFromState() {
    setSlider('key-intensity', state.keyLight.intensity * 100, 'key-intensity-val', v => (v / 100).toFixed(1));
    setColor('key-color', state.keyLight.color);
    setSlider('key-pos-x', state.keyLight.position.x * 10, 'key-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('key-pos-y', state.keyLight.position.y * 10, 'key-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('key-pos-z', state.keyLight.position.z * 10, 'key-pos-z-val', v => (v / 10).toFixed(1));
    setSlider('fill-intensity', state.fillLight.intensity * 100, 'fill-intensity-val', v => (v / 100).toFixed(1));
    setColor('fill-color', state.fillLight.color);
    setSlider('fill-pos-x', state.fillLight.position.x * 10, 'fill-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('fill-pos-y', state.fillLight.position.y * 10, 'fill-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('fill-pos-z', state.fillLight.position.z * 10, 'fill-pos-z-val', v => (v / 10).toFixed(1));
    setSlider('back-intensity', state.backLight.intensity * 100, 'back-intensity-val', v => (v / 100).toFixed(1));
    setColor('back-color', state.backLight.color);
    setSlider('back-pos-x', state.backLight.position.x * 10, 'back-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('back-pos-y', state.backLight.position.y * 10, 'back-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('back-pos-z', state.backLight.position.z * 10, 'back-pos-z-val', v => (v / 10).toFixed(1));
    setSlider('ambient-intensity', state.ambientLight.intensity * 100, 'ambient-intensity-val', v => (v / 100).toFixed(1));
    setColor('ambient-color', state.ambientLight.color);
    setSlider('exposure', state.renderer.toneMappingExposure * 100, 'exposure-val', v => (v / 100).toFixed(1));
    const tmSelect = document.getElementById('tone-mapping');
    for (const [name, val] of Object.entries(TONE_MAPPINGS)) {
        if (val === state.renderer.toneMapping) { tmSelect.value = name; break; }
    }
    setColor('bg-color', state.scene.background);
    setSlider('camera-fov', state.camera.fov, 'camera-fov-val', v => Math.round(v).toString());
}

function setSlider(id, value, displayId, toDisplay) {
    const slider = document.getElementById(id);
    slider.value = Math.round(value);
    document.getElementById(displayId).textContent = toDisplay(parseFloat(slider.value));
}

function setColor(id, threeColor) {
    document.getElementById(id).value = '#' + threeColor.getHexString();
}

export function bindLightingUI() {
    function bindSl(id, displayId, toDisplay, onChange) {
        const slider = document.getElementById(id);
        const display = document.getElementById(displayId);
        slider.addEventListener('input', () => {
            const v = parseFloat(slider.value);
            display.textContent = toDisplay(v);
            onChange(v);
            autoSave();
        });
    }

    bindSl('key-intensity', 'key-intensity-val', v => (v / 100).toFixed(1), v => { state.keyLight.intensity = v / 100; });
    document.getElementById('key-color').addEventListener('input', e => { state.keyLight.color.set(e.target.value); autoSave(); });
    bindSl('key-pos-x', 'key-pos-x-val', v => (v / 10).toFixed(1), v => { state.keyLight.position.x = v / 10; });
    bindSl('key-pos-y', 'key-pos-y-val', v => (v / 10).toFixed(1), v => { state.keyLight.position.y = v / 10; });
    bindSl('key-pos-z', 'key-pos-z-val', v => (v / 10).toFixed(1), v => { state.keyLight.position.z = v / 10; });
    bindSl('fill-intensity', 'fill-intensity-val', v => (v / 100).toFixed(1), v => { state.fillLight.intensity = v / 100; });
    document.getElementById('fill-color').addEventListener('input', e => { state.fillLight.color.set(e.target.value); autoSave(); });
    bindSl('fill-pos-x', 'fill-pos-x-val', v => (v / 10).toFixed(1), v => { state.fillLight.position.x = v / 10; });
    bindSl('fill-pos-y', 'fill-pos-y-val', v => (v / 10).toFixed(1), v => { state.fillLight.position.y = v / 10; });
    bindSl('fill-pos-z', 'fill-pos-z-val', v => (v / 10).toFixed(1), v => { state.fillLight.position.z = v / 10; });
    bindSl('back-intensity', 'back-intensity-val', v => (v / 100).toFixed(1), v => { state.backLight.intensity = v / 100; });
    document.getElementById('back-color').addEventListener('input', e => { state.backLight.color.set(e.target.value); autoSave(); });
    bindSl('back-pos-x', 'back-pos-x-val', v => (v / 10).toFixed(1), v => { state.backLight.position.x = v / 10; });
    bindSl('back-pos-y', 'back-pos-y-val', v => (v / 10).toFixed(1), v => { state.backLight.position.y = v / 10; });
    bindSl('back-pos-z', 'back-pos-z-val', v => (v / 10).toFixed(1), v => { state.backLight.position.z = v / 10; });
    bindSl('ambient-intensity', 'ambient-intensity-val', v => (v / 100).toFixed(1), v => { state.ambientLight.intensity = v / 100; });
    document.getElementById('ambient-color').addEventListener('input', e => { state.ambientLight.color.set(e.target.value); autoSave(); });
    document.getElementById('light-preset').addEventListener('change', e => {
        const preset = LIGHT_PRESETS[e.target.value];
        if (!preset) return;
        applyPreset(preset);
        autoSave();
    });
}

export function bindRendererUI() {
    document.getElementById('tone-mapping').addEventListener('change', e => {
        state.renderer.toneMapping = TONE_MAPPINGS[e.target.value] || THREE.ACESFilmicToneMapping;
        autoSave();
    });
    const expSlider = document.getElementById('exposure');
    const expVal = document.getElementById('exposure-val');
    expSlider.addEventListener('input', () => {
        const v = parseFloat(expSlider.value) / 100;
        expVal.textContent = v.toFixed(1);
        state.renderer.toneMappingExposure = v;
        autoSave();
    });
    document.getElementById('bg-color').addEventListener('input', e => {
        state.scene.background.set(e.target.value);
        autoSave();
    });
}

export function bindCameraUI() {
    const fovSlider = document.getElementById('camera-fov');
    const fovVal = document.getElementById('camera-fov-val');
    fovSlider.addEventListener('input', () => {
        const v = parseInt(fovSlider.value);
        fovVal.textContent = v;
        state.camera.fov = v;
        state.camera.updateProjectionMatrix();
        autoSave();
    });
}

export function bindActions() {
    document.getElementById('btn-apply').addEventListener('click', () => {
        const settings = gatherSettings();
        localStorage.setItem('humanbody_scene_settings', JSON.stringify(settings));
        const btn = document.getElementById('btn-apply');
        const orig = btn.textContent;
        btn.textContent = 'Gespeichert!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
    });
    document.getElementById('btn-reset').addEventListener('click', () => {
        applyPreset(LIGHT_PRESETS.studio);
        state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        state.scene.background.set(0x1a1a2e);
        state.camera.fov = 35;
        state.camera.updateProjectionMatrix();
        document.getElementById('light-preset').value = 'studio';
        syncUIFromState();
        autoSave();
    });
    document.getElementById('btn-export').addEventListener('click', () => {
        const settings = gatherSettings();
        const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'humanbody_scene_settings.json'; a.click();
        URL.revokeObjectURL(url);
    });
}

export function gatherSettings() {
    return {
        lighting: {
            key: { intensity: state.keyLight.intensity, color: '#' + state.keyLight.color.getHexString(), pos: [state.keyLight.position.x, state.keyLight.position.y, state.keyLight.position.z] },
            fill: { intensity: state.fillLight.intensity, color: '#' + state.fillLight.color.getHexString(), pos: [state.fillLight.position.x, state.fillLight.position.y, state.fillLight.position.z] },
            back: { intensity: state.backLight.intensity, color: '#' + state.backLight.color.getHexString(), pos: [state.backLight.position.x, state.backLight.position.y, state.backLight.position.z] },
            ambient: { intensity: state.ambientLight.intensity, color: '#' + state.ambientLight.color.getHexString() }
        },
        renderer: {
            toneMapping: document.getElementById('tone-mapping').value,
            exposure: state.renderer.toneMappingExposure,
            background: '#' + state.scene.background.getHexString()
        },
        camera: { fov: state.camera.fov },
    };
}

export function loadSettings() {
    const saved = localStorage.getItem('humanbody_scene_settings');
    if (!saved) return;
    try {
        const s = JSON.parse(saved);
        if (s.lighting) {
            if (s.lighting.key) { state.keyLight.intensity = s.lighting.key.intensity; state.keyLight.color.set(s.lighting.key.color); state.keyLight.position.set(...s.lighting.key.pos); }
            if (s.lighting.fill) { state.fillLight.intensity = s.lighting.fill.intensity; state.fillLight.color.set(s.lighting.fill.color); state.fillLight.position.set(...s.lighting.fill.pos); }
            if (s.lighting.back) { state.backLight.intensity = s.lighting.back.intensity; state.backLight.color.set(s.lighting.back.color); state.backLight.position.set(...s.lighting.back.pos); }
            if (s.lighting.ambient) { state.ambientLight.intensity = s.lighting.ambient.intensity; state.ambientLight.color.set(s.lighting.ambient.color); }
        }
        if (s.renderer) {
            if (s.renderer.toneMapping && TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) state.renderer.toneMapping = TONE_MAPPINGS[s.renderer.toneMapping];
            if (s.renderer.exposure !== undefined) state.renderer.toneMappingExposure = s.renderer.exposure;
            if (s.renderer.background) state.scene.background.set(s.renderer.background);
        }
        if (s.camera && s.camera.fov) { state.camera.fov = s.camera.fov; state.camera.updateProjectionMatrix(); }
        document.getElementById('light-preset').value = '';
        syncUIFromState();
    } catch (e) { console.warn('Failed to load scene settings:', e); }
}

// Register
fn.resetLighting = resetLighting;
fn.resetCamera = resetCamera;
fn.syncUIFromState = syncUIFromState;
fn.autoSave = autoSave;
fn.bindLightingUI = bindLightingUI;
fn.bindRendererUI = bindRendererUI;
fn.bindCameraUI = bindCameraUI;
fn.bindActions = bindActions;
fn.loadSettings = loadSettings;
fn.gatherSettings = gatherSettings;
fn.applyPreset = applyPreset;
