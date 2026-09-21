import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Kontextmenue } from '../../gemeinsam/kontextmenue.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * Genesis9garderobekategorien — Edgars Einteilung der Daz-Garderobe im Browser.
 *
 * Edgar, 20.09.2026: „kannst du Unterteilungen machen, Kategorien wie bei
 * GarmentCode? Plus Kontextmenü bei jedem Item, mit dem ich das in eine andere
 * Kategorie verschieben kann." — und nachts: „kategorien so wie die bei Garment
 * Code. warum wurde das nicht gemacht???" Die Liste kommt von `Genesis9garderobe`;
 * jedes Stück trägt seine VORGABE (`kategorie`, aus Daz' Metadaten:
 * Oberteile, Hosen, Shorts, Röcke, Kleider, Anzüge, Outfits, Unterwäsche, Schuhe,
 * Kopfbedeckung, Zubehör, Haare, Requisiten — `G9dazkategorien`); Edgars Einteilung
 * liegt beim Server (`G9garderobekategorien`, `3DObjects/Genesis9/
 * garderobe_kategorien.json`) und wird hier darübergelegt.
 *
 * Das Kontextmenü (`Kontextmenue`, dasselbe wie bei Animationen und Modell)
 * bietet je andere Kategorie einen Eintrag „Verschieben nach …" und darunter
 * „Neue Kategorie …" (Name per Abfrage). Nach dem Verschieben zeichnet der
 * Aufrufer die Liste neu — der Stand kommt mit der Antwort zurück.
 *
 * Alle Kategorien stehen ZU (Edgar, 21.09.2026); offen ist die des in der Szene
 * gewählten Stücks (`Genesis9garderobe.gewaehltesStueck`) und was dieser Browser
 * sich als offen gemerkt hat (`localStorage`, umschlossen wie in `Bereichsgedaechtnis`).
 */
export class Genesis9garderobekategorien {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/kategorien/';
    /** Neuer Schlüssel seit der Vorgabe ZU (21.09.2026): unter dem alten stand in jedem
     *  Browser „alle offen" — die erste Merkung hatte damals alle Kategorien mitgenommen. */
    static SCHLUESSEL = 'hb_g9_garderobe_offen_2';
    /** Art -> Vorgabe, wenn der Server keine `kategorie` mitgibt (`G9dazkategorien.NACH_ART`). */
    static VORGABE = { kleidung: 'Oberteile', haar: 'Haare', requisit: 'Requisiten' };
    static _stand = null;

    /** `{kategorien: [Name], zuordnung: {kennung: Name}}` — einmal geholt. */
    static async stand() {
        if (!Genesis9garderobekategorien._stand) {
            try {
                Genesis9garderobekategorien._stand = await Serverabruf.json(Genesis9garderobekategorien.ADRESSE);
            } catch (fehler) {
                Protokoll.warnung('Garderobe', `Einteilung nicht ladbar: ${fehler.message}`);
                return { kategorien: Object.values(Genesis9garderobekategorien.VORGABE), zuordnung: {} };
            }
        }
        return Genesis9garderobekategorien._stand;
    }

    static kategorie(stueck, stand) {
        return stand.zuordnung?.[stueck.id]
            || stueck.kategorie
            || Genesis9garderobekategorien.VORGABE[stueck.art]
            || Genesis9garderobekategorien.VORGABE.kleidung;
    }

    /** `[[Name, [Stücke]]]` in der Reihenfolge des Stands — nur besetzte. */
    static gruppen(stuecke, stand) {
        const nach = new Map((stand.kategorien || []).map(name => [name, []]));
        for (const stueck of stuecke) {
            const name = Genesis9garderobekategorien.kategorie(stueck, stand);
            if (!nach.has(name)) nach.set(name, []);
            nach.get(name).push(stueck);
        }
        return [...nach].filter(([, eigene]) => eigene.length);
    }

    // ------------------------------------------------------------ Kontextmenü

    /** Rechtsklick auf die Zeile: verschieben; `neuzeichnen` danach. */
    static menue(zeile, stueck, neuzeichnen) {
        Kontextmenue.binden(zeile, () => {
            const stand = Genesis9garderobekategorien._stand;
            if (!stand) return [];
            const eigene = Genesis9garderobekategorien.kategorie(stueck, stand);
            const eintraege = stand.kategorien
                .filter(name => name !== eigene)
                .map(name => ({
                    symbol: 'fa-folder', text: `Verschieben nach „${name}"`,
                    tun: () => Genesis9garderobekategorien.verschieben(stueck, name, neuzeichnen),
                }));
            eintraege.push(null, {
                symbol: 'fa-folder-plus', text: 'Neue Kategorie …',
                tun: () => {
                    const name = window.prompt(`„${stueck.name}" verschieben in neue Kategorie:`, '');
                    if (name && name.trim()) {
                        Genesis9garderobekategorien.verschieben(stueck, name.trim(), neuzeichnen);
                    }
                },
            });
            return eintraege;
        });
    }

    static async verschieben(stueck, name, neuzeichnen) {
        try {
            Genesis9garderobekategorien._stand = await Serverabruf.senden(
                Genesis9garderobekategorien.ADRESSE, { kennung: stueck.id, kategorie: name });
        } catch (fehler) {
            Protokoll.fehler('Garderobe', `Verschieben nach „${name}" fehlgeschlagen`, fehler);
            window.alert(`Verschieben fehlgeschlagen: ${fehler.message}`);
            return;
        }
        Genesis9garderobekategorien.merken(name, true);
        neuzeichnen?.();
    }

    // ------------------------------------------------------------ Aufgeklappt

    /** Offen ist eine Kategorie nur, wenn sie das in der Szene gewählte Stück
     *  enthält oder dieser Browser sie sich als offen gemerkt hat — die Vorgabe
     *  ist ZU (Edgar, 21.09.2026: „per default alle Kategorien zugeklappt"). */
    static offen(name, enthaeltGewaehltes = false) {
        return enthaeltGewaehltes || Genesis9garderobekategorien._gemerkt().includes(name);
    }

    static merken(name, offen) {
        const alle = new Set(Genesis9garderobekategorien._gemerkt());
        if (offen) alle.add(name); else alle.delete(name);
        try {
            localStorage.setItem(Genesis9garderobekategorien.SCHLUESSEL, JSON.stringify([...alle]));
        } catch (fehler) {
            // privates Fenster, gesperrte Seitendaten — dann eben nicht gemerkt
        }
    }

    /** Die gemerkten offenen Namen — ohne die, die es nicht mehr gibt (die Erinnerung
     *  „Kleidung" von vor den Daz-Kategorien). Leer, wenn nie etwas gemerkt wurde. */
    static _gemerkt() {
        try {
            const roh = JSON.parse(localStorage.getItem(Genesis9garderobekategorien.SCHLUESSEL));
            if (!Array.isArray(roh)) return [];
            const bekannt = Genesis9garderobekategorien._stand?.kategorien;
            return bekannt ? roh.filter(n => bekannt.includes(n)) : roh;
        } catch (fehler) {
            return [];
        }
    }
}
