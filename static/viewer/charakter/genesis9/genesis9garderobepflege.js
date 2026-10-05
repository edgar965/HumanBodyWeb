import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9kleidung } from '../../gemeinsam/genesis9kleidung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * Genesis9garderobepflege — „Umbenennen" und „Löschen" im Kontextmenü eines Garderobenstücks.
 *
 * Edgar, 05.10.2026: „füge im Kontextmenü bei allen ein: Löschen, Umbenennen (zum löschen und umbenennen)". Der Server
 * (`G9garderobepflege`) ändert beim Umbenennen nur den ANZEIGENAMEN — die Kennung bleibt, Rezepte und Aufträge nennen die Stücke
 * dabei. Gelöscht wird ein eigenes Stück (Foto-Stücke, Uhr, GarmentCode, MakeHuman) in den Papierkorb
 * (`3DObjects/Genesis9/papierkorb/`, zurückholbar); ein Stück der Daz-Bibliothek wird nur ausgeblendet, die Dateien bleiben.
 * Danach holt `Genesis9kleidung` den Katalog neu, und der Aufrufer zeichnet die Liste neu.
 */
export class Genesis9garderobepflege {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';

    /** Die zwei Einträge für das Kontextmenü einer Zeile (`Kontextmenue.binden`). */
    static eintraege(stueck, neuzeichnen) {
        return [
            { symbol: 'fa-pen', text: 'Umbenennen …', tun: () => Genesis9garderobepflege.umbenennen(stueck, neuzeichnen) },
            { symbol: 'fa-trash', text: 'Löschen …', tun: () => Genesis9garderobepflege.loeschen(stueck, neuzeichnen) },
        ];
    }

    static adresse(stueck, aktion) {
        return `${Genesis9garderobepflege.ADRESSE}${encodeURIComponent(stueck.id)}/${aktion}/`;
    }

    static async umbenennen(stueck, neuzeichnen) {
        const neu = window.prompt(`Neuer Name für „${stueck.name}" (leer = Name der Bibliothek):`, stueck.name);
        if (neu === null) return;
        await Genesis9garderobepflege._senden(stueck, 'umbenennen', { name: neu }, 'Umbenennen', neuzeichnen);
    }

    static async loeschen(stueck, neuzeichnen) {
        const frage = stueck.eigen
            ? `„${stueck.name}" in den Papierkorb legen?\n\nDie Dateien liegen danach in 3DObjects/Genesis9/papierkorb/ und lassen sich zurückholen.`
            : `„${stueck.name}" ausblenden?\n\nDas ist ein Stück der Daz-Bibliothek: Seine Dateien bleiben unberührt, es verschwindet nur aus dieser Liste.`;
        if (!window.confirm(frage)) return;
        await Genesis9garderobepflege._senden(stueck, 'loeschen', {}, 'Löschen', neuzeichnen);
    }

    static async _senden(stueck, aktion, nutzlast, titel, neuzeichnen) {
        try {
            await Serverabruf.senden(Genesis9garderobepflege.adresse(stueck, aktion), nutzlast);
        } catch (fehler) {
            Protokoll.fehler('Garderobe', `${titel} von „${stueck.name}" fehlgeschlagen`, fehler);
            window.alert(`${titel} fehlgeschlagen: ${fehler.message}`);
            return;
        }
        Genesis9kleidung.vergessen();
        neuzeichnen?.();
    }
}
