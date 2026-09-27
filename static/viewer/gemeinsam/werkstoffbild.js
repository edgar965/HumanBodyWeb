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
     * @param flipY     `texture.flipY` der Karte, aus der das Bild stammt.
     *                  `false` heißt: die Zeilen liegen schon andersherum —
     *                  siehe unten, dann wird beim Zeichnen gespiegelt.
     * @param farbe     `{r, g, b}` (0…1) wird in die Karte MULTIPLIZIERT.
     *                  Für Farbkarten gedacht, nie für Masken — warum, steht
     *                  unten bei `einfaerben`.
     * @param schwelle  `material.alphaTest` (0…1). Über null wird die Karte
     *                  daran HART geschnitten — siehe `schneiden`. Nur für
     *                  Deckkraftmasken.
     */
    static async png(image, maxSeite = 0, flipY = true, farbe = null, schwelle = 0) {
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
            const ctx = canvas.getContext('2d');
            // ZEILENRICHTUNG (FUND 26.09.2026, Edgar: „gleiche Fehler"):
            // Three lädt die Karten als `ImageBitmap` und setzt dafür
            // `texture.flipY = false` — das Bild liegt dann schon so im
            // Speicher, wie die Grafikkarte es braucht: Zeile 0 gehört zu
            // v = 0, also UNTEN. Eine Bilddatei neben einer `.obj` wird
            // andersherum gelesen: Zeile 0 ist oben, v = 1.
            //
            // Wer das Bild einfach abmalt, schreibt die Karte also auf den
            // Kopf. Im fremden Programm trifft dann jede Fläche die falsche
            // Texturzeile. Auf der Haut fällt das kaum auf — Haut auf Haut
            // sieht aus wie Haut; sichtbar wird es dort, wo die gespiegelte
            // Stelle NEBEN die UV-Insel fällt: helle Flecken an Hals, Knie
            // und Fingern. Gemessen an DamiraFein.obj: 133.552 von 1.514.592
            // Flächen trafen leeren Kartenrand, mit Spiegelung null.
            if (flipY === false) {
                ctx.translate(0, zielHoehe);
                ctx.scale(1, -1);
            }
            ctx.drawImage(image, 0, 0, zielBreite, zielHoehe);
            Werkstoffbild.einfaerben(ctx, farbe, zielBreite, zielHoehe);
            Werkstoffbild.schneiden(ctx, schwelle, zielBreite, zielHoehe);
            return await new Promise((resolve, reject) => {
                canvas.toBlob(blob => (blob ? resolve(blob) : reject(new Error('toBlob leer'))), 'image/png');
            });
        } catch (fehler) {
            console.warn('Werkstoffbild: Bild nicht exportierbar', fehler);
            return null;
        }
    }

    /**
     * Die Grundfarbe des Werkstoffs in die Karte multiplizieren.
     *
     * FUND 26.09.2026 (Edgar, nach dem Augenfix: die Brauen waren weiß):
     * Three rechnet `material.color` MAL `material.map` — die Brauenkarte ist
     * ein helles Graustufenbild, und erst die fast schwarze Grundfarbe
     * (0,0395 / 0,0232 / 0,0185) macht daraus dunkle Härchen. Blender und
     * MeshLab lesen eine `.mtl` anders: steht dort `map_Kd`, ERSETZT die
     * Karte das `Kd` — die Grundfarbe fällt unter den Tisch. Ergebnis:
     * schneeweiße Brauen und ein um ein Drittel zu helles Haar (dort
     * Kd 0,6444).
     *
     * Deshalb wird die Farbe hier in die Bilddatei gerechnet, und `ObjMtl`
     * schreibt dazu `Kd 1 1 1`. Dann kommt bei BEIDEN Lesarten dasselbe
     * heraus — beim Ersetzen ohnehin, beim Multiplizieren wegen der Eins.
     *
     * NUR FARBKARTEN: Eine Deckkraftmaske (`map_d`) einzufärben würde die
     * Maske verfälschen — sie ist kein Bild, sondern eine Zahl je Bildpunkt.
     */
    static einfaerben(ctx, farbe, breite, hoehe) {
        if (!farbe) return;
        const { r = 1, g = 1, b = 1 } = farbe;
        if (r === 1 && g === 1 && b === 1) return;
        const zahl = (wert) => Math.round(Math.min(1, Math.max(0, wert)) * 255);
        ctx.globalCompositeOperation = 'multiply';
        ctx.fillStyle = `rgb(${zahl(r)}, ${zahl(g)}, ${zahl(b)})`;
        ctx.fillRect(0, 0, breite, hoehe);
        ctx.globalCompositeOperation = 'source-over';
    }

    /**
     * Die Deckkraftmaske am `alphaTest` hart schneiden: ganz da oder ganz weg.
     *
     * FUND 26.09.2026 (Edgar mit Bild: die Haarsträhne über der Brust war ein
     * brauner Klecks): Three zeichnet Haarkarten mit `alphaTest` — eine Fläche
     * ist ENTWEDER voll da ODER gar nicht, und der Tiefenpuffer entscheidet,
     * welche Strähne vorn liegt. Ein `.obj`-Leser kennt keinen alphaTest; er
     * nimmt `map_d` als Deckkraft und MISCHT. Damit schimmern die schwach
     * maskierten Strähnenenden durch die vorderen hindurch — und weil die
     * Karte dort beige ausläuft, wurde aus der Strähne ein Klecks.
     *
     * Gegenprobe gerendert (Blender, Damira1): mit weicher Maske eine
     * zerfranste Strähne mit beigem Fleck, mit geschnittener eine volle
     * Strähne. Der Anteil sichtbarer Bildpunkte ändert sich dabei kaum
     * (Haarkarten 10,6 % und 14,3 % über der Schwelle).
     *
     * NUR MIT `alphaTest`: Ein Werkstoff, der wirklich mischen soll (ein
     * Schleier mit `transparent: true` und alphaTest 0), behält seine weiche
     * Maske — sonst verlöre er seine Durchsichtigkeit.
     */
    static schneiden(ctx, schwelle, breite, hoehe) {
        if (!schwelle || schwelle <= 0) return;
        const grenze = Math.round(Math.min(1, schwelle) * 255);
        const daten = ctx.getImageData(0, 0, breite, hoehe);
        const p = daten.data;
        for (let i = 0; i < p.length; i += 4) {
            const wert = p[i] >= grenze ? 255 : 0;
            p[i] = wert; p[i + 1] = wert; p[i + 2] = wert;
        }
        ctx.putImageData(daten, 0, 0);
    }
}
