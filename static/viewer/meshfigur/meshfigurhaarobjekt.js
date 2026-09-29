import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/**
 * Meshfigurhaarobjekt — ein Haar als eigenes Objekt auf der Figur der Bühne: das Haar aus dem Netz
 * (`ergebnis/haar.glb`, 27.09.2026) oder die Haarkarten aus seiner Schale (`ergebnis/haarkarten.glb`,
 * Schritt „frisur", 29.09.2026). Beide liegen schon in der Ruhelage der Figur — sie hängen ohne eigene Lage
 * in deren Gruppe und wandern mit, wenn die Figur neu gebaut wird (`anhaengen`).
 *
 * `art`: `{name, datei: ergebnis => {datei, bytes, fehler}, karten}`. Karten tragen ein Deckkraftbild
 * (glTF `MASK`): `alphaToCoverage` statt harter Kante — genesis9-inhalte.md, Kin: „alphaTest 0.3 machte
 * krebskranke Haare".
 *
 * SICHTBAR JE NETZ, NICHT JE GRUPPE: Der Export (`Modellexportinhalt.objekte`) fragt `mesh.visible`; eine
 * ausgeblendete Gruppe mit sichtbaren Netzen darin ging mit in die GLB (bis 29.09.2026 beim Schalter „Haar").
 */
export class Meshfigurhaarobjekt {

    constructor(seite, melden, art) {
        this.seite = seite;
        this.melden = melden;
        this.art = art;
        this.objekt = null;
        this.gruppe = null;
        this.an = false;
        this.vorhanden = false;
        this._stand = null;
    }

    /** Laden, wenn sich die Datei geändert hat; `gruppe` = die Gruppe der Figur (oder null). */
    zeigen(z, gruppe) {
        const o = this.art.datei(z.ergebnis || {}) || {};
        this.vorhanden = Boolean(o.datei);
        if (o.fehler) this.melden(`${this.art.name}: ${o.fehler}`);
        if (!o.datei) return;
        const stand = JSON.stringify([o.datei, o.bytes, o.flaechen, o.punkte]);
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
        this.sichtbar(this.an);
    }

    sichtbar(an) {
        this.an = an;
        this.objekt?.traverse(o => { if (o.isMesh) o.visible = an; });
    }

    _laden(adresse) {
        new GLTFLoader().load(adresse, gltf => {
            const neu = gltf.scene;
            neu.name = this.art.name;
            neu.traverse(o => {
                for (const m of [].concat(o.material || [])) {
                    m.side = THREE.DoubleSide;
                    m.metalness = 0;
                    if (this.art.karten && m.map) m.alphaToCoverage = true;
                }
            });
            if (this.objekt) {
                this.objekt.parent?.remove(this.objekt);
                this.objekt.traverse(o => { o.geometry?.dispose?.(); });
            }
            this.objekt = neu;
            if (this.gruppe) this.anhaengen(this.gruppe);
        }, undefined, fehler => this.melden(`${this.art.name} nicht geladen: ${fehler.message || fehler}`));
    }
}
