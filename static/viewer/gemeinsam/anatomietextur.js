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
        const t = new vorlage.constructor(leinwand);
        for (const name of ['colorSpace', 'flipY', 'wrapS', 'wrapT', 'minFilter', 'magFilter', 'anisotropy', 'generateMipmaps']) t[name] = vorlage[name];
        t.needsUpdate = true;
        return t;
    }
}
