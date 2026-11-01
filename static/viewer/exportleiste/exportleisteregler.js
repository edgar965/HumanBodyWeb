import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';

/**
 * Exportleisteregler — die Regler für Rendering und Physik der Exportleiste (31.10.2026): fünf Gruppen aus `Figurfilm.Filmregler` (Qualität, Licht, Haut, Physik, Mimik), Katalog
 * und Werte im Zustand, je Gruppe ein zugeklapptes `<details>` mit den Feldern von `Meshoptionenformular` — wie bei „2D3D Kleider". Jede Änderung geht sofort an
 * `…/einstellungen/` (Auswahl sofort, Text und Zahlen `WARTEN_MS` nach dem letzten Tastendruck); der Render liest sie dort.
 */
export class Exportleisteregler {

    static WARTEN_MS = 700;

    constructor(leiste) {
        this.leiste = leiste;
        this.feld = leiste.wurzel.querySelector('#exportleiste-regler');
        this.meldung = leiste.wurzel.querySelector('#exportleiste-regler-meldung');
        this._gebaut = false;
        this._uhr = null;
        this.feld.addEventListener('change', () => this._bald(0));
        this.feld.addEventListener('input', e => { if (e.target.matches('input[type="text"], input[type="number"]')) this._bald(); });
    }

    /** Einmal bauen — danach gehören die Felder dem Nutzer (ein Neubau je Takt nähme ihm die Eingabe weg). */
    zeigen(z) {
        if (this._gebaut || !z.katalog) return;
        for (const [gruppe, katalog] of Object.entries(z.katalog)) {
            const klappe = document.createElement('details');
            klappe.className = 'exportleiste-reglergruppe';
            const titel = document.createElement('summary');
            titel.textContent = katalog.titel || gruppe;
            const behaelter = document.createElement('div');
            behaelter.className = 'mesh-optionen';
            behaelter.dataset.gruppe = gruppe;
            klappe.append(titel, behaelter);
            this.feld.appendChild(klappe);
            Meshoptionenformular.bauen(behaelter, katalog, (z.optionen || {})[gruppe] || {});
        }
        this._gebaut = true;
    }

    sperren(gesperrt) {
        for (const eingabe of this.feld.querySelectorAll('input, select, textarea')) eingabe.disabled = gesperrt;
    }

    optionen() {
        const aus = {};
        for (const behaelter of this.feld.querySelectorAll('[data-gruppe]')) aus[behaelter.dataset.gruppe] = Meshoptionenformular.lesen(behaelter);
        return aus;
    }

    _bald(ms = Exportleisteregler.WARTEN_MS) {
        clearTimeout(this._uhr);
        this._uhr = setTimeout(() => this.speichern(), ms);
    }

    /** Sofort speichern (vor „Rendern") — true, wenn gespeichert. */
    async speichern() {
        clearTimeout(this._uhr);
        try {
            const antwort = await Serverabruf.senden(this.leiste.adresse('einstellungen/'), { optionen: this.optionen() });
            if (antwort.error) throw new Error(antwort.error);
            if (this.leiste.zustand) this.leiste.zustand.optionen = antwort.optionen;
            this.meldung.textContent = `Regler gespeichert ${new Date().toLocaleTimeString('de-DE')}.`;
            this.meldung.classList.remove('hb-schlecht');
            return true;
        } catch (fehler) {
            this.meldung.textContent = `Regler nicht gespeichert: ${fehler.daten?.error || fehler.message}`;
            this.meldung.classList.add('hb-schlecht');
            return false;
        }
    }
}
