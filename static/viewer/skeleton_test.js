/**
 * Skeleton Test — 6 Testzustand.skeletons for bone-mapping debugging.
 *
 * Row 1: DEF (red) | CMU (green) | Mixamo (orange) | MocapNET (blue) | Bandai (purple)
 * Row 2: SMPL (orange-red, behind DEF)
 */
import * as THREE from 'three';
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

    rootBone.updateWorldMatrix(true, true);

    // Measure height and scale to ~1.68m
    const box = new THREE.Box3();
    const tmpVec = new THREE.Vector3();
    bones.forEach(b => { b.getWorldPosition(tmpVec); box.expandByPoint(tmpVec); });
    const bvhHeight = Math.max(box.max.y - box.min.y, 0.01);
    const targetH = 1.68;
    const scale = targetH / bvhHeight;

    // Wrapper group for scaling + centering
    const center = new THREE.Vector3();
    box.getCenter(center);
    const wrapper = new THREE.Group();
    wrapper.scale.set(scale, scale, scale);
    // Center skeleton horizontally and put feet on ground
    wrapper.position.set(-center.x * scale, -box.min.y * scale, -center.z * scale);
    wrapper.add(rootBone);
    skel.group.add(wrapper);
    skel.wrapper = wrapper;
    skel.rootBone = rootBone;
    skel.bones = bones;

    // Bone cylinders + joints — invScale compensates wrapper so sizes match DEF
    createBoneViz(bones, skelKey, 1 / scale);

    // Bone number labels
    createBoneLabels(bones, skelKey);

    Protokoll.debug('Viewer',
        `${skelKey.toUpperCase()} skeleton placed: ${bones.length} bones, `
        + `scale=${scale.toFixed(4)}, bvhH=${bvhHeight.toFixed(1)}, `
        + `box.y=[${box.min.y.toFixed(1)},${box.max.y.toFixed(1)}], `
        + `center.z=${center.z.toFixed(1)}, `
        + `wrapper.z=${wrapper.position.z.toFixed(3)}`);
}






// =========================================================================
// Boot
// =========================================================================
// `.catch`: Ein Fehler im Aufbau darf nicht als stille Rejection enden —
// die Seite waere leer, ohne dass jemand den Grund sieht.
init().catch(fehler => {
    console.error('[Skelett-Test] Aufbau gescheitert:', fehler);
});
