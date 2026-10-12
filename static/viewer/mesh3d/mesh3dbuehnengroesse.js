/**
 * Mesh3dbuehnengroesse — Höhe UND Breite einer 3D-Ansicht einstellen (12.10.2026, Edgar: „die neue 3D View … auch einstellbar in Größe“; danach: „die 3D Views sind in der Höhe einstellbar,
 * nicht aber in der Breite, fixe“).
 *
 * Zwei Wege zu jeder Zahl: der Regler über der Ansicht und der Ziehgriff in ihrer unteren rechten Ecke (`resize: both` in `mesh3d.css`). Wer zieht, stellt den Regler nach (`ResizeObserver` auf der
 * Ansicht); wer den Regler stellt, setzt die Größe der Ansicht. Die Leinwand folgt in beiden Fällen von selbst — die Bühne beobachtet ihren Behälter.
 *
 * Die Breite ist anders als die Höhe KEINE feste Zahl, solange niemand sie angefasst hat: die Ansicht füllt dann die Karte (Stil `width: 100%`) und wächst mit dem Fenster. Erst ein Regler oder
 * Ziehgriff setzt eine Breite in Pixeln (`style.width`); reicht sie bis an den Rand der Karte, geht die Ansicht wieder auf „volle Breite“ zurück und vergisst die Zahl. Gemerkt wird nur, was jemand
 * gewählt hat — ein Fenster, das sich ändert, schreibt nichts.
 * Die Wahl bleibt im Browser (`localStorage`, nur eine Bequemlichkeit: ohne Speicher gilt die Vorgabe der Vorlage); geschrieben wird nur, wenn sich die Größe wirklich ändert.
 */
export class Mesh3dbuehnengroesse {
    /**
     * @param {HTMLElement} feld die Ansicht  @param {HTMLInputElement} regler Höhe  @param {HTMLElement} wert Anzeige neben dem Höhenregler  @param {string} schluessel Name der Höhe im Browserspeicher
     * @param {{regler: HTMLInputElement, wert: HTMLElement, schluessel: string}|null} breite dasselbe für die Breite (leer: nur die Höhe ist einstellbar)
     */
    constructor(feld, regler, wert, schluessel, breite = null) {
        this.feld = feld;
        this.regler = regler;
        this.wert = wert;
        this.schluessel = schluessel;
        this.breite = breite;
        const gemerkt = this._lesen(this.schluessel, this.min, this.max);
        if (gemerkt) this.feld.style.height = `${gemerkt}px`;
        this._zuletzt = this.feld.clientHeight;
        if (this.breite) {
            const b = this._lesen(this.breite.schluessel, this.minBreite, Infinity);
            if (b) this.feld.style.width = `${b}px`;
            this._zuletztBreite = this.feld.clientWidth;
            this.breite.regler.addEventListener('input', () => this._breiteSetzen(Number(this.breite.regler.value)));
        }
        this._anzeigen();
        this.regler.addEventListener('input', () => this._setzen(Number(this.regler.value)));
        // Der Ziehgriff ändert die Größe ohne unsere Regler: Anzeige nachstellen und die neue Größe merken.
        new ResizeObserver(() => this._anzeigen()).observe(this.feld);
    }

    get min() { return Number(this.regler.min) || 240; }

    get max() { return Number(this.regler.max) || 1600; }

    get minBreite() { return Number(this.breite?.regler.min) || 320; }

    /** So breit kann die Ansicht höchstens werden: die Karte, in der sie steht (ohne deren Rand). */
    get platz() {
        const eltern = this.feld.parentElement;
        if (!eltern) return this.feld.clientWidth;
        const stil = globalThis.getComputedStyle ? globalThis.getComputedStyle(eltern) : {};
        return eltern.clientWidth - (parseFloat(stil.paddingLeft) || 0) - (parseFloat(stil.paddingRight) || 0);
    }

    _setzen(hoehe) {
        this.feld.style.height = `${Math.min(this.max, Math.max(this.min, Math.round(hoehe)))}px`;
        this._anzeigen();
    }

    /** Reicht die Breite bis an den Rand der Karte, ist es die volle Breite: der Stil fällt weg, und die Ansicht wächst wieder mit dem Fenster. */
    _breiteSetzen(breite) {
        // Ein Regler mit Schrittweite 10 rastet höchstens bis auf 9 px an seinen Endwert ein (gemessen: 2030 von 2032) — „bis auf einen Schritt an den Rand“ zählt als der Rand.
        const schritt = Math.max(1, Number(this.breite.regler.step) || 1);
        const voll = Math.round(breite) >= this.platz - schritt;
        this.feld.style.width = voll ? '' : `${Math.max(this.minBreite, Math.round(breite))}px`;
        if (voll) this._schreiben(this.breite.schluessel, null);
        this._anzeigen();
    }

    /** Regler und Zahlen auf die wirkliche Größe stellen (ausgeblendet hat die Ansicht keine: dann bleibt alles, wie es ist). */
    _anzeigen() {
        const h = this.feld.clientHeight;
        if (!h) return;
        this.regler.value = String(Math.min(this.max, Math.max(this.min, h)));
        this.wert.textContent = `${h} px`;
        if (h !== this._zuletzt) {
            this._zuletzt = h;
            this._schreiben(this.schluessel, h);
        }
        if (this.breite) this._breiteAnzeigen();
    }

    _breiteAnzeigen() {
        const b = this.feld.clientWidth;
        if (!b) return;
        const platz = Math.max(this.platz, this.minBreite);
        // Gezogen bis an den Rand (oder das Fenster wurde schmaler als die gewählte Breite): zurück auf „volle Breite“, die Zahl fällt weg.
        if (this.feld.style.width && b >= platz - 1) {
            this.feld.style.width = '';
            this._schreiben(this.breite.schluessel, null);
        }
        this.breite.regler.max = String(Math.round(platz));
        this.breite.regler.value = String(Math.min(platz, Math.max(this.minBreite, b)));
        this.breite.wert.textContent = this.feld.style.width ? `${b} px` : `volle Breite (${b} px)`;
        if (b !== this._zuletztBreite) {
            this._zuletztBreite = b;
            // Nur eine gewählte Breite wird gemerkt; wächst die volle Breite mit dem Fenster, ist das keine Wahl.
            if (this.feld.style.width) this._schreiben(this.breite.schluessel, b);
        }
    }

    _lesen(schluessel, unten, oben) {
        try {
            const wert = Number(window.localStorage.getItem(schluessel));
            return wert >= unten && wert <= oben ? wert : 0;
        } catch (fehler) { return 0; }
    }

    /** `null` löscht den Eintrag. */
    _schreiben(schluessel, wert) {
        try {
            if (wert === null) window.localStorage.removeItem?.(schluessel);
            else window.localStorage.setItem(schluessel, String(wert));
        } catch (fehler) { /* Speicher gesperrt: beim nächsten Mal gilt die Vorgabe */ }
    }
}
