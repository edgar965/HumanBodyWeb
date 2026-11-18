/**
 * Lockenpendel — die Rechnung der Bewegung je Locke ohne Three.js, prüfbar in Node (16.11.2026, Edgar zur Goldprinzessin: „Überlege dir was, mit dem Du einzelne Haare zu Strähnen
 * zusammenfasst … aber die Strähnen müssen eine eigene Bewegung haben“ — Option 2).
 *
 * Eine Locke ist eine Leitsträhne von `haar_Bart` (G Leitsträhnen zu je K+1 Punkten, `leitpunkte`); jede Strähne ihres Büschels folgt ihr (`leit` je Punkt, im Shader von
 * `Meshgenesishaarschwung`). Je Bild, je Leitpunkt k ≥ 1 (Verlet, wie `Zopfpendel` nach VRMC_springBone-1.0):
 *
 *     next = x + (x − prev)·(1 − DAEMPFUNG) + g·SCHWERE·dt² + (ziel − x)·STEIF
 *
 * `ziel` ist der Leitpunkt, gehäutet wie die Figur (die Locke ohne eigene Bewegung); Punkt 0 (die Wurzel) sitzt auf dem Ziel. Danach `RUNDEN` mal die Gliedlängen der Ruhe (von der
 * Wurzel aus), zuletzt die Auslenkung je Punkt höchstens `GRENZE_M` (die Locke stößt nicht durch den Körper — den Schub aus fremden Gliedern macht danach `Meshgenesiskollision`).
 * Die Stärke nimmt zur Spitze zu (`frei` = k / K): an der Wurzel hält die Haut, die Spitze schwingt. Zurück kommt die Verschiebung je Leitpunkt (Ziel → Locke), die der Shader
 * zu jedem Punkt der Locke addiert. Die Zahlen sind Setzungen (im Bild zu wählen).
 */
export class Lockenpendel {

    /** Dämpfung und Zug zur gehäuteten Locke je Bild: mit 0,12 / 0,08 lag die Spitze bei Tanztempo (≈ 1 m/s, 1,7 cm je Bild) rund 20 cm zurück, die Hälfte der Leitpunkte an der
     *  Grenze (goldprinzessin_mesh_genesis_20 im Browser) */
    static DAEMPFUNG = 0.25;
    /** Schwerkraft (m/s²) — 0: die Ruhe der Locke hängt schon (wie `Zopfpendel.GRAVITY_POWER`); mit 9,81 sank jede Spitze dauerhaft um die Grenze von 80 mm (gemessen an
     *  goldprinzessin_mesh_genesis_20 im Browser, Tanz), auch im Stand */
    static SCHWERE = 0.0;
    static STEIF = 0.3;
    static RUNDEN = 2;
    static GRENZE_M = 0.08;

    /**
     * @param ruhe Float32Array (G·(K+1)·3) Leitpunkte in Ruhe (für die Gliedlängen)
     * @param g, k1 Leitsträhnen und Punkte je Leitsträhne
     */
    static anlegen(ruhe, g, k1) {
        const laengen = new Float32Array(g * k1);
        for (let s = 0; s < g; s++) {
            for (let k = 1; k < k1; k++) {
                const a = (s * k1 + k - 1) * 3, b = (s * k1 + k) * 3;
                laengen[s * k1 + k] = Math.hypot(ruhe[b] - ruhe[a], ruhe[b + 1] - ruhe[a + 1], ruhe[b + 2] - ruhe[a + 2]);
            }
        }
        return { g, k1, laengen, x: null, prev: null, versatz: new Float32Array(g * k1 * 3) };
    }

    /** Zurück auf das Ziel (Stopp, Sprung in der Zeit). */
    static ruhe(zustand) {
        zustand.x = null;
        zustand.prev = null;
        zustand.versatz.fill(0);
    }

    /**
     * Ein Bild. @param ziel Float32Array (G·(K+1)·3) gehäutete Leitpunkte @param dt Sekunden @param unten [x, y, z] Richtung der Schwerkraft im Raum der Punkte (Einheit)
     * @returns Float32Array Verschiebung je Leitpunkt (Locke − Ziel), dieselbe Ablage wie `zustand.versatz`
     */
    static schritt(zustand, ziel, dt, unten, werte = Lockenpendel) {
        const { g, k1, laengen } = zustand;
        const n = g * k1 * 3;
        if (!zustand.x || !(dt > 0)) {
            zustand.x = Float32Array.from(ziel);
            zustand.prev = Float32Array.from(ziel);
            zustand.versatz.fill(0);
            return zustand.versatz;
        }
        const x = zustand.x, prev = zustand.prev;
        const h = Math.min(dt, 1 / 20);                                  // große Sprünge (Tab im Hintergrund) nicht als Wurf rechnen
        const tr = 1 - werte.DAEMPFUNG;
        const sx = unten[0] * werte.SCHWERE * h * h, sy = unten[1] * werte.SCHWERE * h * h, sz = unten[2] * werte.SCHWERE * h * h;
        for (let s = 0; s < g; s++) {
            const o0 = s * k1 * 3;
            x[o0] = ziel[o0]; x[o0 + 1] = ziel[o0 + 1]; x[o0 + 2] = ziel[o0 + 2];
            prev[o0] = x[o0]; prev[o0 + 1] = x[o0 + 1]; prev[o0 + 2] = x[o0 + 2];
            for (let k = 1; k < k1; k++) {
                const o = o0 + k * 3;
                const frei = k / (k1 - 1);
                const steif = werte.STEIF + (1 - werte.STEIF) * (1 - frei) * (1 - frei) * 0.5;   // an der Wurzel stärker am Ziel
                for (let c = 0; c < 3; c++) {
                    const v = x[o + c];
                    const next = v + (v - prev[o + c]) * tr + (c === 0 ? sx : c === 1 ? sy : sz) * frei + (ziel[o + c] - v) * steif;
                    prev[o + c] = v;
                    x[o + c] = next;
                }
            }
            for (let r = 0; r < werte.RUNDEN; r++) {                     // Gliedlängen von der Wurzel aus
                for (let k = 1; k < k1; k++) {
                    const a = o0 + (k - 1) * 3, b = o0 + k * 3;
                    const dx = x[b] - x[a], dy = x[b + 1] - x[a + 1], dz = x[b + 2] - x[a + 2];
                    const d = Math.hypot(dx, dy, dz) || 1e-9;
                    const f = laengen[s * k1 + k] / d;
                    x[b] = x[a] + dx * f; x[b + 1] = x[a + 1] + dy * f; x[b + 2] = x[a + 2] + dz * f;
                }
            }
        }
        const grenze = werte.GRENZE_M;
        const v = zustand.versatz;
        for (let i = 0; i < n; i += 3) {
            let dx = x[i] - ziel[i], dy = x[i + 1] - ziel[i + 1], dz = x[i + 2] - ziel[i + 2];
            const d = Math.hypot(dx, dy, dz);
            if (d > grenze) {
                const f = grenze / d;
                dx *= f; dy *= f; dz *= f;
                x[i] = ziel[i] + dx; x[i + 1] = ziel[i + 1] + dy; x[i + 2] = ziel[i + 2] + dz;
            }
            v[i] = dx; v[i + 1] = dy; v[i + 2] = dz;
        }
        return v;
    }

    /** Größte Auslenkung (m) — für Sichtproben. */
    static auslenkung(zustand) {
        let m = 0;
        const v = zustand.versatz;
        for (let i = 0; i < v.length; i += 3) m = Math.max(m, Math.hypot(v[i], v[i + 1], v[i + 2]));
        return m;
    }
}
