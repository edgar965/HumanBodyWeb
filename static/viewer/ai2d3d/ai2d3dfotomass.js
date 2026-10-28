/**
 * Ai2d3dfotomass — wie hoch steht die Person im Foto von Feld 1? (27.10.2026, Edgar: „die Größen aller Figuren bitte gleich machen“): Zeilen mit Personenpixeln eines freigestellten
 * Fotos (Grund weiß oder durchsichtig) als Anteil der Bildhöhe. Daraus rechnet `Ai2d3dseite` den Rand der 3D-Felder (`Ai2d3dkamera.feldStellen`), sodass jede Figur so hoch steht
 * wie die Person im Foto.
 */
export class Ai2d3dfotomass {
    /** Gerechnet auf einer Verkleinerung dieser Höhe. */
    static HOEHE = 400;
    /** Ein Pixel gehört zur Person, wenn es nicht durchsichtig und in mindestens einem Kanal dunkler als GRUND ist. */
    static GRUND = 245;
    static _gemessen = new Map();

    /** @param {HTMLImageElement} bild geladen @returns {{oben: number, unten: number}|null} Anteile der Bildhöhe */
    static anteil(bild) {
        if (Ai2d3dfotomass._gemessen.has(bild.src)) return Ai2d3dfotomass._gemessen.get(bild.src);
        const h = Ai2d3dfotomass.HOEHE, b = Math.max(1, Math.round(h * bild.naturalWidth / bild.naturalHeight));
        const c = Object.assign(document.createElement('canvas'), { width: b, height: h }).getContext('2d', { willReadFrequently: true });
        c.drawImage(bild, 0, 0, b, h);
        const d = c.getImageData(0, 0, b, h).data, g = Ai2d3dfotomass.GRUND;
        let oben = -1, unten = -1;
        for (let y = 0; y < h; y++) {
            let n = 0;
            for (let x = 0; x < b; x++) {
                const i = 4 * (y * b + x);
                if (d[i + 3] > 16 && (d[i] < g || d[i + 1] < g || d[i + 2] < g)) n++;
            }
            if (n >= 2) {
                if (oben < 0) oben = y;
                unten = y + 1;
            }
        }
        const aus = oben < 0 ? null : { oben: oben / h, unten: unten / h };
        Ai2d3dfotomass._gemessen.set(bild.src, aus);
        return aus;
    }

    /** Höhe der Person in Feld 1 in Bildschirmpixeln (Bild mit object-fit: contain in `feld`) oder null. */
    static personPx(bild, feld) {
        const a = bild.naturalHeight ? Ai2d3dfotomass.anteil(bild) : null;
        if (!a) return null;
        const s = Math.min(feld.clientWidth / bild.naturalWidth, feld.clientHeight / bild.naturalHeight);
        return (a.unten - a.oben) * bild.naturalHeight * s;
    }
}
