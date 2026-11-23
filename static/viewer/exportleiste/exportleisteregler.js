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
        this._gesperrt = false;
        /** Behälter einer zugeklappten Gruppe → {katalog, werte}, bis sie das erste Mal aufgeht */
        this._offen = new Map();
        this._uhr = null;
        this.feld.addEventListener('change', () => this._bald(0));
        this.feld.addEventListener('input', e => { if (e.target.matches('input[type="text"], input[type="number"]')) this._bald(); });
    }

    /**
     * Einmal bauen — danach gehören die Felder dem Nutzer (ein Neubau je Takt nähme ihm die Eingabe weg). Die Felder einer Gruppe entstehen erst, wenn sie aufgeht (24.11.2026,
     * Edgar „fixe“ — Block ohne Skript beim Laden der Foto-Genesis-Testseite): Chrome-Spur über ETW, iphone_mit_lidar_dycheck_space_out — 240,6 ms tastete die Erweiterung
     * „iCloud-Passwörter“ (Apples Formularerkennung, Metadaten je Eingabefeld) die Seite ab, 426 der 495 Felder standen in den zugeklappten Gruppen hier.
     */
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
            this._offen.set(behaelter, { katalog, werte: (z.optionen || {})[gruppe] || {} });
            klappe.addEventListener('toggle', () => { if (klappe.open) this._bauen(behaelter); });
        }
        this._gebaut = true;
    }

    _bauen(behaelter) {
        const offen = this._offen.get(behaelter);
        if (!offen) return;
        this._offen.delete(behaelter);
        // Hover-Hilfe und Wertebereich je Regler (19.11.2026, Edgar: „bei dem Render fenster mach eine Hilfe (Hover) und range … für jede einstellung“)
        Meshoptionenformular.bauen(behaelter, offen.katalog, offen.werte, { hilfe: true });
        if (this._gesperrt) this.sperren(true);
    }

    sperren(gesperrt) {
        this._gesperrt = gesperrt;
        for (const eingabe of this.feld.querySelectorAll('input, select, textarea')) eingabe.disabled = gesperrt;
    }

    /** Die Werte aller Gruppen; eine noch zugeklappte wird dafür gebaut — gelesen wird wie bisher aus den Feldern (Vorgaben und Umrechnung des Formulars). */
    optionen() {
        const aus = {};
        for (const behaelter of this.feld.querySelectorAll('[data-gruppe]')) {
            this._bauen(behaelter);
            aus[behaelter.dataset.gruppe] = Meshoptionenformular.lesen(behaelter);
        }
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
