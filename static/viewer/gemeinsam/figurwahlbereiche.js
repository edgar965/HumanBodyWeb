import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { Figurkataloge } from './figurkataloge.js';

/**
 * Figurwahlbereiche — die zwei zugeklappten Bereiche je Reiter des
 * Figurwahl-Dialogs: „Standard-Modelle" und „Gespeicherte Modelle".
 *
 * ANLASS (Edgar, 17.09.2026): „bei Modell hinzufügen mach zwei zugeklappte
 * Bereiche - die Standard Modelle (also z.B. die vorgefertigten Genesis9 aus
 * der Bibliothek, oder die Male, Human usw. aus HumanBody), zweiter bereich -
 * die gespeicherten Modelle (also alle HumanBody von der Platte, UMA von der
 * Platte, und die Genesis9 die ich gespeichert habe)."
 *
 * Herausgelöst aus `figurwahldialog.js` (der stand danach bei 339 Zeilen):
 * hier das Markup der Bereiche und das Verteilen der Zeilen. Welche Zeile in
 * welchen Bereich gehört, sagt `Figurkataloge` (`bereich`).
 *
 * IMMER ZU (Edgar, 18.10.2026: „die tabs bei Charakter hinzufügen sollen immer
 * eingeklappt sein"): Bis dahin merkte sich jeder Bereich im localStorage, ob
 * er offen war, und ging beim nächsten Öffnen wieder auf. Jetzt klappt
 * `zuklappen` bei jedem Öffnen des Dialogs alles zu, Bereiche wie Ordner.
 */
export class Figurwahlbereiche {

    /** Das Markup der Bereiche EINES Reiters. */
    static html(kennung, quelle, versteckt) {
        return `<div class="figurwahl-bereiche${versteckt ? ' hb-versteckt' : ''}" `
            + `id="${kennung}-liste-${quelle}" data-quelle="${quelle}">`
            + Figurkataloge.BEREICHE.map(([bereich, titel]) =>
                `<details class="dialogbereich" data-bereich="${bereich}">`
                + `<summary>${Htmltext.t(titel)} <span class="gedaempft" data-zahl></span></summary>`
                + `<ul class="preset-list" data-quelle="${quelle}" data-bereich="${bereich}"></ul>`
                + '</details>').join('')
            + '</div>';
    }

    static liste(behaelter, bereich) {
        return behaelter?.querySelector(`ul[data-bereich="${bereich}"]`) || null;
    }

    /** Alle Listen des Reiters auf „Lade …" oder eine Fehlerzeile setzen. */
    static meldung(behaelter, html) {
        for (const [bereich] of Figurkataloge.BEREICHE) {
            const liste = Figurwahlbereiche.liste(behaelter, bereich);
            if (liste) liste.innerHTML = html;
        }
    }

    /**
     * Alphabetisch nach der angezeigten Bezeichnung (Edgar, 09.10.2026: „bei Charakter
     * hinzufügen sollen die Modelle alphabetisch sortiert sein"). Ohne Groß-/Kleinschreibung
     * und mit Zahlen als Zahlen — der Server liefert Dateinamen in Codepunkt-Reihenfolge, da
     * stünde „cute girl" hinter „Edgar" und „Zoe".
     */
    static sortiert(eintraege) {
        const text = e => String(e.anzeige ?? e.name ?? '');
        return [...eintraege].sort((a, b) =>
            text(a).localeCompare(text(b), 'de', { sensitivity: 'base', numeric: true }));
    }

    /**
     * Die Zeilen auf die Bereiche verteilen; `zeile(eintrag)` baut das `li`.
     * Ein leerer Bereich sagt es; ist der ganze Reiter leer, steht der
     * Leertext der Quelle in beiden. Innerhalb eines Bereichs alphabetisch.
     */
    static verteilen(behaelter, eintraege, zeile, leerText, ordner = null) {
        for (const [bereich] of Figurkataloge.BEREICHE) {
            const liste = Figurwahlbereiche.liste(behaelter, bereich);
            if (!liste) continue;
            liste.innerHTML = '';
            const eigene = Figurwahlbereiche.sortiert(
                eintraege.filter(e => (e.bereich || 'standard') === bereich));
            const zahl = liste.parentElement.querySelector('[data-zahl]');
            if (zahl) zahl.textContent = `(${eigene.length})`;
            // Die gespeicherten Modelle in Ordnern, mit Mehrfachauswahl (15.10.2026, `Figurwahlordner`).
            if (bereich === 'gespeichert' && ordner) {
                ordner.fuellen(behaelter.dataset.quelle, liste, eigene, zeile, eintraege.length ? 'Keine Einträge.' : leerText);
                continue;
            }
            if (!eigene.length) {
                liste.innerHTML = `<li class="gedaempft">${Htmltext.t(
                    eintraege.length ? 'Keine Einträge.' : leerText)}</li>`;
                continue;
            }
            for (const eintrag of eigene) liste.appendChild(zeile(eintrag));
        }
    }

    /** Alle Bereiche und Ordner des Dialogs zu — bei jedem Öffnen (der Dialog wird nur einmal gebaut und behielte sonst den letzten Stand). */
    static zuklappen(dialog) {
        for (const kasten of dialog?.querySelectorAll('details') || []) kasten.open = false;
    }
}
