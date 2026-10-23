/**
 * Mesh3daitestnetzbau — ein Anzeigenetz (`Mesh3daiflaechennetz`: Figur oder Kleidungsstück) aus seiner Ruhelage mit den Knochenmatrizen der vorhergesagten Haltung häuten (17.10.2026 nachts).
 * Aus `Mesh3daitestseite._figurBauen` herausgelöst, damit die Kleider und Bestandteile eines Tests (`Mesh3daitestkleider`) mit DENSELBEN Matrizen und derselben Hautmischung gehäutet werden wie die Figur.
 */
import * as THREE from 'three';
import { Mesh3daiflaechen } from './mesh3daiflaechen.js';
import { Mesh3daiflaechennormalen } from './mesh3daiflaechennormalen.js';
import { Mesh3daihaeutung } from './mesh3daihaeutung.js';

export class Mesh3daitestnetzbau {
    /**
     * @param netz `Mesh3daiflaechennetz` mit `ruhe` @param matrizen Knochenmatrizen (`Mesh3daihaeutung.ausDrehungen`)
     * @param verdeckt Uint8Array je Dreieck (1 = unter einem gewählten Stück, fällt weg — die Hautverdeckung der Testseite, `Mesh3daitestkleider.verdeckt`) oder null
     * @returns {THREE.Mesh} Dreiecke nach Material gruppiert, geteilt markiert
     */
    static mesh(netz, matrizen, verdeckt = null) {
        if (!netz.ruhe) throw new Error('Anzeigenetz ohne Ruhelage');
        const lage = Mesh3daihaeutung.verformen(netz.ruhe, netz.knochen, netz.gewicht, netz.kopf.haut, matrizen);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        geo.setAttribute('uv', netz.uvAttribut);
        netz.farbe ??= Mesh3daiflaechen.farben(netz.kopf, netz.dreiecke, netz.etikett);
        geo.setAttribute('color', netz.farbe);
        // Dreiecke nach Material sortiert (eine Gruppe je Material, −1 = Farbe je Punkt = das letzte Material).
        const materialien = netz.materialien();
        const letzter = materialien.length - 1;
        const je = Array.from({ length: materialien.length }, () => []);
        for (let t = 0; t < netz.material.length; t++) {
            if (verdeckt && verdeckt[t]) continue;
            const m = netz.material[t] < 0 ? letzter : netz.material[t];
            je[m].push(netz.dreiecke[t * 3], netz.dreiecke[t * 3 + 1], netz.dreiecke[t * 3 + 2]);
        }
        const index = new Uint32Array(je.reduce((s, l) => s + l.length, 0));
        let ab = 0;
        je.forEach((l, m) => {
            if (!l.length) return;
            index.set(l, ab);
            geo.addGroup(ab, l.length, m);
            ab += l.length;
        });
        geo.setIndex(new THREE.BufferAttribute(index, 1));
        // mitgelieferte Normalen (21.10.2026, Weg g mit Textur je Stück: die Punkte sind an den Atlasnähten doppelt — gerechnet knickte dort die Schattierung), mit der Haltung gedreht
        Mesh3daiflaechennormalen.setzen(geo, netz.normalen ? Mesh3daiflaechennormalen.gehaeutet(netz.normalen, netz.knochen, netz.gewicht, netz.kopf.haut, matrizen) : null);
        geo.userData.gemeinsam = true;          // die Felder geben ihren Inhalt bei jedem Zeichnen frei — dieses Netz bleibt
        for (const m of materialien) m.userData.gemeinsam = true;
        return new THREE.Mesh(geo, materialien);
    }
}
