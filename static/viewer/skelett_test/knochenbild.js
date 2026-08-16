/**
 * Knochen sichtbar machen: Kugeln, Zylinder, Beschriftungen.
 *
 * Aus skeleton_test.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { Testzustand } from './testzustand.js';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


// Shared materials for bone visualization
const JOINT_MAT = new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false });

const BONE_MAT  = new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false });

// Base sizes (at scale=1)
const JOINT_RADIUS = 0.008;

const CYL_RADIUS_TOP = 0.003;

const CYL_RADIUS_BOT = 0.004;

// =========================================================================
// Bone Visualization — white cylinders + joint spheres
// =========================================================================
export function createBoneViz(bones, skelKey, invScale) {
    const skel = Testzustand.skeletons[skelKey];
    removeBoneViz(skelKey);

    // invScale compensates for wrapper scaling so all Testzustand.skeletons look identical
    const s = invScale || 1;
    const jointGeo = new THREE.SphereGeometry(JOINT_RADIUS * s, 6, 4);
    const _up = new THREE.Vector3(0, 1, 0);

    for (const bone of bones) {
        // Joint sphere at each bone origin
        const joint = new THREE.Mesh(jointGeo, JOINT_MAT);
        joint.renderOrder = 998;
        bone.add(joint);
        skel.vizMeshes.push(joint);

        // Cylinder from parent to this bone
        if (!bone.parent || !bone.parent.isBone) continue;
        const len = bone.position.length();
        if (len < 0.0001) continue;

        const cylGeo = new THREE.CylinderGeometry(CYL_RADIUS_TOP * s, CYL_RADIUS_BOT * s, len, 4, 1);
        const cyl = new THREE.Mesh(cylGeo, BONE_MAT);
        cyl.renderOrder = 998;

        cyl.position.copy(bone.position).multiplyScalar(0.5);
        const dir = bone.position.clone().normalize();
        cyl.quaternion.setFromUnitVectors(_up, dir);

        bone.parent.add(cyl);
        skel.vizMeshes.push(cyl);
    }

    skel._jointGeo = jointGeo;
}

export function removeBoneViz(skelKey) {
    const skel = Testzustand.skeletons[skelKey];
    for (const mesh of skel.vizMeshes) {
        if (mesh.parent) mesh.parent.remove(mesh);
        if (mesh.geometry) mesh.geometry.dispose();
    }
    skel.vizMeshes = [];
    skel._jointGeo = null;
}

// =========================================================================
// Bone Labels (CSS2DObjects) — sequential numbers only
// =========================================================================
export function createBoneLabels(bones, skelKey) {
    const skel = Testzustand.skeletons[skelKey];
    // Remove old labels
    skel.labels.forEach(lbl => lbl.parent && lbl.parent.remove(lbl));
    skel.labels = [];

    const colorMap = { def: '#ff6666', cmu: '#66ff66', mixamo: '#ffaa66', mocapnet: '#6699ff', bandai: '#cc66ff', smpl: '#ffff00', openpose: '#44dddd' };
    const color = colorMap[skelKey] || '#ffffff';
    const showLabels = document.getElementById('toggle-labels').checked;

    // Store name mapping for tooltip/console lookup
    skel.boneIndex = [];

    for (let i = 0; i < bones.length; i++) {
        const bone = bones[i];
        skel.boneIndex.push(bone.name);

        const div = document.createElement('div');
        div.textContent = i;
        div.title = bone.name;
        div.style.cssText = `
            font-size: 8px;
            font-family: monospace;
            color: ${color};
            background: rgba(0,0,0,0.55);
            padding: 0px 2px;
            border-radius: 2px;
            line-height: 1.1;
            pointer-events: none;
        `;

        const label = new CSS2DObject(div);
        label.visible = showLabels;
        bone.add(label);
        skel.labels.push(label);
    }

    // Log mapping to console for reference
    Protokoll.debug('Viewer', `${skelKey.toUpperCase()} bone index:`, skel.boneIndex.map((n, i) => `${i}: ${n}`));
}
