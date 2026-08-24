import * as THREE from 'three';
import { state } from './state.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { Smplkoerperfrage } from './smpl_koerperfrage.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Smplkleidernetz — ein SMPL-Kleidungsstück laden, anpassen und entfernen.
 *
 * Herausgelöst aus `smpl.js` (393 Zeilen). Es gibt ZWEI Netze je Stück, und das
 * ist Absicht:
 *
 *     state.smplGarmentMeshes[id]       das Stück am SMPL-Körper (Vorschau)
 *     state.garmentMeshes['smpl:'+id]   dasselbe Stück an der eigenen Figur
 *
 * Deshalb räumt `entfernen` auch beide weg — sonst bleibt eines im Grafik-
 * speicher und schwebt weiter in der Szene.
 *
 * Die Punkte des angepassten Netzes kommen in Blender-Achsen
 * (`blenderToThreeCoords`), die des Vorschau-Netzes nicht — der Server liefert
 * dort schon Three.js-Achsen. Wer das vertauscht, legt das Kleidungsstück quer.
 */
export class Smplkleidernetz {

    static ERSATZFARBE = '#4d8066';

    /** Material für Stoff: doppelseitig und minimal vor der Haut. */
    static stoffwerkstoff(farbe, rauheit) {
        return new THREE.MeshStandardMaterial({
            color: farbe, roughness: rauheit, metalness: 0.0,
            side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnit: -1,
        });
    }

    // ------------------------------------------------------------- Vorschau

    /** Das Stück am SMPL-Körper zeigen; liefert `true` bei Erfolg. */
    static async laden(kennung) {
        let daten;
        try {
            daten = await Serverabruf.json('/api/smpl/garment/mesh/'
                + `?garment_id=${encodeURIComponent(kennung)}`);
        } catch (fehler) {
            Protokoll.fehler('smpl', 'Kleidungsstück nicht ladbar', fehler);
            return false;
        }
        if (daten.error) {
            Protokoll.warnung('smpl', 'Kleidungsstück:', daten.error);
            return false;
        }
        Smplkleidernetz.entfernen(kennung);
        const netz = new THREE.Mesh(Smplkleidernetz._geometrie(daten),
                                    Smplkleidernetz._werkstoffAusReglern());
        netz.name = `smpl_garment_${kennung}`;
        Smplkleidernetz._stellen(netz);
        state.smplGarmentMeshes[kennung] = netz;
        state.scene.add(netz);
        Protokoll.debug('Viewer',
                        `SMPL garment loaded: ${kennung} (${daten.vertex_count} verts)`);
        if (state.bodyMesh && state.rigifySkeleton) {
            await Smplkleidernetz.anpassen(kennung);
        }
        return true;
    }

    static _geometrie(daten) {
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(
            base64ToFloat32(daten.vertices), 3));
        geometrie.setIndex(new THREE.BufferAttribute(
            base64ToUint32(daten.faces), 1));
        geometrie.setAttribute('normal', new THREE.BufferAttribute(
            base64ToFloat32(daten.normals), 3));
        return geometrie;
    }

    static _werkstoffAusReglern() {
        const farbe = document.getElementById('smpl-garment-color')?.value
            || Smplkleidernetz.ERSATZFARBE;
        const rauheit = document.getElementById('smpl-garment-roughness');
        return Smplkleidernetz.stoffwerkstoff(
            farbe, rauheit ? rauheit.value / 100 : 0.8);
    }

    /**
     * Das Vorschaunetz an den SMPL-Körper stellen.
     *
     * Ohne Körper (der Reiter wurde noch nicht benutzt) steht es an der Stelle
     * des Versatzreglers auf Hüfthöhe — sonst läge es im Boden.
     */
    static _stellen(netz) {
        const koerper = state.smplBodyMesh;
        if (!koerper) {
            const versatz = document.getElementById('smpl-body-xoffset');
            netz.position.x = versatz ? versatz.value / 100 : 1.0;
            netz.position.y = 0.86;
            netz.rotation.y = Math.PI;
            return;
        }
        netz.position.copy(koerper.position);
        netz.rotation.copy(koerper.rotation);
        const punkte = koerper.geometry.getAttribute('position');
        let summe = 0;
        for (let i = 0; i < punkte.count; i++) summe += punkte.getY(i);
        netz.position.y = summe / punkte.count;
    }

    // -------------------------------------------------------------- Anpassen

    /** Das Stück an die eigene Figur rechnen (Server) und einhängen. */
    static async anpassen(kennung) {
        let daten;
        try {
            ensureSkinned();
            daten = await Serverabruf.json(
                `/api/smpl/garment/fit/?${Smplkleidernetz._anpassfrage(kennung)}`);
        } catch (fehler) {
            Protokoll.fehler('smpl', 'Anpassen fehlgeschlagen', fehler);
            return;
        }
        if (daten.error) {
            Protokoll.warnung('smpl', 'Anpassen:', daten.error);
            return;
        }
        const schluessel = 'smpl:' + kennung;
        Smplkleidernetz._wegnehmen(state.garmentMeshes, schluessel);
        const netz = Smplkleidernetz._angepasstesNetz(daten);
        netz.name = `smpl_garment_fit_${kennung}`;
        state.garmentMeshes[schluessel] = netz;
        state.scene.add(netz);
    }

    static _anpassfrage(kennung) {
        const farbe = new THREE.Color(
            document.getElementById('smpl-garment-color')?.value
            || Smplkleidernetz.ERSATZFARBE);
        return `garment_id=${encodeURIComponent(kennung)}`
            + `&${Smplkoerperfrage.text()}`
            + `&color_r=${farbe.r.toFixed(3)}&color_g=${farbe.g.toFixed(3)}`
            + `&color_b=${farbe.b.toFixed(3)}`;
    }

    /**
     * Das angepasste Netz — mit Hautbindung, wenn die Figur ein Skelett hat.
     *
     * Ohne die Bindung bliebe das Kleidungsstück in der Ruhelage stehen, während
     * sich die Figur bewegt.
     */
    static _angepasstesNetz(daten) {
        const punkte = base64ToFloat32(daten.vertices);
        blenderToThreeCoords(punkte);
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        geometrie.setIndex(new THREE.BufferAttribute(
            base64ToUint32(daten.faces), 1));
        geometrie.computeVertexNormals();
        const werkstoff = Smplkleidernetz.stoffwerkstoff(
            new THREE.Color(daten.color[0], daten.color[1], daten.color[2]), 0.8);
        if (!state.isSkinned || !state.rigifySkeleton
                || !daten.skin_indices || !daten.skin_weights) {
            return new THREE.Mesh(geometrie, werkstoff);
        }
        geometrie.setAttribute('skinIndex', new THREE.Float32BufferAttribute(
            base64ToFloat32(daten.skin_indices), 4));
        geometrie.setAttribute('skinWeight', new THREE.Float32BufferAttribute(
            base64ToFloat32(daten.skin_weights), 4));
        const netz = new THREE.SkinnedMesh(geometrie, werkstoff);
        netz.bind(state.rigifySkeleton.skeleton, state.bodyMesh.bindMatrix);
        return netz;
    }

    // -------------------------------------------------------------- Entfernen

    /** Beide Netze eines Stücks entfernen und freigeben. */
    static entfernen(kennung) {
        Smplkleidernetz._wegnehmen(state.smplGarmentMeshes, kennung);
        Smplkleidernetz._wegnehmen(state.garmentMeshes, 'smpl:' + kennung);
    }

    static _wegnehmen(ablage, schluessel) {
        const netz = ablage[schluessel];
        if (!netz) return;
        state.scene.remove(netz);
        netz.geometry.dispose();
        netz.material.dispose();
        delete ablage[schluessel];
    }
}
