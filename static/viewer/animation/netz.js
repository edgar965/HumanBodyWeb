/**
 * Netz und Skelett der Animationsseite laden.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026).
 */

import * as THREE from 'three';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';
import { Seitenzustand } from './seitenzustand.js';
import { BODY_MATERIALS, applySceneSkinSettings, applySkinColor } from './material.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Hautgewichte } from '../gemeinsam/hautgewichte.js';


export async function loadMesh() {
    try {
        const data = await Serverabruf.json('/api/character/mesh/');
        if (data.error) { Protokoll.fehler('Netz', data.error); return; }

        document.getElementById('vertex-count').textContent =
            data.vertex_count.toLocaleString();

        // Puffer, Normalen, Materialgruppen: siehe `Koerpernetz`. Diese dreißig
        // Zeilen standen fünfmal im Projekt (Befund `doppelcode`, 17.08.2026).
        Seitenzustand.bodyMesh = Koerpernetz.netz(data, THREE);
        const geo = Seitenzustand.bodyMesh.geometry;

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


    Hautgewichte.anGeometrie(Seitenzustand.bodyGeometry, swData, THREE.Float32BufferAttribute);

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
