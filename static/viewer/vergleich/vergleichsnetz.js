/**
 * Vergleichsnetz — Koerpernetz einer Vergleichsspalte laden und einfaerben.
 *
 * WARUM eigenes Modul (Umbau 16.08.2026): In viewer_compare.js standen
 * `loadMesh` (62 Zeilen) und `reloadMesh` (67 Zeilen) fast buchstabengleich
 * untereinander. Unterschied waren drei Dinge: das Entfernen des alten Netzes,
 * der Zusatz `?body_type=…` an der Adresse und ein abschliessender Aufruf der
 * Hautfarbe. Hier ist es EINE Methode mit zwei Schaltern.
 */
import * as THREE from 'three';
import { base64ToFloat32, blenderToThreeCoords }
    from '../gemeinsam/kodierung.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';

/** Materialien des Koerpers, nach Materialnummer des Netzes. */
const KOERPERMATERIALIEN = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },   // 0 Haut
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },   // 1 Zensur
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },   // 2 Wimper
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },   // 3 Pupille
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },   // 4 Lederhaut
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true }, // 5 Hornhaut
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },   // 6 Iris
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },   // 7 Zunge
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },   // 8 Zaehne
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },   // 9 Fingernaegel
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },   // 10 Fussnaegel
];

export class Vergleichsnetz {
    /**
     * Netz laden und in die Szene setzen.
     * @param {string|null} koerperart  gesetzt = altes Netz ersetzen
     */
    static async laden(ansicht, koerperart = null) {
        if (koerperart !== null) Vergleichsnetz._altesEntfernen(ansicht);
        const adresse = ansicht.apiPrefix + '/mesh/'
            + (koerperart ? '?body_type=' + encodeURIComponent(koerperart) : '');
        try {
            const daten = await Serverabruf.json(adresse);
            if (daten.error) {
                console.error(`[${ansicht.label}] mesh error:`, daten.error);
                return;
            }
            ansicht.vertexCount = daten.vertex_count;
            ansicht.felder.zahl('vertexzahl', ansicht.vertexCount.toLocaleString());

            const geo = Vergleichsnetz._geometrie(daten);
            const materialien = KOERPERMATERIALIEN.map(d =>
                new THREE.MeshStandardMaterial({
                    color: d.color, roughness: d.roughness, metalness: d.metalness,
                    side: THREE.DoubleSide,
                    transparent: d.transparent || false,
                    opacity: d.opacity !== undefined ? d.opacity : 1.0,
                }));
            const gruppen = daten.groups || [];
            if (geo.index && gruppen.length > 0) {
                for (const g of gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
                ansicht.bodyMesh = new THREE.Mesh(geo, materialien);
            } else {
                ansicht.bodyMesh = new THREE.Mesh(geo, materialien[0]);
            }
            ansicht.bodyGeometry = geo;
            ansicht.scene.add(ansicht.bodyMesh);
            ansicht.felder.zahl('vertexzahl',
                                geo.attributes.position.count.toLocaleString());
            if (koerperart === null) Vergleichsnetz.hautfarbeAnwenden(ansicht);
        } catch (e) {
            console.error(`[${ansicht.label}] Failed to load mesh:`, e);
        }
    }

    static _altesEntfernen(ansicht) {
        if (!ansicht.bodyMesh) return;
        ansicht.scene.remove(ansicht.bodyMesh);
        ansicht.bodyMesh.geometry?.dispose();
        ansicht.bodyMesh = null;
        ansicht.bodyGeometry = null;
    }

    /** Die Geometrie einer Ansicht — gebaut wie ueberall (28.08.2026). */
    static _geometrie(daten) {
        return Koerpernetz.geometrie(daten, THREE);
    }

    /** Neue Punkte vom Server einsetzen (Morph-Aenderung ueber die Funkstrecke). */
    static punkteSetzen(ansicht, puffer) {
        if (!ansicht.bodyGeometry) return;
        const punkte = ansicht.bodyGeometry.attributes.position;
        const neu = new Float32Array(puffer);
        blenderToThreeCoords(neu);
        punkte.array.set(neu);
        punkte.needsUpdate = true;
        ansicht.bodyGeometry.computeBoundingSphere();
    }

    /** Das Hautmaterial des Netzes oder null. */
    static hautmaterial(ansicht) {
        const m = ansicht.bodyMesh?.material;
        if (!m) return null;
        return Array.isArray(m) ? m[0] : m;
    }

    /** Hautfarbe zur Herkunft der eingestellten Koerperart setzen. */
    static hautfarbeAnwenden(ansicht) {
        const art = ansicht.felder.koerperart?.value || ansicht.defaultBodyType || '';
        if (!art || !Object.keys(ansicht.skinColorMap).length) return;
        const material = Vergleichsnetz.hautmaterial(ansicht);
        if (!Hautfarbe.ausKoerperart(material, art, ansicht.skinColorMap)) return;
        Vergleichsnetz.reglerNachziehen(ansicht, material);
    }

    /** Hautregler auf die Werte des Materials stellen. */
    static reglerNachziehen(ansicht, material) {
        const f = ansicht.felder;
        if (f.hautfarbe) f.hautfarbe.value = '#' + material.color.getHexString();
        if (f.rauheit) {
            f.rauheit.value = Math.round(material.roughness * 100);
            f.rauheitWert.textContent = material.roughness.toFixed(2);
        }
        if (f.metall) {
            f.metall.value = Math.round(material.metalness * 100);
            f.metallWert.textContent = material.metalness.toFixed(2);
        }
    }
}
