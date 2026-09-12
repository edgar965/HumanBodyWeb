import { Velocityskinning as V } from './velocityskinning.js';

/**
 * Weichgewebeknochen — der Takt des Velocity Skinning je KNOCHEN.
 *
 * Herausgelöst aus `weichgewebekoerper.js` (12.09.2026, Befund `jsfunktionen`:
 * `takt` mit 94 Zeilen). `bild` rechnet, was je Knochen einmal gilt — Tempo,
 * bewegter Schwerpunkt, `T - I` des squashy-Anteils, Drehachse und
 * Achsenkreuz —, `zuschlagen` läuft damit über die Punkte des Knochens.
 *
 * ALLOKATIONSFREI in der Punktschleife: Ein Objekt entsteht je Knochen
 * (höchstens 176 je Takt), in der Schleife darunter nur Zahlen in lokalen
 * Variablen. Die erste Fassung rief je Punkt-Knochen-Paar `V.kreuz`,
 * `V.einheit`, `V.matVek` — drei Millionen Objekte je Bild, der Sammler
 * fror den Renderer sekundenlang ein. Dieselben Formeln, ausgeschrieben.
 *
 * `stufen` = { schwelle, squashy, floppy } — die Konstanten von
 * `Weichgewebekoerper`, floppy und squashy schon mit der Stärke verrechnet.
 */
export class Weichgewebeknochen {

    /**
     * Was je Knochen EINMAL gilt: Tempo, bewegter Schwerpunkt, `T - I` des
     * squashy-Anteils, Drehachse und das Achsenkreuz (medial, längs, quer).
     * `null`, wenn der Knochen weder fährt noch dreht.
     */
    static bild(k, matrizen, gelenke, linear, winkel, stufen, schwerpunktRuhe) {
        const vx = linear[3 * k], vy = linear[3 * k + 1], vz = linear[3 * k + 2];
        const wx = winkel[3 * k], wy = winkel[3 * k + 1], wz = winkel[3 * k + 2];
        const vn = Math.hypot(vx, vy, vz), wn = Math.hypot(wx, wy, wz);
        const bewegt = vn >= stufen.schwelle;
        const dreht = wn >= stufen.schwelle;
        if (!bewegt && !dreht) return null;
        const wS = stufen.squashy;
        const kn = {
            bewegt, dreht, vx, vy, vz, wx, wy, wz, wS,
            wF: stufen.floppy,
            gx: gelenke[3 * k], gy: gelenke[3 * k + 1], gz: gelenke[3 * k + 2],
            // squashy linear: T - I einmal je Knochen (3x3 zeilenweise).
            t: bewegt ? V.squashyLinearMatrix(wS, [vx, vy, vz]) : null,
            cx: 0, cy: 0, cz: 0,
            ux: 0, uy: 0, uz: 0, mx: 0, my: 0, mz: 0,
            lx: 0, ly: 0, lz: 0, qx: 0, qy: 0, qz: 0, kreuzGilt: false,
        };
        const o = 16 * k, sp = schwerpunktRuhe;
        const px = sp[3 * k], py = sp[3 * k + 1], pz = sp[3 * k + 2];
        kn.cx = matrizen[o] * px + matrizen[o + 4] * py + matrizen[o + 8] * pz + matrizen[o + 12];
        kn.cy = matrizen[o + 1] * px + matrizen[o + 5] * py + matrizen[o + 9] * pz + matrizen[o + 13];
        kn.cz = matrizen[o + 2] * px + matrizen[o + 6] * py + matrizen[o + 10] * pz + matrizen[o + 14];
        if (!dreht) return kn;
        // Drehachse und Achsenkreuz einmal je Knochen.
        kn.ux = wx / wn; kn.uy = wy / wn; kn.uz = wz / wn;
        let mx = kn.cx - kn.gx, my = kn.cy - kn.gy, mz = kn.cz - kn.gz;
        const mn = Math.hypot(mx, my, mz);
        if (mn <= 1e-4) return kn;
        mx /= mn; my /= mn; mz /= mn;
        // laengs = medial x achse, quer = medial x laengs
        const lx = my * kn.uz - mz * kn.uy, ly = mz * kn.ux - mx * kn.uz, lz = mx * kn.uy - my * kn.ux;
        const ln = Math.hypot(lx, ly, lz);
        if (ln < 1e-2) return kn;
        kn.mx = mx; kn.my = my; kn.mz = mz;
        kn.lx = lx / ln; kn.ly = ly / ln; kn.lz = lz / ln;
        kn.qx = my * kn.lz - mz * kn.ly; kn.qy = mz * kn.lx - mx * kn.lz; kn.qz = mx * kn.ly - my * kn.lx;
        kn.kreuzGilt = true;
        return kn;
    }

    /** Die Punkte EINES Knochens: floppy (Rodrigues) und squashy auf `aus` addieren. */
    static zuschlagen(kn, idx, gew, lbs, weich, aus) {
        const { bewegt, dreht, vx, vy, vz, wx, wy, wz, wS, wF, gx, gy, gz, cx, cy, cz, t,
                ux, uy, uz, mx, my, mz, lx, ly, lz, qx, qy, qz, kreuzGilt } = kn;
        const MAX = V.HOECHSTWINKEL;
        for (let j = 0; j < idx.length; j++) {
            const i = idx[j], haut = gew[j];
            const wf = wF * weich[i];
            const px = lbs[3 * i], py = lbs[3 * i + 1], pz = lbs[3 * i + 2];
            let dx = 0, dy = 0, dz = 0;
            if (bewegt) {
                dx -= wf * vx; dy -= wf * vy; dz -= wf * vz;
                const rx = px - cx, ry = py - cy, rz = pz - cz;
                dx += t[0] * rx + t[1] * ry + t[2] * rz;
                dy += t[3] * rx + t[4] * ry + t[5] * rz;
                dz += t[6] * rx + t[7] * ry + t[8] * rz;
            }
            if (dreht) {
                const rx = px - gx, ry = py - gy, rz = pz - gz;
                // Bahntempo des Punktes: |w x rel|
                const bx = wy * rz - wz * ry, by = wz * rx - wx * rz, bz = wx * ry - wy * rx;
                const punkttempo = Math.hypot(bx, by, bz);
                // floppy: Rodrigues um -winkel, weich gedeckelt.
                let winkelP = punkttempo * wf;
                if (winkelP > MAX) winkelP = MAX + (winkelP - MAX) / Math.max(punkttempo, 1e-9);
                const c = Math.cos(-winkelP), sn = Math.sin(-winkelP);
                const kx = uy * rz - uz * ry, ky = uz * rx - ux * rz, kz = ux * ry - uy * rx;
                const sk = rx * ux + ry * uy + rz * uz;
                dx += (c - 1) * rx + sn * kx + (1 - c) * sk * ux;
                dy += (c - 1) * ry + sn * ky + (1 - c) * sk * uy;
                dz += (c - 1) * rz + sn * kz + (1 - c) * sk * uz;
                if (kreuzGilt) {
                    // squashy: Rest senkrecht zur Gliedachse, strecken
                    // entlang laengs, stauchen entlang quer.
                    const entlang = rx * mx + ry * my + rz * mz;
                    const ex = rx - entlang * mx, ey = ry - entlang * my, ez = rz - entlang * mz;
                    const f = wS * punkttempo;
                    const l = (ex * lx + ey * ly + ez * lz) * f;
                    const q = (ex * qx + ey * qy + ez * qz) * (-f / (1 + f));
                    dx += l * lx + q * qx; dy += l * ly + q * qy; dz += l * lz + q * qz;
                }
            }
            aus[3 * i] += haut * dx; aus[3 * i + 1] += haut * dy; aus[3 * i + 2] += haut * dz;
        }
    }
}
