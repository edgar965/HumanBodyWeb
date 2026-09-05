/**
 * Skeleton Test — die Skelettspalten der Vergleichsseite (`testzustand.js`).
 *
 * Reihe 1: DEF (rot) | CMU (grün) | Mixamo (orange) | MocapNET (blau) | Bandai (lila) | OpenPose
 * Reihe 2: SMPL (gelb, hinter DEF) | UMA (rosa, hinter CMU)
 */
import 'three/addons/controls/OrbitControls.js';
import 'three/addons/loaders/BVHLoader.js';
import 'three/addons/renderers/CSS2DRenderer.js';
import './retarget_hybrid.js';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js';
import './animation/wiedergabe.js';
import './animation/baum.js';
import { Testzustand } from './skelett_test/testzustand.js';
import { createBoneLabels, createBoneViz } from './skelett_test/knochenbild.js';
import { init } from './skelett_test/aufbau.js';
import { Protokoll } from './gemeinsam/protokoll.js';
import { Anfangshaltung } from './anfangshaltung.js';
import { Einpassung } from './skelett_test/einpassung.js';

// =========================================================================
// Global state
// =========================================================================


// Animation

// DEF skeleton data from API

// All animations list (for auto-loading first of each type)

// Five skeleton groups



// Retarget via server-side API (retarget_hybrid.js)

// =========================================================================
// buildRigifySkeleton() imported from rigify_skeleton_builder.js








// =========================================================================
// DEF Skeleton (left, red)
// =========================================================================
export async function loadRigifySkeleton() {
    try {
        const [skelResp, swResp] = await Promise.all([
            fetch('/api/character/rigify-skeleton/'),
            fetch('/api/character/skin-weights/')
        ]);

        if (!skelResp.ok || !swResp.ok) {
            Protokoll.warnung('skeleton_test', 'DEF skeleton or skin weights not available');
            return;
        }

        Testzustand.rigifySkeletonData = await skelResp.json();
        Testzustand.skinWeightData = await swResp.json();

        const rigifySkel = buildRigifySkeleton(Testzustand.rigifySkeletonData, Testzustand.skinWeightData);
        Testzustand.skeletons.def.rootBone = rigifySkel.rootBone;
        Testzustand.skeletons.def.boneByName = rigifySkel.boneByName;
        Testzustand.skeletons.def.skeleton = rigifySkel;
        Testzustand.skeletons.def.bones = rigifySkel.bones;
        Testzustand.skeletons.def.group.add(rigifySkel.rootBone);

        // Bone cylinders + joints (white)
        createBoneViz(rigifySkel.bones, 'def');

        // Bone number labels
        createBoneLabels(rigifySkel.bones, 'def');

        Protokoll.debug('Viewer', `DEF skeleton loaded: ${rigifySkel.bones.length} bones`);
    } catch (e) {
        console.error('Failed to load DEF skeleton:', e);
    }
}

// =========================================================================
// BVH Skeleton helper — load and place a BVH as a rest-pose skeleton
// =========================================================================
export function placeBvhSkeleton(result, skelKey) {
    const skel = Testzustand.skeletons[skelKey];
    const bones = result.skeleton.bones;
    if (bones.length === 0) return;

    const rootBone = bones[0];

    // Bild 0 auf die Knochen legen — ohne das sitzt die Zentrierung daneben.
    // Was dabei je Format zu tun ist, steht in `anfangshaltung.js`.
    new Anfangshaltung(bones, result.clip).anwenden(skelKey, rootBone);

    // Auf Vergleichsgröße bringen, mittig, Füße am Boden (`einpassung.js`).
    const einpassung = new Einpassung(rootBone, bones);
    const scale = einpassung.anwenden(skelKey);
    skel.rootBone = rootBone;
    skel.bones = bones;

    // Bone cylinders + joints — invScale compensates wrapper so sizes match DEF
    createBoneViz(bones, skelKey, 1 / scale);

    // Bone number labels
    createBoneLabels(bones, skelKey);

    Protokoll.debug('Viewer',
        `${skelKey.toUpperCase()} skeleton placed: ${bones.length} bones, `
        + einpassung.beschreibung());
}






// =========================================================================
// Boot
// =========================================================================
// `.catch`: Ein Fehler im Aufbau darf nicht als stille Rejection enden —
// die Seite waere leer, ohne dass jemand den Grund sieht.
init().catch(fehler => {
    console.error('[Skelett-Test] Aufbau gescheitert:', fehler);
});
