import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/**
 * Meshfigurhaarobjekt — das Haar aus dem Netz als eigenes Objekt auf der Figur der Bühne (27.09.2026).
 *
 * Edgar: „mach mir die Haare als extra Objekt darin". Die Datei `ergebnis/haar.glb` schreibt der Schritt
 * „vorschau" (`Meshfigurhaar.objekt`) schon in der Ruhelage der Figur — sie hängt also ohne eigene Lage in
 * deren Gruppe und wandert mit, wenn die Figur neu gebaut wird (`anhaengen`). Der Schalter „Haar" blendet es
 * aus und ein.
 */
export class Meshfigurhaarobjekt {

    constructor(seite, melden) {
        this.seite = seite;
        this.melden = melden;
        this.objekt = null;
        this.gruppe = null;
        this._stand = null;
        this.schalter = document.getElementById('buehne-haar');
        this.schalter?.addEventListener('change', () => this._sichtbar());
    }

    /** Laden, wenn sich die Datei geändert hat; `gruppe` = die Gruppe der Figur (oder null). */
    zeigen(z, gruppe) {
        const o = ((z.ergebnis || {}).haar || {}).objekt || {};
        if (this.schalter) this.schalter.closest('label').hidden = !o.datei;
        if (o.fehler) this.melden(`Haarobjekt: ${o.fehler}`);
        if (!o.datei) return;
        const stand = JSON.stringify([o.datei, o.bytes, o.flaechen, z.updated_at && o.punkte]);
        if (stand !== this._stand) {
            this._stand = stand;
            this._laden(`${this.seite.dateiAdresse('ergebnis', o.datei)}?t=${encodeURIComponent(stand)}`);
        }
        if (gruppe) this.anhaengen(gruppe);
    }

    anhaengen(gruppe) {
        this.gruppe = gruppe;
        if (this.objekt && this.objekt.parent !== gruppe) {
            this.objekt.parent?.remove(this.objekt);
            gruppe.add(this.objekt);
        }
        this._sichtbar();
    }

    _sichtbar() {
        if (this.objekt) this.objekt.visible = this.schalter ? this.schalter.checked : true;
    }

    _laden(adresse) {
        new GLTFLoader().load(adresse, gltf => {
            const neu = gltf.scene;
            neu.name = 'Haar aus dem Netz';
            neu.traverse(o => {
                for (const m of [].concat(o.material || [])) {
                    m.side = THREE.DoubleSide;
                    m.metalness = 0;
                }
            });
            if (this.objekt) {
                this.objekt.parent?.remove(this.objekt);
                this.objekt.traverse(o => { o.geometry?.dispose?.(); });
            }
            this.objekt = neu;
            if (this.gruppe) this.anhaengen(this.gruppe);
        }, undefined, fehler => this.melden(`Haarobjekt nicht geladen: ${fehler.message || fehler}`));
    }
}
