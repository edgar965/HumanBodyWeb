/**
 * Kleiderfelder — die vier MakeHuman-Vorgabefelder der Szenen-Einstellungen.
 *
 * Herausgeloest aus settings_scene.html (Umbau 16.08.2026). Der Block war mit
 * 33 Zeilen der laengste Inline-Teil der Vorlage und mischte Datenholen,
 * Gruppieren und DOM-Bau in einer Schleife.
 *
 * Die Bibliothek kommt als {Kategorie: [Kleid, …]}; im Auswahlfeld wird daraus
 * je Kategorie ein <optgroup>.
 */
import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
export class Kleiderfelder {

    static ENDPUNKT = '/api/character/garment/library/';
    static LEER_TEXT = '(Kein Asset)';

    /**
     * @param {string[]} feldIds  ids der Auswahlfelder
     * @param {string[]} gewaehlt gespeicherte Kleid-Kennung je Feld
     */
    static async fuellen(feldIds, gewaehlt) {
        try {
            const daten = await Serverabruf.json(`${Kleiderfelder.ENDPUNKT}?t=${Date.now()}`);
            const nachKategorie = daten.garments || {};
            feldIds.forEach((feldId, nummer) => {
                const feld = document.getElementById(feldId);
                if (feld) Kleiderfelder._eintragen(feld, nachKategorie, gewaehlt[nummer]);
            });
        } catch (fehler) {
            console.warn('Kleider-Bibliothek nicht ladbar:', fehler);
        }
    }

    static _eintragen(feld, nachKategorie, gewaehlt) {
        feld.innerHTML = '';
        feld.appendChild(new Option(Kleiderfelder.LEER_TEXT, ''));
        Object.keys(nachKategorie).sort().forEach(kategorie => {
            const gruppe = document.createElement('optgroup');
            gruppe.label = kategorie.charAt(0).toUpperCase() + kategorie.slice(1);
            (nachKategorie[kategorie] || []).forEach(kleid => {
                const eintrag = new Option(kleid.name || kleid.id, kleid.id);
                eintrag.selected = kleid.id === gewaehlt;
                gruppe.appendChild(eintrag);
            });
            feld.appendChild(gruppe);
        });
    }
}
