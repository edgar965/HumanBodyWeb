/**
 * Schluesselpaar — die zwei Keyframes um ein Bild herum.
 *
 * Herausgelöst aus `spur_anwenden.js` (288 Zeilen): Die Suche stand dort ZWEIMAL
 * buchstabengleich — einmal für die Kamera, einmal für das Licht. Beide Male
 * dieselben zehn Zeilen samt derselben Rückfall-Regel.
 *
 * DIE RÜCKFALL-REGEL
 * ==================
 * Steht der Abspielkopf vor dem ersten Keyframe, gilt der erste; steht er hinter
 * dem letzten, gilt der letzte. Ohne diesen Rückfall wäre die Kamera außerhalb
 * der Keyframes gar nicht gesetzt — sie behielte die Position vom letzten
 * Mausklick, und der Nutzer sieht beim Abspielen etwas anderes als beim Rendern.
 *
 * WANN NICHT INTERPOLIERT WIRD (`sprung`)
 * =======================================
 * * `fade === false` am VORHERIGEN Keyframe: ausdrücklich harter Wechsel.
 * * Beide Keyframes auf demselben Bild (das Paar am Schnitt): Zwischen zwei
 *   Werten am gleichen Bild gibt es keine Strecke, über die man mischen könnte.
 * * Nur ein Keyframe vorhanden.
 */
export class Schluesselpaar {

    /**
     * @param clips  Keyframes einer Spur, nach `startFrame` sortiert
     * @param bild   Bild des Abspielkopfs
     * @returns Schluesselpaar oder `null`, wenn es keine Keyframes gibt
     */
    static finden(clips, bild) {
        if (!clips || clips.length === 0) return null;
        let vorher = null;
        let nachher = null;
        for (const clip of clips) {
            if (clip.startFrame <= bild) vorher = clip;
            if (clip.startFrame >= bild && !nachher) nachher = clip;
        }
        if (!vorher && !nachher) return null;
        return new Schluesselpaar(vorher || nachher, nachher || vorher, bild);
    }

    constructor(vorher, nachher, bild) {
        this.vorher = vorher;
        this.nachher = nachher;
        this.bild = bild;
    }

    /** Kein Mischen — siehe Klassendoku. */
    get sprung() {
        return this.vorher === this.nachher
            || this.vorher.data.fade === false
            || this.vorher.startFrame === this.nachher.startFrame;
    }

    /** Anteil 0..1 zwischen den beiden Keyframes. */
    get anteil() {
        const strecke = this.nachher.startFrame - this.vorher.startFrame;
        if (strecke <= 0) return 0;
        return (this.bild - this.vorher.startFrame) / strecke;
    }

    /**
     * Anteil nach Interpolationsart des vorherigen Keyframes.
     *
     * `smooth` ist die Glättung `3t² − 2t³` (langsam an, langsam aus), `step`
     * bleibt auf dem vorherigen Wert, alles andere ist gerade.
     */
    get gewichtung() {
        const anteil = this.anteil;
        const art = this.vorher.data.interpolation || 'linear';
        if (art === 'smooth') return anteil * anteil * (3 - 2 * anteil);
        if (art === 'step') return 0;
        return anteil;
    }

    /** Ein Zahlenwert der beiden Keyframes, gemischt. */
    mischen(feld, gewicht = this.anteil) {
        const a = this.vorher.data[feld];
        const b = this.nachher.data[feld];
        if (a == null || b == null) return a ?? b ?? null;
        return a + (b - a) * gewicht;
    }
}
