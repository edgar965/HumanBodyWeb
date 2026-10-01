import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PLYLoader } from 'three/addons/loaders/PLYLoader.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

/**
 * Meshfigurnetze — Körpernetz und (falls angegeben) Kopfnetz eines Auftrags „Mesh to 3D" auf der Bühne.
 *
 * Beide stehen in der Lage, die die Erkennung gefunden hat (`erkennung.matrix`, der Kopf mit
 * `erkennung.kopf.matrix_lage`), ggf. um den Faktor „Körpergröße" gestreckt. Mit Kopfnetz schneidet
 * je eine Ebene quer zum Hals (`erkennung.kopf.ebene`) wie im Zielnetz des Runners: unten zeigt das
 * Körpernetz, oben das Kopfnetz — so sieht man, woran die Figur angepasst wurde.
 */
export class Meshfigurnetze {

    constructor(seite, szene, melden) {
        this.seite = seite;
        this.szene = szene;
        this.melden = melden;
        this.gruppe = null;
        this._schluessel = null;
        this._ebenen = [];
        this._ebene = null;
    }

    static lader(name) {
        const endung = String(name).toLowerCase().split('.').pop();
        if (endung === 'glb' || endung === 'gltf') return ['gltf', new GLTFLoader()];
        if (endung === 'obj') return ['obj', new OBJLoader()];
        if (endung === 'ply') return ['ply', new PLYLoader()];
        if (endung === 'stl') return ['stl', new STLLoader()];
        return [null, null];
    }

    static matrix(m, faktor) {
        const matrix = new THREE.Matrix4().set(...m[0], ...m[1], ...m[2], ...m[3]);
        return matrix.premultiply(new THREE.Matrix4().makeScale(faktor, faktor, faktor));
    }

    /** Ohne Lage der Erkennung: das Netz mittig auf den Boden (TRELLIS liefert Y oben, um den Ursprung). */
    static aufBoden(objekt) {
        const kasten = new THREE.Box3().setFromObject(objekt), mitte = kasten.getCenter(new THREE.Vector3());
        return new THREE.Matrix4().makeTranslation(-mitte.x, -kasten.min.y, -mitte.z);
    }

    /** Netze (neu) laden, wenn sich Eingang oder Lage geändert haben — true, wenn neu geladen. */
    zeigen(z) {
        const e = z.ergebnis || {};
        const erkennung = e.erkennung || {};
        // Ohne Erkennung (gleich nach dem Netz, vor „Körper") das Netz roh, auf den Boden gestellt (01.10.2026).
        if (!erkennung.matrix && !(z.eingang || {}).datei) return false;
        const kopf = (z.eingang || {}).kopf && erkennung.kopf && erkennung.kopf.matrix_lage ? erkennung.kopf : null;
        const schluessel = JSON.stringify([(z.eingang || {}).datei, ((z.eingang || {}).kopf || {}).datei,
                                           erkennung.matrix, kopf && kopf.matrix_lage, erkennung.skalierung]);
        if (schluessel === this._schluessel) return false;
        this._schluessel = schluessel;
        this.entfernen();
        const faktor = (erkennung.skalierung || {}).faktor || 1;
        this.gruppe = new THREE.Group();
        this.gruppe.visible = false;
        this.szene.add(this.gruppe);
        this._ebene = kopf ? {
            punkt: new THREE.Vector3(...kopf.ebene.punkt).multiplyScalar(faktor),
            achse: new THREE.Vector3(...kopf.ebene.achse).normalize(),
        } : null;
        this._ebenen = kopf ? [new THREE.Plane(), new THREE.Plane()] : [];
        this.verschieben(0);
        this._laden('eingang', z.eingang.datei, erkennung.matrix ? Meshfigurnetze.matrix(erkennung.matrix, faktor) : null,
            this._ebenen[0]);
        if (kopf) this._laden('eingang_kopf', z.eingang.kopf.datei, Meshfigurnetze.matrix(kopf.matrix_lage, faktor), this._ebenen[1]);
        return true;
    }

    /** Schnittebenen in Weltlage nachziehen (die Gruppe rückt bei „Nebeneinander" nach rechts). */
    verschieben(x) {
        if (this.gruppe) this.gruppe.position.x = x;
        if (!this._ebene) return;
        const punkt = this._ebene.punkt.clone().add(new THREE.Vector3(x, 0, 0));
        // Körper: sichtbar, was UNTER der Ebene liegt; Kopf: was darüber liegt (three.js schneidet weg,
        // was auf der negativen Seite einer Ebene liegt).
        this._ebenen[0].setFromNormalAndCoplanarPoint(this._ebene.achse.clone().negate(), punkt);
        this._ebenen[1].setFromNormalAndCoplanarPoint(this._ebene.achse, punkt);
    }

    sichtbar(ja) { if (this.gruppe) this.gruppe.visible = ja; }

    entfernen() {
        if (!this.gruppe) return;
        this.szene.remove(this.gruppe);
        this.gruppe.traverse(o => { o.geometry?.dispose?.(); });
        this.gruppe = null;
    }

    _laden(ordner, datei, matrix, ebene) {
        const [art, lader] = datei ? Meshfigurnetze.lader(datei) : [null, null];
        if (!lader) { this.melden(`Netz ${datei || '—'}: Format wird hier nicht angezeigt`); return; }
        const gruppe = this.gruppe;
        lader.load(this.seite.dateiAdresse(ordner, datei), ergebnis => {
            let objekt = ergebnis.scene || ergebnis;
            if (ergebnis.isBufferGeometry) {
                ergebnis.computeVertexNormals();
                objekt = new THREE.Mesh(ergebnis, new THREE.MeshStandardMaterial({ color: 0xc9b4a4, roughness: 0.8 }));
            }
            if (ebene) {
                objekt.traverse(o => {
                    for (const m of [].concat(o.material || [])) m.clippingPlanes = [ebene];
                });
            }
            objekt.updateMatrixWorld(true);
            const innen = new THREE.Group();
            innen.matrixAutoUpdate = false;
            innen.matrix.copy(matrix || Meshfigurnetze.aufBoden(objekt));
            innen.add(objekt);
            gruppe.add(innen);
        }, undefined, fehler => this.melden(`Netz (${art}) nicht geladen: ${fehler.message || fehler}`));
    }
}
