/**
 * Mesh3dbuehnengriff — der sichtbare Ziehgriff unten rechts in einer 3D-Ansicht (13.10.2026, Edgar: „der Greifer zum Verkleinern des Views ist weg“).
 *
 * Der Griff des Browsers (`resize: both`) ist ein 15-px-Zeichen in der Ecke der Ansicht, dunkelgrau auf dem schwarzen Grund der Leinwand — auf dem Bildschirm nicht zu sehen, auch wenn er da ist
 * (gemessen am Bildschirmfoto der Seite: ein winziges Dreieck). Dieser Griff ist ein eigenes Element, hell, 28 px groß und über der Leinwand; er zieht Höhe und Breite über dieselben Wege wie die
 * Regler (`Mesh3dbuehnengroesse._setzen`, `_breiteSetzen`), also gelten Grenzen, „volle Breite“ am Rand und das Merken im Browser unverändert.
 */
export class Mesh3dbuehnengriff {
    /** @param {import('./mesh3dbuehnengroesse.js').Mesh3dbuehnengroesse} groesse die Größenregelung der Ansicht */
    constructor(groesse) {
        this.groesse = groesse;
        this.start = null;
        const feld = groesse.feld;
        // Ohne Dokument (Test mit Attrappen) gibt es nichts zu zeichnen.
        if (typeof document === 'undefined' || typeof feld.appendChild !== 'function') return;
        this.element = document.createElement('div');
        this.element.className = 'mesh3d-griff';
        this.element.title = 'Ziehen: Höhe und Breite der Ansicht ändern';
        this.element.setAttribute('aria-hidden', 'true');
        feld.appendChild(this.element);
        this.element.addEventListener('pointerdown', ereignis => this._anfassen(ereignis));
        this.element.addEventListener('pointermove', ereignis => this._ziehen(ereignis));
        for (const art of ['pointerup', 'pointercancel']) this.element.addEventListener(art, ereignis => this._loslassen(ereignis));
    }

    _anfassen(ereignis) {
        if (ereignis.button !== undefined && ereignis.button !== 0) return;
        ereignis.preventDefault();
        this.element.setPointerCapture?.(ereignis.pointerId);
        const feld = this.groesse.feld;
        this.start = { x: ereignis.clientX, y: ereignis.clientY, hoehe: feld.clientHeight, breite: feld.clientWidth };
    }

    _ziehen(ereignis) {
        if (!this.start) return;
        this.groesse._setzen(this.start.hoehe + (ereignis.clientY - this.start.y));
        if (this.groesse.breite) this.groesse._breiteSetzen(this.start.breite + (ereignis.clientX - this.start.x));
    }

    _loslassen(ereignis) {
        this.start = null;
        this.element?.releasePointerCapture?.(ereignis.pointerId);
    }
}
