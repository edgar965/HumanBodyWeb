import { state } from './state.js';

/**
 * Glaettungszustand — der sitzungsweite Schalter der Gauß-Glättung.
 *
 * Herausgelöst aus `werkzeug_glaettung.js`, wo es ein Objektliteral auf
 * Modulebene war (`{active, sigma, origClips}`) und drei Funktionen daran
 * arbeiteten — Befund `klassenplan`: geteilter Zustand gehört in eine Klasse.
 *
 * WARUM DIE ROHWERTE GESICHERT WERDEN
 * ===================================
 * Die Glättung arbeitet IN den Werten der Animation. Ohne Sicherung ließe sie
 * sich nie zurücknehmen: Die Rohwerte kämen erst beim nächsten Laden wieder vom
 * Server. Gesichert wird je Clip (`<kategorie>/<name>`) und je Spur, weil ein
 * Clip mehrfach in der Zeitleiste liegen kann und dieselbe Animation teilt.
 *
 * ZWEIMAL GLÄTTEN IST NICHT ZWEIMAL GLATT
 * =======================================
 * Vor jedem Anwenden werden die Rohwerte zurückgeschrieben. Sonst faltet der
 * zweite Lauf über das Ergebnis des ersten — die Bewegung wird mit jedem
 * Reglerzug weiter verschliffen, und der Nutzer kann σ nicht mehr verkleinern.
 */
export class Glaettungszustand {

    constructor() {
        /** Ist die Glättung eingeschaltet? */
        this.active = false;
        /** Stärke (Standardabweichung in Bildern). */
        this.sigma = 2.0;
        /** `<kategorie>/<name>` -> `{spurname: Float32Array}` (Rohwerte). */
        this.origClips = new Map();
    }

    static schluessel(clip) {
        return `${clip.category}/${clip.name}`;
    }

    /** Rohwerte sichern, falls noch nicht gesichert. */
    sichern(clip) {
        const schluessel = Glaettungszustand.schluessel(clip);
        if (this.origClips.has(schluessel)) {
            return this.origClips.get(schluessel);
        }
        const sicherung = {};
        for (const spur of clip.animClip.tracks) {
            sicherung[spur.name] = new Float32Array(spur.values);
        }
        this.origClips.set(schluessel, sicherung);
        return sicherung;
    }

    /** Rohwerte zurückschreiben — `true`, wenn es welche gab. */
    zuruecksetzen(clip) {
        const sicherung = this.origClips.get(Glaettungszustand.schluessel(clip));
        if (!sicherung) return false;
        for (const spur of clip.animClip.tracks) {
            if (sicherung[spur.name]) spur.values.set(sicherung[spur.name]);
        }
        return true;
    }

    vergessen() {
        this.origClips.clear();
    }

    /** Alle Bewegungsclips des Projekts — die einzige Stelle, die das weiß. */
    static clips() {
        const gefunden = [];
        for (const spur of state.project.tracks) {
            if (spur.type !== 'bvh') continue;
            for (const clip of spur.clips) {
                if (clip.animClip) gefunden.push({ spur, clip });
            }
        }
        return gefunden;
    }

    /**
     * Mixer zurücksetzen, damit Three.js die neuen Werte nimmt.
     *
     * WICHTIG: `uncacheClip`. Der Mixer hält eine fertige Action mit den ALTEN
     * Werten; ohne das Verwerfen läuft die Wiedergabe unverändert weiter, und die
     * Glättung sieht wirkungslos aus.
     */
    static mixerLoesen(spur, clip) {
        if (spur.mixer) spur.mixer.uncacheClip(clip.animClip);
    }

    static spurZuruecksetzen(spur) {
        if (spur.mixer) spur.mixer.stopAllAction();
        spur._activeClip = null;
        spur._activeAction = null;
    }
}
