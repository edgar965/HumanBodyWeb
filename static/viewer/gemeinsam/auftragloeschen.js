/**
 * Auftragloeschen — der „Auftrag löschen"-Knopf auf einer Auftragsseite (27.09.2026).
 *
 * Edgar: „mach bei jeden Job einen löschen button … dann soll das auch aus der Jobliste
 * gelöscht sein". Die Endpunkte gab es längst (je Bereich ein
 * `POST /api/<bereich>/<id>/loeschen/`, dieselbe Funktion, die der Löschknopf ÜBER der
 * Liste für mehrere Aufträge nutzt) — es fehlte nur der Knopf auf der Seite selbst.
 * Der Endpunkt entfernt Ordner UND Datenbankeintrag; danach ist der Auftrag deshalb
 * auch aus der Liste verschwunden, ohne dass hier etwas nachgezogen werden müsste.
 *
 * Alles Bereichsspezifische steht als `data-`Attribut am Knopf, damit dieselbe Klasse
 * für „Modell aus Bildern", „Mesh" und „Mesh to 3D" reicht:
 *   data-adresse  Endpunkt (Pflicht)
 *   data-ziel     wohin nach dem Löschen (Vorgabe: die Übersicht)
 *   data-frage    Text der Sicherheitsabfrage
 *
 * Ein Löschen ist nicht umkehrbar, deshalb IMMER eine Rückfrage — und der Knopf bleibt
 * bis zur Antwort des Servers gesperrt, damit ein zweiter Klick nicht in einen 404 läuft.
 */
import { Serverabruf } from './serverabruf.js';

export class Auftragloeschen {

    static KNOPF = 'auftrag-loeschen';
    static ZIEL = '/modell-aus-dateien/';
    static FRAGE = 'Diesen Auftrag mit allen Dateien löschen? Das lässt sich nicht rückgängig machen.';

    /** Bindet den Knopf, falls die Seite einen hat. */
    static binden(id = Auftragloeschen.KNOPF) {
        const knopf = document.getElementById(id);
        if (!knopf) return null;
        knopf.addEventListener('click', () => Auftragloeschen.ausfuehren(knopf));
        return knopf;
    }

    static async ausfuehren(knopf) {
        const adresse = knopf.dataset.adresse;
        if (!adresse) return;
        if (!window.confirm(knopf.dataset.frage || Auftragloeschen.FRAGE)) return;
        knopf.disabled = true;
        try {
            const antwort = await Serverabruf.senden(adresse, {});
            if (antwort && antwort.error) throw new Error(antwort.error);
            window.location.href = knopf.dataset.ziel || Auftragloeschen.ZIEL;
        } catch (fehler) {
            knopf.disabled = false;
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
        }
    }
}
