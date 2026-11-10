/**
 * Meshgenesiskapseln — Werkzeug der Zeichner auf der Seite „Mesh-Genesis“ (14.10.2026): Kapseln um die Knochen eines Gerüsts, Punktwolke auf diesen Kapseln, Fehlerpunkte und Rohre.
 * Gebraucht von `Meshgenesiskapselzeichner` (ganzer Körper, Hände/Füße, Kleider) und `Meshgenesisgesichtzeichner`. Eine Beschreibung ist `[{name, gruppe, eltern (Index oder −1), radius?, farbe?}]`;
 * `radius` und `farbe` aus dem Server gelten vor den Tabellen hier (der ganze Körper führt keine und fällt auf die Tabellen zurück).
 */
import * as THREE from 'three';
import { Meshgenesisgemeinsam } from './meshgenesisgemeinsam.js';
import { Meshgenesismaterial } from './meshgenesismaterial.js';

export class Meshgenesiskapseln {
    /** Farben des Soll je Gruppe des Körpergerüsts (Oberteil, Haut, Hose, Schuhe) — Dummy-Farben. */
    static SOLLFARBEN = { rumpf: 0x3b6ea5, arm: 0x3b6ea5, kopf: 0xe0b394, hand: 0xe0b394, bein: 0x2b2f3a, fuss: 0x1c1f27 };
    static AUSGABEFARBE = 0xf08a3c;
    static GEISTFARBE = 0xcfd6e4;
    static PUNKTFARBE = 0x9fb4d1;
    /** Dicke der Kapsel um den Knochen, der am Gelenk endet (m): nach Name, sonst nach Gruppe. */
    static RADIUS_NAME = { Scheitel: 0.085, Kopf: 0.050, Hals: 0.045, Brust: 0.115, Bauch: 0.105 };
    static RADIUS_GRUPPE = { rumpf: 0.100, kopf: 0.050, arm: 0.040, hand: 0.030, bein: 0.065, fuss: 0.040 };

    /** Knochen = (Elterngelenk → Gelenk) mit der Dicke und Farbe des Gelenks. */
    static knochen(gelenke, lagen) {
        const liste = [];
        gelenke.forEach((g, i) => {
            if (g.eltern < 0) return;
            const a = new THREE.Vector3().fromArray(lagen[g.eltern]);
            const b = new THREE.Vector3().fromArray(lagen[i]);
            liste.push({ a, b, gruppe: g.gruppe, textur: g.textur ?? g.gruppe, farbe: g.farbe, radius: g.radius ?? Meshgenesiskapseln.RADIUS_NAME[g.name] ?? Meshgenesiskapseln.RADIUS_GRUPPE[g.gruppe] });
        });
        return liste;
    }

    /** Geteilte Geometrien und Materialien (`Meshgenesisgemeinsam`): dieselbe Kapsel, Kugel oder Röhre wird von Bild zu Bild wieder hergegeben, statt neu hochgeladen zu werden. */
    static kapselgeometrie(radius, laenge) {
        const g = Meshgenesisgemeinsam;
        return g.geometrie(`kapsel:${radius.toFixed(4)}:${g.laenge(laenge)}`, () => new THREE.CapsuleGeometry(radius, laenge, 4, 10));
    }

    static kugelgeometrie(radius, breite = 10, hoehe = 8) {
        return Meshgenesisgemeinsam.geometrie(`kugel:${radius.toFixed(4)}:${breite}:${hoehe}`, () => new THREE.SphereGeometry(radius, breite, hoehe));
    }

    static basismaterial(farbe) {
        const hex = new THREE.Color(farbe).getHex();
        return Meshgenesisgemeinsam.material(`basis:${hex}`, () => new THREE.MeshBasicMaterial({ color: hex }));
    }

    /**
     * Kapseln um die Knochen in der gewählten Ansichtsart (`Meshgenesismaterial`).
     * `stil`: `{modus}` = Farben des Soll; `{modus, tint, deckkraft}` = eingefärbt (Ausgabe des Netzes); `{wand: true}` = Geist als Drahtgitter.
     */
    static geruest(gelenke, lagen, stil = {}) {
        const gruppe = new THREE.Group();
        const hoch = new THREE.Vector3(0, 1, 0);
        for (const k of Meshgenesiskapseln.knochen(gelenke, lagen)) {
            const richtung = new THREE.Vector3().subVectors(k.b, k.a);
            const laenge = richtung.length();
            if (laenge < 1e-4) continue;
            const geo = Meshgenesiskapseln.kapselgeometrie(k.radius, Math.max(laenge - 2 * k.radius, 0.002));
            const kapsel = Meshgenesismaterial.netz(geo, { ...stil, sollfarbe: k.farbe ?? Meshgenesiskapseln.SOLLFARBEN[k.gruppe], gruppe: k.textur });
            kapsel.position.copy(k.a).add(k.b).multiplyScalar(0.5);
            kapsel.quaternion.setFromUnitVectors(hoch, richtung.normalize());
            gruppe.add(kapsel);
        }
        return gruppe;
    }

    /** Ansicht „Punkte / Gerüst“: Kugeln an den Punkten und dünne Rohre von jedem Punkt zu seinem Elternpunkt. `farbe` ersetzt die Farben des Modells; `kugelradius` 0 = nur Linien. */
    static gerippe(gelenke, lagen, { farbe = null, kugelradius = 0.02, rohrradius = 0.004 } = {}) {
        const gruppe = new THREE.Group();
        const kugel = kugelradius > 0 ? Meshgenesiskapseln.kugelgeometrie(kugelradius) : null;
        gelenke.forEach((g, i) => {
            const c = Meshgenesismaterial.heller(farbe ?? g.farbe ?? Meshgenesiskapseln.SOLLFARBEN[g.gruppe] ?? Meshgenesiskapseln.PUNKTFARBE);
            const lage = new THREE.Vector3().fromArray(lagen[i]);
            if (kugel) {
                const punkt = new THREE.Mesh(kugel, Meshgenesiskapseln.basismaterial(c));
                punkt.position.copy(lage);
                gruppe.add(punkt);
            }
            if (g.eltern >= 0) gruppe.add(Meshgenesiskapseln.rohr(new THREE.Vector3().fromArray(lagen[g.eltern]), lage, rohrradius, Meshgenesiskapseln.basismaterial(c)));
        });
        return gruppe;
    }

    /** Ein dünnes Rohr von `a` nach `b` (Linien des Gesichts); `material` wird geteilt. */
    static rohr(a, b, radius, material) {
        const richtung = new THREE.Vector3().subVectors(b, a);
        const laenge = richtung.length();
        const g = Meshgenesisgemeinsam;
        const geo = g.geometrie(`rohr:${radius.toFixed(4)}:${g.laenge(Math.max(laenge, 1e-4))}`, () => new THREE.CylinderGeometry(radius, radius, Math.max(laenge, 1e-4), 6));
        const rohr = new THREE.Mesh(geo, material);
        rohr.position.copy(a).add(b).multiplyScalar(0.5);
        rohr.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), richtung.normalize());
        return rohr;
    }

    /** Fehlerfarbe: grün bei 0 mm bis rot ab `rotMm`. */
    static fehlerfarbe(mm, rotMm) {
        return new THREE.Color().setHSL((1 - Math.min(mm / rotMm, 1)) * 0.33, 0.9, 0.5);
    }

    /** Fehlerfarbe in 24 Stufen (Farbton-Schritt 0,014 ≈ 5°, am Bild nicht zu sehen) — so teilen sich Punkte und Bilder wenige Materialien, statt jedes Mal neue anzulegen. */
    static fehlerfarbeStufe(mm, rotMm) {
        return Meshgenesiskapseln.fehlerfarbe(Math.round(Math.min(mm / rotMm, 1) * 24), 24);
    }

    static fehlerstufe(mm, rotMm) {
        return Meshgenesiskapseln.basismaterial(Meshgenesiskapseln.fehlerfarbeStufe(mm, rotMm));
    }

    /** Kugeln an den Lagen, gefärbt nach dem Fehler je Punkt (`je_mm`). */
    static fehlerpunkte(lagen, jeMm, rotMm, radius) {
        const gruppe = new THREE.Group();
        const kugel = Meshgenesiskapseln.kugelgeometrie(radius, 12, 8);
        lagen.forEach((lage, i) => {
            const punkt = new THREE.Mesh(kugel, Meshgenesiskapseln.fehlerstufe(jeMm[i], rotMm));
            punkt.position.fromArray(lage);
            gruppe.add(punkt);
        });
        return gruppe;
    }

    static zufall(samen) {
        let s = samen >>> 0;
        return () => {
            s = (s + 0x6D2B79F5) >>> 0;
            let t = Math.imul(s ^ (s >>> 15), 1 | s);
            t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }

    static punkte(lage, groesse) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        return new THREE.Points(geo, new THREE.PointsMaterial({ color: Meshgenesiskapseln.PUNKTFARBE, size: groesse, sizeAttenuation: true }));
    }

    /** Dummy der Außenfläche: `anzahl` Punkte auf den Kapseln um die Knochen (gewichtet nach Länge × Dicke), fester Zufall je Probe. */
    static punktwolke(gelenke, lagen, anzahl, samen, groesse = 0.016) {
        const zufall = Meshgenesiskapseln.zufall(samen * 7919 + 17);
        const knochen = Meshgenesiskapseln.knochen(gelenke, lagen).filter(k => k.a.distanceTo(k.b) > 1e-4);
        const gewicht = knochen.map(k => k.a.distanceTo(k.b) * k.radius);
        const summe = gewicht.reduce((s, w) => s + w, 0);
        const lage = new Float32Array(anzahl * 3);
        for (let n = 0; n < anzahl; n++) {
            let wahl = zufall() * summe, i = 0;
            while (i < knochen.length - 1 && wahl > gewicht[i]) wahl -= gewicht[i++];
            const k = knochen[i];
            const achse = new THREE.Vector3().subVectors(k.b, k.a);
            const d = achse.clone().normalize();
            const u = new THREE.Vector3().crossVectors(d, Math.abs(d.y) < 0.9 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0)).normalize();
            const v = new THREE.Vector3().crossVectors(d, u);
            const w = zufall() * Math.PI * 2;
            const p = k.a.clone().addScaledVector(achse, zufall()).addScaledVector(u, Math.cos(w) * k.radius).addScaledVector(v, Math.sin(w) * k.radius);
            p.toArray(lage, n * 3);
        }
        return Meshgenesiskapseln.punkte(lage, groesse);
    }
}
