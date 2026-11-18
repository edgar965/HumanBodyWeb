import { Genesis9Modell } from '../../gemeinsam/genesis9modell.js';

/**
 * Genesis9anatomievorgabe — eine Figur aus dem Genesis-9-Katalog bekommt beim Laden das Anatomie-Stück ihres Geschlechts (16.11.2026).
 *
 * Edgar, 16.11.2026: „warum werden die männlichen Modelle ohne männliches Geschlechtsteil gebaut“ — „ja, automatisch anlegen nach Geschlecht“ —
 * „mach aber das optional, bei Einstellungen - Charakter eine Checkbox ob mit oder ohne“ — „default: An“.
 *
 * Daz' Charaktere bringen die Genitalien nicht mit: sie sind ein eigenes Geograft („Genesis 9 Anatomical Elements Male|Female“), das man in Daz Studio
 * selbst dazulegt (gelesen 16.11.2026, `_wegwerf/anatomie_in_presets.py`: James 9, Barbossa, Matt G9, JamesF ohne jeden Verweis darauf). Hier liegt
 * es als Garderobestück „Daz Anatomie Frau|Mann“ bereit (`Dazgeograft`); die Ergebnisfiguren von Mesh-Genesis tragen es schon nach Geschlecht
 * (`core/dienste/meshgenesisergebnisfigur.py`). Diese Klasse tut dasselbe für die Katalogfiguren der Szene (`Genesis9katalog.hinzufuegen`: Dialog,
 * Startfigur, Kontextmenü) — vor dem ersten Bau, damit das Stück mit dem Körper kommt (`Genesis9aufbau.alles`). Ein gespeichertes Modell bringt seine
 * Kleidung selbst mit und bleibt unberührt; „neutral“ bekommt nichts.
 *
 * Schalter: Einstellungen → Charakter → „Anatomie nach Geschlecht anlegen“ (`ui_prefs.anatomie_automatisch`, Vorgabe an), gesetzt von
 * `Starteinstellungen`.
 */
export class Genesis9anatomievorgabe {

    static SCHLUESSEL = 'anatomie_automatisch';
    /** Geschlecht des Katalogeintrags (`Genesis9/charaktere.py`) → Kennung des Stücks */
    static STUECK = { weiblich: 'daz_anatomie_frau', männlich: 'daz_anatomie_mann' };
    static an = true;

    /** Wert aus `ui_prefs` ('1' | '0'); ohne Wert gilt die Vorgabe „an“. */
    static einstellen(wert) {
        Genesis9anatomievorgabe.an = String(wert ?? '1') !== '0';
    }

    /** Kennung des Stücks für ein Geschlecht — oder null (ausgeschaltet, neutral, unbekannt). */
    static stueck(geschlecht) {
        return Genesis9anatomievorgabe.an ? (Genesis9anatomievorgabe.STUECK[geschlecht] || null) : null;
    }

    /** Vor dem ersten Bau: das Stück in die Kleidung der Figur. Das Geschlecht aus dem Eintrag des Dialogs, sonst aus dem Katalog. */
    static async anlegen(figur, eintrag = null) {
        if (!Genesis9anatomievorgabe.an) return null;
        const geschlecht = eintrag?.geschlecht ?? (await Genesis9Modell.eintrag(figur.figur))?.geschlecht;
        const kennung = Genesis9anatomievorgabe.stueck(geschlecht);
        if (kennung && !figur.kleidung[kennung]) figur.kleidung[kennung] = {};
        return kennung;
    }
}
