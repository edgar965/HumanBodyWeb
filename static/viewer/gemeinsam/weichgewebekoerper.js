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
import { Weichgewebeknochen } from './weichgewebeknochen.js';

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
            if (s > 1e-9) {
                this.schwerpunktRuhe[3 * k] = x / s;
                this.schwerpunktRuhe[3 * k + 1] = y / s;
                this.schwerpunktRuhe[3 * k + 2] = z / s;
            }
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
     *
     * Die Rechnung je Knochen steht in `weichgewebeknochen.js` — dort auch,
     * warum sie ausgeschrieben und allokationsfrei ist.
     */
    takt(matrizen, gelenke, linear, winkel, staerke) {
        const aus = this.zuschlag;
        aus.fill(0);
        if (staerke <= 0) return aus;
        const lbs = this._skinning(matrizen);
        const stufen = { schwelle: Weichgewebekoerper.SCHWELLE,
                         squashy: Weichgewebekoerper.SQUASHY * staerke,
                         floppy: Weichgewebekoerper.FLOPPY * staerke };
        for (let k = 0; k < this.b; k++) {
            const { idx, gew } = this.punkteJeKnochen[k];
            if (!idx.length) continue;
            const kn = Weichgewebeknochen.bild(k, matrizen, gelenke, linear, winkel,
                                             stufen, this.schwerpunktRuhe);
            if (kn) Weichgewebeknochen.zuschlagen(kn, idx, gew, lbs, this.weich, aus);
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
