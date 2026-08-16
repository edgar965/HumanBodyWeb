/**
 * Metaregler — Alter, Masse, Muskeln, Größe.
 *
 * Diese vier Regler zeigen ihre eigene Einheit (Jahre, Kilogramm, Prozent,
 * Zentimeter), der Server rechnet aber mit -1..1 um die Mitte des Bereichs.
 *
 * Umbau 16.08.2026: Die Umrechnung
 * `halb ? (angezeigt - (min + max) / 2) / halb : 0`
 * stand an FÜNF Stellen ausgeschrieben — viewer/morphs.js (zweimal, einmal
 * beim Zurücksetzen), photo_to_3d/humanbody_morphs.js, scene/properties.js,
 * vergleich/vergleichsregler.js und in umgekehrter Richtung in
 * photo_to_3d/fotoanalyse.js. Dazu viermal derselbe Block, der min/max/default
 * aus `meta_sliders` in die vier Bedienelemente schreibt.
 */
export class Metaregler {

    /** Reihenfolge wie in den Vorlagen. */
    static NAMEN = ['age', 'mass', 'tone', 'height'];

    /** Angezeigter Wert → Serverwert -1..1. */
    static innen(angezeigt, min, max) {
        const halb = (max - min) / 2;
        return halb ? (angezeigt - (min + max) / 2) / halb : 0;
    }

    /** Serverwert -1..1 → angezeigter Wert in der Einheit des Reglers. */
    static aussen(innen, min, max) {
        return (min + max) / 2 + innen * ((max - min) / 2);
    }

    /** Serverwert aus der Stellung eines Reglers. */
    static ausRegler(regler, angezeigt = null) {
        return Metaregler.innen(
            angezeigt === null ? parseInt(regler.value, 10) : angezeigt,
            parseInt(regler.min, 10), parseInt(regler.max, 10));
    }

    /**
     * Die vier Regler der Seite verdrahten.
     *
     * @param grenzen    `meta_sliders` aus /api/character/morphs/
     * @param geaendert  (name, serverwert, regler) => void
     */
    static verdrahten(grenzen, geaendert) {
        for (const name of Metaregler.NAMEN) {
            const teile = Metaregler.elemente(name);
            if (!teile) continue;
            Metaregler.grenzenSetzen(teile, grenzen?.[name]);
            teile.regler.addEventListener('input', () => {
                teile.anzeige.textContent = teile.regler.value;
                geaendert(name, Metaregler.ausRegler(teile.regler), teile.regler);
            });
        }
    }

    /** Regler und Wertanzeige zu einem Namen, oder null. */
    static elemente(name) {
        const regler = document.getElementById(`meta-${name}`);
        if (!regler) return null;
        return { regler, anzeige: document.getElementById(`meta-${name}-val`) };
    }

    static grenzenSetzen(teile, grenze) {
        if (!grenze) return;
        teile.regler.min = grenze.min;
        teile.regler.max = grenze.max;
        teile.regler.value = grenze.default;
        if (teile.anzeige) teile.anzeige.textContent = grenze.default;
    }

    /** Alle vier auf ihren Vorgabewert — beim Zurücksetzen der Seite. */
    static zuruecksetzen(grenzen) {
        for (const name of Metaregler.NAMEN) {
            const teile = Metaregler.elemente(name);
            if (teile) Metaregler.grenzenSetzen(teile, grenzen?.[name]);
        }
    }

    /** Einen angezeigten Wert in einen Regler schreiben. */
    static setzen(name, angezeigt) {
        const teile = Metaregler.elemente(name);
        if (!teile) return false;
        teile.regler.value = angezeigt;
        if (teile.anzeige) teile.anzeige.textContent = angezeigt;
        return true;
    }
}
