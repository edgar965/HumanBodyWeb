/**
 * Bereichsgriff — ein Bereich (Seitenleiste, Feld) lässt sich am Rand ziehen.
 *
 * ANLASS (Edgar, 11.09.2026, Theatre): „möchte den rechten Bereich verschieben
 * können, die Griffe fehlen". Die Szene-Seite hatte den Griff als 30 Zeilen
 * Inline-Skript in ihrer Vorlage (`#panel-resize-handle`, nur für ein Feld
 * links); das Theatre hatte keinen. Hier ist derselbe Griff als Klasse, für
 * ein Feld links ODER rechts, mit gemerkter Breite.
 *
 * Was er tut: Ziehen setzt die Breite des Bereichs (innerhalb `min`/`max`),
 * Doppelklick stellt die Vorgabe wieder her, die Breite überlebt das Neuladen
 * (`localStorage`, wenn ein Schlüssel angegeben ist) und wird auf Wunsch als
 * CSS-Variable gesetzt — für Überlagerungen, die sich nach dem Bereich
 * richten (das Theatre-Studio hängt so an der rechten Leiste). Nach jeder
 * Änderung feuert `resize`, damit die Leinwand nachzieht.
 *
 * Verwendung:
 *
 *     new Bereichsgriff({ griff: el, bereich: feld, seite: 'links',
 *                         min: 240, max: 700, vorgabe: 300,
 *                         schluessel: 'theatre_panel_breite',
 *                         variable: '--theatre-panel-breite' }).verdrahten();
 *
 * `seite` sagt, an welchem Rand des Bereichs der Griff sitzt: `'rechts'`
 * (Bereich links im Fenster, wächst nach rechts) oder `'links'` (Bereich
 * rechts im Fenster, wächst nach links).
 */
export class Bereichsgriff {

    static AKTIV = 'aktiv';

    constructor({ griff, bereich, seite = 'rechts', min = 200, max = 600,
                  vorgabe = 300, schluessel = null, variable = null }) {
        this.griff = griff;
        this.bereich = bereich;
        this.richtung = seite === 'links' ? -1 : 1;
        this.min = min;
        this.max = max;
        this.vorgabe = vorgabe;
        this.schluessel = schluessel;
        this.variable = variable;
        this.breite = vorgabe;
        this._start = null;          // { x, breite } während des Ziehens
        this._bewegen = (e) => this._ziehen(e);
        this._loslassen = () => this._ende();
    }

    /** Hörer anhängen und die gemerkte Breite anwenden. */
    verdrahten() {
        if (!this.griff || !this.bereich) return this;
        this.setzen(this.gemerkt() ?? this.vorgabe, false);
        this.griff.addEventListener('mousedown', (e) => this._beginn(e));
        this.griff.addEventListener('dblclick', () => this.setzen(this.vorgabe));
        return this;
    }

    /** Breite setzen (begrenzt), anzeigen, merken. Liefert die Breite. */
    setzen(breite, merken = true) {
        this.breite = Bereichsgriff.begrenzen(breite, this.min, this.max);
        const px = `${this.breite}px`;
        this.bereich.style.width = px;
        if (this.variable) {
            document.documentElement.style.setProperty(this.variable, px);
        }
        if (merken) this._merken();
        window.dispatchEvent(new Event('resize'));
        return this.breite;
    }

    /** Die neue Breite aus Start und Mausweg — richtungsabhängig. */
    static naechsteBreite(startBreite, weg, richtung, min, max) {
        return Bereichsgriff.begrenzen(startBreite + richtung * weg, min, max);
    }

    static begrenzen(breite, min, max) {
        const zahl = Number(breite);
        if (!Number.isFinite(zahl)) return min;
        return Math.max(min, Math.min(max, Math.round(zahl)));
    }

    // -- Ziehen ---------------------------------------------------------------

    _beginn(e) {
        this._start = { x: e.clientX, breite: this.breite };
        this.griff.classList.add(Bereichsgriff.AKTIV);
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        document.addEventListener('mousemove', this._bewegen);
        document.addEventListener('mouseup', this._loslassen);
        e.preventDefault();
    }

    _ziehen(e) {
        if (!this._start) return;
        this.setzen(Bereichsgriff.naechsteBreite(
            this._start.breite, e.clientX - this._start.x,
            this.richtung, this.min, this.max), false);
    }

    _ende() {
        if (!this._start) return;
        this._start = null;
        this.griff.classList.remove(Bereichsgriff.AKTIV);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', this._bewegen);
        document.removeEventListener('mouseup', this._loslassen);
        this._merken();
    }

    // -- Gedächtnis -----------------------------------------------------------

    /** Die gemerkte Breite oder `null`; ein kaputter Wert gilt als keiner. */
    gemerkt() {
        if (!this.schluessel) return null;
        try {
            const wert = Number(localStorage.getItem(this.schluessel));
            return wert > 0 ? wert : null;
        } catch (fehler) {
            return null;               // privates Fenster, gesperrter Speicher
        }
    }

    _merken() {
        if (!this.schluessel) return;
        try {
            localStorage.setItem(this.schluessel, String(this.breite));
        } catch (fehler) {
            // stumm gewollt: Ohne Speicher gilt beim nächsten Laden die Vorgabe.
        }
    }
}
