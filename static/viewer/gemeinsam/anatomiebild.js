import { Anatomieproben } from './anatomieproben.js';
import { Anatomierahmen } from './anatomierahmen.js';

/**
 * Anatomiebild — aus der Zuordnung (Texel des Stücks → Stelle der Haut) die drei Karten des Stücks rechnen (11.10.2026, für `Anatomiebacken`).
 *
 * Rechnet auf Fenstern, die `Anatomiefenster` schon gelesen hat — ohne DOM und ohne Three.js, damit es im Worker läuft (`anatomiearbeiter.js`, 12.10.2026).
 *
 * Je belegtem Texel: Haut-UV aus dem Hautdreieck und den Schwerpunktgewichten; über die Fläche des Texels so viele Proben, wie es Texel der Haut
 * deckt (`_proben`, ein Raster, höchstens `PROBEN_MAX` je Richtung), und gemittelt:
 * - Farbe: im linearen Raum gemittelt, als sRGB zurück.
 * - Normalen: als Vektor gemittelt, dann vom Rahmen der Haut in den des Stücks umgerechnet (`Anatomierahmen`), normiert.
 * - Rauheit: die Bytes gemittelt.
 * Ein Hautdreieck ohne Karte (`fenster[g]` ist null): seine Texel bleiben leer.
 */
export class Anatomiebild {

    static TAKT_MS = 25;
    /** Höchstens so viele Proben je Richtung (ein Texel des Stücks kann viele Texel der Haut decken). */
    static PROBEN_MAX = 8;

    /**
     * Wie viele Proben je Richtung ein Texel braucht, das `texel` Texel der Haut deckt: Gemessen am Daz-Stück deckt ein Texel im Mittel 0,8–1,4 Texel der Haut
     * (4096²), aber oben, wo die Insel des Stücks im Atlas schmal ist, ein Vielfaches — mit festen 2 × 2 Proben standen dort Blöcke von der Größe eines Texels.
     */
    static _proben(texel) {
        return Math.max(1, Math.min(Anatomiebild.PROBEN_MAX, Math.ceil(texel * 0.9)));
    }

    /**
     * @param zu        Ergebnis von `Anatomiezuordnung.rechnen`
     * @param st        `Anatomiedreiecke` des Stücks (Rahmen aus der UV des Netzes)
     * @param ha        `Anatomiedreiecke` der Haut (nur die in Frage kommenden Dreiecke)
     * @param gruppe    `Uint8Array`: je Hautdreieck der Eintrag in `fenster`
     * @param fenster   `Anatomiefenster.lesen`: je Gruppe der Haut `{farbe, normal, rauh}` oder null
     * @param uvKarte   die UV des Stücks in Zeilen der Karte (Zeile = v · Höhe)
     * @param atmen     `async () => void` oder null (im Worker nicht nötig)
     * @returns `{farbe, normal, rauheit}` je `Uint8ClampedArray` (RGBA, `breite · hoehe`); `rauheit` null, wenn keine Gruppe eine Karte dafür hat
     */
    static async rechnen(zu, st, ha, gruppe, fenster, breite, hoehe, uvKarte, atmen = null) {
        const aus = { farbe: new Uint8ClampedArray(breite * hoehe * 4), normal: new Uint8ClampedArray(breite * hoehe * 4), rauheit: null };
        const je = fenster.map(() => []);
        for (let k = 0; k < zu.anzahl; k++) je[gruppe[zu.btri[k]]].push(k);
        const z = { zu, st, ha, breite, hoehe, uvKarte, aus, d1: new Float64Array(2), d2: new Float64Array(2), px: new Float64Array(4), c: new Float64Array(9) };
        let letzte = performance.now(), hatNormale = false;
        for (let g = 0; g < fenster.length; g++) {
            if (!je[g].length || !fenster[g]) continue;
            z.f = fenster[g];
            hatNormale = hatNormale || !!z.f.normal;
            if (z.f.rauh && !aus.rauheit) aus.rauheit = new Uint8ClampedArray(breite * hoehe * 4);
            for (let i = 0; i < je[g].length; i++) {
                Anatomiebild._texel(z, je[g][i]);
                if ((i & 255) === 255 && atmen && performance.now() - letzte > Anatomiebild.TAKT_MS) { await atmen(); letzte = performance.now(); }
            }
        }
        if (!hatNormale) aus.normal = null;
        return aus;
    }

    /** Ein Texel: Stelle, Proben, Rahmen. */
    static _texel(z, k) {
        const { zu, st, ha, f, aus, d1, d2, px, c } = z, t = zu.btri[k], s = zu.stri[k], e = ha.ecken, uv = ha.uv;
        const l2 = zu.l2[k], l3 = zu.l3[k], l1 = 1 - l2 - l3, a = 2 * e[3 * t], b = 2 * e[3 * t + 1], cc = 2 * e[3 * t + 2];
        const u0 = l1 * uv[a] + l2 * uv[b] + l3 * uv[cc], v0 = l1 * uv[a + 1] + l2 * uv[b + 1] + l3 * uv[cc + 1];
        const po = st.proPixel(s, z.breite, z.hoehe, z.uvKarte), pp = st.pixel;
        ha.uvAenderung(t, pp[po], pp[po + 1], pp[po + 2], d1);
        ha.uvAenderung(t, pp[po + 3], pp[po + 4], pp[po + 5], d2);
        const zx = Anatomiebild._proben(Math.hypot(d1[0] * f.farbe.breite, d1[1] * f.farbe.hoehe)), zy = Anatomiebild._proben(Math.hypot(d2[0] * f.farbe.breite, d2[1] * f.farbe.hoehe));
        let r = 0, g = 0, bl = 0, nx = 0, ny = 0, nz = 0, ra = 0, n = 0;
        for (let ix = 0; ix < zx; ix++) for (let iy = 0; iy < zy; iy++) {
            const ox = (ix + 0.5) / zx - 0.5, oy = (iy + 0.5) / zy - 0.5;
            const u = u0 + d1[0] * ox + d2[0] * oy, v = v0 + d1[1] * ox + d2[1] * oy;
            Anatomieproben.lesen(f.farbe, u, v, px);
            r += Anatomieproben.LINEAR[Math.round(px[0])]; g += Anatomieproben.LINEAR[Math.round(px[1])]; bl += Anatomieproben.LINEAR[Math.round(px[2])];
            if (f.normal) { Anatomieproben.lesen(f.normal, u, v, px); nx += px[0] / 127.5 - 1; ny += px[1] / 127.5 - 1; nz += px[2] / 127.5 - 1; }
            if (f.rauh) { Anatomieproben.lesen(f.rauh, u, v, px); ra += px[1]; }
            n++;
        }
        const o = 4 * zu.texel[k];
        aus.farbe[o] = Anatomieproben.kodieren(r / n); aus.farbe[o + 1] = Anatomieproben.kodieren(g / n); aus.farbe[o + 2] = Anatomieproben.kodieren(bl / n); aus.farbe[o + 3] = 255;
        Anatomiebild._normale(z, t, s, f.normal ? [nx / n, ny / n, nz / n] : [0, 0, 1], o, c);
        if (aus.rauheit) { const w = f.rauh ? ra / n : 255; aus.rauheit[o] = aus.rauheit[o + 1] = aus.rauheit[o + 2] = w; aus.rauheit[o + 3] = 255; }
    }

    /**
     * Der gemittelte Karteneintrag `v` vom Rahmen der Haut in den des Stücks, normiert und als Byte nach `normal[o …]`. Übertragen wird nur die
     * STÖRUNG (x, y: Poren, Falten), gedreht auf die Tangenten des Stücks; z bleibt. Die ganze Rechnung `M_stück⁻¹ · M_haut · v` trüge auch die Neigung
     * der Hautfläche gegen die des Stücks mit (in der Furche, wo das Stück tief liegt: bunte Ellipse in der Karte, Furche wie überbrückt beleuchtet).
     */
    static _normale(z, t, s, v, o, c) {
        const { st, ha, aus } = z;
        Anatomierahmen.mal(st.umkehr, st.umkehrung(s), ha.matrix, ha.rahmen(t), c);
        const x = c[0] * v[0] + c[1] * v[1], y = c[3] * v[0] + c[4] * v[1], w = v[2];
        const l = Math.hypot(x, y, w) || 1;
        aus.normal[o] = (x / l * 0.5 + 0.5) * 255; aus.normal[o + 1] = (y / l * 0.5 + 0.5) * 255; aus.normal[o + 2] = (w / l * 0.5 + 0.5) * 255; aus.normal[o + 3] = 255;
    }
}
