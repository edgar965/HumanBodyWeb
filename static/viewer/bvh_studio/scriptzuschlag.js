import { Lebendigkeit } from './lebendigkeit.js';

/**
 * Scriptzuschlag — was die Script-Clips eines Modells an der Zeit beitragen.
 *
 * Edgar, 15.09.2026: „Animation mit normaler Animation, Mimik und Script."
 * Ein Script ist ein Clip auf der Script-Spur (eingerückt unter der
 * Modellspur): Solange der Abspielkopf in ihm steht, laufen seine
 * Lebendigkeits-Bausteine (`clip.data` = Blinzeln, Blick, Atmen, Variation,
 * Zucken, Schlucken, Saat) über der Mimik. Die Zeit zählt AB DEM CLIPANFANG —
 * ein verschobener Clip nimmt seine Blinzelfolge mit; nach einem Split setzt
 * die zweite Hälfte sie fort (`trimIn`).
 *
 * Ohne Importe außer `Lebendigkeit` — der Test rechnet in Node
 * (`test_js_scriptzuschlag`).
 */
export class Scriptzuschlag {

    /** Sichtbare Bilder eines Clips (Bewegung: `totalFrames − trimIn − trimOut`). */
    static bilder(clip) {
        return Math.max(0, (clip.totalFrames || 0) - (clip.trimIn || 0) - (clip.trimOut || 0));
    }

    /** Die Script-Clips, in denen `bild` liegt. */
    static aktive(clips, bild) {
        return (clips || []).filter(c => c.type === 'script'
            && bild >= c.startFrame && bild < c.startFrame + Scriptzuschlag.bilder(c));
    }

    /**
     * Zuschlag auf die Gewichte an `bild`: Summe über alle aktiven Clips.
     * @param pose  die Gewichte der Mimik an dieser Stelle (das Blinzeln setzt
     *              aus, wenn die Pose die Augen schließt)
     * @returns {{aktiv: boolean, zuschlag: Object}}
     */
    static gewichte(clips, bild, fps, pose = {}) {
        const zuschlag = {};
        const aktive = Scriptzuschlag.aktive(clips, bild);
        for (const clip of aktive) {
            const t = (bild - clip.startFrame + (clip.trimIn || 0)) / (fps || 30);
            for (const [einheit, g] of Object.entries(Lebendigkeit.zuschlag(clip.data, t, pose))) {
                zuschlag[einheit] = (zuschlag[einheit] || 0) + g;
            }
        }
        return { aktiv: aktive.length > 0, zuschlag };
    }
}
