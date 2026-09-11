/**
 * Abspielende — wo das Abspielen endet, und was dann passiert.
 *
 * ANLASS (Edgar, 11.09.2026): „Mach einen Button «Endlos» mit dem das Video
 * von vorne abgespielt wird wenn die letzte Animation zu ende ist."
 *
 * Bis dahin sprang der Abspielkopf IMMER am Ende der PROJEKTDAUER auf 0 —
 * und die Projektdauer ist das Ende des längsten Clips über alle Spuren:
 * ein Modellclip ist mindestens 300 Bilder lang, eine Tonspur läuft nach
 * der letzten Bewegung oft minutenlang weiter. Die Figur stand dann still,
 * bis der Ton zu Ende war. Gemeint ist das Ende der letzten ANIMATION: der
 * späteste Clip auf einer Bewegungsspur. Ohne Bewegungsclips gilt die
 * Projektdauer (ein Projekt aus Kamera und Licht spielt sich auch ab).
 *
 * Ohne „Endlos" hält das Abspielen dort an (Pause am letzten Bild); mit
 * „Endlos" beginnt es von vorn. Ohne DOM, damit es in Node prüfbar ist.
 */
export class Abspielende {

    /** Das Bild, an dem die letzte Animation endet (oder die Projektdauer). */
    static bild(spuren, fps, dauerSekunden) {
        let ende = 0;
        for (const spur of spuren) {
            if (spur.type !== 'bvh') continue;
            for (const clip of spur.clips || []) {
                if (clip.endFrame > ende) ende = clip.endFrame;
            }
        }
        return ende > 0 ? ende : Math.round((dauerSekunden || 0) * fps);
    }

    /**
     * Der nächste Stand des Abspielkopfs.
     * @returns {{bild: number, anhalten: boolean}}
     */
    static naechstes(bild, ende, endlos) {
        if (ende <= 0) return { bild: 0, anhalten: false };   // leeres Projekt: bleibt bei 0
        if (bild < ende) return { bild, anhalten: false };
        return endlos ? { bild: 0, anhalten: false } : { bild: ende, anhalten: true };
    }

    /** Beim Start hinter dem Ende: von vorn, sonst hielte es sofort wieder an. */
    static startbild(bild, ende) {
        return (ende > 0 && bild >= ende) ? 0 : bild;
    }
}
