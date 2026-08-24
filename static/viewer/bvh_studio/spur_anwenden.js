/**
 * Spuren am Abspielkopf anwenden: BVH, Kamera, Licht, Ton, Modell, Objekt.
 *
 * Aus playback.js herausgeloest (Umbau 16.08.2026): Die Datei hatte 637 Zeilen
 * und zwei Aufgaben — die Wiedergabe steuern und je Spurart auswerten, was an
 * dieser Stelle der Zeitleiste gilt. Das Zweite ist der groessere Teil.
 *
 * UMBAU 17.08.2026: 288 Zeilen, vier Spurarten und ZWEIMAL dieselbe
 * Keyframe-Suche (Kamera und Licht, buchstabengleich). Jetzt:
 *
 *     schluesselpaar.js   die zwei Keyframes um ein Bild (einmal, für beide)
 *     kameraspur.js       Standort, Blickziel, Bildwinkel
 *     lichtspurwerte.js   Ort, Farbe, Stärke, Kegel
 *     bvhspur.js          den passenden Bewegungsclip spielen
 *     modellspur.js       welche Figur gerade gilt (mit Ladeschutz)
 *
 * Hier bleibt der Einstieg und die Objektspur — die ist vier Zeilen lang und
 * braucht keine eigene Datei.
 */

import { Bvhspur } from './bvhspur.js';
import { Kameraspur } from './kameraspur.js';
import { Lichtspurwerte } from './lichtspurwerte.js';
import { Modellspur } from './modellspur.js';

/**
 * Objektspur: Boden und eigene 3D-Objekte.
 *
 * Ein eigenes Objekt bleibt sichtbar, solange es überhaupt einen Clip hat — auch
 * ohne Wiedergabe. Nur so kann der Nutzer es anklicken und mit Alt+Klick
 * versetzen.
 */
export function applySceneObjectTrack(track, t) {
    if (!track.mesh) return;
    if (track.subtype === 'floor') {
        track.mesh.visible = !track.muted;
        return;
    }
    const hatClips = track.clips.some(clip => clip.type === 'object_clip');
    track.mesh.visible = hatClips && !track.muted;
}

export function applyBvhTrack(track, t) { Bvhspur.anwenden(track, t); }
export function applyCameraTrack(track, t) { Kameraspur.anwenden(track, t); }
export function applyLightTrack(track, t) { Lichtspurwerte.anwenden(track, t); }
export function applyModelTrack(track, t) { Modellspur.anwenden(track, t); }
