/**
 * Modellzustaendigkeit — welche Modellspur die Figur einer Animationsspur zu
 * einer Zeit bestimmt.
 *
 * WARUM (11.09.2026, Edgar: „bei Klick auf Play im BVH Studio verschwindet das
 * Modell"): Im Projekt TechnoDance hingen ZWEI Modellspuren an „Animation 1" —
 * „Modell 1" mit vier Clips und „Modell 2" ohne einen einzigen (beim Laden des
 * Projekts auf die erste BVH-Spur gelegt, siehe
 * `Projektwiederherstellung._modellspurenVerlinken`). Je Bild zeigte die erste
 * die Figur, die leere versteckte sie wieder und setzte `meshActive` zurück,
 * worauf die erste ihr Preset NEU lud: im Client-Log 39× `preset_load_start
 * Female1` binnen einer Minute, die Figur war fast nie zu sehen.
 *
 * Regel: Je Animationsspur bestimmt genau EINE Modellspur — die erste
 * verknüpfte, nicht stumme, die an dieser Stelle einen Clip hat; hat keine
 * einen, die erste verknüpfte (sie versteckt dann die Figur). Die Clips
 * mehrerer Modellspuren derselben Animation ergänzen sich damit, statt sich je
 * Bild zu überschreiben.
 *
 * Kein Import — damit der Test (`test_js_modellzustaendigkeit.py`) das Modul
 * ohne three.js in Node ausführen kann.
 */
export class Modellzustaendigkeit {

    /**
     * Die zuständige Modellspur oder null.
     * @param spuren  alle Spuren des Projekts (`state.project.tracks`)
     * @param stelle  Index der Animationsspur in `spuren`
     * @param zeit    Abspielzeit in Sekunden
     * @param fps     Bildrate des Projekts
     */
    static spur(spuren, stelle, zeit, fps) {
        const verknuepft = spuren.filter(
            s => s.type === 'model' && !s.muted && s._linkedAnimIdx === stelle);
        return verknuepft.find(s => Modellzustaendigkeit.preset(s, zeit, fps))
            || verknuepft[0] || null;
    }

    /** Das Preset des Modell-Clips, der `zeit` enthält — oder null. */
    static preset(spur, zeit, fps) {
        for (const clip of spur.clips || []) {
            if (clip.type !== 'model') continue;
            const beginn = clip.startFrame / fps;
            if (zeit >= beginn && zeit < beginn + clip.duration) {
                return clip.data?.preset || null;
            }
        }
        return null;
    }
}
