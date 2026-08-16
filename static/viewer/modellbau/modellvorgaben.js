/**
 * Modellvorgaben — welche Form ein Knochen bekommt, wenn nichts gewaehlt ist.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026).
 */

import { Knochengruppen } from './knochengruppen.js';
import { computeBoneWorldTransforms, computeRigBoneWorldTransforms }
    from './knochenmatrizen.js';


/**
 * Build default model configuration from skeleton data.
 * Auto-computes radius as bone_length × 0.2, clamped [0.01, 0.05].
 */
export function getDefaultModelConfig(skelData, swData) {
    const classified = Knochengruppen.einteilen(skelData);
    const worldTransforms = computeBoneWorldTransforms(skelData, swData);

    const boneParts = {};
    const defaultColor = '#4488cc';
    const defaultRadius = 0.03;

    const allVisible = [...classified.body];
    const allHidden  = [...classified.finger, ...classified.face];

    for (const name of allVisible) {
        const wt = worldTransforms.get(name);
        const len = wt ? wt.length : 0.1;
        const autoRadius = Math.min(0.05, Math.max(0.01, len * 0.2));
        boneParts[name] = {
            shape: 'cylinder',
            radius: parseFloat(autoRadius.toFixed(4)),
            color: defaultColor,
            visible: true,
        };
    }
    for (const name of allHidden) {
        const wt = worldTransforms.get(name);
        const len = wt ? wt.length : 0.05;
        const autoRadius = Math.min(0.05, Math.max(0.01, len * 0.2));
        boneParts[name] = {
            shape: 'cylinder',
            radius: parseFloat(autoRadius.toFixed(4)),
            color: defaultColor,
            visible: false,
        };
    }

    return {
        type: 'generated_model',
        version: 1,
        name: 'Neues Modell',
        bone_parts: boneParts,
        default_color: defaultColor,
        default_radius: defaultRadius,
        segments: 8,
    };
}

/**
 * Build default config for rig bones. Only DEF bones visible by default.
 */
export function getDefaultRigConfig(rigData) {
    const classified = Knochengruppen.einteilenRig(rigData);
    const worldTransforms = computeRigBoneWorldTransforms(rigData);

    const boneParts = {};
    const defaultColor = '#4488cc';
    const defaultRadius = 0.03;
    const colors = {
        def: '#4488cc',
        mch: '#cc8844',
        org: '#44cc88',
        control: '#cc4488',
    };

    for (const [cat, boneList] of Object.entries(classified)) {
        const visible = cat === 'def';
        for (const name of boneList) {
            const wt = worldTransforms.get(name);
            const len = wt ? wt.length : 0.05;
            const autoRadius = Math.min(0.05, Math.max(0.005, len * 0.15));
            boneParts[name] = {
                shape: 'cylinder',
                radius: parseFloat(autoRadius.toFixed(4)),
                color: colors[cat],
                visible,
            };
        }
    }

    return {
        type: 'generated_model',
        skeleton_type: 'rig',
        version: 1,
        name: 'Rig Model',
        bone_parts: boneParts,
        default_color: defaultColor,
        default_radius: defaultRadius,
        segments: 8,
    };
}
