/**
 * Mesh3daikapseln — Werkzeug der Zeichner auf der Seite „Mesh3D-AI“ (14.10.2026): Kapseln um die Knochen eines Gerüsts, Punktwolke auf diesen Kapseln, Fehlerpunkte und Rohre.
 * Gebraucht von `Mesh3daikapselzeichner` (ganzer Körper, Hände/Füße, Kleider) und `Mesh3daigesichtzeichner`. Eine Beschreibung ist `[{name, gruppe, eltern (Index oder −1), radius?, farbe?}]`;
 * `radius` und `farbe` aus dem Server gelten vor den Tabellen hier (der ganze Körper führt keine und fällt auf die Tabellen zurück).
 */
import * as THREE from 'three';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3daimaterial } from './mesh3daimaterial.js';

export class Mesh3daikapseln {
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
            liste.push({ a, b, gruppe: g.gruppe, textur: g.textur ?? g.gruppe, farbe: g.farbe, radius: g.radius ?? Mesh3daikapseln.RADIUS_NAME[g.name] ?? Mesh3daikapseln.RADIUS_GRUPPE[g.gruppe] });
        });
        return liste;
    }

    /** Geteilte Geometrien und Materialien (`Mesh3daigemeinsam`): dieselbe Kapsel, Kugel oder Röhre wird von Bild zu Bild wieder hergegeben, statt neu hochgeladen zu werden. */
    static kapselgeometrie(radius, laenge) {
        const g = Mesh3daigemeinsam;
        return g.geometrie(`kapsel:${radius.toFixed(4)}:${g.laenge(laenge)}`, () => new THREE.CapsuleGeometry(radius, laenge, 4, 10));
    }

    static kugelgeometrie(radius, breite = 10, hoehe = 8) {
        return Mesh3daigemeinsam.geometrie(`kugel:${radius.toFixed(4)}:${breite}:${hoehe}`, () => new THREE.SphereGeometry(radius, breite, hoehe));
    }

    static basismaterial(farbe) {
        const hex = new THREE.Color(farbe).getHex();
        return Mesh3daigemeinsam.material(`basis:${hex}`, () => new THREE.MeshBasicMaterial({ color: hex }));
    }

    /**
     * Kapseln um die Knochen in der gewählten Ansichtsart (`Mesh3daimaterial`).
     * `stil`: `{modus}` = Farben des Soll; `{modus, tint, deckkraft}` = eingefärbt (Ausgabe des Netzes); `{wand: true}` = Geist als Drahtgitter.
     */
    static geruest(gelenke, lagen, stil = {}) {
        const gruppe = new THREE.Group();
        const hoch = new THREE.Vector3(0, 1, 0);
        for (const k of Mesh3daikapseln.knochen(gelenke, lagen)) {
            const richtung = new THREE.Vector3().subVectors(k.b, k.a);
            const laenge = richtung.length();
            if (laenge < 1e-4) continue;
            const geo = Mesh3daikapseln.kapselgeometrie(k.radius, Math.max(laenge - 2 * k.radius, 0.002));
            const kapsel = Mesh3daimaterial.netz(geo, { ...stil, sollfarbe: k.farbe ?? Mesh3daikapseln.SOLLFARBEN[k.gruppe], gruppe: k.textur });
            kapsel.position.copy(k.a).add(k.b).multiplyScalar(0.5);
            kapsel.quaternion.setFromUnitVectors(hoch, richtung.normalize());
            gruppe.add(kapsel);
        }
        return gruppe;
    }

    /** Ansicht „Punkte / Gerüst“: Kugeln an den Punkten und dünne Rohre von jedem Punkt zu seinem Elternpunkt. `farbe` ersetzt die Farben des Modells; `kugelradius` 0 = nur Linien. */
    static gerippe(gelenke, lagen, { farbe = null, kugelradius = 0.02, rohrradius = 0.004 } = {}) {
        const gruppe = new THREE.Group();
        const kugel = kugelradius > 0 ? Mesh3daikapseln.kugelgeometrie(kugelradius) : null;
        gelenke.forEach((g, i) => {
            const c = Mesh3daimaterial.heller(farbe ?? g.farbe ?? Mesh3daikapseln.SOLLFARBEN[g.gruppe] ?? Mesh3daikapseln.PUNKTFARBE);
            const lage = new THREE.Vector3().fromArray(lagen[i]);
            if (kugel) {
                const punkt = new THREE.Mesh(kugel, Mesh3daikapseln.basismaterial(c));
                punkt.position.copy(lage);
                gruppe.add(punkt);
            }
            if (g.eltern >= 0) gruppe.add(Mesh3daikapseln.rohr(new THREE.Vector3().fromArray(lagen[g.eltern]), lage, rohrradius, Mesh3daikapseln.basismaterial(c)));
        });
        return gruppe;
    }

    /** Ein dünnes Rohr von `a` nach `b` (Linien des Gesichts); `material` wird geteilt. */
    static rohr(a, b, radius, material) {
        const richtung = new THREE.Vector3().subVectors(b, a);
        const laenge = richtung.length();
        const g = Mesh3daigemeinsam;
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
        return Mesh3daikapseln.fehlerfarbe(Math.round(Math.min(mm / rotMm, 1) * 24), 24);
    }

    static fehlerstufe(mm, rotMm) {
        return Mesh3daikapseln.basismaterial(Mesh3daikapseln.fehlerfarbeStufe(mm, rotMm));
    }

    /** Kugeln an den Lagen, gefärbt nach dem Fehler je Punkt (`je_mm`). */
    static fehlerpunkte(lagen, jeMm, rotMm, radius) {
        const gruppe = new THREE.Group();
        const kugel = Mesh3daikapseln.kugelgeometrie(radius, 12, 8);
        lagen.forEach((lage, i) => {
            const punkt = new THREE.Mesh(kugel, Mesh3daikapseln.fehlerstufe(jeMm[i], rotMm));
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
        return new THREE.Points(geo, new THREE.PointsMaterial({ color: Mesh3daikapseln.PUNKTFARBE, size: groesse, sizeAttenuation: true }));
    }

    /** Dummy der Außenfläche: `anzahl` Punkte auf den Kapseln um die Knochen (gewichtet nach Länge × Dicke), fester Zufall je Probe. */
    static punktwolke(gelenke, lagen, anzahl, samen, groesse = 0.016) {
        const zufall = Mesh3daikapseln.zufall(samen * 7919 + 17);
        const knochen = Mesh3daikapseln.knochen(gelenke, lagen).filter(k => k.a.distanceTo(k.b) > 1e-4);
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
        return Mesh3daikapseln.punkte(lage, groesse);
    }
}
