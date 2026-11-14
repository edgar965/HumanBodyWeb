/**
 * Stoffglaettung — anliegender Stoff wird je Bild dort geglättet, wo die Häutung ihn aufreißt (12.11.2026).
 *
 * WARUM (Edgar, 12.11.2026, Olesia1 im Spagat: „der helle streifen im Schritt ist die Hose, die gleich zerreisst...“, dann „mach“ zu
 * „Daz glättet den Stoff an solchen Stellen in jedem Bild nach“): Die Schrittnaht der Jeans hängt links am rechten, rechts am linken
 * Oberschenkel. Spreizen sich die Beine, trägt die Häutung die ganze Mehrlänge in die wenigen Kanten am Übergang der Gewichte — gemessen
 * 11- bis 13-fach, p99 der ganzen Hose nur 2,14. Weder die halbe Dual-Quaternion-Häutung noch geglättete Gewichte senkten p99.
 *
 * WAS DAZ TUT (Doku `DzMeshSmoothModifier`, gelesen für `Genesis9/drapierer.py`; der Quelltext ist nicht offen): Ein Smoothing Modifier am
 * Stück glättet nach Häutung und Morphen, VOR der Unterteilung, mit Weight 0,5 und einigen Durchgängen; Standardtyp „Base Shape Matching“
 * (die Form der Ruhelage bleibt, geglättet wird die Verformung); danach Kollisionsdurchgänge gegen die Figur.
 *
 * WIE ES HIER GERECHNET WIRD (nicht gegen Daz' Code geprüft, der ist zu):
 *   1. Der Käfig des Stücks (Daz' Punkte vor der Unterteilung) wird gehäutet wie der Shader (`haeuten`, mit der Mischung aus `Dqhaut`).
 *   2. Kanten, die länger als `GRENZE` × Ruhe sind, und `RINGE` Nachbarringe darum bilden die Zone; alles andere bleibt, wie die Häutung
 *      es legt (Daz' „Lock Distance“ in anderer Form: nur was aufreißt, bewegt sich).
 *   3. In der Zone `DURCHGAENGE` × Gauß-Seidel auf  x_i ← x_i + GEWICHT·(Mittel der Nachbarn + d_i − x_i). d_i ist die Ruhe-Laplace-Koordinate
 *      (Punkt minus Mittel seiner Nachbarn in Ruhe), gehäutet mit den Gewichten von i: Wo ein Stück nur gedreht wird, ist das die gehäutete
 *      Lage selbst (nichts ändert sich), wo die Häutung zerrt, verteilt die Glättung die Mehrlänge über die Zone („Base Shape Matching“).
 *      Nach jedem Schritt die Kollision: kein Punkt unter die Tangentialebene seiner gehäuteten Lage (Außennormale aus der Ruhe, durch
 *      die Häutung getragen). Ohne sie zog die Glättung die Jeans im Schritt bis 5 cm in den Körper, im Bild kam Haut durch.
 *   4. Der Versatz geglättet − gehäutet geht über die Unterteilungsmatrix auf die Browserpunkte und von dort als Attribut `glaettung` in den
 *      Shader, NACH der Häutung und VOR der Hautbindung, die den Stoff aus dem Körper schiebt — das ist hier die Kollision.
 *
 * Ohne Three.js: `test_js_stoffglaettung` prüft es in Node.
 */
export class Stoffglaettung {

    /** Ab dieser Kantendehnung (Verhältnis zur Ruhe) wird geglättet. Ein gebeugtes Knie streckt die Käfigkanten außen um gut ein Drittel. */
    static GRENZE = 1.5;
    /** So viele Nachbarringe um die aufreißenden Kanten gehören zur Zone. */
    static RINGE = 6;
    /**
     * Gauß-Seidel-Durchgänge je Bild, mit der Kollision in jedem. Örtlich wie Daz (wenige Durchgänge), nicht bis zum Gleichgewicht: Über eine
     * breite Zone exakt gelöst (konjugierte Gradienten) summierten sich die Widersprüche der einzeln gehäuteten Laplace-Koordinaten — Risse in
     * 14 bis 16 von 25 Bildern statt 2, Versatz bis 208 mm (Olesia1, Spagat, 12.11.2026). Gemessen an der Jeans (aufreißende Kanten in Bild 45/50):
     * 3 Ringe/20 Durchgänge 145/126, 6/40 93/83 (im Mittel 7 ms je Bild), 10/80 45/35 (16 ms).
     */
    static DURCHGAENGE = 40;
    /** Daz' „Weight“ (Doku `DzMeshSmoothModifier`, Vorgabe 0,5). */
    static GEWICHT = 0.5;
    /** Größter Versatz eines Käfigpunkts (Meter), unter der seitlichen Grenze der Hautbindung (3 cm). */
    static VERSATZ_M = 0.02;
    /** Schrittweite (Meter), mit der die Außennormale eines Punkts durch die Häutung getragen wird. */
    static NORMALE_M = 0.01;

    /**
     * @param ruhe    Float32Array (n·3) der Käfig in Ruhe (Raum der Geometrie)
     * @param kanten  Uint32Array (E·2) Käfigkanten
     * @param matrix  `{indptr, indices, data, zeilen}` Unterteilung Käfig → Browserpunkte (CSR)
     * @param normalen  Float32Array (zeilen·3) Außennormalen der Browserpunkte in Ruhe — daraus die des Käfigs (Kollision, `bild`)
     */
    constructor(ruhe, kanten, matrix, normalen = null) {
        this.n = ruhe.length / 3;
        this.ruhe = ruhe;
        this.zeilen = matrix.zeilen;
        const E = kanten.length >> 1;
        this.a = new Uint32Array(E); this.b = new Uint32Array(E); this.l = new Float32Array(E);
        const grad = new Uint32Array(this.n + 1);
        for (let e = 0; e < E; e++) {
            const i = kanten[2 * e], j = kanten[2 * e + 1];
            this.a[e] = i; this.b[e] = j;
            this.l[e] = Math.hypot(ruhe[3 * i] - ruhe[3 * j], ruhe[3 * i + 1] - ruhe[3 * j + 1], ruhe[3 * i + 2] - ruhe[3 * j + 2]);
            grad[i + 1]++; grad[j + 1]++;
        }
        for (let i = 0; i < this.n; i++) grad[i + 1] += grad[i];
        this.zeiger = grad;
        this.nachbarn = new Uint32Array(2 * E);
        const stand = grad.slice(0, this.n);
        for (let e = 0; e < E; e++) { this.nachbarn[stand[this.a[e]]++] = this.b[e]; this.nachbarn[stand[this.b[e]]++] = this.a[e]; }
        // Mittel der Nachbarn in Ruhe — d_i = S_i(ruhe_i) − S_i(mittel_i)
        this.mittel = new Float32Array(3 * this.n);
        for (let i = 0; i < this.n; i++) {
            const von = grad[i], bis = grad[i + 1];
            if (bis === von) { this.mittel.set(ruhe.subarray(3 * i, 3 * i + 3), 3 * i); continue; }
            let x = 0, y = 0, z = 0;
            for (let k = von; k < bis; k++) { const j = 3 * this.nachbarn[k]; x += ruhe[j]; y += ruhe[j + 1]; z += ruhe[j + 2]; }
            const f = 1 / (bis - von);
            this.mittel[3 * i] = x * f; this.mittel[3 * i + 1] = y * f; this.mittel[3 * i + 2] = z * f;
        }
        // Spalten der Unterteilungsmatrix: welche Browserpunkte ein Käfigpunkt bewegt (nur die der Zone werden angefasst).
        const { indptr, indices, data } = matrix;
        const spalte = new Uint32Array(this.n + 1);
        for (let e = 0; e < indices.length; e++) spalte[indices[e] + 1]++;
        for (let i = 0; i < this.n; i++) spalte[i + 1] += spalte[i];
        this.spaltenZeiger = spalte;
        this.spaltenZeile = new Uint32Array(indices.length);
        this.spaltenWert = new Float32Array(indices.length);
        const pos = spalte.slice(0, this.n);
        for (let r = 0; r < this.zeilen; r++) {
            for (let e = indptr[r]; e < indptr[r + 1]; e++) {
                const c = indices[e], p = pos[c]++;
                this.spaltenZeile[p] = r; this.spaltenWert[p] = data[e];
            }
        }
        // Außennormalen des Käfigs in Ruhe: die der Browserpunkte, mit der Unterteilungsmatrix eingesammelt.
        this.normale = null;
        if (normalen && normalen.length === 3 * this.zeilen) {
            this.normale = new Float32Array(3 * this.n);
            for (let i = 0; i < this.n; i++) {
                let x = 0, y = 0, z = 0;
                for (let k = spalte[i]; k < spalte[i + 1]; k++) {
                    const r = 3 * this.spaltenZeile[k], g = this.spaltenWert[k];
                    x += g * normalen[r]; y += g * normalen[r + 1]; z += g * normalen[r + 2];
                }
                const l = Math.hypot(x, y, z) || 1;
                this.normale[3 * i] = x / l; this.normale[3 * i + 1] = y / l; this.normale[3 * i + 2] = z / l;
            }
        }
        this.nz = new Float32Array(3 * this.n);         // gehäutete Außennormale je Punkt der Zone
        this.x = new Float32Array(3 * this.n);          // gehäutet, dann geglättet
        this.lage = new Float32Array(3 * this.n);       // gehäutet
        this.d = new Float32Array(3 * this.n);
        this.zone = new Uint8Array(this.n);
        this.versatz = new Float32Array(3 * this.zeilen);
        this._beruehrt = [];                            // Zeilen mit Versatz aus dem vorigen Bild
        this._tmp = [0, 0, 0];
    }

    /**
     * Ein Bild. `haeuten(i, x, y, z, aus)` legt den Punkt (x, y, z) mit den Gewichten des Käfigpunkts i in die Pose (Raum der Geometrie).
     * @returns {{versatz: Float32Array, zone: number, risse: number, groesste: number, geaendert: boolean}} `versatz` je Browserpunkt (zeilen·3)
     */
    bild(haeuten) {
        const { n, ruhe, mittel, x, lage, d, zone } = this, t = this._tmp;
        for (let i = 0; i < n; i++) {
            const o = 3 * i;
            haeuten(i, ruhe[o], ruhe[o + 1], ruhe[o + 2], t);
            lage[o] = t[0]; lage[o + 1] = t[1]; lage[o + 2] = t[2];
        }
        zone.fill(0);
        let risse = 0, groesste = 1;
        for (let e = 0; e < this.a.length; e++) {
            const i = 3 * this.a[e], j = 3 * this.b[e], l0 = this.l[e];
            if (l0 <= 1e-9) continue;
            const s = Math.hypot(lage[i] - lage[j], lage[i + 1] - lage[j + 1], lage[i + 2] - lage[j + 2]) / l0;
            if (s > groesste) groesste = s;
            if (s > Stoffglaettung.GRENZE) { zone[this.a[e]] = 1; zone[this.b[e]] = 1; risse++; }
        }
        const geaendert = this._beruehrt.length > 0;
        if (!risse) {
            this._leeren();
            return { versatz: this.versatz, zone: 0, risse: 0, groesste, geaendert };
        }
        const liste = this._ringe();
        // Die gehäutete Laplace-Koordinate nur in der Zone (die zweite Häutung je Punkt kostete am Hemd von Olesia1 die Hälfte der 7 ms).
        x.set(lage);
        const N = this.normale, nz = this.nz, eps = Stoffglaettung.NORMALE_M;
        for (const i of liste) {
            const o = 3 * i;
            haeuten(i, mittel[o], mittel[o + 1], mittel[o + 2], t);
            d[o] = lage[o] - t[0]; d[o + 1] = lage[o + 1] - t[1]; d[o + 2] = lage[o + 2] - t[2];
            if (!N) continue;
            haeuten(i, ruhe[o] + eps * N[o], ruhe[o + 1] + eps * N[o + 1], ruhe[o + 2] + eps * N[o + 2], t);
            const ax = t[0] - lage[o], ay = t[1] - lage[o + 1], az = t[2] - lage[o + 2], l = Math.hypot(ax, ay, az) || 1;
            nz[o] = ax / l; nz[o + 1] = ay / l; nz[o + 2] = az / l;
        }
        const w = Stoffglaettung.GEWICHT, { zeiger, nachbarn } = this;
        for (let durchgang = 0; durchgang < Stoffglaettung.DURCHGAENGE; durchgang++) {
            for (const i of liste) {
                const von = zeiger[i], bis = zeiger[i + 1];
                if (bis === von) continue;
                let mx = 0, my = 0, mz = 0;
                for (let k = von; k < bis; k++) { const j = 3 * nachbarn[k]; mx += x[j]; my += x[j + 1]; mz += x[j + 2]; }
                const f = 1 / (bis - von), o = 3 * i;
                x[o] += w * (mx * f + d[o] - x[o]);
                x[o + 1] += w * (my * f + d[o + 1] - x[o + 1]);
                x[o + 2] += w * (mz * f + d[o + 2] - x[o + 2]);
                if (!N) continue;
                // Kollision: nie unter die Tangentialebene der gehäuteten Lage — sonst zieht die Glättung den Stoff über die
                // Hohlkehle in den Körper (Olesia1, Spagat Bild 50: Schrittpunkte 5 cm verschoben, Haut durch die Jeans im Bild).
                const s = (x[o] - lage[o]) * nz[o] + (x[o + 1] - lage[o + 1]) * nz[o + 1] + (x[o + 2] - lage[o + 2]) * nz[o + 2];
                if (s < 0) { x[o] -= s * nz[o]; x[o + 1] -= s * nz[o + 1]; x[o + 2] -= s * nz[o + 2]; }
            }
        }
        // Höchstens `VERSATZ_M` weit: Die Hautbindung im Shader schiebt einen Punkt nur aus dem Körper, wenn er höchstens 3 cm seitlich
        // von seinem Körperdreieck liegt (`OberflaecheGLSL`, `uSeitGrenze`) — weiter geglättet blieb er drin (Olesia1, Spagat Bild 50: Hautfleck im Schritt).
        const grenze = Stoffglaettung.VERSATZ_M;
        for (const i of liste) {
            const o = 3 * i, vx = x[o] - lage[o], vy = x[o + 1] - lage[o + 1], vz = x[o + 2] - lage[o + 2], l = Math.hypot(vx, vy, vz);
            if (l > grenze) { const f = grenze / l; x[o] = lage[o] + f * vx; x[o + 1] = lage[o + 1] + f * vy; x[o + 2] = lage[o + 2] + f * vz; }
        }
        this._leeren();
        const { spaltenZeiger, spaltenZeile, spaltenWert, versatz } = this, beruehrt = this._beruehrt;
        const markiert = this._markiert || (this._markiert = new Uint8Array(this.zeilen));
        for (const i of liste) {
            const o = 3 * i, vx = x[o] - lage[o], vy = x[o + 1] - lage[o + 1], vz = x[o + 2] - lage[o + 2];
            if (vx === 0 && vy === 0 && vz === 0) continue;
            for (let k = spaltenZeiger[i]; k < spaltenZeiger[i + 1]; k++) {
                const r = spaltenZeile[k], g = spaltenWert[k];
                versatz[3 * r] += g * vx; versatz[3 * r + 1] += g * vy; versatz[3 * r + 2] += g * vz;
                if (!markiert[r]) { markiert[r] = 1; beruehrt.push(r); }
            }
        }
        return { versatz, zone: liste.length, risse, groesste, geaendert: true };
    }

    /** Die Zone um die aufreißenden Kanten um `RINGE` Ringe erweitern; die Punkte der Zone als Liste. */
    _ringe() {
        const { n, zone, zeiger, nachbarn } = this;
        let rand = [];
        for (let i = 0; i < n; i++) if (zone[i]) rand.push(i);
        const liste = rand.slice();
        for (let ring = 0; ring < Stoffglaettung.RINGE; ring++) {
            const neu = [];
            for (const i of rand) {
                for (let k = zeiger[i]; k < zeiger[i + 1]; k++) {
                    const j = nachbarn[k];
                    if (!zone[j]) { zone[j] = 1; neu.push(j); }
                }
            }
            for (const j of neu) liste.push(j);
            rand = neu;
        }
        return liste;
    }

    /** Den Versatz des vorigen Bildes zurücksetzen (nur die Zeilen, die er hatte). */
    _leeren() {
        const { versatz } = this, markiert = this._markiert;
        for (const r of this._beruehrt) {
            versatz[3 * r] = 0; versatz[3 * r + 1] = 0; versatz[3 * r + 2] = 0;
            if (markiert) markiert[r] = 0;
        }
        this._beruehrt.length = 0;
    }
}
