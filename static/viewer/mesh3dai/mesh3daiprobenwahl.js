/**
 * Mesh3daiprobenwahl — die Wahl der Probe auf der Seite „Mesh3D-AI“ (14.10.2026): ein Kästchen je Probe (Rand nach Fehler, getönt bei Prüfposen), Vor/Zurück, Pfeiltasten, Filter
 * „nur Prüfposen“ und „schlechteste zuerst“. Die Reihenfolge der Kästchen ist fest (die Nummer der Probe), außer „schlechteste zuerst“ sortiert nach dem mittleren Gelenkfehler.
 */
export class Mesh3daiprobenwahl {
    /** Mittlerer Gelenkfehler in mm, ab dem ein Kästchen einen farbigen unteren Rand bekommt. */
    static MITTEL_MM = 10;
    static HOCH_MM = 25;

    /** @param {{chips, zurueck, weiter, zaehler, nurPruefung, schlechtZuerst}} el die Elemente; @param {(probe: object) => void} beiWahl */
    constructor(el, beiWahl) {
        this.el = el;
        this.beiWahl = beiWahl;
        this.proben = [];
        this.sichtbar = [];
        this.gewaehlt = null;
        el.zurueck.addEventListener('click', () => this.schritt(-1));
        el.weiter.addEventListener('click', () => this.schritt(1));
        // Die Filter merkt sich die Seite (`Mesh3daiansichtgedaechtnis`, 17.10.2026) — hier nur der Hörer, der den Stand schickt, hängt in `Mesh3daiseite`.
        el.nurPruefung.addEventListener('change', () => this._aufbauen());
        el.schlechtZuerst.addEventListener('change', () => this._aufbauen());
        document.addEventListener('keydown', e => this._taste(e));
    }

    /** @param {object[]} proben; @param {number|null} start die Nummer der Probe, die zuerst gewählt wird (die zuletzt gewählte, 17.10.2026) — fehlt sie oder ist sie ausgefiltert, die erste */
    laden(proben, start = null) {
        this.proben = proben;
        this.gewaehlt = start == null ? null : proben.find(p => p.id === start) ?? null;
        this._aufbauen();
    }

    _taste(e) {
        if (e.target.closest?.('input, select, textarea') || e.ctrlKey || e.altKey || e.metaKey) return;
        if (e.key === 'ArrowLeft') this.schritt(-1);
        else if (e.key === 'ArrowRight') this.schritt(1);
    }

    /** Die Kästchen nach den Filtern neu bauen; die gewählte Probe bleibt, wenn sie noch sichtbar ist, sonst die erste. */
    _aufbauen() {
        let liste = this.proben.filter(p => !this.el.nurPruefung.checked || p.aufteilung === 'pruefung');
        if (this.el.schlechtZuerst.checked) liste = [...liste].sort((a, b) => b.kennzahlen.mittel_mm - a.kennzahlen.mittel_mm);
        this.sichtbar = liste;
        this.el.chips.replaceChildren(...liste.map(p => this._chip(p)));
        const bleibt = liste.find(p => p.id === this.gewaehlt?.id) ?? liste[0] ?? null;
        this.waehlen(bleibt);
    }

    _chip(p) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'mesh3dai-chip';
        knopf.setAttribute('role', 'option');
        knopf.dataset.id = String(p.id);
        knopf.dataset.aufteilung = p.aufteilung;
        const m = p.kennzahlen.mittel_mm;
        knopf.dataset.fehler = m >= Mesh3daiprobenwahl.HOCH_MM ? 'hoch' : m >= Mesh3daiprobenwahl.MITTEL_MM ? 'mittel' : 'gering';
        knopf.textContent = String(p.id);
        const art = p.gruppe === 'spagat' ? 'Spagat-Bild, nie trainiert' : p.aufteilung === 'pruefung' ? 'Prüfpose' : 'Training';
        knopf.title = `${p.name} — ${art} — Ø ${m.toLocaleString('de-DE')} mm`;
        knopf.addEventListener('click', () => this.waehlen(p));
        return knopf;
    }

    schritt(richtung) {
        if (!this.sichtbar.length) return;
        const i = this.sichtbar.findIndex(p => p.id === this.gewaehlt?.id);
        this.waehlen(this.sichtbar[(i + richtung + this.sichtbar.length) % this.sichtbar.length]);
    }

    waehlen(probe) {
        this.gewaehlt = probe;
        const i = probe ? this.sichtbar.indexOf(probe) : -1;
        this.el.zaehler.textContent = probe ? `${i + 1} von ${this.sichtbar.length}` : '—';
        for (const knopf of this.el.chips.children) {
            const aktiv = !!probe && knopf.dataset.id === String(probe.id);
            knopf.setAttribute('aria-selected', aktiv ? 'true' : 'false');
            if (aktiv) knopf.scrollIntoView({ block: 'nearest', inline: 'nearest' });
        }
        this.beiWahl(probe);
    }
}
