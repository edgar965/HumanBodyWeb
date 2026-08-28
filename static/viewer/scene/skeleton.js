/**
 * Scene Editor -- Skeleton/Skinning helpers.
 * DEF Skeleton + Skin Weights + BVH skinning utilities.
 */
import { THREE, buildRigifySkeleton } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { base64ToFloat32 } from './utils.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';
import { Hautgewichte } from '../gemeinsam/hautgewichte.js';
import { skinifyHairGroup } from '../character_core.js';

export async function loadRigifySkeleton() {
    try {
        const resp = await fetch('/api/character/rigify-skeleton/');
        if (resp.ok) state.rigifySkeletonData = await resp.json();
    } catch (e) { Protokoll.debug('skelett', 'Rigify-Skelett nicht abrufbar', e); }
}

export async function loadSkinWeights() {
    try {
        const resp = await fetch('/api/character/skin-weights/');
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) { Protokoll.debug('skelett', 'Hautgewichte nicht abrufbar', e); }
}

export function convertToRigifySkinnedMesh() {
    if (state.isSkinned || !state.bodyMesh || !state.bodyGeometry || !state.skinWeightData) return;
    state.bodyGeometry = state.bodyGeometry.clone();
    Hautgewichte.anGeometrie(state.bodyGeometry, state.skinWeightData, THREE.Float32BufferAttribute);
    state.rigifySkeleton = buildRigifySkeleton(state.rigifySkeletonData, state.skinWeightData);
    const mat = state.bodyMesh.material;
    const pos = state.bodyMesh.position.clone();
    const vis = state.bodyMesh.visible;
    state.scene.remove(state.bodyMesh);
    state.bodyMesh = new THREE.SkinnedMesh(state.bodyGeometry, mat);
    state.bodyMesh.position.copy(pos);
    state.bodyMesh.visible = vis;
    state.bodyMesh.add(state.rigifySkeleton.rootBone);
    state.bodyMesh.bind(state.rigifySkeleton.skeleton);
    state.scene.add(state.bodyMesh);
    state.isSkinned = true;
}

/** Convert a CharacterInstance body to SkinnedMesh for animation. */
export function convertInstToSkinned(inst) {
    if (inst.isSkinned || !inst.bodyMesh || !state.skinWeightData || !state.rigifySkeletonData) return;
    if (inst.generatedConfig) return;
    const geo = inst.bodyMesh.geometry.clone();
    Hautgewichte.anGeometrie(geo, state.skinWeightData, THREE.Float32BufferAttribute);
    inst.rigifySkeleton = buildRigifySkeleton(state.rigifySkeletonData, state.skinWeightData);
    const mat = inst.bodyMesh.material;
    const vis = inst.bodyMesh.visible;
    inst.group.remove(inst.bodyMesh);
    inst.bodyMesh = new THREE.SkinnedMesh(geo, mat);
    inst.bodyMesh.visible = vis;
    inst.bodyMesh.add(inst.rigifySkeleton.rootBone);
    inst.bodyMesh.bind(inst.rigifySkeleton.skeleton);
    inst.group.add(inst.bodyMesh);
    inst.isSkinned = true;

    // FEHLER bis 16.08.2026: Hier stand `inst._loadHair()` — eine Methode, die
    // `CharacterInstance` nicht (mehr) hat; das Laden der Haare wurde beim
    // Umbau am 16.08. nach `Charakterzubehoer.haare()` verschoben. Der Aufruf
    // warf "inst._loadHair is not a function" und brach damit ALLES ab, was
    // `convertInstToSkinned` sonst noch anstößt — unter anderem die erste Stufe
    // der Kleideranpassung. Zweiter Fall desselben Musters nach
    // `inst.reloadBody()` in properties.js.
    if (inst.hairMesh) {
        inst.group.remove(inst.hairMesh);
        fn.charakterHaare?.(inst);
    }
}

/**
 * Create SkinnedMesh (if skin data available) or plain Mesh.
 */
export function _skinifyMesh(geo, mat, inst, data) {
    if (inst.isSkinned && inst.rigifySkeleton && data.skin_indices && data.skin_weights) {
        const siBuf = base64ToFloat32(data.skin_indices);
        const swBuf = base64ToFloat32(data.skin_weights);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
        const mesh = new THREE.SkinnedMesh(geo, mat);
        mesh.bind(inst.rigifySkeleton.skeleton, inst.bodyMesh.bindMatrix);
        return mesh;
    }
    return new THREE.Mesh(geo, mat);
}

/** Find the head bone index in skinWeightData.bone_names. */
export function _findHeadBoneIndex() {
    if (!state.skinWeightData) return -1;
    const names = state.skinWeightData.bone_names;
    for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
        const idx = names.indexOf(tryName);
        if (idx >= 0) return idx;
    }
    return -1;
}

/**
 * Haare einer GLTF-Szene an den Kopfknochen dieser FIGUR binden.
 *
 * Die Rechnung steht in `character_core.skinifyHairGroup` (Umbau 28.08.2026,
 * Befund `doppelcode`): Hier stand sie ein zweites Mal, in `viewer/hair.js`
 * ein drittes. Die drei unterschieden sich NUR darin, woher Skelett und
 * Bindematrix kommen — hier aus der Figur, dort aus dem Seitenzustand. Genau
 * das gehoert an die Aufrufstelle.
 */
export function _skinifyHairGroup(gltfScene, inst) {
    const headBoneIdx = _findHeadBoneIndex();
    if (headBoneIdx < 0 || !inst.isSkinned || !inst.rigifySkeleton) return gltfScene;
    return skinifyHairGroup(gltfScene, headBoneIdx,
                            inst.rigifySkeleton.skeleton,
                            inst.bodyMesh.bindMatrix);
}

// Register
fn.loadRigifySkeleton = loadRigifySkeleton;
fn.loadSkinWeights = loadSkinWeights;
fn.convertToRigifySkinnedMesh = convertToRigifySkinnedMesh;
fn.convertInstToSkinned = convertInstToSkinned;
fn._skinifyMesh = _skinifyMesh;
fn._skinifyHairGroup = _skinifyHairGroup;
