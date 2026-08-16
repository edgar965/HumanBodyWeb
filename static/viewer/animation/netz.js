/**
 * Netz und Skelett der Animationsseite laden.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026).
 */

import * as THREE from 'three';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js?v=2';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { Seitenzustand } from './seitenzustand.js';
import { BODY_MATERIALS, applySceneSkinSettings, applySkinColor } from './material.js';


export async function loadMesh() {
    try {
        const resp = await fetch('/api/character/mesh/');
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        document.getElementById('vertex-count').textContent =
            data.vertex_count.toLocaleString();

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            const faceBuf = base64ToUint32(data.faces);
            index = new THREE.BufferAttribute(faceBuf, 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            const uvBuf = base64ToFloat32(data.uvs);
            uvAttr = new THREE.BufferAttribute(uvBuf, 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        let geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        const groups = data.groups || [];

        // Use server-computed normals (quad-topology based, no triangulation artifacts)
        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            Seitenzustand.bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            Seitenzustand.bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        Seitenzustand.bodyGeometry = geo;
        Seitenzustand.scene.add(Seitenzustand.bodyMesh);

        document.getElementById('vertex-count').textContent =
            geo.attributes.position.count.toLocaleString();

        applySceneSkinSettings();
        applySkinColor();
        Seitenzustand.groesseAnpassen();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

export async function loadRigifySkeleton() {
    try {
        const resp = await fetch('/api/character/rigify-skeleton/');
        if (resp.ok) {
            Seitenzustand.rigifySkeletonData = await resp.json();
            console.log(`DEF skeleton loaded: ${Seitenzustand.rigifySkeletonData.bone_count} bones`);
        }
    } catch (e) {
        console.warn('DEF skeleton not available:', e);
    }
}

export async function loadSkinWeights() {
    try {
        const resp = await fetch('/api/character/skin-weights/');
        if (resp.ok) Seitenzustand.skinWeightData = await resp.json();
    } catch (e) {
        console.warn('Skin weights not available:', e);
    }
}

export function convertToRigifySkinnedMesh(rigifySkel, swData) {
    if (Seitenzustand.isSkinned || !Seitenzustand.bodyMesh || !Seitenzustand.bodyGeometry) return;

    Seitenzustand.bodyGeometry = Seitenzustand.bodyGeometry.clone();

    const vCount = Seitenzustand.bodyGeometry.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);

    for (let v = 0; v < vCount; v++) {
        const infs = swData.weights[v] || [];
        const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
        let sum = sorted.reduce((s, e) => s + e[1], 0);
        if (sum < 1e-6) sum = 1;
        for (let i = 0; i < 4; i++) {
            skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
            skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
        }
    }

    Seitenzustand.bodyGeometry.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
    Seitenzustand.bodyGeometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

    Seitenzustand.rigifySkeleton = buildRigifySkeleton(Seitenzustand.rigifySkeletonData, swData);

    const mat = Seitenzustand.bodyMesh.material;
    const pos = Seitenzustand.bodyMesh.position.clone();
    const vis = Seitenzustand.bodyMesh.visible;
    Seitenzustand.scene.remove(Seitenzustand.bodyMesh);

    Seitenzustand.bodyMesh = new THREE.SkinnedMesh(Seitenzustand.bodyGeometry, mat);
    Seitenzustand.bodyMesh.position.copy(pos);
    Seitenzustand.bodyMesh.visible = vis;
    Seitenzustand.bodyMesh.add(Seitenzustand.rigifySkeleton.rootBone);
    Seitenzustand.bodyMesh.bind(Seitenzustand.rigifySkeleton.skeleton);
    Seitenzustand.scene.add(Seitenzustand.bodyMesh);
    Seitenzustand.isSkinned = true;
    console.log('SkinnedMesh created:', Seitenzustand.bodyMesh.isSkinnedMesh, 'bones:', Seitenzustand.rigifySkeleton.skeleton.bones.length);
}

// =========================================================================
// BVH animation playback
// =========================================================================
// Skeleton wrapper for scaling
export let skelWrapper = null;
