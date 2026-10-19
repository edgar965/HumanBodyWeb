/**
 * Mesh3daianatomie — das Anatomie-Stück eines Anzeigenetzes trägt die Haut des Körpers (18.10.2026, Edgar: „alle testjobs haben das männliche Geschlechtsteil ohne Textur des Körpers.
 * Das ist gerade gefixt worden in einer anderen Session … Warum fehlt das bei der Berechnung bei Dir??“).
 *
 * Der Fix steckt in `Anatomiebacken` (gemeinsam/, für Charakter und Studio): eine Karte im Atlas des Stücks, je Texel von der Hautstelle darunter. Die Seiten von Mesh3D-AI bauen keine
 * Genesis-Instanz, sondern zeigen ein fertiges Anzeigenetz (`Mesh3daiflaechennetz`) — dort stand das Stück mit seinem eigenen Material (Matt0: „daz_anatomie_mann/farbe“, nur eine Farbe).
 * Hier wird nur übergeben, was `Anatomiebacken` liest: `inst.bodyMesh` (Ruhelage, UV, Index der Hautdreiecke je Kachel, Materialien mit `userData.gruppe` und `map`) und das Stück als eigenes
 * Netz. Gerechnet wird in der Ruhelage (die Zuordnung hängt nicht an der Haltung), einmal je Anzeigenetz; die Karte ersetzt Bild und Farbe des Anatomie-Materials — es ist dasselbe Material
 * in allen Feldern, die dieses Netz zeigen.
 */
import * as THREE from 'three';
import { Anatomiebacken } from '../gemeinsam/anatomiebacken.js';

export class Mesh3daianatomie {
    /** Gruppenname, unter dem `Anatomiebacken` die Haut sucht (`Anatomiehaut.HAUT`); die Namen im Paket sind die der ersten Gruppe je Kachel („Mouth Cavity“ trägt die Kopfkachel). */
    static HAUT_GRUPPE = 'Body';
    /** So lange wird auf die Hautbilder gewartet (sie laden mit dem Netz). */
    static WARTEN_MS = 60000;

    /** Einmal je Anzeigenetz anstoßen; `fertig()` nach einer gelungenen Rechnung (die Seite zeichnet neu). */
    static anwenden(netz, materialien, fertig) {
        if (!netz._anatomie) {
            netz._anatomie = Mesh3daianatomie._backen(netz, materialien)
                .then((ok) => { if (ok) fertig?.(); return ok; })
                .catch((fehler) => { console.warn(`Mesh3daianatomie: ${fehler.message}`); return false; });
        }
        return netz._anatomie;
    }

    static async _backen(netz, materialien) {
        const teile = netz.kopf.teile || [];
        const koerper = teile.indexOf('koerper'), anatomie = teile.indexOf('anatomie');
        if (anatomie < 0 || koerper < 0 || !netz.ruhe) return false;
        // Trainingspaare (19.10.2026, Edgar: „die textur der Scham ist falsch, fangen wir wieder von vorne an mit dieser Textur??“): das Netz kommt aus dem GLB-Export der
        // Charakter-Seite, das Stück trägt dort schon die Karte, die `Anatomiebacken` auf der Charakter-Seite gerechnet hat — nicht noch einmal backen.
        if (netz.kopf.anatomie_fertig) return false;
        const stueck = [], stueckMaterial = new Set(), haut = new Map();
        for (let t = 0; t < netz.material.length; t++) {
            const m = netz.material[t], e = netz.etikett[t];
            const ecken = [netz.dreiecke[3 * t], netz.dreiecke[3 * t + 1], netz.dreiecke[3 * t + 2]];
            if (e === anatomie) {
                stueck.push(...ecken);
                if (m >= 0) stueckMaterial.add(m);
            } else if (e === koerper && m >= 0 && materialien[m]?.map) {
                if (!haut.has(m)) haut.set(m, []);
                haut.get(m).push(...ecken);
            }
        }
        if (!stueck.length || !haut.size || !stueckMaterial.size) return false;
        await Promise.all([...haut.keys()].map(m => Mesh3daianatomie._geladen(materialien[m].map)));
        const inst = { bodyMesh: Mesh3daianatomie._koerper(netz, haut, materialien) };
        const netzStueck = { geometry: Mesh3daianatomie._stueck(netz, stueck), userData: {} };
        const gebacken = await Anatomiebacken.backen(inst, netzStueck, { karte: null, normalen: null, rauheit: null }, [Mesh3daianatomie.HAUT_GRUPPE]);
        if (!gebacken?.map) return false;
        for (const m of stueckMaterial) {
            const material = materialien[m];
            material.map = gebacken.map;
            material.color.set(0xffffff);
            material.needsUpdate = true;
        }
        return true;
    }

    /** Die Haut in der Ruhelage: Index je Kachel als Gruppe, Materialien als schlichte Objekte mit den Feldern, die `Anatomiebacken.quelle` liest. */
    static _koerper(netz, haut, materialien) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(netz.ruhe, 3));
        geo.setAttribute('uv', netz.uvAttribut);
        const index = new Uint32Array([...haut.values()].reduce((s, l) => s + l.length, 0));
        const material = [];
        let ab = 0;
        for (const [m, liste] of haut) {
            index.set(liste, ab);
            geo.addGroup(ab, liste.length, material.length);
            material.push({ userData: { gruppe: Mesh3daianatomie.HAUT_GRUPPE }, map: materialien[m].map, normalMap: null, roughnessMap: null, color: new THREE.Color(1, 1, 1) });
            ab += liste.length;
        }
        geo.setIndex(new THREE.BufferAttribute(index, 1));
        geo.computeVertexNormals();
        return { geometry: geo, material };
    }

    /** Das Stück als eigenes Netz (nur seine Punkte — `Anatomieton.kasten` misst über alle Punkte der Geometrie). */
    static _stueck(netz, dreiecke) {
        const neu = new Map(), index = new Uint32Array(dreiecke.length);
        for (let i = 0; i < dreiecke.length; i++) {
            let n = neu.get(dreiecke[i]);
            if (n === undefined) { n = neu.size; neu.set(dreiecke[i], n); }
            index[i] = n;
        }
        const pos = new Float32Array(neu.size * 3), uv = new Float32Array(neu.size * 2);
        for (const [a, n] of neu) {
            pos.set(netz.ruhe.subarray(3 * a, 3 * a + 3), 3 * n);
            uv.set(netz.uv.subarray(2 * a, 2 * a + 2), 2 * n);
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
        geo.setIndex(new THREE.BufferAttribute(index, 1));
        geo.computeVertexNormals();
        return geo;
    }

    static _geladen(textur) {
        return new Promise((fertig, fehler) => {
            const start = performance.now();
            const pruefen = () => {
                if (textur.image?.width) return fertig();
                if (performance.now() - start > Mesh3daianatomie.WARTEN_MS) return fehler(new Error('Hautbild nicht geladen'));
                setTimeout(pruefen, 200);
            };
            pruefen();
        });
    }
}
