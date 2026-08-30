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
    Szeneneinstellungen.hautWerte(Szeneneinstellungen.erstesMaterial(mesh));
}

fn.applySceneSkinSettings = applySceneSkinSettings;
