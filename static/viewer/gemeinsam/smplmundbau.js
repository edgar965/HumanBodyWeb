import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { Eigenhaut } from './eigenhaut.js';

/**
 * Smplmundbau — Mundhöhle, Zähne und Zunge für eine SMPL-X-Figur.
 *
 * WARUM (Edgar, 25.09.2026: „mach auch … Mund"): Das SMPL-X-Netz hat genau
 * EIN Loch — den Mund (32 Randpunkte, gemessen; `SMPL/xdetails.py`) —, aber
 * nichts dahinter: Wer hineinsieht, sieht die Rückseite des Kopfes. Hier
 * entstehen drei Teile in der Ruhelage der Figur (Meter, Y oben, Z vorn):
 *   - die Höhle: Ringe vom Mundrand nach hinten, mit den Hautgewichten des
 *     jeweiligen Randpunkts (Oberlippe folgt dem Kopf, Unterlippe dem Kiefer);
 *   - Zähne: je Reihe 14 Kästen auf einem Parabelbogen hinter den Lippen,
 *     oben am Kopf (`Head`), unten am Kiefer (`Jaw`);
 *   - die Zunge: ein flaches Ellipsoid am Kiefer.
 * Die Maße (mm) sind anatomische Mittelwerte, skaliert mit der Mundbreite.
 */
export class Smplmundbau {

    /** Ringe der Höhle: [Skalierung um die Mitte, Tiefe m, Senkung m]. */
    static RINGE = [[0.96, 0.003, 0.0], [1.12, 0.010, 0.002], [1.05, 0.022, 0.004],
                    [0.7, 0.034, 0.004], [0.25, 0.040, 0.003]];
    static ZAEHNE_JE_REIHE = 14;

    /** Die Randschleife des Netzes (Punktnummern, geordnet) — das Mundloch. */
    static randschleife(dreiecke) {
        const zaehler = new Map();
        for (const [a, b, c] of dreiecke) {
            for (const [p, q] of [[a, b], [b, c], [c, a]]) {
                const schluessel = p < q ? `${p}_${q}` : `${q}_${p}`;
                zaehler.set(schluessel, (zaehler.get(schluessel) || 0) + 1);
            }
        }
        const nachbarn = new Map();
        for (const [schluessel, n] of zaehler) {
            if (n !== 1) continue;
            const [p, q] = schluessel.split('_').map(Number);
            if (!nachbarn.has(p)) nachbarn.set(p, []);
            if (!nachbarn.has(q)) nachbarn.set(q, []);
            nachbarn.get(p).push(q);
            nachbarn.get(q).push(p);
        }
        if (!nachbarn.size) return [];
        const start = nachbarn.keys().next().value;
        const schleife = [start];
        let vorher = -1;
        let jetzt = start;
        for (let i = 0; i < nachbarn.size; i++) {
            const weiter = nachbarn.get(jetzt).find((x) => x !== vorher);
            if (weiter === undefined || weiter === start) break;
            schleife.push(weiter);
            vorher = jetzt;
            jetzt = weiter;
        }
        return schleife;
    }

    /**
     * Die drei Teile bauen und an die Figur hängen.
     * @param gruppe   Figurgruppe
     * @param skelett  `{skeleton, bones}` aus `Knochenbau`
     * @param punkte   Ruhepunkte des UNGETEILTEN Netzes ([[x,y,z], …])
     * @param dreiecke Dreiecke des ungeteilten Netzes
     * @param haut     Hautgewichte am ungeteilten Netz (Serverantwort)
     * @returns {{hoehle, zaehne, zunge}|null}
     */
    static bauen(gruppe, skelett, punkte, dreiecke, haut) {
        const schleife = Smplmundbau.randschleife(dreiecke);
        if (schleife.length < 8 || !skelett?.skeleton) return null;
        const knochen = new Map(skelett.bones.map((k, i) => [k.name, i]));
        const kopf = knochen.get('Head');
        const kiefer = knochen.get('Jaw') ?? kopf;
        if (kopf === undefined) return null;
        const rand = schleife.map((i) => new THREE.Vector3(...punkte[i]));
        const mitte = rand.reduce((s, p) => s.add(p), new THREE.Vector3()).divideScalar(rand.length);
        const breite = Math.max(...rand.map((p) => p.x)) - Math.min(...rand.map((p) => p.x));
        const gewichte = Smplmundbau._randgewichte(schleife, haut, skelett, kopf, kiefer);
        const teile = {
            hoehle: Smplmundbau._hoehle(rand, mitte, gewichte, kopf, kiefer),
            zaehne: Smplmundbau._zaehne(mitte, breite, kopf, kiefer),
            zunge: Smplmundbau._zunge(mitte, breite, kiefer),
        };
        for (const [name, netz] of Object.entries(teile)) {
            netz.name = `smpl_mund_${name}`;
            netz.frustumCulled = false;
            Eigenhaut.einhaengen(gruppe, netz, skelett);
        }
        return teile;
    }

    /** Je Randpunkt seine vier Knochen und Gewichte (Knochennummern im Skelett). */
    static _randgewichte(schleife, haut, skelett, kopf, kiefer) {
        const spalte = haut?.knochen ? Eigenhaut.spaltenNummern(haut.knochen, skelett) : null;
        if (!spalte) return schleife.map(() => [[kopf, 0.5, kiefer, 0.5, 0, 0, 0, 0]]);
        const { index, gewicht } = Eigenhaut.gewichte(haut);
        return schleife.map((p) => {
            const aus = [];
            for (let k = 0; k < 4; k++) aus.push(spalte[index[p * 4 + k]] ?? kopf, gewicht[p * 4 + k]);
            return aus;
        });
    }

    static _haut(geometrie, je) {
        const n = geometrie.attributes.position.count;
        const index = new Float32Array(n * 4);
        const gewicht = new Float32Array(n * 4);
        for (let i = 0; i < n; i++) {
            const g = je(i);
            for (let k = 0; k < 4; k++) {
                index[i * 4 + k] = g[k * 2] ?? 0;
                gewicht[i * 4 + k] = g[k * 2 + 1] ?? 0;
            }
        }
        geometrie.setAttribute('skinIndex', new THREE.Float32BufferAttribute(index, 4));
        geometrie.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewicht, 4));
    }

    static _hoehle(rand, mitte, gewichte, kopf, kiefer) {
        const n = rand.length;
        const lage = [];
        const quelle = [];
        for (const [s, tief, senk] of Smplmundbau.RINGE) {
            for (let i = 0; i < n; i++) {
                const p = rand[i].clone().sub(mitte).multiplyScalar(s).add(mitte);
                p.z -= tief;
                p.y -= senk;
                lage.push(p.x, p.y, p.z);
                quelle.push(i);
            }
        }
        const deckel = lage.length / 3;
        lage.push(mitte.x, mitte.y - 0.003, mitte.z - 0.042);
        quelle.push(-1);
        const index = [];
        const ringe = [rand.map((_, i) => -1 - i), ...Smplmundbau.RINGE.map((_, r) => rand.map((_, i) => r * n + i))];
        // Ring 0 ist der Mundrand selbst — als eigene Punkte (gleiche Lage wie der Rand).
        const randpunkte = lage.length / 3;
        for (let i = 0; i < n; i++) {
            lage.push(rand[i].x, rand[i].y, rand[i].z);
            quelle.push(i);
        }
        ringe[0] = rand.map((_, i) => randpunkte + i);
        for (let r = 0; r + 1 < ringe.length; r++) {
            for (let i = 0; i < n; i++) {
                const a = ringe[r][i], b = ringe[r][(i + 1) % n];
                const c = ringe[r + 1][i], d = ringe[r + 1][(i + 1) % n];
                index.push(a, c, b, b, c, d);
            }
        }
        const letzter = ringe[ringe.length - 1];
        for (let i = 0; i < n; i++) index.push(letzter[i], deckel, letzter[(i + 1) % n]);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.Float32BufferAttribute(lage, 3));
        geo.setIndex(index);
        geo.computeVertexNormals();
        Smplmundbau._haut(geo, (i) => (quelle[i] < 0 ? [kopf, 0.5, kiefer, 0.5] : gewichte[quelle[i]]));
        return new THREE.SkinnedMesh(geo, new THREE.MeshPhysicalMaterial({
            color: 0x3a1418, roughness: 0.75, side: THREE.DoubleSide,
        }));
    }

    static _zaehne(mitte, breite, kopf, kiefer) {
        const teile = [];
        const reihen = [[+1, kopf, 0.0085], [-1, kiefer, 0.0075]];
        const bogen = 0.82 * breite;
        for (const [seite, knochen, hoehe] of reihen) {
            const zahl = Smplmundbau.ZAEHNE_JE_REIHE;
            for (let i = 0; i < zahl; i++) {
                const t0 = -1 + (2 * i) / zahl;
                const t1 = -1 + (2 * (i + 1)) / zahl;
                const t = (t0 + t1) / 2;
                const x = (t * bogen) / 2;
                const z = mitte.z - 0.005 - 0.02 * t * t;
                const dx = ((t1 - t0) * bogen) / 2;
                const dz = -0.04 * t * (t1 - t0);
                const breit = Math.hypot(dx, dz) * 0.9;
                const vorn = Math.abs(t) < 0.3;
                const box = new THREE.BoxGeometry(breit, hoehe * (vorn ? 1 : 0.85), vorn ? 0.004 : 0.007);
                box.rotateY(-Math.atan2(dz, dx));
                box.translate(x, mitte.y + seite * (0.0006 + (hoehe * (vorn ? 1 : 0.85)) / 2), z);
                const n = box.attributes.position.count;
                box.setAttribute('skinIndex', new THREE.Float32BufferAttribute(new Array(n).fill([knochen, 0, 0, 0]).flat(), 4));
                box.setAttribute('skinWeight', new THREE.Float32BufferAttribute(new Array(n).fill([1, 0, 0, 0]).flat(), 4));
                teile.push(box);
            }
        }
        const geo = mergeGeometries(teile);
        return new THREE.SkinnedMesh(geo, new THREE.MeshPhysicalMaterial({
            color: 0xf0ece0, roughness: 0.25, clearcoat: 0.4,
        }));
    }

    static _zunge(mitte, breite, kiefer) {
        const geo = new THREE.SphereGeometry(1, 24, 12);
        geo.scale(0.36 * breite, 0.006, 0.026);
        geo.translate(mitte.x, mitte.y - 0.0085, mitte.z - 0.022);
        const n = geo.attributes.position.count;
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(new Array(n).fill([kiefer, 0, 0, 0]).flat(), 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(new Array(n).fill([1, 0, 0, 0]).flat(), 4));
        return new THREE.SkinnedMesh(geo, new THREE.MeshPhysicalMaterial({
            color: 0xb55a6a, roughness: 0.45,
        }));
    }
}
