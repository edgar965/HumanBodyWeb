/**
 * Studiostand — ein Schnappschuss des BVH-Studios für Undo/Redo.
 *
 * WARUM EINE KLASSE (28.08.2026, Befunde `doppelcode` und
 * „Datensatz mit mehr als drei Feldern"): Dieses Objekt
 *
 *     { label, data, playheadFrame, selectedTrackIdx, selectedClipIdx }
 *
 * wurde in `undo.js` an DREI Stellen von Hand gebaut (`pushUndo`, `undo`,
 * `redo`) und an ZWEI Stellen wieder ausgepackt — jedes Mal dieselben fünf
 * Zeilen mit denselben `??`-Vorgaben.
 *
 * WAS DAS KOSTET, WENN EIN FELD DAZUKOMMT: Wer die Kameraposition mit
 * aufnehmen will, muss sie an drei Stellen einpacken und an zwei auspacken.
 * Vergisst er eine, ist der Schnappschuss unvollständig — und das merkt
 * niemand beim Speichern, sondern erst beim Zurücknehmen, wenn die Kamera
 * springt. Keine Ausnahme, kein Logeintrag.
 *
 * `-1` als Vorgabe für die Auswahl ist NICHT dasselbe wie `0`: Sie bedeutet
 * „nichts ausgewählt". Deshalb `??` und nicht `||` — Spur 0 ist eine gültige
 * Auswahl und würde von `||` verschluckt. Beim Abspielkopf ist `||` dagegen
 * richtig: Bild 0 und „kein Wert" sollen beide 0 ergeben.
 *
 * WARUM `state` UND `fn` ALS PARAMETER: Ohne sie hätte dieses Modul einen
 * Import auf `state.js`, und das zieht die ganze Three.js-Instanz der Seite
 * nach. Ein Test in Node käme dann nicht einmal bis zur ersten Zusicherung
 * (`Cannot find package 'three'`) — genau daran ist der erste Wurf
 * gescheitert. So ist die Klasse reine Datenhaltung und prüfbar.
 */
export class Studiostand {

    /**
     * @param label wofür der Schritt im Menü steht („Clip gelöscht")
     * @param data Projektdaten aus `fn.buildProjectData()`
     */
    constructor(label, data, playheadFrame, selectedTrackIdx, selectedClipIdx) {
        this.label = label;
        this.data = data;
        this.playheadFrame = playheadFrame;
        this.selectedTrackIdx = selectedTrackIdx;
        this.selectedClipIdx = selectedClipIdx;
    }

    /** Den JETZIGEN Stand aufnehmen. */
    static jetzt(label, state, fn) {
        return new Studiostand(label, fn.buildProjectData(),
                               state.playheadFrame, state.selectedTrackIdx,
                               state.selectedClipIdx);
    }

    /**
     * Diesen Stand wiederherstellen — Daten, Abspielkopf, Auswahl, Anzeige.
     *
     * Die vier `fn.*`-Aufrufe am Ende gehören dazu: Ohne sie stimmen die
     * Daten, aber die Zeitleiste zeigt noch den alten Stand.
     */
    async herstellen(state, fn) {
        await fn.restoreProjectData(this.data);
        state.playheadFrame = this.playheadFrame || 0;
        state.selectedTrackIdx = this.selectedTrackIdx ?? -1;
        state.selectedClipIdx = this.selectedClipIdx ?? -1;
        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updatePlaybackUI();
        fn.updateProperties();
    }
}
