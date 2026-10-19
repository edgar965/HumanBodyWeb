import { Anatomiemitte } from './anatomiemitte.js';
import { Dreiecksabstand } from './dreiecksabstand.js';
import { Strahldreieck } from './strahldreieck.js';

/**
 * Anatomiezuordnung — zu jedem Texel der Karte des Stücks die Stelle der Haut, auf der es liegt (11.10.2026, für `Anatomiebacken`).
 *
 * WARUM je Texel und nicht je Punkt (Edgar: „Skin änderung funktioniert nicht bei der Scham"; im Chrome gesehen, Haut „G9 Feminine Skin 04"): Die UV
 * der Haut springt an den Nähten ihrer Inseln und zwischen den Karten von Rumpf und Beinen. Ein UV je Punkt des Stücks zieht ein Dreieck über so
 * eine Naht über die halbe Karte (gemessen: 246 von 8.320 Dreiecken, Spanne 0,47–0,98, als Streifen in der Mittelfurche) und streckt die Ränder an
 * der Leiste. Hier wird die Karte des Stücks Texel für Texel gerechnet: Jedes Texel findet den nächsten Punkt der Hautfläche (Dreieck + Schwerpunkt),
 * die Haut-UV dort ist die richtige — an einer Naht links die Insel links, rechts die rechts, ohne Übergang.
 *
 * Ablauf: dichtes Gitter über die Hautdreiecke (Zellen `ZELLE`, in Zeilen abgelegt); je Dreieck des Stücks die Kandidaten, einmal auf die Mitte geprüft
 * (nur Dreiecke, die für irgendein Texel das nächste sein können: Abstand zur Mitte ≤ kleinster + 2 · Umkreis + `SCHLEPP`), nach diesem Abstand sortiert;
 * je Texel in der Fläche des Dreiecks (Mitte des Texels liegt drin) zuerst der nächste Punkt — die Suche bricht ab, sobald der Rest nicht mehr näher sein
 * kann —, dann, wenn das Stück Normalen hat, der Strahl entlang seiner Normale (`Strahldreieck`): Der nächste Punkt einer Fläche aus ebenen Facetten hängt an
 * den Kanten und Ecken (alle Texel über einer Kante bekamen dieselbe Stelle, Blöcke in der Karte), der Strahl geht stetig von Dreieck zu Dreieck. Der Treffer
 * des Strahls gilt, wo er flach genug auf der Haut steht und nicht weiter als 2,5 × der nächste Abstand liegt; sonst bleibt der nächste Punkt.
 * Texel, die kein Hautdreieck näher als `REICHWEITE` haben, bleiben leer (die Karte füllt sie auf). Weit vor der Haut hängende Stücke: `Anatomiemitte`.
 */
export class Anatomiezuordnung {

    /** Kantenlänge (m) der Gitterzellen — etwa die Kante eines Hautdreiecks (4 mm auf Stufe 1). */
    static ZELLE = 0.006;
    /** So weit (m) darf die Haut vom Stück entfernt liegen. „cute girl" Median 3 / größte 11,5 mm; „Daz Anatomie Frau" an DamiraAlt mit Einzug 4,8 / 17,5 mm (ohne: 14 / 31). */
    static REICHWEITE = 0.04;
    /** Erst so weit (m) um das Dreieck suchen; reicht das nicht für alle Texel, danach bis `REICHWEITE`. */
    static NAH = 0.012;
    /** Um so viel (m) mehr als der nächste Abstand bleiben Dreiecke Kandidaten: ein schräger Strahl trifft weiter seitlich (`Strahldreieck`). */
    static SCHLEPP = 0.003;
    /** Nach so vielen Millisekunden Rechnen wird dem Hauptfaden Luft gelassen. */
    static TAKT_MS = 25;
    /** Texel, deren Mitte so knapp (Anteil der Dreiecksfläche) außerhalb liegt, zählen noch dazu — keine Pinselstiche an den Kanten. */
    static RAND = 0.002;

    /**
     * @param stueck  `{pos: Float32Array, uv: Float32Array, index, normal?}` — `uv` je Punkt, bereits so gedreht, dass Zeile = v · Höhe gilt; `normal`: die Normalen je Punkt
     * @param haut    `{pos: Float32Array, ecken: Uint32Array}` — Punkte der Haut und die Ecken der in Frage kommenden Dreiecke (3 je Dreieck)
     * @param atmen   `async () => void` oder null — Gelegenheit für den Hauptfaden
     * @returns `{anzahl, texel, btri, l2, l3, stri, belegt}`: je belegtem Texel (Nummer `zeile · breite + spalte`) das Hautdreieck (Nummer in
     *          `haut.ecken`, geteilt durch 3), die Gewichte der zweiten und dritten Ecke und das Dreieck des Stücks
     */
    static async rechnen(stueck, haut, breite, hoehe, atmen = null) {
        const gitter = Anatomiezuordnung._gitter(haut);
        const belegt = new Uint8Array(breite * hoehe);
        const liste = { n: 0, texel: new Uint32Array(65536), btri: new Int32Array(65536), l2: new Float32Array(65536), l3: new Float32Array(65536), stri: new Int32Array(65536) };
        const index = stueck.index, ab = new Float64Array(3), dreiecke = Math.floor(index.length / 3), kands = [];
        let letzte = performance.now(), fern = 0;
        const luft = async (s) => { if (atmen && (s & 31) === 31 && performance.now() - letzte > Anatomiezuordnung.TAKT_MS) { await atmen(); letzte = performance.now(); } };
        for (let s = 0; s < dreiecke; s++) {
            kands.push(Anatomiezuordnung._kandidaten(gitter, haut, stueck.pos, [index[3 * s], index[3 * s + 1], index[3 * s + 2]], ab));
            if (Anatomiemitte.fern(kands[s])) fern++;
            await luft(s);
        }
        // Hängt das Stück weit vor der Haut (Penis: Matt0 54 % der Punkte über 20 mm), bildet `Anatomiemitte` es von einer Mitte im Becken aus ab.
        const stellen = fern > Anatomiemitte.ANTEIL * dreiecke ? Anatomiemitte.stellen(stueck, haut, gitter) : null;
        const dazu = (nr, bt, l2, l3, s) => Anatomiezuordnung._dazu(liste, nr, bt, l2, l3, s);
        for (let s = 0; s < dreiecke; s++) {
            const ecken = [index[3 * s], index[3 * s + 1], index[3 * s + 2]];
            if (stellen) Anatomiemitte.rastern(stueck, ecken, s, stellen, haut, gitter, breite, hoehe, belegt, dazu);
            else if (kands[s]) Anatomiezuordnung._rastern(stueck, ecken, s, kands[s], haut, breite, hoehe, belegt, liste, ab);
            await luft(s);
        }
        const n = liste.n;
        return { anzahl: n, texel: liste.texel.slice(0, n), btri: liste.btri.slice(0, n), l2: liste.l2.slice(0, n), l3: liste.l3.slice(0, n), stri: liste.stri.slice(0, n), belegt };
    }

    /**
     * Dichtes Gitter über den Kasten aller Hautdreiecke: `start[zelle] … start[zelle + 1]` sind die Stellen in `liste`, an denen die Nummern der
     * Dreiecke stehen, die die Zelle berühren (Kasten des Dreiecks). Zelle = `(x · ny + y) · nz + z`.
     */
    static _gitter(haut) {
        const z = Anatomiezuordnung.ZELLE, p = haut.pos, e = haut.ecken, nt = Math.floor(e.length / 3);
        const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i < e.length; i++) for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], p[3 * e[i] + k]); hi[k] = Math.max(hi[k], p[3 * e[i] + k]); }
        const n = [0, 1, 2].map(k => Math.max(1, Math.floor((hi[k] - lo[k]) / z) + 1));
        const g = { lo, n, zelle: z, start: new Int32Array(n[0] * n[1] * n[2] + 1), liste: null };
        const zellen = (t) => {
            const a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
            const von = [0, 1, 2].map(k => Math.floor((Math.min(p[a + k], p[b + k], p[c + k]) - lo[k]) / z));
            const bis = [0, 1, 2].map(k => Math.floor((Math.max(p[a + k], p[b + k], p[c + k]) - lo[k]) / z));
            return [von, bis];
        };
        for (const zaehlen of [true, false]) {
            const stelle = zaehlen ? null : Int32Array.from(g.start);
            for (let t = 0; t < nt; t++) {
                const [von, bis] = zellen(t);
                for (let x = von[0]; x <= bis[0]; x++) for (let y = von[1]; y <= bis[1]; y++) for (let w = von[2]; w <= bis[2]; w++) {
                    const zelle = (x * n[1] + y) * n[2] + w;
                    if (zaehlen) g.start[zelle + 1]++; else g.liste[stelle[zelle]++] = t;
                }
            }
            if (zaehlen) {
                for (let i = 0; i < g.start.length - 1; i++) g.start[i + 1] += g.start[i];
                g.liste = new Int32Array(g.start[g.start.length - 1]);
            }
        }
        g.marke = new Int32Array(nt);
        g.stempel = 0;
        // Mitte und Umkreis je Hautdreieck — für den Vorfilter in `_strahl`/`_naechster` (19.10.2026).
        g.mitte = new Float64Array(3 * nt);
        g.rad = new Float64Array(nt);
        for (let t = 0; t < nt; t++) {
            const a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
            const mx = (p[a] + p[b] + p[c]) / 3, my = (p[a + 1] + p[b + 1] + p[c + 1]) / 3, mz = (p[a + 2] + p[b + 2] + p[c + 2]) / 3;
            g.mitte[3 * t] = mx; g.mitte[3 * t + 1] = my; g.mitte[3 * t + 2] = mz;
            g.rad[t] = Math.sqrt(Math.max(...[a, b, c].map(o => (p[o] - mx) ** 2 + (p[o + 1] - my) ** 2 + (p[o + 2] - mz) ** 2)));
        }
        return g;
    }

    /**
     * Die Hautdreiecke, die für irgendein Texel des Dreiecks `ecken` das nächste sein können, nach dem Abstand ihrer Mitte geordnet:
     * `{ids, abstand, radius}` — oder null, wenn keines näher als `REICHWEITE` liegt.
     */
    static _kandidaten(g, haut, sp, ecken, ab) {
        const q = ecken.map(i => 3 * i), p = haut.pos, e = haut.ecken;
        const mitte = [0, 1, 2].map(k => (sp[q[0] + k] + sp[q[1] + k] + sp[q[2] + k]) / 3);
        const radius = Math.sqrt(Math.max(...q.map(o => (sp[o] - mitte[0]) ** 2 + (sp[o + 1] - mitte[1]) ** 2 + (sp[o + 2] - mitte[2]) ** 2)));
        const kleinste = [0, 1, 2].map(k => Math.min(sp[q[0] + k], sp[q[1] + k], sp[q[2] + k])), groesste = [0, 1, 2].map(k => Math.max(sp[q[0] + k], sp[q[1] + k], sp[q[2] + k]));
        const z = Anatomiezuordnung.ZELLE, reich = Anatomiezuordnung.REICHWEITE;
        let ids = [], abstand = [], kleinster = Infinity;
        for (const weite of [Anatomiezuordnung.NAH, reich]) {
            const von = [0, 1, 2].map(k => Math.max(0, Math.floor((kleinste[k] - weite - g.lo[k]) / z)));
            const bis = [0, 1, 2].map(k => Math.min(g.n[k] - 1, Math.floor((groesste[k] + weite - g.lo[k]) / z)));
            ids = []; abstand = []; kleinster = Infinity;
            g.stempel++;
            // Erst die Mitten (19.10.2026): genauer Abstand ≤ |Mitte − Punkt| (die Mitte liegt im Dreieck) und ≥ |Mitte − Punkt| − Umkreis. Den teuren genauen Abstand braucht nur, wer unter
            // der Schwelle liegen kann; die übrigen fielen unten aus der Liste. Exakt — gleiche Liste, gleiche Reihenfolge (gemessen an Damira0, ultrafein: 7,1 s von 15,5 s in dieser Suche).
            const kandidat = [], unten = [];
            let oben = Infinity;
            for (let x = von[0]; x <= bis[0]; x++) for (let y = von[1]; y <= bis[1]; y++) for (let w = von[2]; w <= bis[2]; w++) {
                const zelle = (x * g.n[1] + y) * g.n[2] + w;
                for (let i = g.start[zelle]; i < g.start[zelle + 1]; i++) {
                    const t = g.liste[i];
                    if (g.marke[t] === g.stempel) continue;
                    g.marke[t] = g.stempel;
                    const dx = g.mitte[3 * t] - mitte[0], dy = g.mitte[3 * t + 1] - mitte[1], dz = g.mitte[3 * t + 2] - mitte[2];
                    const dm = Math.sqrt(dx * dx + dy * dy + dz * dz);
                    kandidat.push(t); unten.push(dm - g.rad[t] - 1e-9);
                    if (dm < oben) oben = dm;
                }
            }
            const schwelle = oben + 2 * radius + Anatomiezuordnung.SCHLEPP + 1e-9;
            for (let k = 0; k < kandidat.length; k++) {
                if (unten[k] > schwelle) continue;
                const t = kandidat[k], a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
                Dreiecksabstand.naechster(mitte[0], mitte[1], mitte[2], p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], ab);
                const d = Math.sqrt(ab[0]);
                ids.push(t); abstand.push(d);
                if (d < kleinster) kleinster = d;
            }
            if (kleinster + 2 * radius + Anatomiezuordnung.SCHLEPP <= weite) break;          // alles, was für ein Texel noch das nächste sein kann, ist schon dabei
        }
        if (kleinster > reich) return null;
        const reihe = ids.map((t, k) => k).filter(k => abstand[k] <= kleinster + 2 * radius + Anatomiezuordnung.SCHLEPP + 1e-9).sort((a, b) => abstand[a] - abstand[b]);
        return { ids: Int32Array.from(reihe.map(k => ids[k])), abstand: Float64Array.from(reihe.map(k => abstand[k])), radius, mitte: g.mitte, rad: g.rad };
    }

    /** Die Texel in der Fläche des Stück-Dreiecks `s` (Ecken `ecken`) belegen: je Texel der Strahl entlang der Normale (`_strahl`), sonst der nächste Punkt unter den Kandidaten (`_naechster`). */
    static _rastern(stueck, ecken, s, kand, haut, breite, hoehe, belegt, liste, ab) {
        const sp = stueck.pos, uv = stueck.uv, sn = stueck.normal || null, eps = Anatomiezuordnung.RAND, hilf = new Float64Array(3);
        const x = ecken.map(i => uv[2 * i] * breite), y = ecken.map(i => uv[2 * i + 1] * hoehe), o = ecken.map(i => 3 * i);
        const flaeche = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0]);
        if (Math.abs(flaeche) < 1e-9) return;
        const j0 = Math.max(0, Math.floor(Math.min(...y))), j1 = Math.min(hoehe - 1, Math.floor(Math.max(...y)));
        const i0 = Math.max(0, Math.floor(Math.min(...x))), i1 = Math.min(breite - 1, Math.floor(Math.max(...x)));
        let vorher = -1;                                              // das Hautdreieck, das der Strahl des letzten Texels traf (Schranke in `_strahl`)
        const folge = sn ? Anatomiezuordnung._strahlfolge(kand, sp, sn, o) : null;
        for (let j = j0; j <= j1; j++) {
            for (let i = i0; i <= i1; i++) {
                const nr = j * breite + i;
                if (belegt[nr]) continue;
                const cx = i + 0.5, cy = j + 0.5;
                const w1 = ((cx - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (cy - y[0])) / flaeche;
                const w2 = ((x[1] - x[0]) * (cy - y[0]) - (cx - x[0]) * (y[1] - y[0])) / flaeche;
                const w0 = 1 - w1 - w2;
                if (w0 < -eps || w1 < -eps || w2 < -eps) continue;
                const px = w0 * sp[o[0]] + w1 * sp[o[1]] + w2 * sp[o[2]], py = w0 * sp[o[0] + 1] + w1 * sp[o[1] + 1] + w2 * sp[o[2] + 1], pz = w0 * sp[o[0] + 2] + w1 * sp[o[1] + 2] + w2 * sp[o[2] + 2];
                // Lieber der Strahl entlang der Normale des Stücks: stetig über die Kanten der Facetten; der nächste Punkt nur, wo kein Strahl trifft.
                let bt = sn ? Anatomiezuordnung._strahl(sn, o, w0, w1, w2, px, py, pz, kand, haut, ab, hilf, vorher, folge) : -1;
                if (bt >= 0) vorher = bt;
                else bt = Anatomiezuordnung._naechster(px, py, pz, kand, haut, ab, hilf);
                if (bt < 0) continue;
                belegt[nr] = 1;
                Anatomiezuordnung._dazu(liste, nr, bt, ab[1], ab[2], s);
            }
        }
    }

    /**
     * Die Kandidaten in der Folge, in der `_strahl` sie prüft (19.10.2026): nach dem Abstand ihrer Mitte zur Geraden durch die Mitte des Stück-Dreiecks entlang seiner mittleren
     * Normale, minus Umkreis. Jeder Texelstrahl des Dreiecks läuft nahe an dieser Geraden — höchstens Umkreis des Stück-Dreiecks + |t|·sin α daneben (α: größter Winkel einer
     * Eckennormale zur mittleren; die gemischte Normale eines Texels liegt in diesem Kegel) —, darum darf `_strahl` in dieser Folge abbrechen. Vorher lagen die Kandidaten nach
     * dem Abstand zur Mitte geordnet, fast alle im selben schmalen Band: jedes Texel ging die ganze Liste durch (Damira0 ultrafein: über tausend je Texel).
     * Ohne brauchbare Normalen die Liste, wie sie ist (`schluessel` −∞: kein Abbruch).
     */
    static _strahlfolge(kand, sp, sn, o) {
        const { ids, mitte, rad } = kand, m = ids.length;
        const roh = { folge: Int32Array.from({ length: m }, (_, k) => k), schluessel: new Float64Array(m).fill(-Infinity), sinus: 0 };
        const n = [0, 1, 2].map(k => sn[o[0] + k] + sn[o[1] + k] + sn[o[2] + k]), nl = Math.hypot(n[0], n[1], n[2]);
        if (!sp || !mitte || !(nl > 1e-9)) return roh;
        const nx = n[0] / nl, ny = n[1] / nl, nz = n[2] / nl;
        let cosmin = 1;
        for (const q of o) {
            const l = Math.hypot(sn[q], sn[q + 1], sn[q + 2]);
            if (!(l > 1e-9)) return roh;
            cosmin = Math.min(cosmin, (sn[q] * nx + sn[q + 1] * ny + sn[q + 2] * nz) / l);
        }
        if (cosmin <= 0.1) return roh;
        const mx = (sp[o[0]] + sp[o[1]] + sp[o[2]]) / 3, my = (sp[o[0] + 1] + sp[o[1] + 1] + sp[o[2] + 1]) / 3, mz = (sp[o[0] + 2] + sp[o[1] + 2] + sp[o[2] + 2]) / 3;
        const schl = new Float64Array(m);
        for (let k = 0; k < m; k++) {
            const t = ids[k], vx = mitte[3 * t] - mx, vy = mitte[3 * t + 1] - my, vz = mitte[3 * t + 2] - mz, l = vx * nx + vy * ny + vz * nz;
            schl[k] = Math.sqrt(Math.max(0, vx * vx + vy * vy + vz * vz - l * l)) - rad[t];
        }
        const folge = roh.folge.sort((a, b) => schl[a] - schl[b]);
        // +0,02: die Gewichte am Rand dürfen um `RAND` negativ sein — die Normale liegt dann ein wenig außerhalb des Kegels.
        return { folge, schluessel: Float64Array.from(folge, k => schl[k]), sinus: Math.sqrt(1 - cosmin * cosmin) + 0.02 };
    }

    /**
     * Das Hautdreieck, das der Strahl vom Punkt entlang der Normale des Stücks (in beide Richtungen) zuerst trifft: Nummer, `ab[1]`/`ab[2]` Gewichte; sonst −1. Bei gleichem
     * Abstand das, das in `kand` zuerst steht (`k`) — wie früher, als die Liste in dieser Reihenfolge durchlaufen wurde.
     */
    static _strahl(sn, o, w0, w1, w2, px, py, pz, kand, haut, ab, treffer, vorher = -1, folge = null) {
        const mx = w0 * sn[o[0]] + w1 * sn[o[1]] + w2 * sn[o[2]], my = w0 * sn[o[0] + 1] + w1 * sn[o[1] + 1] + w2 * sn[o[2] + 1], mz = w0 * sn[o[0] + 2] + w1 * sn[o[1] + 2] + w2 * sn[o[2] + 2];
        const ml = Math.hypot(mx, my, mz);
        if (!(ml > 1e-9)) return -1;
        const { ids, abstand, radius, mitte, rad } = kand, p = haut.pos, e = haut.ecken;
        const rx = mx / ml, ry = my / ml, rz = mz / ml;
        let grenze = Anatomiezuordnung.REICHWEITE, bt = -1, schranke = grenze;
        // Schranke (19.10.2026): das Dreieck des Nachbartexels (aus DERSELBEN Liste) trifft fast immer wieder; sein Abstand begrenzt die Suche von oben. Gewählt wird weiter
        // in der Reihenfolge der Liste — das erste Dreieck mit dem kleinsten Abstand, wie ohne Schranke (Gegenprobe `ProjektTemp/_wegwerf/anatomie_tempo/vergleich.mjs`).
        if (vorher >= 0) {
            const a = 3 * e[3 * vorher], b = 3 * e[3 * vorher + 1], c = 3 * e[3 * vorher + 2];
            if (Strahldreieck.trifft(px, py, pz, rx, ry, rz, p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], treffer)) schranke = treffer[0] + 1e-12;
        }
        const { folge: f, schluessel: sch, sinus } = folge || Anatomiezuordnung._strahlfolge(kand, null, sn, o);
        let bk = -1;
        for (let j = 0; j < f.length; j++) {
            const s = grenze < schranke ? grenze : schranke;
            if (sch[j] > radius * 1.01 + s * sinus + 1e-6) break;   // geordnet nach dem Abstand zur Geraden: der Rest liegt zu weit neben jedem Strahl dieses Dreiecks
            const k = f[j];
            if (abstand[k] - radius > s) continue;                   // weiter weg von der Mitte, als ein Treffer näher als `s` sein kann
            const t = ids[k], a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
            // Vorfilter (19.10.2026): der Treffer q = Punkt + t·Richtung (|t| < s) liegt im Dreieck, also höchstens `rad` von seiner Mitte — die Mitte liegt dann höchstens `rad` neben
            // der Geraden und längs höchstens s + rad vom Punkt. Exakt, kein anderes Ergebnis; vorher bekam jedes Kandidatendreieck den vollen Strahltest (gemessen an Damira0, fein:
            // 1,18 Mio. Texel, 4,9 s im Strahl).
            if (mitte) {
                const vx = mitte[3 * t] - px, vy = mitte[3 * t + 1] - py, vz = mitte[3 * t + 2] - pz, rr = rad[t] + 1e-9;
                const laengs = vx * rx + vy * ry + vz * rz;
                if (vx * vx + vy * vy + vz * vz - laengs * laengs > rr * rr || Math.abs(laengs) > s + rr) continue;
            }
            if (Strahldreieck.trifft(px, py, pz, rx, ry, rz, p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], treffer)
                && (treffer[0] < grenze || (treffer[0] === grenze && bt >= 0 && k < bk))) {
                grenze = treffer[0]; bt = t; bk = k; ab[1] = treffer[1]; ab[2] = treffer[2];
            }
        }
        return bt;
    }

    /** Das Hautdreieck mit dem nächsten Punkt (näher als `REICHWEITE`): Nummer, `ab[1]`/`ab[2]` Gewichte; sonst −1. */
    static _naechster(px, py, pz, kand, haut, ab, treffer) {
        const { ids, abstand, radius, mitte, rad } = kand, p = haut.pos, e = haut.ecken;
        let beste = Anatomiezuordnung.REICHWEITE ** 2, bt = -1;
        for (let k = 0; k < ids.length; k++) {
            const mind = abstand[k] - radius;                 // näher als das kann dieses Dreieck keinem Texel des Stück-Dreiecks sein
            if (mind > 0 && mind * mind >= beste) break;      // die Liste ist nach `abstand` geordnet: der Rest ist weiter weg
            const t = ids[k], a = 3 * e[3 * t], b = 3 * e[3 * t + 1], c = 3 * e[3 * t + 2];
            if (mitte) {                                      // Vorfilter wie in `_strahl`: näher als `|Mitte − Punkt| − Umkreis` kommt das Dreieck dem Punkt nicht
                const dx = mitte[3 * t] - px, dy = mitte[3 * t + 1] - py, dz = mitte[3 * t + 2] - pz;
                const d = Math.sqrt(dx * dx + dy * dy + dz * dz) - rad[t] - 1e-9;
                if (d > 0 && d * d >= beste) continue;
            }
            Dreiecksabstand.naechster(px, py, pz, p[a], p[a + 1], p[a + 2], p[b], p[b + 1], p[b + 2], p[c], p[c + 1], p[c + 2], treffer);
            if (treffer[0] < beste) { beste = treffer[0]; bt = t; ab[1] = treffer[1]; ab[2] = treffer[2]; }
        }
        return bt;
    }

    /** Ein Texel in die Liste (sie wächst in Verdopplungen). */
    static _dazu(liste, nr, bt, b2, b3, s) {
        if (liste.n === liste.texel.length) {
            for (const name of ['texel', 'btri', 'l2', 'l3', 'stri']) { const neu = new liste[name].constructor(liste[name].length * 2); neu.set(liste[name]); liste[name] = neu; }
        }
        const n = liste.n++;
        liste.texel[n] = nr; liste.btri[n] = bt; liste.l2[n] = b2; liste.l3[n] = b3; liste.stri[n] = s;
    }
}
