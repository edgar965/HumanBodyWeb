import * as THREE from 'three';
import { _makeDoubleSided, _mergeSimpleGeos } from './formenbauer.js';

/**
 * Wendelband — ein durchgehendes Band, das sich wie ein Korkenzieher nach unten
 * windet. Es hat eine Breite (innere zur äußeren Kante) und eine Dicke, die
 * äußere Kante darf hängen.
 *
 * Je Schritt entstehen vier Eckpunkte in dieser Reihenfolge:
 *
 *     0 außen oben   1 innen oben
 *     3 außen unten  2 innen unten
 *
 * Aus formen_band.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`:
 * `_buildHelixRibbon()` hatte 90 Zeilen).
 */
export class Wendelband {
    /** Mindestzahl der Schritte, damit die Wendel rund wirkt. */
    static MINDESTSCHRITTE = 48;
    /** Schritte je Windung. */
    static SCHRITTE_JE_WINDUNG = 64;
    /** Kleinster zulässiger Innenradius in Metern. */
    static MINDESTRADIUS = 0.002;
    /** Kleinster Innenradius des Unterrocks. */
    static MINDESTRADIUS_ROCK = 0.003;
    /** Segmente des Unterrocks. */
    static ROCKSEGMENTE = 48;

    /**
     * @param {Object} part Formbeschreibung aus der Konfiguration
     * @param {number} radius Grundradius des Knochens
     */
    constructor(part, radius) {
        this.windungen = part.spiralWinds ?? 3;
        this.startRadius = part.spiralStartR ?? radius * 0.5;
        this.endRadius = part.spiralEndR ?? radius;
        this.oben = part.spiralPosTop ?? 0.05;
        this.unten = part.spiralPosBottom ?? -0.15;
        this.bandbreite = part.ribbonWidth ?? 0.04;
        this.dicke = part.tutuThickness ?? 0.005;
        this.haengen = part.tutuDroop ?? 0.015;
        this.mitRock = !!part.spiralSkirt;
        this.schritte = Math.max(
            Wendelband.MINDESTSCHRITTE,
            Math.round(this.windungen * Wendelband.SCHRITTE_JE_WINDUNG));
    }

    /**
     * @param {Object} part
     * @param {number} radius
     * @returns {THREE.BufferGeometry}
     */
    static bauen(part, radius) {
        return new Wendelband(part, radius).geometrie();
    }

    geometrie() {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position',
                         new THREE.BufferAttribute(this._punkte(), 3));
        geo.setIndex(new THREE.BufferAttribute(this._flaechen(), 1));
        geo.computeVertexNormals();
        const band = _makeDoubleSided(geo);
        return this.mitRock ? _mergeSimpleGeos(band, this._rock()) : band;
    }

    /** Vier Eckpunkte je Schritt. */
    _punkte() {
        const feld = new Float32Array((this.schritte + 1) * 4 * 3);
        const gesamtwinkel = this.windungen * Math.PI * 2;
        const gesamthoehe = this.oben - this.unten;
        const halbeDicke = this.dicke * 0.5;
        for (let i = 0; i <= this.schritte; i++) {
            const t = i / this.schritte;
            const winkel = t * gesamtwinkel;
            const y = this.oben - t * gesamthoehe;
            const r = this.startRadius + t * (this.endRadius - this.startRadius);
            const cos = Math.cos(winkel);
            const sin = Math.sin(winkel);
            const innen = Math.max(Wendelband.MINDESTRADIUS,
                                   r - this.bandbreite * 0.5);
            const aussen = r + this.bandbreite * 0.5;
            const s = i * 4 * 3;
            feld[s] = aussen * cos;                       // 0 außen oben
            feld[s + 1] = y - this.haengen + halbeDicke;
            feld[s + 2] = aussen * sin;
            feld[s + 3] = innen * cos;                    // 1 innen oben
            feld[s + 4] = y + halbeDicke;
            feld[s + 5] = innen * sin;
            feld[s + 6] = innen * cos;                    // 2 innen unten
            feld[s + 7] = y - halbeDicke;
            feld[s + 8] = innen * sin;
            feld[s + 9] = aussen * cos;                   // 3 außen unten
            feld[s + 10] = y - this.haengen - halbeDicke;
            feld[s + 11] = aussen * sin;
        }
        return feld;
    }

    /** Vier Vierecke je Schritt: oben, unten, Außen- und Innenkante. */
    _flaechen() {
        const feld = new Uint32Array(this.schritte * 4 * 2 * 3);
        let f = 0;
        const viereck = (a, b, c, d) => {
            feld[f++] = a; feld[f++] = b; feld[f++] = c;
            feld[f++] = a; feld[f++] = c; feld[f++] = d;
        };
        for (let i = 0; i < this.schritte; i++) {
            const a = i * 4;
            const b = (i + 1) * 4;
            viereck(a, b, b + 1, a + 1);              // oben
            viereck(a + 2, b + 2, b + 3, a + 3);      // unten
            viereck(a, a + 3, b + 3, b);              // Außenkante
            viereck(a + 1, b + 1, b + 2, a + 2);      // Innenkante
        }
        return feld;
    }

    /** Unterrock: ein Kegelstumpf innerhalb der Wendel. */
    _rock() {
        const obenInnen = Math.max(Wendelband.MINDESTRADIUS_ROCK,
                                   this.startRadius - this.bandbreite * 0.5);
        const untenInnen = Math.max(Wendelband.MINDESTRADIUS_ROCK,
                                    this.endRadius - this.bandbreite * 0.5);
        const punkte = [
            new THREE.Vector2(obenInnen + this.dicke, this.oben),
            new THREE.Vector2(untenInnen + this.dicke, this.unten),
            new THREE.Vector2(untenInnen, this.unten),
            new THREE.Vector2(obenInnen, this.oben),
        ];
        return _makeDoubleSided(
            new THREE.LatheGeometry(punkte, Wendelband.ROCKSEGMENTE));
    }
}
