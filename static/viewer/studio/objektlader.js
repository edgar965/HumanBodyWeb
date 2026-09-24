import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Objektlader — eine 3D-Datei laden und für die Szene brauchbar machen.
 *
 * Aus objektimport.js herausgeloest (Umbau 17.08.2026):
 * `_loadSceneObjectIntoTrack` hatte 116 Zeilen und tat vier Dinge —
 * Datei laden, Materialien reparieren, Groesse und Lage normieren, und die
 * Spur samt Clip aufbauen. Hier stehen die ersten drei; das Einsetzen in die
 * Spur bleibt beim Aufrufer, der die Zeitleiste kennt.
 *
 * ZWEI EIGENHEITEN, die hier bewusst erhalten sind:
 *
 *  * OBJ ohne Normalen wird sonst schwarz gerendert — `computeVertexNormals`
 *    ist kein Schoenheitsschritt.
 *  * 3ds Max schreibt `Ke` (emissive) oft auf 1,1,1. Zusammen mit einer Textur
 *    ueberstrahlt das alles: Das Objekt erscheint einheitlich weiss. Bei
 *    vorhandener Textur ist Emissive praktisch immer ein Exportfehler.
 */
export class Objektlader {

    /** Zielgroesse der laengsten Kante in Metern. */
    static ZIELGROESSE = 1;
    /** Farbe, wenn ein OBJ gar kein Material mitbringt. */
    static ERSATZFARBE = 0x888899;
    static ERSATZRAUHEIT = 0.7;

    /**
     * @param {string} url     Adresse der Datei
     * @param {string} ext     'obj' | 'glb' | 'gltf'
     * @param {string} mtlUrl  Materialdatei, wenn bekannt
     */
    constructor(url, ext, mtlUrl = null) {
        this.url = url;
        this.ext = ext;
        this.mtlUrl = mtlUrl;
    }

    /** Geladenes und normiertes Objekt. Wirft, wenn das Format nicht geht. */
    async laden() {
        const objekt = this.ext === 'obj' ? await this._obj()
            : (this.ext === 'glb' || this.ext === 'gltf') ? await this._gltf()
            : null;
        if (!objekt) {
            throw new Error(`Format "${this.ext}" wird noch nicht unterstützt`);
        }
        this._ersatzmaterial(objekt);
        Objektlader.normieren(objekt);
        return objekt;
    }

    async _obj() {
        const lader = new OBJLoader();
        if (this.mtlUrl) await this._materialien(lader);
        const objekt = await lader.loadAsync(this.url);
        objekt.traverse(teil => Objektlader._materialReparieren(teil));
        return objekt;
    }

    async _gltf() {
        return (await new GLTFLoader().loadAsync(this.url)).scene;
    }

    /** MTL laden und am OBJ-Lader setzen. Scheitert es, laeuft OBJ ohne. */
    async _materialien(lader) {
        try {
            const mtl = new MTLLoader();
            const basis = this.mtlUrl.substring(0, this.mtlUrl.lastIndexOf('/') + 1);
            mtl.setResourcePath(basis);
            mtl.setPath(basis);
            const materialien = await mtl.loadAsync(
                this.mtlUrl.substring(this.mtlUrl.lastIndexOf('/') + 1));
            materialien.preload();
            lader.setMaterials(materialien);
            const namen = Object.keys(materialien.materials || {});
            Protokoll.debug('3D-Objekt', `MTL geladen: ${namen.length} Materialien`
                            + ` (${namen.join(', ')})`);
        } catch (fehler) {
            Protokoll.warnung('3D-Objekt', 'MTL nicht ladbar, OBJ ohne:', fehler);
        }
    }

    static _materialReparieren(teil) {
        if (!teil.isMesh) return;
        if (teil.geometry && !teil.geometry.attributes.normal) {
            teil.geometry.computeVertexNormals();
        }
        if (!teil.material) return;
        const alle = Array.isArray(teil.material) ? teil.material : [teil.material];
        for (const material of alle) {
            if (!material) continue;
            // Viele OBJs haben uneinheitliche Normalen — beidseitig zeichnen.
            material.side = THREE.DoubleSide;
            const leuchtet = material.emissive
                && (material.emissive.r > 0 || material.emissive.g > 0
                    || material.emissive.b > 0);
            if (material.map && leuchtet) {
                material.emissive.setRGB(0, 0, 0);
                material.needsUpdate = true;
            }
        }
    }

    /** Nur wenn gar kein Material da ist — sonst bliebe das Objekt unsichtbar. */
    _ersatzmaterial(objekt) {
        if (this.ext !== 'obj' || this.mtlUrl) return;
        objekt.traverse(teil => {
            if (teil.isMesh && (!teil.material || !teil.material.color)) {
                teil.material = new THREE.MeshStandardMaterial({
                    color: Objektlader.ERSATZFARBE,
                    roughness: Objektlader.ERSATZRAUHEIT,
                });
            }
        });
    }

    /**
     * Auf Zielgroesse skalieren und so setzen, dass das Objekt mittig auf dem
     * Boden steht (y = 0 an der Unterkante).
     */
    static normieren(objekt) {
        const kasten = new THREE.Box3().setFromObject(objekt);
        const groesse = new THREE.Vector3();
        const mitte = new THREE.Vector3();
        kasten.getSize(groesse);
        kasten.getCenter(mitte);
        const laengste = Math.max(groesse.x, groesse.y, groesse.z);
        if (laengste <= 0) return objekt;
        const faktor = Objektlader.ZIELGROESSE / laengste;
        objekt.scale.setScalar(faktor);
        objekt.position.set(-mitte.x * faktor, -kasten.min.y * faktor,
                            -mitte.z * faktor);
        return objekt;
    }

    /** Ein Objekt samt Geometrien und Materialien freigeben. */
    static entsorgen(objekt) {
        objekt?.traverse?.(teil => {
            teil.geometry?.dispose?.();
            if (!teil.material) return;
            const alle = Array.isArray(teil.material) ? teil.material
                                                      : [teil.material];
            alle.forEach(material => material?.dispose?.());
        });
    }
}
