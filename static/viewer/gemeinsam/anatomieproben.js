/**
 * Anatomieproben — Texel aus gelesenen Fenstern der Karten der Haut mischen (11.10.2026, für `Anatomiebild`).
 *
 * Die Fenster liest `Anatomiefenster` (Canvas, nur Hauptfaden); `lesen` mischt bilinear daraus und kennt weder DOM noch Three.js — es läuft auch im
 * Worker (`anatomiearbeiter.js`).
 */
export class Anatomieproben {

    /** sRGB-Byte → linear. */
    static LINEAR = Float32Array.from({ length: 256 }, (_, i) => {
        const c = i / 255;
        return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    });

    /** linear → sRGB-Byte (0–255, gerundet). */
    static kodieren(l) {
        const c = l <= 0.0031308 ? 12.92 * l : 1.055 * Math.pow(l, 1 / 2.4) - 0.055;
        return Math.max(0, Math.min(255, Math.round(c * 255)));
    }

    /** Bilinear gemischt: RGBA (0–255, nicht gerundet) an der Stelle `(u, v)` nach `aus[o … o + 3]`; außerhalb des Fensters gilt der Rand. */
    static lesen(f, u, v, aus, o = 0) {
        const x = Math.min(f.b - 1, Math.max(0, u * f.breite - 0.5 - f.x0));
        const y = Math.min(f.h - 1, Math.max(0, (f.flip ? 1 - v : v) * f.hoehe - 0.5 - f.y0));
        const xi = Math.min(f.b - 2, Math.floor(x)), yi = Math.min(f.h - 2, Math.floor(y));
        const fx = f.b > 1 ? x - xi : 0, fy = f.h > 1 ? y - yi : 0;
        const nx = f.b > 1 ? 1 : 0, ny = f.h > 1 ? 1 : 0;
        const a = 4 * (Math.max(0, yi) * f.b + Math.max(0, xi)), b = a + 4 * nx, c = a + 4 * ny * f.b, d = c + 4 * nx;
        for (let k = 0; k < 4; k++) {
            aus[o + k] = (f.daten[a + k] * (1 - fx) + f.daten[b + k] * fx) * (1 - fy) + (f.daten[c + k] * (1 - fx) + f.daten[d + k] * fx) * fy;
        }
    }
}
