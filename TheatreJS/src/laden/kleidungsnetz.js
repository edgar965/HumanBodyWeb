import * as THREE from 'three';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords }
    from '../../../static/viewer/gemeinsam/kodierung.js';
import { Koerperfrage } from './koerperfrage.js';

/**
 * Kleidungsnetz — ein Kleidungsstück vom Server anpassen lassen und aufbauen.
 *
 * Aus asset-loader.js herausgeloest (Umbau 16.08.2026): 97 Zeilen in einer
 * Funktion, die vier Dinge auf einmal tat — Farbe deuten, Anfrage bauen, Netz
 * aufbauen, Kenndaten anhängen. Jeder Schritt ist jetzt eine Methode.
 *
 * Der Server passt das Kleidungsstück an den MORPHTEN Körper an, deshalb gehen
 * Morph- und Meta-Werte mit in die Anfrage. Fehlen sie, sitzt das Kleid am
 * Standardkörper und schwebt oder schneidet ein.
 */
export class Kleidungsnetz {

    static ENDPUNKT = '/api/character/garment/fit/';
    static VORGABE_FARBE = [0.3, 0.35, 0.5];

    /**
     * @param {Object} kleid    Angaben aus der Vorgabe (id, offset, stiffness, …)
     * @param {string} koerper  Körpertyp
     * @param {Object} vorgabe  ganze Vorgabe — fuer Morph- und Meta-Werte
     */
    constructor(kleid, koerper, vorgabe = {}) {
        this.kleid = kleid;
        this.koerper = koerper || 'Female_Caucasian';
        this.vorgabe = vorgabe;
    }

    /** Kurzform: anpassen lassen und Netz zurückgeben. */
    static async laden(kleid, koerper, vorgabe = {}) {
        return new Kleidungsnetz(kleid, koerper, vorgabe).netz();
    }

    async netz() {
        const antwort = await fetch(Kleidungsnetz.ENDPUNKT + '?' + this.frage());
        if (!antwort.ok) throw new Error('Garment-fit-API: ' + antwort.status);
        const daten = await antwort.json();
        if (daten.error) throw new Error(daten.error);
        return this.aufbauen(daten);
    }

    // ------------------------------------------------------------------ Anfrage

    /** Farbe aus Zahlenfeld ODER Zeichenkette lesen. */
    farbe() {
        const wert = this.kleid.color ?? Kleidungsnetz.VORGABE_FARBE;
        if (Array.isArray(wert)) {
            return Kleidungsnetz.VORGABE_FARBE.map((ersatz, i) => wert[i] ?? ersatz);
        }
        if (typeof wert === 'string') {
            const farbe = new THREE.Color(wert);
            return [farbe.r, farbe.g, farbe.b];
        }
        return [...Kleidungsnetz.VORGABE_FARBE];
    }

    frage() {
        const { id, offset = 0.006, stiffness = 0.8 } = this.kleid;
        const [r, g, b] = this.farbe();
        // Morphs und Meta-Werte kommen aus Koerperfrage — dieselbe Frage
        // brauchen auch das Netz der Figur und das Nachladen im Figurpanel.
        const frage = new Koerperfrage(
            { ...this.vorgabe, body_type: this.koerper }).felder();
        frage.set('garment_id', id);
        frage.set('offset', String(offset));
        frage.set('stiffness', String(stiffness));
        frage.set('color_r', r.toFixed(3));
        frage.set('color_g', g.toFixed(3));
        frage.set('color_b', b.toFixed(3));
        return frage.toString();
    }

    // ------------------------------------------------------------------ Aufbau

    aufbauen(daten) {
        const geo = this._geometrie(daten);
        const netz = this._netzArt(geo, daten, this._stoff(daten));
        netz.castShadow = true;
        netz.receiveShadow = true;
        this._kenndatenAnhaengen(netz);
        return netz;
    }

    _geometrie(daten) {
        const punkte = blenderToThreeCoords(base64ToFloat32(daten.vertices));
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        geo.setIndex(new THREE.BufferAttribute(base64ToUint32(daten.faces), 1));
        geo.computeVertexNormals();
        return geo;
    }

    _stoff(daten) {
        const [r, g, b] = daten.color;
        return new THREE.MeshStandardMaterial({
            color: new THREE.Color(r, g, b),
            roughness: this.kleid.roughness ?? 0.8,
            metalness: this.kleid.metalness ?? 0,
            side: THREE.DoubleSide,
            // Ohne den Versatz flackert das Kleid gegen die Haut darunter.
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnit: -1,
        });
    }

    /**
     * Mit Hautgewichten wird es ein SkinnedMesh — dann muss es spaeter ans
     * Skelett gebunden werden (`needsBinding`, siehe Skinner).
     */
    _netzArt(geo, daten, stoff) {
        if (!daten.skin_indices || !daten.skin_weights) {
            return new THREE.Mesh(geo, stoff);
        }
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(
            base64ToFloat32(daten.skin_indices), 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(
            base64ToFloat32(daten.skin_weights), 4));
        const netz = new THREE.SkinnedMesh(geo, stoff);
        netz.userData.needsBinding = true;
        return netz;
    }

    /** Werte, die das Kleiderpanel spaeter wieder anzeigt. */
    _kenndatenAnhaengen(netz) {
        const { id, offset = 0.006, stiffness = 0.8 } = this.kleid;
        Object.assign(netz.userData, {
            garmentId: id, offset, stiffness,
            originalColor: this.farbe(),
            roughness: this.kleid.roughness ?? 0.8,
            metalness: this.kleid.metalness ?? 0,
        });
        netz.name = id;
    }
}
