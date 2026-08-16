import * as THREE from 'three';
import { base64ToFloat32, base64ToUint32, base64ToUint16 } from './helpers.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Smplxnetz — aus der Serverantwort ein SkinnedMesh mit Skelett bauen.
 *
 * Aus smplx_model.js herausgeloest (Umbau 17.08.2026): `loadSmplxModel` hatte
 * 103 Zeilen — Anfrage, Aufräumen, Skelettbau, Geometrie, Material, Binden und
 * Anzeige in einer Funktion. Der Bau steht jetzt hier, das Einsetzen in die
 * Szene bleibt beim Aufrufer.
 *
 * ZWEI FASSUNGEN DERSELBEN GEOMETRIE: Der Server liefert das Netz wahlweise
 * mit UV-Zerlegung (`uv_vertices`, mehr Punkte, weil Nähte doppelt liegen) oder
 * ohne. Beide Fassungen bringen ihre eigenen Skinning-Gewichte mit — sie zu
 * mischen ergäbe ein verzerrtes Netz.
 */
export class Smplxnetz {

    /** Hautton des SMPL-X-Vergleichsmodells. */
    static FARBE = 0xccaa88;
    static RAUHEIT = 0.55;
    /** So viele Knochen wirken auf einen Punkt. */
    static EINFLUESSE = 4;

    constructor(daten) {
        this.daten = daten;
        this.mitUv = !!daten.uv_coords;
    }

    /** Fertiges SkinnedMesh, Skelett bereits gebunden. */
    bauen() {
        const knochen = this.knochen();
        const netz = new THREE.SkinnedMesh(this.geometrie(), Smplxnetz.material());
        // Reihenfolge zählt: erst den Wurzelknochen anhängen, dann binden.
        netz.add(knochen[0]);
        netz.bind(new THREE.Skeleton(knochen));
        return netz;
    }

    /**
     * Knochenkette aus Gelenkpunkten und Elternliste.
     *
     * Die Punkte kommen in Weltkoordinaten; Three.js erwartet die Lage
     * RELATIV zum Elternknochen — daher die Differenz.
     */
    knochen() {
        const punkte = base64ToFloat32(this.daten.joints);
        const eltern = this.daten.parents;
        const anzahl = this.daten.n_joints;
        const knochen = [];
        for (let i = 0; i < anzahl; i++) {
            const einer = new THREE.Bone();
            einer.name = `smplx_j${i}`;
            knochen.push(einer);
        }
        for (let i = 0; i < anzahl; i++) {
            const elter = eltern[i];
            const x = punkte[i * 3], y = punkte[i * 3 + 1], z = punkte[i * 3 + 2];
            if (elter < 0) {
                knochen[i].position.set(x, y, z);
                continue;
            }
            knochen[i].position.set(x - punkte[elter * 3],
                                    y - punkte[elter * 3 + 1],
                                    z - punkte[elter * 3 + 2]);
            knochen[elter].add(knochen[i]);
        }
        return knochen;
    }

    geometrie() {
        const daten = this.daten;
        const uv = this.mitUv;
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(
            base64ToFloat32(uv ? daten.uv_vertices : daten.vertices), 3));
        geo.setIndex(new THREE.BufferAttribute(
            base64ToUint32(uv ? daten.uv_faces : daten.faces), 1));
        if (uv) {
            geo.setAttribute('uv', new THREE.BufferAttribute(
                base64ToFloat32(daten.uv_coords), 2));
            Protokoll.debug('SMPL-X', `UV-Daten: ${daten.n_uv_verts} Punkte`);
        }
        geo.computeVertexNormals();
        geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(
            base64ToUint16(uv ? daten.uv_skin_indices : daten.skin_indices),
            Smplxnetz.EINFLUESSE));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(
            base64ToFloat32(uv ? daten.uv_skin_weights : daten.skin_weights),
            Smplxnetz.EINFLUESSE));
        return geo;
    }

    static material() {
        return new THREE.MeshStandardMaterial({
            color: Smplxnetz.FARBE, roughness: Smplxnetz.RAUHEIT,
            metalness: 0.0, side: THREE.DoubleSide,
        });
    }

    /** Die 310 Formwerte: 10 Körperform, ab 300 die Mimik. */
    static formwerte(betas, ausdruck) {
        const alle = new Array(Smplxnetz.WERTE).fill(0);
        for (let i = 0; i < Smplxnetz.FORM; i++) alle[i] = betas[i];
        for (let i = 0; i < Smplxnetz.MIMIK; i++) {
            alle[Smplxnetz.MIMIK_AB + i] = ausdruck[i];
        }
        return alle;
    }

    static WERTE = 310;
    static FORM = 10;
    static MIMIK = 10;
    static MIMIK_AB = 300;
}
