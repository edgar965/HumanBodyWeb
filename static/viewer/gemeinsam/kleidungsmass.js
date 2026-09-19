/**
 * Kleidungsmass — Maße zwischen einem Stück und dem Körper auf flachen
 * Punktfeldern (n·3), ohne Three.js: Kantendehnung, Abstand zum nächsten
 * Körperpunkt, Tiefe hinter einer Fläche. Für die `Kleidungsprobe`
 * (`scene/kleidungsprobe.js`), die eine Animation im laufenden Chrome
 * Bild für Bild misst — und in Node prüfbar (`test_js_kleidungsmass`).
 *
 * WARUM (Edgar, 19.09.2026 nachts: „teste mit der ganzen Animation … die Arme
 * sollen nicht in die Kleider hineinragen, die Hose soll am Körper bleiben"
 * und „teste nur in chrome, du blockierst den ganzen Rechner"): Was der
 * Browser zeigt, wird im Browser gemessen — dieselben gehäuteten Punkte,
 * die der Shader zeichnet (`Stoffhaut.welt`), keine Nachrechnung in Python.
 *
 * Nächste Nachbarn über ein Würfelraster mit Kantenlänge `weite`: ein Punkt
 * sieht die 27 Zellen um sich; was weiter als `weite` weg ist, gilt als
 * „nicht nah" (Abstand = weite). Das reicht, weil nur Nähe zählt.
 */
export class Kleidungsmass {

    /** Perzentil (0..1) einer Liste — 0 für eine leere. */
    static perzentil(werte, p) {
        if (!werte.length) return 0;
        const s = Float64Array.from(werte).sort();
        return s[Math.min(s.length - 1, Math.floor(s.length * p))];
    }

    /** Die Kanten eines Dreiecksindex, jede einmal: `{a: Uint32Array, b: Uint32Array}`. */
    static kanten(index) {
        const gesehen = new Set(), a = [], b = [];
        for (let t = 0; t + 2 < index.length; t += 3) {
            for (let k = 0; k < 3; k++) {
                const i = index[t + k], j = index[t + (k + 1) % 3];
                if (i === j) continue;
                const lo = Math.min(i, j), hi = Math.max(i, j), s = lo * 4294967296 + hi;
                if (gesehen.has(s)) continue;
                gesehen.add(s); a.push(lo); b.push(hi);
            }
        }
        return { a: Uint32Array.from(a), b: Uint32Array.from(b) };
    }

    /** Dehnung jeder Kante (bewegt/ruhe, 1 = unverändert) als Float64Array. */
    static dehnung(ruhe, bewegt, kanten) {
        const n = kanten.a.length, aus = new Float64Array(n);
        for (let e = 0; e < n; e++) {
            const i = 3 * kanten.a[e], j = 3 * kanten.b[e];
            const l0 = Math.hypot(ruhe[i] - ruhe[j], ruhe[i + 1] - ruhe[j + 1], ruhe[i + 2] - ruhe[j + 2]);
            const l1 = Math.hypot(bewegt[i] - bewegt[j], bewegt[i + 1] - bewegt[j + 1], bewegt[i + 2] - bewegt[j + 2]);
            aus[e] = l0 > 1e-9 ? l1 / l0 : 1;
        }
        return aus;
    }

    /** Flächengewichtete Punktnormalen (n·3, Länge 1) aus einem Dreiecksindex. */
    static normalen(punkte, index, n) {
        const aus = new Float64Array(n * 3);
        for (let t = 0; t + 2 < index.length; t += 3) {
            const a = 3 * index[t], b = 3 * index[t + 1], c = 3 * index[t + 2];
            const ux = punkte[b] - punkte[a], uy = punkte[b + 1] - punkte[a + 1], uz = punkte[b + 2] - punkte[a + 2];
            const vx = punkte[c] - punkte[a], vy = punkte[c + 1] - punkte[a + 1], vz = punkte[c + 2] - punkte[a + 2];
            const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
            for (const o of [a, b, c]) { aus[o] += nx; aus[o + 1] += ny; aus[o + 2] += nz; }
        }
        for (let i = 0; i < n; i++) {
            const o = 3 * i, l = Math.hypot(aus[o], aus[o + 1], aus[o + 2]) || 1;
            aus[o] /= l; aus[o + 1] /= l; aus[o + 2] /= l;
        }
        return aus;
    }

    /** Ein Würfelraster über `punkte` (n·3) mit Zellweite `weite` (Meter). */
    static raster(punkte, n, weite) {
        const zellen = new Map(), w = weite;
        for (let i = 0; i < n; i++) {
            const s = Kleidungsmass._schluessel(punkte[3 * i], punkte[3 * i + 1], punkte[3 * i + 2], w);
            let liste = zellen.get(s);
            if (!liste) { liste = []; zellen.set(s, liste); }
            liste.push(i);
        }
        return { punkte, zellen, weite };
    }

    /** Zellschlüssel als Zahl (Zellen −1024…1023 je Achse) — Text wäre je Abfrage 27 Verkettungen. */
    static _schluessel(x, y, z, w) {
        return ((Math.floor(x / w) + 1024) * 2048 + Math.floor(y / w) + 1024) * 2048 + Math.floor(z / w) + 1024;
    }

    /** Nächster Rasterpunkt zu (x, y, z): `{i, d}` — i = -1 und d = weite, wenn keiner nah ist. */
    static naechster(raster, x, y, z) {
        const { punkte, zellen, weite } = raster;
        const cx = Math.floor(x / weite), cy = Math.floor(y / weite), cz = Math.floor(z / weite);
        let beste = -1, d2 = weite * weite;
        for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
            const liste = zellen.get(((cx + dx + 1024) * 2048 + cy + dy + 1024) * 2048 + cz + dz + 1024);
            if (!liste) continue;
            for (const i of liste) {
                const o = 3 * i, ex = punkte[o] - x, ey = punkte[o + 1] - y, ez = punkte[o + 2] - z;
                const e2 = ex * ex + ey * ey + ez * ez;
                if (e2 < d2) { d2 = e2; beste = i; }
            }
        }
        return { i: beste, d: Math.sqrt(d2) };
    }

    /** Abstand jedes `schritt`-ten Punkts (n·3) zum nächsten Rasterpunkt, gedeckelt auf `weite`. */
    static abstaende(punkte, n, raster, schritt = 1) {
        const aus = new Float64Array(Math.ceil(n / schritt));
        for (let i = 0, k = 0; i < n; i += schritt, k++) {
            aus[k] = Kleidungsmass.naechster(raster, punkte[3 * i], punkte[3 * i + 1], punkte[3 * i + 2]).d;
        }
        return aus;
    }

    /**
     * Tiefe jedes Punkts hinter der Fläche des Rasters (negativ = innen),
     * entlang der Normale des nächsten Flächenpunkts; NaN ohne nahen Punkt.
     * `wahl(i)` darf Flächenpunkte ausschließen (z. B. nur das Oberteil).
     */
    static tiefen(punkte, n, raster, normalen, wahl = null, schritt = 1) {
        const aus = new Float64Array(Math.ceil(n / schritt));
        for (let i = 0, k = 0; i < n; i += schritt, k++) {
            const x = punkte[3 * i], y = punkte[3 * i + 1], z = punkte[3 * i + 2];
            const { i: j } = Kleidungsmass.naechster(raster, x, y, z);
            if (j < 0 || (wahl && !wahl(j))) { aus[k] = NaN; continue; }
            const o = 3 * j;
            aus[k] = (x - raster.punkte[o]) * normalen[o] + (y - raster.punkte[o + 1]) * normalen[o + 1]
                   + (z - raster.punkte[o + 2]) * normalen[o + 2];
        }
        return aus;
    }

    /** Kennzahlen einer Liste: `{p1, p50, p95, p99, min, max, n}` — NaN wird übersprungen. */
    static kennzahlen(werte) {
        const g = Array.from(werte).filter(v => !Number.isNaN(v));
        if (!g.length) return { n: 0 };
        const P = (p) => Kleidungsmass.perzentil(g, p);
        let min = Infinity, max = -Infinity;
        for (const v of g) { if (v < min) min = v; if (v > max) max = v; }
        return { n: g.length, p1: P(0.01), p50: P(0.5), p95: P(0.95), p99: P(0.99), min, max };
    }
}
