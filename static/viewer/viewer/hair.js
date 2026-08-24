/**
 * Viewer — Hair UI (loading, refit, coloring).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { ensureSkinned } from './skinning.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Hautgewichte } from '../gemeinsam/hautgewichte.js';
import { Werkstofffreigabe } from '../gemeinsam/werkstofffreigabe.js';

export async function loadHairUI() {
    try {
        const data = await Serverabruf.json('/api/character/hairstyles/');
        const select = document.getElementById('hair-style-select');
        const colorSelect = document.getElementById('hair-color-select');
        if (!select) return;

        state.hairColorData = data.colors || {};

        (data.hairstyles || []).forEach(h => {
            const opt = document.createElement('option');
            opt.value = h.url;
            opt.textContent = h.label;
            opt.dataset.name = h.name;
            select.appendChild(opt);
        });

        if (colorSelect) {
            Object.keys(state.hairColorData).forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                colorSelect.appendChild(opt);
            });
        }

        select.addEventListener('change', () => {
            if (!select.value) { removeHair(); return; }
            loadHair(select.value);
        });

        if (colorSelect) {
            colorSelect.addEventListener('change', () => {
                applyHairColor(colorSelect.value);
            });
        }
    } catch (e) {
        Protokoll.warnung('hair', 'Hair UI not available:', e);
    }
}

export function loadHair(url) {
    removeHair();
    ensureSkinned();

    state.gltfLoader.load(url, (gltf) => {
        let hairGroup = gltf.scene;

        if (state.isSkinned && state.rigifySkeleton && state.skinWeightData) {
            const headBoneIdx = _findHeadBoneIndex();
            if (headBoneIdx >= 0) {
                hairGroup = _skinifyHairGroup(hairGroup, headBoneIdx);
            }
        }

        state.hairMesh = hairGroup;
        const colorSelect = document.getElementById('hair-color-select');
        if (colorSelect && colorSelect.value) {
            applyHairColorToObject(state.hairMesh, colorSelect.value);
        }
        state.scene.add(state.hairMesh);
        Protokoll.debug('Viewer', 'Hair loaded:', url, 'skinned=' + (state.isSkinned && state.rigifySkeleton ? 'yes' : 'no'));
        fn.updateEquippedList();
    }, undefined, (err) => {
        console.error('Failed to load hair:', err);
    });
}

function _findHeadBoneIndex() {
    if (!state.skinWeightData) return -1;
    const names = state.skinWeightData.bone_names;
    for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
        const idx = names.indexOf(tryName);
        if (idx >= 0) return idx;
    }
    return -1;
}

function _skinifyHairGroup(gltfScene, headBoneIdx) {
    const meshChildren = [];
    gltfScene.traverse(child => {
        if (child.isMesh) meshChildren.push(child);
    });

    const group = new THREE.Group();
    for (const child of meshChildren) {
        const geo = child.geometry.clone();
        Hautgewichte.anEinenKnochen(geo, headBoneIdx, THREE.Float32BufferAttribute);

        const skinnedChild = new THREE.SkinnedMesh(geo, child.material);
        child.updateWorldMatrix(true, false);
        skinnedChild.applyMatrix4(child.matrixWorld);
        skinnedChild.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        group.add(skinnedChild);
    }
    return group;
}

export function removeHair() {
    if (state.hairMesh) {
        state.scene.remove(state.hairMesh);
        Werkstofffreigabe.baum(state.hairMesh);   // samt Texturen
        state.hairMesh = null;
        fn.updateEquippedList();
    }
}

export function refitHairToBody() {
    if (!state.bodyGeometry || state.initialBodyTop === null) return;
    const hairSelect = document.getElementById('hair-style-select');
    if (!hairSelect || !hairSelect.value) return;
    if (!state.hairMesh) return;

    const currentTop = fn._getBodyTop();
    if (currentTop === null || Math.abs(currentTop - state.initialBodyTop) < 0.001) return;
    const scale = currentTop / state.initialBodyTop;

    const hairUrl = hairSelect.value;
    const colorSelect = document.getElementById('hair-color-select');
    const colorName = colorSelect ? colorSelect.value : '';
    removeHair();

    state.gltfLoader.load(hairUrl, (gltf) => {
        let hairGroup = gltf.scene;

        hairGroup.traverse(child => {
            if (child.isMesh) {
                child.geometry.scale(scale, scale, scale);
            }
        });

        if (state.isSkinned && state.rigifySkeleton && state.skinWeightData) {
            const headBoneIdx = _findHeadBoneIndex();
            if (headBoneIdx >= 0) {
                hairGroup = _skinifyHairGroup(hairGroup, headBoneIdx);
            }
        }

        state.hairMesh = hairGroup;
        if (colorName) applyHairColorToObject(state.hairMesh, colorName);
        state.scene.add(state.hairMesh);
        fn.updateEquippedList();
        Protokoll.debug('Hair refit', `scale=${scale.toFixed(4)} (initial=${state.initialBodyTop.toFixed(4)}, current=${currentTop.toFixed(4)})`);
    }, undefined, (err) => {
        console.error('[Hair refit] failed to reload:', err);
    });
}

export function applyHairColor(colorName) {
    if (state.hairMesh) applyHairColorToObject(state.hairMesh, colorName);
}

export function applyHairColorToObject(obj, colorName) {
    const rgb = state.hairColorData[colorName];
    if (!rgb) return;
    const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
    obj.traverse(child => {
        if (child.isMesh && child.material) {
            const mats = Array.isArray(child.material) ? child.material : [child.material];
            mats.forEach(m => { m.color.copy(color); });
        }
    });
}

// Register
fn.loadHairUI = loadHairUI;
fn.loadHair = loadHair;
fn.removeHair = removeHair;
fn.refitHairToBody = refitHairToBody;
fn.applyHairColor = applyHairColor;
