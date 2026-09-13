/**
 * Figur einer Spur laden — Anmeldung.
 *
 * Der Aufbau steckt in `Spurfigur` (spurfigur.js), und die baut seit dem
 * 13.09.2026 nichts mehr selbst: Sie setzt ein `HumanbodyModell`
 * (`gemeinsam/humanbodymodell.js`) in die Spur. Vorher standen hier zwei
 * Funktionen mit je 113 Zeilen, die beide Netzdaten holten, ein SkinnedMesh
 * bauten und banden.
 */
import { _sanitizeBoneNames } from './spur_clips.js';
import { Spurfigur } from './spurfigur.js';

export async function loadTrackCharacter(track) {
    return new Spurfigur(track, { namenSaeubern: _sanitizeBoneNames }).laden();
}
