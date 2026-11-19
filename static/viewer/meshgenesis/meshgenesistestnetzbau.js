/**
 * Meshgenesistestnetzbau — ein Anzeigenetz (`Meshgenesisflaechennetz`: Figur oder Kleidungsstück) aus seiner Ruhelage mit den Knochenmatrizen der vorhergesagten Haltung häuten (17.10.2026 nachts).
 * Aus `Meshgenesistestseite._figurBauen` herausgelöst, damit die Kleider und Bestandteile eines Tests (`Meshgenesistestkleider`) mit DENSELBEN Matrizen und derselben Hautmischung gehäutet werden wie die Figur.
 */
import * as THREE from 'three';
import { Meshgenesisflaechen } from './meshgenesisflaechen.js';
import { Meshgenesisflaechennormalen } from './meshgenesisflaechennormalen.js';
import { Meshgenesishaeutung } from './meshgenesishaeutung.js';

export class Meshgenesistestnetzbau {
    /**
     * @param netz `Meshgenesisflaechennetz` mit `ruhe` @param matrizen Knochenmatrizen (`Meshgenesishaeutung.ausDrehungen`)
     * @param verdeckt Uint8Array je Dreieck (1 = unter einem gewählten Stück, fällt weg — die Hautverdeckung der Testseite, `Meshgenesistestkleider.verdeckt`) oder null
     * @returns {THREE.Mesh} Dreiecke nach Material gruppiert, geteilt markiert
     */
    /**
     * Index der sichtbaren Dreiecke nach Material sortiert (eine Gruppe je Material, −1 = Farbe je Punkt = das letzte), in jeder Gruppe in der Reihenfolge des Netzes; `gruppe(ab, n, m)`
     * je nicht leerem Material. `verborgen` (Paket `Meshgenesisflaechennetz`): die Haut unter dem Anatomie-Stück, seit 08.11.2026 auch an den Testfiguren
     * (`Meshgenesismeshanatomie.anzeigenetz`, Edgar zu n1: „Scham fehlt“). 19.11.2026 (Ladezeit): Zählsortieren in einem Uint32Array statt `push` in Listen — Haar mit
     * 1,56 Mio. Dreiecken 162 ms; derselbe Index, dieselben Gruppen.
     */
    static nachMaterial(netz, anzahl, verdeckt, gruppe) {
        const letzter = anzahl - 1, f = netz.material.length, mat = netz.material, ver = netz.verborgen, d = netz.dreiecke;
        const zahl = new Uint32Array(anzahl), wahl = new Int32Array(f);
        for (let t = 0; t < f; t++) {
            if ((verdeckt && verdeckt[t]) || ver?.[t]) {
                wahl[t] = -1;
                continue;
            }
            const m = mat[t] < 0 ? letzter : mat[t];
            wahl[t] = m;
            zahl[m]++;
        }
        const anfang = new Uint32Array(anzahl);
        let summe = 0;
        for (let m = 0; m < anzahl; m++) {
            anfang[m] = summe;
            if (zahl[m]) gruppe(summe * 3, zahl[m] * 3, m);
            summe += zahl[m];
        }
        const index = new Uint32Array(summe * 3);
        for (let t = 0; t < f; t++) {
            const m = wahl[t];
            if (m < 0) continue;
            const o = anfang[m]++ * 3;
            index[o] = d[t * 3];
            index[o + 1] = d[t * 3 + 1];
            index[o + 2] = d[t * 3 + 2];
        }
        return index;
    }

    static mesh(netz, matrizen, verdeckt = null) {
        if (!netz.ruhe) throw new Error('Anzeigenetz ohne Ruhelage');
        const lage = Meshgenesishaeutung.verformen(netz.ruhe, netz.knochen, netz.gewicht, netz.kopf.haut, matrizen);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        geo.setAttribute('uv', netz.uvAttribut);
        netz.farbe ??= Meshgenesisflaechen.farben(netz.kopf, netz.dreiecke, netz.etikett);
        geo.setAttribute('color', netz.farbe);
        // Dreiecke nach Material sortiert (eine Gruppe je Material, −1 = Farbe je Punkt = das letzte Material).
        const materialien = netz.materialien();
        geo.setIndex(new THREE.BufferAttribute(Meshgenesistestnetzbau.nachMaterial(netz, materialien.length, verdeckt, (ab, n, m) => geo.addGroup(ab, n, m)), 1));
        // mitgelieferte Normalen (21.10.2026, Weg g mit Textur je Stück: die Punkte sind an den Atlasnähten doppelt — gerechnet knickte dort die Schattierung), mit der Haltung gedreht
        Meshgenesisflaechennormalen.setzen(geo, netz.normalen ? Meshgenesisflaechennormalen.gehaeutet(netz.normalen, netz.knochen, netz.gewicht, netz.kopf.haut, matrizen) : null);
        geo.userData.gemeinsam = true;          // die Felder geben ihren Inhalt bei jedem Zeichnen frei — dieses Netz bleibt
        for (const m of materialien) m.userData.gemeinsam = true;
        return new THREE.Mesh(geo, materialien);
    }
}
