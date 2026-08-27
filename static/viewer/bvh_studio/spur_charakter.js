/**
 * Figur einer Spur laden — Anmeldung.
 *
 * Der Aufbau steckt in `Spurfigur` (spurfigur.js), Kleidung und Haare in
 * `Spurzubehoer`. Vorher standen hier zwei Funktionen mit je 113 Zeilen, die
 * beide Netzdaten holten, ein SkinnedMesh bauten und banden.
 */
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';
import { computeSkinAttributes } from '../character_core.js';
import { _sanitizeBoneNames } from './spur_clips.js';
import { Spurzubehoer } from './spurzubehoer.js';
import { Spurfigur } from './spurfigur.js';

export async function _loadPresetAccessories(track, modelData) {
    return new Spurzubehoer(track, modelData).laden();
}

export async function loadTrackCharacter(track) {
    return new Spurfigur(track, {
        skelettBauen: buildRigifySkeleton,
        gewichteBauen: computeSkinAttributes,
        namenSaeubern: _sanitizeBoneNames,
    }).laden();
}
