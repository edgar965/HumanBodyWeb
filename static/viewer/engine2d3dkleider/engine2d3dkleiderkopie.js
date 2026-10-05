import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderkopie — der Knopf „Kopie mit allen Daten" über der Auftragsliste von „2D3D Kleider" (05.10.2026).
 *
 * Edgar: „mach zwei Copy-Job-Optionen … Einmal MIT allen Daten, Modellen, usw. und Ausgaben, einmal ohne." Die ohne Daten ist der Knopf daneben
 * (`Auftragduplizieren`: Fotos und Einstellungen); diese kopiert den ganzen Auftrag (`Engine2d3dKleiderauftragskopie`, Umfang „alles") in einen
 * neuen Auftrag. Kopiert werden die angehakten Zeilen (dieselbe `Zeilenwahl` wie beim Löschen). Die Kopie startet nichts; danach lädt die Seite neu.
 */
export class Engine2d3dKleiderkopie {

    static ADRESSE = '/api/engine2d3dkleider/kopieren/';

    /**
     * @param {object} wahl Die `Zeilenwahl` der Tabelle (liefert `kennungen()`)
     * @param {string} knopfId Knopf im Listenkopf
     * @param {string} zaehlerId Zahl der gewählten Zeilen im Knopf
     */
    constructor(wahl, knopfId = 'engine2d3dkleider-kopie-alles', zaehlerId = 'engine2d3dkleider-kopie-alles-count') {
        this.wahl = wahl;
        this.knopf = document.getElementById(knopfId);
        this.zaehler = document.getElementById(zaehlerId);
        if (!this.knopf) {
            console.warn(`Engine2d3dKleiderkopie: Knopf #${knopfId} fehlt — „Kopie mit allen Daten" nicht verfügbar`);
            return;
        }
        this.knopf.addEventListener('click', () => this.kopieren());
    }

    /** Aufruf aus dem Rückruf der `Zeilenwahl`: Knopf nur mit Auswahl frei. */
    anzeigen(anzahl) {
        if (this.knopf) this.knopf.disabled = anzahl === 0;
        if (this.zaehler) this.zaehler.textContent = String(anzahl);
    }

    async kopieren() {
        const ids = this.wahl?.kennungen() || [];
        if (!ids.length) return;
        if (!window.confirm(`${ids.length} Auftrag/Aufträge mit allen Daten kopieren (Fotos, Netz, Figur, Runden, Renderläufe, Modelle)? Das kopiert den ganzen Ordner und kann etwas dauern.`)) return;
        let teilweise = false;
        try {
            // Ohne Ersatztext: `Knopfsperre` schriebe ihn in die äußere Hülle und nähme den Zähler mit (wie bei `Auftragduplizieren`).
            await Knopfsperre.waehrend(this.knopf, async () => {
                const antwort = await Serverabruf.senden(Engine2d3dKleiderkopie.ADRESSE, { ids });
                if (antwort.error) throw new Error(antwort.error);
                window.location.reload();
            });
        } catch (fehler) {
            teilweise = (fehler.daten?.kopiert || 0) > 0;
            window.alert(`Kopieren fehlgeschlagen: ${fehler.daten?.error || fehler.message}${teilweise ? ` (${fehler.daten.kopiert} Kopie(n) sind schon angelegt)` : ''}`);
            if (teilweise) window.location.reload();
        }
    }
}
