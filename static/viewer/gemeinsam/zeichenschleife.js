/**
 * Die Zeichenschleife einer Seite — Basisklasse.
 *
 * WARUM (Befund `doppelcode`, 27.08.2026): Diese acht Zeilen standen an VIER
 * Stellen wortgleich —
 *
 *     starten() {
 *         const takt = () => {
 *             requestAnimationFrame(takt);
 *             this.schritt();
 *         };
 *         requestAnimationFrame(takt);
 *         return this;
 *     }
 *
 * in `Studioschleife`, `Videoschleife`, `Szenenschleife` und `Bildschleife`.
 * Vier Kopien einer Schleife, die auf JEDER Seite bei 60 Bildern je Sekunde
 * läuft: Wer sie einmal ändert (Drosseln bei verstecktem Tab, Zählwerk,
 * Abbruch), muss es viermal tun — und die vierte vergisst man.
 *
 * Wer eine eigene Vorbereitung braucht, überschreibt `vorbereiten()`; wer die
 * Schleife anhalten will, ruft `anhalten()`.
 */
export class Zeichenschleife {
    constructor() {
        /** Kennung des laufenden Bildaufrufs — null, solange nichts läuft. */
        this._kennung = null;
    }

    /**
     * Startet die Schleife und gibt die Instanz zurück (Aufrufer verketten).
     * @returns {this}
     */
    starten() {
        this.vorbereiten();
        const takt = () => {
            this._kennung = requestAnimationFrame(takt);
            this.schritt();
        };
        this._kennung = requestAnimationFrame(takt);
        return this;
    }

    /** Hängt sich vor den ersten Takt — Vorgabe: nichts zu tun. */
    vorbereiten() {}

    /** Ein Bild. Muss die Unterklasse liefern. */
    schritt() {
        throw new Error('Zeichenschleife.schritt() muss überschrieben werden');
    }

    /** Hält die Schleife an. Ein zweiter Aufruf schadet nicht. */
    anhalten() {
        if (this._kennung === null) return;
        cancelAnimationFrame(this._kennung);
        this._kennung = null;
    }

    /** Läuft sie gerade? */
    get laeuft() {
        return this._kennung !== null;
    }
}
