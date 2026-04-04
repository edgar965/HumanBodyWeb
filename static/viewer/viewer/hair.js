/**
 * Viewer — Hair UI (loading, refit, coloring).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { ensureSkinned } from './skinning.js';

export async function loadHairUI() {
    try {
        const resp = await fetch('/api/character/hairstyles/');
        const data = await resp.json();
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
        console.warn('Hair UI not available:', e);
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
        console.log('Hair loaded:', url, 'skinned=' + (state.isSkinned && state.rigifySkeleton ? 'yes' : 'no'));
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
        const vCount = geo.attributes.position.count;
        const si = new Float32Array(vCount * 4);
        const sw = new Float32Array(vCount * 4);
        for (let v = 0; v < vCount; v++) {
            si[v * 4] = headBoneIdx;
            sw[v * 4] = 1.0;
        }
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(si, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));

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
        console.log(`[Hair refit] scale=${scale.toFixed(4)} (initial=${state.initialBodyTop.toFixed(4)}, current=${currentTop.toFixed(4)})`);
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
