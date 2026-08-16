/**
 * Zoomfenster — zeigt die Projektionsvorschau bildschirmfüllend, mit Mausrad
 * zum Zoomen und Ziehen zum Verschieben.
 *
 * Aus photo_to_3d/alignment_preview.js herausgeloest (Umbau 16.08.2026):
 * `openPreviewDialog()` waren 95 Zeilen, davon 25 reines `Object.assign(
 * element.style, {...})` — vier Stilblöcke, die jetzt als CSS-Klassen im
 * Seitenkopf stehen (`.zoomfenster*`).
 *
 * Dabei behoben: Die Zuhörer für `mousemove` und `mouseup` wurden am `window`
 * angemeldet und NIE abgemeldet. Jedes Öffnen ließ ein Paar zurück; nach
 * zwanzig Blicken auf die Vorschau liefen zwanzig Paare mit, jedes mit einem
 * Verweis auf die alte Leinwand — der Speicher blieb belegt.
 */
export class Zoomfenster {

    static ID = 'preview-zoom-dialog';
    /** Anteil des Fensters, den das Bild höchstens einnimmt. */
    static BREITE_ANTEIL = 0.92;
    static HOEHE_ANTEIL = 0.90;
    /** Zoomschritte je Radrastung und die Grenzen. */
    static ZOOM_REIN = 1.15;
    static ZOOM_RAUS = 0.87;
    static ZOOM_MIN = 0.5;
    static ZOOM_MAX = 10;

    static zeigen(quelle) {
        return new Zoomfenster(quelle).oeffnen();
    }

    constructor(quelle) {
        this.quelle = quelle;
        this.zoom = 1;
        this.x = 0;
        this.y = 0;
        this.zieht = false;
        this.letzte = { x: 0, y: 0 };
        this.abmelden = [];
    }

    oeffnen() {
        document.getElementById(Zoomfenster.ID)?.remove();
        this.hintergrund = document.createElement('div');
        this.hintergrund.id = Zoomfenster.ID;
        this.hintergrund.className = 'zoomfenster';

        const rahmen = document.createElement('div');
        rahmen.className = 'zoomfenster-rahmen';
        rahmen.append(this._leinwand(), this._schliessknopf());
        this.hintergrund.appendChild(rahmen);

        // Klick auf den Hintergrund schließt, Klick auf das Bild nicht.
        this.hintergrund.addEventListener('click', ereignis => {
            if (ereignis.target === this.hintergrund) this.schliessen();
        });
        this._merken(window, 'keydown', ereignis => {
            if (ereignis.key === 'Escape') this.schliessen();
        });
        document.body.appendChild(this.hintergrund);
        this._lageSetzen();
        return this;
    }

    _leinwand() {
        const leinwand = document.createElement('canvas');
        leinwand.className = 'zoomfenster-bild';
        leinwand.width = this.quelle.width;
        leinwand.height = this.quelle.height;
        leinwand.getContext('2d').drawImage(this.quelle, 0, 0);

        // Anfangsgröße: einpassen, aber nie über die Originalgröße hinaus.
        const passt = Math.min(
            window.innerWidth * Zoomfenster.BREITE_ANTEIL / leinwand.width,
            window.innerHeight * Zoomfenster.HOEHE_ANTEIL / leinwand.height, 1);
        leinwand.style.width = Math.round(leinwand.width * passt) + 'px';
        leinwand.style.height = Math.round(leinwand.height * passt) + 'px';

        leinwand.addEventListener('wheel', ereignis => this._zoomen(ereignis),
                                  { passive: false });
        leinwand.addEventListener('mousedown', ereignis => {
            if (ereignis.button !== 0) return;
            this.zieht = true;
            this.letzte = { x: ereignis.clientX, y: ereignis.clientY };
            leinwand.classList.add('zieht');
        });
        this._merken(window, 'mousemove', ereignis => this._ziehen(ereignis));
        this._merken(window, 'mouseup', () => {
            this.zieht = false;
            leinwand.classList.remove('zieht');
        });
        this.leinwand = leinwand;
        return leinwand;
    }

    _schliessknopf() {
        const knopf = document.createElement('button');
        knopf.className = 'zoomfenster-zu';
        knopf.innerHTML = '&times;';
        knopf.addEventListener('click', () => this.schliessen());
        return knopf;
    }

    /** Zuhörer am Fenster mitschreiben, damit sie beim Schließen weggehen. */
    _merken(ziel, art, hoerer) {
        ziel.addEventListener(art, hoerer);
        this.abmelden.push(() => ziel.removeEventListener(art, hoerer));
    }

    _zoomen(ereignis) {
        ereignis.preventDefault();
        const kasten = this.leinwand.getBoundingClientRect();
        const mx = ereignis.clientX - kasten.left;
        const my = ereignis.clientY - kasten.top;
        const vorher = this.zoom;
        this.zoom = Math.max(Zoomfenster.ZOOM_MIN, Math.min(Zoomfenster.ZOOM_MAX,
            this.zoom * (ereignis.deltaY < 0 ? Zoomfenster.ZOOM_REIN
                                             : Zoomfenster.ZOOM_RAUS)));
        // Verschieben, damit der Punkt unter dem Zeiger stehen bleibt.
        this.x -= mx * (this.zoom - vorher);
        this.y -= my * (this.zoom - vorher);
        this._lageSetzen();
    }

    _ziehen(ereignis) {
        if (!this.zieht) return;
        this.x += ereignis.clientX - this.letzte.x;
        this.y += ereignis.clientY - this.letzte.y;
        this.letzte = { x: ereignis.clientX, y: ereignis.clientY };
        this._lageSetzen();
    }

    _lageSetzen() {
        this.leinwand.style.transform =
            `translate(${this.x}px, ${this.y}px) scale(${this.zoom})`;
    }

    schliessen() {
        for (const weg of this.abmelden) weg();
        this.abmelden = [];
        this.hintergrund.remove();
    }
}
