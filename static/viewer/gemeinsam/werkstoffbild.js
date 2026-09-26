/**
 * Werkstoffbild — die Bildkarte eines Werkstoff-Slots als PNG-Blob.
 *
 * WARUM EIGENES MODUL (26.09.2026): `ObjMtl` (OBJ-Export) und der
 * Collada-Schreiber (DAE-Export) brauchen GENAU dasselbe: aus
 * `material.map.image` (ein `<img>`/`<canvas>`/`ImageBitmap`, wie Three es
 * aus dem Server-Textur-Endpunkt lädt) eine PNG-Datei machen, die neben der
 * Exportdatei liegt. Zwei Kopien dieser sieben Zeilen wären die Fehlerklasse
 * „DIESELBEN LISTEN, ZWEIMAL" aus `kontextmenue.js` — hier als DIESELBE
 * FUNKTION, ZWEIMAL gerufen.
 */
export class Werkstoffbild {

    /**
     * Das Bild als PNG-Blob — oder `null`, wenn es keins gibt oder fehlschlägt.
     *
     * @param maxSeite  0 = Originalauflösung. Sonst wird die LÄNGERE Seite auf
     *                  höchstens `maxSeite` Pixel begrenzt (Seitenverhältnis
     *                  bleibt erhalten) — nur verkleinern, nie vergrößern.
     */
    static async png(image, maxSeite = 0) {
        if (!image) return null;
        const breite = image.width || image.videoWidth || image.naturalWidth || 0;
        const hoehe = image.height || image.videoHeight || image.naturalHeight || 0;
        if (!breite || !hoehe) return null;
        const faktor = maxSeite > 0 ? Math.min(1, maxSeite / Math.max(breite, hoehe)) : 1;
        const zielBreite = Math.max(1, Math.round(breite * faktor));
        const zielHoehe = Math.max(1, Math.round(hoehe * faktor));
        try {
            const canvas = document.createElement('canvas');
            canvas.width = zielBreite;
            canvas.height = zielHoehe;
            canvas.getContext('2d').drawImage(image, 0, 0, zielBreite, zielHoehe);
            return await new Promise((resolve, reject) => {
                canvas.toBlob(blob => (blob ? resolve(blob) : reject(new Error('toBlob leer'))), 'image/png');
            });
        } catch (fehler) {
            console.warn('Werkstoffbild: Bild nicht exportierbar', fehler);
            return null;
        }
    }
}
