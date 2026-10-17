/**
 * Mesh3daihaeutung — die Figur einer Probe mit dem VORHERGESAGTEN Rig häuten, damit „Ausgabe des Netzes“ eine Fläche zeigt (15.10.2026, Edgar: „im Ergebnis fenster werden 2 Rigs aber sonst nichts angezeigt“).
 * Das Netz sagt nur die 138 Rig-Punkte voraus, keine Drehungen. Die Drehung je Knochen ist darum eine NÄHERUNG: der kürzeste Bogen von der Richtung „Knochen → Mittel seiner Kinder“ im Soll zur selben Richtung in der
 * Vorhersage (keine Verdrehung um die eigene Achse); Knochen ohne Kinder (Finger- und Zehenspitzen, Gesicht) übernehmen die Drehung ihres Elternknochens. Jeder Punkt der Figur folgt seinen Hautgewichten
 * (`flaeche.npz`, Fassung 2): p' = Σ w · (R · (p − Soll) + Vorhersage). Ausgangslage ist die gehäutete Figur in der Pose des Soll — bei fehlerfreier Vorhersage bleibt sie unverändert.
 */
import * as THREE from 'three';

export class Mesh3daihaeutung {
    /** Je Knochen eine 3×4-Matrix (zeilenweise) für p' = R · p + t mit t = Vorhersage − R · Soll. */
    static knochenmatrizen(soll, ausgabe, eltern) {
        const n = soll.length;
        const kinder = Array.from({ length: n }, () => []);
        eltern.forEach((e, j) => { if (e >= 0 && e < n) kinder[e].push(j); });
        const mittel = (liste, lagen) => liste.reduce((s, j) => s.add(new THREE.Vector3().fromArray(lagen[j])), new THREE.Vector3()).multiplyScalar(1 / liste.length);
        const drehungen = new Array(n);
        const drehung = j => {
            if (drehungen[j]) return drehungen[j];
            if (kinder[j].length) {
                const a = mittel(kinder[j], soll).sub(new THREE.Vector3().fromArray(soll[j]));
                const b = mittel(kinder[j], ausgabe).sub(new THREE.Vector3().fromArray(ausgabe[j]));
                if (a.lengthSq() > 1e-12 && b.lengthSq() > 1e-12) return (drehungen[j] = new THREE.Quaternion().setFromUnitVectors(a.normalize(), b.normalize()));
            }
            return (drehungen[j] = eltern[j] >= 0 ? drehung(eltern[j]) : new THREE.Quaternion());
        };
        const aus = new Float32Array(n * 12);
        const r = new THREE.Matrix4();
        const s = new THREE.Vector3();
        for (let j = 0; j < n; j++) {
            const e = r.makeRotationFromQuaternion(drehung(j)).elements;     // spaltenweise
            s.fromArray(soll[j]).applyMatrix4(r);
            const o = j * 12;
            aus.set([e[0], e[4], e[8], ausgabe[j][0] - s.x, e[1], e[5], e[9], ausgabe[j][1] - s.y, e[2], e[6], e[10], ausgabe[j][2] - s.z], o);
        }
        return aus;
    }

    /**
     * Lauf mit Daz-Winkeln (16.10.2026): je Knochen die Matrix aus der vorhergesagten Drehung gegen die Ruhelage (`dreh`, Quaternion x, y, z, w, schon ausgerichtet), dem vorhergesagten Gelenk
     * (`punkte`) und dem Gelenk in der Ruhelage (`ruhezentren`): p' = R · (p − c) + Gelenk. Angewandt auf die Ruhelage ist das dieselbe Hautmischung wie das Ziel im Datenskript (`Ursula.haeuten`).
     */
    static ausDrehungen(dreh, punkte, ruhezentren) {
        const n = dreh.length;
        const aus = new Float32Array(n * 12);
        const q = new THREE.Quaternion();
        const r = new THREE.Matrix4();
        const c = new THREE.Vector3();
        for (let j = 0; j < n; j++) {
            const e = r.makeRotationFromQuaternion(q.set(dreh[j][0], dreh[j][1], dreh[j][2], dreh[j][3])).elements;      // spaltenweise
            c.fromArray(ruhezentren[j]).applyMatrix4(r);
            aus.set([e[0], e[4], e[8], punkte[j][0] - c.x, e[1], e[5], e[9], punkte[j][1] - c.y, e[2], e[6], e[10], punkte[j][2] - c.z], j * 12);
        }
        return aus;
    }

    /** @param {Float32Array} lage Punkte (V·3) in der Pose des Soll (Näherung) oder in der Ruhelage (`ausDrehungen`) @param {Uint8Array} knochen, gewicht (V·K, Gewicht ×255) @returns {Float32Array} die verformten Punkte */
    static verformen(lage, knochen, gewicht, k, m) {
        const v = lage.length / 3;
        const aus = new Float32Array(lage.length);
        for (let i = 0; i < v; i++) {
            const px = lage[i * 3], py = lage[i * 3 + 1], pz = lage[i * 3 + 2];
            let x = 0, y = 0, z = 0, summe = 0;
            for (let h = 0; h < k; h++) {
                const w = gewicht[i * k + h];
                if (!w) continue;
                const o = knochen[i * k + h] * 12;
                x += w * (m[o] * px + m[o + 1] * py + m[o + 2] * pz + m[o + 3]);
                y += w * (m[o + 4] * px + m[o + 5] * py + m[o + 6] * pz + m[o + 7]);
                z += w * (m[o + 8] * px + m[o + 9] * py + m[o + 10] * pz + m[o + 11]);
                summe += w;
            }
            if (summe > 0) {
                aus[i * 3] = x / summe;
                aus[i * 3 + 1] = y / summe;
                aus[i * 3 + 2] = z / summe;
            } else {
                aus[i * 3] = px;
                aus[i * 3 + 1] = py;
                aus[i * 3 + 2] = pz;
            }
        }
        return aus;
    }
}
