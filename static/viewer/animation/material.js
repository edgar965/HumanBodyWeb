/**
 * Material und Beleuchtung der Animationsseite.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026).
 */

import * as THREE from 'three';
import { Seitenzustand } from './seitenzustand.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';


// =========================================================================
// Tone mapping lookup (for Seitenzustand.scene settings)
// =========================================================================
// Die Tabelle stand hier als eine von vier Kopien, eine davon unter
// anderem Namen — jetzt an EINER Stelle (`gemeinsam/tonwerte.js`,
// Befunde `doppelcode` und `namensvarianten`, 17.08.2026).
import { tonwerte } from '../gemeinsam/tonwerte.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Szeneneinstellungen } from '../gemeinsam/szeneneinstellungen.js';
export const TONE_MAPPINGS = tonwerte(THREE);

// =========================================================================
// Scene settings from localStorage
// =========================================================================
export function applySceneSettings(keyLight, fillLight, backLight, ambient) {
    new Szeneneinstellungen({
        keyLight, fillLight, backLight, ambient,
        renderer: Seitenzustand.renderer,
        scene: Seitenzustand.scene,
        camera: Seitenzustand.camera,
        tonwerte: TONE_MAPPINGS,
        woher: 'material',
    }).anwenden();
}

export function applySceneSkinSettings() {
    const saved = localStorage.getItem('humanbody_scene_settings');
    const mat = getSkinMat();
    if (!saved || !mat) return;
    try {
        const s = JSON.parse(saved);
        if (s.skin) {
            // NOTE: skin COLOR is NOT applied from Seitenzustand.scene settings —
            // it comes from SKIN_COLORS per ethnicity (body type).
            if (s.skin.roughness !== undefined) mat.roughness = s.skin.roughness;
            if (s.skin.metalness !== undefined) mat.metalness = s.skin.metalness;
        }
    } catch (e) { Protokoll.debug('material', 'Hauteinstellungen nicht anwendbar', e); }
}

// =========================================================================
// Mesh loading — full-mesh subdivision preserving all material groups
// =========================================================================
// Die Tabelle stand hier als sechste Kopie — jetzt an EINER Stelle
// (`gemeinsam/koerpermaterialien.js`, Befund `doppelcode` 17.08.2026).
export { BODY_MATERIALS } from '../gemeinsam/koerpermaterialien.js';

export function getSkinMat() {
    if (!Seitenzustand.bodyMesh || !Seitenzustand.bodyMesh.material) return null;
    return Array.isArray(Seitenzustand.bodyMesh.material) ? Seitenzustand.bodyMesh.material[0] : Seitenzustand.bodyMesh.material;
}

export function applySkinColor() {
    if (!Object.keys(Seitenzustand.skinColors).length) return;
    // Die Seite startet immer mit Female_Caucasian.
    Hautfarbe.setzen(getSkinMat(),
                     Seitenzustand.skinColors[Hautfarbe.ERSATZ_ETHNIE]);
}

export async function loadSkinColors() {
    try {
        const data = await Serverabruf.json('/api/character/morphs/');
        Seitenzustand.skinColors = data.skin_colors || {};
        applySkinColor();
    } catch (e) { Protokoll.debug('material', 'Hautfarben nicht abrufbar', e); }
}
