/**
 * Proportionendialog — das Popup, in dem Edgar die Maße einstellt: zwei Reiter.
 *
 * Edgar (19.09.2026): „Mit einem Popup kommt ein Fenster, wo ich diese
 * anpassen kann" — abends: „ein Bild pro Zeile, Popup auf dem Bild gibt die
 * Maße an … zwei Tabs, einmal mit Bild, wo ich alle Maße per Ziehen festlegen
 * kann, zweiter Tab die Maße … auch die Position."
 *
 * Reiter „Bild" (`Proportionenbildtab`): das Bild, auf das geklickt wurde —
 * ein Foto der Tabelle oder ein Vorher-Bild — mit den Linien und Griffen.
 * Reiter „Maße": eine Zeile je Maß (`katalog.proportionen`, 19), Eingabe in
 * cm (leer = keine Vorgabe), Ziel wie gemessen, Modell, Differenz. Der Dialog
 * hält den Zustand für beide und für die Tabelle der Seite: `eingaben` (cm je
 * Maß), `lagen` (Linie je Quelle und Maß, Pixel des jeweiligen Bildes) und
 * `start` (die Lagen, wie der Server sie liefert — `zustand.fotolinien` je
 * Foto, gemerkte Züge eingemischt; die Linien des gerenderten Ziels je
 * Ansicht). Quellen heißen `foto:<datei>` und `ziel:<ansicht>`. Ein Zug setzt
 * Lage und Wert (die Schwesterlinien in anderen Bildern folgen der Länge),
 * eine getippte Zahl streckt alle Linien des Maßes um ihre Mitte, „×" stellt
 * die Startlagen her. „Übernehmen" legt Werte UND die gezogenen Linien der
 * Fotos am Auftrag ab (POST `proportionen/`), „… und neu berechnen" startet ab
 * „Anpassung" (ab „Zielnetz", wenn Größe oder Gewicht geändert sind).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Proportionenbildtab } from './proportionenbildtab.js';
import { Proportionenlinien } from './proportionenlinien.js';

export class Proportionendialog {

    static ANSICHT = { vorn: 'vorn', seite: 'seite', kopf: 'Kopf' };
    static TITEL = { vorn: 'Vorderansicht', seite: 'Seitenansicht', hinten: 'Rückansicht', kopf: 'Kopf' };

    constructor(auftrag, katalog, aenderung) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.aenderung = aenderung || (() => {});
        this.dialog = document.getElementById('proportionen-dialog');
        this.eingaben = { ...((auftrag.zustand.optionen || {}).proportionen || {}) };
        this.quellen = {};
        this.start = {};
        this.lagen = {};
        this._quellstand = null;
        if (!this.dialog) return;
        this.tabelle = this.dialog.querySelector('tbody');
        this.bild = new Proportionenbildtab(this.dialog.querySelector('#proportionen-bildtab'), this.katalog,
            (id, k, linie) => this.lageGezogen(id, k, linie));
        for (const knopf of this.dialog.querySelectorAll('[data-tab-knopf]')) {
            knopf.addEventListener('click', () => this.reiter(knopf.dataset.tabKnopf));
        }
        this.dialog.querySelector('[data-tat="uebernehmen"]')?.addEventListener('click', () => this.uebernehmen(false));
        this.dialog.querySelector('[data-tat="rechnen"]')?.addEventListener('click', () => this.uebernehmen(true));
        this.dialog.querySelector('[data-tat="alle-loeschen"]')?.addEventListener('click', () => this.alleLoeschen());
        this.dialog.querySelector('[data-tat="schliessen"]')?.addEventListener('click', () => this.dialog.close());
    }

    /** `{schluessel: cm}` der ausgefüllten Felder. */
    werte() {
        const aus = {};
        for (const [k, v] of Object.entries(this.eingaben)) {
            if (v !== null && v !== undefined && v !== '' && Number.isFinite(Number(v))) aus[k] = Number(v);
        }
        return aus;
    }

    daten() { return (this.auftrag.zustand.ergebnis || {}).proportionen || { ziel: {}, modell: {} }; }

    // ---------------------------------------------------------- Quellen

    /** Je Foto der Tabelle und je Vorher-Bild eine Quelle mit Startlagen — neu nur bei geändertem Zustand. */
    quellenAufbauen() {
        const z = this.auftrag.zustand;
        const p = this.daten();
        const fotos = z.fotolinien || [];
        const stand = JSON.stringify([z.updated_at, fotos.map(f => [f.datei, f.px_je_m, Object.keys(f.linien || {}).length]),
                                      Object.keys(p.ansichten || {})]);
        if (stand === this._quellstand) return;
        this._quellstand = stand;
        this.quellen = {};
        this.start = {};
        for (const f of fotos) {
            if (!f.px_je_m || !f.breite || !f.hoehe) continue;
            const id = `foto:${f.datei}`;
            this.quellen[id] = { id, art: 'foto', datei: f.datei, ansicht: f.ansicht, breite: f.breite, hoehe: f.hoehe,
                                 px_je_m: f.px_je_m, src: this.auftrag.dateiAdresse('zuschnitt', f.datei), titel: f.datei };
            this.start[id] = Proportionendialog._kopie(f.linien || {});
        }
        for (const [a, r] of Object.entries(p.ansichten || {})) {
            const id = `ziel:${a}`;
            this.quellen[id] = { id, art: 'ziel', ansicht: a, breite: r.breite, hoehe: r.hoehe, px_je_m: r.px_je_m.ziel,
                                 src: this.auftrag.dateiAdresse('ergebnis', r.bild.ziel) + `?t=${Date.now()}`,
                                 titel: `Vorher — Ziel, ${Proportionendialog.TITEL[a] || a}` };
            this.start[id] = Proportionendialog._kopie((r.linien || {}).ziel || {});
        }
        this.lagen = Proportionendialog._kopie(this.start);
        for (const k of Object.keys(this.werte())) this._strecken(k, this.eingaben[k]);
        // Ist das Popup gerade offen (Zustand kam vom Lauf), zeigt sein Bild die neuen Lagen.
        if (this.bild.quelle) this.bild.lagen = this.lagen[this.bild.quelle.id] || {};
    }

    static _kopie(o) { return JSON.parse(JSON.stringify(o)); }

    /** Alle Linien des Maßes `k` auf `cm` bringen (um ihre Mitte), wo die Länge abweicht; leer = Startlage. */
    _strecken(k, cm, ausser = null) {
        for (const [id, q] of Object.entries(this.quellen)) {
            if (id === ausser) continue;
            const linie = (this.lagen[id] || {})[k];
            if (!linie || !q.px_je_m) continue;
            if (cm === null || cm === undefined || cm === '') { this.lagen[id][k] = Proportionendialog._kopie(this.start[id][k]); continue; }
            if (Math.abs((Proportionenlinien.cm(linie, q.px_je_m) || 0) - Number(cm)) > 0.05) {
                this.lagen[id][k] = Proportionenlinien.strecken(linie, Number(cm) / 100 * q.px_je_m);
            }
        }
    }

    /** Wert eines Maßes für ein Bild: Eingabe, sonst Länge im Foto, sonst Ziel. */
    wert(id, k) {
        if (this.eingaben[k] !== undefined && this.eingaben[k] !== null && this.eingaben[k] !== '') return Number(this.eingaben[k]);
        const q = this.quellen[id];
        const linie = (this.lagen[id] || {})[k];
        if (q && q.art === 'foto' && linie) return Proportionenlinien.cm(linie, q.px_je_m);
        return (this.daten().ziel || {})[k];
    }

    // ----------------------------------------------------------- Reiter

    reiter(name) {
        for (const knopf of this.dialog.querySelectorAll('[data-tab-knopf]')) {
            knopf.setAttribute('aria-selected', String(knopf.dataset.tabKnopf === name));
        }
        for (const feld of this.dialog.querySelectorAll('[data-tab]')) feld.hidden = feld.dataset.tab !== name;
        if (name === 'bild') this.bild.zeichnen();
    }

    /** `quelleId`: das Bild, auf das geklickt wurde (ohne: Reiter Maße); `mass`: hervorgehoben. */
    oeffnen(quelleId = null, mass = null) {
        if (!this.dialog) return;
        this.quellenAufbauen();
        const daten = this.daten();
        this._tabelleFuellen(daten);
        const q = quelleId ? this.quellen[quelleId] : null;
        this.bild.zeigen(q, q ? this.lagen[q.id] : {}, this.eingaben, daten.ziel || {}, mass);
        this.dialog.querySelector('[data-tab-knopf="bild"]').hidden = !q;
        this.reiter(q ? 'bild' : 'masse');
        this.dialog.showModal();
        if (mass) this.tabelle.querySelector(`tr[data-mass="${mass}"]`)?.classList.add('prop-aktiv');
    }

    _tabelleFuellen(daten) {
        this.tabelle.innerHTML = '';
        const [lo, hi] = this.katalog.proportion_cm || [0.5, 120];
        for (const m of this.katalog.proportionen || []) {
            const k = m.schluessel;
            const ziel = daten.ziel[k], modell = daten.modell[k];
            const tr = document.createElement('tr');
            tr.dataset.mass = k;
            const wert = this.eingaben[k] ?? '';
            const diff = (ziel !== undefined && modell !== undefined) ? (modell - ziel).toFixed(1) : '–';
            const formung = (daten.formung || {})[k];
            const hinweis = !m.formbar ? '<span class="hb-hinweis">nur Ansicht — Augäpfel folgen nicht</span>'
                : formung ? `<span class="hb-hinweis">geformt ${formung.vorher} → ${formung.nachher} cm</span>` : '';
            tr.innerHTML = `<th>${m.name}<br><span class="hb-hinweis">${Proportionendialog.ANSICHT[m.ansicht] || m.ansicht}</span></th>`
                + `<td><input type="number" step="0.1" min="${lo}" max="${hi}" value="${wert}" placeholder="${ziel ?? ''}" ${m.formbar ? '' : 'disabled'}>`
                + `<button type="button" class="btn btn-sm btn-secondary" data-tat="leeren" title="Vorgabe löschen — Linien zurück auf ihre Startlage">×</button></td>`
                + `<td>${ziel !== undefined ? ziel.toFixed(1) : '–'}</td><td>${modell !== undefined ? modell.toFixed(1) : '–'}</td>`
                + `<td>${diff}</td><td>${hinweis}</td>`;
            const input = tr.querySelector('input');
            input.addEventListener('input', () => this.wertGetippt(k, input.value === '' ? null : Number(input.value)));
            tr.querySelector('[data-tat="leeren"]').addEventListener('click', () => { input.value = ''; this.wertGetippt(k, null); });
            this.tabelle.appendChild(tr);
        }
    }

    // --------------------------------------------------------- Änderung

    /** Aus der Tabelle: Wert merken, alle Linien strecken (oder zurück), Bild und Seite nachziehen. */
    wertGetippt(k, wert) {
        this.eingaben[k] = wert;
        this._strecken(k, wert);
        this.bild.zeichnen();
        this.aenderung();
    }

    /** Aus dem Bild: Lage merken, Wert = Länge, Schwesterlinien auf die Länge, Tabelle nachziehen. */
    lageGezogen(id, k, linie) {
        this.lagen[id] = this.lagen[id] || {};
        this.lagen[id][k] = linie;
        const cm = Proportionenlinien.cm(linie, this.quellen[id].px_je_m);
        if (cm === null) return;
        this.eingaben[k] = cm;
        this._strecken(k, cm, id);
        const feld = this.tabelle.querySelector(`tr[data-mass="${k}"] input`);
        if (feld) feld.value = cm;
        this.aenderung();
    }

    alleLoeschen() {
        for (const k of Object.keys(this.eingaben)) this.eingaben[k] = null;
        this.lagen = Proportionendialog._kopie(this.start);
        for (const i of this.tabelle.querySelectorAll('input')) i.value = '';
        this.bild.lagen = this.bild.quelle ? this.lagen[this.bild.quelle.id] : {};
        this.bild.zeichnen();
        this.aenderung();
    }

    /** Die Linien der Fotos zu Maßen mit Eingabe — `{datei: {linien}}`. */
    linienZumSpeichern() {
        const werte = this.werte();
        const aus = {};
        for (const [id, q] of Object.entries(this.quellen)) {
            if (q.art !== 'foto') continue;
            const linien = {};
            for (const k of Object.keys(werte)) if ((this.lagen[id] || {})[k]) linien[k] = this.lagen[id][k];
            if (Object.keys(linien).length) aus[q.datei] = { linien };
        }
        return aus;
    }

    async uebernehmen(rechnen) {
        const proportionen = this.werte();
        const linien = this.linienZumSpeichern();
        try {
            const antwort = await Serverabruf.senden(this.auftrag.adresse('proportionen/'), { proportionen, linien });
            if (antwort.error) throw new Error(antwort.error);
            this.auftrag.zustand.optionen = { ...(this.auftrag.zustand.optionen || {}), proportionen: antwort.proportionen,
                                              proportionen_linien: antwort.linien };
            for (const k of Object.keys(this.eingaben)) delete this.eingaben[k];
            Object.assign(this.eingaben, antwort.proportionen);
            this.dialog.close();
            this.aenderung();
            if (rechnen) {
                // Größe/Gewicht unverändert: das Zielnetz steht, ab „Anpassung" reicht (spart den Zielschritt).
                const p = window.__bildmodell?.person;
                if (p) await p.neuBerechnen(p.unveraendert() ? 'anpassung' : 'ziel');
            }
        } catch (fehler) {
            window.alert(`Proportionen nicht übernommen: ${fehler.message}`);
        }
    }
}
