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
import { Effektespur } from './effektespur.js';

export class Abspielende {

    /**
     * Das Bild, an dem die letzte Animation endet (oder die Projektdauer).
     * Fuer eine Animationsspur mit verknuepfter Effekte-Spur zaehlt die
     * ANZEIGE-Stelle des letzten Clips, nicht seine unveraenderte
     * Inhalt-Stelle — sonst haelt das Abspielen mitten in einem gedehnten
     * Standbild/einer Zeitlupe an (Edgar, 21.09.2026, `effektebindung.js`).
     */
    static bild(spuren, fps, dauerSekunden) {
        let ende = 0;
        for (let i = 0; i < spuren.length; i++) {
            const spur = spuren[i];
            if (spur.type !== 'bvh') continue;
            const effekte = spuren.find(t => t.type === 'effekte' && t._linkedAnimIdx === i);
            const schluessel = effekte ? Effektespur.schluessel(effekte.clips) : [];
            for (const clip of spur.clips || []) {
                const bild = schluessel.length
                    ? Effektespur.anzeige(schluessel, clip.endFrame) : clip.endFrame;
                if (bild > ende) ende = bild;
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
