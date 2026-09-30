import { dbTabelle } from '/static/djangobase/js/tabelle_bauen.js';
import { tabellenBinden } from '/static/djangobase/js/tabellen_auto.js';
import { Zeilenwahl } from '../../js/auftraege/zeilenwahl.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Blendermodellrundenzeilen } from './blendermodellrundenzeilen.js';

/**
 * Blendermodellrundentabelle — die Runden der Iterationen als djangoBase-Tabelle (Edgar, 30.09.2026: „mach die
 * Iterationen in einer Tabelle (djangoBase Vorlage), sortierbar, auswählbar und mit Löschen-Button, Batch löschen" —
 * „lass aber nichts weg von der aktuellen Tabelle, ggf. mehrzeiliger Eintrag pro Runde (mit Unterzeilen)").
 *
 * Kopf, Rahmen, Sortierung und Spaltenbreiten kommen von djangoBase (`dbTabelle`, `tabellenBinden`); die Zeilen
 * baut `Blendermodellrundenzeilen` als DOM: je Runde eine Hauptzeile mit den sortierbaren Kennzahlen und
 * Unterzeilen (Notiz, Prüf-KI, Bilder, Dateien), die auf- und zuklappen. Die Unterzeilen tragen `data-eltern` und
 * folgen ihrer Hauptzeile nach jedem Sortieren (`tabelle:sortiert`, wie `Detailzeilen`); sie haben nur EINE Zelle,
 * die Sortierung stellt sie damit ans Ende, bevor sie zurückgehängt werden.
 *
 * WAS ANGEZEIGT WIRD („Zeige nur jede x-te Iteration", auch im laufenden Lauf einstellbar): jede Runde, deren Nummer
 * durch x teilbar ist — dazu immer die neueste und die beste. Nur die Anzeige: die Runden bleiben alle gespeichert,
 * Auswahl und „Gewählte löschen" gelten für das, was angezeigt wird. Gemerkt wird je Auftrag im Browser (wie
 * welche Runden aufgeklappt sind).
 *
 * Gebaut wird neu, wenn sich die Liste ändert (neue Runde, gelöscht, Filter) — die Auswahl bleibt dabei erhalten.
 */
export class Blendermodellrundentabelle {

    static KEY = 'blendermodell-iterationen';
    // Neuer Schlüssel: Die Karten der ersten Fassung (`<details>`) schrieben bei jedem Einfügen ein „offen" für die
    // neueste Runde — unter dem alten Schlüssel stünden Hunderte Runden als „aufgeklappt", die keiner geöffnet hat.
    static OFFEN = 'blendermodell.iterationen.details.';
    static JEDE = 'blendermodell.iterationen.jede.';

    /** @param seite `Blendermodellseite`, @param zeilen `Blendermodellrundenzeilen` */
    constructor(seite, zeilen) {
        this.seite = seite;
        this.zeilen = zeilen;
        const $ = id => document.getElementById(id);
        this.feld = $('iterationen');
        this.jedeFeld = $('iterationen-jede');
        this.zaehler = $('iterationen-angezeigt');
        this.loeschKnopf = $('iterationen-loeschen');
        this.loeschZahl = $('iterationen-loeschen-anzahl');
        this.meldung = $('iterationen-meldung');
        this.offen = this._lesen(Blendermodellrundentabelle.OFFEN + seite.jobId, {});
        this.jede = Math.max(1, Number(this._lesen(Blendermodellrundentabelle.JEDE + seite.jobId, 1)) || 1);
        this.gewaehlt = new Set();
        this.vorgemerkt = [];
        this.kinder = new Map();
        this.daten = new Map();
        this._stand = '';
        this.jedeFeld.value = String(this.jede);
        this.jedeFeld.addEventListener('input', () => this._jede());
        $('iterationen-alle-auf').addEventListener('click', () => this._alle(true));
        $('iterationen-alle-zu').addEventListener('click', () => this._alle(false));
        this.loeschKnopf.addEventListener('click', () => this.loeschen([...this.gewaehlt]));
    }

    // ---------------------------------------------------------------- Merken

    _lesen(schluessel, vorgabe) {
        try { return JSON.parse(localStorage.getItem(schluessel) ?? 'null') ?? vorgabe; } catch { return vorgabe; }
    }

    _schreiben(schluessel, wert) {
        try { localStorage.setItem(schluessel, JSON.stringify(wert)); } catch { /* stumm gewollt: nur Bequemlichkeit */ }
    }

    // ---------------------------------------------------------------- Filter

    /** Jede `jede`-te Runde (Nummer durch `jede` teilbar), dazu die neueste und die beste. `runden` aufsteigend. */
    static sichtbar(runden, jede, beste) {
        const n = Math.max(1, Math.floor(jede) || 1);
        const neueste = runden.length ? runden[runden.length - 1].runde : null;
        return runden.filter(r => n === 1 || r.runde % n === 0 || r.runde === neueste || r.runde === beste);
    }

    _jede() {
        const n = Math.min(100000, Math.max(1, Math.floor(Number(this.jedeFeld.value)) || 1));
        if (n === this.jede) return;
        this.jede = n;
        this._schreiben(Blendermodellrundentabelle.JEDE + this.seite.jobId, n);
        this.zeigen(this.seite.zustand);
    }

    // ---------------------------------------------------------------- Anzeige

    zeigen(z) {
        const e = z.ergebnis || {};
        const alle = [...(e.iterationen || [])].sort((a, b) => a.runde - b.runde);
        const beste = (e.kostuem || {}).runde_bester;
        const vorgemerkt = z.loeschen_vorgemerkt || [];
        // Das jüngste Modell (wie die Bühne): Ersatz für die neueste Runde ohne Modell; ein nachgebautes Modell ändert nur die Zahl.
        const mit = alle.filter(r => (r.dateien || {}).modell);
        const sichtbar = Blendermodellrundentabelle.sichtbar(alle, this.jede, beste);
        this.zaehler.textContent = this.jede > 1
            ? `${sichtbar.length} von ${alle.length} Runden angezeigt (jede ${this.jede}., dazu neueste und beste)`
            : `${alle.length} Runden`;
        const stand = [alle.length, alle.length ? alle[alle.length - 1].runde : '', beste, this.jede,
            sichtbar.map(r => r.runde).join(','), vorgemerkt.join(','), mit.length].join('|');
        if (stand === this._stand) return;
        this._stand = stand;
        this.vorgemerkt = vorgemerkt;
        this._bauen(sichtbar, beste, alle.length ? alle[alle.length - 1].runde : null, mit[mit.length - 1] || null);
    }

    _bauen(sichtbar, beste, neueste, juengstes) {
        this.kinder = new Map();
        this.daten = new Map(sichtbar.map(r => [r.runde, r]));
        this.zeilen.bilder.vergleichen(neueste, this.daten.get(beste) || null, juengstes);
        this._wahl = null;
        if (!sichtbar.length) {
            this.feld.replaceChildren(Blendermodellrundenzeilen.el('p', 'Noch keine Runde abgelegt.', 'hb-hinweis'));
            this._gewaehltGeaendert(0);
            return;
        }
        const wirt = document.createElement('div');
        wirt.innerHTML = dbTabelle({ key: Blendermodellrundentabelle.KEY, spalten: Blendermodellrundenzeilen.SPALTEN,
            zeilen: [], klasse: 'auftragstabelle blendermodell-rundentabelle' });
        const tabelle = wirt.querySelector('table');
        const rumpf = tabelle.tBodies[0];
        for (const r of sichtbar) {
            // Ohne gemerkten Stand ist nur die neueste Runde aufgeklappt.
            const offen = this.offen[r.runde] ?? (r.runde === neueste);
            rumpf.appendChild(this.zeilen.haupt(r, { beste: r.runde === beste, offen, geloescht: this.vorgemerkt.includes(r.runde) }));
            const unter = this.zeilen.unter(r, offen);
            this.kinder.set(String(r.runde), unter);
            for (const u of unter) {
                rumpf.appendChild(u);
                if (offen) this.zeilen.bilderFuellen(u, r);
            }
        }
        // VOR dem Binden: `tabellenBinden` wendet die gemerkte Sortierung an und meldet sie mit `tabelle:sortiert`.
        tabelle.addEventListener('tabelle:sortiert', () => this._nachziehen(tabelle));
        tabelle.addEventListener('click', ereignis => this._klick(ereignis));
        this.feld.replaceChildren(...wirt.childNodes);
        this._wahlBinden(tabelle);
        tabellenBinden(this.feld);
        this._nachziehen(tabelle);
    }

    /** Jede Unterzeile direkt hinter ihre Hauptzeile hängen. */
    _nachziehen(tabelle) {
        for (const tr of [...tabelle.tBodies[0].rows]) {
            if (tr.classList.contains('iter-unterzeile')) continue;
            let letzte = tr;
            for (const kind of this.kinder.get(tr.dataset.id) || []) {
                letzte.after(kind);
                letzte = kind;
            }
        }
    }

    // ---------------------------------------------------------------- Auswahl

    _wahlBinden(tabelle) {
        // `binden()` meldet schon einmal (mit leerer Auswahl) — die alte Auswahl vorher merken.
        const vorher = new Set(this.gewaehlt);
        this._wahl = new Zeilenwahl(tabelle, anzahl => this._gewaehltGeaendert(anzahl)).binden();
        // Eigenes Kopfkästchen: `Zeilenwahl` kennt nur `#select-all` (siehe `Blendermodellliste`).
        tabelle.querySelector('#iterationen-select-all')?.addEventListener('click', () => {
            const wahlbar = this._wahl.kaesten().filter(k => !k.disabled);
            const alleAn = wahlbar.length > 0 && wahlbar.every(k => k.checked);
            wahlbar.forEach(k => { k.checked = !alleAn; });
            this._wahl.nachziehen();
        });
        for (const kasten of this._wahl.kaesten()) kasten.checked = !kasten.disabled && vorher.has(Number(kasten.value));
        this._wahl.nachziehen();
    }

    _gewaehltGeaendert(anzahl) {
        this.gewaehlt = new Set(this._wahl ? this._wahl.kennungen().map(Number) : []);
        this.loeschZahl.textContent = String(anzahl);
        this.loeschKnopf.disabled = anzahl === 0;
        for (const [runde, kinder] of this.kinder) {
            const an = this.gewaehlt.has(Number(runde));
            kinder.forEach(k => k.classList.toggle('gewaehlt', an));
        }
        const kopf = document.getElementById('iterationen-select-all');
        if (kopf && this._wahl) {
            const stand = Zeilenwahl.kopfstand(anzahl, this._wahl.kaesten().filter(k => !k.disabled).length);
            kopf.checked = stand.checked;
            kopf.indeterminate = stand.indeterminate;
        }
    }

    // ---------------------------------------------------------------- Klicks

    _klick(ereignis) {
        const zeile = ereignis.target.closest('tr.iter-zeile');
        if (!zeile) return;
        const runde = Number(zeile.dataset.id);
        if (ereignis.target.closest('.iter-auf')) this._umschalten(runde);
        else if (ereignis.target.closest('.iter-loeschen')) this.loeschen([runde]);
        else if (ereignis.target.closest('img.iter-mini')) this.zeilen.bilder.oeffnen(this.daten.get(runde), 0);
    }

    _umschalten(runde, auf = null) {
        const kinder = this.kinder.get(String(runde)) || [];
        const neu = auf === null ? kinder.some(k => k.hidden) : auf;
        kinder.forEach(k => {
            k.hidden = !neu;
            if (neu) this.zeilen.bilderFuellen(k, this.daten.get(runde));
        });
        const knopf = this.feld.querySelector(`tr.iter-zeile[data-id="${runde}"] .iter-auf`);
        if (knopf) {
            knopf.textContent = neu ? '▾' : '▸';
            knopf.setAttribute('aria-expanded', String(neu));
        }
        this.offen[runde] = neu;
        this._schreiben(Blendermodellrundentabelle.OFFEN + this.seite.jobId, this.offen);
    }

    _alle(auf) {
        for (const runde of this.daten.keys()) this._umschalten(runde, auf);
    }

    // ---------------------------------------------------------------- Löschen

    _melden(text, fehler = false) {
        this.meldung.textContent = text;
        this.meldung.classList.toggle('hb-schlecht', fehler);
    }

    /** Runden löschen (einzeln oder viele). Ohne Lauf sofort, sonst vormerken: Der Lauf löscht sie zu Beginn seiner
     *  nächsten Runde (`Kostuemloeschung`) — solange steht die Zeile durchgestrichen da. */
    async loeschen(runden) {
        const schon = new Set(this.vorgemerkt);
        runden = runden.filter(n => !schon.has(n)).sort((a, b) => a - b);
        if (!runden.length) return;
        const liste = runden.length > 8 ? `${runden.slice(0, 8).join(', ')} …` : runden.join(', ');
        const was = runden.length === 1 ? `Runde ${liste}` : `${runden.length} Runden (${liste})`;
        if (!window.confirm(`${was} löschen?\n\nBilder, Modell-GLB und Dateien der Runde werden entfernt. `
            + 'Die Kurve und das beste Modell bleiben.')) return;
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('runden/loeschen/'), { runden });
            if (antwort.error) throw new Error(antwort.error);
            this._melden((antwort.geloescht || []).length
                ? `${antwort.geloescht.length} Runde(n) gelöscht.`
                : `${runden.length} Runde(n) vorgemerkt — der laufende Lauf löscht sie zu Beginn der nächsten Runde.`);
            runden.forEach(n => this.gewaehlt.delete(n));
            await this.seite.aktualisieren();
        } catch (fehler) {
            this._melden(`Löschen fehlgeschlagen: ${fehler.daten?.error || fehler.message}`, true);
        }
    }
}
