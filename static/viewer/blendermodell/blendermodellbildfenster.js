import { Dialoggroesse } from '../bildmodell/dialoggroesse.js';

/**
 * Blendermodellbildfenster — Bilder der Iterationen groß ansehen (Edgar, 29.09.2026: „Mach die Bilder vergrößerbar per
 * Popup-Klick bei Iterationen, damit ich mir die Unterschiede anschauen kann. Das Popup-Fenster soll vergrößerbar und
 * zoombar sein").
 *
 * Ein `<dialog>` (`#bildfenster`, EINES je Seite): Das Fenster zieht man an der Ecke größer (`resize: both`, Größe je
 * Browser gemerkt über `Dialoggroesse`). Gezeigt wird eine GRUPPE nebeneinander — Vorlage und Render desselben
 * Blickwinkels —, beide mit DERSELBEN Vergrößerung und Verschiebung: Mausrad zoomt um den Zeiger, Ziehen verschiebt,
 * Doppelklick oder „Einpassen" setzt zurück, „1:1" zeigt Bildpunkte. ←/→ blättern durch die Gruppen der Runde.
 */
export class Blendermodellbildfenster {

    static MERKER = 'blendermodell.bildfenster.groesse';
    static SCHRITT = 1.25;
    static GRENZEN = [0.1, 40];

    constructor() {
        this.dialog = document.getElementById('bildfenster');
        this.titel = document.getElementById('bildfenster-titel');
        this.flaeche = document.getElementById('bildfenster-flaeche');
        this.gruppen = [];
        this.index = 0;
        this.zoom = 1;
        this.x = 0;
        this.y = 0;
        this._zug = null;
        Dialoggroesse.merken(this.dialog, Blendermodellbildfenster.MERKER);
        this.dialog.addEventListener('click', ereignis => this._knopf(ereignis));
        this.dialog.addEventListener('keydown', ereignis => this._taste(ereignis));
        this.flaeche.addEventListener('wheel', ereignis => this._rad(ereignis), { passive: false });
        this.flaeche.addEventListener('pointerdown', ereignis => this._greifen(ereignis));
        this.flaeche.addEventListener('pointermove', ereignis => this._ziehen(ereignis));
        this.flaeche.addEventListener('pointerup', () => { this._zug = null; });
        this.flaeche.addEventListener('dblclick', () => this.einpassen());
        new ResizeObserver(() => { if (this.dialog.open) this._anwenden(); }).observe(this.flaeche);
    }

    /** `gruppen`: [{titel, bilder: [{src, titel}]}] — `index` die angeklickte. */
    oeffnen(gruppen, index = 0) {
        this.gruppen = gruppen;
        if (!this.dialog.open) this.dialog.showModal();
        this.zeigen(index);
    }

    zeigen(index) {
        const anzahl = this.gruppen.length;
        this.index = ((index % anzahl) + anzahl) % anzahl;
        const g = this.gruppen[this.index];
        this.titel.textContent = anzahl > 1 ? `${g.titel} (${this.index + 1} von ${anzahl})` : g.titel;
        this.flaeche.replaceChildren(...g.bilder.map(b => this._feld(b)));
        this.einpassen();
    }

    _feld(b) {
        const feld = document.createElement('figure');
        feld.className = 'blendermodell-bildfenster-feld';
        const bild = document.createElement('img');
        bild.src = b.src;
        bild.alt = b.titel;
        bild.draggable = false;
        bild.addEventListener('load', () => this._anwenden());
        const unter = document.createElement('figcaption');
        unter.textContent = b.titel;
        feld.append(bild, unter);
        return feld;
    }

    einpassen() {
        this.zoom = 1;
        this.x = 0;
        this.y = 0;
        this._anwenden();
    }

    /** Jedes Bild wird in sein Feld eingepasst (Maßstab 1 = eingepasst), dann gemeinsam vergrößert/verschoben. */
    _anwenden() {
        for (const bild of this.flaeche.querySelectorAll('img')) {
            const feld = bild.parentElement;
            const passt = Math.min(feld.clientWidth / (bild.naturalWidth || 1), feld.clientHeight / (bild.naturalHeight || 1));
            const m = passt * this.zoom;
            bild.style.width = `${(bild.naturalWidth || 0) * m}px`;
            bild.style.transform = `translate(calc(-50% + ${this.x}px), calc(-50% + ${this.y}px))`;
        }
        const erstes = this.flaeche.querySelector('img');
        const passt = erstes?.naturalWidth
            ? Math.min(erstes.parentElement.clientWidth / erstes.naturalWidth, erstes.parentElement.clientHeight / erstes.naturalHeight) : 1;
        const knopf = this.dialog.querySelector('[data-bildfenster="massstab"]');
        if (knopf) knopf.textContent = `${Math.round(passt * this.zoom * 100)} %`;
    }

    _zoomen(faktor, px = 0, py = 0) {
        const [min, max] = Blendermodellbildfenster.GRENZEN;
        const neu = Math.min(max, Math.max(min, this.zoom * faktor));
        const f = neu / this.zoom;
        // Der Punkt unter dem Zeiger bleibt stehen: Verschiebung mitskalieren.
        this.x = px - (px - this.x) * f;
        this.y = py - (py - this.y) * f;
        this.zoom = neu;
        this._anwenden();
    }

    /** 1:1 — ein Bildpunkt der ersten Datei je Bildschirmpunkt. */
    _echt() {
        const bild = this.flaeche.querySelector('img');
        if (!bild?.naturalWidth) return;
        const feld = bild.parentElement;
        const passt = Math.min(feld.clientWidth / bild.naturalWidth, feld.clientHeight / bild.naturalHeight);
        this._zoomen(1 / passt / this.zoom);
    }

    _rad(ereignis) {
        ereignis.preventDefault();
        const feld = ereignis.target.closest('figure');
        if (!feld) return;
        const r = feld.getBoundingClientRect();
        const faktor = ereignis.deltaY < 0 ? Blendermodellbildfenster.SCHRITT : 1 / Blendermodellbildfenster.SCHRITT;
        this._zoomen(faktor, ereignis.clientX - r.left - r.width / 2, ereignis.clientY - r.top - r.height / 2);
    }

    _greifen(ereignis) {
        if (ereignis.button !== 0) return;
        this._zug = { x: ereignis.clientX - this.x, y: ereignis.clientY - this.y };
        this.flaeche.setPointerCapture(ereignis.pointerId);
    }

    _ziehen(ereignis) {
        if (!this._zug) return;
        this.x = ereignis.clientX - this._zug.x;
        this.y = ereignis.clientY - this._zug.y;
        this._anwenden();
    }

    _knopf(ereignis) {
        const aktion = ereignis.target.closest('[data-bildfenster]')?.dataset.bildfenster;
        if (aktion === 'zu') this.dialog.close();
        if (aktion === 'plus') this._zoomen(Blendermodellbildfenster.SCHRITT);
        if (aktion === 'minus') this._zoomen(1 / Blendermodellbildfenster.SCHRITT);
        if (aktion === 'einpassen') this.einpassen();
        if (aktion === 'massstab') this._echt();
        if (aktion === 'zurueck') this.zeigen(this.index - 1);
        if (aktion === 'vor') this.zeigen(this.index + 1);
    }

    _taste(ereignis) {
        const tasten = { ArrowLeft: -1, ArrowRight: 1 };
        if (tasten[ereignis.key] && this.gruppen.length > 1) {
            ereignis.preventDefault();
            ereignis.stopPropagation();
            this.zeigen(this.index + tasten[ereignis.key]);
        }
        if (ereignis.key === '+' || ereignis.key === '=') this._zoomen(Blendermodellbildfenster.SCHRITT);
        if (ereignis.key === '-') this._zoomen(1 / Blendermodellbildfenster.SCHRITT);
        if (ereignis.key === '0') this.einpassen();
    }
}
