/**
 * scene_session.js — sessionStorage persistence for the Scene Editor.
 * Survives page navigation within the same tab.
 */
import { TONE_MAPPINGS } from './scene_state.js?v=1';
import { state, SESSION_KEY } from './scene_state.js?v=1';

// =========================================================================
// Save session state to sessionStorage
// =========================================================================
export function saveSessionState(gatherSceneState) {
    try {
        const sceneData = gatherSceneState();
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(sceneData));
    } catch (e) {
        console.warn('Failed to save session state:', e);
    }
}

// =========================================================================
// Restore session state from sessionStorage
// =========================================================================
export async function restoreSessionState({
    CharacterInstance,
    clearAllCharacters,
    syncUIFromState,
    updateCharacterListUI,
    updateVertexCount,
    selectCharacter,
    gatherSceneState,
}) {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return false;
    try {
        const data = JSON.parse(raw);
        sessionStorage.removeItem(SESSION_KEY);

        // Restore characters
        if (data.characters && data.characters.length > 0) {
            clearAllCharacters();
            for (const charData of data.characters) {
                try {
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

        state.currentSceneName = data.name || '';
        syncUIFromState();
        updateCharacterListUI();
        updateVertexCount();

        // Auto-select first character so Assets tab is immediately usable
        if (state.characters.size > 0 && !state.selectedCharacterId) {
            selectCharacter(state.characters.keys().next().value);
        }

        console.log('Session state restored');
        return true;
    } catch (e) {
        console.warn('Failed to restore session state:', e);
        sessionStorage.removeItem(SESSION_KEY);
        return false;
    }
}
