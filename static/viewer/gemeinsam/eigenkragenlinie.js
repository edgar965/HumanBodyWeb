/**
 * Eigenkragenlinie — wo auf der Haut der Ausschnitt eines eigenen Oberteils verläuft, als Linie im Raum (25.10.2026 nachts, Auftrag Edgar: „Kragen mit echter Geometrie
 * (Polo-/Hemdkragen, Stehkragen) … die am Ausschnittrand ansetzt“). Für `Eigenkragengeometrie`. Ohne Three.js, in Node prüfbar.
 *
 * DIESELBE KANTE WIE IM SHADER: Der Ausschnitt wird im Fragment-Shader je Pixel geschnitten (`EigenkleidschnittGLSL.kkHals`: f = (h − Ansatz − Tiefe(x, vorn))·L,
 * > 0 = Stoff). `hals` rechnet dieselbe Formel auf der CPU je Punkt (Höhe unter dem Halsansatz `kkAnsatz`, x der Ruhelage, vorn = cos des Umfangswinkels aus
 * `kkKoord`); die Linie f = c ist die Nullstelle über die
 * Dreiecke, linear auf den Kanten — der Shader interpoliert dieselben drei Größen linear über das Dreieck, die Linie trifft seine Kante also bis auf die Krümmung von
 * f innerhalb eines Dreiecks (fein: Kanten um 5 mm).
 * STUFEN: c = 0 ist der Rand; c < 0 liegt in der Öffnung (Hals, Haut im V), c > 0 auf dem Stoff darunter (Schulter, Brust) — daraus nimmt der Kragen seine
 * Richtungen: hinauf am Hals (Steg) und hinab über die Schulter (umgelegter Teil).
 * ABTASTEN nach dem Winkel um die Halsachse (Mitte der Halspunkte, Kette 6; 0 = vorn, +x = links der Figur), `FAECHER` Fächer: je Fach der Schnittpunkt mit dem
 * kleinsten Abstand zur Achse (der innere Ring; eine zweite Kreuzung weiter außen gehört nicht zum Ausschnitt); leere Fächer übernehmen das nächste besetzte.
 */
export class Eigenkragenlinie {

    static FAECHER = 240;
    /** Ketten der Körperkoordinaten, auf denen der Ausschnitt liegen kann: Rumpf, Hals, Kopf. */
    static KETTEN = new Set([1, 6, 7]);

    /** Wie `kkForm` im Shader. */
    static form(u, form) {
        const v = Math.min(1, Math.max(0, u));
        const s = form < 0.5 ? Math.sqrt(1 - v * v) : form < 1.5 ? 1 - v : form < 2.5 ? Math.sqrt(1 - v ** 4) : 1 - v ** 6;
        return u >= 1 ? 0 : s;
    }

    /** Wie `kkHals` im Shader; `w` = {form, tiefe, hinten, breite (m), laenge (m, Rumpf), steh (m, Stehkragenhöhe)}. */
    static hals(h, x, vorn, w) {
        const u = Math.abs(x) / Math.max(0.5 * w.breite, 0.001);
        const t = Math.min(1, Math.max(0, (vorn + 0.35) / 0.7)), mischung = t * t * (3 - 2 * t);
        const tiefe = w.hinten * Eigenkragenlinie.form(u, 0) * (1 - mischung) + w.tiefe * Eigenkragenlinie.form(u, w.form) * mischung;
        return w.form > 3.5 ? h * w.laenge + w.steh : (h - tiefe) * w.laenge;
    }

    /** Dreiecke (Eckindizes) auf Rumpf, Hals, Kopf in Halsnähe — einmal je Geometrie; `haut(start)` sagt, ob die Gruppe ab `start` Haut ist. */
    static bereich(index, gruppen, koord, haut) {
        const aus = [];
        const nah = p => Eigenkragenlinie.KETTEN.has(Math.round(koord[4 * p])) && koord[4 * p + 2] > -0.6 && koord[4 * p + 2] < 0.7;
        for (const g of gruppen) {
            if (!haut(g)) continue;
            for (let i = g.start; i + 2 < g.start + g.count; i += 3) {
                if (nah(index[i]) && nah(index[i + 1]) && nah(index[i + 2])) aus.push(index[i], index[i + 1], index[i + 2]);
            }
        }
        return Uint32Array.from(aus);
    }

    /** Mitte der Halspunkte (x, z) — die Achse, um die abgetastet wird. */
    static achse(position, koord) {
        let x = 0, z = 0, n = 0;
        for (let p = 0; p < koord.length / 4; p++) {
            if (Math.round(koord[4 * p]) !== 6) continue;
            x += position[3 * p]; z += position[3 * p + 2]; n++;
        }
        return n ? { cx: x / n, cz: z / n } : { cx: 0, cz: 0 };
    }

    /** f je Punkt des Bereichs (sonst NaN); `ansatz` = Höhe des Halsansatzes je Punkt (`kkAnsatz`, fehlt er: 0 wie im Shader). */
    static feld(position, koord, ansatz, dreiecke, w) {
        const f = new Float32Array(position.length / 3).fill(NaN);
        for (const p of dreiecke) {
            const h = koord[4 * p + 2] - (ansatz ? ansatz[p] : 0);
            if (Number.isNaN(f[p])) f[p] = Eigenkragenlinie.hals(h, position[3 * p], Math.cos(2 * Math.PI * koord[4 * p + 3]), w);
        }
        return f;
    }

    /**
     * Die Linie f = c, je Fach ein Schnittpunkt `{a, b, s}` (Punkt = a + s·(b − a)); `null`, wenn weniger als ein Viertel der Fächer besetzt ist (kein Ausschnitt da).
     */
    static stufe(position, dreiecke, f, c, achse) {
        const n = Eigenkragenlinie.FAECHER, best = new Array(n).fill(null), r = new Float64Array(n).fill(Infinity), gesehen = new Set();
        const kante = (a, b) => {
            const da = f[a] - c, db = f[b] - c;
            if ((da < 0) === (db < 0)) return;
            const schluessel = a < b ? a * 4194304 + b : b * 4194304 + a;
            if (gesehen.has(schluessel)) return;
            gesehen.add(schluessel);
            const s = da / (da - db);
            const x = position[3 * a] + s * (position[3 * b] - position[3 * a]) - achse.cx;
            const z = position[3 * a + 2] + s * (position[3 * b + 2] - position[3 * a + 2]) - achse.cz;
            const k = Math.min(n - 1, Math.floor(((Math.atan2(x, z) / (2 * Math.PI) + 1) % 1) * n)), abstand = Math.hypot(x, z);
            if (abstand < r[k]) { r[k] = abstand; best[k] = { a, b, s }; }
        };
        for (let i = 0; i < dreiecke.length; i += 3) {
            const [p, q, t] = [dreiecke[i], dreiecke[i + 1], dreiecke[i + 2]];
            kante(p, q); kante(q, t); kante(t, p);
        }
        const besetzt = best.filter(Boolean).length;
        if (besetzt < n / 4) return null;
        for (let k = 0; k < n; k++) {
            if (best[k]) continue;
            for (let d = 1; d < n; d++) {
                const q = best[(k + d) % n] || best[(k - d + n) % n];
                if (q) { best[k] = q; break; }
            }
        }
        return { punkte: best, besetzt };
    }

    /** Ein Attribut (Feld mit `breite` Werten je Punkt) am Schnittpunkt `e`. */
    static wert(feld, breite, e) {
        const aus = new Array(breite);
        for (let i = 0; i < breite; i++) aus[i] = feld[breite * e.a + i] * (1 - e.s) + feld[breite * e.b + i] * e.s;
        return aus;
    }
}
