import { Bildmittel } from './bildmittel.js';

/**
 * Anatomieton — welchen Farbton ein Netz an SEINEN Stellen zeigt (11.10.2026, für `Anatomiehaut`).
 *
 * WARUM nicht der Median der ganzen Karte (im Chrome gemessen, Ursula-Geograft auf Damira): Die Karte des Stücks ist ein UV-Atlas,
 * der zum größten Teil weißes Füllwerk ist — Median der Karte 251/251/251, das Stück selbst steht am Körper rosa da. Gezählt werden
 * deshalb nur die Texel an den UV der Punkte, die das Netz wirklich zeigt (bei der Haut: die Punkte rings um das Stück).
 *
 * Gelesen wird eine Verkleinerung (`SEITE` × `SEITE`) der Karte, einmal je Bild (`textur.userData.tonraster`). Die Bitmaps der Figur
 * kommen schon gewendet (`Genesis9texturen`, `flipY: false`): Zeile 0 ist v = 0.
 */
export class Anatomieton {

    static SEITE = 256;

    /** RGBA-Bytes der Karte auf `SEITE` × `SEITE` — null ohne Bild oder ohne Canvas. */
    static raster(textur) {
        if (!textur?.image) return null;
        const merk = textur.userData?.tonraster;
        if (merk && merk.bild === textur.image) return merk.pixel;
        const s = Anatomieton.SEITE;
        let pixel = null;
        try {
            const leinwand = typeof OffscreenCanvas === 'function'
                ? new OffscreenCanvas(s, s) : Object.assign(document.createElement('canvas'), { width: s, height: s });
            const ctx = leinwand.getContext('2d', { willReadFrequently: true });
            ctx.drawImage(textur.image, 0, 0, s, s);
            pixel = ctx.getImageData(0, 0, s, s).data;
        } catch {
            return null;
        }
        textur.userData = textur.userData || {};
        textur.userData.tonraster = { bild: textur.image, pixel };
        return pixel;
    }

    /** Die Texel der Karte an den Punkten `punkte` (Nummern in `uv`) mal `farbe`, linear: `[[r, g, b], …]`; Deckkraft ≤ 0,5 zählt nicht. */
    static proben(material, uv, punkte) {
        const f = material.color ? [material.color.r, material.color.g, material.color.b] : [1, 1, 1];
        if (!material.map) return [f];                       // einfache Farbe: ein Ton für alle Punkte
        const pixel = Anatomieton.raster(material.map);
        if (!pixel || !uv) return null;
        const s = Anatomieton.SEITE, aus = [];
        for (const i of punkte) {
            const u = uv.getX(i), v = uv.getY(i);
            const x = Math.min(s - 1, Math.floor((u - Math.floor(u)) * s));
            const y = Math.min(s - 1, Math.floor((v - Math.floor(v)) * s));
            const k = 4 * (y * s + x);
            if (pixel[k + 3] > 127) aus.push([0, 1, 2].map(c => Bildmittel.linear(pixel[k + c]) * f[c]));
        }
        return aus;
    }

    /** Der Median je Kanal (linear) — null ohne Proben. */
    static median(proben) {
        if (!proben?.length) return null;
        return [0, 1, 2].map(c => proben.map(p => p[c]).sort((a, b) => a - b)[Math.floor(proben.length / 2)]);
    }

    /** CIELAB (D65) einer linearen sRGB-Farbe: `[L, a, b]`. */
    static lab(lin) {
        const [r, g, b] = lin;
        const f = t => (t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116);
        const x = f((0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047);
        const y = f(0.2126 * r + 0.7152 * g + 0.0722 * b);
        const z = f((0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883);
        return [116 * y - 16, 500 * (x - y), 200 * (y - z)];
    }

    /** Farbabstand ΔE76 zweier linearer sRGB-Farben — um 2 gerade sichtbar, um 10 deutlich, ab 30 zwei verschiedene Farben. */
    static abstand(a, b) {
        const p = Anatomieton.lab(a), q = Anatomieton.lab(b);
        return Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
    }

    /** Alle Punktnummern einer Geometrie. */
    static alle(geo) {
        return Array.from({ length: geo.attributes.position.count }, (_, i) => i);
    }

    /** Der Kasten (min/max) der Punkte einer Geometrie, ringsum um `rand` (m) erweitert. */
    static kasten(geo, rand) {
        const p = geo.attributes.position;
        const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i < p.count; i++) {
            const w = [p.getX(i), p.getY(i), p.getZ(i)];
            for (let c = 0; c < 3; c++) { lo[c] = Math.min(lo[c], w[c]); hi[c] = Math.max(hi[c], w[c]); }
        }
        return { lo: lo.map(w => w - rand), hi: hi.map(w => w + rand) };
    }

    /** Die Punktnummern aus dem Indexbereich `gruppe` (`{start, count}`), die im Kasten liegen. */
    static nahe(geo, gruppe, kasten) {
        const p = geo.attributes.position, index = geo.index, aus = new Set();
        const lauf = index ? gruppe.count : p.count;
        for (let n = 0; n < lauf; n++) {
            const i = index ? index.getX(gruppe.start + n) : n;
            if (aus.has(i)) continue;
            const w = [p.getX(i), p.getY(i), p.getZ(i)];
            if (w.every((x, c) => x >= kasten.lo[c] && x <= kasten.hi[c])) aus.add(i);
        }
        return aus;
    }
}
