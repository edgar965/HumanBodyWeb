/**
 * Animationsbaum und Wiedergabe der Vergleichsseite.
 *
 * Aus skeleton_test.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 18.08.2026: 232 Zeilen. Jetzt:
 *
 *     animationsbaum.js        Liste der Kategorien + Ruhelagen-Skelette
 *     vergleichswiedergabe.js  Laden, Abspielen, Anhalten, Zeitleiste
 *     mischerbund.js           mehrere AnimationMixer als einer
 *
 * Hier bleiben die Einstiegspunkte, die `aufbau.js` aufruft. Entfallen sind die
 * Debug-Globalen `window._cmuMixer`, `_cmuRootBone`, `_defMixer`, `_defRootBone`
 * und `_defClip` — sie wurden nirgends gelesen.
 */

import '../animation/wiedergabe.js';
import { Animationsbaum } from './animationsbaum.js';
import { Vergleichswiedergabe } from './vergleichswiedergabe.js';

export async function loadAnimationTree() {
    const baum = new Animationsbaum(document.getElementById('anim-tree'),
                                    Vergleichswiedergabe.laden);
    return baum.laden();
}

export function bindPlaybackControls() {
    Vergleichswiedergabe.bedienungBinden();
}

export function stopAnimation() {
    Vergleichswiedergabe.anhalten();
}
