/**
 * Charakter einer Spur laden — Netz, Skelett, Zubehoer der Voreinstellung.
 *
 * Aus tracks.js herausgeloest (Umbau 15.08.2026): zwei Funktionen mit je 113
 * Zeilen, die Netzdaten holen, ein SkinnedMesh bauen und Haare, Kleidung und
 * Zubehoer nachladen.
 */

import * as THREE from 'three';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js?v=2';

import { sharedState } from '../character_core.js?v=1';
import { _sanitizeBoneNames } from './spur_clips.js';
import { applySkinColorToMaterials, computeSkinAttributes } from '../character_core.js?v=1';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { BODY_MATERIALS } from '../character_core.js?v=1';
import { generateRigBoneMesh } from '../modellbau/rignetz.js';
const ss = sharedState;


export async function _loadPresetAccessories(track, modelData) {
    // Garments laden
    for (const g of (modelData.garments || [])) {
        try {
            const params = new URLSearchParams({
                garment_id: g.id,
                body_type: track.bodyType || 'Female_Caucasian',
                offset: g.offset || 0,
                stiffness: g.stiffness || 0.5,
                min_dist: g.minDist || 0,
                crotch_floor: g.crotchFloor || 0,
                lift: g.lift || 0,
                crotch_depth: g.crotchDepth || 0,
            });
            // Morphs aus dem Preset übergeben
            if (modelData.morphs) {
                for (const [k, v] of Object.entries(modelData.morphs)) {
                    params.append(`morph_${k}`, v);
                }
            }
            if (modelData.meta) {
                for (const [k, v] of Object.entries(modelData.meta)) {
                    params.append(`meta_${k}`, v);
                }
            }
            const resp = await fetch(`/api/character/garment/fit/?${params}`);
            const data = await resp.json();
            if (data.error) { console.warn(`[BVH Studio] Garment ${g.id} failed:`, data.error); continue; }

            const vertBuf = base64ToFloat32(data.vertices);
            blenderToThreeCoords(vertBuf);
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
            if (data.faces) geo.setIndex(new THREE.BufferAttribute(base64ToUint32(data.faces), 1));
            if (data.normals) {
                const nb = base64ToFloat32(data.normals);
                blenderToThreeCoords(nb);
                geo.setAttribute('normal', new THREE.BufferAttribute(nb, 3));
            } else {
                geo.computeVertexNormals();
            }

            const color = g.color || [0.5, 0.5, 0.5];
            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color(color[0], color[1], color[2]),
                roughness: g.roughness ?? 0.7,
                metalness: g.metalness ?? 0.0,
                side: THREE.DoubleSide,
            });

            // Skinning
            if (data.skin_indices && data.skin_weights && track.skeleton) {
                const siBuf = base64ToFloat32(data.skin_indices);
                const swBuf = base64ToFloat32(data.skin_weights);
                geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
                geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
                const skinnedGarment = new THREE.SkinnedMesh(geo, mat);
                skinnedGarment.bind(track.skeleton.skeleton, track.mesh.bindMatrix);
                track.group.add(skinnedGarment);
            } else {
                track.group.add(new THREE.Mesh(geo, mat));
            }
            console.log(`[BVH Studio] Garment loaded: ${g.id}`);
        } catch (e) {
            console.warn(`[BVH Studio] Garment ${g.id} error:`, e);
        }
    }

    // Hair laden
    if (modelData.hair_style?.url) {
        try {
            const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
            const loader = new GLTFLoader();
            const hairUrl = modelData.hair_style.url;
            const gltf = await new Promise((resolve, reject) => loader.load(hairUrl, resolve, undefined, reject));
            const hairGroup = new THREE.Group();

            // Alle Meshes im GLTF an Head-Bone binden
            const headBoneIdx = track.skeleton?.skeleton?.bones.findIndex(b => b.name.includes('spine_006')) ?? -1;
            gltf.scene.traverse(child => {
                if (!child.isMesh) return;
                const geo = child.geometry.clone();

                // Hair-Farbe
                const colorName = modelData.hair_style.color || 'Silken Black';
                const hairColor = ss.hairColorData?.[colorName] || [0.02, 0.02, 0.02];
                const mat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color(hairColor[0], hairColor[1], hairColor[2]),
                    roughness: 0.6, metalness: 0.1, side: THREE.DoubleSide,
                });

                if (headBoneIdx >= 0 && track.skeleton) {
                    // Alle Vertices an Head-Bone pinnen
                    const vCount = geo.attributes.position.count;
                    const si = new Float32Array(vCount * 4);
                    const sw = new Float32Array(vCount * 4);
                    for (let v = 0; v < vCount; v++) { si[v * 4] = headBoneIdx; sw[v * 4] = 1.0; }
                    geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(si, 4));
                    geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
                    const skinnedHair = new THREE.SkinnedMesh(geo, mat);
                    skinnedHair.bind(track.skeleton.skeleton, track.mesh.bindMatrix);
                    hairGroup.add(skinnedHair);
                } else {
                    hairGroup.add(new THREE.Mesh(geo, mat));
                }
            });
            track.group.add(hairGroup);
            console.log(`[BVH Studio] Hair loaded: ${modelData.hair_style.name || hairUrl}`);
        } catch (e) {
            console.warn('[BVH Studio] Hair load error:', e);
        }
    }
}

export async function loadTrackCharacter(track) {
    try {
        const modelResp = await fetch(`/api/character/model/${encodeURIComponent(track.preset)}/`);
        const modelData = await modelResp.json();
        track.modelData = modelData;  // cached so Export1 can read bone_parts

        let newMesh = null;

        // Generated model (Rig1-4): Bone-Mesh aus modellbau/rignetz.js
        if (modelData.type === 'generated_model') {
            let rigBonesData = null;
            try {
                const rigResp = await fetch('/api/character/rig/');
                if (rigResp.ok) rigBonesData = await rigResp.json();
            } catch (e) {}

            if (rigBonesData && ss.rigifySkeletonData && ss.skinWeightData) {
                const result = generateRigBoneMesh(rigBonesData, modelData, ss.rigifySkeletonData, ss.skinWeightData);
                if (result?.mesh) {
                    newMesh = result.mesh;
                    if (result.skeleton) {
                        track.skeleton = result.skeleton;
                        _sanitizeBoneNames(track.skeleton);
                    }
                }
            }
        }

        // Standard-Mesh (FemaleGarment etc.): SkinnedMesh mit Skin-Weights.
        // Morphs + Meta-Params aus dem Preset an die Mesh-API weiterreichen,
        // sonst kommt immer das Standard-Mesh zurück (Bug: FrauHaarDünn sah aus
        // wie das Default-Modell weil morphs nicht angewendet wurden).
        if (!newMesh) {
            // Preset kann einen abweichenden bodyType haben (z.B. Female_Asian) —
            // dann überschreibt der Preset den Track-Default.
            const effectiveBodyType = modelData.body_type || track.bodyType;
            track.bodyType = effectiveBodyType;
            const params = new URLSearchParams();
            params.set('body_type', effectiveBodyType);
            const morphs = modelData.morphs || {};
            for (const [k, v] of Object.entries(morphs)) {
                if (v !== 0) params.set(`morph_${k}`, v);
            }
            const meta = modelData.meta || {};
            for (const [k, v] of Object.entries(meta)) {
                if (v !== 0) params.set(`meta_${k}`, v);
            }
            const resp = await fetch(`/api/character/mesh/?${params}`);
            const data = await resp.json();
            if (data.error) return;

            const vertBuf = base64ToFloat32(data.vertices);
            blenderToThreeCoords(vertBuf);
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
            if (data.faces) geo.setIndex(new THREE.BufferAttribute(base64ToUint32(data.faces), 1));
            if (data.normals) {
                const nb = base64ToFloat32(data.normals);
                blenderToThreeCoords(nb);
                geo.setAttribute('normal', new THREE.BufferAttribute(nb, 3));
            } else {
                geo.computeVertexNormals();
            }

            const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
                color: d.color, roughness: d.roughness, metalness: d.metalness,
                side: THREE.DoubleSide, transparent: d.transparent || false,
                opacity: d.opacity !== undefined ? d.opacity : 1.0,
            }));
            applySkinColorToMaterials(materials, track.bodyType, ss.skinColors);

            const groups = data.groups || [];
            if (groups.length > 0) {
                for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
                newMesh = new THREE.Mesh(geo, materials);
            } else {
                newMesh = new THREE.Mesh(geo, materials[0]);
            }

            const { skinIndices, skinWeights } = computeSkinAttributes(geo, ss.skinWeightData);
            geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

            track.skeleton = buildRigifySkeleton(ss.rigifySkeletonData, ss.skinWeightData);
            _sanitizeBoneNames(track.skeleton);
            const skinnedMesh = new THREE.SkinnedMesh(geo, newMesh.material);
            skinnedMesh.add(track.skeleton.rootBone);
            skinnedMesh.bind(track.skeleton.skeleton);
            newMesh = skinnedMesh;
        }

        // Vorherige Meshes aus Group entfernen (nicht disposen — könnten gecacht sein)
        while (track.group.children.length > 0) track.group.remove(track.group.children[0]);
        track.mesh = newMesh;
        // Mesh selbst immer visible — die track.group.visible wird von
        // applyModelTrack/applyBvhTrack gesteuert (deckt Mesh + Garments + Hair ab).
        track.mesh.visible = true;
        track.group.add(newMesh);
        track.mixer = new THREE.AnimationMixer(newMesh);
        track._activeClip = null;
        track._activeAction = null;

        // Garments und Hair aus Preset laden (falls vorhanden)
        if (modelData.garments || modelData.hair_style) {
            await _loadPresetAccessories(track, modelData);
        }

        console.log(`[BVH Studio] Character loaded: ${track.preset} for ${track.name}`);

    } catch (e) {
        console.error('[BVH Studio] Character load failed:', e);
    }
}
