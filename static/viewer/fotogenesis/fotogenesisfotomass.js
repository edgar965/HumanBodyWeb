/**
 * Fotogenesisfotomass — wie hoch steht die Person im Foto von Feld 1? (27.10.2026, Edgar: „die Größen aller Figuren bitte gleich machen“): Zeilen mit Personenpixeln eines freigestellten
 * Fotos (Grund weiß oder durchsichtig) als Anteil der Bildhöhe. Daraus rechnet `Fotogenesisseite` den Rand der 3D-Felder (`Fotogenesiskamera.feldStellen`), sodass jede Figur so hoch steht
 * wie die Person im Foto.
 */
export class Fotogenesisfotomass {
    /** Gerechnet auf einer Verkleinerung dieser Höhe. */
    static HOEHE = 400;
    /** Ein Pixel gehört zur Person, wenn es nicht durchsichtig und in mindestens einem Kanal dunkler als GRUND ist. */
    static GRUND = 245;
    static _gemessen = new Map();

    /** @param {HTMLImageElement} bild geladen @returns {{oben: number, unten: number, links: number, rechts: number}|null} Anteile der Bildhöhe bzw. -breite */
    static anteil(bild) {
        if (Fotogenesisfotomass._gemessen.has(bild.src)) return Fotogenesisfotomass._gemessen.get(bild.src);
        const h = Fotogenesisfotomass.HOEHE, b = Math.max(1, Math.round(h * bild.naturalWidth / bild.naturalHeight));
        const c = Object.assign(document.createElement('canvas'), { width: b, height: h }).getContext('2d', { willReadFrequently: true });
        c.drawImage(bild, 0, 0, b, h);
        const d = c.getImageData(0, 0, b, h).data, g = Fotogenesisfotomass.GRUND;
        let oben = -1, unten = -1, links = b, rechts = 0;
        for (let y = 0; y < h; y++) {
            let n = 0;
            for (let x = 0; x < b; x++) {
                const i = 4 * (y * b + x);
                if (d[i + 3] > 16 && (d[i] < g || d[i + 1] < g || d[i + 2] < g)) {
                    n++;
                    links = Math.min(links, x);
                    rechts = Math.max(rechts, x + 1);
                }
            }
            if (n >= 2) {
                if (oben < 0) oben = y;
                unten = y + 1;
            }
        }
        const aus = oben < 0 ? null : { oben: oben / h, unten: unten / h, links: links / b, rechts: rechts / b };
        Fotogenesisfotomass._gemessen.set(bild.src, aus);
        return aus;
    }

    /** Höhe der Person in Feld 1 in Bildschirmpixeln (Bild mit object-fit: contain in `feld`) oder null. */
    static personPx(bild, feld) {
        const a = bild.naturalHeight ? Fotogenesisfotomass.anteil(bild) : null;
        if (!a) return null;
        const s = Math.min(feld.clientWidth / bild.naturalWidth, feld.clientHeight / bild.naturalHeight);
        return (a.unten - a.oben) * bild.naturalHeight * s;
    }
}
