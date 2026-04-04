/**
 * Result Character — Hair loading and management.
 */
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { state } from './state.js';
import { fn } from './registry.js';
import {
    sharedState,
    findHeadBoneIndex, skinifyHairGroup, applyHairColor,
} from '../character_core.js?v=1';

const ss = sharedState;
const gltfLoader = new GLTFLoader();

export function loadHair(url) {
    removeHair();
    if (!state.isSkinned || !state.rigifySkeleton || !ss.skinWeightData) return;

    gltfLoader.load(url, (gltf) => {
        let hairGroup = gltf.scene;
        const headBoneIdx = findHeadBoneIndex(ss.skinWeightData);
        if (headBoneIdx >= 0) {
            hairGroup = skinifyHairGroup(hairGroup, headBoneIdx,
                state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        }
        state.hairMesh = hairGroup;

        if (Object.keys(ss.hairColorData).length > 0) {
            const firstName = Object.keys(ss.hairColorData)[0];
            applyHairColor(state.hairMesh, firstName, ss.hairColorData);
        }
        state.scene.add(state.hairMesh);
        console.log('[result_character] Hair loaded:', url);
    }, undefined, (err) => {
        console.error('[result_character] Failed to load hair:', err);
    });
}

export function removeHair() {
    if (state.hairMesh) {
        state.scene.remove(state.hairMesh);
        state.hairMesh.traverse(child => {
            if (child.isMesh) {
                child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(m => m.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            }
        });
        state.hairMesh = null;
    }
}

fn.loadHair = loadHair;
fn.removeHair = removeHair;
