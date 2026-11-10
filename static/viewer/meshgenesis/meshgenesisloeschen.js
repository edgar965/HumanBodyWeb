/**
 * Meshgenesisloeschen — Auswahl und „Gewählte löschen“ je Tabelle auf `/mesh-genesis/` (23.10.2026, Edgar: „mach bei den Jobs die Auswahl-Checkboxen und dann die Buttons zum Löschen“, Reiter Jobs und Test).
 * Eine Instanz je Karte mit `[data-loeschen="jobs|tests"]`: Kästchen `.meshgenesis-wahl` je Zeile, `.meshgenesis-alle` im Kopf, Knopf mit Zähler. Gelöscht wird über `POST /api/meshgenesis/loeschen/`
 * (`Meshgenesispapierkorb`: der Ordner wird nach `3DObjects/meshgenesis/_beiseite/<Zeit>_geloescht/` verschoben, nicht gelöscht). Ein Klick in die Zelle des Kästchens hakt an, statt die Seite zu öffnen.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Meshgenesisloeschen {
    static aufbauen() {
        return [...document.querySelectorAll('[data-loeschen]')].map(feld => new Meshgenesisloeschen(feld));
    }

    constructor(feld) {
        this.feld = feld;
        this.art = feld.dataset.loeschen;
        this.knopf = feld.querySelector('[data-aktion="loeschen"]');
        this.alle = feld.querySelector('.meshgenesis-alle');
        feld.addEventListener('click', e => this._klick(e), true);
        feld.addEventListener('change', () => this.zaehlen());
        this.alle?.addEventListener('change', () => {
            for (const k of this.kaesten()) k.checked = this.alle.checked;
            this.zaehlen();
        });
        this.knopf?.addEventListener('click', () => this.loeschen());
        window.addEventListener('pageshow', () => this.zaehlen());     // Chrome stellt Haken beim Zurückkehren ohne Ereignis wieder her
        this.zaehlen();
    }

    kaesten() { return [...this.feld.querySelectorAll('input.meshgenesis-wahl')]; }
    gewaehlt() { return this.kaesten().filter(k => k.checked).map(k => k.dataset.id); }

    _klick(e) {
        const zelle = e.target.closest('td.meshgenesis-wahlzelle');
        if (!zelle) return;
        e.stopPropagation();                                            // die Zeile öffnet sonst die Seite des Jobs
        if (e.target.matches('input')) return;
        const k = zelle.querySelector('input.meshgenesis-wahl');
        k.checked = !k.checked;
        this.zaehlen();
    }

    zaehlen() {
        const n = this.gewaehlt().length;
        if (this.knopf) {
            this.knopf.querySelector('.meshgenesis-zaehler').textContent = String(n);
            this.knopf.disabled = n === 0;
        }
        const alle = this.kaesten().length;
        if (this.alle) {
            this.alle.checked = alle > 0 && n === alle;
            this.alle.indeterminate = n > 0 && n < alle;
        }
    }

    async loeschen() {
        const ids = this.gewaehlt();
        if (!ids.length) return;
        const was = this.art === 'jobs' ? 'Jobs' : 'Tests';
        if (!window.confirm(`${ids.length} ${was} löschen?\n\n${ids.join(', ')}\n\nDie Ordner werden nach 3DObjects/meshgenesis/_beiseite/<Zeit>_geloescht/ verschoben (nicht endgültig gelöscht).`)) return;
        this.knopf.disabled = true;
        try {
            const antwort = await Serverabruf.senden('/api/meshgenesis/loeschen/', { art: this.art, ids });
            const fehler = (antwort.ergebnis || []).filter(e => !e.ok);
            if (fehler.length) window.alert(`Nicht gelöscht:\n${fehler.map(e => `${e.kennung}: ${e.fehler}`).join('\n')}`);
        } catch (fehler) {
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
        window.location.reload();
    }
}
