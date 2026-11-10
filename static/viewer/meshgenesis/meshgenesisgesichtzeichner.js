/**
 * Meshgenesisgesichtzeichner — zeichnet die Gesichts-Zeile der Seite „Mesh-Genesis“ (14.10.2026): ein Kopf-Ellipsoid mit Nase in der Kopfhaltung der Pose, dazu Landmarken und Linienzüge (Kontur, Brauen, Augen, Nase, Mund).
 * Eingabe = die Außenfläche des Kopfes (Dummy: Ellipsoid mit Nase), gewünschte Ausgabe = Schale mit Landmarken, Ausgabe des Netzes = orange Schale, Landmarken und Linien in Orange, gefärbt nach dem Fehler je Punkt
 * (grün 0 mm bis rot ab `fehler_rot_mm`), auf Wunsch mit dem Soll als Drahtgitter-Geist. Die Ansichtsart (`d.modus`, `Meshgenesismaterial`) wählt, wie die Schale aussieht; „Punkte / Gerüst“ lässt sie weg und zeigt in der Eingabe
 * die Punktwolke, sonst nur Landmarken und Linien. Alles Dummy: das Gesicht ist erfunden und in jeder Probe dasselbe, nur die Haltung wechselt.
 */
import * as THREE from 'three';
import { Meshgenesisechtzeichner } from './meshgenesisechtzeichner.js';
import { Meshgenesiskapseln } from './meshgenesiskapseln.js';
import { Meshgenesismaterial } from './meshgenesismaterial.js';

export class Meshgenesisgesichtzeichner {
    static HAUT = 0xe0b394;
    static LINIE = 0x3a2a22;
    static GRUPPENFARBE = { Kontur: 0xf2f2f2, Brauen: 0x6b4a2f, Augen: 0x3b6ea5, Nase: 0xb98a6a, Mund: 0xc2605f };
    static PUNKTRADIUS = 0.0034;
    static ROHRRADIUS = 0.0012;
    static NASENRADIUS = 0.012;
    /** Punkte auf der Nase zusätzlich zu denen des Ellipsoids. */
    static NASENPUNKTE = 160;

    /** Matrix aus Drehung (9 Zahlen, Zeilen) und Halbachsen: Spalte j mal Halbachse j. */
    static _matrix(drehung, radien) {
        const r = drehung;
        return new THREE.Matrix4().set(r[0] * radien[0], r[1] * radien[1], r[2] * radien[2], 0, r[3] * radien[0], r[4] * radien[1], r[5] * radien[2], 0,
            r[6] * radien[0], r[7] * radien[1], r[8] * radien[2], 0, 0, 0, 0, 1);
    }

    static _punkt(beschreibung, lagen, name) {
        return new THREE.Vector3().fromArray(lagen[beschreibung.punkte.findIndex(p => p.name === name)]);
    }

    /** Kopf-Ellipsoid und Nasenrücken in der gewählten Ansichtsart; `faktor` > 1 legt den Geist knapp über die Schale (sonst flackern beide). */
    _huelle(beschreibung, teil, lagen, stil, faktor = 1) {
        const z = Meshgenesisgesichtzeichner;
        const gruppe = new THREE.Group();
        const schale = Meshgenesismaterial.netz(Meshgenesiskapseln.kugelgeometrie(1, 40, 28), { ...stil, sollfarbe: z.HAUT, gruppe: 'haut' });
        schale.matrixAutoUpdate = false;
        schale.matrix.copy(z._matrix(teil.huelle.drehung, beschreibung.huelle.radien.map(r => r * faktor)));
        gruppe.add(schale);
        if (!stil.wand) {
            const wurzel = z._punkt(beschreibung, lagen, 'Nasenwurzel');
            const spitze = z._punkt(beschreibung, lagen, 'Nasenspitze');
            const laenge = wurzel.distanceTo(spitze);
            const nase = Meshgenesismaterial.netz(Meshgenesiskapseln.kapselgeometrie(z.NASENRADIUS, Math.max(laenge - 2 * z.NASENRADIUS, 0.002)), { ...stil, sollfarbe: z.HAUT, gruppe: 'haut' });
            nase.position.copy(wurzel).add(spitze).multiplyScalar(0.5);
            nase.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), spitze.clone().sub(wurzel).normalize());
            gruppe.add(nase);
        }
        return gruppe;
    }

    /** Landmarken als Kugeln (Farbe nach Gruppe oder nach Fehler) und die Linienzüge als Rohre. */
    _landmarken(inhalt, beschreibung, lagen, farbe, linienfarbe) {
        const z = Meshgenesisgesichtzeichner;
        const kugel = Meshgenesiskapseln.kugelgeometrie(z.PUNKTRADIUS);
        beschreibung.punkte.forEach((p, i) => {
            const punkt = new THREE.Mesh(kugel, Meshgenesiskapseln.basismaterial(farbe(p, i)));
            punkt.position.fromArray(lagen[i]);
            inhalt.add(punkt);
        });
        const material = Meshgenesiskapseln.basismaterial(linienfarbe);
        for (const zug of beschreibung.linien) {
            for (let k = 0; k + 1 < zug.length; k++) {
                inhalt.add(Meshgenesiskapseln.rohr(new THREE.Vector3().fromArray(lagen[zug[k]]), new THREE.Vector3().fromArray(lagen[zug[k + 1]]), z.ROHRRADIUS, material));
            }
        }
    }

    /** Dummy der Außenfläche: Punkte gleichmäßig in den Winkeln auf dem Ellipsoid, dazu einige um den Nasenrücken. */
    _punktwolke(beschreibung, teil, samen) {
        const z = Meshgenesisgesichtzeichner;
        const zufall = Meshgenesiskapseln.zufall(samen * 7919 + 31);
        const m = z._matrix(teil.huelle.drehung, beschreibung.huelle.radien);
        const n = teil.eingabe.punkte;
        const lage = new Float32Array((n + z.NASENPUNKTE) * 3);
        const v = new THREE.Vector3();
        for (let i = 0; i < n; i++) {
            const h = 2 * zufall() - 1, w = zufall() * Math.PI * 2, s = Math.sqrt(1 - h * h);
            v.set(s * Math.cos(w), h, s * Math.sin(w)).applyMatrix4(m).toArray(lage, i * 3);
        }
        const wurzel = z._punkt(beschreibung, teil.soll, 'Nasenwurzel');
        const achse = z._punkt(beschreibung, teil.soll, 'Nasenspitze').sub(wurzel);
        for (let i = 0; i < z.NASENPUNKTE; i++) {
            v.copy(wurzel).addScaledVector(achse, zufall()).add(new THREE.Vector3(zufall() - 0.5, zufall() - 0.5, zufall() - 0.5).multiplyScalar(0.022)).toArray(lage, (n + i) * 3);
        }
        return Meshgenesiskapseln.punkte(lage, 0.0035);
    }

    zeichnen(inhalt, art, d) {
        // Echte Daten (15.10.2026): der Kopf der gehäuteten Figur und sein Rig (`Meshgenesisechtzeichner`), keine Dummy-Landmarken.
        if (d.echt) {
            Meshgenesisechtzeichner.zeichnen(inhalt, art, d);
            return;
        }
        const z = Meshgenesisgesichtzeichner;
        const { beschreibung, teil } = d;
        const gerippe = d.modus === 'punkte';
        if (art === 'eingabe') {
            inhalt.add(gerippe ? this._punktwolke(beschreibung, teil, d.id) : this._huelle(beschreibung, teil, teil.soll, { modus: d.modus }));
        } else if (art === 'soll') {
            if (!gerippe) inhalt.add(this._huelle(beschreibung, teil, teil.soll, { modus: d.modus }));
            this._landmarken(inhalt, beschreibung, teil.soll, p => z.GRUPPENFARBE[p.gruppe] ?? 0xffffff, gerippe ? Meshgenesismaterial.heller(z.LINIE, 0.7) : z.LINIE);
        } else {
            const je = teil.kennzahlen.je_gelenk_mm;
            if (!gerippe) {
                if (d.geist) inhalt.add(this._huelle(beschreibung, teil, teil.soll, { wand: true }, 1.01));
                inhalt.add(this._huelle(beschreibung, teil, teil.ausgabe, { modus: d.modus, tint: Meshgenesiskapseln.AUSGABEFARBE, deckkraft: 0.8 }));
            }
            this._landmarken(inhalt, beschreibung, teil.ausgabe, (p, i) => Meshgenesiskapseln.fehlerfarbeStufe(je[i], beschreibung.fehler_rot_mm), Meshgenesiskapseln.AUSGABEFARBE);
        }
    }
}
