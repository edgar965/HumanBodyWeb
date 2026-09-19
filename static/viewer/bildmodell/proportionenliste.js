/**
 * Proportionenliste — rechts im Bild-Reiter: ALLE Maße der Figur, ins Bild ziehen oder löschen.
 *
 * Edgar (20.09.2026): „mach in dem Popup rechts ALLE Maße die du für die Figur
 * hast, mit Möglichkeit, die auf die Figur zu ziehen, falls sie noch nicht da
 * sind" — und: „ich möchte einzelne Marker LÖSCHEN können aus den Popups".
 *
 * Eine Zeile je Maß des Katalogs (19): Name, Wert in cm (Eingabe, sonst Länge im
 * Bild, sonst Ziel) und der Stand in DIESEM Bild — „im Bild" (Klick markiert die
 * Linie), „entfernt" oder „nicht im Bild". Ein Maß ohne Linie hat einen Griff
 * (⤓): mit gedrücktem Zeiger auf das Bild ziehen setzt die Linie an der
 * losgelassenen Stelle, ein Klick setzt sie in die Bildmitte (`beiSetzen(k,
 * punkt|null)`). Ein Maß mit Linie hat ein × (`beiLoeschen(k)`) — dasselbe wie
 * das × an der Linie im Bild.
 */
export class Proportionenliste {

    /**
     * @param feld        Element der Liste (wird gefüllt)
     * @param katalog     `katalog.proportionen`
     * @param bildtab     `Proportionenbildtab` — für `bildpunktVon(clientX, clientY)`
     * @param beiSetzen   `(schluessel, punkt|null)` — Linie ins Bild
     * @param beiLoeschen `(schluessel)` — Linie aus dem Bild
     * @param beiWahl     `(schluessel)` — Linie im Bild markieren
     */
    constructor(feld, katalog, bildtab, beiSetzen, beiLoeschen, beiWahl) {
        this.feld = feld;
        this.katalog = katalog || {};
        this.bildtab = bildtab;
        this.beiSetzen = beiSetzen;
        this.beiLoeschen = beiLoeschen;
        this.beiWahl = beiWahl;
        this.zug = null;
        if (!this.feld) return;
        this.feld.addEventListener('pointerdown', e => this._anfassen(e));
        this.feld.addEventListener('pointerup', e => this._loslassen(e));
        this.feld.addEventListener('pointercancel', () => { this.zug = null; });
    }

    /**
     * @param lagen     `{k: linie}` des gezeigten Bildes
     * @param entfernt  Set der Maße, die aus dem Bild gelöscht sind
     * @param wert      `(k) => cm|undefined`
     * @param aktiv     markiertes Maß
     */
    zeigen(lagen, entfernt, wert, aktiv) {
        if (!this.feld) return;
        this.feld.innerHTML = '';
        const kopf = document.createElement('div');
        kopf.className = 'bildmodell-proplistekopf';
        kopf.textContent = 'Alle Maße — ⤓ ins Bild ziehen, × aus dem Bild löschen';
        this.feld.appendChild(kopf);
        for (const m of this.katalog.proportionen || []) {
            const k = m.schluessel;
            const drin = !!(lagen || {})[k];
            const zeile = document.createElement('div');
            zeile.className = 'bildmodell-proplistezeile' + (drin ? ' drin' : '') + (k === aktiv ? ' aktiv' : '');
            zeile.dataset.mass = k;
            const v = wert(k);
            const stand = drin ? 'im Bild' : (entfernt && entfernt.has(k) ? 'entfernt' : 'nicht im Bild');
            zeile.innerHTML = `<span class="name">${m.name}</span>`
                + `<span class="wert">${v === undefined || v === null ? '–' : `${Number(v).toFixed(1).replace('.', ',')} cm`}</span>`
                + `<span class="stand">${stand}</span>`
                + (drin
                    ? `<button type="button" class="btn btn-sm btn-secondary" data-tat="weg" title="${m.name} aus diesem Bild löschen">×</button>`
                    : `<button type="button" class="btn btn-sm btn-secondary" data-tat="setzen" title="${m.name} ins Bild ziehen (oder klicken: Bildmitte)">⤓</button>`);
            if (drin) zeile.querySelector('.name').addEventListener('click', () => this.beiWahl(k));
            zeile.querySelector('[data-tat="weg"]')?.addEventListener('click', () => this.beiLoeschen(k));
            this.feld.appendChild(zeile);
        }
    }

    // ---------------------------------------------------------- Ziehen

    _anfassen(e) {
        const knopf = e.target.closest ? e.target.closest('[data-tat="setzen"]') : null;
        if (!knopf) return;
        const zeile = knopf.closest('[data-mass]');
        this.zug = { k: zeile.dataset.mass, von: [e.clientX, e.clientY] };
        try { this.feld.setPointerCapture(e.pointerId); } catch (fehler) { /* kein echter Zeiger (Test) */ }
        e.preventDefault();
    }

    _loslassen(e) {
        if (!this.zug) return;
        const z = this.zug;
        this.zug = null;
        try { this.feld.releasePointerCapture(e.pointerId); } catch (fehler) { /* schon frei */ }
        const weg = Math.hypot(e.clientX - z.von[0], e.clientY - z.von[1]);
        const punkt = weg > 8 && this.bildtab ? this.bildtab.bildpunktVon(e.clientX, e.clientY) : null;
        this.beiSetzen(z.k, punkt);
    }
}
