/**
 * Mesh3daiausrichtung — die starre Abbildung (Drehung + Verschiebung), die Punktpaare a → b am besten deckt (19.10.2026).
 *
 * Die Felder der Jobseite stehen im ausgerichteten Rahmen der Probe (Rig `probe.rig.soll`); die Genesis-Figur kommt vom Server in ihrem eigenen Rahmen (Wurzel in Ruhe). Ihre Gelenke und das Rig sind
 * dieselben 138 Knochen derselben Figur in derselben Haltung — die Abbildung zwischen ihnen ist starr. Verfahren nach Horn (1987, „Closed-form solution of absolute orientation using unit quaternions“):
 * die Quaternion ist der Eigenvektor zum größten Eigenwert der symmetrischen 4×4-Matrix aus der Kreuzkovarianz; Eigenvektoren hier mit Jacobi-Drehungen.
 */
import * as THREE from 'three';

export class Mesh3daiausrichtung {
    /**
     * @param {number[][]} a Punkte im Rahmen der Figur
     * @param {number[][]} b dieselben Punkte im Rahmen der Seite
     * @returns {{quaternion: THREE.Quaternion, verschiebung: THREE.Vector3, rest_mm: number}}
     */
    static starr(a, b) {
        const n = a.length;
        const ca = [0, 0, 0], cb = [0, 0, 0];
        for (let i = 0; i < n; i++) for (let k = 0; k < 3; k++) { ca[k] += a[i][k] / n; cb[k] += b[i][k] / n; }
        const s = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
        for (let i = 0; i < n; i++) {
            for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) s[r][c] += (a[i][r] - ca[r]) * (b[i][c] - cb[c]);
        }
        const [[xx, xy, xz], [yx, yy, yz], [zx, zy, zz]] = s;
        const m = [
            [xx + yy + zz, yz - zy, zx - xz, xy - yx],
            [yz - zy, xx - yy - zz, xy + yx, zx + xz],
            [zx - xz, xy + yx, -xx + yy - zz, yz + zy],
            [xy - yx, zx + xz, yz + zy, -xx - yy + zz],
        ];
        const [werte, vektoren] = Mesh3daiausrichtung._jacobi(m);
        let best = 0;
        for (let i = 1; i < 4; i++) if (werte[i] > werte[best]) best = i;
        const q = new THREE.Quaternion(vektoren[1][best], vektoren[2][best], vektoren[3][best], vektoren[0][best]).normalize();
        const t = new THREE.Vector3(...cb).sub(new THREE.Vector3(...ca).applyQuaternion(q));
        let summe = 0;
        const p = new THREE.Vector3();
        for (let i = 0; i < n; i++) summe += p.fromArray(a[i]).applyQuaternion(q).add(t).distanceTo(new THREE.Vector3(...b[i]));
        return { quaternion: q, verschiebung: t, rest_mm: 1000 * summe / Math.max(n, 1) };
    }

    /** Eigenwerte und Eigenvektoren (Spalten) einer symmetrischen 4×4-Matrix. */
    static _jacobi(eingabe) {
        const a = eingabe.map(z => z.slice());
        const v = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
        for (let runde = 0; runde < 60; runde++) {
            let p = 0, q = 1, groesste = 0;
            for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) if (Math.abs(a[i][j]) > groesste) { groesste = Math.abs(a[i][j]); p = i; q = j; }
            if (groesste < 1e-14) break;
            const theta = (a[q][q] - a[p][p]) / (2 * a[p][q]);
            const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
            const c = 1 / Math.sqrt(t * t + 1), s = t * c;
            for (let k = 0; k < 4; k++) {
                const akp = a[k][p], akq = a[k][q];
                a[k][p] = c * akp - s * akq;
                a[k][q] = s * akp + c * akq;
            }
            for (let k = 0; k < 4; k++) {
                const apk = a[p][k], aqk = a[q][k];
                a[p][k] = c * apk - s * aqk;
                a[q][k] = s * apk + c * aqk;
            }
            for (let k = 0; k < 4; k++) {
                const vkp = v[k][p], vkq = v[k][q];
                v[k][p] = c * vkp - s * vkq;
                v[k][q] = s * vkp + c * vkq;
            }
        }
        return [[a[0][0], a[1][1], a[2][2], a[3][3]], v];
    }
}
