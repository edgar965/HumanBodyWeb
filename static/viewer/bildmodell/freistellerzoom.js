/**
 * Freistellerzoom — Vergrößern und Verschieben im Freisteller-Fenster (21.09.2026).
 *
 * Edgar: „ich brauche auch ein Vergrößerungsmöglichkeit auf dem Hintergrund entfernen Fenster,
 * zum genauen Arbeiten, z.B. mit mittlerer Rad-Taste?" Mausrad über Foto oder Vorschau zoomt um
 * den Zeiger (1× … 16×), die gedrückte mittlere Taste oder Strg + linke Taste verschiebt. Foto und Vorschau bekommen
 * dieselbe Transformation (beide Felder sind gleich groß, beide Bilder `object-fit: contain`
 * mit demselben Seitenverhältnis) — man sieht links und rechts denselben Ausschnitt. Die
 * Pinsel-Leinwand liegt in der Bühne und wird mitgezoomt; ihre Koordinaten kommen aus
 * `getBoundingClientRect`, das die Transformation schon enthält. „Einpassen" setzt zurück.
 */
export class Freistellerzoom {

    static MAX = 16;
    static SCHRITT = 1.25;

    /** `buehnen`: die transformierten Kinder je Feld; das Feld (Elternelement) fängt Rad und Zeiger. */
    constructor(buehnen, onAenderung) {
        this.buehnen = (buehnen || []).filter(Boolean);
        this.onAenderung = onAenderung;
        this.skala = 1;
        this.tx = 0;
        this.ty = 0;
        this._griff = null;
        for (const b of this.buehnen) {
            const feld = b.parentElement;
            feld.addEventListener('wheel', e => this._rad(e, feld), { passive: false });
            feld.addEventListener('pointerdown', e => this._anfang(e, feld));
            feld.addEventListener('pointermove', e => this._weiter(e));
            feld.addEventListener('pointerup', e => this._ende(e, feld));
            feld.addEventListener('pointercancel', e => this._ende(e, feld));
            // Chrome: mittlere Taste = Autoscroll, mittlerer Klick = auxclick — beides nicht hier.
            feld.addEventListener('mousedown', e => { if (e.button === 1) e.preventDefault(); });
            feld.addEventListener('auxclick', e => { if (e.button === 1) e.preventDefault(); });
        }
    }

    einpassen() { this.setzen(1, 0, 0); }

    setzen(skala, tx, ty) {
        const feld = this.buehnen[0]?.parentElement;
        if (!feld) return;
        const s = Math.max(1, Math.min(Freistellerzoom.MAX, skala));
        // Die Bühne bleibt im Feld: kein Rand links/oben (tx ≤ 0), keiner rechts/unten.
        const w = feld.clientWidth, h = feld.clientHeight;
        this.skala = s;
        this.tx = Math.min(0, Math.max(w - w * s, tx));
        this.ty = Math.min(0, Math.max(h - h * s, ty));
        for (const b of this.buehnen) b.style.transform = s === 1 ? '' : `translate(${this.tx}px, ${this.ty}px) scale(${s})`;
        this.onAenderung?.(s);
    }

    _rad(e, feld) {
        e.preventDefault();
        const r = feld.getBoundingClientRect();
        const px = e.clientX - r.left, py = e.clientY - r.top;
        const s = Math.max(1, Math.min(Freistellerzoom.MAX, this.skala * (e.deltaY < 0 ? Freistellerzoom.SCHRITT : 1 / Freistellerzoom.SCHRITT)));
        // Der Punkt unter dem Zeiger bleibt liegen: (px − tx)/skala = (px − tx')/s.
        this.setzen(s, px - (px - this.tx) * s / this.skala, py - (py - this.ty) * s / this.skala);
    }

    _anfang(e, feld) {
        // Mittlere Taste oder Strg + linke Taste (Edgar, 21.09.2026: „ziehen des Bildes mit Ctrl-Maus Drag").
        if (!(e.button === 1 || (e.button === 0 && e.ctrlKey)) || this.skala === 1) return;
        e.preventDefault();
        this._griff = { id: e.pointerId, x: e.clientX, y: e.clientY, tx: this.tx, ty: this.ty };
        try { feld.setPointerCapture(e.pointerId); } catch (_) { /* kein echter Zeiger */ }
        feld.style.cursor = 'grabbing';
    }

    _weiter(e) {
        if (!this._griff || e.pointerId !== this._griff.id) return;
        this.setzen(this.skala, this._griff.tx + e.clientX - this._griff.x, this._griff.ty + e.clientY - this._griff.y);
    }

    _ende(e, feld) {
        if (!this._griff || e.pointerId !== this._griff.id) return;
        try { feld.releasePointerCapture(e.pointerId); } catch (_) { /* kein echter Zeiger */ }
        feld.style.cursor = '';
        this._griff = null;
    }
}
