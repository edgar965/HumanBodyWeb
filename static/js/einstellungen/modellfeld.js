/**
 * Modellfeld — fuellt ein <select> mit den Modell-Vorgaben aus
 * /api/character/models/.
 *
 * Umbau 16.08.2026 (Anforderung 6, keine doppelten Funktionen): derselbe
 * fetch-Block stand fuenfmal in den Einstellungsvorlagen — zweimal in
 * settings_model.html, je einmal in settings_result.html und zweimal in
 * settings_scene.html (Standardmodell + Kleider-Knochenmodell). Vier davon
 * loggten bei Fehlern, eine schrieb "Fehler beim Laden" ins Feld; sonst waren
 * sie identisch.
 *
 * Die Liste wird je Seitenaufruf einmal geholt und geteilt: mehrere Felder auf
 * derselben Seite loesen sonst mehrere gleiche Abfragen aus.
 */
import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';

export class Modellfeld {

    static ENDPUNKT = '/api/character/models/';
    static _laufend = null;

    /** Vorgabenliste holen — je Seitenaufruf nur eine Abfrage. */
    static async vorgaben() {
        if (!Modellfeld._laufend) {
            Modellfeld._laufend = Serverabruf
                .json(`${Modellfeld.ENDPUNKT}?t=${Date.now()}`)
                .then(daten => daten.presets || []);
        }
        return Modellfeld._laufend;
    }

    /**
     * @param {string} feldId   id des <select>
     * @param {string} aktuell  vorausgewaehlter Modellname
     * @param {{leerText?: string}} optionen  leerText setzt einen
     *        "(nichts gewaehlt)"-Eintrag an den Anfang.
     */
    static async fuellen(feldId, aktuell, optionen = {}) {
        const feld = document.getElementById(feldId);
        if (!feld) return null;
        try {
            const vorgaben = await Modellfeld.vorgaben();
            feld.innerHTML = '';
            if (optionen.leerText) {
                feld.appendChild(Modellfeld._eintrag('', optionen.leerText, false));
            }
            vorgaben.forEach(vorgabe => {
                feld.appendChild(Modellfeld._eintrag(
                    vorgabe.name, vorgabe.label || vorgabe.name, vorgabe.name === aktuell));
            });
            // Stand der Dinge sichern: ist der gespeicherte Name nicht mehr in
            // der Liste, waere das Feld sonst stumm auf den ersten Eintrag
            // gesprungen und der naechste Speichern-Klick haette ihn ersetzt.
            if (aktuell && feld.value !== aktuell) feld.value = aktuell;
            return feld;
        } catch (fehler) {
            feld.innerHTML = '<option value="">Fehler beim Laden</option>';
            console.warn('Modell-Vorgaben nicht ladbar:', fehler);
            return feld;
        }
    }

    static _eintrag(wert, beschriftung, gewaehlt) {
        const option = document.createElement('option');
        option.value = wert;
        option.textContent = beschriftung;
        option.selected = gewaehlt;
        return option;
    }
}
