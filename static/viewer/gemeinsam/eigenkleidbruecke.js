import { Querschnitthuelle } from './querschnitthuelle.js';

/**
 * Eigenkleidbruecke — wie weit Stoff über den Mulden der Haut stehen muss, damit er eine Brücke spannt statt einzusinken (Stufe K2a, 25.10.2026, Edgar: „drapierungen
 * so dass man die Hautformen darunter nicht sieht, wie bei einem T-Shirt über die Brust, das legt sich nicht an der Haut zwischen den Brüsten“).
 *
 * EINGANG (stückunabhängig): die Punkte eines Netzes in Ruhelage (`position`, xyz) und ihre Körperkoordinaten (`Koerperkoordinatenpunkte`). Gerechnet wird auf DER
 * Haut, die gerade da ist — jede Figur, jeder Reglerstand; der Rufer rechnet nach jedem Neubau neu (`Eigenkleidgeometrie`).
 * BEREICH: der Rumpf (Kette 1) und die Beinpunkte über dem Schritt (Höhe < 1) — so bleibt der Querschnitt bis zum Schritt EIN Ring (Gesäßfalte), die Arme stehen
 * frei daneben und zählen nicht.
 *
 * HINDERNIS sind die Wölbungen der Haut selbst (Brust, Schulterblätter, Gesäß). Je waagrechter Scheibe (`SCHEIBE_M`, Mitte = EINE Achse für alle Scheiben,
 * `_mitten`) die konvexe Hülle (`Querschnitthuelle`), je Richtung (`WINKEL` Strahlen, 0 = vorn) ihr Halbmesser und der Weg vom Treffpunkt zur nächsten STÜTZE
 * (Eckpunkt = Hautpunkt, auf dem der Stoff aufliegt). Darauf von oben nach unten der FALL: Stoff kommt je Meter abwärts höchstens `FALL` Meter nach innen (unter
 * der Brust, unter den Schulterblättern, unter einem Bauch hängt er), mit dem Weg zur Scheibe, an der der Fall begann.
 * Die drei Regler sind die des Drapierers an Hosen (`Genesis9/drapierer.py`: Abstand, Ausbreitung, Glättung 0 Membran = straff … 1 Platte = weich), allgemein
 * beschriftet; dessen Rechnung (Hindernisproblem für das Hubfeld eines Stoffnetzes, scipy auf dem Server) passt nicht auf eine Schale, die ihre eigene Haut als
 * Hindernis hat — übernommen sind die Bedeutungen. Der Shader (`EigenkleidGLSL.kkHub`) blendet die Brücke nach dem Weg zur Stütze aus (Ausbreitung) und mischt
 * ZELT (gerade Kanten der Hülle, straff) und RUND (der Halbmesser der HAUT über ±`RUND_WINKEL` Strahlen und ±`RUND_SCHEIBEN` Scheiben gemittelt, nie unter der Haut —
 * weich: der Stoff sinkt gerundet in die Mulde; im Chrome war die geglättete Hülle in der Brustmitte nur 0,7 mm von der Zelt-Fassung entfernt).
 * `FALL` (Vorgabe; seit 25.10.2026 nachts Regler „Fall unter Wölbungen“), `HUB_MAX_M` und die Rundung sind GESETZT (Augenmaß), nicht gemessen.
 *
 * AUSGANG je Punkt zwei Felder zu je 4 Werten (m): `feld` (Hubrichtung waagrecht von der Mitte weg x, z; Hub Hülle; Hub Hülle + Fall — Zelt) und `feldB` (Hub Hülle
 * rund; Hub Hülle + Fall rund; Weg zur Stütze; Weg im Fall) und `feldC` (Neigung dr/dy Zelt, rund; –; –); außerhalb des Bereichs 0. „Fall“ heißt seit 25.10.2026
 * nachts: senkrechte Hülle über der Wölbung (`_zelt`) und Fall darunter. Dazu `rumpfLaenge` (m, Halsansatz bis Schritt DIESER Figur, aus Höhe und y der
 * Rumpfpunkte ausgeglichen) — der Shader rechnet damit Säume in Meter um.
 */
export class Eigenkleidbruecke {

    static SCHEIBE_M = 0.01;
    static WINKEL = 90;
    static FALL = 0.5;
    static HUB_MAX_M = 0.08;
    static RUND_WINKEL = 4;
    static RUND_SCHEIBEN = 2;
    static OBEN_AB = 0.12;
    static OBEN_VOLL = 0.2;
    static SAUM_RAND = 0.03;

    /** `armanteil`: Rumpfpunkte der Schulterkappe (Armanteil über −0,15) zählen nicht — von ihnen fiel der Stoff seitlich als Kasten bis zur Taille (im Chrome
     *  gesehen, 25.10.2026 nachts, nachdem der Fall langsamer wurde); unter dem Arm hängt er von der Achsel, nicht von der Schulter. */
    static imBereich(kette, hoehe, armanteil = -0.5) {
        return (kette === 1 && armanteil <= -0.15) || ((kette === 4 || kette === 5) && hoehe < 1);
    }

    /**
     * `fall`: m nach innen je m abwärts (Regler „Fall unter Wölbungen“, `Eigenkleidgeometrie.fallen`); ohne Angabe `FALL`. `saum` (Rumpfhöhe): nur Haut ÜBER dem Saum
     * des Stücks trägt — sonst spannte das Zelt das Kleid-Oberteil von der Hüfte aus über die Taille (im Chrome gesehen: Bahnen neben dem Rumpf, 33–53 mm Zelthub
     * seitlich und hinten); ohne Angabe alles (Hose).
     */
    static rechnen(position, koord, fall = Eigenkleidbruecke.FALL, saum = Infinity) {
        const t0 = performance.now();
        const n = koord.kette.length, dy = Eigenkleidbruecke.SCHEIBE_M, w = Eigenkleidbruecke.WINKEL;
        let ymin = Infinity, ymax = -Infinity, m = 0, sh = 0, sy = 0, shh = 0, shy = 0;
        for (let p = 0; p < n; p++) {
            const k = koord.kette[p], h = koord.hoehe[p], y = position[3 * p + 1];
            if (k === 1) { m++; sh += h; sy += y; shh += h * h; shy += h * y; }
            if (Eigenkleidbruecke.imBereich(k, h)) { ymin = Math.min(ymin, y); ymax = Math.max(ymax, y); }
        }
        const rumpfLaenge = m > 10 ? -(m * shy - sh * sy) / (m * shh - sh * sh) : null;
        const feld = new Float32Array(4 * n), feldB = new Float32Array(4 * n), feldC = new Float32Array(4 * n);
        if (!Number.isFinite(ymin)) return { feld, feldB, feldC, rumpfLaenge, punkte: 0, ms: 0 };
        const s = Math.max(1, Math.ceil((ymax - ymin) / dy));
        // `glieder` bilden die Hülle (Stützen: ohne Schulterkappe, nur über dem Saum); `empfaenger` bekommen den Hub — ALLE Punkte des Bereichs. Bis 25.10.2026 23:55
        // waren beide dieselbe Menge: die Schulterkappe bekam 0 statt des ausgeblendeten Hubs (`_ort`), daneben voller Hub — Risse an der Achsel, Striche auf der
        // Schulter (Edgar, mit Bild: „das hat doch kaputte Teile“)
        const glieder = Array.from({ length: s }, () => []), empfaenger = Array.from({ length: s }, () => []);
        const traegt = p => (koord.kette[p] === 1 ? koord.hoehe[p] <= saum + Eigenkleidbruecke.SAUM_RAND : saum >= 1);
        for (let p = 0; p < n; p++) {
            if (!Eigenkleidbruecke.imBereich(koord.kette[p], koord.hoehe[p])) continue;
            const i = Math.min(s - 1, Math.floor((position[3 * p + 1] - ymin) / dy));
            empfaenger[i].push(p);
            if (Eigenkleidbruecke.imBereich(koord.kette[p], koord.hoehe[p], koord.anteil[p]) && traegt(p)) glieder[i].push(p);
        }
        const [cx, cz] = Eigenkleidbruecke._mitten(position, glieder);
        const huelle = new Float32Array(s * w), stuetze = new Float32Array(s * w), haut = new Float32Array(s * w);
        for (let i = 0; i < s; i++) {
            const pkt = glieder[i].map(p => [position[3 * p] - cx[i], position[3 * p + 2] - cz[i]]);
            Querschnitthuelle.scheibe(pkt, huelle.subarray(i * w, (i + 1) * w), stuetze.subarray(i * w, (i + 1) * w));
            Eigenkleidbruecke._haut(pkt, huelle.subarray(i * w, (i + 1) * w), haut.subarray(i * w, (i + 1) * w));
        }
        const gemittelt = Eigenkleidbruecke._mitteln(haut, s, w);
        const rund = haut.map((v, i) => Math.max(v, gemittelt[i]));
        const zelt = Eigenkleidbruecke._senkrechtGlatt(Eigenkleidbruecke._rundum(Eigenkleidbruecke._fallen(Eigenkleidbruecke._zelt(huelle, s, w), s, w, fall), s, w), huelle, s, w);
        const rundFall = Eigenkleidbruecke._senkrechtGlatt(Eigenkleidbruecke._rundum(Eigenkleidbruecke._fallen(Eigenkleidbruecke._zelt(rund, s, w), s, w, fall), s, w), rund, s, w);
        const g = { huelle, stuetze, rund, zelt, rundFall, neigZ: Eigenkleidbruecke._neigung(zelt.e, s, w), neigR: Eigenkleidbruecke._neigung(rundFall.e, s, w) };
        let punkte = 0, maxH = 0, maxF = 0;
        const max = Eigenkleidbruecke.HUB_MAX_M;
        for (let i = 0; i < s; i++) {
            for (const p of empfaenger[i]) {
                const lage =(position[3 * p + 1] - ymin) / dy - 0.5;
                const i0 = Math.max(0, Math.min(s - 1, Math.floor(lage))), i1 = Math.min(s - 1, i0 + 1), f = Math.max(0, Math.min(1, lage - i0));
                const dx = position[3 * p] - (cx[i0] * (1 - f) + cx[i1] * f), dz = position[3 * p + 2] - (cz[i0] * (1 - f) + cz[i1] * f);
                const r = Math.hypot(dx, dz) || 1e-6;
                const kf = ((Math.atan2(dx, dz) / (2 * Math.PI) + 1) % 1) * w;
                const k0 = Math.floor(kf) % w, k1 = (k0 + 1) % w, a = kf - Math.floor(kf);
                const wert = v => (v[i0 * w + k0] * (1 - a) + v[i0 * w + k1] * a) * (1 - f) + (v[i1 * w + k0] * (1 - a) + v[i1 * w + k1] * a) * f;
                const armanteil = koord.kette[p] === 1 ? koord.anteil[p] : -0.5;
                const ort = Eigenkleidbruecke._ort(koord.hoehe[p], armanteil), ortV = Eigenkleidbruecke._ort(koord.hoehe[p], armanteil, true);
                const hubH = ort * Math.min(max, Math.max(0, wert(huelle) - r)), hubF = Math.max(hubH, ortV * Math.min(max, Math.max(0, wert(g.zelt.e) - r)));
                const rundH = ort * Math.min(max, Math.max(0, wert(rund) - r)), rundF = Math.max(rundH, ortV * Math.min(max, Math.max(0, wert(g.rundFall.e) - r)));
                feld.set([dx / r, dz / r, hubH, hubF], 4 * p);
                feldB.set([rundH, rundF, wert(stuetze), wert(g.zelt.weg)], 4 * p);
                feldC.set([wert(g.neigZ), wert(g.neigR), 0, 0], 4 * p);
                punkte++; maxH = Math.max(maxH, hubH); maxF = Math.max(maxF, hubF);
            }
        }
        return { feld, feldB, feldC, rumpfLaenge, punkte, scheiben: s, maxHuelleM: maxH, maxFallM: maxF, ms: Math.round(performance.now() - t0) };
    }

    /**
     * Wo die Brücke gilt (0…1): nicht über Schulterhöhe (Rumpfhöhe < `OBEN_AB`…`OBEN_VOLL`) und nicht an der Achsel (Armanteil eines Rumpfpunkts über −0,15) — dort
     * spannte die waagrechte Hülle über den Trapezmuskel bzw. quer über die Achselhöhle (im Chrome gesehen: helle Absätze an der Schulter, ein Keil an der Achsel).
     * `senkrecht` (Zelt und Fall): erst ab `OBEN_V_AB`…`OBEN_V_VOLL` — die Brust beginnt bei DamiraAlt unter 20 % Rumpfhöhe, mit der waagrechten Grenze lag der Stoff
     * oben auf der Brust an und zeichnete ihre Rundung (im Chrome gesehen, Seitenansicht, 25.10.2026 nachts).
     */
    static OBEN_V_AB = 0.02;
    static OBEN_V_VOLL = 0.08;

    static _ort(hoehe, armanteil, senkrecht = false) {
        const glatt = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
        const [ab, voll] = senkrecht ? [Eigenkleidbruecke.OBEN_V_AB, Eigenkleidbruecke.OBEN_V_VOLL] : [Eigenkleidbruecke.OBEN_AB, Eigenkleidbruecke.OBEN_VOLL];
        return glatt(ab, voll, hoehe) * (1 - glatt(-0.15, -0.05, armanteil));
    }

    /** Fall von oben nach unten: höchstens fall·dy nach innen je Scheibe; `weg` = Meter seit der Scheibe, an der der Fall begann (0, wo die Hülle trägt). */
    static _fallen(v, s, w, fall) {
        const e = v.slice(), weg = new Float32Array(s * w), dy = Eigenkleidbruecke.SCHEIBE_M;
        for (let i = s - 2; i >= 0; i--) {
            for (let k = 0; k < w; k++) {
                const oben = e[(i + 1) * w + k] - fall * dy;
                if (oben > e[i * w + k]) { e[i * w + k] = oben; weg[i * w + k] = weg[(i + 1) * w + k] + dy; }
            }
        }
        return { e, weg };
    }

    /**
     * Senkrechte Hülle je Strahl (Edgar, 25.10.2026 nachts: „die Drapierung soll so weit gehen, dass keine Körperformen erkennbar sind“): ÜBER einer Wölbung (Brust,
     * Schulterblätter, Gesäß) spannt der Stoff gerade von der Stütze darüber zur Wölbung, statt ihrer Rundung zu folgen. Obere konkave Hülle der Halbmesser über die
     * Höhe (monotone Kette); genommen nur die Strecken, die nach unten nach außen gehen — darunter hängt der Stoff (`_fallen`, Regler „Fall unter Wölbungen“).
     */
    static _zelt(v, s, w) {
        const e = v.slice(), kette = new Int32Array(s);
        for (let k = 0; k < w; k++) {
            let n = 0;
            for (let i = 0; i < s; i++) {
                while (n >= 2) {
                    const a = kette[n - 2], b = kette[n - 1];
                    if ((b - a) * (v[i * w + k] - v[a * w + k]) - (v[b * w + k] - v[a * w + k]) * (i - a) >= 0) n--; else break;
                }
                kette[n++] = i;
            }
            for (let j = 0; j + 1 < n; j++) {
                const a = kette[j], b = kette[j + 1], ra = v[a * w + k], rb = v[b * w + k];      // a unten, b oben
                if (ra <= rb) continue;
                for (let i = a + 1; i < b; i++) e[i * w + k] = Math.max(e[i * w + k], ra + (rb - ra) * (i - a) / (b - a));
            }
        }
        return e;
    }

    /**
     * Nach Zelt und Fall jede Scheibe noch einmal konvex (`{e, weg}` an Ort und Stelle): Der Fall hängt Strahl für Strahl — neben der Brust hing keiner, und der
     * Vorhang unter ihr endete seitlich mit einer Kante (im Chrome gesehen, Seitenansicht, 25.10.2026 nachts). So läuft er gerade zur Seite des Rumpfs.
     */
    static _rundum(g, s, w) {
        const halb = new Float32Array(w), weg = new Float32Array(w);
        for (let i = 0; i < s; i++) {
            const pkt = [];
            for (let k = 0; k < w; k++) {
                const r = g.e[i * w + k], t = 2 * Math.PI * k / w;
                if (r > 0) pkt.push([r * Math.sin(t), r * Math.cos(t)]);
            }
            halb.fill(0);
            Querschnitthuelle.scheibe(pkt, halb, weg);
            for (let k = 0; k < w; k++) g.e[i * w + k] = Math.max(g.e[i * w + k], halb[k]);
        }
        return g;
    }

    /**
     * Senkrecht über ±`GLATT_SCHEIBEN` Scheiben mitteln, nie unter `basis` (Hülle der Haut) — nach `_rundum` schwankte der Halbmesser vor der Brust von Scheibe zu
     * Scheibe: Treppe im Umriss und Streifen im Licht im Abstand der Scheiben (im Chrome gesehen, T-Shirt, Seitenansicht, 26.10.2026 0:05).
     */
    static GLATT_SCHEIBEN = 2;

    /** Dazu über ±`GLATT_STRAHLEN` Strahlen (ringförmig): das Zelt hängt je Strahl an eigenen Stützen — Nachbarstrahlen hatten verschiedene Neigungen, an den Seiten des
     *  T-Shirts senkrechte Streifen im Licht (im Chrome gesehen, 26.10.2026 0:30). */
    static GLATT_STRAHLEN = 2;

    static _senkrechtGlatt(g, basis, s, w) {
        const e = new Float32Array(s * w), a = new Float32Array(s * w), n = Eigenkleidbruecke.GLATT_SCHEIBEN, m = Eigenkleidbruecke.GLATT_STRAHLEN;
        for (let i = 0; i < s; i++) {
            const u = Math.max(0, i - n), o = Math.min(s - 1, i + n);
            for (let k = 0; k < w; k++) {
                let summe = 0;
                for (let j = u; j <= o; j++) summe += g.e[j * w + k];
                a[i * w + k] = summe / (o - u + 1);
            }
        }
        for (let i = 0; i < s; i++) {
            for (let k = 0; k < w; k++) {
                let summe = 0;
                for (let d = -m; d <= m; d++) summe += a[i * w + ((k + d + w) % w)];
                e[i * w + k] = Math.max(basis[i * w + k], summe / (2 * m + 1));
            }
        }
        g.e = e;
        return g;
    }

    /** Neigung des Halbmessers über die Höhe (dr/dy, über ±2 Scheiben, auf ±2 begrenzt) — für das Licht: die Normale der Stofffläche ist Hubrichtung − dr/dy · oben. */
    static _neigung(e, s, w) {
        const aus = new Float32Array(s * w), dy = Eigenkleidbruecke.SCHEIBE_M;
        for (let i = 0; i < s; i++) {
            const o = Math.min(s - 1, i + 2), u = Math.max(0, i - 2);
            if (o === u) continue;
            for (let k = 0; k < w; k++) aus[i * w + k] = Math.max(-2, Math.min(2, (e[o * w + k] - e[u * w + k]) / ((o - u) * dy)));
        }
        return aus;
    }

    /** Halbmesser der Haut je Strahl (größter Halbmesser der Punkte dieses Winkelfachs); ein leeres Fach nimmt die Hülle. */
    static _haut(pkt, huelle, aus) {
        const w = aus.length;
        aus.fill(-1);
        for (const [x, z] of pkt) {
            const k = Math.round(((Math.atan2(x, z) / (2 * Math.PI) + 1) % 1) * w) % w;
            aus[k] = Math.max(aus[k], Math.hypot(x, z));
        }
        for (let k = 0; k < w; k++) if (aus[k] < 0) aus[k] = huelle[k];
    }

    /** Halbmesser über ±RUND_WINKEL Strahlen (ringförmig) und ±RUND_SCHEIBEN Scheiben gemittelt — mit `haut` die runde Fassung (weich: sinkt gerundet ein). */
    static _mitteln(v, s, w) {
        const a = new Float32Array(s * w), b = new Float32Array(s * w), rw = Eigenkleidbruecke.RUND_WINKEL, rs = Eigenkleidbruecke.RUND_SCHEIBEN;
        for (let i = 0; i < s; i++) {
            for (let k = 0; k < w; k++) { let summe = 0; for (let d = -rw; d <= rw; d++) summe += v[i * w + ((k + d + w) % w)]; a[i * w + k] = summe / (2 * rw + 1); }
        }
        for (let i = 0; i < s; i++) {
            for (let k = 0; k < w; k++) {
                let summe = 0, z = 0;
                for (let j = Math.max(0, i - rs); j <= Math.min(s - 1, i + rs); j++) { summe += a[j * w + k]; z++; }
                b[i * w + k] = summe / z;
            }
        }
        return b;
    }

    /**
     * EINE senkrechte Achse für alle Scheiben: das Mittel der Rechteckmitten (x und z). Bis 25.10.2026 nachts je Scheibe die eigene Mitte (über fünf Scheiben
     * geglättet) — in Brusthöhe rückte sie um die halbe Brust nach vorn, seitlich und hinten wuchs der Halbmesser dort, und der Fall trug den Überschuss nach unten:
     * im Chrome Stoffbahnen neben dem Rumpf bis zur Taille, 31–46 mm Fallhub an der Seite (gemessen, Attribut `kkBruecke.w` je Höhe und Winkel). Zelt und Fall
     * vergleichen Halbmesser ÜBER die Scheiben — das geht nur von derselben Achse aus.
     */
    static _mitten(position, glieder) {
        const s = glieder.length, cx = new Float64Array(s), cz = new Float64Array(s), da = new Uint8Array(s);
        for (let i = 0; i < s; i++) {
            let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
            for (const p of glieder[i]) {
                x0 = Math.min(x0, position[3 * p]); x1 = Math.max(x1, position[3 * p]);
                z0 = Math.min(z0, position[3 * p + 2]); z1 = Math.max(z1, position[3 * p + 2]);
            }
            if (glieder[i].length) { cx[i] = (x0 + x1) / 2; cz[i] = (z0 + z1) / 2; da[i] = 1; }
        }
        const n = da.reduce((a, b) => a + b, 0) || 1;
        const mx = cx.reduce((a, v, i) => a + (da[i] ? v : 0), 0) / n, mz = cz.reduce((a, v, i) => a + (da[i] ? v : 0), 0) / n;
        return [cx.fill(mx), cz.fill(mz)];
    }
}
