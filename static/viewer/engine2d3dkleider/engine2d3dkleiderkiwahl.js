import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderkiwahl — die Spalte „KI" der Liste von „2D3D Kleider": welche KI den Schritt „Netz" rechnet (03.10.2026).
 *
 * Jede Zeile trägt ein Auswahlfeld (`select.engine2d3dkleider-ki`, `data-id`): TRELLIS.2, Pixal3D, Pixal3D Mehrbild. Eine Änderung geht sofort als
 * Option `mesh.modell` an `/api/engine2d3dkleider/<id>/einstellungen/` — dieselbe Option wie das Feld „Modell" der Karte „Mesh" auf der Auftragsseite,
 * gerechnet wird erst beim nächsten Lauf. Läuft der Auftrag, lehnt der Server mit 409 ab (die Zeile ist dann ohnehin gesperrt); jeder Fehler setzt das Feld
 * auf den alten Wert zurück: Ein stehen gebliebener neuer Wert würde etwas behaupten, was der Server nicht hat.
 */
export class Engine2d3dKleiderkiwahl {

    static ADRESSE = id => `/api/engine2d3dkleider/${id}/einstellungen/`;

    /** Hört auf die Auswahlfelder der Tabelle (Ereignisdelegation: die Zeilen entstehen auch neu, wenn die Liste sich aktualisiert). */
    static binden(tabelle) {
        tabelle.addEventListener('change', e => {
            const feld = e.target.closest('select.engine2d3dkleider-ki');
            if (feld) Engine2d3dKleiderkiwahl.speichern(feld);
        });
    }

    static async speichern(feld) {
        const vorher = feld.dataset.vorher || '';
        feld.disabled = true;
        try {
            const antwort = await Serverabruf.senden(Engine2d3dKleiderkiwahl.ADRESSE(feld.dataset.id), { optionen: { mesh: { modell: feld.value } } });
            if (antwort.error) throw new Error(antwort.error);
            if (antwort.optionen?.mesh?.modell !== feld.value) throw new Error('Der Server hat einen anderen Wert gespeichert');
            feld.dataset.vorher = feld.value;
            feld.closest('td')?.setAttribute('data-sort', feld.value);
            feld.title = feld.options[feld.selectedIndex]?.title || feld.title;
        } catch (fehler) {
            if (vorher) feld.value = vorher;
            window.alert(`KI konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
        } finally {
            feld.disabled = false;
        }
    }
}
