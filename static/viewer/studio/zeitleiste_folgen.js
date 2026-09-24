/**
 * Zeitleistenfolge — die Zeitleiste blättert beim Abspielen mit dem Abspielkopf.
 *
 * WARUM (Edgar, 13.09.2026: „bei Play soll die Zeitleiste die Timeline
 * mitziehen, im Moment ist der Playhead außerhalb des sichtbaren Bereichs"):
 * `timelineScrollX` änderte sich nur über Rad und Ziehen. Bei 100 px/s und
 * rund 1.300 px Sichtbreite lief der Kopf nach 13 s rechts aus dem Bild, und
 * die Leiste zeigte weiter den Anfang — bei einer Animation von 251 s die
 * meiste Zeit.
 *
 * Blättern statt Schieben: Verlässt der Kopf den sichtbaren Bereich, springt
 * der Ausschnitt so, dass der Kopf mit einem kleinen Rand links steht.
 * Dazwischen steht die Leiste — Klips lassen sich während der Wiedergabe
 * weiter anfassen, und wer von Hand wegblättert, wird erst beim nächsten
 * Verlassen zurückgeholt. Ohne Importe, damit der Test die Rechnung in Node
 * prüfen kann (`test_js_zeitleistenfolge`).
 */
export class Zeitleistenfolge {
    /** Rand links vom Kopf nach dem Blättern, in Pixeln. */
    static RAND = 24;

    /**
     * Die Verschiebung, die den Kopf sichtbar macht — oder `null`, wenn er es
     * schon ist (dann bleibt die Leiste, wo sie steht).
     * @param {number} kopfPx   Lage des Kopfes in Leistenpixeln, ohne Verschiebung
     * @param {number} scrollX  aktuelle Verschiebung
     * @param {number} sichtbar Breite des sichtbaren Bereichs rechts der Kopfspalte
     */
    static verschiebung(kopfPx, scrollX, sichtbar) {
        if (!(sichtbar > 0)) return null;
        const x = kopfPx - scrollX;
        if (x >= 0 && x < sichtbar) return null;
        return Math.max(0, kopfPx - Zeitleistenfolge.RAND);
    }

    /**
     * Zieht `zustand.timelineScrollX` nach, wenn der Kopf nicht zu sehen ist.
     * @returns {boolean} ob geblättert wurde
     */
    static nachziehen(zustand, sichtbar) {
        const kopfPx = (zustand.playheadFrame / zustand.project.fps) * zustand.timelineZoom;
        const neu = Zeitleistenfolge.verschiebung(kopfPx, zustand.timelineScrollX, sichtbar);
        if (neu === null) return false;
        zustand.timelineScrollX = neu;
        return true;
    }
}
