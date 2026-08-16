/**
 * Charakterkoerper — Koerpernetz neu berechnen, aus einer Modellkonfiguration
 * bauen, Hautfarbe setzen.
 *
 * Aus character.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { base64ToFloat32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { generateModelMesh, generateRigBoneMesh } from './state.js';
import { Modellbauzustand } from './modellgenerator/zustand.js';

export class Charakterkoerper {

    static async neuLaden(inst) {
        const params = new URLSearchParams();
        params.set('body_type', inst.bodyType);
        for (const [k, v] of Object.entries(inst.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(inst.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        const resp = await fetch(`/api/character/mesh/?${params}`);
        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        if (inst.bodyMesh && inst.bodyMesh.geometry.attributes.position.count === vertBuf.length / 3) {
            inst.bodyMesh.geometry.attributes.position.array.set(vertBuf);
            inst.bodyMesh.geometry.attributes.position.needsUpdate = true;

            if (data.normals) {
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);
                if (inst.bodyMesh.geometry.attributes.normal) {
                    inst.bodyMesh.geometry.attributes.normal.array.set(normalBuf);
                    inst.bodyMesh.geometry.attributes.normal.needsUpdate = true;
                }
            } else {
                inst.bodyMesh.geometry.computeVertexNormals();
            }

            inst.bodyMesh.geometry.computeBoundingSphere();
            inst.bodyMesh.geometry.computeBoundingBox();
        } else {
            if (inst.bodyMesh) {
                inst.group.remove(inst.bodyMesh);
                inst.bodyMesh.geometry.dispose();
                const mats = Array.isArray(inst.bodyMesh.material)
                    ? inst.bodyMesh.material : [inst.bodyMesh.material];
                mats.forEach(m => m.dispose());
                inst.bodyMesh = null;
            }
            await inst.load();
        }
    }

    static async ausKonfiguration(inst) {
        const skelType = inst.generatedConfig.skeleton_type || 'def';
        let result;

        if (skelType === 'rig') {
            await Modellbauzustand.rigKnochenLaden();
            if (!Modellbauzustand.rigKnochen) {
                throw new Error('Rig bones data not loaded');
            }
            result = generateRigBoneMesh(Modellbauzustand.rigKnochen, inst.generatedConfig, state.rigifySkeletonData, state.skinWeightData);
            if (result.skeleton) {
                inst.rigifySkeleton = result.skeleton;
                inst.isSkinned = true;
            }
        } else {
            if (!state.rigifySkeletonData || !state.skinWeightData) {
                throw new Error('Skeleton data not loaded');
            }
            result = generateModelMesh(state.rigifySkeletonData, state.skinWeightData, inst.generatedConfig);
            if (result.skeleton) {
                inst.rigifySkeleton = result.skeleton;
                inst.isSkinned = true;
            }
        }

        if (!result) throw new Error('No visible bones in generated model config');

        inst.bodyMesh = result.mesh;
        inst.group.add(inst.bodyMesh);
        return inst;
    }

    static hautfarbe(inst, materials) {
        if (!Object.keys(state.skinColors).length) return;
        const parts = inst.bodyType.split('_');
        const ethnicity = parts.length > 1 ? parts.slice(1).join('_') : 'Caucasian';
        const colors = state.skinColors[ethnicity] || state.skinColors['Caucasian'];
        if (colors && materials[0]) {
            materials[0].color.setRGB(
                Math.pow(colors[0], 1/2.2),
                Math.pow(colors[1], 1/2.2),
                Math.pow(colors[2], 1/2.2)
            );
            if (materials[1]) {
                materials[1].color.copy(materials[0].color);
            }
        }
    }
}
