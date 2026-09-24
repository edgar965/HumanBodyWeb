/**
 * Bildmittel — die mittlere Farbe (linear) der BELEGTEN Texel eines Bildes.
 *
 * WARUM (24.09.2026, `Umfaerbung`, im Chrome gesehen): Das Mittel aus der
 * obersten Mip-Stufe schloss die leeren Flächen des UV-Atlas mit ein —
 * `AngieJeansMedBlue.png` ist zu großen Teilen durchsichtig/schwarz, das
 * Mittel viel zu dunkel, das Verhältnis Texel ÷ Mittel lief an den Deckel
 * und die umgefärbte Jeans stand fast weiß da. Gezählt werden deshalb nur
 * Texel mit Deckkraft über 0,5 und über dem Schwarz des Hintergrunds
 * (sRGB 12/255 — schwarzes Haar liegt bei 20–40); sind es keine, alle.
 *
 * Gemessen wird auf einer Verkleinerung (64 × 64), einmal je Bild; das
 * Ergebnis hängt an `textur.userData.bildmittel`. Die Rechnung selbst
 * (`ausPixeln`) ist rein und in Node prüfbar.
 */
export class Bildmittel {

    static SEITE = 64;
    static SCHWARZ = 12;

    /** `[r, g, b]` linear — oder null (Bild noch nicht da, kein Canvas). */
    static von(textur) {
        if (!textur?.image) return null;
        const merk = textur.userData?.bildmittel;
        if (merk && merk.bild === textur.image) return merk.farbe;
        const pixel = Bildmittel._pixel(textur.image);
        if (!pixel) return null;
        const farbe = Bildmittel.ausPixeln(pixel);
        textur.userData = textur.userData || {};
        textur.userData.bildmittel = { bild: textur.image, farbe };
        return farbe;
    }

    /** Das Mittel aus RGBA-Bytes (sRGB) — linear. */
    static ausPixeln(pixel) {
        const summe = [0, 0, 0], alle = [0, 0, 0];
        let n = 0, nAlle = 0;
        for (let i = 0; i + 3 < pixel.length; i += 4) {
            const lin = [Bildmittel.linear(pixel[i]), Bildmittel.linear(pixel[i + 1]),
                         Bildmittel.linear(pixel[i + 2])];
            for (let k = 0; k < 3; k++) alle[k] += lin[k];
            nAlle += 1;
            const belegt = pixel[i + 3] > 127
                && Math.max(pixel[i], pixel[i + 1], pixel[i + 2]) > Bildmittel.SCHWARZ;
            if (!belegt) continue;
            for (let k = 0; k < 3; k++) summe[k] += lin[k];
            n += 1;
        }
        if (n) return summe.map(s => s / n);
        return nAlle ? alle.map(s => s / nAlle) : [1, 1, 1];
    }

    static linear(byte) {
        const c = byte / 255;
        return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    }

    static _pixel(bild) {
        try {
            const s = Bildmittel.SEITE;
            const leinwand = typeof OffscreenCanvas === 'function'
                ? new OffscreenCanvas(s, s) : Object.assign(document.createElement('canvas'), { width: s, height: s });
            const ctx = leinwand.getContext('2d', { willReadFrequently: true });
            ctx.drawImage(bild, 0, 0, s, s);
            return ctx.getImageData(0, 0, s, s).data;
        } catch {
            return null;            // ohne Canvas (Node) oder fremde Herkunft: GPU-Mittel bleibt
        }
    }
}
