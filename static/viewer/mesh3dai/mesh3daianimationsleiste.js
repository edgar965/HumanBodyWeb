/**
 * Mesh3daianimationsleiste — die Animationsleiste EINER Zeile der Seite „Mesh3D-AI“ (14.10.2026): Play/Pause, Regler und Bildzähler (`.mesh3dai-animation` im Kopf der Zeile).
 * Edgar: „bei Taste / Klick auf Play in den einzelnen Zeilen möchte ich die animiert sehen“ — Standardanimation ist „Spagat“ (`Mesh3daianimationsdaten`). Jede Zeile spielt für sich; läuft mehr als eine, teilen sie
 * sich EINE Schleife (`requestAnimationFrame` läuft nur, solange mindestens eine Zeile spielt — die Felder zeichnen sonst nie von selbst).
 * Die Zeit bestimmt das Bild, nicht die Zahl der Takte: wird das Zeichnen langsamer als die Bildrate der Bewegung, werden Bilder übersprungen, die Bewegung läuft nicht in Zeitlupe.
 * Leertaste spielt/pausiert die Zeile, die gerade unter dem festen Block oben steht (`leertaste`). Eine neue Probe in der Probenwahl hält die Animation an (`Mesh3daizeile.probe`).
 */
import { Mesh3daianimationsdaten } from './mesh3daianimationsdaten.js';
import { Mesh3daianimationsflaechen } from './mesh3daianimationsflaechen.js';

export class Mesh3daianimationsleiste {
    /** Alle Leisten der Seite in der Reihenfolge der Zeilen (für die Leertaste). */
    static alle = [];
    static _spielende = new Set();
    static _lauf = 0;
    /** Abstand unter dem festen Block, an dem die „aktive“ Zeile für die Leertaste gesucht wird (px). */
    static LINIE_PX = 70;

    constructor(element, zeile) {
        this.zeile = zeile;
        this.play = element.querySelector('.mesh3dai-play');
        this.regler = element.querySelector('.mesh3dai-bildregler');
        this.zaehler = element.querySelector('.mesh3dai-bildzaehler');
        this.daten = null;
        this.bild = 0;
        this.spielt = false;
        this._t0 = 0;
        this._gezeichnet = -1;
        this._laedt = null;
        this.flaechen = null;
        this.flaechenFehler = null;
        this.play.addEventListener('click', () => this.umschalten());
        this.regler.addEventListener('input', () => this._gezogen());
        this._anzeige();
        Mesh3daianimationsleiste.alle.push(this);
    }

    // ------------------------------------------------------------------ Laden

    /** Die Bewegung holen (einmal je Job, von allen Zeilen geteilt); `null`, wenn die Zeile noch keine Antwort des Servers hat oder das Laden scheitert. */
    async _laden() {
        if (this.daten) return this.daten;
        const antwort = this.zeile.antwort;
        if (!antwort) return null;
        this._laedt ??= (async () => {
            this._text('lädt die Bewegung …');
            this.play.disabled = true;
            try {
                this.daten = await Mesh3daianimationsdaten.laden(antwort.job);
                // Echte Daten: die Flächen aller Bilder (ein Paket, rund 38 MB) kommen nach — bis dahin zeigen die Felder Rig und Text, danach die gehäutete Figur je Bild.
                if (this.daten.attrappe === false) this._flaechenHolen(antwort.job);
            } catch (fehler) {
                this._text(`Nicht geladen: ${fehler.message ?? fehler}`, true);
                return null;
            } finally {
                this.play.disabled = false;
                this._laedt = null;
            }
            this._anzeige();
            return this.daten;
        })();
        return this._laedt;
    }

    async _flaechenHolen(job) {
        try {
            this.flaechen = await Mesh3daianimationsflaechen.laden(job);
        } catch (fehler) {
            this.flaechenFehler = fehler.message ?? String(fehler);
            return;
        }
        if (this._gezeichnet >= 0 && this.daten) this.bildSetzen(this._gezeichnet);
    }

    // ------------------------------------------------------------------ Bedienung

    async umschalten() {
        if (this.spielt) {
            this.anhalten();
            return;
        }
        if (await this._laden()) this.starten();
    }

    starten() {
        const z = Mesh3daianimationsleiste;
        this.spielt = true;
        this._t0 = performance.now() - (this.bild / this.daten.fps) * 1000;
        z._spielende.add(this);
        this._knopf();
        if (!z._lauf) z._lauf = requestAnimationFrame(z._schleife);
    }

    anhalten() {
        this.spielt = false;
        Mesh3daianimationsleiste._spielende.delete(this);
        this._knopf();
    }

    /** Neue Probe oder neuer Job: anhalten und wieder auf Bild 1 — die Felder zeigen dann die Probe, nicht ein Bild der Bewegung. */
    zuruecksetzen(daten = false) {
        this.anhalten();
        if (daten) {
            this.daten = null;
            this.flaechen = null;
        }
        this.bild = 0;
        this._gezeichnet = -1;
        this._anzeige();
    }

    async _gezogen() {
        if (!(await this._laden())) return;
        const n = this.daten.bilder.length;
        const b = Math.round((Number(this.regler.value) / 1000) * (n - 1));
        if (this.spielt) this._t0 = performance.now() - (b / this.daten.fps) * 1000;
        this.bildSetzen(b);
    }

    // ------------------------------------------------------------------ Zeichnen

    /** Bild `b` (0-basiert) in die Felder der Zeile zeichnen. */
    bildSetzen(b) {
        const n = this.daten.bilder.length;
        this.bild = Math.max(0, Math.min(n - 1, b));
        this._gezeichnet = this.bild;
        const bild = this.daten.bilder[this.bild];
        // Das Bild-Objekt teilen sich alle Zeilen; die Fläche wird unmittelbar vor dem Zeichnen gesetzt (zwei Zeilen können verschiedene Bilder zeigen).
        if (this.flaechen) bild.flaeche = this.flaechen.bild(this.bild);
        else if (this.flaechenFehler) bild.flaecheFehlt = this.flaechenFehler;
        this.zeile.zeigenBild(bild);
        this._anzeige();
    }

    _takt(jetzt) {
        const n = this.daten.bilder.length;
        const b = Math.floor(((jetzt - this._t0) / 1000) * this.daten.fps) % n;
        if (b !== this._gezeichnet) this.bildSetzen(b);
    }

    /** Die gemeinsame Schleife aller spielenden Zeilen; endet von selbst, wenn keine mehr spielt. */
    static _schleife(jetzt) {
        const z = Mesh3daianimationsleiste;
        for (const leiste of [...z._spielende]) {
            try {
                leiste._takt(jetzt);
            } catch (fehler) {
                leiste.anhalten();
                leiste._text(`Fehler beim Zeichnen: ${fehler.message ?? fehler}`, true);
                console.error(fehler);
            }
        }
        z._lauf = z._spielende.size ? requestAnimationFrame(z._schleife) : 0;
    }

    // ------------------------------------------------------------------ Anzeige

    _knopf() {
        this.play.classList.toggle('active', this.spielt);
        this.play.replaceChildren(Object.assign(document.createElement('i'), { className: `fas ${this.spielt ? 'fa-pause' : 'fa-play'}` }), this.spielt ? ' Pause' : ' Play');
    }

    _text(text, fehler = false) {
        this.zaehler.textContent = text;
        this.zaehler.classList.toggle('fehlertext', fehler);
    }

    _anzeige() {
        this._knopf();
        const d = this.daten;
        if (!d) {
            this.regler.value = 0;
            this._text('Spagat — Play lädt die Bewegung');
            return;
        }
        const n = d.bilder.length;
        this.regler.value = n > 1 ? Math.round((this.bild / (n - 1)) * 1000) : 0;
        this._text(`${d.name} · Bild ${this.bild + 1} von ${n} · ${d.fps.toLocaleString('de-DE')} Bilder/s`);
    }

    // ------------------------------------------------------------------ Leertaste

    /**
     * Leertaste = Play/Pause der Zeile, die unter dem festen Block oben steht (die Zeile, deren Kasten die Linie `LINIE_PX` unter dem Block schneidet; sonst die nächste darunter).
     * Nicht in Eingabefeldern, Auswahllisten und auf Knöpfen — dort gehört die Leertaste dem Element.
     */
    static leertaste(ereignis) {
        const z = Mesh3daianimationsleiste;
        if (ereignis.code !== 'Space' || ereignis.repeat || ereignis.ctrlKey || ereignis.metaKey || ereignis.altKey) return;
        if (ereignis.target?.closest?.('input, select, textarea, button, a, [contenteditable]')) return;
        const css = getComputedStyle(document.documentElement);
        const oben = (parseFloat(css.getPropertyValue('--mesh3dai-leiste')) || 0) + (parseFloat(css.getPropertyValue('--mesh3dai-oben')) || 0);
        const linie = oben + z.LINIE_PX;
        const kaesten = z.alle.map(leiste => ({ leiste, r: leiste.zeile.element.getBoundingClientRect() }));
        const treffer = kaesten.find(k => k.r.top <= linie && k.r.bottom > linie) ?? kaesten.find(k => k.r.top > linie);
        if (!treffer) return;
        ereignis.preventDefault();
        treffer.leiste.umschalten();
    }
}
