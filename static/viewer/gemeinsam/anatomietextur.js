/**
 * Anatomietextur — aus gerechneten Bytes eine Textur machen (12.10.2026, aus `Anatomiefuellung` herausgelöst, für `Anatomiebacken`).
 *
 * Braucht das DOM (Canvas) und bleibt deshalb auf dem Hauptfaden; die Bytes kommen aus `Anatomierechnung`, im Worker oder ohne ihn.
 */
export class Anatomietextur {

    /**
     * Eine Textur mit den Bytes `rgba` und den Einstellungen von `vorlage` (Farbraum, Umbruch, Filter, Mip-Kette). Eine EIGENE Quelle: ein Klon der
     * Vorlage teilte deren `Source`, und das Bild der Vorlage wäre überschrieben.
     */
    static aus(vorlage, rgba, breite, hoehe) {
        const leinwand = Object.assign(document.createElement('canvas'), { width: breite, height: hoehe });
        leinwand.getContext('2d').putImageData(new ImageData(rgba, breite, hoehe), 0, 0);
        return Anatomietextur._textur(vorlage, leinwand);
    }

    /** Dasselbe aus einem abgelegten Bild (`Anatomievorrat.holen`): auf eine Leinwand gleicher Größe, dann wie `aus`. */
    static ausBild(vorlage, bild, breite, hoehe) {
        const leinwand = Object.assign(document.createElement('canvas'), { width: breite, height: hoehe });
        leinwand.getContext('2d').drawImage(bild, 0, 0, breite, hoehe);
        bild.close?.();
        return Anatomietextur._textur(vorlage, leinwand);
    }

    static _textur(vorlage, leinwand) {
        // Eine Vorlage als S3TC-Block (`Texturweg`, Weg C, 19.10.2026): die Leinwand wird eine gewöhnliche Textur (die Elternklasse) und behält deren Mip-Kette —
        // ein Block hat `generateMipmaps = false`, die Leinwand hätte sonst keine Stufen bei einem Mip-Filter (schwarz).
        const block = !!vorlage.isCompressedTexture;
        const t = new (block ? Object.getPrototypeOf(vorlage.constructor) : vorlage.constructor)(leinwand);
        for (const name of ['colorSpace', 'flipY', 'wrapS', 'wrapT', 'minFilter', 'magFilter', 'anisotropy', 'generateMipmaps']) if (!block || !['minFilter', 'generateMipmaps'].includes(name)) t[name] = vorlage[name];
        t.needsUpdate = true;
        return t;
    }
}
