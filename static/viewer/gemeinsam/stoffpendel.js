/**
 * Stoffpendel — die Rechnung des Stoffschwungs ohne Three.js, prüfbar in Node.
 *
 * WAS ES IST (18.09.2026, Edgar: „dForce-Stoff … kannst du das einbauen"):
 * kein dForce (Daz simuliert vorab, Sekunden je Bild), sondern eine Näherung,
 * die live läuft: Verlet-Teilchen auf den Browserpunkten eines Stücks,
 * die Kanten des Netzes als Längenbedingungen (Position-Based Dynamics,
 * Müller et al. 2007), ein Reichweiten-Anker je Punkt (`stoffanker.js`),
 * eine schwache Feder zur GEHÄUTETEN Lage (die Form, die das Stück ohne
 * Schwung hätte — Formgedächtnis, kein Halteseil), Schwerkraft, und Kapseln
 * um die Knochen als Körper. Je Punkt eine FREIHEIT 0..1 vom Server
 * (`Genesis9/stoff.py`: Daz' Dynamics Strength mal Abstand zur Haut in
 * Ruhe): 0 = folgt der Haut, 1 = hängt frei.
 *
 *     v      = (x − xAlt)·(1 − DAEMPFUNG·dt)
 *     x'     = x + v + (ziel − x)·(min(1, dt·(1 − f)·FEDER_HAFT) + FEDER·dt²·f)
 *                + g·dt²·f
 *     Kanten: je Durchgang jede Kante auf ihre Ruhelänge, Verschiebung nach
 *             Freiheit verteilt (f = 0 bewegt sich nicht)
 *     Anker:  kein Punkt weiter von seinem gebundenen Anker als der Stoffweg
 *     Kapseln: elliptische Kegelkapseln um die Knochen (`stoffkoerper.js`,
 *             19.09.2026 — EIN Radius je Knochen blähte die Jeans am Knie auf,
 *             ein runder lag an der breiten Seite des Schenkels in der Haut)
 *
 * WARUM DIE FORMEL SO IST (20.09.2026, Edgar: „das kleid muss nach unten
 * animieren!!!", „bei der Jump animation verliert die Person das Kleid!!"):
 * Bis dahin galt `(ziel − x)·dt·2` gegen `g·0,3·dt²` — die Feder war eine
 * Verschiebung je Bild, die Schwerkraft eine Beschleunigung; ihr Gleichgewicht
 * lag bei 9,81·0,3/(30·2) = 4,9 cm (gemessen 5,0), an 60 Hz die Hälfte davon.
 * Ein 40 cm waagerecht modellierter Rock blieb also 40 cm abstehen, und die
 * hängenden Arme liefen hindurch. Jetzt sind beide Beschleunigungen: die Feder
 * hält gegen die Schwerkraft nur noch tan θ = FEDER·s/g — bei 40 cm Stoffweg
 * 14 Grad aus der Senkrechten, unabhängig von der Bildrate. Beim Sprung rissen
 * die Kanten (1,89-fache Länge: vier Durchgänge ziehen vier Reihen, der Rest
 * blieb stehen); der Anker zieht den straff hängenden Rock im selben Bild mit.
 *
 * Die Zahlen sind Anzeigewerte, keine Daz-Werte: Dämpfung 1,5/s, Feder 6/s²,
 * Feder Haftung 30/s, volle Schwerkraft, 4 Durchgänge, 6 mm über der Kapsel,
 * Zeitschritt höchstens 1/30 s. Gemessen wird in der Szene
 * (`__stoffschwung.probe`); die Kunststreifen prüft `test_js_stoffpendel*`.
 */
import { Stoffanker } from './stoffanker.js';
import { Stoffkoerper } from './stoffkoerper.js';

export class Stoffpendel {

    /** Dämpfung der Geschwindigkeit je Sekunde (Luft, Reibung). */
    static DAEMPFUNG = 1.5;
    /** Feder zur gehäuteten Lage, als Beschleunigung [1/s²] — Formgedächtnis, sonst nichts. */
    static FEDER = 6.0;
    /** Kinematisches Folgen an der Haut für Punkte mit kleiner Freiheit [1/s]. */
    static FEDER_HAFT = 30.0;
    static SCHWERKRAFT = 9.81;
    /** Anteil der Schwerkraft — 1: der Stoff fällt wie Stoff. */
    static SCHWERE = 1.0;
    static DURCHGAENGE = 4;
    /** Anteil je Bild, um den eine gestauchte Biegebedingung ausgeglichen wird (0 = Stoff ohne Steifigkeit). */
    static BIEGUNG = 0.1;
    static ABSTAND = 0.006;
    static MAX_DT = 1 / 30;
    /** Ab dieser Bildzeit (Sekunden) gilt das Bild als Sprung: die Figur ist
     *  weitergesprungen, der Stoff wird auf die gehäutete Lage gesetzt statt
     *  gezogen — sonst zerreißen die Kanten (Edgar, 18.09.2026: das Kleid
     *  hing in Fetzen, das Haar schwebte neben der Figur; Ladezeiten von
     *  Sekunden je Bild bei hoher Auflösung). */
    static SPRUNG_DT = 0.25;
    /** Ab dieser Auslenkung (Meter) ist die Simulation entgleist: zurück auf die Lage.
     *  Ein langer Rock schwingt legitim über 0,5 m von seiner Lage weg; der Anker
     *  verhindert das Entgleisen ohnehin, die Grenze fängt nur noch Sprünge. */
    static ENTGLEIST_M = 1.0;
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
        this.anker = Stoffanker.rechnen(this.n, kanten, this.frei);
        this.biegung = Stoffanker.biegung(this.n, kanten, this.x);
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
        // Die Lage selbst ist weggesprungen (Szenenwechsel, Teleport): setzen statt
        // ziehen. Nach dem Schritt sieht man das nicht mehr - der Anker holt jeden
        // Punkt im selben Bild in seine Reichweite, als waagerechte Peitsche.
        if (this.auslenkung(ziel) > werte.ENTGLEIST_M) { this.setzen(ziel); return { x: this.x, zurueckgesetzt: true }; }
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
     * @param kapseln  [{a, b, u, rua, rwa, rub, rwb}] Körper (`Stoffkoerper`;
     *                 `{a, b, r}` gilt als runde Kapsel)
     * @returns {Float32Array} die Punkte (this.x)
     */
    schritt(ziel, dt, kapseln = [], werte = Stoffpendel) {
        dt = Math.min(Math.max(dt, 0), werte.MAX_DT);
        const { x, xAlt, frei, n } = this;
        const g = werte.SCHWERKRAFT * werte.SCHWERE * dt * dt;
        const dv = Math.max(0, 1 - werte.DAEMPFUNG * dt);
        for (let i = 0; i < n; i++) {
            const f = frei[i], o = 3 * i;
            if (f <= 0) {
                x[o] = xAlt[o] = ziel[o]; x[o + 1] = xAlt[o + 1] = ziel[o + 1]; x[o + 2] = xAlt[o + 2] = ziel[o + 2];
                continue;
            }
            const zug = Math.min(1, dt * (1 - f) * werte.FEDER_HAFT) + werte.FEDER * dt * dt * f;
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
        this._biegen(werte.BIEGUNG);
        if (this.anker) Stoffanker.halten(x, frei, n, this.anker.anker, this.anker.reichweite);
        if (kapseln.length) this._kapseln(kapseln, werte.ABSTAND);
        return x;
    }

    /** Gestauchte Biegebedingungen (`Stoffanker.biegung`) um `anteil` ausgleichen. */
    _biegen(anteil) {
        if (!(anteil > 0) || !this.biegung) return;
        const { x, frei } = this, { a, b, l } = this.biegung;
        for (let e = 0; e < a.length; e++) {
            const i = 3 * a[e], j = 3 * b[e];
            const wi = frei[a[e]], wj = frei[b[e]], summe = wi + wj;
            if (summe <= 0) continue;
            const dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2];
            const len = Math.hypot(dx, dy, dz);
            if (len < 1e-9 || len >= l[e]) continue;
            const diff = anteil * (len - l[e]) / len;
            const ki = diff * wi / summe, kj = diff * wj / summe;
            x[i] += dx * ki; x[i + 1] += dy * ki; x[i + 2] += dz * ki;
            x[j] -= dx * kj; x[j + 1] -= dy * kj; x[j + 2] -= dz * kj;
        }
    }

    /** Freie Punkte aus den Körperkapseln hinaus — `Stoffkoerper` (elliptische Kegelkapseln). */
    _kapseln(kapseln, abstand) {
        Stoffkoerper.hinaus(this.x, this.frei, this.n, kapseln, abstand);
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
