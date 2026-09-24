import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Mimikbasis — die Posenbibliothek und die Rechnung Gewichte → Knochen.
 *
 * Lädt einmal `static/mimik/basis.json` (Einheit → Knochenbewegung für +1 und
 * −1, aus `manage.py mimik_vorbereiten`) und `posen.json` (78 MB-Lab-Posen
 * in zehn Gruppen). Eine Bewegung je Knochen ist `[tx, ty, tz, px, py, pz]`:
 * Drehvektor (rad, Knochenraum) und Versatz (m, Elternraum), Three.js-Achsen.
 * Gewichte werden linear gemischt — kleine Drehungen addieren sich als
 * Vektoren, erst am Ende wird daraus ein Quaternion.
 */
export class Mimikbasis {
    static BASIS = '/static/mimik/basis.json';
    static POSEN = '/static/mimik/posen.json';
    static VORSCHAU = '/static/mimik/vorschau/';

    static basis = null;
    static posen = [];
    static gruppen = [];
    static _lader = null;

    /** Beide Dateien holen (einmal); danach `basis`, `posen`, `gruppen` gefüllt. */
    static laden() {
        if (!Mimikbasis._lader) {
            Mimikbasis._lader = Promise.all([
                Serverabruf.json(Mimikbasis.BASIS),
                Serverabruf.json(Mimikbasis.POSEN),
            ]).then(([basis, posen]) => {
                Mimikbasis.basis = basis;
                Mimikbasis.posen = posen.posen || [];
                Mimikbasis.gruppen = posen.gruppen || [];
                Mimikbasis.eigeneLaden();
                return Mimikbasis;
            });
        }
        return Mimikbasis._lader;
    }

    static get bereit() { return !!Mimikbasis.basis; }

    /** Die Pose zu einer Kennung — aus der Bibliothek oder den eigenen. */
    static pose(id) {
        return Mimikbasis.posen.find(p => p.id === id) || null;
    }

    /** Alle Knochen, die irgendeine Einheit bewegt — sie werden je Bild gesetzt. */
    static knochen() {
        if (!Mimikbasis._knochen && Mimikbasis.basis) {
            const namen = new Set();
            for (const einheit of Object.values(Mimikbasis.basis)) {
                for (const richtung of Object.values(einheit)) {
                    for (const name of Object.keys(richtung)) namen.add(name);
                }
            }
            Mimikbasis._knochen = [...namen];
        }
        return Mimikbasis._knochen || [];
    }

    /**
     * Gewichte → `{knochen: {rot: THREE.Quaternion, pos: THREE.Vector3}}`.
     * Positive Gewichte nehmen `plus`, negative `minus` (MB-Labs _max/_min).
     */
    static bewegungen(gewichte) {
        /** @type {Object<string, number[]>} */
        const summe = {};
        for (const [einheit, g] of Object.entries(gewichte || {})) {
            const eintrag = Mimikbasis.basis?.[einheit];
            if (!eintrag || !g) continue;
            const richtung = g > 0 ? eintrag.plus : eintrag.minus;
            const betrag = Math.abs(g);
            for (const [knochen, w] of Object.entries(richtung)) {
                const s = summe[knochen] || (summe[knochen] = [0, 0, 0, 0, 0, 0]);
                for (let i = 0; i < 6; i++) s[i] += w[i] * betrag;
            }
        }
        /** @type {Object<string, {rot: THREE.Quaternion, pos: THREE.Vector3}>} */
        const aus = {};
        for (const [knochen, s] of Object.entries(summe)) {
            const achse = new THREE.Vector3(s[0], s[1], s[2]);
            const winkel = achse.length();
            const rot = winkel > 1e-9
                ? new THREE.Quaternion().setFromAxisAngle(achse.divideScalar(winkel), winkel)
                : new THREE.Quaternion();
            aus[knochen] = { rot, pos: new THREE.Vector3(s[3], s[4], s[5]) };
        }
        return aus;
    }

    // ------------------------------------------------------------ eigene Posen
    static EIGENE = 'bvh_studio_mimik_eigene';

    static eigeneLaden() {
        try {
            const eigene = JSON.parse(localStorage.getItem(Mimikbasis.EIGENE) || '[]');
            Mimikbasis.posen = Mimikbasis.posen.filter(p => p.gruppe !== 'eigene').concat(eigene);
        } catch (_fehler) {
            // stumm gewollt: kein Browserspeicher heißt keine eigenen Posen
        }
    }

    /** Eine eigene Pose (Gruppe „Eigene") merken — ersetzt eine gleichnamige. */
    static eigeneSpeichern(name, gewichte) {
        const id = 'eigene_' + name.toLowerCase().replace(/[^a-z0-9]+/g, '_');
        const pose = { id, name, gruppe: 'eigene', gewichte };
        const eigene = Mimikbasis.posen.filter(p => p.gruppe === 'eigene' && p.id !== id);
        eigene.push(pose);
        try {
            localStorage.setItem(Mimikbasis.EIGENE, JSON.stringify(eigene));
        } catch (_fehler) {
            // stumm gewollt: ohne Browserspeicher bleibt die Pose nur in dieser Sitzung
        }
        Mimikbasis.posen = Mimikbasis.posen.filter(p => p.gruppe !== 'eigene').concat(eigene);
        return pose;
    }
}
