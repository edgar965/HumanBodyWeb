/**
 * Photo To 3D — Facial expression to HumanBody bone rotation mapping.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';

// smplxExpr: [jawOpen, smile, browUp, browDown, lipUp, lipCorner, cheekPuff, squint, noseWrinkle, eyeWide]
export function applyFacialExpression(expr) {
    if (!state.rigifySkeleton || !state.rigifySkeleton.restQuats) return;
    const { boneByName, restQuats } = state.rigifySkeleton;

    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
    const jawOpen     = clamp(expr[0] || 0, 0, 1.5);
    const smile       = clamp(expr[1] || 0, -1.5, 1.5);
    const browUp      = clamp(expr[2] || 0, -1.5, 1.5);
    const browDown    = clamp(expr[3] || 0, -1.5, 1.5);
    const lipUp       = clamp(expr[4] || 0, -1.5, 1.5);
    const lipCorner   = clamp(expr[5] || 0, -1.5, 1.5);
    const cheekPuff   = clamp(expr[6] || 0, -1.5, 1.5);
    const squint      = clamp(expr[7] || 0, -1.5, 1.5);
    const noseWrinkle = clamp(expr[8] || 0, -1.5, 1.5);
    const eyeWide     = clamp(expr[9] || 0, -1.5, 1.5);

    const S = 0.03;  // Subtle bone rotation on top of vertex morphs
    const browNet = (browUp - browDown) * S;

    // Accumulate [rx, ry, rz] per bone (Blender local space)
    const acc = {};
    function add(name, rx, ry, rz) {
        if (!acc[name]) acc[name] = [0, 0, 0];
        acc[name][0] += rx;
        acc[name][1] += ry;
        acc[name][2] += rz;
    }

    // === JAW ===
    add('DEF-jaw', jawOpen * S, 0, 0);

    // === LIPS ===
    const sm = smile * S;
    const lu = lipUp * S;
    const lc = lipCorner * S;
    add('DEF-lip.T.L',     -lu, 0, 0);
    add('DEF-lip.T.R',     -lu, 0, 0);
    add('DEF-lip.T.L.001', -sm * 0.5, 0, -sm * 0.3 - lc * 0.5);
    add('DEF-lip.T.R.001', -sm * 0.5, 0,  sm * 0.3 + lc * 0.5);
    add('DEF-lip.B.L.001',  sm * 0.3, 0, -sm * 0.3 - lc * 0.5);
    add('DEF-lip.B.R.001',  sm * 0.3, 0,  sm * 0.3 + lc * 0.5);

    // === BROWS ===
    add('DEF-brow.B.L',       browNet,       0, 0);
    add('DEF-brow.B.L.001',   browNet * 0.8, 0, 0);
    add('DEF-brow.B.L.002',   browNet * 0.6, 0, 0);
    add('DEF-brow.B.R',       browNet,       0, 0);
    add('DEF-brow.B.R.001',   browNet * 0.8, 0, 0);
    add('DEF-brow.B.R.002',   browNet * 0.6, 0, 0);
    add('DEF-brow.T.L',       browNet * 0.5, 0, 0);
    add('DEF-brow.T.L.001',   browNet * 0.5, 0, 0);
    add('DEF-brow.T.R',       browNet * 0.5, 0, 0);
    add('DEF-brow.T.R.001',   browNet * 0.5, 0, 0);

    // === CHEEKS ===
    const ck = cheekPuff * S;
    add('DEF-cheek.B.L', 0, 0, -ck);
    add('DEF-cheek.B.R', 0, 0,  ck);
    add('DEF-cheek.T.L', 0, 0, -ck * 0.5);
    add('DEF-cheek.T.R', 0, 0,  ck * 0.5);

    // === EYELIDS ===
    const topLid = (squint - eyeWide) * S;
    const botLid = (-squint + eyeWide) * S;
    add('DEF-lid.T.L.001', topLid, 0, 0);
    add('DEF-lid.T.L.002', topLid, 0, 0);
    add('DEF-lid.T.R.001', topLid, 0, 0);
    add('DEF-lid.T.R.002', topLid, 0, 0);
    add('DEF-lid.B.L.001', botLid, 0, 0);
    add('DEF-lid.B.L.002', botLid, 0, 0);
    add('DEF-lid.B.R.001', botLid, 0, 0);
    add('DEF-lid.B.R.002', botLid, 0, 0);

    // === NOSE ===
    const nr = noseWrinkle * S * 0.5;
    add('DEF-nose.L',   0, 0, -nr);
    add('DEF-nose.R',   0, 0,  nr);
    add('DEF-nose.001', nr, 0,  0);

    // === CHIN ===
    add('DEF-chin',     jawOpen * S * 0.3, 0, 0);
    add('DEF-chin.001', jawOpen * S * 0.15, 0, 0);

    // Apply accumulated rotations to bones
    const tmpE = new THREE.Euler();
    const tmpQ = new THREE.Quaternion();
    for (const [name, [rx, ry, rz]] of Object.entries(acc)) {
        const bone = boneByName[name];
        const rest = restQuats[name];
        if (!bone || !rest) continue;
        // Blender local -> Three.js: swap Y<->Z, negate new Z
        tmpE.set(rx, rz, -ry, 'XYZ');
        tmpQ.setFromEuler(tmpE);
        bone.quaternion.copy(rest).multiply(tmpQ);
    }

    // Force skeleton update
    if (state.rigifySkeleton.rootBone) state.rigifySkeleton.rootBone.updateWorldMatrix(true, true);
    if (state.bodyMesh && state.bodyMesh.skeleton) state.bodyMesh.skeleton.update();

    console.log('[FaceExpr] Applied:', {jawOpen, smile, browUp, browDown, lipUp, lipCorner, cheekPuff, squint, noseWrinkle, eyeWide});
}

fn.applyFacialExpression = applyFacialExpression;
