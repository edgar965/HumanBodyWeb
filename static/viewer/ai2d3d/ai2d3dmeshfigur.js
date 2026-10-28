/**
 * Ai2d3dmeshfigur — Feld 3 der Mesh-Zeile der Jobseite: die Genesis-Figur, die `Genesis9.meshgenesis` in die geometrische Figur eingepasst hat (28.10.2026, Edgar: „eine extra Zeile
 * ganz oben … das dritte Bild mit dem Mesh Modell anstelle von Genesis“).
 *
 * Daten: `genesis` in `<Job>/abnahme/training_figur.json` (`mesh_auf_genesis.py`, `figur_eintragen`): je Foto die Punkte der Figur in dessen Haltung, Dreiecke des Käfigs, Zahlen
 * der Einpassung (`masse`). Die Daten teilt sich der Zeichner mit `Ai2d3dtrainingfigur` (ein Abruf). Ansichtsarten wie die anderen Felder (Ersatzmaterial auf Ebene 1); „Textur“
 * zeigt die Oberfläche — die Figur trägt keine Farben.
 */
import * as THREE from 'three';
import { Ai2d3dnetz } from './ai2d3dnetz.js';
import { Ai2d3dtrainingfigur } from './ai2d3dtrainingfigur.js';

export class Ai2d3dmeshfigur {
    /** @param {Ai2d3dtrainingfigur} quelle der Zeichner der geometrischen Figur (dieselbe Datei) */
    constructor(quelle) {
        this.quelle = quelle;
        this.bereit = quelle.bereit;
        this._netze = new Map();
    }

    get daten() {
        return this.quelle.daten;
    }

    /** Zahlen der Einpassung (`masse` des Laufs) oder null. */
    get masse() {
        return this.daten?.genesis?.masse ?? null;
    }

    _netz(nr) {
        const g = this.daten?.genesis, punkte = g?.fotos?.[String(nr + 1)];
        if (!punkte) return null;
        if (this._netze.has(nr)) return this._netze.get(nr);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(Ai2d3dtrainingfigur._feld(punkte, Float32Array), 3));
        geo.setIndex(new THREE.BufferAttribute(Ai2d3dtrainingfigur._feld(g.dreiecke, Uint32Array), 1));
        geo.computeVertexNormals();
        const netz = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0xc8c8c8, roughness: 1, metalness: 0 }));
        netz.layers.set(1);                       // Ebene 1: die Ansichtsart zeichnet mit ihrem Ersatzmaterial (`Mesh3daiansicht._malen`)
        netz.frustumCulled = false;
        netz.userData.mesh3daiFremd = true;       // gehört dem Zeichner, nicht dem Feld
        this._netze.set(nr, netz);
        return netz;
    }

    /** Zeichner von `Mesh3daiansicht`: `d = {nr, modus}`. */
    zeichnen(inhalt, _art, d) {
        if (!this.daten) {
            inhalt.userData.hinweis = this.quelle.fehler ? `Figur nicht geladen: ${this.quelle.fehler}` : 'Figur wird geladen …';
            return;
        }
        const netz = this._netz(d.nr);
        if (!netz) {
            inhalt.userData.hinweis = 'Noch keine Genesis-Figur aus der Mesh-Methode für dieses Foto (mesh_auf_genesis.py).';
            return;
        }
        inhalt.add(netz);
        inhalt.userData.genesisErsatz = Ai2d3dnetz.ersatz(d.modus === 'textur' ? 'oberflaeche' : d.modus);
    }
}
