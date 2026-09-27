/**
 * Schnittfeld — ein Schnitt der Seite „Gesichtsform" als SVG: Tiefenprofil der Figur ohne (grau) und mit
 * Kopf-Eigen (blau), das Ziel (rot) zum Malen.
 *
 * Maß in Millimetern, 1 mm in beiden Richtungen gleich groß. Waagerecht (von oben): u = x' nach rechts,
 * vorn (z') nach oben. Senkrecht (von der Seite): vorn nach rechts, u = y' nach oben.
 * Malen: Ziehen zieht das Ziel unter dem Zeiger zu ihm hin, mit einer Gaußglocke der Pinselbreite
 * (`pinsel()` in mm) — so entsteht die Kurve entlang des Zeigerwegs. Mit Alt: löschen (keine Vorgabe).
 */
export class Schnittfeld {

    static RAND = 6;
    static NS = 'http://www.w3.org/2000/svg';

    constructor(eltern, profil, pinsel, beiAenderung) {
        this.art = profil.art;
        this.lage = profil.lage;
        this.u = profil.u;
        this.pinsel = pinsel;
        this.beiAenderung = beiAenderung;
        this.kasten = document.createElement('div');
        this.kasten.className = 'gf-feld';
        this.kopf = document.createElement('div');
        this.kopf.className = 'gf-feldkopf';
        this.svg = document.createElementNS(Schnittfeld.NS, 'svg');
        this.kasten.append(this.kopf, this.svg);
        eltern.appendChild(this.kasten);
        this.pfade = {};
        for (const art of ['ist', 'ergebnis', 'ziel']) {
            const p = document.createElementNS(Schnittfeld.NS, 'path');
            p.setAttribute('class', `gf-kurve ${art}`);
            this.svg.appendChild(p);
            this.pfade[art] = p;
        }
        this._ziehen();
    }

    /** `ist`, `ergebnis`, `ziel`: z je u (mm oder null), alle auf dem Raster `this.u`. */
    setzen(ist, ergebnis, ziel, guete) {
        this.ist = ist;
        this.ergebnis = ergebnis;
        this.zielwerte = ziel.slice();
        const text = guete ? ` · max ${guete.vorher_max ?? '–'} → ${guete.nachher_max ?? '–'} mm` : '';
        this.kopf.textContent = `${this.art === 'waagerecht' ? 'y′' : 'x′'} ${this._zahl(this.lage)} mm${text}`;
        this._rahmen();
        this.zeichnen();
    }

    ziel() {
        const z = this.zielwerte.map(v => (v === null ? null : +v.toFixed(2)));
        return { art: this.art, lage: this.lage, u: this.u, z };
    }

    // ------------------------------------------------------------ Zeichnen

    _zahl(x) { return (x >= 0 ? '+' : '') + x.toFixed(1).replace('.', ','); }

    /** (u, z) → SVG-Punkt. */
    _bild(u, z) { return this.art === 'waagerecht' ? [u, -z] : [z, -u]; }

    _rahmen() {
        const werte = [...this.ist, ...(this.ergebnis || []), ...this.zielwerte].filter(v => v !== null);
        const zmin = Math.min(...werte), zmax = Math.max(...werte);
        const umin = this.u[0], umax = this.u[this.u.length - 1], r = Schnittfeld.RAND;
        const [a, b] = this._bild(umin, zmax), [c, d] = this._bild(umax, zmin);
        const x0 = Math.min(a, c) - r, y0 = Math.min(b, d) - r;
        const w = Math.abs(c - a) + 2 * r, h = Math.abs(d - b) + 2 * r;
        this.svg.setAttribute('viewBox', `${x0} ${y0} ${w} ${h}`);
    }

    _pfad(werte) {
        let d = '', offen = false;
        werte.forEach((z, i) => {
            if (z === null || z === undefined) { offen = false; return; }
            const [x, y] = this._bild(this.u[i], z);
            d += `${offen ? 'L' : 'M'}${x.toFixed(2)} ${y.toFixed(2)} `;
            offen = true;
        });
        return d;
    }

    zeichnen() {
        this.pfade.ist.setAttribute('d', this._pfad(this.ist));
        this.pfade.ergebnis.setAttribute('d', this.ergebnis ? this._pfad(this.ergebnis) : '');
        this.pfade.ziel.setAttribute('d', this._pfad(this.zielwerte));
    }

    // -------------------------------------------------------------- Malen

    /** Zeiger → (u, z) in mm. */
    _ort(ereignis) {
        const umkehr = this.svg.getScreenCTM().inverse();
        const p = new DOMPoint(ereignis.clientX, ereignis.clientY).matrixTransform(umkehr);
        return this.art === 'waagerecht' ? [p.x, -p.y] : [-p.y, p.x];
    }

    _ziehen() {
        let aktiv = false;
        const malen = (ereignis) => {
            const [u0, z0] = this._ort(ereignis), r = Math.max(1, this.pinsel());
            this.u.forEach((u, i) => {
                const g = Math.exp(-(((u - u0) / r) ** 2));
                if (g < 0.02) return;
                if (ereignis.altKey) { if (g > 0.5) this.zielwerte[i] = null; return; }
                const jetzt = this.zielwerte[i] ?? this.ist[i];
                if (jetzt === null || jetzt === undefined) return;
                this.zielwerte[i] = jetzt + (z0 - jetzt) * g;
            });
            this.zeichnen();
        };
        this.svg.addEventListener('pointerdown', (e) => {
            aktiv = true;
            this.svg.setPointerCapture(e.pointerId);
            malen(e);
        });
        this.svg.addEventListener('pointermove', (e) => { if (aktiv) malen(e); });
        const ende = () => { if (aktiv) { aktiv = false; this.beiAenderung(); } };
        this.svg.addEventListener('pointerup', ende);
        this.svg.addEventListener('pointercancel', ende);
    }
}
