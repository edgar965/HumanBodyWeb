/**
 * Proportionenbildtab — der erste Reiter des Popups: EIN Bild, die Maßlinien darauf ziehen.
 *
 * Edgar (19.09.2026): „ein Bild pro Zeile, Popup auf dem Bild gibt die Maße
 * an … ich möchte die Regler-Position auch verschieben können, nicht nur die
 * Länge."
 *
 * Das Bild ist das, auf das Edgar geklickt hat — das Foto der Zeile oder das
 * gerenderte Vorher-Bild. Jede Maßlinie hat einen Griff an beiden Enden: ein
 * Griff setzt SEIN Ende (Lage und Länge frei), die Linie selbst (Strich oder
 * Beschriftung) verschiebt beide Enden. Der Wert in cm ist die Länge durch
 * `px_je_m` des Bildes. Jeder Zug geht als `beiLage(quelle, schluessel, linie)`
 * an den Dialog, der Lage und Wert hält und Tabelle und Zeilenbilder nachzieht.
 * Das SVG fängt den Zeiger (`setPointerCapture` auf dem SVG — die Griffe
 * werden bei jedem Zeichnen neu gebaut). Das × am linken Ende einer Linie
 * (oder Entf auf der markierten Linie) geht als `beiLoeschen(schluessel)` an
 * den Dialog: das Maß verliert seine Vorgabe, in ALLEN Bildern.
 */
import { Proportionenlinien } from './proportionenlinien.js';

export class Proportionenbildtab {

    /**
     * @param feld     Element des Reiters (wird gefüllt)
     * @param katalog  `katalog.proportionen` liefert Name und formbar je Maß
     * @param beiLage  `(quelleId, schluessel, linie)` — eine Linie wurde gezogen
     * @param beiLoeschen  `(schluessel)` — das × einer Linie oder Entf auf der markierten
     */
    constructor(feld, katalog, beiLage, beiLoeschen) {
        this.feld = feld;
        this.katalog = katalog || {};
        this.beiLage = beiLage;
        this.beiLoeschen = beiLoeschen || (() => {});
        this.quelle = null;
        this.lagen = {};
        this.eingaben = {};
        this.werte = {};
        this.aktiv = null;
        this.zug = null;
        if (!this.feld) return;
        this.feld.innerHTML = '<figure class="bildmodell-propgross"><img alt=""><svg class="bildmodell-proplinien bildmodell-propgriffe"></svg>'
            + '<figcaption></figcaption></figure>';
        this.figur = this.feld.querySelector('figure');
        this.bild = this.feld.querySelector('img');
        this.text = this.feld.querySelector('figcaption');
        this.svg = this.feld.querySelector('svg');
        this.svg.addEventListener('pointerdown', e => this._anfassen(e));
        this.svg.addEventListener('pointermove', e => this._ziehen(e));
        this.svg.addEventListener('pointerup', e => this._loslassen(e));
        this.svg.addEventListener('pointercancel', e => this._loslassen(e));
        this.svg.tabIndex = 0;
        this.svg.addEventListener('keydown', e => {
            if ((e.key === 'Delete' || e.key === 'Backspace') && this.aktiv) { e.preventDefault(); this.beiLoeschen(this.aktiv); }
        });
    }

    // ---------------------------------------------------------- Zeigen

    /**
     * @param quelle    `{id, art, src, breite, hoehe, px_je_m, titel}`
     * @param lagen     `{k: linie}` dieser Quelle — vom Dialog gehalten, hier nur gelesen
     * @param eingaben  `{k: cm}` — vom Dialog gehalten
     * @param werte     `{k: cm}` — die gemessenen Zielwerte (Anzeige, wo keine Eingabe steht)
     */
    zeigen(quelle, lagen, eingaben, werte, mass = null) {
        if (!this.feld) return;
        this.quelle = quelle;
        this.lagen = lagen || {};
        this.eingaben = eingaben;
        this.werte = werte || {};
        this.aktiv = mass;
        if (!quelle) { this.svg.innerHTML = ''; this.bild.removeAttribute('src'); this.text.textContent = ''; return; }
        this.figur.style.aspectRatio = `${quelle.breite} / ${quelle.hoehe}`;
        this.bild.src = quelle.src;
        this.svg.setAttribute('viewBox', `0 0 ${quelle.breite} ${quelle.hoehe}`);
        this.text.textContent = quelle.titel || '';
        this.zeichnen();
    }

    /** Linien, Beschriftung und Griffe aus den Lagen. */
    zeichnen() {
        const q = this.quelle;
        if (!q) return;
        const eintraege = Object.entries(this.lagen).map(([k, linie]) => {
            const eingestellt = this.eingaben[k] !== undefined && this.eingaben[k] !== null && this.eingaben[k] !== '';
            const wert = eingestellt ? Number(this.eingaben[k])
                : (q.art === 'foto' ? Proportionenlinien.cm(linie, q.px_je_m) : this.werte[k]);
            return { k, name: this._name(k), p: linie[0], q: linie[1], wert, eingestellt, aktiv: k === this.aktiv };
        });
        this.svg.innerHTML = Proportionenlinien.markup(eintraege, Proportionenlinien.bezug(q.breite, q.hoehe), true);
    }

    _name(k) {
        return (this.katalog.proportionen || []).find(m => m.schluessel === k)?.name || k;
    }

    // ---------------------------------------------------------- Ziehen

    /** Zeigerlage in Bildpixeln (viewBox), über die Abbildung des SVG. */
    _bildpunkt(e) {
        const m = this.svg.getScreenCTM();
        if (!m) return null;
        const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(m.inverse());
        return [p.x, p.y];
    }

    /** Bildpunkt zu Fensterkoordinaten — null außerhalb des Bildes (für die Liste rechts). */
    bildpunktVon(clientX, clientY) {
        if (!this.quelle) return null;
        const punkt = this._bildpunkt({ clientX, clientY });
        if (!punkt) return null;
        const [x, y] = punkt;
        if (x < 0 || y < 0 || x > this.quelle.breite || y > this.quelle.hoehe) return null;
        return [Math.round(x * 10) / 10, Math.round(y * 10) / 10];
    }

    _anfassen(e) {
        const gruppe = e.target.closest ? e.target.closest('g[data-mass]') : null;
        if (!gruppe || !this.quelle) return;
        const k = gruppe.dataset.mass;
        const m = (this.katalog.proportionen || []).find(x => x.schluessel === k);
        if (m && m.formbar === false) return;
        if (e.target.closest('.prop-loeschen')) { e.preventDefault(); this.beiLoeschen(k); return; }
        this.svg.focus({ preventScroll: true });
        const linie = this.lagen[k];
        const punkt = this._bildpunkt(e);
        if (!linie || !punkt) return;
        const griff = e.target.closest('.prop-griff');
        this.zug = { k, linie, ende: griff ? Number(griff.dataset.ende) : null, von: punkt };
        this.aktiv = k;
        this.svg.setPointerCapture(e.pointerId);
        e.preventDefault();
    }

    _ziehen(e) {
        if (!this.zug) return;
        const punkt = this._bildpunkt(e);
        if (!punkt) return;
        const z = this.zug;
        const neu = z.ende === null
            ? Proportionenlinien.verschoben(z.linie, punkt[0] - z.von[0], punkt[1] - z.von[1])
            : Proportionenlinien.mitEnde(z.linie, z.ende, punkt);
        const gerundet = neu.map(([x, y]) => [Math.round(x * 10) / 10, Math.round(y * 10) / 10]);
        this.beiLage(this.quelle.id, z.k, gerundet);
        this.zeichnen();
    }

    _loslassen(e) {
        if (!this.zug) return;
        try { this.svg.releasePointerCapture(e.pointerId); } catch (fehler) { /* schon frei */ }
        this.zug = null;
    }
}
