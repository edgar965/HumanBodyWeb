/**
 * Stoffpendel — die Rechnung des Stoffschwungs ohne Three.js, prüfbar in Node.
 *
 * WAS ES IST (18.09.2026, Edgar: „dForce-Stoff … kannst du das einbauen"):
 * kein dForce (Daz simuliert vorab, Sekunden je Bild), sondern eine Näherung,
 * die live läuft: Verlet-Teilchen auf den Käfigpunkten eines Stücks,
 * die Kanten des Netzes als Längenbedingungen (Position-Based Dynamics,
 * Müller et al. 2007, `stoffkanten.js`), ein Reichweiten-Anker je Punkt
 * (`stoffanker.js`), eine schwache Feder zur GEHÄUTETEN Lage (die Form, die
 * das Stück ohne Schwung hätte — Formgedächtnis, kein Halteseil),
 * Schwerkraft, Kapseln um die Knochen (`stoffkoerper.js`) und die Haut der
 * Figur (`stoffoberflaeche.js`) als Körper. Je Punkt eine FREIHEIT 0..1 vom
 * Server (`Genesis9/stoff.py`: Daz' Dynamics Strength mal Abstand zur Haut
 * in Ruhe): 0 = folgt der Haut, 1 = hängt frei.
 *
 *     v      = (x − xAlt) − DAEMPFUNG·dt·((x − xAlt) − MITNAHME·vAnker)
 *     x°     = x + v + g·dt²·f + MITNAHME·(zielAnker − 2·zielAnkerAlt + zielAnkerAlt2)
 *     x'     = x° + (ziel − x°)·min(1, dt·(1 − f)·FEDER_HAFT + FEDER·dt²·f)
 *     je Durchgang: Anker, dann jede Kante auf ihre Ruhelänge
 *     dann Biegung; Körper (Kapseln mit denen des vorigen Schritts, Haut),
 *     noch einmal Kanten, noch einmal Körper
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
 * MITNAHME (20.09.2026, Browser, Jump: Kantendehnung p99 4,75 trotz Anker):
 * Vier Gauss-Seidel-Durchgänge tragen eine Bewegung vier Kantenreihen weit.
 * Solange der Körper BESCHLEUNIGT, bleibt alles dahinter zurück, bis der Anker
 * greift — und der greift erst, wenn der Punkt am Ende seines Stoffwegs ist;
 * ein gefalteter oder ausgestellter Rock hat Spiel. Deshalb bekommt jeder
 * freie Punkt die Beschleunigung seines Ankers mit (zweite Differenz der
 * gehäuteten Lage des Ankers): Der Stoff wird im Bezugssystem des Körpers
 * gerechnet, wie Kleidung an einem Menschen — Trägheit hat er gegenüber
 * seiner EIGENEN Bewegung (Schwingen, Fallen), nicht gegenüber dem, der ihn
 * trägt. Bei gleichförmiger Bewegung ist der Term null (Verlet trägt die
 * Geschwindigkeit ohnehin). MITNAHME 1 = ganz mitgenommen, 0 = die alte Welt.
 *
 * Die Zahlen sind Anzeigewerte, keine Daz-Werte: Dämpfung 1,5/s, Feder 6/s²,
 * Feder Haftung 60/s, volle Schwerkraft, 4 Durchgänge, 6 mm über der Kapsel,
 * Teilschritt höchstens 1/60 s (ein Bein legt beim Sprung 5 cm in 1/60 s
 * zurück — eine Kapsel darf je Teilschritt nicht durch den Stoff hindurch).
 * Gemessen wird in der Szene (`__stoffschwung.probe`, `__kleidungsprobe`);
 * die Kunststreifen prüft `test_js_stoffpendel*`.
 */
import { Stoffanker } from './stoffanker.js';
import { Stoffkanten } from './stoffkanten.js';
import { Stoffkoerper } from './stoffkoerper.js';

export class Stoffpendel {

    /** Dämpfung der Geschwindigkeit je Sekunde (Luft, Reibung). */
    static DAEMPFUNG = 1.5;
    /** Feder zur gehäuteten Lage, als Beschleunigung [1/s²] — Formgedächtnis, sonst nichts. */
    static FEDER = 6.0;
    /** Kinematisches Folgen an der Haut für Punkte mit kleiner Freiheit [1/s].
     *  120 = 2/MAX_DT: ein Punkt mit Freiheit ≤ 0,5 folgt in EINEM Teilschritt
     *  (1/60 s) VOLLSTÄNDIG (dt·(1 − f)·120 ≥ 1). Mit 30 folgte das Oberteil des
     *  Kleids (f 0,1–0,3) nur zu 80 % je Schritt, und beim Sprung riss der Rock
     *  es 4 cm vom Körper (Browser, Jump: Haut −32 mm, Dehnung p99 8,8); mit 60
     *  und Teilschritten von 1/60 s folgten die Punkte um f = 0,5 nur zu 50 %
     *  je Teilschritt, und im freien Fall (2,9 m/s) rissen die Kanten am Bund
     *  (Browser, Jump: p99 3,75, 3.219 Kanten über dem Dreifachen, alle auf
     *  Hüft- bis Brusthöhe). */
    static FEDER_HAFT = 120.0;
    static SCHWERKRAFT = 9.81;
    /** Anteil der Schwerkraft — 1: der Stoff fällt wie Stoff. */
    static SCHWERE = 1.0;
    /** Anteil der Ankerbeschleunigung, den ein freier Punkt mitbekommt (Kopf der Datei). */
    static MITNAHME = 1.0;
    static DURCHGAENGE = 4;
    /** Anteil je Schritt, um den eine gestauchte Biegebedingung ausgeglichen wird (0 = Stoff ohne Steifigkeit). */
    static BIEGUNG = 0.1;
    static ABSTAND = 0.006;
    /** Längster Teilschritt (s) — darüber wird ein Bild zerlegt. */
    static MAX_DT = 1 / 60;
    /** Höchstens so viele Teilschritte je Bild — darüber läuft der Stoff in Zeitlupe,
     *  statt den Worker weiter hinter die Szene fallen zu lassen. */
    static TEILE = 4;
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
        /** Die Haut der Figur (`Stoffoberflaeche`, gehäutet) — setzt der Worker je Bild; null: ohne. */
        this.oberflaeche = null;
        this._zielAlt = null; this._zielAlt2 = null;
        this._kapselnAlt = null;
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
            const dx = ruhe[3 * j] - ruhe[3 * i], dy = ruhe[3 * j + 1] - ruhe[3 * i + 1], dz = ruhe[3 * j + 2] - ruhe[3 * i + 2];
            l[e] = Math.sqrt(dx * dx + dy * dy + dz * dz);
        }
        return new Stoffpendel(ruhe, frei, { a, b, l });
    }

    /** Zustand auf die gehäutete Lage setzen (Start, Stopp, Sprung). */
    setzen(ziel) {
        this.x.set(ziel); this.xAlt.set(ziel);
        this._zielAlt = Float32Array.from(ziel); this._zielAlt2 = Float32Array.from(ziel);
        this._kapselnAlt = null;
    }

    /**
     * Ein Bild — mit Sprungschutz: ein Bild über `SPRUNG_DT` oder eine
     * Auslenkung über `ENTGLEIST_M` setzt auf die gehäutete Lage; sonst
     * Teilschritte zu höchstens `MAX_DT`, bis zu `TEILE` (der Schritt selbst
     * deckelt bei `MAX_DT`), Lage und Kapseln dazwischen linear interpoliert.
     * @returns {{x: Float32Array, zurueckgesetzt: boolean}}
     */
    bild(ziel, dt, kapseln = [], werte = Stoffpendel) {
        if (!(dt >= 0) || dt > werte.SPRUNG_DT) { this.setzen(ziel); return { x: this.x, zurueckgesetzt: true }; }
        // Die Lage selbst ist weggesprungen (Szenenwechsel, Teleport): setzen statt
        // ziehen. Nach dem Schritt sieht man das nicht mehr - der Anker holt jeden
        // Punkt im selben Bild in seine Reichweite, als waagerechte Peitsche.
        if (this.auslenkung(ziel) > werte.ENTGLEIST_M) { this.setzen(ziel); return { x: this.x, zurueckgesetzt: true }; }
        const teile = Math.min(werte.TEILE, Math.max(1, Math.ceil(dt / werte.MAX_DT - 1e-6)));
        // Eigene Kopie: `schritt` tauscht seine Lagepuffer, `_zielAlt` wäre ab dem dritten Teilschritt überschrieben.
        const von = this._zielAlt ? this._kopie(this._zielAlt) : ziel;
        let koerperAlt = this._kapselnAlt && this._kapselnAlt.length === kapseln.length ? this._kapselnAlt : null;
        let x = this.x;
        for (let t = 1; t <= teile; t++) {
            const letzter = t === teile;
            const zwischen = letzter ? ziel : Stoffpendel._zwischen(von, ziel, t / teile, this._puffer(ziel.length));
            // Auch der Körper wandert je Teilschritt - ein Bein, das in einem Aufruf 20 cm
            // hochkommt, schöbe den Stoff sonst durch sich hindurch statt vor sich her.
            const koerper = letzter || !koerperAlt ? kapseln : Stoffpendel._kapselnZwischen(koerperAlt, kapseln, t / teile);
            x = this.schritt(zwischen, dt / teile, koerper, werte, koerperAlt, letzter);
            koerperAlt = koerper;
        }
        this._kapselnAlt = kapseln.map(k => ({ ...k, a: [...k.a], b: [...k.b] }));
        if (this.auslenkung(ziel) > werte.ENTGLEIST_M) { this.setzen(ziel); return { x: this.x, zurueckgesetzt: true }; }
        return { x, zurueckgesetzt: false };
    }

    /** Ein wiederverwendeter Puffer für die Zwischenlage. */
    _puffer(laenge) {
        if (!this._zwischenpuffer || this._zwischenpuffer.length !== laenge) this._zwischenpuffer = new Float32Array(laenge);
        return this._zwischenpuffer;
    }

    /** Die Lage des vorigen Bildes, in einem eigenen Puffer. */
    _kopie(lage) {
        if (!this._vonpuffer || this._vonpuffer.length !== lage.length) this._vonpuffer = new Float32Array(lage.length);
        this._vonpuffer.set(lage);
        return this._vonpuffer;
    }

    /** Kapseln mit Achsenenden zwischen zwei Lagen (Radien und Querachse vom Ziel). */
    static _kapselnZwischen(von, nach, anteil) {
        return nach.map((k, i) => ({
            ...k,
            a: [0, 1, 2].map(j => von[i].a[j] + (k.a[j] - von[i].a[j]) * anteil),
            b: [0, 1, 2].map(j => von[i].b[j] + (k.b[j] - von[i].b[j]) * anteil),
        }));
    }

    /** `von + (nach − von)·anteil`, in `aus`. */
    static _zwischen(von, nach, anteil, aus) {
        for (let i = 0; i < nach.length; i++) aus[i] = von[i] + (nach[i] - von[i]) * anteil;
        return aus;
    }

    /**
     * Ein Schritt rechnen.
     * @param ziel        Float32Array (n·3) die gehäutete Lage dieses Schritts
     * @param dt          Sekunden
     * @param kapseln     [{a, b, u, rua, rwa, rub, rwb}] Körper (`Stoffkoerper`;
     *                    `{a, b, r}` gilt als runde Kapsel)
     * @param kapselnAlt  dieselben Kapseln im vorigen Schritt (Seite von vorhin), oder null
     * @param haut        auch die Haut (`oberflaeche`) am Ende - `bild` nur im letzten Teilschritt:
     *                    19k Punkte gegen das Hautraster kosten 10 ms, die Kapseln 1,6 (Node)
     * @returns {Float32Array} die Punkte (this.x)
     */
    schritt(ziel, dt, kapseln = [], werte = Stoffpendel, kapselnAlt = null, haut = true) {
        dt = Math.min(Math.max(dt, 0), werte.MAX_DT);
        const { x, xAlt, frei, n } = this;
        if (!this._zielAlt || this._zielAlt.length !== ziel.length) {
            this._zielAlt = Float32Array.from(ziel); this._zielAlt2 = Float32Array.from(ziel);
        }
        const zAlt = this._zielAlt, zAlt2 = this._zielAlt2, anker = this.anker ? this.anker.anker : null;
        const g = werte.SCHWERKRAFT * werte.SCHWERE * dt * dt;
        const dv = Math.max(0, 1 - werte.DAEMPFUNG * dt), mit = werte.MITNAHME;
        for (let i = 0; i < n; i++) {
            const f = frei[i], o = 3 * i;
            if (f <= 0) {
                x[o] = xAlt[o] = ziel[o]; x[o + 1] = xAlt[o + 1] = ziel[o + 1]; x[o + 2] = xAlt[o + 2] = ziel[o + 2];
                continue;
            }
            const zug = Math.min(1, dt * (1 - f) * werte.FEDER_HAFT + werte.FEDER * dt * dt * f);
            const p = anker && anker[i] >= 0 ? 3 * anker[i] : -1;
            for (let k = 0; k < 3; k++) {
                const alt = x[o + k], v = alt - xAlt[o + k];
                // Gedämpft wird die Geschwindigkeit GEGENÜBER dem Anker (mit MITNAHME gewichtet),
                // nicht die in der Welt: sonst bremst die Dämpfung den Stoff gegen den Körper,
                // der ihn trägt, und er bleibt bei 20 cm je Bild 0,5 cm je Bild zurück.
                const vAnker = p >= 0 ? mit * (zAlt[p + k] - zAlt2[p + k]) : 0;
                let freiBewegt = alt + v - (1 - dv) * (v - vAnker) + werte.G[k] * g * f;
                if (p >= 0) freiBewegt += mit * (ziel[p + k] - 2 * zAlt[p + k] + zAlt2[p + k]);
                // Die Lage MISCHT sich aus freier Bewegung und Ziel - nicht Ziel PLUS Geschwindigkeit:
                // so addiert lief jeder Haftpunkt seiner Lage einen Schritt voraus (bei 3 m/s 5 cm),
                // und wo die Freiheit wechselt, riss es (Browser, Jump: p99 4,26, 4.168 Kanten über
                // dem Dreifachen, alle zwischen Hüfte und Brust).
                x[o + k] = freiBewegt + (ziel[o + k] - freiBewegt) * zug;
                xAlt[o + k] = alt;
            }
        }
        for (let d = 0; d < werte.DURCHGAENGE; d++) {
            // Anker VOR den Kanten, in jedem Durchgang: einmal am Ende gesetzt, standen
            // Nachbarn am Saum auf verschiedenen Kugeln (verschiedene Anker, verschiedene
            // Reichweiten) und die Kante dazwischen blieb gedehnt (Browser, Jump: p99 5,9).
            if (this.anker) Stoffanker.halten(x, frei, n, this.anker.anker, this.anker.reichweite);
            Stoffkanten.halten(x, frei, this.kanten);
        }
        Stoffkanten.biegen(x, frei, this.biegung, werte.BIEGUNG);
        // Körper, Kanten, Körper: Nach dem ersten Hinausdrücken zieht ein Kantendurchgang die
        // Nachbarn nach (eine Kapsel, die in einem Bild 15 cm durch den Streifen fegt, ließ die
        // Kante zur Nachbarreihe sonst ein Bild lang 1,8-fach gedehnt), der zweite stellt
        // sicher, dass nichts im Körper bleibt.
        this._koerper(kapseln, kapselnAlt, werte, false);
        if (werte.DURCHGAENGE > 0) Stoffkanten.halten(x, frei, this.kanten);
        this._koerper(kapseln, kapselnAlt, werte, haut);
        // Lage dieses Schritts merken (zwei zurück, für die Ankerbeschleunigung).
        this._zielAlt2 = zAlt; this._zielAlt = zAlt2; this._zielAlt.set(ziel);
        return x;
    }

    /** Kapseln (mit der Seite von vorhin) und, mit `haut`, die Haut: alles Freie aus dem Körper heraus. */
    _koerper(kapseln, kapselnAlt, werte, haut) {
        const { x, xAlt, frei, n } = this;
        if (kapseln.length) Stoffkoerper.hinaus(x, frei, n, kapseln, werte.ABSTAND, kapselnAlt, xAlt);
        if (haut && this.oberflaeche) this.oberflaeche.hinaus(x, frei, n, werte.ABSTAND);
    }

    /** Größter Abstand eines freien Punkts von seiner gehäuteten Lage (m). */
    auslenkung(ziel) {
        let max = 0;
        for (let i = 0; i < this.n; i++) {
            if (this.frei[i] <= 0) continue;
            const o = 3 * i;
            const dx = this.x[o] - ziel[o], dy = this.x[o + 1] - ziel[o + 1], dz = this.x[o + 2] - ziel[o + 2];
            const d = dx * dx + dy * dy + dz * dz;
            if (d > max) max = d;
        }
        return Math.sqrt(max);
    }
}
