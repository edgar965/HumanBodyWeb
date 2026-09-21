/**
 * Freistellerpinsel — Striche und Klickpunkte auf dem Foto im Freisteller-Fenster (21.09.2026).
 *
 * Edgar: „Das Hintergrund entfernen feature könnte mehr automatische, halbautomatischen und
 * manuelle Möglichkeiten enthalten zur Korrektur?" Eine `<canvas>` liegt über dem Foto links;
 * je nach Werkzeug (`werkzeug`):
 *   pinsel-drin / pinsel-draussen   Striche — der Server setzt die Maske dort auf 1 / 0
 *                                   (`Bildmodellfreistellerkorrektur.striche`), zuletzt und immer
 *   punkt-drin / punkt-draussen     Klickpunkte für SAM (Modell `sam`): Person / Hintergrund
 *   (leer)                          nichts — nur ansehen
 * Alles in normierten Bildkoordinaten (0..1), damit es für Vorschau (720 px) und volle Größe
 * gleich gilt. `striche()`/`punkte()` liefern die Regler-Felder, `setzen()` nimmt gespeicherte
 * zurück, `rueckgaengig()` nimmt den letzten Strich oder Punkt. Nach jedem Strich meldet
 * `onAenderung` — der Freisteller holt dann die Vorschau.
 */
export class Freistellerpinsel {

    static FARBEN = { 'pinsel-drin': 'rgba(60,200,90,0.55)', 'pinsel-draussen': 'rgba(230,60,60,0.55)',
                      'punkt-drin': '#3cc85a', 'punkt-draussen': '#e63c3c' };
    /** Pinselbreite in BILDPIXELN: Regler 1–100 → 1 … 400 px, quadratisch (unten fein gestuft).
     *  Edgar (21.09.2026, Bild): „der Stift ist viel zu dick, auch wenn ich die geringste Größe wähle" —
     *  vorher war das Minimum 0,4 % der Bildbreite (8 px bei 2000 px). Gespeichert wird weiter der
     *  Anteil der Bildbreite (`breite`), damit Vorschau (720 px) und volle Größe gleich rechnen. */
    static BREITE_PX = (wert) => Math.round(1 + ((Math.max(1, Math.min(100, Number(wert) || 20)) - 1) / 99) ** 2 * 399);
    /** Längste Leinwandseite — die Leinwand hat die Auflösung des Bildes, damit ein 1-px-Strich 1 px ist. */
    static LEINWAND_MAX = 4096;

    constructor(leinwand, foto, onAenderung) {
        this.leinwand = leinwand;
        this.foto = foto;
        this.onAenderung = onAenderung;
        this.werkzeug = '';
        this.regler = 20;        // Reglerstellung; `breite` (Anteil) folgt daraus und aus der Bildbreite
        this._striche = [];
        this._punkte = [];
        this._folge = [];       // Reihenfolge für Rückgängig: 'strich' | 'punkt'
        this._zurueck = [];     // Zurückgenommenes, für Wiederholen: {art: 'strich'|'punkt', wert}
        this._aktiv = null;
        this._zeiger = null;    // Lage des Zeigers (normiert) für den Pinselkreis
        if (!leinwand) return;
        leinwand.addEventListener('pointerdown', e => this._anfang(e));
        leinwand.addEventListener('pointermove', e => this._weiter(e));
        leinwand.addEventListener('pointerup', e => this._ende(e));
        leinwand.addEventListener('pointerleave', e => { this._ende(e); this._zeiger = null; this.zeichnen(); });
        if (typeof ResizeObserver !== 'undefined') new ResizeObserver(() => this.passen()).observe(foto);
        foto.addEventListener('load', () => this.passen());
    }

    // ------------------------------------------------------------ Zustand

    striche() { return this._striche.map(s => ({ art: s.art, breite: s.breite, punkte: s.punkte })); }
    punkte() { return this._punkte.map(p => [p[0], p[1], p[2]]); }

    setzen(striche, punkte) {
        this._striche = (striche || []).filter(s => s && s.punkte && s.punkte.length).map(s => ({ ...s }));
        this._punkte = (punkte || []).filter(p => p && p.length >= 3).map(p => [Number(p[0]), Number(p[1]), Number(p[2]) ? 1 : 0]);
        this._folge = [...this._striche.map(() => 'strich'), ...this._punkte.map(() => 'punkt')];
        this._zurueck = [];
        this.zeichnen();
    }

    leeren() {
        // „Alle weg" ist selbst rückgängig zu machen: alles als EIN Schritt merken.
        if (!this.leer) this._zurueck.push({ art: 'alles', striche: this._striche, punkte: this._punkte, folge: this._folge });
        this._striche = []; this._punkte = []; this._folge = [];
        this.zeichnen();
        this.onAenderung?.();
    }

    rueckgaengig() {
        const letzte = this._folge.pop();
        if (letzte === 'strich') this._zurueck.push({ art: 'strich', wert: this._striche.pop() });
        else if (letzte === 'punkt') this._zurueck.push({ art: 'punkt', wert: this._punkte.pop() });
        else return;
        this.zeichnen();
        this.onAenderung?.();
    }

    wiederholen() {
        const z = this._zurueck.pop();
        if (!z) return;
        if (z.art === 'alles') { this._striche = z.striche; this._punkte = z.punkte; this._folge = z.folge; }
        else if (z.art === 'strich') { this._striche.push(z.wert); this._folge.push('strich'); }
        else { this._punkte.push(z.wert); this._folge.push('punkt'); }
        this.zeichnen();
        this.onAenderung?.();
    }

    get leer() { return !this._striche.length && !this._punkte.length; }
    get rueckgaengigMoeglich() { return this._folge.length > 0; }
    get wiederholenMoeglich() { return this._zurueck.length > 0; }

    // ------------------------------------------------------------ Zeigen

    /** Pinselbreite als Anteil der Bildbreite (so wird sie gespeichert und gerechnet). */
    get breite() { return Freistellerpinsel.BREITE_PX(this.regler) / (this.foto?.naturalWidth || 1000); }

    /** Leinwand deckungsgleich mit dem angezeigten Foto (das Foto ist `object-fit: contain`), in
     *  Bildauflösung (bis LEINWAND_MAX) — CSS skaliert sie auf die Anzeige, der Zoom vergrößert mit. */
    passen() {
        const f = this.foto;
        if (!f || !f.naturalWidth) return;
        const zb = f.clientWidth, zh = f.clientHeight;
        const s = Math.min(zb / f.naturalWidth, zh / f.naturalHeight);
        const b = Math.round(f.naturalWidth * s), h = Math.round(f.naturalHeight * s);
        const k = Math.min(1, Freistellerpinsel.LEINWAND_MAX / Math.max(f.naturalWidth, f.naturalHeight));
        this.leinwand.width = Math.round(f.naturalWidth * k);
        this.leinwand.height = Math.round(f.naturalHeight * k);
        this._jeCss = this.leinwand.width / Math.max(1, b);   // Leinwandpixel je CSS-Pixel
        this.leinwand.style.width = `${b}px`;
        this.leinwand.style.height = `${h}px`;
        this.leinwand.style.left = `${f.offsetLeft + Math.round((zb - b) / 2)}px`;
        this.leinwand.style.top = `${f.offsetTop + Math.round((zh - h) / 2)}px`;
        this.zeichnen();
    }

    zeichnen() {
        const c = this.leinwand, ctx = c.getContext('2d');
        ctx.clearRect(0, 0, c.width, c.height);
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        const je = this._jeCss || 1;   // Marken (Punkte, Pinselkreis) bleiben in CSS-Pixeln gleich groß
        for (const s of [...this._striche, ...(this._aktiv ? [this._aktiv] : [])]) {
            ctx.strokeStyle = Freistellerpinsel.FARBEN[`pinsel-${s.art}`];
            ctx.lineWidth = Math.max(1, s.breite * c.width);   // Leinwand = Bildauflösung: so breit rechnet der Server
            ctx.beginPath();
            s.punkte.forEach(([x, y], i) => { if (i) ctx.lineTo(x * c.width, y * c.height); else ctx.moveTo(x * c.width, y * c.height); });
            if (s.punkte.length === 1) ctx.lineTo(s.punkte[0][0] * c.width + 0.1, s.punkte[0][1] * c.height);
            ctx.stroke();
        }
        for (const [x, y, l] of this._punkte) {
            ctx.fillStyle = Freistellerpinsel.FARBEN[l ? 'punkt-drin' : 'punkt-draussen'];
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2 * je;
            ctx.beginPath();
            ctx.arc(x * c.width, y * c.height, 7 * je, 0, 2 * Math.PI);
            ctx.fill();
            ctx.stroke();
        }
        // Der Pinsel selbst: ein Kreis in Pinselbreite am Zeiger (Edgar, 21.09.2026: „die
        // Pinselgröße anpassbar" — man sieht, wie breit der nächste Strich wird).
        if (this._zeiger && this.werkzeug.startsWith('pinsel-')) {
            const [x, y] = this._zeiger;
            ctx.strokeStyle = this.werkzeug === 'pinsel-drin' ? '#3cc85a' : '#e63c3c';
            ctx.lineWidth = 1.5 * je;
            ctx.setLineDash([4 * je, 3 * je]);
            ctx.beginPath();
            ctx.arc(x * c.width, y * c.height, Math.max(0.5, this.breite * c.width / 2), 0, 2 * Math.PI);
            ctx.stroke();
            ctx.setLineDash([]);
        }
        c.style.cursor = this.werkzeug.startsWith('pinsel-') ? 'none' : this.werkzeug ? 'crosshair' : 'default';
        c.style.pointerEvents = this.werkzeug ? 'auto' : 'none';
    }

    /** Pinselbreite in Bildpixeln (voll aufgelöst) — für die Anzeige neben dem Regler. */
    breitePx() { return this.foto?.naturalWidth ? Freistellerpinsel.BREITE_PX(this.regler) : 0; }

    // ------------------------------------------------------------ Zeiger

    _lage(e) {
        const r = this.leinwand.getBoundingClientRect();
        return [Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)),
                Math.max(0, Math.min(1, (e.clientY - r.top) / r.height))];
    }

    _anfang(e) {
        if (!this.werkzeug || e.button !== 0 || e.ctrlKey) return;   // Strg + Ziehen schiebt das Bild (Zoom)
        e.preventDefault();
        const [x, y] = this._lage(e);
        this._zurueck = [];       // Neues nach einem Rückgängig: das Wiederholen verfällt
        if (this.werkzeug.startsWith('punkt-')) {
            this._punkte.push([x, y, this.werkzeug === 'punkt-drin' ? 1 : 0]);
            this._folge.push('punkt');
            this.zeichnen();
            this.onAenderung?.();
            return;
        }
        this._aktiv = { art: this.werkzeug === 'pinsel-drin' ? 'drin' : 'draussen', breite: this.breite, punkte: [[x, y]] };
        try { this.leinwand.setPointerCapture(e.pointerId); } catch (_) { /* kein echter Zeiger */ }
        this.zeichnen();
    }

    _weiter(e) {
        const [x, y] = this._lage(e);
        this._zeiger = [x, y];
        if (!this._aktiv) { this.zeichnen(); return; }
        const letzter = this._aktiv.punkte[this._aktiv.punkte.length - 1];
        if (Math.hypot(x - letzter[0], y - letzter[1]) < 0.002) return;
        this._aktiv.punkte.push([x, y]);
        this.zeichnen();
    }

    _ende(e) {
        if (!this._aktiv) return;
        this._striche.push(this._aktiv);
        this._folge.push('strich');
        this._aktiv = null;
        try { this.leinwand.releasePointerCapture(e.pointerId); } catch (_) { /* kein echter Zeiger */ }
        this.zeichnen();
        this.onAenderung?.();
    }
}
