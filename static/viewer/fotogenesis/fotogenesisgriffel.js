/**
 * Fotogenesisgriffel — der Griffel zwischen Genesis-Ergebnis und Seitenleiste in Zeile 1 (19.11.2026, Edgar: „50% Genesis, 50% Leiste dafür der Breite“, „einstellbar die 50%, mach einen
 * Griffel“). Ziehen verschiebt die Grenze der beiden Spalten (20–80 %), Doppelklick stellt 50 % her. Die Spalten lesen `--fotogenesis-links`/`--fotogenesis-rechts`
 * (`fotogenesis.css`, `.fotogenesis-mit-leiste`); die 3D-Ansicht folgt über ihren ResizeObserver (`Meshgenesisansicht`). Der Anteil bleibt im Browser dieses Betrachters
 * (localStorage, nur Bequemlichkeit; ohne Speicher gilt 50 %).
 *
 *     Fotogenesisgriffel.binden(document.querySelector('.fotogenesis-mit-leiste'));
 */
export class Fotogenesisgriffel {
    static SCHLUESSEL = 'fotogenesis.leistenanteil';
    static VON = 0.2;
    static BIS = 0.8;

    static binden(raster) {
        const leiste = raster?.querySelector(':scope > .fotogenesis-seitenleiste');
        return leiste ? new Fotogenesisgriffel(raster, leiste) : null;
    }

    constructor(raster, leiste) {
        this.raster = raster;
        this.start = null;
        this.element = document.createElement('div');
        this.element.className = 'fotogenesis-griffel';
        this.element.setAttribute('role', 'separator');
        this.element.setAttribute('aria-orientation', 'vertical');
        this.element.dataset.tip = 'Ziehen: Breite von Genesis-Ergebnis und Leiste ändern · Doppelklick: halb und halb';
        leiste.prepend(this.element);
        this.setzen(this.gemerkt());
        this.element.addEventListener('pointerdown', e => this._anfassen(e));
        this.element.addEventListener('pointermove', e => this._ziehen(e));
        for (const art of ['pointerup', 'pointercancel']) this.element.addEventListener(art, e => this._loslassen(e));
        this.element.addEventListener('dblclick', () => { this.setzen(0.5); this.merken(); });
    }

    gemerkt() {
        try {
            const a = parseFloat(localStorage.getItem(Fotogenesisgriffel.SCHLUESSEL));
            return Number.isFinite(a) ? a : 0.5;
        } catch {
            return 0.5;
        }
    }

    merken() {
        try { localStorage.setItem(Fotogenesisgriffel.SCHLUESSEL, String(this.anteil)); } catch { /* ohne Speicher bleibt es bei dieser Seite */ }
    }

    /** Anteil der linken Spalte (Genesis-Ergebnis) an der Breite, begrenzt auf 20–80 %. */
    setzen(anteil) {
        this.anteil = Math.min(Fotogenesisgriffel.BIS, Math.max(Fotogenesisgriffel.VON, anteil));
        this.raster.style.setProperty('--fotogenesis-links', `${this.anteil.toFixed(4)}fr`);
        this.raster.style.setProperty('--fotogenesis-rechts', `${(1 - this.anteil).toFixed(4)}fr`);
        this.element.setAttribute('aria-valuenow', String(Math.round(100 * this.anteil)));
    }

    _anfassen(e) {
        if (e.button !== undefined && e.button !== 0) return;
        e.preventDefault();
        this.element.setPointerCapture?.(e.pointerId);
        this.start = this.raster.getBoundingClientRect();
        this.element.classList.add('fotogenesis-griffel-aktiv');
    }

    _ziehen(e) {
        if (!this.start) return;
        this.setzen((e.clientX - this.start.left) / this.start.width);
    }

    _loslassen(e) {
        if (!this.start) return;
        this.start = null;
        this.element.releasePointerCapture?.(e.pointerId);
        this.element.classList.remove('fotogenesis-griffel-aktiv');
        this.merken();
    }
}
