/**
 * Dqhautproben — die gehäutete Lage jedes `schritt`-ten Punkts eines Netzes, das `Dqhaut.einschalten` häutet, in EINEM Durchgang (23.11.2026, Edgar: „löse das“ — lange Bilder
 * beim Laden der Foto-Genesis-Testseite).
 *
 * `Fotogenesiskamera.huelle` rief `getVertexPosition` je Punkt, für die Genesis-Figur also `Dqhaut.knochenlage` je Punkt: je Einfluss ein Matrixprodukt, eine Quaternion aus der
 * Matrix und neue Arrays. Gemessen im Tab (/foto-genesis/test/iphone_mit_lidar_dycheck_space_out/, Feld „Genesis-Ergebnis“, 237.000 Proben): 79–121 ms je Aufruf, im Bild mit der
 * fertigen Figur. Hier je Knochen EINMAL Matrix, Quaternion und Dualteil, je Punkt nur Zahlen — dieselben Rechenschritte in derselben Reihenfolge wie `knochenlage`
 * (`Vector3.applyMatrix4` samt Division durch w, `addScaledVector`, Vorzeichen je Einfluss), also dieselben Zahlen wie `getVertexPosition`.
 */
import * as THREE from 'three';
import { Dqhaut } from './dqhaut.js';

export class Dqhautproben {
    /** Ein Netz mit der Häutung von `Dqhaut` (eigenes `applyBoneTransform`, Mischung in `userData.dqMisch`) und ohne Morph-Ziele — nur dann rechnet `getVertexPosition` genau das hier. */
    static gilt(netz) {
        return !!netz?.isSkinnedMesh && Object.hasOwn(netz, 'applyBoneTransform') && Number.isFinite(netz.userData?.dqMisch) && !netz.geometry.morphAttributes?.position;
    }

    /** Je Knochen 24 Zahlen ab `24 · b`: Elemente von matrixWorld · Inverse (16), Quaternion q [w, x, y, z] (4), Dualteil d (4) — wie in `Dqhaut.knochenlage` je Einfluss gerechnet. */
    static _tafel(skelett) {
        const zahl = skelett.bones.length, T = new Float64Array(24 * zahl), m = new THREE.Matrix4();
        for (let b = 0; b < zahl; b++) {
            const e = m.multiplyMatrices(skelett.bones[b].matrixWorld, skelett.boneInverses[b]).elements, q = Dqhaut.drehung(e), t = [e[12], e[13], e[14]];
            T.set(e, 24 * b);
            T.set(q, 24 * b + 16);
            T.set([-0.5 * (t[0] * q[1] + t[1] * q[2] + t[2] * q[3]), 0.5 * (t[0] * q[0] + t[1] * q[3] - t[2] * q[2]),
                   0.5 * (-t[0] * q[3] + t[1] * q[0] + t[2] * q[1]), 0.5 * (t[0] * q[2] - t[1] * q[1] + t[2] * q[0])], 24 * b + 20);
        }
        return T;
    }

    /** Ein Feld, wie `getX` … es liest: eigenes Array, nicht verschränkt, nicht normiert — sonst null (dann bleibt `getVertexPosition`). */
    static _roh(attribut, breite) {
        return attribut && !attribut.isInterleavedBufferAttribute && !attribut.normalized && attribut.itemSize === breite ? attribut.array : null;
    }

    /** Netz → das letzte Ergebnis mit seinem Zustand (`_zustand`, Felder, Schritt): dieselbe Stellung kommt beim Laden mehrmals (Figur fertig, Foto geladen: je 49–86 ms). */
    static _merk = new WeakMap();

    /** Alles, wovon das Ergebnis außer den Feldern abhängt: Mischung, Binde- und Umkehrmatrix, je Knochen matrixWorld und Inverse. */
    static _zustand(netz) {
        const sk = netz.skeleton, n = sk.bones.length, z = new Float64Array(33 + 32 * n);
        z[0] = netz.userData.dqMisch || 0;
        z.set(netz.bindMatrix.elements, 1);
        z.set(netz.bindMatrixInverse.elements, 17);
        for (let b = 0; b < n; b++) {
            z.set(sk.bones[b].matrixWorld.elements, 33 + 32 * b);
            z.set(sk.boneInverses[b].elements, 49 + 32 * b);
        }
        return z;
    }

    /** → Float64Array [x, y, z, …] im Rahmen des Netzes: `netz.getVertexPosition(i, v)` für i = 0, schritt, 2·schritt, … (Skelett und Matrizen wie gerade gestellt); null, wenn ein Feld anders liegt. */
    static proben(netz, schritt) {
        const geo = netz.geometry, P = Dqhautproben._roh(geo.attributes.position, 3), I = Dqhautproben._roh(geo.attributes.skinIndex, 4), W = Dqhautproben._roh(geo.attributes.skinWeight, 4);
        if (!P || !I || !W) return null;
        const zustand = Dqhautproben._zustand(netz), alt = Dqhautproben._merk.get(netz);
        const fassung = `${schritt}/${geo.attributes.position.version}/${geo.attributes.skinIndex.version}/${geo.attributes.skinWeight.version}`;
        if (alt && alt.fassung === fassung && alt.P === P && alt.I === I && alt.W === W && alt.skelett === netz.skeleton && alt.zustand.every((x, i) => x === zustand[i])) return alt.proben;
        const aus = Dqhautproben._rechnen(netz, schritt, P, I, W);
        Dqhautproben._merk.set(netz, { fassung, P, I, W, skelett: netz.skeleton, zustand, proben: aus });
        return aus;
    }

    static _rechnen(netz, schritt, P, I, W) {
        const n = P.length / 3, aus = new Float64Array(Math.ceil(n / schritt) * 3), T = Dqhautproben._tafel(netz.skeleton);
        const B = netz.bindMatrix.elements, BI = netz.bindMatrixInverse.elements, a = netz.userData.dqMisch || 0;
        for (let i = 0, o = 0; i < n; i += schritt, o += 3) {
            const vx = P[3 * i], vy = P[3 * i + 1], vz = P[3 * i + 2];
            // basis = v · bindMatrix (Vector3.applyMatrix4)
            const bw = 1 / (B[3] * vx + B[7] * vy + B[11] * vz + B[15]);
            const rx = (B[0] * vx + B[4] * vy + B[8] * vz + B[12]) * bw, ry = (B[1] * vx + B[5] * vy + B[9] * vz + B[13]) * bw, rz = (B[2] * vx + B[6] * vy + B[10] * vz + B[14]) * bw;
            let lx = 0, ly = 0, lz = 0, s0 = 0, s1 = 0, s2 = 0, s3 = 0, d0 = 0, d1 = 0, d2 = 0, d3 = 0;
            for (let k = 0; k < 4; k++) {
                let w = W[4 * i + k];
                if (w === 0) continue;
                const t = 24 * I[4 * i + k];
                const tw = 1 / (T[t + 3] * rx + T[t + 7] * ry + T[t + 11] * rz + T[t + 15]);
                lx += (T[t] * rx + T[t + 4] * ry + T[t + 8] * rz + T[t + 12]) * tw * w;
                ly += (T[t + 1] * rx + T[t + 5] * ry + T[t + 9] * rz + T[t + 13]) * tw * w;
                lz += (T[t + 2] * rx + T[t + 6] * ry + T[t + 10] * rz + T[t + 14]) * tw * w;
                if (T[t + 16] * s0 + T[t + 17] * s1 + T[t + 18] * s2 + T[t + 19] * s3 < 0) w = -w;
                s0 += w * T[t + 16]; s1 += w * T[t + 17]; s2 += w * T[t + 18]; s3 += w * T[t + 19];
                d0 += w * T[t + 20]; d1 += w * T[t + 21]; d2 += w * T[t + 22]; d3 += w * T[t + 23];
            }
            const w = s0, x = s1, y = s2, z = s3, l2 = w * w + x * x + y * y + z * z, l = l2 > 0 ? 1 / l2 : 0;
            const px = (w * w + x * x - y * y - z * z) * rx + 2 * (x * y - w * z) * ry + 2 * (x * z + w * y) * rz;
            const py = 2 * (x * y + w * z) * rx + (w * w + y * y - x * x - z * z) * ry + 2 * (y * z - w * x) * rz;
            const pz = 2 * (x * z - w * y) * rx + 2 * (y * z + w * x) * ry + (w * w + z * z - x * x - y * y) * rz;
            const tx = 2 * (-d0 * x + w * d1 - d2 * z + y * d3);
            const ty = 2 * (-d0 * y + d1 * z - x * d3 + w * d2);
            const tz = 2 * (-d0 * z + x * d2 + w * d3 - d1 * y);
            const mx = (1 - a) * lx + a * (px + tx) * l, my = (1 - a) * ly + a * (py + ty) * l, mz = (1 - a) * lz + a * (pz + tz) * l;
            // zurück: · bindMatrixInverse (Vector3.applyMatrix4)
            const iw = 1 / (BI[3] * mx + BI[7] * my + BI[11] * mz + BI[15]);
            aus[o] = (BI[0] * mx + BI[4] * my + BI[8] * mz + BI[12]) * iw;
            aus[o + 1] = (BI[1] * mx + BI[5] * my + BI[9] * mz + BI[13]) * iw;
            aus[o + 2] = (BI[2] * mx + BI[6] * my + BI[10] * mz + BI[14]) * iw;
        }
        return aus;
    }
}
