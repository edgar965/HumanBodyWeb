import { Kontextmenue } from '../../gemeinsam/kontextmenue.js';
import { Genesis9garderobekategorien } from './genesis9garderobekategorien.js';
import { Genesis9garderobepflege } from './genesis9garderobepflege.js';

/**
 * Genesis9stueckmenue — das Kontextmenü eines Stücks der Daz-Garderobe: Verschieben, Umbenennen, Löschen (16.11.2026).
 *
 * Edgar, 16.11.2026: „bei den einstellungen eines Assets mach Button zum Umbenennen, Löschen und verschieben (in eine andere Kategorie)“ —
 * „ok, dann brauche ich die Buttons nicht!“ (das Menü hat alle drei) — „mach aber die Klasse dafür“: EINE Klasse für die drei Einträge. Bis
 * dahin setzten zwei Stellen sie getrennt zusammen: die Zeile der Garderobe (`Genesis9garderobekategorien.menue` mit
 * `Genesis9garderobepflege.eintraege`) und der Kasten im Bereich „Genitalien“ (`Genesis9genitalmenue.eintraege`). Die Handlungen selbst
 * bleiben, wo sie waren: Verschieben in `Genesis9garderobekategorien` (Combo-Box mit allen Kategorien, „Neue Kategorie …“), Umbenennen und
 * Löschen in `Genesis9garderobepflege` (Anzeigename; eigenes Stück in den Papierkorb, Daz-Stück ausgeblendet; beides ohne Neuaufbau).
 *
 * Eine Abweichung von vorher: Die Zeile der Garderobe bot gar kein Menü, solange die Einteilung (`Genesis9garderobekategorien._stand`) noch
 * nicht geladen war; jetzt stehen Umbenennen und Löschen dann schon da, Verschieben kommt mit der Einteilung. Ein Sammeleintrag oben
 * („Kleidung – Generisch: Alle Kategorien“, `stueck.oben`) bekommt wie bisher keines.
 */
export class Genesis9stueckmenue {

    /** Rechtsklick auf `ziel` öffnet das Menü; die Einträge entstehen erst beim Öffnen (`optionen` wie bei `eintraege`, oder eine Funktion, die sie liefert). */
    static binden(ziel, stueck, optionen = {}) {
        Kontextmenue.binden(ziel, () => Genesis9stueckmenue.eintraege(stueck, typeof optionen === 'function' ? optionen() : optionen));
    }

    /**
     * Die Einträge für `Kontextmenue`.
     *
     * @param zeile           was beim Löschen sofort verschwindet und bei einem Fehler zurückkommt (Zeile der Garderobe oder Kasten der Genitalien)
     * @param neuzeichnen     nach dem Server, wenn keine Zeile bekannt ist (dann wird die Liste neu gebaut)
     * @param garderobezeile  die Zeile der Garderobe, die beim Verschieben in ihre neue Kategorie wandert (Vorgabe: `zeile`)
     * @param text            Beschriftung des Verschiebens
     */
    static eintraege(stueck, { zeile = null, neuzeichnen = null, garderobezeile = zeile, text = 'Verschieben nach' } = {}) {
        if (stueck.oben) return [];
        const verschieben = Genesis9garderobekategorien.verschiebenEintrag(stueck, neuzeichnen, garderobezeile, text);
        // Ein Sammeleintrag („Kleidung – Generisch: Hosen“, „Haar – Generisch“; `generisch: true` vom Server) ist kein Stück mit Datei: Umbenennen und
        // Löschen lehnt der Server ab (404 „ein Sammeleintrag lässt sich nicht ändern“, Edgar 16.11.2026 an `kleidung_generisch_koerper`) — nur Verschieben.
        if (stueck.generisch === true) return verschieben ? [verschieben] : [];
        return [
            ...(verschieben ? [verschieben, null] : []),
            // Kopf, Garderobenzeile und Kasten der Genitalien setzt `Genesis9garderobepflege` nach dem Umbenennen aus dem frischen Katalog.
            { symbol: 'fa-pen', text: 'Umbenennen …', tun: () => Genesis9garderobepflege.umbenennen(stueck, neuzeichnen) },
            { symbol: 'fa-trash', text: 'Löschen', tun: () => Genesis9garderobepflege.loeschen(stueck, neuzeichnen, zeile) },
        ];
    }
}
