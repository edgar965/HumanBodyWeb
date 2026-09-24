/**
 * Modellplatz — wo eine neue Figur im BVH Studio steht und welche Spur sie
 * trägt. Ohne DOM, ohne Three.js, ohne `state`: die Entscheidung allein,
 * damit sie in Node prüfbar ist (`test_js_modellplatz.py`).
 *
 * ANLASS (Edgar, 11.09.2026): „beim Hinzufügen eines Modells bitte den
 * gleichen Popup dialog wie bei /humanbody/scene/, wo ich das Modell und die
 * Position auswähle, default die gleichen Meter."
 *
 * Im Studio gehört die LAGE einer Figur zur Animationsspur (`position`,
 * `group`), das MODELL zur verknüpften Modellspur. „Ein Modell hinzufügen"
 * heißt deshalb: eine Animationsspur, die noch niemand trägt, bekommt die
 * Lage und eine Modellspur mit dem gewählten Modell — gibt es keine freie,
 * kommt eine neue Animationsspur dazu.
 *
 * Die Vorgabe der Lage ist die der Szene-Seite: `ABSTAND_M` rechts neben der
 * zuletzt angelegten Figur; ohne Figur der Ursprung.
 */
export class Modellplatz {

    /** Abstand zur Nachbarfigur in Metern — derselbe wie im Szene-Dialog. */
    static ABSTAND_M = 1.5;

    /**
     * Trägt die Animationsspur schon eine Figur? Ja, wenn sie geladen ist,
     * Clips hat oder eine Modellspur auf sie zeigt — eine Modellspur, deren
     * Figur noch lädt, zählt also mit, sonst stünde die nächste am selben Ort.
     */
    static besetzt(spur, spuren) {
        const stelle = spuren.indexOf(spur);
        return Boolean(spur.mesh) || (spur.clips || []).length > 0
            || spuren.some(s => s.type === 'model' && s._linkedAnimIdx === stelle);
    }

    /** Die Figur, an der sich eine neue ausrichtet: die zuletzt angelegte. */
    static vorbild(spuren) {
        let letzte = null;
        for (const spur of spuren) {
            if (spur.type === 'bvh' && Modellplatz.besetzt(spur, spuren)) letzte = spur;
        }
        return letzte;
    }

    /** Position X, die der Dialog vorschlägt. */
    static vorgabeX(spuren, abstand = Modellplatz.ABSTAND_M) {
        const vorbild = Modellplatz.vorbild(spuren);
        if (!vorbild) return 0;
        return Number(((vorbild.position?.[0] || 0) + abstand).toFixed(2));
    }

    /**
     * Die Animationsspur, die das neue Modell trägt: die gewählte, wenn sie
     * frei ist, sonst die erste freie; `null`, wenn keine frei ist.
     */
    static freieAnimation(spuren, gewaehlt = -1) {
        const frei = s => s && s.type === 'bvh' && !Modellplatz.besetzt(s, spuren);
        if (frei(spuren[gewaehlt])) return spuren[gewaehlt];
        return spuren.find(frei) || null;
    }
}
