/**
 * Vorderansicht — Lage und Größe von Augen, Brauen, Nase und Lippen (Seite „Gesichtsform").
 *
 * Die Konturen der FaceLandmarker-Punkte im Gesichtsrahmen (x' nach rechts, y' nach oben, mm): Figur
 * ohne Kopf-Eigen grau, mit blau, Ziel rot mit ziehbaren Punkten. Ziehen verschiebt den Punkt, mit
 * Umschalt die ganze Kontur, mit Strg wird die Kontur um ihre Mitte größer (nach oben) oder kleiner.
 * Das Oval wird nur gezeigt — der Schnittmorph setzt es nicht (`G9schnittmorph.KONTUREN`), die
 * Gesichtsseiten formen die Schnitte. Dazu die Schnittlagen als Hilfslinien.
 */
export class Vorderansicht {

    static NS = 'http://www.w3.org/2000/svg';
    static RAND = 12;
    static NUR_ZEIGEN = new Set(['oval']);

    constructor(eltern, beiAenderung) {
        this.beiAenderung = beiAenderung;
        this.svg = document.createElementNS(Vorderansicht.NS, 'svg');
        eltern.appendChild(this.svg);
        this.zielpunkte = {};
        this._ziehen();
    }

    setzen(daten, ziel) {
        this.konturen = daten.konturen;
        this.ist = daten.ist.punkte;
        this.ergebnis = daten.ergebnis ? daten.ergebnis.punkte : null;
        this.lagen = daten.lagen;
        this.zielpunkte = {};
        const quelle = (ziel && ziel.punkte) || this.ergebnis || this.ist;
        for (const [nr, p] of Object.entries(quelle)) this.zielpunkte[nr] = p.slice();
        this._rahmen();
        this.zeichnen();
    }

    ziel() {
        return Object.fromEntries(Object.entries(this.zielpunkte).map(([k, p]) => [k, p.map(v => +v.toFixed(2))]));
    }

    zuruecksetzen() {
        const quelle = this.ergebnis || this.ist;
        this.zielpunkte = Object.fromEntries(Object.entries(quelle).map(([k, p]) => [k, p.slice()]));
        this.zeichnen();
    }

    // ------------------------------------------------------------ Zeichnen

    _rahmen() {
        const alle = Object.values(this.ist);
        const xs = alle.map(p => p[0]), ys = alle.map(p => -p[1]), r = Vorderansicht.RAND;
        this.box = [Math.min(...xs) - r, Math.min(...ys) - r, Math.max(...xs) - Math.min(...xs) + 2 * r,
            Math.max(...ys) - Math.min(...ys) + 2 * r];
        this.svg.setAttribute('viewBox', this.box.join(' '));
    }

    _linie(punkte, name, art) {
        const nr = this.konturen[name].filter(n => punkte[n]);
        if (nr.length < 2) return '';
        const d = nr.map((n, i) => `${i ? 'L' : 'M'}${punkte[n][0].toFixed(2)} ${(-punkte[n][1]).toFixed(2)}`)
            .join(' ');
        return `<path class="gf-kurve ${art}" d="${d}${name === 'nase' ? '' : ' Z'}"/>`;
    }

    zeichnen() {
        const [x0, y0, w, h] = this.box;
        let html = '';
        for (const y of this.lagen.waagerecht || []) {
            html += `<line class="gf-kurve hilfslinie" x1="${x0}" x2="${x0 + w}" y1="${-y}" y2="${-y}"/>`;
        }
        for (const x of this.lagen.senkrecht || []) {
            html += `<line class="gf-kurve hilfslinie" x1="${x}" x2="${x}" y1="${y0}" y2="${y0 + h}"/>`;
        }
        for (const name of Object.keys(this.konturen)) {
            html += this._linie(this.ist, name, 'ist');
            if (this.ergebnis) html += this._linie(this.ergebnis, name, 'ergebnis');
            html += this._linie(this.zielpunkte, name, 'ziel');
        }
        for (const name of Object.keys(this.konturen)) {
            const art = Vorderansicht.NUR_ZEIGEN.has(name) ? ' oval' : '';
            for (const n of this.konturen[name]) {
                const p = this.zielpunkte[n];
                if (!p) continue;
                html += `<circle class="gf-punkt${art}" r="0.9" cx="${p[0]}" cy="${-p[1]}" data-nr="${n}" `
                    + `data-kontur="${name}"/>`;
            }
        }
        this.svg.innerHTML = html;
    }

    // ------------------------------------------------------------- Ziehen

    _ort(e) {
        const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(this.svg.getScreenCTM().inverse());
        return [p.x, -p.y];
    }

    _ziehen() {
        let zug = null;
        this.svg.addEventListener('pointerdown', (e) => {
            const kreis = e.target.closest('circle.gf-punkt');
            if (!kreis || kreis.classList.contains('oval')) return;
            const name = kreis.dataset.kontur;
            const nummern = (e.shiftKey || e.ctrlKey) ? this.konturen[name].filter(n => this.zielpunkte[n])
                : [kreis.dataset.nr];
            const start = Object.fromEntries(nummern.map(n => [n, this.zielpunkte[n].slice()]));
            const pts = Object.values(start);
            const mitte = [0, 1].map(k => pts.reduce((s, p) => s + p[k], 0) / pts.length);
            zug = { start, mitte, ort: this._ort(e), skalieren: e.ctrlKey };
            this.svg.setPointerCapture(e.pointerId);
        });
        this.svg.addEventListener('pointermove', (e) => {
            if (!zug) return;
            const [x, y] = this._ort(e), dx = x - zug.ort[0], dy = y - zug.ort[1];
            const faktor = 1 + dy / 50;
            for (const [n, p] of Object.entries(zug.start)) {
                this.zielpunkte[n] = zug.skalieren
                    ? [zug.mitte[0] + (p[0] - zug.mitte[0]) * faktor, zug.mitte[1] + (p[1] - zug.mitte[1]) * faktor]
                    : [p[0] + dx, p[1] + dy];
            }
            this.zeichnen();
        });
        const ende = () => { if (zug) { zug = null; this.beiAenderung(); } };
        this.svg.addEventListener('pointerup', ende);
        this.svg.addEventListener('pointercancel', ende);
    }
}
