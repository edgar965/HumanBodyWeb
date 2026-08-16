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
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


export async function loadMesh() {
    try {
        const data = await Serverabruf.json('/api/character/mesh/');
        if (data.error) { Protokoll.fehler('Netz', data.error); return; }

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
        Protokoll.fehler('Netz', 'nicht ladbar:', e);
    }
}

export async function loadRigifySkeleton() {
    // `jsonOderNull`: Ohne Skelett laeuft die Seite weiter (kein Skinning),
    // deshalb warnen statt werfen — wie die frueheren `if (resp.ok)`-Zweige.
    const daten = await Serverabruf.jsonOderNull('/api/character/rigify-skeleton/');
    if (!daten) return;
    Seitenzustand.rigifySkeletonData = daten;
    Protokoll.debug('Skelett', `DEF-Skelett geladen: ${daten.bone_count} Knochen`);
}

export async function loadSkinWeights() {
    const daten = await Serverabruf.jsonOderNull('/api/character/skin-weights/');
    if (daten) Seitenzustand.skinWeightData = daten;
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
    Protokoll.debug('Netz', 'SkinnedMesh gebaut,',
                    Seitenzustand.rigifySkeleton.skeleton.bones.length, 'Knochen');
}

// Die Skalierungsgruppe des BVH-Skeletts liegt jetzt im Seitenzustand
// (`Seitenzustand.skelWrapper`) — hier war sie ein `export let`, auf das
// wiedergabe.js schrieb: ein TypeError zur Laufzeit (Umbau 16.08.2026).
