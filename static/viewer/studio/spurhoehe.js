import { TRACK_HEIGHT } from './state.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Spurhoehe — die Höhe EINER Zeitleistenspur, einzeln einstellbar und gemerkt.
 *
 * Edgar (24.09.2026, mit Bild): „mach die Höhe der Timelines veränderbar (alle
 * haben die gleiche Höhe, wenn ich die Höhe im ersten Balken ändere, ändern
 * sich alle), merke dir die Höhe". Bis dahin rechneten Zeichnen, Treffer,
 * Kopfspalte und Scrollen mit dem festen `TRACK_HEIGHT`.
 *
 * Gemerkt wird zweimal: am Spurobjekt (`spur.hoehe`, geht mit Projekt und
 * Sitzung — `Projektdaten._spur`) und im `localStorage` je Spurname. Das Zweite
 * gibt eine neue Spur gleichen Namens („Audio", „Animation 1") dieselbe Höhe,
 * auch in einem anderen Projekt. Gruppenzeilen bleiben bei `TRACK_HEIGHT`.
 */
export class Spurhoehe {
    static MIN = 24;
    static MAX = 240;
    static SCHLUESSEL = 'bvhStudio_spurhoehen_1';
    static _gemerkt = null;

    /** Höhe einer Spur in Pixeln. */
    static von(spur) {
        if (!spur) return TRACK_HEIGHT;
        const h = spur.hoehe ?? Spurhoehe._merkliste()[spur.name];
        return Number.isFinite(h) ? Spurhoehe._begrenzt(h) : TRACK_HEIGHT;
    }

    /** Höhe einer Anzeigereihe (`Reihen.liste()`). */
    static reihe(reihe, spuren) {
        return reihe.header ? TRACK_HEIGHT : Spurhoehe.von(spuren[reihe.trackIdx]);
    }

    /** Höhe setzen (begrenzt, ganze Pixel) und unter dem Spurnamen merken. */
    static setzen(spur, px) {
        const h = Spurhoehe._begrenzt(Math.round(px));
        spur.hoehe = h;
        const liste = Spurhoehe._merkliste();
        if (h === TRACK_HEIGHT) delete liste[spur.name];
        else liste[spur.name] = h;
        try {
            localStorage.setItem(Spurhoehe.SCHLUESSEL, JSON.stringify(liste));
        } catch (e) {
            Protokoll.debug('spurhoehe', 'Spurhöhe nicht merkbar', e);
        }
        return h;
    }

    static _begrenzt(h) {
        return Math.min(Spurhoehe.MAX, Math.max(Spurhoehe.MIN, h));
    }

    static _merkliste() {
        if (Spurhoehe._gemerkt) return Spurhoehe._gemerkt;
        let liste = {};
        try {
            liste = JSON.parse(localStorage.getItem(Spurhoehe.SCHLUESSEL) || '{}') || {};
        } catch (e) {
            Protokoll.debug('spurhoehe', 'gemerkte Spurhöhen unlesbar', e);
        }
        Spurhoehe._gemerkt = liste;
        return liste;
    }
}
