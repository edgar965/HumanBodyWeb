/**
 * Result Character — Scene settings from localStorage + skin settings.
 */
import { TONE_MAPPINGS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Szeneneinstellungen } from '../gemeinsam/szeneneinstellungen.js';

export function applySceneSettings(renderer, scene, camera, keyLight, fillLight, backLight, ambient) {
    new Szeneneinstellungen({
        keyLight, fillLight, backLight, ambient, renderer, scene, camera,
        tonwerte: TONE_MAPPINGS,
        woher: 'result_character',
    }).anwenden();
}

export function applySceneSkinSettings(mesh) {
    const saved = localStorage.getItem('humanbody_scene_settings');
    const mat = mesh && mesh.material
        ? (Array.isArray(mesh.material) ? mesh.material[0] : mesh.material)
        : null;
    if (!saved || !mat) return;
    try {
        const s = JSON.parse(saved);
        if (s.skin) {
            if (s.skin.roughness !== undefined) mat.roughness = s.skin.roughness;
            if (s.skin.metalness !== undefined) mat.metalness = s.skin.metalness;
        }
    } catch (e) { Protokoll.debug('szene', 'Hauteinstellungen nicht anwendbar', e); }
}

fn.applySceneSettings = applySceneSettings;
fn.applySceneSkinSettings = applySceneSkinSettings;
