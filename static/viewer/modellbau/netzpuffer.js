import * as THREE from 'three';

/**
 * Die Zielpuffer der Netzverschmelzung — alle Stücke in einem Satz Feldern.
 *
 * Die Größe steht vor dem ersten Anfügen fest (`vorbereiten`), damit die
 * typisierten Felder genau einmal angelegt werden. `anfuegen()` kopiert ein
 * Stück an die nächste freie Stelle und verschiebt dessen Indizes mit.
 *
 * Aus netzverschmelzung.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`).
 */
export class Netzpuffer {
    /**
     * @param {number} punkte Gesamtzahl der Eckpunkte
     * @param {boolean} mitUV ob eine UV-Ebene gebraucht wird
     */
    constructor(punkte, mitUV) {
        this.positionen = new Float32Array(punkte * 3);
        this.normalen = new Float32Array(punkte * 3);
        this.knochenIndex = new Float32Array(punkte * 4);
        this.knochenGewicht = new Float32Array(punkte * 4);
        this.uvs = mitUV ? new Float32Array(punkte * 2) : null;
        this.indizes = [];
        /** Nächste freie Eckpunktstelle. */
        this.punktstelle = 0;
        /** Anzahl bisher geschriebener Indizes — die Grenze der Zeichengruppen. */
        this.indexstelle = 0;
        /** boneName -> { start, count } */
        this.knochenbereiche = {};
    }

    /**
     * Zählt die Stücke durch und legt die Puffer in der richtigen Größe an.
     * @param {Array} stuecke
     * @returns {Netzpuffer}
     */
    static vorbereiten(stuecke) {
        let punkte = 0;
        let mitUV = false;
        for (const stueck of stuecke) {
            punkte += stueck.geometry.attributes.position.count;
            if (stueck.geometry.attributes.uv || stueck.texture) mitUV = true;
        }
        return new Netzpuffer(punkte, mitUV);
    }

    /**
     * Kopiert ein Geometriestück in die Puffer und gibt dessen Geometrie frei.
     * @param {{geometry, boneName, boneIndex}} stueck
     */
    anfuegen(stueck) {
        const geo = stueck.geometry;
        const anzahl = geo.attributes.position.count;
        if (stueck.boneName) {
            this.knochenbereiche[stueck.boneName] =
                { start: this.punktstelle, count: anzahl };
        }
        this.positionen.set(geo.attributes.position.array, this.punktstelle * 3);
        this.normalen.set(geo.attributes.normal.array, this.punktstelle * 3);
        if (this.uvs && geo.attributes.uv) {
            // Stücke ohne UV behalten die Vorbelegung (0, 0).
            this.uvs.set(geo.attributes.uv.array, this.punktstelle * 2);
        }
        this._haut(stueck.boneIndex, anzahl);
        this._indizes(geo, anzahl);
        this.punktstelle += anzahl;
        geo.dispose();
    }

    /** Starre Bindung: jeder Punkt hängt zu 100 % an genau einem Knochen. */
    _haut(knochenIndex, anzahl) {
        for (let v = 0; v < anzahl; v++) {
            const stelle = (this.punktstelle + v) * 4;
            this.knochenIndex[stelle] = knochenIndex;
            this.knochenIndex[stelle + 1] = 0;
            this.knochenIndex[stelle + 2] = 0;
            this.knochenIndex[stelle + 3] = 0;
            this.knochenGewicht[stelle] = 1;
            this.knochenGewicht[stelle + 1] = 0;
            this.knochenGewicht[stelle + 2] = 0;
            this.knochenGewicht[stelle + 3] = 0;
        }
    }

    _indizes(geo, anzahl) {
        if (geo.index) {
            const feld = geo.index.array;
            for (let i = 0; i < feld.length; i++) {
                this.indizes.push(feld[i] + this.punktstelle);
            }
            this.indexstelle += feld.length;
            return;
        }
        for (let i = 0; i < anzahl; i++) {
            this.indizes.push(this.punktstelle + i);
        }
        this.indexstelle += anzahl;
    }

    /**
     * Die fertige Geometrie mit ihren Zeichengruppen.
     * @param {Array<{start, count, materialIndex}>} zeichengruppen
     * @returns {THREE.BufferGeometry}
     */
    geometrie(zeichengruppen) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position',
            new THREE.Float32BufferAttribute(this.positionen, 3));
        geo.setAttribute('normal',
            new THREE.Float32BufferAttribute(this.normalen, 3));
        if (this.uvs) {
            geo.setAttribute('uv', new THREE.Float32BufferAttribute(this.uvs, 2));
        }
        geo.setAttribute('skinIndex',
            new THREE.Float32BufferAttribute(this.knochenIndex, 4));
        geo.setAttribute('skinWeight',
            new THREE.Float32BufferAttribute(this.knochenGewicht, 4));
        geo.setIndex(this.indizes);
        for (const gruppe of zeichengruppen) {
            geo.addGroup(gruppe.start, gruppe.count, gruppe.materialIndex);
        }
        return geo;
    }
}
