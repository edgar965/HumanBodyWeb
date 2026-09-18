/**
 * Stoffarbeiter — der Stoffschwung eines dForce-Stücks in einem Web Worker.
 *
 * WARUM EIN WORKER (18.09.2026): Auf dem Hauptfaden kostete das Dancing-
 * Queen-Kleid 170 ms je Bild (75.977 Browserpunkte, 225.228 Kanten) — die
 * Szene stand. Hier läuft die Rechnung auf dem KÄFIG (18.979 Daz-Punkte,
 * 37.000 Kanten) neben dem Zeichnen, und die Browserpunkte entstehen aus
 * derselben Unterteilungsmatrix wie auf dem Server (CSR, `bauplan`). Der
 * Hauptfaden schickt je Bild die Knochenmatrizen und Kapseln
 * (`genesis9stoffschwung.js`), bekommt Punkte und Normalen zurück und
 * zeichnet, was zuletzt kam — die Figur läuft mit 60 Bildern, der Stoff mit
 * so vielen, wie der Worker schafft.
 *
 * Nachrichten:
 *   bauen  {kaefig (n·3), frei (n), kanten (E·2), indptr, indices, data,
 *           zeilen, hautIndex (n·4), hautGewicht (n·4), dreiecke (Browser)}
 *   bild   {M (Knochen·16), W (16), inv (16), kapseln (K·7), dt}
 *           → punkte {pos (zeilen·3), nrm (zeilen·3)}   (übertragen, nicht kopiert)
 */
import { Stoffpendel } from './stoffpendel.js';

class Stoffarbeiter {

    static pendel = null;
    static kaefig = null;
    static ziel = null;
    static hautIndex = null;
    static hautGewicht = null;
    static matrix = null;
    static dreiecke = null;
    static zeilen = 0;

    static bauen(d) {
        Stoffarbeiter.kaefig = d.kaefig;
        Stoffarbeiter.pendel = Stoffpendel.ausKanten(d.kaefig, d.kanten, d.frei);
        Stoffarbeiter.ziel = new Float32Array(d.kaefig.length);
        // Ganzzahlen als Index — Float32 als Feldindex kostet V8 je Zugriff eine Umwandlung.
        Stoffarbeiter.hautIndex = Uint16Array.from(d.hautIndex);
        Stoffarbeiter.hautGewicht = d.hautGewicht;
        Stoffarbeiter.matrix = { indptr: d.indptr, indices: d.indices, data: d.data };
        Stoffarbeiter.dreiecke = d.dreiecke;
        Stoffarbeiter.zeilen = d.zeilen;
        Stoffarbeiter.erstes = true;
    }

    /** Käfig häuten (wie der Shader) → Welt. */
    static haeuten(M, W) {
        const { kaefig: pos, hautIndex: index, hautGewicht: gewicht, ziel } = Stoffarbeiter;
        const n = pos.length / 3;
        for (let i = 0; i < n; i++) {
            const x = pos[3 * i], y = pos[3 * i + 1], z = pos[3 * i + 2];
            let sx = 0, sy = 0, sz = 0;
            for (let k = 0; k < 4; k++) {
                const w = gewicht[4 * i + k];
                if (w === 0) continue;
                const o = 16 * index[4 * i + k];
                sx += w * (M[o] * x + M[o + 4] * y + M[o + 8] * z + M[o + 12]);
                sy += w * (M[o + 1] * x + M[o + 5] * y + M[o + 9] * z + M[o + 13]);
                sz += w * (M[o + 2] * x + M[o + 6] * y + M[o + 10] * z + M[o + 14]);
            }
            ziel[3 * i] = W[0] * sx + W[4] * sy + W[8] * sz + W[12];
            ziel[3 * i + 1] = W[1] * sx + W[5] * sy + W[9] * sz + W[13];
            ziel[3 * i + 2] = W[2] * sx + W[6] * sy + W[10] * sz + W[14];
        }
        return ziel;
    }

    static bild(d) {
        const { pendel, matrix, zeilen, dreiecke } = Stoffarbeiter;
        if (!pendel) return;
        const zeiten = {}, t0 = performance.now();
        const ziel = Stoffarbeiter.haeuten(d.M, d.W);
        zeiten.haut = performance.now() - t0;
        if (Stoffarbeiter.erstes) { pendel.setzen(ziel); Stoffarbeiter.erstes = false; }
        const kapseln = [];
        for (let k = 0; k + 6 < d.kapseln.length; k += 7) {
            kapseln.push({ a: [d.kapseln[k], d.kapseln[k + 1], d.kapseln[k + 2]],
                           b: [d.kapseln[k + 3], d.kapseln[k + 4], d.kapseln[k + 5]], r: d.kapseln[k + 6] });
        }
        // Große Zeitschritte in zwei Teile — der Pendel deckelt bei MAX_DT.
        const teile = d.dt > Stoffpendel.MAX_DT ? 2 : 1;
        let x = null;
        let t1 = performance.now();
        for (let t = 0; t < teile; t++) x = pendel.schritt(ziel, d.dt / teile, kapseln);
        zeiten.schritt = performance.now() - t1; t1 = performance.now();
        // Browserpunkte = Matrix · Käfig (Welt), dann in den Raum des Anzeigenetzes.
        const pos = new Float32Array(zeilen * 3);
        const { indptr, indices, data } = matrix;
        const inv = d.inv;
        for (let r = 0; r < zeilen; r++) {
            let wx = 0, wy = 0, wz = 0;
            for (let e = indptr[r]; e < indptr[r + 1]; e++) {
                const c = 3 * indices[e], w = data[e];
                wx += w * x[c]; wy += w * x[c + 1]; wz += w * x[c + 2];
            }
            pos[3 * r] = inv[0] * wx + inv[4] * wy + inv[8] * wz + inv[12];
            pos[3 * r + 1] = inv[1] * wx + inv[5] * wy + inv[9] * wz + inv[13];
            pos[3 * r + 2] = inv[2] * wx + inv[6] * wy + inv[10] * wz + inv[14];
        }
        zeiten.matrix = performance.now() - t1; t1 = performance.now();
        const nrm = Stoffarbeiter.normalen(pos, dreiecke, zeilen);
        zeiten.normalen = performance.now() - t1;
        zeiten.gesamt = performance.now() - t0;
        self.postMessage({ typ: 'punkte', pos, nrm, auslenkung: pendel.auslenkung(ziel), zeiten },
                         [pos.buffer, nrm.buffer]);
    }

    /** Flächennormalen auf die Ecken verteilt, normiert (wie `computeVertexNormals`). */
    static normalen(pos, dreiecke, zeilen) {
        const nrm = new Float32Array(zeilen * 3);
        for (let t = 0; t + 2 < dreiecke.length; t += 3) {
            const a = 3 * dreiecke[t], b = 3 * dreiecke[t + 1], c = 3 * dreiecke[t + 2];
            const abx = pos[b] - pos[a], aby = pos[b + 1] - pos[a + 1], abz = pos[b + 2] - pos[a + 2];
            const acx = pos[c] - pos[a], acy = pos[c + 1] - pos[a + 1], acz = pos[c + 2] - pos[a + 2];
            const nx = aby * acz - abz * acy, ny = abz * acx - abx * acz, nz = abx * acy - aby * acx;
            nrm[a] += nx; nrm[a + 1] += ny; nrm[a + 2] += nz;
            nrm[b] += nx; nrm[b + 1] += ny; nrm[b + 2] += nz;
            nrm[c] += nx; nrm[c + 1] += ny; nrm[c + 2] += nz;
        }
        for (let i = 0; i < zeilen; i++) {
            const o = 3 * i, l = Math.hypot(nrm[o], nrm[o + 1], nrm[o + 2]) || 1;
            nrm[o] /= l; nrm[o + 1] /= l; nrm[o + 2] /= l;
        }
        return nrm;
    }
}

self.onmessage = (ereignis) => {
    const d = ereignis.data;
    if (d.typ === 'bauen') Stoffarbeiter.bauen(d);
    else if (d.typ === 'bild') Stoffarbeiter.bild(d);
};
