/**
 * Kleidungsstueck in zwei Stufen an den Koerper anpassen.
 *
 * Aus kleider.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _applyGarmentRegionOffsets, _computeGarmentRegionWeights } from './kleidung_anpassen.js';
import { _charQueryParams, _selectedInst, _sliderVal } from './utils.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { generateModelMesh } from './state.js';


async function _doKleiderStage1() {
    // Load the configured bone model (from Settings -> Szene -> Kleider)
    // and display it as the "kld_hull" submesh
    const inst = _selectedInst();
    if (!inst) return;

    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }

    // Get bone model name from settings
    let boneModelName = 'Rig1';
    try {
        const settingsResp = await fetch('/api/settings/humanbody/');
        const settings = await settingsResp.json();
        boneModelName = settings.ui_prefs?.kleider_bone_model || 'Rig1';
    } catch(e) {}

    // Load the model preset
    let preset;
    try {
        const resp = await fetch(`/api/character/model/${encodeURIComponent(boneModelName)}/`);
        preset = await resp.json();
    } catch(e) {
        console.error('Stage 1: Failed to load bone model preset:', boneModelName, e);
        return;
    }

    // Generate the mesh using model_generator
    const config = preset;
    const radiusMul = parseFloat(document.getElementById('kleider-bone-radius')?.value || '1.3');
    if (config.bone_parts) {
        for (const part of Object.values(config.bone_parts)) {
            if (part.visible) {
                part.radius = (part.radius || 0.03) * radiusMul;
            }
        }
    }

    let result;
    if (config.skeleton_type === 'rig' || preset.type === 'generated_model') {
        const { generateRigBoneMesh: genRigMesh } = await import('../model_generator.js');
        let rigData = null;
        try {
            const r = await fetch('/api/character/rig/');
            rigData = await r.json();
        } catch(e) {}
        result = genRigMesh(rigData, config, state.rigifySkeletonData, state.skinWeightData);
    } else {
        result = generateModelMesh(state.rigifySkeletonData, state.skinWeightData, config);
    }

    if (!result || !result.mesh) {
        console.warn('Stage 1: Failed to generate bone model from preset:', boneModelName);
        return;
    }

    const key = 'kld_hull';

    // Remove old hull if exists
    if (inst.clothMeshes[key]) {
        inst.group.remove(inst.clothMeshes[key]);
        inst.clothMeshes[key].geometry.dispose();
        inst.clothMeshes[key].material.dispose();
        delete inst.clothMeshes[key];
    }

    // Extract vertices in Three.js coords and convert to Blender for server
    const posAttr = result.mesh.geometry.getAttribute('position');
    const threeVerts = new Float32Array(posAttr.array);

    // Store Blender-coords version for server (Three->Blender: x,y,z -> x,-z,y)
    state._kleiderHullVertices = new Float32Array(threeVerts.length);
    for (let i = 0; i < threeVerts.length; i += 3) {
        state._kleiderHullVertices[i]     = threeVerts[i];      // X
        state._kleiderHullVertices[i + 1] = -threeVerts[i + 2]; // -Z -> Y
        state._kleiderHullVertices[i + 2] = threeVerts[i + 1];  // Y -> Z
    }

    // Display the generated mesh (semi-transparent)
    const mat = new THREE.MeshStandardMaterial({
        color: 0x44aaff, roughness: 0.5, metalness: 0.1,
        transparent: true, opacity: 0.5, side: THREE.DoubleSide,
    });
    const mesh = result.mesh;
    mesh.material = mat;

    // Apply current pose (T-pose etc.) to hull's own skeleton
    if (mesh.isSkinnedMesh && mesh.skeleton && inst.bodyMesh?.isSkinnedMesh && inst.bodyMesh.skeleton) {
        const bodySkel = inst.bodyMesh.skeleton;
        const hullSkel = mesh.skeleton;
        let copied = 0;
        for (const hullBone of hullSkel.bones) {
            const bodyBone = bodySkel.getBoneByName(hullBone.name);
            if (bodyBone) {
                hullBone.quaternion.copy(bodyBone.quaternion);
                copied++;
            }
        }
        const hullRoot = hullSkel.bones.find(b => !b.parent || b.parent === mesh);
        if (hullRoot) hullRoot.updateWorldMatrix(true, true);
        console.log(`[Hull] Copied ${copied} bone quaternions from body pose`);
    }

    inst.clothMeshes[key] = mesh;
    inst.group.add(mesh);

    console.log(`Stage 1: Bone model '${boneModelName}' loaded (${posAttr.count} verts)`);
    fn.updateEquippedList(inst);
    fn.updateVertexCount();
}

async function _doKleiderFit(fitMode) {
    if (!state._selectedKleiderId) return;
    const inst = _selectedInst();
    if (!inst) return;

    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }

    state._refitting = true;

    const params = _charQueryParams(inst);
    params.set('garment_id', state._selectedKleiderId);
    params.set('offset', (_sliderVal('kleider-offset') / 1000).toFixed(4));
    params.set('stiffness', (_sliderVal('kleider-stiffness') / 100).toFixed(2));
    params.set('min_dist', _sliderVal('kleider-min-dist'));
    params.set('crotch_floor', _sliderVal('kleider-crotch-floor'));
    params.set('lift', _sliderVal('kleider-lift'));
    params.set('crotch_depth', _sliderVal('kleider-crotch-depth'));
    params.set('fit_mode', fitMode || 'rig_hull');

    const colorHex = document.getElementById('kleider-color')?.value || '#4d5980';
    const c = new THREE.Color(colorHex);
    params.set('color_r', c.r.toFixed(3));
    params.set('color_g', c.g.toFixed(3));
    params.set('color_b', c.b.toFixed(3));

    try {
        let resp;
        if (fitMode === 'rig_hull' && state._kleiderHullVertices) {
            // Stage 2: Send hull vertices to server via POST
            const hullB64 = btoa(String.fromCharCode(...new Uint8Array(state._kleiderHullVertices.buffer)));
            resp = await fetch(`/api/character/garment/fit/?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hull_vertices: hullB64 }),
            });
        } else {
            resp = await fetch(`/api/character/garment/fit/?${params}`);
        }
        const data = await resp.json();
        if (data.error) { console.warn('Kleider fit error:', data.error); state._refitting = false; return; }

        const key = `kld_${state._selectedKleiderId}`;

        if (inst.clothMeshes[key]) {
            inst.group.remove(inst.clothMeshes[key]);
            inst.clothMeshes[key].geometry.dispose();
            inst.clothMeshes[key].material.dispose();
            delete inst.clothMeshes[key];
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        const roughness = _sliderVal('kleider-roughness') / 100;
        const metalness = _sliderVal('kleider-metalness') / 100;
        const mat = new THREE.MeshStandardMaterial({
            color: c, roughness, metalness, side: THREE.DoubleSide,
        });

        const mesh = _skinifyMesh(geo, mat, inst, data);
        inst.clothMeshes[key] = mesh;
        inst.group.add(mesh);

        inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
        _computeGarmentRegionWeights(inst, key);

        const prevSt = inst.garmentState[key];
        inst.garmentState[key] = {
            offset: _sliderVal('kleider-offset') / 1000,
            stiffness: _sliderVal('kleider-stiffness') / 100,
            minDist: _sliderVal('kleider-min-dist'),
            crotchFloor: _sliderVal('kleider-crotch-floor'),
            lift: _sliderVal('kleider-lift'),
            crotchDepth: _sliderVal('kleider-crotch-depth'),
            color: [c.r, c.g, c.b],
            roughness, metalness,
            regionTop: prevSt?.regionTop || 0,
            regionUpper: prevSt?.regionUpper || 0,
            regionMid: prevSt?.regionMid || 0,
            regionLower: prevSt?.regionLower || 0,
            regionBottom: prevSt?.regionBottom || 0,
        };

        _applyGarmentRegionOffsets(inst, key);

        state._refitting = false;
        fn.updateEquippedList(inst);
        fn.updateVertexCount();
    } catch (e) {
        state._refitting = false;
        console.error('Kleider fit failed:', e);
    }
}

export { _doKleiderStage1, _doKleiderFit };
