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
 * eine getippte Zahl streckt alle Linien des Maßes um ihre Mitte, „×" in der
 * Tabelle löscht die Vorgabe (Linien zurück auf die Startlage). Im Bild-Reiter
 * (Edgar, 20.09.2026: „einzelne Marker LÖSCHEN … ALLE Maße rechts, auf die Figur
 * ziehen"): × an der Linie oder in der Liste rechts nimmt den MARKER aus diesem
 * Bild (`entfernt`, je Foto gemerkt), ⤓ zieht ein fehlendes Maß ins Bild
 * (`markerSetzen`: Linie an der Stelle, Länge = Wert). Das Fenster ist
 * vergrößerbar, die Größe steht im `localStorage`. „Übernehmen" und „… und neu
 * berechnen": `Proportionenuebernahme`. Der Knopf „3D-Modell" öffnet das
 * 3D-Popup (`Proportionen3d`): das Zielnetz folgt jedem Pfeil, jeder Zahl und
 * jedem Schieber dort (Edgar, 20.09.2026: „das 3D Modell interaktiv anpassen,
 * wenn ich die Pfeile ändere … wie die Morph-Slider bei Genesis").
 */
import { Proportionen3d } from './proportionen3d.js';
import { Proportionenbildtab } from './proportionenbildtab.js';
import { Proportionenlinien } from './proportionenlinien.js';
import { Proportionenliste } from './proportionenliste.js';
import { Proportionenmasstab } from './proportionenmasstab.js';
import { Proportionenuebernahme } from './proportionenuebernahme.js';
import { Proportionenvorschlag } from './proportionenvorschlag.js';
import { Dialoggroesse } from './dialoggroesse.js';

export class Proportionendialog {

    static GROESSE = 'bildmodell.prop.dialog';
    /** Länge einer neu gesetzten Linie ohne Wert (cm). */
    static NEU_CM = 20;
    static TITEL = { vorn: 'Vorderansicht', seite: 'Seitenansicht', hinten: 'Rückansicht', kopf: 'Kopf' };

    constructor(auftrag, katalog, aenderung) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        // Jede Änderung geht an die Seite (Tabelle) und ans 3D-Popup, wenn es offen ist.
        this.aenderung = () => { (aenderung || (() => {}))(); this.dreid?.nachziehen(); };
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
            (id, k, linie) => this.lageGezogen(id, k, linie), k => this.markerLoeschen(k));
        this.liste = new Proportionenliste(this.dialog.querySelector('#proportionen-bildliste'), this.katalog, this.bild,
            (k, punkt) => this.markerSetzen(k, punkt), k => this.markerLoeschen(k),
            k => { this.bild.aktiv = k; this.bild.zeichnen(); this.listeZeigen(); }, () => this.alleSetzen());
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
            if (!this.entfernt[id]) this.entfernt[id] = new Set(f.entfernt || []);
        }
        for (const [a, r] of Object.entries(p.ansichten || {})) {
            const id = `ziel:${a}`;
            this.quellen[id] = { id, art: 'ziel', ansicht: a, breite: r.breite, hoehe: r.hoehe, px_je_m: r.px_je_m.ziel,
                                 src: this.auftrag.dateiAdresse('ergebnis', r.bild.ziel) + `?t=${Date.now()}`,
                                 titel: `Vorher — Ziel, ${Proportionendialog.TITEL[a] || a}` };
            this.start[id] = Proportionendialog._kopie((r.linien || {}).ziel || {});
        }
        for (const [id, weg] of Object.entries(this.entfernt)) for (const k of weg) delete (this.start[id] || {})[k];
        this.serverStart = Proportionendialog._kopie(this.start);
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
        if (name === 'bild') { this.bild.zeichnen(); this.listeZeigen(); }
    }

    listeZeigen() {
        const q = this.bild.quelle;
        if (!q) return;
        this.liste.zeigen(this.lagen[q.id] || {}, this.entfernt[q.id] || new Set(), k => this.wert(q.id, k), this.bild.aktiv);
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

    /** Aus der Tabelle: Wert merken, alle Linien strecken (oder zurück), Bild und Seite nachziehen. */
    wertGetippt(k, wert) {
        this.eingaben[k] = wert;
        this._strecken(k, wert);
        this.bild.zeichnen();
        this.aenderung();
    }

    /** Aus dem 3D-Popup (Schieber): wie getippt, dazu Tabellenfeld und Liste nachziehen. */
    wertGeschoben(k, cm) {
        this.masstab.setzen(k, cm);
        this.wertGetippt(k, cm);
        this.listeZeigen();
    }

    /** Aus dem Bild: Lage merken, Wert = Länge, Schwesterlinien auf die Länge, Tabelle nachziehen. */
    lageGezogen(id, k, linie) {
        this.lagen[id] = this.lagen[id] || {};
        this.lagen[id][k] = linie;
        const cm = Proportionenlinien.cm(linie, this.quellen[id].px_je_m);
        if (cm === null) return;
        this.eingaben[k] = cm;
        this._strecken(k, cm, id);
        this.masstab.setzen(k, cm);
        this.aenderung();
        const zeile = this.liste.feld?.querySelector(`[data-mass="${k}"] .wert`);
        if (zeile) zeile.textContent = `${cm.toFixed(1).replace('.', ',')} cm`;
    }

    /** Den Marker eines Maßes aus dem gezeigten Bild nehmen — gemerkt je Foto (`entfernt`). */
    markerLoeschen(k) {
        const q = this.bild.quelle;
        if (!q) return;
        delete (this.lagen[q.id] || {})[k];
        delete (this.start[q.id] || {})[k];
        (this.entfernt[q.id] = this.entfernt[q.id] || new Set()).add(k);
        if (this.bild.aktiv === k) this.bild.aktiv = null;
        this.bild.zeichnen();
        this.listeZeigen();
        this.aenderung();
    }

    /** Ein Maß ins gezeigte Bild: waagerecht um `punkt` (sonst Bildmitte), Länge = Wert in cm. */
    markerSetzen(k, punkt, zeichnen = true) {
        const q = this.bild.quelle;
        if (!q || (this.lagen[q.id] || {})[k]) return;
        const cm = Number(this.wert(q.id, k)) || Proportionendialog.NEU_CM;
        const l = q.px_je_m ? cm / 100 * q.px_je_m : q.breite * 0.2;
        const [cx, cy] = punkt || [q.breite / 2, q.hoehe / 2];
        const linie = [[Math.round((cx - l / 2) * 10) / 10, cy], [Math.round((cx + l / 2) * 10) / 10, cy]];
        (this.lagen[q.id] = this.lagen[q.id] || {})[k] = linie;
        (this.start[q.id] = this.start[q.id] || {})[k] = Proportionendialog._kopie(linie);
        if (this.entfernt[q.id]) this.entfernt[q.id].delete(k);
        this.bild.aktiv = k;
        if (!zeichnen) return;
        this.bild.zeichnen();
        this.listeZeigen();
        this.aenderung();
    }

    /** Alle fehlenden Maße der Ansicht ins gezeigte Bild — Lage aus der Ziel-Ansicht (`Proportionenvorschlag`). */
    alleSetzen() {
        const q = this.bild.quelle;
        if (!q) return;
        const reihe = (this.daten().ansichten || {})[q.ansicht];
        for (const m of this.katalog.proportionen || []) {
            if ((this.lagen[q.id] || {})[m.schluessel]) continue;
            const punkt = Proportionenvorschlag.lage(m.schluessel, q, reihe, this.lagen[q.id] || {});
            if (punkt) this.markerSetzen(m.schluessel, punkt, false);
        }
        this.bild.zeichnen();
        this.listeZeigen();
        this.aenderung();
    }

    /** Alle Vorgaben weg, entfernte Marker wieder da, Linien wie vom Server. */
    alleLoeschen() {
        for (const k of Object.keys(this.eingaben)) this.eingaben[k] = null;
        this.entfernt = {};
        this._quellstand = null;
        this.quellenAufbauen();
        this.lagen = Proportionendialog._kopie(this.start);
        for (const i of this.tabelle.querySelectorAll('input')) i.value = '';
        this.bild.lagen = this.bild.quelle ? this.lagen[this.bild.quelle.id] : {};
        this.bild.zeichnen();
        this.listeZeigen();
        this.aenderung();
    }

    /** Für Aufrufer von außen (Tests, Seite): die Linien, die „Übernehmen" speichert. */
    linienZumSpeichern() { return Proportionenuebernahme.linien(this); }
}
