/**
 * Auftragduplizieren — der Knopf „Job duplizieren" über den drei Joblisten (28.09.2026).
 *
 * Edgar: „mach mir einen Button bei der Jobtabelle aller tabs: Job Duplizieren, das dupliziert
 * mir alle Eingabedateien und Parameter, nicht aber die Ausgabe". Dupliziert werden die
 * angehakten Zeilen (dieselbe `Zeilenwahl` wie „Gewählte löschen"); was kopiert wird, entscheidet
 * der Server (`core/dienste/auftragsduplikat.py`). Die Kopien starten nicht von selbst — nach dem
 * Duplizieren lädt die Seite neu, dann stehen sie als „Angelegt" in der Tabelle.
 */
import { Knopfsperre } from './knopfsperre.js';
import { Serverabruf } from './serverabruf.js';

export class Auftragduplizieren {

    /**
     * @param {string} bereich `bildmodell` | `mesh` | `meshfigur` (der `key` der Tabelle)
     * @param {string} knopfId  Knopf im Listenkopf
     * @param {string} zaehlerId Zahl der gewählten Zeilen im Knopf
     * @param {object} wahl Die `Zeilenwahl` der Tabelle (liefert `kennungen()`)
     */
    constructor(bereich, knopfId, zaehlerId, wahl) {
        this.bereich = bereich;
        this.knopf = document.getElementById(knopfId);
        this.zaehler = document.getElementById(zaehlerId);
        this.wahl = wahl;
        if (!this.knopf) {
            console.warn(`Auftragduplizieren: Knopf #${knopfId} fehlt — Duplizieren (${bereich}) nicht verfügbar`);
            return;
        }
        this.knopf.addEventListener('click', () => this.duplizieren());
    }

    /** Aufruf aus dem Rückruf der `Zeilenwahl`: Knopf nur mit Auswahl frei. */
    anzeigen(anzahl) {
        if (this.knopf) this.knopf.disabled = anzahl === 0;
        if (this.zaehler) this.zaehler.textContent = String(anzahl);
    }

    async duplizieren() {
        const ids = this.wahl?.kennungen() || [];
        if (!ids.length) return;
        try {
            // Ohne Ersatztext: `Knopfsperre` schriebe ihn in die äußere Hülle und nähme dabei den
            // Zähler (`<span id=…-count>`) mit — nach einem Fehlschlag zählte der Knopf nicht mehr.
            await Knopfsperre.waehrend(this.knopf, async () => {
                const antwort = await Serverabruf.senden(`/api/modell-aus-dateien/${this.bereich}/duplizieren/`, { ids });
                if (antwort.error) throw new Error(antwort.error);
                window.location.reload();
            });
        } catch (fehler) {
            window.alert(`Duplizieren fehlgeschlagen: ${fehler.daten?.error || fehler.message}`);
        }
    }
}
