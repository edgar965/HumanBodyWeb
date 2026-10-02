/**
 * Engine2d3dKleideriterationen — der zweite Reiter der Auftragsseite: die Runden der Iterationen (30.09.2026).
 *
 * Kopie von `Blendermodelliterationen`: oben die Einstellungen der Iterationen (Runden, Kandidaten, Prüf-KI …, das Formular baut
 * `Engine2d3dKleiderseite`), „Weiter iterieren" (startet NUR den Schritt „iterationen", ab dem besten bisherigen Modell), die Kurve aller
 * Runden (`Engine2d3dKleiderverlauf`) und die Tabelle der Runden (`Engine2d3dKleiderrundentabelle`). Ohne den Vergleich „Vorlage und
 * Ergebnisvideo" aus BlenderModel — den schrieb dort ein Skript von Hand, keine Stelle der Anwendung.
 *
 * Den Zustand holt die Seite selbst im Takt (`Engine2d3dKleiderseite.verfolgen`) und ruft `zeigen`; dieses Modul hat keinen eigenen
 * Takt.
 */
import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Engine2d3dKleiderbildfenster } from './engine2d3dkleiderbildfenster.js';
import { Engine2d3dKleiderrundenbilder } from './engine2d3dkleiderrundenbilder.js';
import { Engine2d3dKleiderrundentabelle } from './engine2d3dkleiderrundentabelle.js';
import { Engine2d3dKleiderrundenzeilen } from './engine2d3dkleiderrundenzeilen.js';
import { Engine2d3dKleiderverlauf } from './engine2d3dkleiderverlauf.js';

export class Engine2d3dKleideriterationen {

    constructor(seite) {
        this.seite = seite;
        const $ = id => document.getElementById(id);
        this.anzahl = $('iterationen-anzahl');
        this.verlauf = $('iterationen-verlauf');
        this.weiter = $('iterationen-weiter');
        this.halt = $('iterationen-anhalten');
        this.stand = $('iterationen-stand');
        this.ki = $('iterationen-ki');
        const datei = name => seite.dateiAdresse('iterationen', name);
        const bilder = new Engine2d3dKleiderrundenbilder(datei, name => seite.fotoAdresse(name), new Engine2d3dKleiderbildfenster());
        this.tabelle = new Engine2d3dKleiderrundentabelle(seite, new Engine2d3dKleiderrundenzeilen(datei, bilder));
        this._stand = '';
        for (const knopf of document.querySelectorAll('#auftrag-reiter [data-reiter]')) {
            knopf.addEventListener('click', () => this.umschalten(knopf.dataset.reiter));
        }
        this.weiter.addEventListener('click', () => this.weiterIterieren());
        this.halt.addEventListener('click', () => this.seite.anhalten());
    }

    /** Nur den Schritt „iterationen" rechnen — mit den Einstellungen, die oben im Reiter stehen (schon gespeichert). */
    async weiterIterieren() {
        const beschriftung = this.weiter.querySelector('span');
        const text = beschriftung.textContent;
        try {
            await Knopfsperre.waehrend(this.weiter, async () => {
                if (!await this.seite.einstellungen.jetzt()) throw new Error('Einstellungen nicht gespeichert');
                const antwort = await Serverabruf.senden(this.seite.adresse('starten/'), { ab: 'iterationen', bis: 'iterationen' });
                if (antwort.error) throw new Error(antwort.error);
            }, 'Startet …');
        } catch (fehler) {
            this.stand.textContent = `Start fehlgeschlagen: ${fehler.daten?.error || fehler.message}`;
            this.weiter.disabled = false;
            return;
        } finally {
            // `Knopfsperre` lässt nach Erfolg den Ersatztext stehen; gesperrt bleibt der Knopf über `zeigen` (läuft).
            beschriftung.textContent = text;
        }
        this.seite.zustand.laeuft = true;
        this.seite.zustand.status = 'laeuft';
        this.seite.zeigen();
        this.seite.verfolgen();
    }

    umschalten(name) {
        for (const knopf of document.querySelectorAll('#auftrag-reiter [data-reiter]')) {
            knopf.setAttribute('aria-selected', String(knopf.dataset.reiter === name));
        }
        document.getElementById('reiter-auftrag').hidden = name !== 'auftrag';
        document.getElementById('reiter-iterationen').hidden = name !== 'iterationen';
        if (name === 'iterationen') this.seite.aktualisieren();
    }

    zeigen(z) {
        const e = z.ergebnis || {};
        const runden = e.iterationen || [];
        const kreislauf = e.kreislauf || {};
        const o = (z.optionen || {}).iterationen || {};
        this.anzahl.textContent = runden.length ? `(${runden.length})` : '';
        this.weiter.disabled = !!z.laeuft;
        this.halt.disabled = !z.laeuft;
        this.stand.textContent = z.laeuft ? `${z.progress || 0} % · ${z.progress_detail || ''}`
            : kreislauf.note ? `Bestes Modell: Runde ${kreislauf.runde_bester}, Abweichung `
                + `${Engine2d3dKleiderrundenzeilen.zahl(kreislauf.note.abweichung, 4)}` : '';
        this.ki.textContent = o.pruefki && o.pruefki !== 'aus'
            ? `Prüf-KI: ${o.pruefki}, alle ${o.pruefki_alle} Runden` : 'Prüf-KI: aus';
        const verlauf = kreislauf.verlauf || [];
        const stand = JSON.stringify([verlauf.length, verlauf[verlauf.length - 1]]);
        if (stand !== this._stand) {
            this._stand = stand;
            Engine2d3dKleiderverlauf.zeichnen(this.verlauf, kreislauf.verlauf);
        }
        this.tabelle.zeigen(z);
    }
}
