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
 * hält den Zustand für alle Sichten: `eingaben` (cm je Maß), `lagen` (Linie
 * je Quelle und Maß, Pixel des jeweiligen Bildes) und `start` (die Lagen, wie
 * der Server sie liefert — `zustand.fotolinien` je Foto, gemerkte Züge
 * eingemischt; die Linien des gerenderten Ziels je Ansicht). Quellen heißen
 * `foto:<datei>` und `ziel:<ansicht>`. Ein Zug setzt Lage und Wert (die
 * Schwesterlinien in anderen Bildern folgen der Länge), eine getippte Zahl
 * streckt alle Linien des Maßes um ihre Mitte, „×" in der Tabelle löscht die
 * Vorgabe (Linien zurück auf die Startlage). Marker setzen und löschen:
 * `Proportionenmarker`. „Übernehmen" und „… und neu berechnen":
 * `Proportionenuebernahme`.
 *
 * SICHTEN (20.09.2026, abends — Edgar: „eine Modell-View mit 3D links, 2D
 * rechts … Wenn ich die Regler ändere, dann ändert sich gleich das 3D Modell
 * links"): das Popup ist EINE Sicht auf diesen Zustand, die `Modellsicht`
 * oben auf der Seite eine zweite (`anmelden(bild, liste)`). Jede Änderung
 * zeichnet alle Sichten nach (`nachzeichnen`) und ruft die Zuhörer
 * (`zuhoeren(fn)`: Tabelle der Seite, Modellsicht) sowie das 3D-Popup; das
 * Zielnetz kommt für alle aus EINER `Zielnetzlive` (`live`).
 */
import { Proportionen3d } from './proportionen3d.js';
import { Proportionenbildtab } from './proportionenbildtab.js';
import { Proportionenlinien } from './proportionenlinien.js';
import { Proportionenliste } from './proportionenliste.js';
import { Proportionenmarker } from './proportionenmarker.js';
import { Proportionenmasstab } from './proportionenmasstab.js';
import { Proportionenuebernahme } from './proportionenuebernahme.js';
import { Dialoggroesse } from './dialoggroesse.js';
import { Zielnetzlive } from './zielnetzlive.js';

export class Proportionendialog {

    static GROESSE = 'bildmodell.prop.dialog';
    static TITEL = { vorn: 'Vorderansicht', seite: 'Seitenansicht', hinten: 'Rückansicht', kopf: 'Kopf' };

    constructor(auftrag, katalog, aenderung) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.zuhoerer = aenderung ? [aenderung] : [];
        // Jede Änderung geht an die Zuhörer (Tabelle der Seite, Modellsicht) und ans 3D-Popup, wenn es offen ist.
        this.aenderung = () => { for (const fn of this.zuhoerer) fn(); this.dreid?.nachziehen(); };
        this.sichten = [];
        this.live = new Zielnetzlive(auftrag, () => this.werte());
        this.dialog = document.getElementById('proportionen-dialog');
        this.eingaben = { ...((auftrag.zustand.optionen || {}).proportionen || {}) };
        this.quellen = {};
        this.start = {};
        this.serverStart = {};
        this.lagen = {};
        this.entfernt = {};
        this._quellstand = null;
        if (!this.dialog) return;
        this.tabelle = this.dialog.querySelector('tbody');
        this.masstab = new Proportionenmasstab(this.tabelle, this.katalog, (k, cm) => this.wertGetippt(k, cm));
        this.bild = new Proportionenbildtab(this.dialog.querySelector('#proportionen-bildtab'), this.katalog,
            (id, k, linie) => this.lageGezogen(id, k, linie), k => this.markerLoeschen(k, this.bild.quelle?.id));
        this.liste = new Proportionenliste(this.dialog.querySelector('#proportionen-bildliste'), this.katalog, this.bild,
            (k, punkt) => this.markerSetzen(k, punkt, true, this.bild.quelle?.id), k => this.markerLoeschen(k, this.bild.quelle?.id),
            k => { this.bild.aktiv = k; this.nachzeichnen(); }, () => this.alleSetzen(this.bild.quelle?.id));
        this.anmelden(this.bild, this.liste);
        this.dreid = new Proportionen3d(this.dialog.querySelector('#proportionen-3d'), auftrag, this.katalog, this);
        this.dialog.querySelector('[data-tat="3d"]')?.addEventListener('click', () => this.dreid.umschalten());
        this.dialog.addEventListener('close', () => { this._dreidWar = this.dreid.offen; this.dreid.schliessen(); });
        Dialoggroesse.merken(this.dialog, Proportionendialog.GROESSE);
        for (const knopf of this.dialog.querySelectorAll('[data-tab-knopf]')) {
            knopf.addEventListener('click', () => this.reiter(knopf.dataset.tabKnopf));
        }
        this.dialog.querySelector('[data-tat="uebernehmen"]')?.addEventListener('click', () => Proportionenuebernahme.uebernehmen(this, false));
        this.dialog.querySelector('[data-tat="rechnen"]')?.addEventListener('click', () => Proportionenuebernahme.uebernehmen(this, true));
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

    // ---------------------------------------------------------- Sichten

    /** `fn()` nach jeder Änderung — die Tabelle der Seite, die Modellsicht. */
    zuhoeren(fn) { this.zuhoerer.push(fn); }

    /** Eine weitere Sicht auf den Zustand: ein `Proportionenbildtab` und (optional) seine `Proportionenliste`. */
    anmelden(bild, liste = null) { this.sichten.push({ bild, liste }); }

    /** Jede Sicht auf den Stand: Lagen ihrer Quelle, Linien neu, Liste neu. Quelle weg → Sicht leer. */
    nachzeichnen() {
        const ziel = this.daten().ziel || {};
        for (const s of this.sichten) {
            const q = s.bild.quelle;
            if (!q) continue;
            if (!this.quellen[q.id]) { s.bild.zeigen(null); s.liste?.zeigen({}, new Set(), () => undefined, null); continue; }
            s.bild.lagen = this.lagen[q.id] || {};
            s.bild.eingaben = this.eingaben;
            s.bild.werte = ziel;
            s.bild.zeichnen();
            s.liste?.zeigen(s.bild.lagen, this.entfernt[q.id] || new Set(), k => this.wert(q.id, k), s.bild.aktiv);
        }
    }

    // ---------------------------------------------------------- Quellen

    /** Je Foto der Tabelle und je Vorher-Bild eine Quelle mit Startlagen — neu nur bei geändertem Zustand. */
    quellenAufbauen() {
        const z = this.auftrag.zustand;
        const p = this.daten();
        const fotos = z.fotolinien || [];
        const stand = JSON.stringify([p.stand || '', fotos.map(f => [f.datei, f.px_je_m, Object.keys(f.linien || {}).length]),
                                      Object.keys(p.ansichten || {})]);
        if (stand === this._quellstand) return false;
        this._quellstand = stand;
        this.quellen = {};
        this.start = {};
        for (const f of fotos) {
            if (!f.px_je_m || !f.breite || !f.hoehe) continue;
            const id = `foto:${f.datei}`;
            this.quellen[id] = { id, art: 'foto', datei: f.datei, ansicht: f.ansicht, breite: f.breite, hoehe: f.hoehe,
                                 px_je_m: f.px_je_m, src: this.auftrag.dateiAdresse('zuschnitt', f.datei), titel: f.datei };
            this.start[id] = Proportionendialog._kopie(f.linien || {});
            if (!this.entfernt[id]) this.entfernt[id] = new Set(f.entfernt || []);
        }
        for (const [a, r] of Object.entries(p.ansichten || {})) {
            const id = `ziel:${a}`;
            this.quellen[id] = { id, art: 'ziel', ansicht: a, breite: r.breite, hoehe: r.hoehe, px_je_m: r.px_je_m.ziel,
                                 src: this.auftrag.dateiAdresse('ergebnis', r.bild.ziel) + `?t=${encodeURIComponent(p.stand || '')}`,
                                 titel: `Vorher — Ziel, ${Proportionendialog.TITEL[a] || a}` };
            this.start[id] = Proportionendialog._kopie((r.linien || {}).ziel || {});
        }
        for (const [id, weg] of Object.entries(this.entfernt)) for (const k of weg) delete (this.start[id] || {})[k];
        this.serverStart = Proportionendialog._kopie(this.start);
        this.lagen = Proportionendialog._kopie(this.start);
        for (const k of Object.keys(this.werte())) this._strecken(k, this.eingaben[k]);
        // Ein neuer Zustand (vom Lauf): jede offene Sicht zeigt die neuen Lagen.
        this.nachzeichnen();
        return true;
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
        if (name === 'bild') this.nachzeichnen();
    }

    /** `quelleId`: das Bild, auf das geklickt wurde (ohne: Reiter Maße); `mass`: hervorgehoben. */
    oeffnen(quelleId = null, mass = null) {
        if (!this.dialog) return;
        this.quellenAufbauen();
        const daten = this.daten();
        this.masstab.fuellen(daten, this.eingaben);
        const q = quelleId ? this.quellen[quelleId] : null;
        this.bild.zeigen(q, q ? this.lagen[q.id] : {}, this.eingaben, daten.ziel || {}, mass);
        this.dialog.querySelector('[data-tab-knopf="bild"]').hidden = !q;
        this.reiter(q ? 'bild' : 'masse');
        this.dialog.showModal();
        if (mass) this.tabelle.querySelector(`tr[data-mass="${mass}"]`)?.classList.add('prop-aktiv');
        if (this._dreidWar) this.dreid.oeffnen();
    }

    // --------------------------------------------------------- Änderung

    /** Aus der Tabelle: Wert merken, alle Linien strecken (oder zurück), Sichten und Seite nachziehen. */
    wertGetippt(k, wert) {
        this.eingaben[k] = wert;
        this._strecken(k, wert);
        this.nachzeichnen();
        this.aenderung();
    }

    /** Aus den Schiebern (3D-Popup, Modellsicht): wie getippt, dazu das Tabellenfeld. */
    wertGeschoben(k, cm) {
        this.masstab.setzen(k, cm);
        this.wertGetippt(k, cm);
    }

    /** Aus dem Bild: Lage merken, Wert = Länge, Schwesterlinien auf die Länge, alles nachziehen. */
    lageGezogen(id, k, linie) {
        this.lagen[id] = this.lagen[id] || {};
        this.lagen[id][k] = linie;
        const cm = Proportionenlinien.cm(linie, this.quellen[id].px_je_m);
        if (cm === null) return;
        this.eingaben[k] = cm;
        this._strecken(k, cm, id);
        this.masstab.setzen(k, cm);
        this.nachzeichnen();
        this.aenderung();
    }

    markerLoeschen(k, id) { Proportionenmarker.loeschen(this, k, id); }

    markerSetzen(k, punkt, zeichnen = true, id) { Proportionenmarker.setzen(this, k, punkt, id, zeichnen); }

    alleSetzen(id) { Proportionenmarker.alle(this, id); }

    alleLoeschen() { Proportionenmarker.alleLoeschen(this); }

    /** Für Aufrufer von außen (Tests, Seite): die Linien, die „Übernehmen" speichert. */
    linienZumSpeichern() { return Proportionenuebernahme.linien(this); }
}
