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

// Steg vom Knochenende zum Kindgelenk (nur mit `achsen`): ab 1 mm Versatz.
const STEG_RADIUS = 0.0015;

const STEG_AB = 0.001;

// =========================================================================
// Bone Visualization — white cylinders + joint spheres
// =========================================================================
/**
 * `achsen` (optional): `{name: Länge}` — dann geht der Zylinder eines Knochens
 * von SEINEM Gelenk entlang seiner Achse (+Y), wie Daz seine Knochen zeigt.
 * Bei Genesis 9 sitzt das Gelenk von `neck2` 12 mm vor dem Ende von `neck1`
 * (so steht es in `Genesis9.dsf`): Gelenk zu Gelenk gezeichnet knickte der
 * Hals 20°, den das Retarget nie gemacht hat (Edgar, 19.09.2026: „Knick
 * zwischen 96, 97 und 110"); nur entlang der Achsen klaffte die Kette
 * („die Knochen am Hals kommen nicht zusammen"). Deshalb dazu ein STEG vom
 * Knochenende zu jedem Kindgelenk, das nicht dort sitzt — dünner, damit
 * der Versatz als Versatz lesbar bleibt.
 */
export function createBoneViz(bones, skelKey, invScale, achsen = null) {
    const skel = Testzustand.skeletons[skelKey];
    removeBoneViz(skelKey);

    // invScale compensates for wrapper scaling so all Testzustand.skeletons look identical
    const s = invScale || 1;
    const jointGeo = new THREE.SphereGeometry(JOINT_RADIUS * s, 6, 4);
    const _up = new THREE.Vector3(0, 1, 0);
    const steg = (eltern, von, nach) => {
        const weg = nach.clone().sub(von);
        const len = weg.length();
        if (len < STEG_AB) return;
        const cyl = new THREE.Mesh(
            new THREE.CylinderGeometry(STEG_RADIUS * s, STEG_RADIUS * s, len, 4, 1), BONE_MAT);
        cyl.renderOrder = 998;
        cyl.position.copy(von).add(weg.multiplyScalar(0.5));
        cyl.quaternion.setFromUnitVectors(_up, nach.clone().sub(von).normalize());
        eltern.add(cyl);
        skel.vizMeshes.push(cyl);
    };

    for (const bone of bones) {
        // Joint sphere at each bone origin
        const joint = new THREE.Mesh(jointGeo, JOINT_MAT);
        joint.renderOrder = 998;
        bone.add(joint);
        skel.vizMeshes.push(joint);

        if (achsen) {
            const laenge = achsen[bone.name];
            if (!laenge) continue;      // Endmarke: kein eigener Knochen
            const cyl = new THREE.Mesh(
                new THREE.CylinderGeometry(CYL_RADIUS_TOP * s, CYL_RADIUS_BOT * s, laenge, 4, 1),
                BONE_MAT);
            cyl.renderOrder = 998;
            cyl.position.set(0, laenge / 2, 0);
            bone.add(cyl);
            skel.vizMeshes.push(cyl);
            const ende = new THREE.Vector3(0, laenge, 0);
            for (const kind of bone.children) {
                if (kind.isBone) steg(bone, ende, kind.position);
            }
            continue;
        }
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

    // Die Farbe kommt aus der Spalte (`testzustand.js`) — dieselbe wie der
    // Punkt in der Legende. Eine zweite Tabelle hier kannte UMA nicht, und
    // seine Nummern standen weiß da (05.09.2026).
    const color = '#' + skel.color.toString(16).padStart(6, '0');
    const showLabels = document.getElementById('toggle-labels').checked;

    // Store name mapping for tooltip/console lookup
    skel.boneIndex = [];

    for (let i = 0; i < bones.length; i++) {
        const bone = bones[i];
        skel.boneIndex.push(bone.name);

        const div = document.createElement('div');
        div.textContent = String(i);
        div.title = bone.name;
        // Nur die FARBE bleibt am Element: Sie sagt, zu welchem Skelett
        // die Nummer gehoert. Alles andere steht als `.knochennummer` in
        // `stilhelfer.css` (30.08.2026, Befund `jsbefunde`).
        div.className = 'knochennummer';
        div.style.color = color;

        const label = new CSS2DObject(div);
        label.visible = showLabels;
        bone.add(label);
        skel.labels.push(label);
    }

    // Log mapping to console for reference
    Protokoll.debug('Viewer', `${skelKey.toUpperCase()} bone index:`, skel.boneIndex.map((n, i) => `${i}: ${n}`));
}
