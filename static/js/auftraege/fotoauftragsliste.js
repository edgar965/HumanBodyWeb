import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';

/**
 * Fotoauftragsliste — die Liste der Fotoanalysen: Häkchen, Massenlöschen und
 * das Löschen einer Zeile.
 *
 * Herausgeloest aus templates/photo_analysis_jobs.html (Umbau 16.08.2026):
 * `toggleAll`, `updateSelection`, `deleteJob` und `bulkDelete` standen dort
 * inline mit 12 `var` und dem CSRF-Token als Django-Variable mitten im
 * JavaScript.
 *
 * Die Loeschadresse einer Zeile steht als `data-loeschen` im Knopf — vorher
 * wurde sie mit zwei Argumenten in ein `onclick` geschrieben und musste dort
 * durch `escapejs` gehen.
 */
export class Fotoauftragsliste {

    static aufbauen(massenadresse) {
        return new Fotoauftragsliste(massenadresse).aufbauen();
    }

    constructor(massenadresse) {
        this.massenadresse = massenadresse;
    }

    aufbauen() {
        document.getElementById('select-all')
            ?.addEventListener('click', ereignis => this.alle(ereignis.target));
        document.querySelectorAll('.job-cb').forEach(kaestchen => {
            kaestchen.addEventListener('click', () => this.auswahlstand());
        });
        document.querySelectorAll('[data-loeschen]').forEach(knopf => {
            knopf.addEventListener('click', ereignis => {
                ereignis.preventDefault();
                this.loeschen(knopf.dataset.loeschen, knopf.dataset.name || '');
            });
        });
        document.getElementById('bulk-delete-btn')
            ?.addEventListener('click', () => this.massenloeschen());
        this.auswahlstand();
        return this;
    }

    alle(hauptfeld) {
        document.querySelectorAll('.job-cb').forEach(kaestchen => {
            kaestchen.checked = hauptfeld.checked;
        });
        this.auswahlstand();
    }

    /** Leiste ein-/ausblenden und das Hauptkästchen auf Teilauswahl stellen. */
    auswahlstand() {
        const alle = document.querySelectorAll('.job-cb');
        const gewaehlt = document.querySelectorAll('.job-cb:checked');
        const leiste = document.getElementById('bulk-actions');
        leiste?.classList.toggle('has-selection', gewaehlt.length > 0);
        const zaehler = document.getElementById('selection-count');
        if (zaehler && gewaehlt.length) {
            zaehler.textContent = `${gewaehlt.length} von ${alle.length} ausgewählt`;
        }
        const hauptfeld = document.getElementById('select-all');
        if (!hauptfeld) return;
        hauptfeld.checked = gewaehlt.length === alle.length && alle.length > 0;
        hauptfeld.indeterminate = gewaehlt.length > 0
                                  && gewaehlt.length < alle.length;
    }

    async loeschen(adresse, name) {
        if (!confirm(`Auftrag löschen: ${name}?`)) return;
        try {
            await Serverabruf.senden(adresse, {});
            location.reload();
        } catch (fehler) {
            alert('Löschen fehlgeschlagen: ' + fehler.message);
        }
    }

    async massenloeschen() {
        const kennungen = [...document.querySelectorAll('.job-cb:checked')]
            .map(feld => feld.dataset.jobId);
        if (!kennungen.length) return;
        if (!confirm(`${kennungen.length} Auftrag/Aufträge endgültig löschen?`)) {
            return;
        }
        try {
            const daten = await Serverabruf.senden(this.massenadresse,
                                                   { ids: kennungen });
            if (!daten.ok) throw new Error(daten.error || 'Unbekannter Fehler');
            location.reload();
        } catch (fehler) {
            alert('Löschen fehlgeschlagen: ' + fehler.message);
        }
    }
}
