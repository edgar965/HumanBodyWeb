import * as THREE from 'three';

/**
 * Geometrieflink — Punktnormalen wie three.js (r170) `computeVertexNormals` sie rechnet, dieselben Zahlen, aber direkt auf den Feldern statt über `Vector3` und `getX` je Ecke
 * (24.11.2026, Edgar „fixe“ — lange Bilder beim Laden der Foto-Genesis-Testseite). Gemessen im Chrome an iphone_mit_lidar_dycheck_space_out: die Normalen der Einpassung (25.182 Punkte)
 * 16–19 ms mit three, 9,7 ms hier — beides der erste, noch nicht optimierte Lauf der Seite. Im Tab gegen three an 15 Netzen der Seite (3,6 Mio. Punkte): 0 abweichende Werte;
 * mit einem um 1 mm verschobenen Punkt 12–32.
 *
 * Dieselbe Rechnung in derselben Reihenfolge: je Dreieck (C − B) × (A − B), zu den drei Ecken addiert — erst alle drei gelesen, dann geschrieben wie bei three (ein entartetes Dreieck
 * zählt so nur einmal) —, jede Summe als float32 abgelegt, dann x · (1 / Länge). Nur für schlichte Felder (nicht verschränkt, nicht normiert, nicht float16, drei Werte je Punkt, Index
 * mit ganzen Dreiecken, noch keine Normalen); sonst rechnet three selbst. (Die Hüllkugel ebenso zu rechnen brachte nichts: threes Fassung ist beim Laden schon warm, 16,8 statt 2,7 ms.)
 */
export class Geometrieflink {

    static _schlicht(attr) {
        return !!attr && !attr.isInterleavedBufferAttribute && !attr.isGLBufferAttribute && !attr.isFloat16BufferAttribute && !attr.normalized && attr.itemSize === 3
            && ArrayBuffer.isView(attr.array);
    }

    /** Wie `geo.computeVertexNormals()`. */
    static normalen(geo) {
        const pos = geo.attributes.position, idx = geo.index;
        if (!Geometrieflink._schlicht(pos) || geo.attributes.normal || !idx || idx.isInterleavedBufferAttribute || idx.itemSize !== 1 || !ArrayBuffer.isView(idx.array)
            || idx.count % 3) {
            geo.computeVertexNormals();
            return;
        }
        const p = pos.array, ix = idx.array, z = idx.count, nf = new Float32Array(pos.count * 3);
        for (let i = 0; i < z; i += 3) {
            const a = 3 * ix[i], b = 3 * ix[i + 1], c = 3 * ix[i + 2];
            const bx = p[b], by = p[b + 1], bz = p[b + 2];
            const ux = p[c] - bx, uy = p[c + 1] - by, uz = p[c + 2] - bz;          // cb = C − B
            const vx = p[a] - bx, vy = p[a + 1] - by, vz = p[a + 2] - bz;          // ab = A − B
            const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
            const ax = nf[a] + nx, ay = nf[a + 1] + ny, az = nf[a + 2] + nz;
            const qx = nf[b] + nx, qy = nf[b + 1] + ny, qz = nf[b + 2] + nz;
            const rx = nf[c] + nx, ry = nf[c + 1] + ny, rz = nf[c + 2] + nz;
            nf[a] = ax; nf[a + 1] = ay; nf[a + 2] = az;
            nf[b] = qx; nf[b + 1] = qy; nf[b + 2] = qz;
            nf[c] = rx; nf[c + 1] = ry; nf[c + 2] = rz;
        }
        for (let i = 0; i < nf.length; i += 3) {
            const x = nf[i], y = nf[i + 1], w = nf[i + 2];
            const s = 1 / (Math.sqrt(x * x + y * y + w * w) || 1);
            nf[i] = x * s; nf[i + 1] = y * s; nf[i + 2] = w * s;
        }
        geo.setAttribute('normal', new THREE.BufferAttribute(nf, 3));
    }
}
