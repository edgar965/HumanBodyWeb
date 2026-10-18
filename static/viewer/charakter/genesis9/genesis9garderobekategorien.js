import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Kontextmenue } from '../../gemeinsam/kontextmenue.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Genesis9garderobepflege } from './genesis9garderobepflege.js';
import { Genesis9garderobezeile } from './genesis9garderobezeile.js';

/**
 * Genesis9garderobekategorien — Edgars Einteilung der Daz-Garderobe im Browser.
 *
 * Edgar, 20.09.2026: „kannst du Unterteilungen machen, Kategorien wie bei
 * GarmentCode? Plus Kontextmenü bei jedem Item, mit dem ich das in eine andere
 * Kategorie verschieben kann." — und nachts: „kategorien so wie die bei Garment
 * Code. warum wurde das nicht gemacht???" Die Liste kommt von `Genesis9garderobe`;
 * jedes Stück trägt seine VORGABE (`kategorie`, aus Daz' Metadaten:
 * Oberteile, Hosen, Shorts, Röcke, Kleider, Anzüge, Outfits, Unterwäsche, Schuhe,
 * Socken, Kopfbedeckung, Zubehör, Haare, Requisiten — `G9dazkategorien`); Edgars Einteilung
 * liegt beim Server (`G9garderobekategorien`, `3DObjects/models/Genesis9/
 * garderobe_kategorien.json`) und wird hier darübergelegt.
 *
 * Das Kontextmenü (`Kontextmenue`, dasselbe wie bei Animationen und Modell)
 * bietet „Verschieben nach" als Combo-Box mit allen Kategorien und am Ende
 * „Neue Kategorie …" (Name per Abfrage; bis 18.10.2026 eine Zeile je Kategorie). Beim Verschieben wandert nur die Zeile
 * (seit 18.10.2026, `verschieben`) — der Stand kommt mit der Antwort zurück.
 *
 * Alle Kategorien stehen ZU; offen ist EINZIG die des in der Szene gewählten Stücks
 * (`Genesis9garderobe.gewaehltesStueck`).
 *
 * KEIN GEDÄCHTNIS MEHR (Edgar, 30.09.2026: „ALLE Einträge in den Tabs zu Assets und anderen
 * sollen beim Laden IMMER zugeklappt sein. das hatte ich schon 10 Mal in Auftrag gegeben …
 * Nur das aktuell selektierte Item soll den Tab / die Gliederung aufklappen"). Hier stand
 * bis dahin ein `localStorage`-Gedächtnis („was dieser Browser sich als offen gemerkt hat"),
 * das die Vorgabe ZU von 21.09.2026 stillschweigend aushebelte: Eine einmal aufgeklappte
 * Kategorie blieb es für immer, in jedem Seitenaufruf. Genau deshalb kam die Bitte immer
 * wieder. Aufgeklappt wird nur, was der Nutzer JETZT anklickt.
 */
export class Genesis9garderobekategorien {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/kategorien/';
    /** Art -> Vorgabe, wenn der Server keine `kategorie` mitgibt (`G9dazkategorien.NACH_ART`). */
    static VORGABE = { kleidung: 'Oberteile', haar: 'Haare', requisit: 'Requisiten' };
    /** Wert der Combo-Box für „Neue Kategorie …" — kein Name einer Kategorie kann ihn tragen. */
    static NEU = '\u0000neu';
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

    /** Ob der Name eine Kategorie der Assets ist (Oberteile, Hosen …) — im Gegensatz zu Passform, Mischung, Textur, Form (Ort). */
    static ist(name) {
        return Boolean(Genesis9garderobekategorien._stand?.kategorien?.includes(name));
    }

    /** `[[Name, [Stücke]]]` in der Reihenfolge des Stands — nur besetzte. */
    static gruppen(stuecke, stand) {
        const nach = new Map((stand.kategorien || []).map(name => [name, []]));
        for (const stueck of stuecke) {
            if (stueck.oben) continue;      // „Kleidung – Generisch: Alle Kategorien": steht über den Kategorien
            const name = Genesis9garderobekategorien.kategorie(stueck, stand);
            if (!nach.has(name)) nach.set(name, []);
            nach.get(name).push(stueck);
        }
        return [...nach].filter(([, eigene]) => eigene.length);
    }

    // ------------------------------------------------------------ Kontextmenü

    /** Rechtsklick auf die Zeile: verschieben, umbenennen, löschen; `neuzeichnen` danach. */
    static menue(zeile, stueck, neuzeichnen) {
        Kontextmenue.binden(zeile, () => {
            const verschieben = Genesis9garderobekategorien.verschiebenEintrag(stueck, neuzeichnen, zeile);
            if (!verschieben) return [];
            // Umbenennen und Löschen bei jedem Stück (Edgar, 05.10.2026) — `Genesis9garderobepflege`.
            return [verschieben, null, ...Genesis9garderobepflege.eintraege(stueck, neuzeichnen, zeile)];
        });
    }

    /**
     * Der Menüeintrag „Verschieben nach" mit allen Kategorien — null, solange der Stand fehlt oder das Stück oben steht (der Eintrag
     * oben gehört zu keiner Kategorie). Auch der Bereich „Genitalien" (`Genesis9genitalmenue`) nimmt ihn: dort gibt es keine eigene
     * Einteilung, ein Stück bleibt in DERSELBEN Kategorie der Garderobe.
     *
     * EINE Combo-Box statt einer Zeile je Kategorie (Edgar, 18.10.2026: „verschieben Funktion vereinfachen, mach eine Combo Box mit
     * allen ordnern (anstelle der Auflistung)"); die eigene steht gewählt, „Neue Kategorie …" am Ende.
     */
    static verschiebenEintrag(stueck, neuzeichnen, zeile, text = 'Verschieben nach') {
        const stand = Genesis9garderobekategorien._stand;
        if (!stand || stueck.oben) return null;
        const eigene = Genesis9garderobekategorien.kategorie(stueck, stand);
        const namen = stand.kategorien.includes(eigene) ? stand.kategorien : [...stand.kategorien, eigene];
        return {
            symbol: 'fa-folder', text, wert: eigene,
            auswahl: [...namen.map(name => ({ wert: name, text: name })),
                      { wert: Genesis9garderobekategorien.NEU, text: 'Neue Kategorie …' }],
            waehlen: wert => Genesis9garderobekategorien._gewaehlt(stueck, wert, neuzeichnen, zeile),
        };
    }

    /** Wahl in der Combo-Box: eine Kategorie, oder `NEU` — dann der Name per Abfrage. */
    static _gewaehlt(stueck, wert, neuzeichnen, zeile) {
        const name = wert === Genesis9garderobekategorien.NEU
            ? (window.prompt(`„${stueck.name}" verschieben in neue Kategorie:`, '') || '').trim()
            : wert;
        if (name) Genesis9garderobekategorien.verschieben(stueck, name, neuzeichnen, zeile);
    }

    /** Die Zeile wandert SOFORT in die Kategorie, der Server im Hintergrund — ohne Neuaufbau, offene Kategorien bleiben offen
     *  (Edgar, 18.10.2026: „nach verschieben eines Assets wird das menü wieder geschlossen", `Genesis9garderobezeile`).
     *  Scheitert der Server, wandert sie zurück. Ohne bekannte Zeile wie bisher: neu zeichnen. */
    static async verschieben(stueck, name, neuzeichnen, zeile = null) {
        const vorher = Genesis9garderobekategorien._stand;
        const alt = vorher ? Genesis9garderobekategorien.kategorie(stueck, vorher) : null;
        const umgehaengt = Boolean(zeile && vorher) && Genesis9garderobekategorien._umhaengen(zeile, stueck, name);
        try {
            Genesis9garderobekategorien._stand = await Serverabruf.senden(
                Genesis9garderobekategorien.ADRESSE, { kennung: stueck.id, kategorie: name });
        } catch (fehler) {
            if (umgehaengt) {
                Genesis9garderobekategorien._stand = vorher;
                Genesis9garderobezeile.verschieben(zeile, alt, vorher.kategorien);
            }
            Protokoll.fehler('Garderobe', `Verschieben nach „${name}" fehlgeschlagen`, fehler);
            window.alert(`Verschieben fehlgeschlagen: ${fehler.message}`);
            return;
        }
        if (!umgehaengt) neuzeichnen?.();
    }

    /** Den Stand so vorwegnehmen, wie der Server ihn gleich zurückgibt, und die Zeile umhängen. */
    static _umhaengen(zeile, stueck, name) {
        const stand = Genesis9garderobekategorien._stand;
        Genesis9garderobekategorien._stand = {
            ...stand,
            kategorien: stand.kategorien.includes(name) ? stand.kategorien : [...stand.kategorien, name],
            zuordnung: { ...(stand.zuordnung || {}), [stueck.id]: name },
        };
        return Genesis9garderobezeile.verschieben(zeile, name, Genesis9garderobekategorien._stand.kategorien);
    }

    // ------------------------------------------------------------ Aufgeklappt

    /** Offen ist eine Kategorie NUR, wenn sie das in der Szene gewählte Stück enthält.
     *  Kein Gedächtnis — siehe Kopf der Datei (Edgar, 30.09.2026). Ein alter
     *  `hb_g9_garderobe_offen_2` darf im Browser liegen bleiben: Er wird nicht mehr
     *  gelesen und kann deshalb nichts mehr offen halten. */
    static offen(name, enthaeltGewaehltes = false) {
        return enthaeltGewaehltes;
    }
}
