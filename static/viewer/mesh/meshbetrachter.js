import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Buehne } from '../gemeinsam/buehne.js';

/**
 * Meshbetrachter — zeigt ein GLB in einer eigenen Leinwand (Reiter „Mesh", 26.09.2026).
 * Nutzt dieselbe Bühne wie jede Figurenseite (`gemeinsam/buehne.js`), zentriert und
 * skaliert das geladene Netz einmal auf den sichtbaren Bereich (die Höhe kommt aus den
 * Meshoptionen, muss aber nicht exakt stimmen — hier zählt nur „sieht man ganz").
 */
export class Meshbetrachter {

    constructor(behaelter) {
        this.behaelter = behaelter;
        this.leinwand = document.createElement('canvas');
        this.behaelter.appendChild(this.leinwand);
        const { renderer, scene, camera, controls } = Buehne.bauen(this.leinwand, { masse: 'rahmen', stil: true });
        Object.assign(this, { renderer, scene, camera, controls });
        this._lader = new GLTFLoader();
        this._objekt = null;
        this._laufend = false;
        window.addEventListener('resize', () => this._groesseAnpassen());
        this._animieren();
    }

    async laden(url) {
        this.entfernen();
        const gltf = await this._lader.loadAsync(url);
        const objekt = gltf.scene;
        this._ausrichten(objekt);
        this.scene.add(objekt);
        this._objekt = objekt;
        return objekt;
    }

    /** Alle Mesh-Knoten des geladenen Netzes — für `Meshfotogewicht` (Live-Vorschau der
     *  Vertexfarben bei Reglerbewegung, ändert `geometry.attributes.color` direkt). */
    meshKnoten() {
        const aus = [];
        this._objekt?.traverse(kind => { if (kind.isMesh) aus.push(kind); });
        return aus;
    }

    entfernen() {
        if (!this._objekt) return;
        this.scene.remove(this._objekt);
        this._objekt.traverse(kind => {
            kind.geometry?.dispose?.();
            const materialien = Array.isArray(kind.material) ? kind.material : [kind.material];
            for (const material of materialien) {
                if (!material) continue;
                for (const schluessel of ['map', 'normalMap', 'roughnessMap', 'metalnessMap']) {
                    material[schluessel]?.dispose?.();
                }
                material.dispose();
            }
        });
        this._objekt = null;
    }

    /** Das Netz auf Größe 2 zentrieren und auf den Boden stellen — unabhängig von seinem
     *  eigenen Maßstab sieht man es damit immer ganz, egal wie `hoehe_cm` gerechnet hat. */
    _ausrichten(objekt) {
        const kasten = new THREE.Box3().setFromObject(objekt);
        const groesse = kasten.getSize(new THREE.Vector3());
        const mitte = kasten.getCenter(new THREE.Vector3());
        const groesster = Math.max(groesse.x, groesse.y, groesse.z, 1e-6);
        const massstab = 2 / groesster;
        objekt.scale.setScalar(massstab);
        objekt.position.set(-mitte.x * massstab, -kasten.min.y * massstab, -mitte.z * massstab);
    }

    _groesseAnpassen() {
        const [breite, hoehe] = Buehne.masse(this.leinwand, 'rahmen');
        if (!breite || !hoehe) return;
        this.camera.aspect = breite / hoehe;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(breite, hoehe, true);
    }

    _animieren() {
        if (this._laufend) return;
        this._laufend = true;
        const takt = () => {
            if (!this.behaelter.isConnected) { this._laufend = false; return; }
            this.controls.update();
            this.renderer.render(this.scene, this.camera);
            requestAnimationFrame(takt);
        };
        this._groesseAnpassen();
        requestAnimationFrame(takt);
    }
}
