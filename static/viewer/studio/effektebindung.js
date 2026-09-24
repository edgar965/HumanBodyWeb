import { state } from './state.js';
import { Effektespur } from './effektespur.js';

/**
 * Effektebindung — die Bruecke zwischen einer BVH-Spur und ihrer
 * verknuepften Effekte-Spur (`state`, darum getrennt von der reinen Rechnung
 * in `effektespur.js`).
 */
export class Effektebindung {
    /** Die Effekte-Spur, die BVH-Spur `bvhIdx` steuert — oder `null`. */
    static spurFuer(bvhIdx) {
        if (bvhIdx < 0) return null;
        return state.project.tracks.find(
            t => t.type === 'effekte' && t._linkedAnimIdx === bvhIdx) || null;
    }

    /**
     * Ihre Speed-Schluessel, sortiert — leer, wenn keine verknuepft ist ODER
     * die Effekte-Spur stummgeschaltet ist (Mute = „Effekt ignorieren", wie
     * bei jeder anderen Spur).
     */
    static schluessel(bvhIdx) {
        const spur = Effektebindung.spurFuer(bvhIdx);
        return (spur && !spur.muted) ? Effektespur.schluessel(spur.clips) : [];
    }

    /** Anzeige-Bild (Wanduhr) -> Inhalt-Bild der Spur `bvhIdx`. */
    static inhaltBild(bvhIdx, bildAnzeige) {
        const schluessel = Effektebindung.schluessel(bvhIdx);
        return schluessel.length ? Effektespur.inhalt(schluessel, bildAnzeige) : bildAnzeige;
    }

    /** Inhalt-Bild -> Anzeige-Bild (fuers Zeichnen/Treffen der BVH-Clips). */
    static anzeigeBild(bvhIdx, bildInhalt) {
        const schluessel = Effektebindung.schluessel(bvhIdx);
        return schluessel.length ? Effektespur.anzeige(schluessel, bildInhalt) : bildInhalt;
    }
}
