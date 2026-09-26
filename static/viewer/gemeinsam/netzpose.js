import * as THREE from 'three';
import { Netzattribute } from './netzattribute.js';

/**
 * Netzpose — ein SkinnedMesh als STARRES Netz, in einer gewählten Pose.
 *
 * FÜR FORMATE OHNE RIG (OBJ, PLY, STL — und GLB/.blend/DAE, wenn „Rig" im
 * Exportdialog aus ist, `Docu/konzept_modellexport.md`): Diese Formate
 * kennen kein Skelett, also müssen die Punkte VORHER in eine feste Lage
 * gebracht werden.
 *
 * ZWEI POSEN, EIN UNTERSCHIED IM AUFWAND
 * =======================================
 * `RUHELAGE`: kein Rechnen nötig. Three.js skinnt nur auf der Grafikkarte —
 * `geometry.attributes.position` ändert sich dabei NIE, dort steht immer die
 * Bindepose. Es wird nur eine Kopie ohne `skinIndex`/`skinWeight` angelegt.
 *
 * `AKTUELL`: CPU-Skinning nach genau der Formel aus Threes eigenem
 * Vertex-Shader (`three/src/renderers/shaders/ShaderChunk/skinning_vertex.glsl.js`):
 * je Punkt die bis zu vier gewichteten Knochenmatrizen anwenden. Das ist ein
 * EINMALIGER Rechenschritt beim Export (kein Dauerbetrieb) — für ein dichtes
 * Netz (Genesis 9, ~70.000 Punkte) im Bereich von Zehntelsekunden in reinem
 * JS, vertretbar für eine Aktion, die der Nutzer einmal auslöst.
 *
 * NORMALEN: nach dem Backen NEU bestimmt (`computeVertexNormals`), nicht
 * mitgerechnet — für OBJ/PLY/STL reicht das; ein kleiner Versatz gegenüber
 * der schattergenauen Normale ist in Kauf genommen, nicht übersehen.
 */
export class Netzpose {

    static RUHELAGE = 'ruhelage';
    static AKTUELL = 'aktuell';

    /**
     * Eine gebackene Kopie: normales `THREE.Mesh`, LOKALE Lage = die
     * WELTLAGE des Originals (die Kopie ist für sich allein gedacht, ohne
     * die Elternkette der Szene — der Aufrufer hängt sie an eine eigene
     * `THREE.Group` bei Identität und ruft `updateMatrixWorld(true)`, dann
     * stimmt die Weltlage wieder).
     */
    static gebacken(mesh, pose = Netzpose.RUHELAGE) {
        const geometrie = mesh.geometry.clone();
        for (const name of ['skinIndex', 'skinWeight']) {
            if (geometrie.getAttribute(name)) geometrie.deleteAttribute(name);
        }
        // Eigene Shader-Attribute (`dicke`, `einzug`, …) raus — siehe `Netzattribute`.
        Netzattribute.eigeneEntfernen(geometrie);
        if (pose === Netzpose.AKTUELL && mesh.isSkinnedMesh && mesh.skeleton) {
            Netzpose._skinnen(mesh, geometrie);
        }
        geometrie.computeVertexNormals();
        const netz = new THREE.Mesh(geometrie, mesh.material);
        netz.name = mesh.name;
        mesh.updateWorldMatrix(true, false);
        mesh.matrixWorld.decompose(netz.position, netz.quaternion, netz.scale);
        return netz;
    }

    /** Punkte in `geometrie.attributes.position` durch die AKTUELLE Pose ersetzen. */
    static _skinnen(mesh, geometrie) {
        const quelle = mesh.geometry;
        const pos = quelle.getAttribute('position');
        const skinIndex = quelle.getAttribute('skinIndex');
        const skinWeight = quelle.getAttribute('skinWeight');
        if (!pos || !skinIndex || !skinWeight) return;
        const { bones, boneInverses } = mesh.skeleton;
        const ausgabe = geometrie.getAttribute('position');
        const v = new THREE.Vector3();
        const beitrag = new THREE.Vector3();
        const summe = new THREE.Vector3();
        const boneMatrix = new THREE.Matrix4();
        for (let i = 0; i < pos.count; i++) {
            v.fromBufferAttribute(pos, i).applyMatrix4(mesh.bindMatrix);
            summe.set(0, 0, 0);
            for (let k = 0; k < 4; k++) {
                const gewicht = skinWeight.getComponent(i, k);
                if (!gewicht) continue;
                const knochen = skinIndex.getComponent(i, k);
                boneMatrix.multiplyMatrices(bones[knochen].matrixWorld, boneInverses[knochen]);
                summe.add(beitrag.copy(v).applyMatrix4(boneMatrix).multiplyScalar(gewicht));
            }
            summe.applyMatrix4(mesh.bindMatrixInverse);
            ausgabe.setXYZ(i, summe.x, summe.y, summe.z);
        }
        ausgabe.needsUpdate = true;
    }
}
