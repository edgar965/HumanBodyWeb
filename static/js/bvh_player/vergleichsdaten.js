/**
 * Vergleichsdaten — 2D-Keypoints und 3D-Knochen auf ein gemeinsames Mass bringen.
 *
 * Aus `updateDebugOverlay` in bvh_player.js herausgeloest (Umbau 16.08.2026).
 *
 * Beide Seiten werden auf das Becken bezogen und mit dem Abstand Becken→Hals
 * skaliert; erst dann sind Bildpunkte und Weltkoordinaten vergleichbar. Die
 * 3D-Y-Achse wird gespiegelt, weil Bildkoordinaten nach unten zaehlen.
 *
 * WAS DABEI AUFFIEL: Die Vorlage rechnete den Beckenabstand der 2D-Punkte in
 * einer ZWEITEN Schleife noch einmal aus (`vidDist`) — dabei ist er nichts
 * anderes als die Laenge des schon normierten Vektors. Zwoelf Zeilen und ein
 * Durchlauf weniger, gleiches Ergebnis.
 */
import * as THREE from 'three';
import { SMPL_ELTERN } from './skelettformate.js';

/** Kleinster brauchbarer Bezugsabstand Becken→Hals. */
const MIN_2D = 0.001;
const MIN_3D = 0.1;

export class Vergleichsdaten {
    constructor(knochenliste) {
        this.knochenliste = knochenliste;
        this.zweiD = null;
        this.dreiD = null;
        this.roh3d = {};
    }

    /** Beide Seiten neu berechnen. */
    erheben(keypointsBild, skelett) {
        this.zweiD = this._normiert2d(keypointsBild);
        this.roh3d = this._weltpositionen(skelett);
        this.dreiD = this._normiert3d();
        return this;
    }

    _normiert2d(bild) {
        if (!bild?.['Pelvis'] || !bild['Neck']) return null;
        const [px, py] = bild['Pelvis'];
        const [nx, ny] = bild['Neck'];
        const bezug = Math.hypot(nx - px, ny - py);
        if (bezug <= MIN_2D) return null;
        const aus = {};
        for (const name of this.knochenliste) {
            const p = bild[name];
            if (p) aus[name] = [(p[0] - px) / bezug, (p[1] - py) / bezug];
        }
        return aus;
    }

    _weltpositionen(skelett) {
        const aus = {};
        for (const name of this.knochenliste) {
            const p = skelett.position(name, new THREE.Vector3());
            if (p) aus[name] = p;
        }
        return aus;
    }

    _normiert3d() {
        const becken = this.roh3d['Pelvis'], hals = this.roh3d['Neck'];
        if (!becken || !hals) return null;
        const bezug = becken.distanceTo(hals);
        if (bezug <= MIN_3D) return null;
        const aus = {};
        for (const name of this.knochenliste) {
            const p = this.roh3d[name];
            // Y gespiegelt: Bildkoordinaten zaehlen nach unten.
            if (p) aus[name] = [(p.x - becken.x) / bezug, -(p.y - becken.y) / bezug];
        }
        return aus;
    }

    /** Abstand vom Becken — die Laenge des normierten Vektors. */
    static abstand(normiert, name) {
        const v = normiert?.[name];
        return v ? Math.hypot(v[0], v[1]) : null;
    }

    /** Winkel Elter→Knochen gegen die Senkrechte, in Grad (0 = unten). */
    static winkel(normiert, name) {
        const elter = SMPL_ELTERN[name];
        if (!normiert || !elter || !normiert[name] || !normiert[elter]) return null;
        const dx = normiert[name][0] - normiert[elter][0];
        const dy = normiert[name][1] - normiert[elter][1];
        return Math.atan2(dx, dy) * (180 / Math.PI);
    }

    /** Laenge des Abschnitts Elter→Knochen im normierten Mass. */
    static abschnitt(normiert, name) {
        const elter = SMPL_ELTERN[name];
        if (!normiert || !elter || !normiert[name] || !normiert[elter]) return null;
        return Math.hypot(normiert[name][0] - normiert[elter][0],
                          normiert[name][1] - normiert[elter][1]);
    }

    /** Hoehenunterschied zweier Knochen, als Pfeil mit Betrag. */
    static gefaelle(normiert, oben, unten) {
        if (!normiert?.[oben] || !normiert[unten]) return '—';
        const dy = normiert[unten][1] - normiert[oben][1];
        return dy > 0 ? `↓${dy.toFixed(2)}` : `↑${(-dy).toFixed(2)}`;
    }
}
