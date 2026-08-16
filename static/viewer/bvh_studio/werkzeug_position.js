/**
 * Feste Position — die Wurzel innerhalb eines Radius halten.
 *
 * Aus tools.js herausgeloest (Umbau 15.08.2026). Der Zwischenspeicher der
 * Originaldaten liegt am CLIP-OBJEKT, nicht an Indizes: Beim Loeschen einer
 * Spur zwischen Ein- und Ausschalten wurden sonst fremde Positionen
 * zurueckgeschrieben (Befund vom 15.08.2026).
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';


// =========================================================================
// Ground Fix (Bodenniveau)
// =========================================================================
// ── Fixed Position (clamp root XZ displacement) ──
// SCHLÜSSEL IST DAS CLIP-OBJEKT, nicht `trackIdx_clipIdx` (Review 15.08.2026).
//
// Der nachstellbare Ablauf mit den alten Index-Schlüsseln:
//   1. Zwei BVH-Spuren A (0) und B (1), „Feste Position" EIN
//      -> origData hat die Schlüssel "0_0" (A) und "1_0" (B)
//   2. Spur A löschen -> B rutscht auf Index 0. `removeTrack` weiß von dieser
//      Sicherung nichts, die Schlüssel bleiben stehen.
//   3. „Feste Position" AUS -> `restoreFixedPositionAll` löst "0_0" auf
//      `tracks[0].clips[0]` auf, und das ist jetzt B: B bekommt die
//      Originalposition VON A geschrieben. "1_0" findet keine Spur und wird
//      still übersprungen.
// Ergebnis: Die Figur springt an eine fremde Stelle, ohne eine einzige Meldung.
// Ein Objekt als Schlüssel überlebt jedes Umsortieren und braucht kein
// Aufräumen an anderer Stelle.
export const _fixedPos = { active: false, radius: 0.5, origData: new Map() };

export function applyFixedPositionAll() {
    const r = _fixedPos.radius;
    for (let ti = 0; ti < state.project.tracks.length; ti++) {
        const track = state.project.tracks[ti];
        for (let ci = 0; ci < track.clips.length; ci++) {
            const clip = track.clips[ci];
            if (!clip.animClip) continue;
            const posTrack = clip.animClip.tracks.find(t => t.name.includes('.position'));
            if (!posTrack) continue;
            // Save original if not already saved
            if (!_fixedPos.origData.has(clip)) _fixedPos.origData.set(clip, new Float32Array(posTrack.values));
            const orig = _fixedPos.origData.get(clip);
            // Anchor = frame 0 position
            const ax = orig[0], az = orig[2];
            for (let f = 0; f < posTrack.times.length; f++) {
                const i = f * 3;
                const dx = orig[i] - ax, dz = orig[i + 2] - az;
                const dist = Math.sqrt(dx * dx + dz * dz);
                if (dist > r) {
                    const scale = r / dist;
                    posTrack.values[i] = ax + dx * scale;
                    posTrack.values[i + 2] = az + dz * scale;
                } else {
                    posTrack.values[i] = orig[i];
                    posTrack.values[i + 2] = orig[i + 2];
                }
                posTrack.values[i + 1] = orig[i + 1]; // keep Y
            }
        }
    }
    fn.applyPlayhead();
    console.log(`[BVH Studio] Fixed position: radius=${r}m`);
}

export function restoreFixedPositionAll() {
    // Der Clip selbst ist der Schlüssel — kein Auflösen über Indizes mehr,
    // die zwischen Ein- und Ausschalten verrutschen können (siehe _fixedPos).
    for (const [clip, orig] of _fixedPos.origData) {
        if (!clip?.animClip) continue;
        const posTrack = clip.animClip.tracks.find(t => t.name.includes('.position'));
        if (!posTrack || posTrack.values.length !== orig.length) continue;
        posTrack.values.set(orig);
    }
    _fixedPos.origData.clear();
    fn.applyPlayhead();
    console.log('[BVH Studio] Fixed position: restored originals');
}
