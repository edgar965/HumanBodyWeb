import * as THREE from 'three';
import { Eigenhaut } from '../gemeinsam/eigenhaut.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Meshfighaut — ein Netz-Objekt (Kleidung, Haar, Hut, Stab …) an das Skelett der Figur binden (13.10.2026).
 *
 * Edgar: „Warum animieren die Kleider nicht?" Die Objekte aus dem Netz sind starre GLB; neben jeder liegt jetzt eine Hautdatei (`Kleidung/hautdatei.py`, `.haut`):
 * zlib über acht Ebenen zu je N Bytes — vier Knochennummern, vier Gewichte (Summe 255) je GLB-Punkt. Die Nummern zählen in der Namensliste des Steckbriefs (`haut.knochen`); welche Nummer ein Knochen im
 * Skelett der Figur hat, entscheidet erst dieses (`Eigenhaut.spaltenNummern`), darum wird `skinIndex` bei JEDER Bindung neu aus den Rohebenen gebaut — die Figur wird bei jedem Reglerzug und jedem Wechsel
 * der Haltung neu gebaut und bekommt ein neues Skelett.
 *
 * Aus dem `Mesh` der GLB wird ein `SkinnedMesh` mit derselben Geometrie und demselben Material; die Lage in der Gruppe ist die Einheit (wie beim Körper, `Eigenhaut.einhaengen`).
 */
export class Meshfighaut {

    /**
     * Die Hautdatei laden und entpacken.
     * @returns {Promise<{n: number, index: Uint8Array, gewicht: Uint8Array}>} `index`/`gewicht` als Ebenen: Ebene k = [k·n, (k+1)·n)
     */
    static async laden(adresse, n) {
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw new Error(`Hautdatei ${antwort.status}`);
        const roh = new Uint8Array(await new Response(antwort.body.pipeThrough(new DecompressionStream('deflate'))).arrayBuffer());
        if (roh.length !== 8 * n) throw new Error(`Hautdatei hat ${roh.length} Bytes, erwartet ${8 * n} (${n} Punkte)`);
        return { n, index: roh.subarray(0, 4 * n), gewicht: roh.subarray(4 * n) };
    }

    /** Alle Netze unter `wurzel` — die der GLB (ein Netz) oder schon gebundene. */
    static netze(wurzel) {
        const liste = [];
        wurzel.traverse(o => { if (o.isMesh) liste.push(o); });
        return liste;
    }

    /**
     * Die Netze von `wurzel` an `skelett` (`{skeleton, bones}` aus `Knochenbau`) binden.
     * @param {object} haut  `Meshfighaut.laden` + `knochen` (Namensliste des Steckbriefs)
     * @returns {boolean} gebunden? (false: Punktzahl oder Knochen passen nicht — das Objekt bleibt, wie es ist)
     */
    static binden(wurzel, skelett, haut) {
        const netze = Meshfighaut.netze(wurzel);
        if (netze.length !== 1) {
            Protokoll.warnung('Meshfighaut', `${netze.length} Netze in der GLB, erwartet 1 — nicht gebunden`);
            return false;
        }
        const netz = netze[0];
        const n = netz.geometry.getAttribute('position').count;
        if (n !== haut.n) {
            Protokoll.warnung('Meshfighaut', `${n} Punkte in der GLB, ${haut.n} in der Hautdatei — nicht gebunden`);
            return false;
        }
        const spalte = Eigenhaut.spaltenNummern(haut.knochen, skelett);
        if (!spalte) return false;
        const index = new Uint16Array(4 * n);
        for (let k = 0; k < 4; k++) {
            const ebene = haut.index.subarray(k * n, (k + 1) * n);
            for (let i = 0; i < n; i++) index[4 * i + k] = spalte[ebene[i]];
        }
        const gewicht = new Uint8Array(4 * n);
        for (let k = 0; k < 4; k++) {
            const ebene = haut.gewicht.subarray(k * n, (k + 1) * n);
            for (let i = 0; i < n; i++) gewicht[4 * i + k] = ebene[i];
        }
        const geo = netz.geometry;
        geo.setAttribute('skinIndex', new THREE.BufferAttribute(index, 4));
        geo.setAttribute('skinWeight', new THREE.BufferAttribute(gewicht, 4, true));
        const gebunden = netz.isSkinnedMesh ? netz : Meshfighaut._umwandeln(netz);
        gebunden.updateMatrix();
        gebunden.bind(skelett.skeleton, gebunden.matrix);
        return true;
    }

    /** Aus dem Netz der GLB ein `SkinnedMesh` an derselben Stelle. */
    static _umwandeln(netz) {
        const gebunden = new THREE.SkinnedMesh(netz.geometry, netz.material);
        gebunden.name = netz.name;
        gebunden.visible = netz.visible;
        gebunden.userData = netz.userData;
        gebunden.frustumCulled = false;                 // eine animierte Figur verlässt ihre Ruhe-Box (wie `Eigenhaut.binden`)
        gebunden.castShadow = netz.castShadow;
        gebunden.receiveShadow = netz.receiveShadow;
        gebunden.position.copy(netz.position);
        gebunden.quaternion.copy(netz.quaternion);
        gebunden.scale.copy(netz.scale);
        netz.parent.add(gebunden);
        netz.parent.remove(netz);
        return gebunden;
    }
}
