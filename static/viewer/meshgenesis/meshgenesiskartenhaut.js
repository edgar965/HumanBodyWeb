/**
 * Meshgenesiskartenhaut — ein Anzeigenetz (`Meshgenesisflaechennetz`) auf der GRAFIKKARTE häuten statt auf der CPU (21.11.2026, Edgar zur Ladezeit von
 * /foto-genesis/test/zauberer_kleidungsregeln_kopie_48/: „ladezeit ewig! fixe“, dann „mach alle drei“ — eins davon: Haar und Bart auf der Karte häuten statt im Hauptfaden).
 *
 * Gemessen im Tab (Zauberer, Rechner unter Last): `Meshgenesistestnetzbau.mesh` für Haar (2,19 Mio. Punkte) und Bart (1,5 Mio.) 636 und 833 ms auf dem Hauptfaden — `verformen`
 * 0,17–0,34 s, Normalen drehen 0,29–0,38 s je Netz —, dazu je Netz gehäutete Punkte und Normalen als eigene Felder (Haar 2 × 26 MB, Bart 2 × 18 MB).
 *
 * HIER: ein `SkinnedMesh` mit FESTEN Knochen — je Knochen seine Matrix aus `Meshgenesishaeutung.ausDrehungen`, getrennte Bindung, Bindematrix und Knocheninverse Einheit: die Karte rechnet
 * Σ w · (R · p + t) wie `verformen`. Punkte, Normalen, Knochen, Gewichte und Dreiecke sind die des Pakets, wo es passt (Ruhelage, keine Kopie; `gewichte`, `index`) — sonst Gewichte auf
 * Summe 1 als Uint16 (Rest auf das größte, je Gewicht höchstens 1/65535 daneben), ein Punkt ohne Gewicht am zusätzlichen Einheitsknochen (`verformen` lässt ihn, wo er ist). Im Tab gegen
 * die CPU-Häutung: höchstens 0,06 µm Abweichung (je rund 2.000 Stichproben in Haar und Bart). three.js häutet damit auch `getVertexPosition`
 * (`Fotogenesiskamera.huelle`). Die Hülle (`boundingSphere`, `boundingBox`) setzt `_huelle` ohne Häutung — fehlt sie, häutet three.js (r170) zum Sortieren alle Punkte auf der CPU
 * (`SkinnedMesh.computeBoundingSphere`); sie dient nur dem Sortieren, das Abschneiden am Sichtkegel ist aus.
 * null, wenn das Netz es nicht hergibt (mehr als vier Knochen je Punkt, keine mitgelieferten Normalen) — dann bleibt `Meshgenesistestnetzbau.mesh`.
 */
import * as THREE from 'three';
import { Meshgenesisflaechen } from './meshgenesisflaechen.js';
import { Meshgenesistestnetzbau } from './meshgenesistestnetzbau.js';

export class Meshgenesiskartenhaut {
    /** Jeder so vielte Punkt zählt für die Hülle. */
    static PROBE = 16;

    /** @param netz `Meshgenesisflaechennetz` mit `ruhe` und `normalen` @param matrizen Knochenmatrizen (3×4 zeilenweise, `Meshgenesishaeutung.ausDrehungen`) @returns {THREE.SkinnedMesh|null} */
    static mesh(netz, matrizen) {
        const k = netz.kopf.haut;
        if (!netz.ruhe || !netz.normalenRoh || netz.normalenRoh.length !== netz.ruhe.length || !(k >= 1 && k <= 4)) return null;
        const { index, gewicht } = Meshgenesiskartenhaut.gewichte(netz, matrizen.length / 12);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(netz.ruhe, 3));
        geo.setAttribute('normal', new THREE.BufferAttribute(netz.normalenRoh, 3, true));     // Int8 normiert: die Karte liest c / 127 wie `Meshgenesisflaechennetz.normalen`
        geo.setAttribute('uv', netz.uvAttribut);
        netz.farbe ??= Meshgenesisflaechen.farben(netz.kopf, netz.dreiecke, netz.etikett);
        geo.setAttribute('color', netz.farbe);
        geo.setAttribute('skinIndex', new THREE.BufferAttribute(index, 4));
        geo.setAttribute('skinWeight', new THREE.BufferAttribute(gewicht, 4, true));
        const materialien = netz.materialien();
        geo.setIndex(new THREE.BufferAttribute(Meshgenesiskartenhaut.index(netz, materialien.length, (ab, n, m) => geo.addGroup(ab, n, m)), 1));
        geo.userData.gemeinsam = true;          // wie `Meshgenesistestnetzbau.mesh`: die Felder geben es beim Zeichnen nicht frei
        for (const m of materialien) m.userData.gemeinsam = true;
        const mesh = new THREE.SkinnedMesh(geo, materialien);
        mesh.bindMode = THREE.DetachedBindMode;
        mesh.bind(Meshgenesiskartenhaut.skelett(matrizen), new THREE.Matrix4());
        mesh.frustumCulled = false;
        Meshgenesiskartenhaut._huelle(mesh, netz, matrizen);
        const proben = new Map();
        mesh.userData.huellproben = schritt => {
            if (!proben.has(schritt)) proben.set(schritt, Meshgenesiskartenhaut.proben(mesh, schritt));
            return proben.get(schritt);
        };
        return mesh;
    }

    /**
     * Die gehäutete Lage jedes `schritt`-ten Punkts (Float64Array, Rahmen des Netzes) für die Kamerahülle (`Fotogenesiskamera.huelle`, 22.11.2026). Die Haltung ist fest, also einmal je Netz
     * statt bei jeder Aufnahme `getVertexPosition` je Punkt — dort je Punkt und Knochen ein Matrixprodukt (Profil am Zauberer: Haar und Bart 233 ms in `Fotogenesiskamera.huelle`). Dieselbe
     * Rechnung in derselben Reihenfolge wie `SkinnedMesh.applyBoneTransform` (Bindematrix und Knocheninverse Einheit): Σ (w / Teiler) · (M · p) — dieselben Zahlen.
     */
    static proben(mesh, schritt) {
        const g = mesh.geometry, p = g.attributes.position.array, si = g.attributes.skinIndex, sw = g.attributes.skinWeight;
        const ki = si.array, kw = sw.array, teiler = sw.normalized && !(kw instanceof Float32Array) ? 2 ** (8 * kw.BYTES_PER_ELEMENT) - 1 : 1;
        const knochen = mesh.skeleton.bones, n = p.length / 3, aus = new Float64Array(Math.ceil(n / schritt) * 3);
        for (let i = 0, o = 0; i < n; i += schritt, o += 3) {
            const x = p[3 * i], y = p[3 * i + 1], z = p[3 * i + 2];
            let ax = 0, ay = 0, az = 0;
            for (let h = 0; h < 4; h++) {
                const w = kw[4 * i + h] / teiler;
                if (w === 0) continue;
                const e = knochen[ki[4 * i + h]].matrixWorld.elements;
                ax += (e[0] * x + e[4] * y + e[8] * z + e[12]) * w;
                ay += (e[1] * x + e[5] * y + e[9] * z + e[13]) * w;
                az += (e[2] * x + e[6] * y + e[10] * z + e[14]) * w;
            }
            aus[o] = ax; aus[o + 1] = ay; aus[o + 2] = az;
        }
        return aus;
    }

    /** Feste Knochen: je Matrix einer (matrixWorld = Matrix, nie neu gerechnet), dazu am Ende der Einheitsknochen; Knocheninverse Einheit. */
    static skelett(matrizen) {
        const zahl = matrizen.length / 12, knochen = [];
        for (let j = 0; j <= zahl; j++) {
            const b = new THREE.Bone(), o = j * 12, m = matrizen;
            if (j < zahl) b.matrix.set(m[o], m[o + 1], m[o + 2], m[o + 3], m[o + 4], m[o + 5], m[o + 6], m[o + 7], m[o + 8], m[o + 9], m[o + 10], m[o + 11], 0, 0, 0, 1);
            b.matrixWorld.copy(b.matrix);
            b.matrixAutoUpdate = false;
            b.matrixWorldAutoUpdate = false;
            knochen.push(b);
        }
        return new THREE.Skeleton(knochen, knochen.map(() => new THREE.Matrix4()));
    }

    /**
     * Der Index nach Material (`Meshgenesistestnetzbau.nachMaterial`, dieselben Gruppen): liegen die Dreiecke schon nach Material und ist keins verborgen, ist das genau die Folge des Pakets —
     * dann seine Dreiecke selbst, ohne Kopie (Zauberer: Haar 25 MB, Bart 17 MB). Gezeichnet wird er nur; Frisur und Bart kürzt keine Maske.
     */
    static index(netz, anzahl, gruppe) {
        // die Läufe hat der Server schon gezählt (24.11.2026, `Meshgenesiskartenvorarbeit`: Haar 2,1 Mio. Punkte, die beiden Schleifen unten 11–15,5 ms im Hauptfaden)
        const laeufe = netz.kopf.laeufe;
        if (!netz.verborgen && Array.isArray(laeufe) && netz.kopf.laeufe_letzter === anzahl - 1) {
            for (const [ab, bis, m] of laeufe) gruppe(ab * 3, (bis - ab) * 3, m);
            return netz.dreiecke;
        }
        const mat = netz.material, letzter = anzahl - 1;
        let sortiert = !netz.verborgen, vor = -1;
        for (let t = 0; sortiert && t < mat.length; t++) {
            const m = mat[t] < 0 ? letzter : mat[t];
            if (m < vor) sortiert = false;
            vor = m;
        }
        if (!sortiert) return Meshgenesistestnetzbau.nachMaterial(netz, anzahl, null, gruppe);
        for (let t = 0; t < mat.length;) {
            const m = mat[t] < 0 ? letzter : mat[t];
            let e = t + 1;
            while (e < mat.length && (mat[e] < 0 ? letzter : mat[e]) === m) e++;
            gruppe(t * 3, (e - t) * 3, m);
            t = e;
        }
        return netz.dreiecke;
    }

    /**
     * Knochen und Gewichte je Punkt für die Karte, vier Plätze. Vier Knochen je Punkt und jede Summe genau 255 (so liefert der Server, Zauberer: alle 3,7 Mio. Punkte): die Felder des Pakets
     * selbst (Gewicht normiert Uint8 = w / 255 = w / Summe wie `verformen`). Sonst neu: Gewichte auf Summe 65535 (normiert Uint16), ohne Gewicht der Einheitsknochen `zahl`.
     */
    static gewichte(netz, zahl) {
        const k = netz.kopf.haut, v = netz.ruhe.length / 3, kn = netz.knochen, g = netz.gewicht;
        if (k === 4) {
            let genau = true;
            // vom Server geprüft (24.11.2026, `Meshgenesiskartenvorarbeit`: Haar hier 10,7–36 ms im Hauptfaden)
            if (netz.kopf.summe255 !== true) for (let i = 0; genau && i < v; i++) genau = g[4 * i] + g[4 * i + 1] + g[4 * i + 2] + g[4 * i + 3] === 255;
            if (genau) return { index: kn, gewicht: g };
        }
        const index = zahl + 1 <= 256 ? new Uint8Array(v * 4) : new Uint16Array(v * 4), gewicht = new Uint16Array(v * 4);
        for (let i = 0; i < v; i++) {
            let summe = 0;
            for (let h = 0; h < k; h++) summe += g[i * k + h];
            if (!summe) {
                index[i * 4] = zahl;
                gewicht[i * 4] = 65535;
                continue;
            }
            let rest = 65535, groesst = -1;
            for (let h = 0; h < k; h++) {
                const w = g[i * k + h];
                if (!w) continue;
                const q = Math.round(65535 * w / summe);
                index[i * 4 + h] = kn[i * k + h];
                gewicht[i * 4 + h] = q;
                rest -= q;
                if (groesst < 0 || w > g[i * k + groesst]) groesst = h;
            }
            gewicht[i * 4 + groesst] += rest;
        }
        return { index, gewicht };
    }

    /**
     * Hülle OHNE Häutung auf der CPU (Edgar, 21.11.2026: „warum auf CPU, das sollte verboten sein!!“): je Knochen der Kasten der Ruhepunkte, die an ihm hängen (jeder `PROBE`-te Punkt),
     * mit der Matrix des Knochens bewegt; die Hülle umfasst alle. Ein gehäuteter Punkt ist eine Mischung seiner bewegten Ruhelagen — er liegt in dieser Hülle (für die Proben). Sie dient
     * nur dem Sortieren der durchsichtigen Netze.
     */
    static _huelle(mesh, netz, m) {
        const k = netz.kopf.haut, p = netz.ruhe, zahl = m.length / 12, kaesten = new Map(), q = new THREE.Vector3();
        // die Kästen je Knochen hat der Server schon gerechnet, über dieselben Proben (24.11.2026, `Meshgenesiskartenvorarbeit`: Haar hier 15,8–18,4 ms im Hauptfaden); −1 = ohne Gewicht
        const fertig = netz.kopf.huelle_probe === Meshgenesiskartenhaut.PROBE && Array.isArray(netz.kopf.huelle) ? netz.kopf.huelle : null;
        for (const [j, ...w] of fertig ?? []) {
            const b = new THREE.Box3(new THREE.Vector3(w[0], w[1], w[2]), new THREE.Vector3(w[3], w[4], w[5])), s = j < 0 ? zahl : j;
            if (kaesten.has(s)) kaesten.get(s).union(b); else kaesten.set(s, b);
        }
        for (let i = 0; !fertig && i < p.length / 3; i += Meshgenesiskartenhaut.PROBE) {
            q.set(p[3 * i], p[3 * i + 1], p[3 * i + 2]);
            let gewichtet = false;
            for (let h = 0; h < k; h++) {
                if (!netz.gewicht[i * k + h]) continue;
                const j = netz.knochen[i * k + h];
                if (!kaesten.has(j)) kaesten.set(j, new THREE.Box3());
                kaesten.get(j).expandByPoint(q);
                gewichtet = true;
            }
            if (!gewichtet) {                                          // am Einheitsknochen: bleibt in Ruhe
                if (!kaesten.has(zahl)) kaesten.set(zahl, new THREE.Box3());
                kaesten.get(zahl).expandByPoint(q);
            }
        }
        const kasten = new THREE.Box3(), matrix = new THREE.Matrix4();
        for (const [j, b] of kaesten) {
            const o = j * 12;
            if (j < zahl) b.applyMatrix4(matrix.set(m[o], m[o + 1], m[o + 2], m[o + 3], m[o + 4], m[o + 5], m[o + 6], m[o + 7], m[o + 8], m[o + 9], m[o + 10], m[o + 11], 0, 0, 0, 1));
            kasten.union(b);
        }
        mesh.boundingBox = kasten;
        mesh.boundingSphere = kasten.getBoundingSphere(new THREE.Sphere());
    }
}
