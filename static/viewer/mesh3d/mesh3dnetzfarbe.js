/**
 * Mesh3dnetzfarbe — die Farbe jeder Fläche des gezeigten Netzes als CIE-Lab, für „Farbe im Umkreis“ (13.10.2026, „Netz bearbeiten“).
 *
 * Dieselbe Rechnung wie `Mesh3dnetzkatalog.farben` / `lab_von` auf dem Server: die Basisfarbtextur an der UV der Flächenmitte, sRGB → CIE-Lab (D65). Der Browser liest die Textur, die er zeigt (glTF-UV: Ursprung oben links,
 * `flipY` aus — der Server dreht v, weil trimesh es beim Laden dreht; es ist dasselbe Pixel). Ein Bild über `MAX_KANTE` wird beim Lesen verkleinert (der Lesepuffer einer 8192er-Textur hat 256 MB); der Unterschied zum Server liegt
 * dann im Pixel, nicht in der Farbe. Maßgeblich für das, was geschnitten wird, ist der Server.
 *
 * Gibt `null`, wenn das Netz weder Farbtextur noch Vertexfarben hat oder das Bild nicht lesbar ist (fremder Ursprung) — der Aufrufer sagt das dem Nutzer.
 */
export class Mesh3dnetzfarbe {
    static MAX_KANTE = 2048;

    /**
     * @param {THREE.Mesh} netz das Netz der Ansicht
     * @param {ArrayLike<number>|null} index0 der geladene Index (Flächen = index0.length / 3), ohne Index: Dreiecke nacheinander
     * @param {number} flaechen Zahl der Flächen
     * @returns {Float32Array|null} (flaechen × 3) L, a, b
     */
    static labfarben(netz, index0, flaechen) {
        const bild = netz.material?.map?.image;
        const uv = netz.geometry.attributes.uv;
        if (!bild || !uv) return Mesh3dnetzfarbe._vertexfarben(netz, index0, flaechen);
        const pixel = Mesh3dnetzfarbe._pixel(bild);
        if (!pixel) return null;
        const { daten, b, h } = pixel;
        const aus = new Float32Array(flaechen * 3);
        const rgb = [0, 0, 0];
        for (let f = 0; f < flaechen; f++) {
            let u = 0, v = 0;
            for (let k = 0; k < 3; k++) {
                const i = index0 ? index0[f * 3 + k] : f * 3 + k;
                u += uv.getX(i);
                v += uv.getY(i);
            }
            const x = Math.min(b - 1, Math.max(0, Math.floor((u / 3) * (b - 1))));
            const y = Math.min(h - 1, Math.max(0, Math.floor((v / 3) * (h - 1))));
            const p = (y * b + x) * 4;
            rgb[0] = daten[p]; rgb[1] = daten[p + 1]; rgb[2] = daten[p + 2];
            const [l, a, bb] = Mesh3dnetzfarbe.lab(rgb);
            aus[f * 3] = l; aus[f * 3 + 1] = a; aus[f * 3 + 2] = bb;
        }
        return aus;
    }

    /**
     * Ohne Textur die Farbe an den Ecken: das Mittel der drei Vertexfarben je Fläche (14.10.2026, Zauberer). Die Vorschau großer Netze (`Mesh3dnetzansicht`, über 15 MB) trägt die Farbe an den Punkten, nicht als Textur — der
     * Hover sagte dort „keine lesbare Farbtextur“, obwohl das Original eine hat. Die Werte gelten wie die Pixel der Textur als sRGB (0…1 → 0…255): so entstanden sie (Textur an den Punkten abgetastet, als Bytes geschrieben).
     * @returns {Float32Array|null} null, wenn es auch keine Vertexfarben gibt
     */
    static _vertexfarben(netz, index0, flaechen) {
        const farbe = netz.geometry.attributes.color;
        if (!farbe || farbe.itemSize < 3) return null;
        const aus = new Float32Array(flaechen * 3);
        const rgb = [0, 0, 0];
        for (let f = 0; f < flaechen; f++) {
            rgb[0] = rgb[1] = rgb[2] = 0;
            for (let k = 0; k < 3; k++) {
                const i = index0 ? index0[f * 3 + k] : f * 3 + k;
                rgb[0] += farbe.getX(i);
                rgb[1] += farbe.getY(i);
                rgb[2] += farbe.getZ(i);
            }
            const [l, a, b] = Mesh3dnetzfarbe.lab([rgb[0] / 3 * 255, rgb[1] / 3 * 255, rgb[2] / 3 * 255]);
            aus[f * 3] = l; aus[f * 3 + 1] = a; aus[f * 3 + 2] = b;
        }
        return aus;
    }

    /** sRGB (0…255) → [L, a, b] (CIE76, D65) — Zahlen wie `Mesh3dnetzkatalog.lab_von`. */
    static lab([r, g, b]) {
        const lin = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
        const [rl, gl, bl] = [lin(r), lin(g), lin(b)];
        const x = (rl * 0.4124 + gl * 0.3576 + bl * 0.1805) / 0.95047;
        const y = rl * 0.2126 + gl * 0.7152 + bl * 0.0722;
        const z = (rl * 0.0193 + gl * 0.1192 + bl * 0.9505) / 1.08883;
        const f = t => (t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116);
        return [116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))];
    }

    /** Der Abstand ΔE (CIE76) zweier Farben aus `labfarben`. */
    static abstand(lab, f, g) {
        return Math.hypot(lab[f * 3] - lab[g * 3], lab[f * 3 + 1] - lab[g * 3 + 1], lab[f * 3 + 2] - lab[g * 3 + 2]);
    }

    static _pixel(bild) {
        try {
            const w0 = bild.width, h0 = bild.height;
            if (!w0 || !h0) return null;
            const s = Math.min(1, Mesh3dnetzfarbe.MAX_KANTE / Math.max(w0, h0));
            const b = Math.max(1, Math.round(w0 * s)), h = Math.max(1, Math.round(h0 * s));
            const leinwand = document.createElement('canvas');
            leinwand.width = b;
            leinwand.height = h;
            const zeichner = leinwand.getContext('2d', { willReadFrequently: true });
            zeichner.drawImage(bild, 0, 0, b, h);
            return { daten: zeichner.getImageData(0, 0, b, h).data, b, h };
        } catch {
            return null;
        }
    }
}
