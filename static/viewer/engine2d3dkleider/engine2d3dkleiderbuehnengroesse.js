/**
 * Engine2d3dKleiderbuehnengroesse — Breite und Höhe der Modellansicht (Bühne) per Griff einstellen, gemerkt für ALLE Aufträge.
 *
 * Edgar, 02.10.2026: „mach die Größe der Modell View anpassbar in Breite und Höhe, merke dir die Einstellungen für alle
 * Jobs". Der Griff sitzt unten rechts in der Bühne: Ziehen setzt die Breite der Bühnenspalte und die Höhe der Bühne,
 * Doppelklick stellt die Vorgabe der Seite wieder her (`meshfigur.css`). Die Leinwand zieht von selbst nach — die Bühne
 * beobachtet ihr Feld (`Meshfigurbuehne`, ResizeObserver). Gemerkt wird im Browser (`localStorage`), ein Schlüssel für
 * alle Aufträge; ohne Speicher (privates Fenster) gilt die Größe bis zum Neuladen.
 */
export class Engine2d3dKleiderbuehnengroesse {

    static SPEICHER = 'engine2d3dkleider.buehne.groesse';
    static MIN = { breite: 320, hoehe: 300 };

    constructor(feld = document.getElementById('buehne')) {
        this.feld = feld;
        this.spalte = feld?.closest('.meshfigur-buehnenspalte') || null;
        if (!this.feld || !this.spalte) {
            console.warn('[2D3D Kleider] Bühnengröße: Bühne oder Bühnenspalte fehlt — kein Griff');
            return;
        }
        this.griff = document.createElement('div');
        this.griff.className = 'engine2d3dkleider-buehnengriff';
        this.griff.title = 'Ziehen: Breite und Höhe der Ansicht (gilt für alle Aufträge) · Doppelklick: Vorgabe';
        this.feld.appendChild(this.griff);
        this.griff.addEventListener('pointerdown', ereignis => this._start(ereignis));
        this.griff.addEventListener('dblclick', () => this.zuruecksetzen());
        const gemerkt = Engine2d3dKleiderbuehnengroesse._lesen();
        if (gemerkt) this.setzen(gemerkt.breite, gemerkt.hoehe);
    }

    static _lesen() {
        try {
            const wert = JSON.parse(localStorage.getItem(Engine2d3dKleiderbuehnengroesse.SPEICHER) || 'null');
            return wert && Number(wert.breite) > 0 && Number(wert.hoehe) > 0 ? wert : null;
        } catch {
            return null;    // stumm gewollt: ohne Speicher gilt die Vorgabe der Seite
        }
    }

    _merken(wert) {
        try {
            if (wert) localStorage.setItem(Engine2d3dKleiderbuehnengroesse.SPEICHER, JSON.stringify(wert));
            else localStorage.removeItem(Engine2d3dKleiderbuehnengroesse.SPEICHER);
        } catch {
            /* stumm gewollt: nur Bequemlichkeit, die Größe gilt dann bis zum Neuladen */
        }
    }

    /** Breite der Spalte und Höhe der Bühne in px (nie unter `MIN`, nie breiter als der Hauptbereich). */
    setzen(breite, hoehe) {
        const platz = this.spalte.parentElement?.clientWidth || window.innerWidth;
        const b = Math.round(Math.min(Math.max(breite, Engine2d3dKleiderbuehnengroesse.MIN.breite), platz));
        const h = Math.round(Math.max(hoehe, Engine2d3dKleiderbuehnengroesse.MIN.hoehe));
        this.spalte.style.flex = `0 0 ${b}px`;
        this.spalte.style.maxWidth = '100%';
        this.feld.style.height = `${h}px`;
        this.feld.style.minHeight = '0';
        return { breite: b, hoehe: h };
    }

    zuruecksetzen() {
        this.spalte.style.flex = '';
        this.spalte.style.maxWidth = '';
        this.feld.style.height = '';
        this.feld.style.minHeight = '';
        this._merken(null);
    }

    _start(ereignis) {
        ereignis.preventDefault();
        ereignis.stopPropagation();          // die Bühne soll beim Ziehen am Griff nicht drehen
        const anfang = { x: ereignis.clientX, y: ereignis.clientY,
            breite: this.spalte.getBoundingClientRect().width, hoehe: this.feld.getBoundingClientRect().height };
        this.griff.setPointerCapture(ereignis.pointerId);
        let zuletzt = null;
        const ziehen = e => {
            zuletzt = this.setzen(anfang.breite + e.clientX - anfang.x, anfang.hoehe + e.clientY - anfang.y);
        };
        const ende = e => {
            this.griff.releasePointerCapture(e.pointerId);
            this.griff.removeEventListener('pointermove', ziehen);
            this.griff.removeEventListener('pointerup', ende);
            this.griff.removeEventListener('pointercancel', ende);
            if (zuletzt) this._merken(zuletzt);
        };
        this.griff.addEventListener('pointermove', ziehen);
        this.griff.addEventListener('pointerup', ende);
        this.griff.addEventListener('pointercancel', ende);
    }
}
