import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';

/**
 * Gezeichneterpunkt — ein Netz so, wie die Szene es zeichnet. Morphe und Häutung kennt `getVertexPosition`; was der Vertex-Shader dazurechnet, nicht:
 *   hauteinzug   `transformed += einzug` hinter `begin_vertex`, VOR dem Skinning (`hauteinzug.js`; auch die Naht am Anatomie-Stück, `hautloch.js`)
 *   weichgewebe  `transformed += zuschlag` hinter `skinning_vertex` (`charakter/weichgewebeaufbau.js`, nur in Bewegung)
 *   oberflaeche  Kleidung aus der Körperoberfläche gedrückt (`oberflaechenbindung.js`, nach dem Skinning, je Bild aus der Körperlage)
 * Anlass 02.11.2026 abends (Edgar, Modell Check an Damira: „die Scham rot markiert, obwohl sie OK ist“, dann „mach genau die gleiche Erzeugung des Modells wie
 * im Haupt View“): das Anatomie-Stück unter g9_base_shorts trägt an 4.231 Punkten bis 41,7 mm Einzug, der Körper an 3.881 bis 14,2 mm (Olesia) — ohne ihn stach die
 * Scham in den Prüfbildern durch die Hose (vorne 1.066 px) und die Naht klaffte.
 */
export class Gezeichneterpunkt {

    static LAGE_EINGRIFFE = ['hauteinzug', 'weichgewebe', 'oberflaeche'];

    /** Punkt `i` von `netz` im Raum des Netzes mit dem Hauteinzug → `ziel` (Vector3). Weltlage: danach `applyMatrix4(netz.matrixWorld)`. */
    static lage(netz, i, ziel) {
        const e = netz.geometry.attributes.einzug;
        if (!e) return netz.getVertexPosition(i, ziel);
        THREE.Mesh.prototype.getVertexPosition.call(netz, i, ziel);           // Morphe — wie `SkinnedMesh.getVertexPosition`, nur mit dem Einzug davor
        ziel.x += e.getX(i); ziel.y += e.getY(i); ziel.z += e.getZ(i);
        return netz.isSkinnedMesh ? netz.applyBoneTransform(i, ziel) : ziel;
    }

    /**
     * `ziel` (ein eigenes Material) bekommt die lageverändernden Eingriffe von `quelle` — dieselben Funktionen samt ihren Uniforms (`Shaderpatch.eingriff`), die das
     * Netz in `onBeforeRender` je Bild nachführt. Gezeichnet liegt `ziel` dann deckungsgleich mit dem Netz der Szene. → `ziel`.
     */
    static eingriffe(quelle, ziel) {
        for (const k of Shaderpatch.schluessel(quelle)) {
            if (Gezeichneterpunkt.LAGE_EINGRIFFE.includes(k) && !Shaderpatch.hat(ziel, k)) Shaderpatch.anhaengen(ziel, k, Shaderpatch.eingriff(quelle, k));
        }
        return ziel;
    }
}
