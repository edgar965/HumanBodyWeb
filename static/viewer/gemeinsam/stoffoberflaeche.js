/**
 * Stoffoberflaeche — die Haut der Figur als Körper für den Stoffschwung:
 * eine Stichprobe der Hautpunkte (mit Normalen), je Bild wie der Shader
 * gehäutet, in ein Raster gelegt, und jeder freie Stoffpunkt, der hinter
 * seinem nächsten Hautpunkt liegt, wird entlang dessen Normale herausgesetzt.
 *
 * WARUM (20.09.2026, Edgar mit Bild: HumanBody im Dancing Queen Dress, der
 * Rock im Becken): Die Kapseln (`stoffkoerper.js`) sind je Knochen EINE
 * Kegelkapsel — was die Haut außerhalb davon tut (Gesäß, Bauch, das Becken
 * ohne eigenen Knochen auf Rigify: `DEF-spine` zeigt zum Mittel von fünf
 * Kindern, ein paar Zentimeter), sieht keine Kapsel. Gemessen im Browser:
 * Ursula, Idle, Haut p1 −8 mm, Jump −31 mm; HumanBody, Idle, −39 mm ab dem
 * ersten Bild — mit einem Kleid, das in Ruhe nirgends tiefer als 3,8 mm in
 * der Haut liegt (`_wegwerf/hb_kaefigprobe.py`). Das Maß der Probe ist
 * genau dieses: der nächste Hautpunkt und seine Normale (`Kleidungsmass.tiefen`).
 * Also wird gegen dasselbe gerechnet. Die Kapseln bleiben davor — sie holen
 * einen Punkt aus der Tiefe eines Schenkels, wo die nächste Hautnormale in
 * jede Richtung zeigen kann.
 *
 * WAS ES KOSTET: Die Stichprobe ist ein Punkt je Rasterzelle der Ruhelage
 * (`Stoffhaut.stichprobe`, Zelle 2,5 cm) — ~3.500 statt 70k (HumanBody) oder
 * 104k (Genesis 9). Häuten, Raster (Zählsortierung, keine Map), 27 Zellen
 * je Stoffpunkt, aber nur für Stoffpunkte in einer Zelle, die einen Hautpunkt
 * in der Nachbarschaft hat; einmal je Bild nach dem letzten Teilschritt.
 *
 * GEDÄCHTNIS (20.09.2026, Browser, Ursula im Kleid: `hinaus` 24 ms von 62 je
 * Bild — jeder der 19k Käfigpunkte suchte jedes Bild 27 bis 54 Zellen ab,
 * 3.700 davon fanden nichts): Je Stoffpunkt bleibt vom letzten Mal, wie weit
 * er vor seinem nächsten Hautpunkt lag (ohne einen: `REICHWEITE`). Je Bild
 * geht davon das Doppelte seines eigenen Wegs und des weitesten Wegs eines
 * Hautpunkts in seiner Umgebung ab (Raster `NAH`, ±1 Zelle — was außerhalb
 * liegt, ist mindestens `NAH` entfernt und kommt in einem Bild nicht in
 * Reichweite; läuft irgendein Hautpunkt weiter als `REICHWEITE`, wird alles
 * geprüft). Solange die Schranke über `abstand` + `RESERVE` bleibt, kann der
 * Punkt nicht hinter der Haut sein — keine Suche. Das Doppelte deckt die
 * Drehung der Haut mit. `test_js_stoffoberflaeche` Fall 3.
 *
 * Ohne Three.js — `test_js_stoffoberflaeche` prüft es in Node.
 */
export class Stoffoberflaeche {

    /** Zwei Raster über denselben Punkten: ein feines (2,5 cm) für die Suche in der Nähe -
     *  die meisten Stoffpunkte nahe der Haut liegen auf `abstand` davor - und ein grobes
     *  (5 cm = `REICHWEITE`) für die, die das feine nicht findet; 27 Zellen je Suche statt 125
     *  (Node, 19k Käfigpunkte: 22 ms → siehe `_wegwerf/pendel_zeit2.mjs`). Das grobe trägt
     *  auch die Nähe-Marke: ohne Hautpunkt in den 27 Zellen ringsum ist der Stoffpunkt fern. */
    static ZELLE = 0.025;
    static GROB = 0.05;
    /** Bis hierher (m) zählt ein Hautpunkt als nächster; weiter weg hält nichts (die Kapseln
     *  holen, was tiefer drin ist). 3 cm reichten nicht: ein Rock, der ins Becken gefallen war,
     *  lag 38 mm tief und blieb dort (HumanBody, Idle, 20.09.2026). */
    static REICHWEITE = 0.05;
    /** Reserve (m) auf die Schranke des Gedächtnisses: der nächste Hautpunkt kann wechseln,
     *  die Stichprobe ist 2,5 cm grob. */
    static RESERVE = 0.002;
    /** Raster (m) der Bewegungsmarke: je Zelle der weiteste Weg eines Hautpunkts in ihr oder ±1. */
    static NAH = 0.10;
    static EIMER = 1 << 17;

    /**
     * @param probe `{n, pos (n·3, Ruhe, lokal), nrm (n·3), index (n·4), gewicht (n·4)}`
     */
    constructor(probe) {
        this.n = probe.n;
        this.pos = probe.pos; this.nrm = probe.nrm;
        this.index = Uint16Array.from(probe.index); this.gewicht = probe.gewicht;
        this.welt = new Float32Array(this.n * 3);
        this.normale = new Float32Array(this.n * 3);
        /** Je Hautpunkt: sein Weg (m) seit dem vorigen Häuten; `bewegtMax` das Meiste davon;
         *  `bewegtNah` je `NAH`-Zelle das Meiste in ihr und ±1. */
        this.gehaeutet = false;
        this.bewegt = new Float32Array(this.n);
        this.bewegtMax = Infinity;
        this.bewegtNah = new Float32Array(Stoffoberflaeche.EIMER);
        /** Je Stoffpunkt (angelegt beim ersten `hinaus`): Schranke und Lage bei der letzten Prüfung. */
        this.merker = null;
        this.fein = Stoffoberflaeche._raster0(this.n, Stoffoberflaeche.ZELLE);
        this.grob = Stoffoberflaeche._raster0(this.n, Stoffoberflaeche.GROB);
        /** Je grober Zelle: liegt in ihr oder einer Nachbarzelle ein Hautpunkt? Sonst ist der Stoffpunkt fern. */
        this.nahe = new Uint8Array(Stoffoberflaeche.EIMER);
    }

    /** Ein leeres Raster (Zählsortierung) mit Zellweite `w`. */
    static _raster0(n, w) {
        return { w, zelle: new Int32Array(n), start: new Int32Array(Stoffoberflaeche.EIMER + 1),
                 fuell: new Int32Array(Stoffoberflaeche.EIMER), eintrag: new Int32Array(n) };
    }

    /** Häuten wie der Shader (`M`: je Knochen 16, `W`: matrixWorld) — Punkte und Normalen in die Welt, dann das Raster. */
    haeuten(M, W) {
        const { n, pos, nrm, index, gewicht, welt, normale, bewegt } = this;
        const alt = this.gehaeutet;
        let bewegtMax = 0;
        for (let i = 0; i < n; i++) {
            const x = pos[3 * i], y = pos[3 * i + 1], z = pos[3 * i + 2];
            const nx = nrm[3 * i], ny = nrm[3 * i + 1], nz = nrm[3 * i + 2];
            let sx = 0, sy = 0, sz = 0, tx = 0, ty = 0, tz = 0;
            for (let k = 0; k < 4; k++) {
                const w = gewicht[4 * i + k];
                if (w === 0) continue;
                const o = 16 * index[4 * i + k];
                sx += w * (M[o] * x + M[o + 4] * y + M[o + 8] * z + M[o + 12]);
                sy += w * (M[o + 1] * x + M[o + 5] * y + M[o + 9] * z + M[o + 13]);
                sz += w * (M[o + 2] * x + M[o + 6] * y + M[o + 10] * z + M[o + 14]);
                tx += w * (M[o] * nx + M[o + 4] * ny + M[o + 8] * nz);
                ty += w * (M[o + 1] * nx + M[o + 5] * ny + M[o + 9] * nz);
                tz += w * (M[o + 2] * nx + M[o + 6] * ny + M[o + 10] * nz);
            }
            const ax = welt[3 * i], ay = welt[3 * i + 1], az = welt[3 * i + 2];
            welt[3 * i] = W[0] * sx + W[4] * sy + W[8] * sz + W[12];
            welt[3 * i + 1] = W[1] * sx + W[5] * sy + W[9] * sz + W[13];
            welt[3 * i + 2] = W[2] * sx + W[6] * sy + W[10] * sz + W[14];
            if (alt) {
                const bx = welt[3 * i] - ax, by = welt[3 * i + 1] - ay, bz = welt[3 * i + 2] - az;
                bewegt[i] = Math.sqrt(bx * bx + by * by + bz * bz);
                if (bewegt[i] > bewegtMax) bewegtMax = bewegt[i];
            }
            const wx = W[0] * tx + W[4] * ty + W[8] * tz, wy = W[1] * tx + W[5] * ty + W[9] * tz;
            const wz = W[2] * tx + W[6] * ty + W[10] * tz, l = Math.sqrt(wx * wx + wy * wy + wz * wz) || 1;
            normale[3 * i] = wx / l; normale[3 * i + 1] = wy / l; normale[3 * i + 2] = wz / l;
        }
        // Beim ersten Häuten gibt es keinen Weg: alles gilt als bewegt (`hinaus` prüft jeden Punkt).
        this.bewegtMax = alt ? bewegtMax : Infinity;
        this.gehaeutet = true;
        this._raster(this.fein);
        this._raster(this.grob);
        this._naehe();
        return this;
    }

    /** Das Gedächtnis für `n` Stoffpunkte — neu, wenn es keins gibt oder die Zahl nicht passt. */
    _merker(n) {
        if (this.merker?.n === n) return this.merker;
        const m = { n, schranke: new Float32Array(n), x: new Float32Array(3 * n) };
        m.schranke.fill(-Infinity);
        this.merker = m;
        return m;
    }

    /** Zählsortierung der Weltpunkte in die Zellen eines Rasters (`start[z] .. start[z+1]` → `eintrag`). */
    _raster(r) {
        const { n, welt } = this, { w, zelle, start, fuell, eintrag } = r;
        start.fill(0);
        for (let i = 0; i < n; i++) {
            const z = Stoffoberflaeche._hash(Math.floor(welt[3 * i] / w), Math.floor(welt[3 * i + 1] / w),
                                             Math.floor(welt[3 * i + 2] / w));
            zelle[i] = z; start[z + 1]++;
        }
        for (let z = 0; z < Stoffoberflaeche.EIMER; z++) start[z + 1] += start[z];
        fuell.set(start.subarray(0, Stoffoberflaeche.EIMER));
        for (let i = 0; i < n; i++) eintrag[fuell[zelle[i]]++] = i;
    }

    /** Nähe: die 27 groben Zellen um jeden Hautpunkt. Der Rock hängt zum größten Teil fern
     *  der Haut - ohne diese Marke suchte jeder seiner Punkte leere Zellen ab (10 ms je Aufruf). */
    _naehe() {
        const { n, welt, nahe, bewegt, bewegtNah } = this, g = Stoffoberflaeche.GROB, b = Stoffoberflaeche.NAH;
        nahe.fill(0);
        bewegtNah.fill(0);
        for (let i = 0; i < n; i++) {
            const ix = Math.floor(welt[3 * i] / g), iy = Math.floor(welt[3 * i + 1] / g), iz = Math.floor(welt[3 * i + 2] / g);
            for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
                nahe[Stoffoberflaeche._hash(ix + dx, iy + dy, iz + dz)] = 1;
            }
            const w = bewegt[i];
            if (w <= 0) continue;
            const bx = Math.floor(welt[3 * i] / b), by = Math.floor(welt[3 * i + 1] / b), bz = Math.floor(welt[3 * i + 2] / b);
            for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
                const h = Stoffoberflaeche._hash(bx + dx, by + dy, bz + dz);
                if (bewegtNah[h] < w) bewegtNah[h] = w;
            }
        }
    }

    static _hash(ix, iy, iz) {
        return ((ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791)) & (Stoffoberflaeche.EIMER - 1);
    }

    /** Der nächste Hautpunkt zu (px, py, pz) in `REICHWEITE`, oder -1. */
    naechster(px, py, pz) {
        const g = Stoffoberflaeche.GROB, gx = Math.floor(px / g), gy = Math.floor(py / g), gz = Math.floor(pz / g);
        if (!this.nahe[Stoffoberflaeche._hash(gx, gy, gz)]) return -1;
        const nah = this._suche(this.fein, px, py, pz, Stoffoberflaeche.ZELLE ** 2);
        return nah >= 0 ? nah : this._suche(this.grob, px, py, pz, Stoffoberflaeche.REICHWEITE ** 2);
    }

    /** Der nächste Hautpunkt in den 27 Zellen des Rasters `r` um den Punkt, näher als √`bis2`, oder -1. */
    _suche(r, px, py, pz, bis2) {
        const { welt } = this, { w, start, eintrag } = r;
        const ix = Math.floor(px / w), iy = Math.floor(py / w), iz = Math.floor(pz / w);
        let beste = -1, bester = bis2;
        for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
            const z = Stoffoberflaeche._hash(ix + dx, iy + dy, iz + dz);
            for (let k = start[z]; k < start[z + 1]; k++) {
                const j = eintrag[k], o = 3 * j;
                const ex = welt[o] - px, ey = welt[o + 1] - py, ez = welt[o + 2] - pz;
                const d2 = ex * ex + ey * ey + ez * ez;
                if (d2 < bester) { bester = d2; beste = j; }
            }
        }
        return beste;
    }

    /** Freie Stoffpunkte, die hinter ihrem nächsten Hautpunkt liegen, auf `abstand` vor die Haut. */
    hinaus(x, frei, n, abstand) {
        const { welt, normale, bewegtNah } = this, m = this._merker(n), b = Stoffoberflaeche.NAH;
        const grenze = abstand + Stoffoberflaeche.RESERVE;
        // Ein Hautpunkt, der weiter lief als die Reichweite, kann von außerhalb der Marke gekommen sein.
        const sprung = this.bewegtMax > Stoffoberflaeche.REICHWEITE;
        for (let i = 0; i < n; i++) {
            if (frei[i] <= 0) continue;
            const o = 3 * i, px = x[o], py = x[o + 1], pz = x[o + 2];
            // Gedächtnis: der Weg des Punkts und der Haut um ihn seit dem letzten Bild, doppelt abgezogen.
            const dx = px - m.x[o], dy = py - m.x[o + 1], dz = pz - m.x[o + 2];
            const haut = sprung ? Infinity
                : bewegtNah[Stoffoberflaeche._hash(Math.floor(px / b), Math.floor(py / b), Math.floor(pz / b))];
            const schranke = m.schranke[i] - 2 * (Math.sqrt(dx * dx + dy * dy + dz * dz) + haut);
            m.x[o] = px; m.x[o + 1] = py; m.x[o + 2] = pz;
            if (schranke > grenze) { m.schranke[i] = schranke; continue; }
            const j = this.naechster(px, py, pz);
            if (j < 0) { m.schranke[i] = Stoffoberflaeche.REICHWEITE; continue; }
            const q = 3 * j, nx = normale[q], ny = normale[q + 1], nz = normale[q + 2];
            const s = (px - welt[q]) * nx + (py - welt[q + 1]) * ny + (pz - welt[q + 2]) * nz;
            if (s >= abstand) { m.schranke[i] = s; continue; }
            const h = abstand - s;
            x[o] += nx * h; x[o + 1] += ny * h; x[o + 2] += nz * h;
            m.x[o] = x[o]; m.x[o + 1] = x[o + 1]; m.x[o + 2] = x[o + 2];
            m.schranke[i] = abstand;
        }
        return x;
    }
}
