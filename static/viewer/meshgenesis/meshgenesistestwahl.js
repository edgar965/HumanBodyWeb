/**
 * Meshgenesistestwahl — die Häkchen „Haut-KI“ und „Keine Kleider“ auf der Seite eines Tests ohne Job
 * (`[data-wahl]` in `meshgenesis_test.html`, 06.11.2026). Jede Änderung speichert sofort in `einstellung.json`
 * (`Meshgenesistestwahl`); die Kette liest sie beim nächsten Rechnen. Tests eines Jobs haben keine Häkchen.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Meshgenesistestwahl {
    static binden(wurzel) {
        if (!wurzel) return;
        const kennung = wurzel.dataset.kennung;
        for (const haken of wurzel.querySelectorAll('input[data-wahl]')) {
            haken.addEventListener('change', () => Meshgenesistestwahl._speichern(kennung, haken));
        }
    }

    static async _speichern(kennung, haken) {
        haken.disabled = true;
        try {
            await Serverabruf.senden(`/api/meshgenesis/test/${encodeURIComponent(kennung)}/wahl/`, { name: haken.dataset.wahl, wert: haken.checked });
        } catch (fehler) {
            haken.checked = !haken.checked;
            alert(`Nicht gespeichert: ${fehler.message}`);
        } finally {
            haken.disabled = false;
        }
    }
}
