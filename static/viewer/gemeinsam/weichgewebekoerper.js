/**
 * Weichgewebekoerper — Velocity Skinning für EIN gehäutetes Netz, je Bild.
 *
 * Ohne Three.js: bekommt Ruhepunkte, Hautgewichte, Knochenkette und je Bild
 * die Knochenmatrizen samt Geschwindigkeiten als flache Felder, gibt den
 * Zuschlag je Punkt zurück. Die Formeln stehen in `velocityskinning.js`;
 * hier steht, was das Original um sie herum baut (`skinning.cpp`):
 *
 *   Ahnengewichte     Zeile 1259–1294: jeder Punkt hängt mit seinem Gewicht
 *                     auch an ALLEN Vorfahren seines Knochens. Ohne das
 *                     spürt eine Hand die Beckendrehung nicht.
 *   Schwerpunkt       Zeile 1493–1537: je Knochen, flächengewichtet.
 *   Hauptschleife     Zeile 108–197.
 *
 * ZWEI NÄHERUNGEN gegenüber der Python-Fassung, beide wegen der Bildrate:
 *
 * 1. Der Schwerpunkt wird EINMAL in Ruhe gerechnet und je Bild mit der
 *    Knochenmatrix mitgeführt, statt je Bild auf dem verformten Netz neu.
 *    Das Original rechnet ihn je Bild; auf 70.851 Punkten und 140.000
 *    Dreiecken wären das je Bild mehr Arbeit als der Zuschlag selbst. Der
 *    Schwerpunkt eines Gliedes bewegt sich mit dem Glied — der Unterschied
 *    ist zweiter Ordnung.
 * 2. Die Weichheit kommt aus dem Gelenkabstand ohne Netzglättung — die
 *    Nachbarliste des unterteilten Netzes zu bauen kostet beim Einschalten
 *    eine Sekunde, die der Regler nicht warten soll. Die Unterteilung
 *    (Catmull-Clark) glättet ohnehin.
 */
import { Velocityskinning as V } from './velocityskinning.js';

export class Weichgewebekoerper {
    /** `skinning.cpp` 110–111. */
    static FLOPPY = 0.4;
    static SQUASHY = 0.1;
    /** Zeile 145 und 165: darunter keine Drehachse. */
    static SCHWELLE = 1e-3;
    /** Hautgewichte unter dieser Grenze zählen nicht als Bindung. */
    static GEWICHTSGRENZE = 1e-4;

    /**
     * @param ruhe        Float32Array n*3, Ruhepunkte im Netzraum
     * @param skinIndex   Uint16/Float32 n*4, Knochennummern
     * @param skinWeight  Float32Array n*4
     * @param eltern      Int32Array b, Elternnummer je Knochen, -1 = Wurzel
     * @param gelenkeRuhe Float32Array b*3, Gelenke in Ruhe im Netzraum
     */
    constructor(ruhe, skinIndex, skinWeight, eltern, gelenkeRuhe) {
        this.n = ruhe.length / 3;
        this.b = eltern.length;
        this.ruhe = ruhe;
        this.eltern = eltern;
        this.gelenkeRuhe = gelenkeRuhe;
        this.zuschlag = new Float32Array(this.n * 3);
        this._lbs = new Float64Array(this.n * 3);
        // Zwischenfeld fuer die Drehformeln: sie lesen `punkte[3*i]` und
        // schreiben `aus[3*i]` — dieselbe Indizierung wie im Fixture-Test.
        this._tmp = new Float64Array(this.n * 3);
        this._ahnen(skinIndex, skinWeight);
        this._weichheit(skinIndex, skinWeight);
        this._schwerpunkte();
        this.staerke = 0;
    }

    // --------------------------------------------------------- Vorbereitung

    /** Kette vom Knochen bis zur Wurzel, als Nummernliste. */
    _kette(k) {
        const aus = [];
        const gesehen = new Set();
        while (k >= 0 && k < this.b && !gesehen.has(k)) {
            gesehen.add(k);
            aus.push(k);
            k = this.eltern[k];
        }
        return aus;
    }

    /**
     * Ahnengewichte als CSR je KNOCHEN: welche Punkte hängen mit welchem
     * Gewicht an ihm. Die Hauptschleife läuft je Knochen über seine Punkte
     * (`vertex_depending_on_joint`, Zeile 1306), nicht je Punkt über seine
     * Knochen — so wird ein stillstehender Knochen ganz übersprungen.
     */
    _ahnen(skinIndex, skinWeight) {
        const ketten = [];
        for (let k = 0; k < this.b; k++) ketten.push(this._kette(k));
        const jeKnochen = Array.from({ length: this.b }, () => []);
        const skinIdx = new Int32Array(this.n * 4);
        this.skinWeight = new Float32Array(this.n * 4);
        for (let i = 0; i < this.n; i++) {
            const summe = new Map();
            for (let j = 0; j < 4; j++) {
                const w = skinWeight[4 * i + j];
                const k = Math.round(skinIndex[4 * i + j]);
                skinIdx[4 * i + j] = k;
                this.skinWeight[4 * i + j] = w;
                if (w < Weichgewebekoerper.GEWICHTSGRENZE || k < 0 || k >= this.b) continue;
                for (const ahn of ketten[k]) summe.set(ahn, (summe.get(ahn) || 0) + w);
            }
            for (const [k, w] of summe) jeKnochen[k].push(i, w);
        }
        this.skinIndex = skinIdx;
        this.punkteJeKnochen = jeKnochen.map((liste) => {
            const idx = new Int32Array(liste.length / 2);
            const gew = new Float32Array(liste.length / 2);
            for (let j = 0; j < idx.length; j++) { idx[j] = liste[2 * j]; gew[j] = liste[2 * j + 1]; }
            return { idx, gew };
        });
    }

    /** Weichheit 0..1 je Punkt: Abstand zum Gelenk des stärksten Knochens,
     *  bezogen auf die Knochenlänge (siehe `weichheit.py`). */
    _weichheit(skinIndex, skinWeight) {
        this.weich = new Float32Array(this.n);
        const laenge = new Float32Array(this.b);
        for (let k = 0; k < this.b; k++) {
            const e = this.eltern[k];
            if (e >= 0) {
                laenge[k] = Math.hypot(this.gelenkeRuhe[3 * k] - this.gelenkeRuhe[3 * e],
                                       this.gelenkeRuhe[3 * k + 1] - this.gelenkeRuhe[3 * e + 1],
                                       this.gelenkeRuhe[3 * k + 2] - this.gelenkeRuhe[3 * e + 2]);
            }
            if (laenge[k] < 1e-4) laenge[k] = 0.1;
        }
        for (let i = 0; i < this.n; i++) {
            let best = -1, bw = 0;
            for (let j = 0; j < 4; j++) {
                if (skinWeight[4 * i + j] > bw) { bw = skinWeight[4 * i + j]; best = Math.round(skinIndex[4 * i + j]); }
            }
            if (best < 0 || best >= this.b) continue;
            const d = Math.hypot(this.ruhe[3 * i] - this.gelenkeRuhe[3 * best],
                                 this.ruhe[3 * i + 1] - this.gelenkeRuhe[3 * best + 1],
                                 this.ruhe[3 * i + 2] - this.gelenkeRuhe[3 * best + 2]);
            this.weich[i] = Math.min(1, d / laenge[best]);
        }
    }

    /** Schwerpunkt je Knochen in Ruhe, gewichtet mit den Ahnengewichten. */
    _schwerpunkte() {
        this.schwerpunktRuhe = new Float32Array(this.b * 3);
        for (let k = 0; k < this.b; k++) {
            const { idx, gew } = this.punkteJeKnochen[k];
            let x = 0, y = 0, z = 0, s = 0;
            for (let j = 0; j < idx.length; j++) {
                const i = idx[j], w = gew[j];
                x += w * this.ruhe[3 * i]; y += w * this.ruhe[3 * i + 1]; z += w * this.ruhe[3 * i + 2];
                s += w;
            }
            if (s > 1e-9) { this.schwerpunktRuhe[3 * k] = x / s; this.schwerpunktRuhe[3 * k + 1] = y / s; this.schwerpunktRuhe[3 * k + 2] = z / s; }
        }
    }

    // ---------------------------------------------------------------- Bild

    /** p = M * p0 für eine 4x4 in Spaltenfolge (Three.js `elements`). */
    static _anwenden(m, o, x, y, z) {
        return [m[o] * x + m[o + 4] * y + m[o + 8] * z + m[o + 12],
                m[o + 1] * x + m[o + 5] * y + m[o + 9] * z + m[o + 13],
                m[o + 2] * x + m[o + 6] * y + m[o + 10] * z + m[o + 14]];
    }

    /** LBS je Punkt aus den Knochenmatrizen — dieselbe Rechnung wie der Shader. */
    _skinning(matrizen) {
        const lbs = this._lbs, r = this.ruhe;
        for (let i = 0; i < this.n; i++) {
            const x = r[3 * i], y = r[3 * i + 1], z = r[3 * i + 2];
            let px = 0, py = 0, pz = 0;
            for (let j = 0; j < 4; j++) {
                const w = this.skinWeight[4 * i + j];
                if (w < Weichgewebekoerper.GEWICHTSGRENZE) continue;
                const o = 16 * this.skinIndex[4 * i + j];
                px += w * (matrizen[o] * x + matrizen[o + 4] * y + matrizen[o + 8] * z + matrizen[o + 12]);
                py += w * (matrizen[o + 1] * x + matrizen[o + 5] * y + matrizen[o + 9] * z + matrizen[o + 13]);
                pz += w * (matrizen[o + 2] * x + matrizen[o + 6] * y + matrizen[o + 10] * z + matrizen[o + 14]);
            }
            lbs[3 * i] = px; lbs[3 * i + 1] = py; lbs[3 * i + 2] = pz;
        }
        return lbs;
    }

    /**
     * Ein Bild. `matrizen` sind b*16 (Netzraum, wie `skeleton.boneMatrices`
     * nach `bindMatrixInverse`), `gelenke` b*3 im selben Raum, `linear` und
     * `winkel` b*3 die Geschwindigkeiten (`knochentempo.js`).
     * Schreibt `this.zuschlag` (n*3).
     */
    takt(matrizen, gelenke, linear, winkel, staerke) {
        const aus = this.zuschlag;
        aus.fill(0);
        if (staerke <= 0) return aus;
        const lbs = this._skinning(matrizen);
        const wS = Weichgewebekoerper.SQUASHY * staerke;
        const wF = Weichgewebekoerper.FLOPPY * staerke;
        const MAX = V.HOECHSTWINKEL;
        const weich = this.weich;
        // ALLOKATIONSFREI. Die erste Fassung rief je Punkt-Knochen-Paar
        // `V.kreuz`, `V.einheit`, `V.matVek` — jede gibt ein neues Feld
        // zurück. Bei rund 600.000 Paaren je Bild (70.851 Punkte, im Mittel
        // neun Ahnen) sind das drei Millionen Objekte je Bild; der Sammler
        // fror den Renderer sekundenlang ein. Hier nur Zahlen in lokalen
        // Variablen — dieselben Formeln, ausgeschrieben.
        for (let k = 0; k < this.b; k++) {
            const { idx, gew } = this.punkteJeKnochen[k];
            if (!idx.length) continue;
            const vx = linear[3 * k], vy = linear[3 * k + 1], vz = linear[3 * k + 2];
            const wx = winkel[3 * k], wy = winkel[3 * k + 1], wz = winkel[3 * k + 2];
            const vn = Math.hypot(vx, vy, vz), wn = Math.hypot(wx, wy, wz);
            const bewegt = vn >= Weichgewebekoerper.SCHWELLE;
            const dreht = wn >= Weichgewebekoerper.SCHWELLE;
            if (!bewegt && !dreht) continue;
            const gx = gelenke[3 * k], gy = gelenke[3 * k + 1], gz = gelenke[3 * k + 2];
            const o = 16 * k, sp = this.schwerpunktRuhe;
            const cx = matrizen[o] * sp[3 * k] + matrizen[o + 4] * sp[3 * k + 1] + matrizen[o + 8] * sp[3 * k + 2] + matrizen[o + 12];
            const cy = matrizen[o + 1] * sp[3 * k] + matrizen[o + 5] * sp[3 * k + 1] + matrizen[o + 9] * sp[3 * k + 2] + matrizen[o + 13];
            const cz = matrizen[o + 2] * sp[3 * k] + matrizen[o + 6] * sp[3 * k + 1] + matrizen[o + 10] * sp[3 * k + 2] + matrizen[o + 14];
            // squashy linear: T - I einmal je Knochen (3x3 zeilenweise).
            let t = null;
            if (bewegt) t = V.squashyLinearMatrix(wS, [vx, vy, vz]);
            // Drehachse und Achsenkreuz einmal je Knochen.
            let ux = 0, uy = 0, uz = 0, lx = 0, ly = 0, lz = 0, qx = 0, qy = 0, qz = 0;
            let mx = 0, my = 0, mz = 0, kreuzGilt = false;
            if (dreht) {
                ux = wx / wn; uy = wy / wn; uz = wz / wn;
                mx = cx - gx; my = cy - gy; mz = cz - gz;
                const mn = Math.hypot(mx, my, mz);
                if (mn > 1e-4) {
                    mx /= mn; my /= mn; mz /= mn;
                    // laengs = medial x achse, quer = medial x laengs
                    lx = my * uz - mz * uy; ly = mz * ux - mx * uz; lz = mx * uy - my * ux;
                    const ln = Math.hypot(lx, ly, lz);
                    if (ln >= 1e-2) {
                        lx /= ln; ly /= ln; lz /= ln;
                        qx = my * lz - mz * ly; qy = mz * lx - mx * lz; qz = mx * ly - my * lx;
                        kreuzGilt = true;
                    }
                }
            }
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
        return aus;
    }

    /** Größter Zuschlag des letzten Bildes, in Metern — die Probe. */
    groesster() {
        let m = 0;
        for (let i = 0; i < this.n; i++) {
            const l = Math.hypot(this.zuschlag[3 * i], this.zuschlag[3 * i + 1], this.zuschlag[3 * i + 2]);
            if (l > m) m = l;
        }
        return m;
    }
}
