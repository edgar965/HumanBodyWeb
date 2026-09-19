/**
 * Proportionenansicht — je Ansicht eine Zeile: Vorher (Ziel, wie eingestellt) und Nachher (Modell).
 *
 * Edgar (19.09.2026): „alle Ansichten aus der zweiten Zeile in jeweils einer
 * Zeile einbringen. Vorher und nachher Bild. Die Zeilen vergrößerbar machen
 * (du merkst dir die Position des Schiebereglers). Dann in jedem Bild die
 * Körperproportionen zeigen."
 *
 * Die Bilder kommen aus `ergebnis.proportionen.ansichten` (orthografisch,
 * `Bildmodellproportionen`), die Maßlinien als Pixel dazu; hier werden sie als
 * SVG über das Bild gelegt (viewBox = Bildgröße, also skaliert alles mit).
 * Links das Ziel mit den Linien, wie Edgar sie im Popup eingestellt hat —
 * ändert er einen Wert, wird die Linie sofort um ihre Mitte auf die neue Länge
 * gebracht (`px_je_m`); das Bild selbst folgt nach „Neu berechnen". Rechts
 * das Modell mit den gemessenen Werten. Zeilenhöhe über den Schieber, gemerkt
 * in `localStorage` (`bildmodell.prop.hoehe`).
 *
 * Das Popup öffnet sich AM BILD (Edgar, 19.09.2026: „fehlt das Popup beim Bild,
 * wo ich die Maße angeben kann"): Klick auf eine Maßlinie springt im Popup zu
 * diesem Maß, Klick auf das Bild oder den Knopf „Maße …" in jedem Vorher-Bild
 * öffnet es ganz; die Linien fangen den Klick (`pointer-events` auf `g`).
 */
import { Proportionendialog } from './proportionendialog.js';

export class Proportionenansicht {

    static ANSICHTEN = { vorn: 'Vorderansicht', seite: 'Seitenansicht', hinten: 'Rückansicht', kopf: 'Kopf' };
    static MERKER = 'bildmodell.prop.hoehe';
    static HOEHE = { min: 160, max: 900, vorgabe: 320 };

    constructor(auftrag, katalog) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.feld = document.getElementById('proportionen');
        if (!this.feld) return;
        this.dialog = new Proportionendialog(auftrag, katalog, () => this.linienZeichnen());
        this._schieber();
        document.getElementById('proportionen-anpassen')?.addEventListener('click', () => this.dialog.oeffnen(this.daten()));
        this._stand = null;
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    daten() { return (this.auftrag.zustand.ergebnis || {}).proportionen || null; }

    /** Die eingestellten Werte (cm je Schlüssel) — gehen mit jedem Start als `optionen.proportionen`. */
    werte() { return this.dialog.werte(); }

    // ------------------------------------------------------------ Höhe

    _schieber() {
        const s = document.getElementById('proportionen-hoehe');
        if (!s) return;
        let gemerkt = null;
        try { gemerkt = Number(localStorage.getItem(Proportionenansicht.MERKER)); } catch (e) { gemerkt = null; }
        const h = Proportionenansicht.HOEHE;
        s.min = h.min; s.max = h.max;
        s.value = gemerkt && gemerkt >= h.min && gemerkt <= h.max ? gemerkt : h.vorgabe;
        this._hoeheSetzen(s.value);
        s.addEventListener('input', () => {
            this._hoeheSetzen(s.value);
            try { localStorage.setItem(Proportionenansicht.MERKER, String(s.value)); } catch (e) { /* ohne Merker */ }
        });
    }

    _hoeheSetzen(px) {
        this.feld.style.setProperty('--prop-hoehe', `${Number(px)}px`);
        const t = document.getElementById('proportionen-hoehe-wert');
        if (t) t.textContent = `${Number(px)} px`;
    }

    // ---------------------------------------------------------- Zeilen

    zeigen(z) {
        const p = (z.ergebnis || {}).proportionen;
        const stand = p ? JSON.stringify([z.updated_at, Object.keys(p.ansichten || {})]) : '';
        if (stand === this._stand) return;
        this._stand = stand;
        this.feld.innerHTML = '';
        const knopf = document.getElementById('proportionen-anpassen');
        if (knopf) knopf.disabled = !p;
        if (!p) return;
        for (const [ansicht, name] of Object.entries(Proportionenansicht.ANSICHTEN)) {
            const a = (p.ansichten || {})[ansicht];
            if (!a) continue;
            const zeile = document.createElement('div');
            zeile.className = 'bildmodell-propzeile';
            zeile.dataset.ansicht = ansicht;
            zeile.innerHTML = `<h4>${name}</h4>`;
            for (const [wer, titel] of [['ziel', 'Vorher — Ziel, wie eingestellt'], ['modell', 'Nachher — aus dem Modell']]) {
                const fig = document.createElement('figure');
                fig.className = 'bildmodell-propbild';
                fig.dataset.wer = wer;
                fig.style.aspectRatio = `${a.breite} / ${a.hoehe}`;
                const src = this.auftrag.dateiAdresse('ergebnis', a.bild[wer]) + `?t=${Date.now()}`;
                fig.innerHTML = `<img src="${src}" alt="${titel}"><svg viewBox="0 0 ${a.breite} ${a.hoehe}" class="bildmodell-proplinien"></svg>`
                    + `<figcaption>${titel}</figcaption>`
                    + (wer === 'ziel' ? '<button type="button" class="btn btn-secondary btn-sm bildmodell-propknopf" title="Proportionen einstellen">'
                        + '<i class="fas fa-ruler-combined"></i> Maße …</button>' : '');
                fig.title = wer === 'ziel' ? 'Klick auf eine Linie: dieses Maß einstellen' : titel;
                fig.addEventListener('click', e => this.amBild(e, wer));
                zeile.appendChild(fig);
            }
            this.feld.appendChild(zeile);
        }
        this.linienZeichnen();
    }

    /** Klick im Bild: auf einer Linie → das Maß im Popup, sonst das Popup. */
    amBild(e, wer) {
        const gruppe = e.target.closest ? e.target.closest('g[data-mass]') : null;
        const mass = gruppe ? gruppe.dataset.mass : null;
        if (wer !== 'ziel' && !mass) return;
        this.dialog.oeffnen(this.daten(), mass);
    }

    /** Linien neu zeichnen — beim Anzeigen und nach jeder Eingabe im Popup. */
    linienZeichnen() {
        const p = this.daten();
        if (!p) return;
        const eingaben = this.werte();
        for (const zeile of this.feld.querySelectorAll('.bildmodell-propzeile')) {
            const a = p.ansichten[zeile.dataset.ansicht];
            for (const fig of zeile.querySelectorAll('figure')) {
                const wer = fig.dataset.wer;
                const svg = fig.querySelector('svg');
                const linien = (a.linien || {})[wer] || {};
                const werte = wer === 'ziel' ? p.ziel : p.modell;
                svg.innerHTML = Object.entries(linien).map(([k, [von, bis]]) => {
                    let wert = werte[k];
                    let klasse = 'prop-linie';
                    let [a1, b1] = [von, bis];
                    if (wer === 'ziel' && eingaben[k] !== undefined && eingaben[k] !== null) {
                        // Wie eingestellt: dieselbe Richtung, Länge aus dem Wert, um die Mitte.
                        [a1, b1] = Proportionenansicht.strecken(von, bis, eingaben[k] / 100 * a.px_je_m[wer]);
                        wert = eingaben[k];
                        klasse += ' prop-eingestellt';
                    }
                    const name = (this.katalog.proportionen || []).find(m => m.schluessel === k)?.name || k;
                    // Beschriftung am rechten Ende, damit sich Schulter/Brust/Oberarm nicht überdecken.
                    const rechts = a1[0] >= b1[0] ? a1 : b1;
                    return `<g class="${klasse}" data-mass="${k}"><title>${name}: ${wert} cm</title>`
                        + `<line x1="${a1[0]}" y1="${a1[1]}" x2="${b1[0]}" y2="${b1[1]}"/>`
                        + `<text x="${rechts[0] + 5}" y="${rechts[1] + 5}">${name} ${wert}</text></g>`;
                }).join('');
            }
        }
    }

    /** Strecke gleicher Richtung und Mitte mit neuer Länge (px). */
    static strecken(von, bis, laenge) {
        const dx = bis[0] - von[0], dy = bis[1] - von[1];
        const alt = Math.hypot(dx, dy) || 1;
        const mx = (von[0] + bis[0]) / 2, my = (von[1] + bis[1]) / 2;
        const ex = dx / alt * laenge / 2, ey = dy / alt * laenge / 2;
        return [[mx - ex, my - ey], [mx + ex, my + ey]];
    }
}
