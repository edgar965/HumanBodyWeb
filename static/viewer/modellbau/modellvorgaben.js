/**
 * Modellvorgaben — welche Form ein Knochen bekommt, wenn nichts gewaehlt ist.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026).
 */

import { Knochengruppen } from './knochengruppen.js';
import { computeBoneWorldTransforms, computeRigBoneWorldTransforms }
    from './knochenmatrizen.js';
import { Knochenteil } from './knochenteil.js';


/**
 * Build default model configuration from skeleton data.
 * Auto-computes radius as bone_length × 0.2, clamped [0.01, 0.05].
 */
export function getDefaultModelConfig(skelData, swData) {
    const classified = Knochengruppen.einteilen(skelData);
    const worldTransforms = computeBoneWorldTransforms(skelData, swData);

    const boneParts = {};
    const defaultColor = '#4488cc';

    // Ersatzlaenge 0,10 fuer sichtbare, 0,05 fuer versteckte Knochen: Finger
    // und Gesichtsknochen sind kuerzer, und ohne Weltmatrix soll ihr Teil nicht
    // dicker ausfallen als der eines Oberschenkels.
    const sichtbarMass = { faktor: 0.2, mindestmass: 0.01, ersatzlaenge: 0.1 };
    const kleinMass = { faktor: 0.2, mindestmass: 0.01, ersatzlaenge: 0.05 };

    for (const name of classified.body) {
        boneParts[name] = Knochenteil.bauen(worldTransforms.get(name), sichtbarMass,
                                            { farbe: defaultColor, sichtbar: true });
    }
    for (const name of [...classified.finger, ...classified.face]) {
        boneParts[name] = Knochenteil.bauen(worldTransforms.get(name), kleinMass,
                                            { farbe: defaultColor, sichtbar: false });
    }

    return _huelle(boneParts, 'Neues Modell');
}

/**
 * Die Huelle einer Modellvorgabe — alles ausser den Knochenteilen.
 *
 * BEFUND `doppelcode` (30.08.2026): Stand zweimal in dieser Datei, einmal
 * fuer das Skelett und einmal fuer das Rig.
 *
 * `version` und `type` sind DRAHTFORMAT: Der Server erkennt an ihnen, dass
 * eine gespeicherte Datei ein erzeugtes Modell ist. `default_color` und
 * `default_radius` sind die Werte, die ein NEU hinzukommender Knochen bekommt
 * — nicht die der vorhandenen; die tragen ihre eigenen.
 *
 * `segments: 8` ist die Aufloesung der Zylinder. Mehr kostet Punkte in jedem
 * einzelnen Teil; bei 700 Rig-Knochen macht sich das sofort bemerkbar.
 */
function _huelle(boneParts, name, skelettart = null) {
    const huelle = {
        type: 'generated_model',
        version: 1,
        name,
        bone_parts: boneParts,
        default_color: '#4488cc',
        default_radius: 0.03,
        segments: 8,
    };
    if (skelettart) huelle.skeleton_type = skelettart;
    return huelle;
}

/**
 * Build default config for rig bones. Only DEF bones visible by default.
 */
export function getDefaultRigConfig(rigData) {
    const classified = Knochengruppen.einteilenRig(rigData);
    const worldTransforms = computeRigBoneWorldTransforms(rigData);

    const boneParts = {};
    const colors = {
        def: '#4488cc',
        mch: '#cc8844',
        org: '#44cc88',
        control: '#cc4488',
    };

    // Feiner als beim Skelett (Faktor 0,15 statt 0,20, Mindestmass 0,005 statt
    // 0,010): Im Rig liegen Steuerknochen neben den DEF-Knochen und verdecken
    // sie mit dem groeberen Mass.
    const rigMass = { faktor: 0.15, mindestmass: 0.005, ersatzlaenge: 0.05 };
    for (const [cat, boneList] of Object.entries(classified)) {
        for (const name of boneList) {
            boneParts[name] = Knochenteil.bauen(
                worldTransforms.get(name), rigMass,
                { farbe: colors[cat], sichtbar: cat === 'def' });
        }
    }

    return _huelle(boneParts, 'Rig Model', 'rig');
}
