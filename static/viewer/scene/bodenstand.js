import { Koerpertiefe } from './koerpertiefe.js';

/**
 * Bodenstand — die animierte Figur mit ihrem tiefsten Punkt auf den Boden.
 *
 * WARUM (Edgar, 13.09.2026: „Animation immer auf Bodenniveau funktioniert
 * nicht, die Fußspitzen gehen noch in den Boden hinein"): Der Bodenfix in
 * `Szenenschleife.aufDenBoden` hatte drei Lücken —
 *
 * 1. Er nahm die GEWÄHLTE Figur (`fn._selectedInst`), nicht die ANIMIERTE
 *    (`state._animatedCharId`). Wer während der Wiedergabe Escape drückt
 *    oder eine zweite Figur anklickt, sah die Tänzerin versinken, während
 *    die stehende Figur um null verschoben wurde.
 * 2. Er lief nur bei `state.playing`. Der Zeitregler ruft `mixer.update(0)`
 *    bei angehaltener Wiedergabe — die Wurzel stand dann roh da, bis zum
 *    nächsten Play. Ebenso das Figurvideo (`videoaufnahme.js`), das die
 *    Bilder selbst stellt.
 * 3. Er kannte nur `rigifySkeleton`; SMPL- und MakeHuman-Figuren
 *    (`Eigenanimation`, Skelett in `inst.skelett`) bekamen keinen Fix.
 *
 * Gemessen wird `Koerpertiefe` — jeder Punkt des Netzes, nicht ein
 * Sohlenband und nicht ein Knochenkopf.
 */
export class Bodenstand {

    /**
     * Die animierte Figur so heben oder senken, dass ihr tiefster Punkt auf
     * y = 0 liegt. Liefert die Verschiebung (m), 0 wenn nichts zu tun war.
     *
     * @param {object} zustand   `state` der Seite
     * @param {object} v         Arbeitsvektor (Vector3), wiederverwendet
     */
    static richten(zustand, v) {
        const figur = Bodenstand.figur(zustand);
        const wurzel = Bodenstand.wurzel(zustand, figur);
        if (!wurzel) return 0;
        const tiefste = Koerpertiefe.tiefste(figur, wurzel, v);
        if (!isFinite(tiefste) || tiefste === 0) return 0;
        wurzel.position.y -= tiefste;
        return tiefste;
    }

    /** Die animierte Figur; ohne Kennung die gewählte (Einzelkörper-Weg). */
    static figur(zustand) {
        const kennung = zustand._animatedCharId || zustand.selectedCharacterId;
        return kennung ? zustand.characters.get(kennung) || null : null;
    }

    /**
     * Die Wurzel, die der Mixer stellt: das Skelett des Modells
     * (`inst.skelett` — bei HumanBody dasselbe Objekt wie `rigifySkeleton`,
     * bei UMA, SMPL und MakeHuman das eigene), sonst das der Seite.
     */
    static wurzel(zustand, figur) {
        const skelett = figur
            ? (figur.skelett || figur.rigifySkeleton)
            : zustand.rigifySkeleton;
        return skelett?.rootBone || null;
    }
}
