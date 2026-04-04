/**
 * Scene Editor -- sessionStorage persistence.
 */
import { THREE, TONE_MAPPINGS } from './state.js';
import { state, SESSION_KEY } from './state.js';
import { fn } from './registry.js';

// =========================================================================
// Save session state to sessionStorage
// =========================================================================
export function saveSessionState() {
    try {
        if (!fn.gatherSceneState) return;
        const sceneData = fn.gatherSceneState();
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(sceneData));
    } catch (e) {
        console.warn('Failed to save session state:', e);
    }
}

// =========================================================================
// Restore session state from sessionStorage
// =========================================================================
export async function restoreSessionState() {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return false;
    try {
        const data = JSON.parse(raw);
        sessionStorage.removeItem(SESSION_KEY);

        // Restore characters
        if (data.characters && data.characters.length > 0) {
            fn.clearAllCharacters();
            for (const charData of data.characters) {
                try {
                    const CharacterInstance = fn.CharacterInstance;
                    const inst = await CharacterInstance.fromJSON(charData);
                    state.characters.set(inst.id, inst);
                    state.scene.add(inst.group);
                } catch (e) {
                    console.error(`Failed to restore character ${charData.presetName}:`, e);
                }
            }
        }

        // Restore lighting
        if (data.lighting) {
            if (data.lighting.key) {
                state.keyLight.intensity = data.lighting.key.intensity;
                state.keyLight.color.set(data.lighting.key.color);
                state.keyLight.position.set(...data.lighting.key.pos);
            }
            if (data.lighting.fill) {
                state.fillLight.intensity = data.lighting.fill.intensity;
                state.fillLight.color.set(data.lighting.fill.color);
                state.fillLight.position.set(...data.lighting.fill.pos);
            }
            if (data.lighting.back) {
                state.backLight.intensity = data.lighting.back.intensity;
                state.backLight.color.set(data.lighting.back.color);
                state.backLight.position.set(...data.lighting.back.pos);
            }
            if (data.lighting.ambient) {
                state.ambientLight.intensity = data.lighting.ambient.intensity;
                state.ambientLight.color.set(data.lighting.ambient.color);
            }
        }

        // Restore renderer
        if (data.renderer) {
            if (data.renderer.toneMapping && TONE_MAPPINGS[data.renderer.toneMapping] !== undefined) {
                state.renderer.toneMapping = TONE_MAPPINGS[data.renderer.toneMapping];
            }
            if (data.renderer.exposure !== undefined) {
                state.renderer.toneMappingExposure = data.renderer.exposure;
            }
            if (data.renderer.background) {
                state.scene.background.set(data.renderer.background);
            }
        }

        // Restore camera
        if (data.camera) {
            if (data.camera.fov) {
                state.camera.fov = data.camera.fov;
                state.camera.updateProjectionMatrix();
            }
            if (data.camera.position) state.camera.position.fromArray(data.camera.position);
            if (data.camera.target) state.controls.target.fromArray(data.camera.target);
            state.controls.update();
        }

        fn.syncUIFromState();
        fn.updateCharacterListUI();
        fn.updateVertexCount();

        if (state.characters.size > 0 && !state.selectedCharacterId) {
            fn.selectCharacter(state.characters.keys().next().value);
        }

        return true;
    } catch (e) {
        console.error('Failed to restore session state:', e);
        return false;
    }
}

// Register
fn.saveSessionState = saveSessionState;
fn.restoreSessionState = restoreSessionState;
