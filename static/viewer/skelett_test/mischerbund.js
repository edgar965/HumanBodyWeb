/**
 * Mischerbund — mehrere `AnimationMixer` als einer.
 *
 * Die Vergleichsseite spielt dieselbe Bewegung auf zwei getrennten Skeletten
 * (BVH-Original und retargetiertes DEF). Three.js kann einen Mischer nur an EINE
 * Wurzel hängen, also gibt es zwei — und die Bedienung (Zeitleiste, Stopp,
 * Bildschleife) soll davon nichts wissen.
 *
 * Vorher stand das als anonymes Objekt mit drei Methoden mitten im Ladecode.
 */
export class Mischerbund {

    constructor(mischer) {
        this._mixers = mischer;
    }

    update(dt) {
        for (const mischer of this._mixers) mischer.update(dt);
    }

    stopAllAction() {
        for (const mischer of this._mixers) mischer.stopAllAction();
    }

    setTime(zeit) {
        for (const mischer of this._mixers) mischer.setTime(zeit);
    }
}
