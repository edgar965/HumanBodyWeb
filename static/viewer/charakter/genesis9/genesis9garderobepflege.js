import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9kleidung } from '../../gemeinsam/genesis9kleidung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Genesis9garderobezeile } from './genesis9garderobezeile.js';
import { Genesis9genitalkasten } from './genesis9genitalkasten.js';

/**
 * Genesis9garderobepflege — „Umbenennen" und „Löschen" im Kontextmenü eines Garderobenstücks.
 *
 * Edgar, 05.10.2026: „füge im Kontextmenü bei allen ein: Löschen, Umbenennen (zum löschen und umbenennen)". Der Server
 * (`G9garderobepflege`) ändert beim Umbenennen nur den ANZEIGENAMEN — die Kennung bleibt, Rezepte und Aufträge nennen die Stücke
 * dabei. Gelöscht wird ein eigenes Stück (Foto-Stücke, Uhr, GarmentCode, MakeHuman) in den Papierkorb
 * (`3DObjects/models/Genesis9/papierkorb/`, zurückholbar); ein Stück der Daz-Bibliothek wird nur ausgeblendet, die Dateien bleiben.
 * Nach dem Umbenennen holt `Genesis9kleidung` den Katalog neu, und der Aufrufer zeichnet die Liste neu.
 *
 * LÖSCHEN OHNE NEUAUFBAU (Edgar, 18.10.2026: „nach jedem Löschen eines Garderobenteils wird das Menü neu aufgebaut - mach das
 * asynchron, so dass ich schnell löschen kann"): Bis dahin stand nach jedem Löschen „Lade Garderobe …" da, bis der ganze Katalog
 * neu geholt und die Liste neu gebaut war — erst dann ließ sich das nächste Stück anklicken. Jetzt verschwindet nur die Zeile
 * (samt Reglerkasten), sofort beim Klick; der Server arbeitet im Hintergrund, und das Stück wird nur aus dem gemerkten
 * Katalog genommen (`Genesis9kleidung.entfernen`). Scheitert der Server, kommt die Zeile wieder.
 *
 * ÜBERALL, WO DAS STÜCK STEHT (Edgar, 18.10.2026: „es sollen doch ALLE Assets umbenannt und gelöscht werden können?"): Dasselbe Stück
 * steht in der Garderobe (Assets-Reiter) und, wenn es eine Anatomie hat, als Kasten im Bereich „Genitalien" (Modell-Reiter). Umbenennen
 * und Löschen ziehen beide nach — von welcher Seite auch ausgelöst (`_nachziehen`, `_mitnehmen`), ohne eine Liste neu zu bauen.
 */
export class Genesis9garderobepflege {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';

    /** Die zwei Einträge für das Kontextmenü einer Zeile (`Kontextmenue.binden`). */
    static eintraege(stueck, neuzeichnen, zeile = null) {
        return [
            { symbol: 'fa-pen', text: 'Umbenennen …', tun: () => Genesis9garderobepflege.umbenennen(stueck, neuzeichnen) },
            { symbol: 'fa-trash', text: 'Löschen', tun: () => Genesis9garderobepflege.loeschen(stueck, neuzeichnen, zeile) },
        ];
    }

    static adresse(stueck, aktion) {
        return `${Genesis9garderobepflege.ADRESSE}${encodeURIComponent(stueck.id)}/${aktion}/`;
    }

    static async umbenennen(stueck, neuzeichnen) {
        const neu = window.prompt(`Neuer Name für „${stueck.name}" (leer = Name der Bibliothek):`, stueck.name);
        if (neu === null) return;
        if (await Genesis9garderobepflege._senden(stueck, 'umbenennen', { name: neu }, 'Umbenennen', neuzeichnen)) {
            await Genesis9garderobepflege._nachziehen(stueck);
        }
    }

    /**
     * Nach dem Umbenennen den Namen aus dem frischen Katalog holen — bei leerem Namen ist es der der Bibliothek, den kennt nur der Server —
     * und in der Garderobenzeile sowie im Kasten der Genitalien setzen (jeweils nur, wenn es sie gibt).
     */
    static async _nachziehen(stueck) {
        const neu = (await Genesis9kleidung.stuecke()).find(s => s.id === stueck.id);
        if (!neu) return;
        stueck.name = neu.name;         // das Menü fragt beim nächsten Mal nach dem jetzigen Namen
        Genesis9garderobezeile.benennen(Genesis9garderobezeile.zeileVon(stueck.id), neu.name);
        Genesis9genitalkasten.benennen(stueck.id, neu.name);
    }

    /** Nach dem Löschen: was vom Stück noch steht (Garderobenzeile, Kasten der Genitalien), nimmt der Server-Erfolg mit. */
    static _mitnehmen(stueck) {
        const zeile = Genesis9garderobezeile.zeileVon(stueck.id);
        if (zeile) Genesis9garderobezeile.entfernen(zeile);
        Genesis9genitalkasten.entfernen(stueck.id);
    }

    /** Ohne Rückfrage (Edgar, 18.10.2026: „mach die Rückfragen vor dem Löschen weg") — ein eigenes Stück liegt danach im
     *  Papierkorb (`3DObjects/models/Genesis9/papierkorb/`), eines der Daz-Bibliothek ist nur ausgeblendet; beides ist zurückholbar. */
    static async loeschen(stueck, neuzeichnen, zeile = null) {
        if (!zeile) {           // ohne bekannte Zeile wie bisher: Katalog neu, Liste neu
            if (await Genesis9garderobepflege._senden(stueck, 'loeschen', {}, 'Löschen', neuzeichnen)) Genesis9garderobepflege._mitnehmen(stueck);
            return;
        }
        Genesis9garderobezeile.zeigen(zeile, false);
        try {
            await Serverabruf.senden(Genesis9garderobepflege.adresse(stueck, 'loeschen'), {});
        } catch (fehler) {
            Genesis9garderobezeile.zeigen(zeile, true);
            Protokoll.fehler('Garderobe', `Löschen von „${stueck.name}" fehlgeschlagen`, fehler);
            window.alert(`Löschen fehlgeschlagen: ${fehler.message}`);
            return;
        }
        Genesis9garderobezeile.entfernen(zeile);        // `zeile` kann auch der Kasten der Genitalien sein (`Genesis9genitalmenue`)
        Genesis9kleidung.entfernen(stueck.id);
        Genesis9garderobepflege._mitnehmen(stueck);
    }

    /** @returns {Promise<boolean>} ob der Server die Änderung angenommen hat */
    static async _senden(stueck, aktion, nutzlast, titel, neuzeichnen) {
        try {
            await Serverabruf.senden(Genesis9garderobepflege.adresse(stueck, aktion), nutzlast);
        } catch (fehler) {
            Protokoll.fehler('Garderobe', `${titel} von „${stueck.name}" fehlgeschlagen`, fehler);
            window.alert(`${titel} fehlgeschlagen: ${fehler.message}`);
            return false;
        }
        Genesis9kleidung.vergessen();
        neuzeichnen?.();
        return true;
    }
}
