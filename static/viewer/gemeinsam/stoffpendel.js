/**
 * Stoffpendel — die Rechnung des Stoffschwungs ohne Three.js, prüfbar in Node.
 *
 * WAS ES IST (18.09.2026, Edgar: „dForce-Stoff … kannst du das einbauen"):
 * kein dForce (Daz simuliert vorab, Sekunden je Bild), sondern eine Näherung,
 * die live läuft: Verlet-Teilchen auf den Browserpunkten eines Stücks,
 * die Kanten des Netzes als Längenbedingungen (Position-Based Dynamics,
 * Müller et al. 2007), eine Feder zur GEHÄUTETEN Lage (die Form, die das
 * Stück ohne Schwung hätte — sie ersetzt Biegesteifigkeit und Gedächtnis),
 * Schwerkraft, und Kapseln um die Knochen als Körper. Je Punkt eine
 * FREIHEIT 0..1 vom Server (`Genesis9/stoff.py`: Daz' Dynamics Strength mal
 * Abstand zur Haut in Ruhe): 0 = folgt der Haut, 1 = hängt frei.
 *
 *     v      = (x − xAlt)·(1 − DAEMPFUNG)
 *     x'     = x + v + (ziel − x)·min(1, dt·(FEDER_FREI + (1 − f)·FEDER_HAFT))
 *                + g·SCHWERKRAFT·dt²·f
 *     Kanten: je Durchgang jede Kante auf ihre Ruhelänge, Verschiebung nach
 *             Freiheit verteilt (f = 0 bewegt sich nicht)
 *     Kapseln: näher als r + ABSTAND an der Achse → auf r + ABSTAND hinaus
 *
 * Die Zahlen sind Anzeigewerte, keine Daz-Werte: Dämpfung 2 %, Feder frei
 * 2/s, Feder Haftung 30/s, Schwerkraft mit Faktor 0,3 (voll ließ jeden Saum
 * 16 cm unter die gehäutete Lage sacken), 4 Durchgänge, 6 mm über der
 * Kapsel, Zeitschritt höchstens 1/30 s. Gemessen wird in der Szene
 * (`__stoffschwung.probe`), nicht hier.
 */
export class Stoffpendel {

    static DAEMPFUNG = 0.02;
    static FEDER_FREI = 2.0;
    static FEDER_HAFT = 30.0;
    static SCHWERKRAFT = 9.81;
    static SCHWERE = 0.3;
    static DURCHGAENGE = 4;
    static ABSTAND = 0.006;
    static MAX_DT = 1 / 30;
    /** Ab dieser Bildzeit (Sekunden) gilt das Bild als Sprung: die Figur ist
     *  weitergesprungen, der Stoff wird auf die gehäutete Lage gesetzt statt
     *  gezogen — sonst zerreißen die Kanten (Edgar, 18.09.2026: das Kleid
     *  hing in Fetzen, das Haar schwebte neben der Figur; Ladezeiten von
     *  Sekunden je Bild bei hoher Auflösung). */
    static SPRUNG_DT = 0.25;
    /** Ab dieser Auslenkung (Meter) ist die Simulation entgleist: zurück auf die Lage. */
    static ENTGLEIST_M = 0.5;
    static G = [0, -1, 0];

    /**
     * @param ruhe    Float32Array (n·3) Punkte der Ruhelage
     * @param frei    Float32Array (n) Freiheit 0..1
     * @param kanten  `{a, b, l}` (`ausDreiecken`/`ausKanten` bauen sie)
     */
    constructor(ruhe, frei, kanten) {
        this.n = frei.length;
        this.frei = Float32Array.from(frei);
        this.x = Float32Array.from(ruhe);
        this.xAlt = Float32Array.from(ruhe);
        this.kanten = kanten;
    }

    /** Aus Dreiecken (Indizes je drei): jede Kante einmal, mit Ruhelänge. */
    static ausDreiecken(ruhe, dreiecke, frei) {
        const n = frei.length, gesehen = new Set(), paare = [];
        for (let t = 0; t + 2 < dreiecke.length; t += 3) {
            for (let k = 0; k < 3; k++) {
                let i = dreiecke[t + k], j = dreiecke[t + (k + 1) % 3];
                if (i === j || i >= n || j >= n) continue;
                if (i > j) { const s = i; i = j; j = s; }
                const key = i * n + j;
                if (gesehen.has(key)) continue;
                gesehen.add(key);
                paare.push(i, j);
            }
        }
        return Stoffpendel.ausKanten(ruhe, paare, frei);
    }

    /** Aus Kantenpaaren `[i, j, i, j, …]` (Daz' Käfigkanten vom Server). */
    static ausKanten(ruhe, paare, frei) {
        const anzahl = paare.length >> 1;
        const a = new Uint32Array(anzahl), b = new Uint32Array(anzahl), l = new Float32Array(anzahl);
        for (let e = 0; e < anzahl; e++) {
            const i = paare[2 * e], j = paare[2 * e + 1];
            a[e] = i; b[e] = j;
            l[e] = Math.hypot(ruhe[3 * j] - ruhe[3 * i], ruhe[3 * j + 1] - ruhe[3 * i + 1],
                              ruhe[3 * j + 2] - ruhe[3 * i + 2]);
        }
        return new Stoffpendel(ruhe, frei, { a, b, l });
    }

    /** Zustand auf die gehäutete Lage setzen (Start, Stopp, Sprung). */
    setzen(ziel) {
        this.x.set(ziel); this.xAlt.set(ziel);
    }

    /**
     * Ein Bild — mit Sprungschutz: ein Bild über `SPRUNG_DT` oder eine
     * Auslenkung über `ENTGLEIST_M` setzt auf die gehäutete Lage; sonst
     * höchstens zwei Teilschritte (der Schritt selbst deckelt bei `MAX_DT`).
     * @returns {{x: Float32Array, zurueckgesetzt: boolean}}
     */
    bild(ziel, dt, kapseln = [], werte = Stoffpendel) {
        if (!(dt >= 0) || dt > werte.SPRUNG_DT) { this.setzen(ziel); return { x: this.x, zurueckgesetzt: true }; }
        const teile = dt > werte.MAX_DT ? 2 : 1;
        let x = this.x;
        for (let t = 0; t < teile; t++) x = this.schritt(ziel, dt / teile, kapseln, werte);
        if (this.auslenkung(ziel) > werte.ENTGLEIST_M) { this.setzen(ziel); return { x: this.x, zurueckgesetzt: true }; }
        return { x, zurueckgesetzt: false };
    }

    /**
     * Ein Bild rechnen.
     * @param ziel     Float32Array (n·3) die gehäutete Lage dieses Bildes
     * @param dt       Sekunden
     * @param kapseln  [{a: [x,y,z], b: [x,y,z], r}] Körper (Achse a→b, Radius r)
     * @returns {Float32Array} die Punkte (this.x)
     */
    schritt(ziel, dt, kapseln = [], werte = Stoffpendel) {
        dt = Math.min(Math.max(dt, 0), werte.MAX_DT);
        const { x, xAlt, frei, n } = this;
        const g = werte.SCHWERKRAFT * werte.SCHWERE * dt * dt;
        const dv = 1 - werte.DAEMPFUNG;
        for (let i = 0; i < n; i++) {
            const f = frei[i], o = 3 * i;
            if (f <= 0) {
                x[o] = xAlt[o] = ziel[o]; x[o + 1] = xAlt[o + 1] = ziel[o + 1]; x[o + 2] = xAlt[o + 2] = ziel[o + 2];
                continue;
            }
            const zug = Math.min(1, dt * (werte.FEDER_FREI + (1 - f) * werte.FEDER_HAFT));
            for (let k = 0; k < 3; k++) {
                const alt = x[o + k];
                x[o + k] = alt + (alt - xAlt[o + k]) * dv + (ziel[o + k] - alt) * zug + werte.G[k] * g * f;
                xAlt[o + k] = alt;
            }
        }
        const { a, b, l } = this.kanten;
        for (let d = 0; d < werte.DURCHGAENGE; d++) {
            for (let e = 0; e < a.length; e++) {
                const i = 3 * a[e], j = 3 * b[e];
                const wi = frei[a[e]], wj = frei[b[e]], summe = wi + wj;
                if (summe <= 0) continue;
                const dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2];
                const len = Math.hypot(dx, dy, dz);
                if (len < 1e-9) continue;
                const diff = (len - l[e]) / len;
                const ki = diff * wi / summe, kj = diff * wj / summe;
                x[i] += dx * ki; x[i + 1] += dy * ki; x[i + 2] += dz * ki;
                x[j] -= dx * kj; x[j + 1] -= dy * kj; x[j + 2] -= dz * kj;
            }
        }
        if (kapseln.length) this._kapseln(kapseln, werte.ABSTAND);
        return x;
    }

    _kapseln(kapseln, abstand) {
        const { x, frei, n } = this;
        for (const k of kapseln) {
            const ax = k.a[0], ay = k.a[1], az = k.a[2];
            const bx = k.b[0] - ax, by = k.b[1] - ay, bz = k.b[2] - az;
            const bb = bx * bx + by * by + bz * bz || 1e-12;
            const r = k.r + abstand;
            // Grobe Hülle: Achse ± Radius.
            const minX = Math.min(ax, k.b[0]) - r, maxX = Math.max(ax, k.b[0]) + r;
            const minY = Math.min(ay, k.b[1]) - r, maxY = Math.max(ay, k.b[1]) + r;
            const minZ = Math.min(az, k.b[2]) - r, maxZ = Math.max(az, k.b[2]) + r;
            for (let i = 0; i < n; i++) {
                if (frei[i] <= 0) continue;
                const o = 3 * i, px = x[o], py = x[o + 1], pz = x[o + 2];
                if (px < minX || px > maxX || py < minY || py > maxY || pz < minZ || pz > maxZ) continue;
                let t = ((px - ax) * bx + (py - ay) * by + (pz - az) * bz) / bb;
                t = t < 0 ? 0 : (t > 1 ? 1 : t);
                const qx = ax + bx * t, qy = ay + by * t, qz = az + bz * t;
                const dx = px - qx, dy = py - qy, dz = pz - qz;
                const d = Math.hypot(dx, dy, dz);
                if (d >= r || d < 1e-9) continue;
                const s = r / d;
                x[o] = qx + dx * s; x[o + 1] = qy + dy * s; x[o + 2] = qz + dz * s;
            }
        }
    }

    /** Größter Abstand eines freien Punkts von seiner gehäuteten Lage (m). */
    auslenkung(ziel) {
        let max = 0;
        for (let i = 0; i < this.n; i++) {
            if (this.frei[i] <= 0) continue;
            const o = 3 * i;
            const d = Math.hypot(this.x[o] - ziel[o], this.x[o + 1] - ziel[o + 1], this.x[o + 2] - ziel[o + 2]);
            if (d > max) max = d;
        }
        return max;
    }
}
