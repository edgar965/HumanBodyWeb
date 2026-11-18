import { Serverabruf } from './serverabruf.js';

/**
 * Standardmodellpflege — Standard-Modelle im Dialog „Charakter hinzufügen“ umbenennen und ausblenden (16.11.2026).
 *
 * Edgar, 16.11.2026: „bei den gespeicherten Modellen gibt es Buttons zum Ändern des Namens und löschen. Mach das auch bei den Standard Modellen rein“.
 * Ein Standard-Modell ist keine Datei (Genesis-9-Charaktere aus der Daz-Bibliothek, Körpertypen aus MB-Lab, SMPL-X, MakeHuman): Umbenennen ändert den
 * Anzeigenamen, Löschen blendet aus — die Daten bleiben (Server: `Standardmodellpflege`, `3DObjects/models/standardmodelle_pflege.json`). Der Name, mit
 * dem der Dialog lädt (`eintrag.name`), bleibt derselbe. `anwenden` legt den Stand über die Zeilen jedes Reiters (`Figurkataloge.modelle`).
 */
export class Standardmodellpflege {

    static ADRESSE = '/api/character/katalog/standard/';
    static _stand = null;

    /** `{quelle: {namen, ausgeblendet}}` — einmal geholt, nach jeder Änderung neu. Ohne Antwort: nichts überlagert. */
    static async stand() {
        if (!Standardmodellpflege._stand) {
            Standardmodellpflege._stand = Serverabruf.json(Standardmodellpflege.ADRESSE).catch(() => ({}));
        }
        return Standardmodellpflege._stand;
    }

    static vergessen() {
        Standardmodellpflege._stand = null;
    }

    /** Die Zeilen eines Reiters: Standard-Zeilen umbenannt, ausgeblendete weg; Gespeichertes bleibt, wie es ist. */
    static async anwenden(quelle, zeilen) {
        const stand = (await Standardmodellpflege.stand())?.[quelle] || {};
        const weg = new Set(stand.ausgeblendet || []);
        const namen = stand.namen || {};
        return zeilen
            .filter(z => Standardmodellpflege.gespeichert(z) || !weg.has(z.name))
            .map(z => (!Standardmodellpflege.gespeichert(z) && namen[z.name]) ? { ...z, anzeige: namen[z.name], vorgabeAnzeige: z.anzeige } : z);
    }

    static gespeichert(zeile) {
        return (zeile.bereich || 'standard') === 'gespeichert';
    }

    /** Nach dem neuen Anzeigenamen fragen; leer = zurück zur Vorgabe. @returns true, wenn sich etwas geändert hat */
    static async umbenennen(quelle, eintrag) {
        const eingabe = window.prompt(`Neuer Name für „${eintrag.anzeige}“ (leer = ursprünglicher Name „${eintrag.vorgabeAnzeige || eintrag.anzeige}“):`, eintrag.anzeige);
        if (eingabe === null || eingabe.trim() === eintrag.anzeige) return false;
        await Standardmodellpflege._senden('umbenennen/', { quelle, name: eintrag.name, neu: eingabe.trim() });
        return true;
    }

    /** Rückfragen und ausblenden. @returns true, wenn ausgeblendet wurde */
    static async loeschen(quelle, eintrag) {
        if (!window.confirm(`Standard-Modell „${eintrag.anzeige}“ aus der Liste löschen?\n\nEs wird nur ausgeblendet — die Daten bleiben erhalten.`)) return false;
        await Standardmodellpflege._senden('loeschen/', { quelle, name: eintrag.name });
        return true;
    }

    /** POST mit CSRF-Kopf (`Serverabruf.senden`; `json` mit `method: 'POST'` schickt keinen — 403 „CSRF token missing“, 16.11.2026). */
    static async _senden(pfad, rumpf) {
        await Serverabruf.senden(Standardmodellpflege.ADRESSE + pfad, rumpf);
        Standardmodellpflege.vergessen();
    }
}
