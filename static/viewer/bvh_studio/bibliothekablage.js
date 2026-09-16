import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Clipfehlt } from './clipfehlt.js';
import { Bibliothekskanal } from '../gemeinsam/bibliothekskanal.js';

/**
 * Bibliothekablage — Dateioperationen auf der BVH-Bibliothek.
 *
 * Herausgelöst aus `library.js` (329 Zeilen): Umbenennen, Kopieren,
 * Verschieben, Löschen, Ordner anlegen — alles über EINEN Endpunkt
 * (`/api/character/bvh-manage/`) mit einem `action`-Feld.
 *
 * WARUM `Serverabruf.senden` UND NICHT `fetch`
 * ===========================================
 * Frühere Reihenfolge war `resp.json()` vor `resp.ok`. Bei einer Fehlerseite
 * scheiterte schon das Auslesen — der Hinweis mit der Servermeldung kam nie an,
 * stattdessen stand „Unexpected token '<'" im Fenster.
 *
 * WAS BEIM LÖSCHEN MITGEHT
 * ========================
 * `clipsEntfernen` räumt die Zeitleiste auf. Eine gelöschte BVH, deren Clip
 * stehen bleibt, ist der übelste Fall: Der Clip zeigt weiter Bewegung an, beim
 * nächsten Laden ist er leer — und der Mixer hält die Animation im Speicher.
 * Das Räumen selbst liegt seit 13.09.2026 in `Clipfehlt` — denselben Weg
 * geht ein Clip, dessen Datei beim Laden fehlt (Retarget 404).
 */
export class Bibliothekablage {

    static ENDPUNKT = '/api/character/bvh-manage/';

    /**
     * Eine Aktion ausführen. Liefert die Antwort oder `null` (mit Meldung).
     */
    static async senden(aktion, daten) {
        try {
            const antwort = await Serverabruf.senden(Bibliothekablage.ENDPUNKT,
                                                     { action: aktion, ...daten });
            // Die anderen Tabs (Szene, Animationen) holen ihren Baum neu.
            Bibliothekskanal.melden(aktion, daten);
            return antwort;
        } catch (fehler) {
            alert('Fehler: ' + fehler.message);
            return null;
        }
    }

    /**
     * Alle Clips einer BVH aus allen Spuren entfernen.
     *
     * Rückgabe: Anzahl der entfernten Clips.
     */
    static clipsEntfernen(kategorie, name) {
        const entfernt = Clipfehlt.entfernen(kategorie, name, state, fn);
        if (entfernt > 0) {
            Protokoll.debug('BVH Studio',
                            `Removed ${entfernt} clip(s) of ${kategorie}/${name} from tracks`);
        }
        return entfernt;
    }
}
