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
    static binden(wurzel, skelett, haut, haltung = null) {
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
        if (haltung) Meshfighaut._an_die_haltung(gebunden, skelett, haltung);
        else {
            gebunden.bind(skelett.skeleton, gebunden.matrix);
            gebunden.userData.haltungsbindung = false;
        }
        return true;
    }

    /**
     * An die HALTUNG des Netzes binden (`Meshfighaltungspose`): das Netz liegt unverändert im Raum der gebackenen Figur (Haltung), eine eigene Skelettinstanz trägt die Umkehrmatrizen der Haltung statt der
     * der Ruhe, und die Bindematrix hebt das Netz um den Bodenversatz in den Raum der Vorwärtsrechnung (`haltung.boden`). Mit `haltung.beweglich` (ein gehaltener Stab) bindet das Netz ABGELÖST: seine eigene Matrix
     * wirkt dann nach der Häutung (`Meshfigurstab` dreht den Stab um die Faust, ohne ihn von der Hand zu lösen) — `userData.hebung` ist die Bindematrix ohne die Lage des Netzes, die der Stab in seine Matrix zurückrechnet.
     */
    static _an_die_haltung(gebunden, skelett, haltung) {
        const skeleton = new THREE.Skeleton(skelett.skeleton.bones, haltung.inverse);
        const hebung = new THREE.Matrix4().makeTranslation(0, haltung.boden, 0);
        gebunden.bindMode = haltung.beweglich ? THREE.DetachedBindMode : THREE.AttachedBindMode;
        gebunden.bind(skeleton, hebung.clone().multiply(gebunden.matrix));
        gebunden.userData.haltungsbindung = true;
        gebunden.userData.hebung = hebung;
        gebunden.userData.bindung = (gebunden.userData.bindung || 0) + 1;
        if (haltung.beweglich) {
            gebunden.matrixAutoUpdate = false;
            gebunden.matrix.copy(hebung);
            gebunden.matrixWorldNeedsUpdate = true;
        }
    }

    /**
     * Die Punkte eines an die Haltung gebundenen Netzes in der RUHELAGE der Figur (`Float32Array`, Lage der Figurgruppe): `Σ w · (Ruhe · Haltung⁻¹) · (Hebung · p)`. Die Maske der Haut-Verdeckung
     * (`Meshfighautstueck`) vergleicht Stoff und Körper in der Ruhelage — die rohen Punkte des Netzes liegen in der Haltung.
     */
    static ruheposition(netz, skelett) {
        const roh = netz.geometry.getAttribute('position'), idx = netz.geometry.getAttribute('skinIndex'), gew = netz.geometry.getAttribute('skinWeight');
        const ruhe = skelett.skeleton.boneInverses, haltung = netz.skeleton.boneInverses;
        const m = ruhe.map((r, i) => r.clone().invert().multiply(haltung[i]).multiply(netz.userData.hebung).elements);
        const n = roh.count, aus = new Float32Array(3 * n);
        for (let v = 0; v < n; v++) {
            const x = roh.getX(v), y = roh.getY(v), z = roh.getZ(v);
            let ax = 0, ay = 0, az = 0;
            for (let k = 0; k < 4; k++) {
                const w = gew.getComponent(v, k);
                if (w === 0) continue;
                const e = m[idx.getComponent(v, k)];
                ax += w * (e[0] * x + e[4] * y + e[8] * z + e[12]);
                ay += w * (e[1] * x + e[5] * y + e[9] * z + e[13]);
                az += w * (e[2] * x + e[6] * y + e[10] * z + e[14]);
            }
            aus[3 * v] = ax; aus[3 * v + 1] = ay; aus[3 * v + 2] = az;
        }
        return aus;
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
