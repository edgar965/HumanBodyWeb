import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';

/**
 * Gcstueckeknopf — Knopf „Neu backen" auf /settings/kleider/: startet den
 * GC-Stapellauf (`manage.py gcstuecke_fortschritt`, Dienst `Gcstueckelauf`)
 * und zeigt seinen Fortschritt, bis er fertig ist.
 *
 * WARUM (Edgar, 26.09.2026: „die müssten neu gebacken werden, da die
 * Drapierung von Garment Code anders ist ... mach mit auf /settings/kleider/
 * einen Button, mit dem diese per script neu gebacken werden können"): Die
 * 171 GarmentCode-Stücke liefen bisher nur über die Konsole (`manage.py
 * gcstuecke`). Ein Lauf ohne `--neu` baut von selbst nur, was veraltet ist —
 * seit die Bauart-Einstellung oben in den Fingerabdruck jedes Stücks
 * einfließt, betrifft das einen Großteil des Bestands.
 */
export class Gcstueckeknopf {

    static TAKT_MS = 3000;

    static aufbauen() {
        const knopf = document.getElementById('gcstuecke-start');
        if (!knopf) return null;
        return new Gcstueckeknopf(knopf).aufbauen();
    }

    constructor(knopf) {
        this.knopf = knopf;
        this.neuKaestchen = document.getElementById('gcstuecke-neu');
        this.zeile = document.getElementById('gcstuecke-zeile');
        this.fuellung = document.getElementById('gcstuecke-balken');
    }

    aufbauen() {
        this.knopf.addEventListener('click', () => this.starten());
        this._nachfragen();
        return this;
    }

    async starten() {
        const neu = this.neuKaestchen?.checked || false;
        const hinweis = neu
            ? 'Baut ALLE ~171 Stücke neu, auch unveränderte — das dauert Stunden.'
            : 'Baut jedes veraltete Stück neu — je Stück ~20–45 s.';
        if (!confirm(hinweis + ' Läuft auf der GPU und blockiert die Grafikkarte. Jetzt starten?')) {
            return;
        }
        this.knopf.disabled = true;
        this._text('Startet …');
        try {
            const antwort = await Serverabruf.senden('/api/kleider/gcstuecke/starten/', { neu });
            if (antwort?.fehler) {
                this._text('Nicht gestartet: ' + antwort.fehler);
                this.knopf.disabled = false;
                return;
            }
            setTimeout(() => this._nachfragen(), Gcstueckeknopf.TAKT_MS);
        } catch (fehler) {
            this._text('Nicht gestartet: ' + fehler.message);
            this.knopf.disabled = false;
        }
    }

    async _nachfragen() {
        let daten;
        try {
            daten = await Serverabruf.json('/api/kleider/gcstuecke/stand/');
        } catch (fehler) {
            setTimeout(() => this._nachfragen(), Gcstueckeknopf.TAKT_MS);
            return;
        }
        this._anzeigen(daten);
        if (daten.gestartet && !daten.fertig) {
            this.knopf.disabled = true;
            setTimeout(() => this._nachfragen(), Gcstueckeknopf.TAKT_MS);
        } else {
            this.knopf.disabled = false;
        }
    }

    _anzeigen(daten) {
        if (!daten.gestartet) { this._text(''); this._fuellen(0); return; }
        const gesamt = daten.gesamt || 0;
        this._fuellen(gesamt ? Math.round((daten.geschafft / gesamt) * 100) : 0);
        if (daten.fehler) {
            this._text('Fehler: ' + daten.fehler);
        } else if (daten.fertig) {
            this._text(`Fertig — gebaut ${daten.gebaut ?? 0}, übersprungen ${daten.uebersprungen ?? 0}, `
                + `Fehler ${daten.fehlerliste?.length || 0}.`);
        } else {
            this._text(`${daten.geschafft}/${gesamt} — ${daten.zeile || ''}`);
        }
    }

    _text(wert) { if (this.zeile) this.zeile.textContent = wert; }
    _fuellen(prozent) { if (this.fuellung) this.fuellung.style.width = prozent + '%'; }
}
