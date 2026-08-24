/**
 * Spielerdaten — 2D-Keypoints und Erkennungsmarken zum Video.
 *
 * Aus bvh_player.js herausgeloest (Umbau 16.08.2026): Dort standen zwei
 * gleichlautende `fetch(...).then(r => r.json()).then(...).catch(() => {})`
 * hintereinander und zwei Rechnungen "Fortschritt → Bildnummer", die sich nur
 * in der Laenge der Liste unterschieden.
 *
 * Beide Dateien sind ausdruecklich freiwillig: Fehlt eine, laeuft der Spieler
 * ohne Ueberlagerung weiter — deshalb wird ein Fehler nur vermerkt.
 */
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

export class Spielerdaten {
    constructor() {
        /** { frames: [...], joints: [...], connections: [...] } oder null. */
        this.keypoints = null;
        /** Wahrheitswert je Bild: wurde eine Person erkannt? */
        this.erkennung = null;
    }

    static async laden(keypointsUrl, erkennungUrl) {
        const daten = new Spielerdaten();
        const [kp, erk] = await Promise.all([
            Spielerdaten._holen(keypointsUrl),
            Spielerdaten._holen(erkennungUrl),
        ]);
        if (kp?.frames?.length) daten.keypoints = kp;
        if (erk?.length) daten.erkennung = erk;
        return daten;
    }

    static async _holen(url) {
        if (!url) return null;
        try {
            const antwort = await fetch(url);
            return antwort.ok ? await antwort.json() : null;
        } catch (e) {
            Protokoll.warnung('bvh_player', 'optionale Daten nicht geladen:', url);
            return null;
        }
    }

    get gelenke() {
        return this.keypoints?.joints || [];
    }

    get verbindungen() {
        return this.keypoints?.connections || [];
    }

    /** Nummer des Bildes, das zu diesem Fortschritt gehoert. */
    bildnummer(fortschritt) {
        const n = this.keypoints?.frames?.length || 0;
        if (n === 0) return -1;
        return Math.min(Math.floor(fortschritt * n), n - 1);
    }

    get bildzahl() {
        return this.keypoints?.frames?.length || 0;
    }

    /** Keypoints eines Bildes oder null. */
    bildZuFortschritt(fortschritt) {
        const i = this.bildnummer(fortschritt);
        return i < 0 ? null : this.keypoints.frames[i];
    }

    /** Wurde an dieser Stelle eine Person erkannt? Ohne Marken: ja. */
    erkanntBei(fortschritt) {
        if (!this.erkennung) return true;
        const i = Math.min(Math.floor(fortschritt * this.erkennung.length),
                           this.erkennung.length - 1);
        return !!this.erkennung[i];
    }
}
