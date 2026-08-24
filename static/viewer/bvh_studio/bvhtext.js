import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Bvhtext — eine BVH-Datei als Text lesen, einzelne Kanalwerte ersetzen und
 * wieder speichern.
 *
 * Aus werkzeug_boden.js herausgeloest (Umbau 16.08.2026): Die zweite Hälfte von
 * `groundFixSelectedClip()` (60 Zeilen) suchte den Yposition-Kanal im Kopf,
 * fand die Bewegungszeilen und ersetzte dort Werte. Das ist BVH-Handwerk und
 * hat mit "Boden richten" nichts zu tun — hier steht es für sich und ist
 * prüfbar.
 */
export class Bvhtext {

    /** Nachkommastellen, mit denen Werte zurückgeschrieben werden. */
    static STELLEN = 6;

    constructor(text) {
        this.zeilen = text.split('\n');
    }

    static async holen(kategorie, name) {
        const adresse = `/api/character/bvh/${encodeURIComponent(kategorie)}/`
                        + `${encodeURIComponent(name)}/`;
        return new Bvhtext(await Serverabruf.text(adresse));
    }

    /**
     * Nummer eines Kanals der Wurzel, etwa 'Yposition' — gezählt ab 0 über alle
     * Kanäle der Datei. Die CHANNELS-Zeile nennt zuerst die Anzahl, deshalb der
     * Versatz von 2.
     */
    kanal(name) {
        let inWurzel = false;
        for (const zeile of this.zeilen) {
            const text = zeile.trim();
            if (text.startsWith('ROOT ')) {
                inWurzel = true;
                continue;
            }
            if (!inWurzel || !text.startsWith('CHANNELS')) continue;
            const teile = text.split(/\s+/);
            for (let i = 2; i < teile.length; i++) {
                if (teile[i] === name) return i - 2;
            }
            return -1;
        }
        return -1;
    }

    /** Zeilennummern der Bewegungsdaten (alles nach MOTION, das mit Zahl beginnt). */
    bewegungszeilen() {
        const start = this.zeilen.findIndex(zeile => zeile.trim() === 'MOTION');
        if (start < 0) return [];
        const nummern = [];
        for (let i = start + 1; i < this.zeilen.length; i++) {
            if (/^[\d\-.]/.test(this.zeilen[i].trim())) nummern.push(i);
        }
        return nummern;
    }

    /**
     * Einen Kanal über alle Bilder neu setzen.
     * @param werte (bildnummer) => Zahl
     * @returns Anzahl geänderter Bilder
     */
    kanalSetzen(kanalnummer, anzahl, werte) {
        if (kanalnummer < 0) return 0;
        const zeilennummern = this.bewegungszeilen();
        const bis = Math.min(anzahl, zeilennummern.length);
        for (let bild = 0; bild < bis; bild++) {
            const nummer = zeilennummern[bild];
            const teile = this.zeilen[nummer].trim().split(/\s+/);
            teile[kanalnummer] = werte(bild).toFixed(Bvhtext.STELLEN);
            this.zeilen[nummer] = teile.join(' ');
        }
        return bis;
    }

    text() {
        return this.zeilen.join('\n');
    }

    /** true, wenn der Server die Datei angenommen hat. */
    async speichern(kategorie, name) {
        try {
            await Serverabruf.senden('/api/character/save-bvh-text/',
                                     { category: kategorie, name,
                                       bvh_text: this.text() });
            return true;
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', 'BVH nicht gespeichert:', fehler.message);
            return false;
        }
    }
}
