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
 * hier das Markup der Bereiche, das Verteilen der Zeilen und das Gedächtnis
 * (localStorage je Dialog, Reiter und Bereich — wer einen Bereich aufklappt,
 * findet ihn beim nächsten Öffnen so wieder; die Vorgabe ist zu). Welche
 * Zeile in welchen Bereich gehört, sagt `Figurkataloge` (`bereich`).
 */
export class Figurwahlbereiche {

    /** Das Markup der Bereiche EINES Reiters. */
    static html(kennung, quelle, versteckt) {
        return `<div class="figurwahl-bereiche${versteckt ? ' hb-versteckt' : ''}" `
            + `id="${kennung}-liste-${quelle}" data-quelle="${quelle}">`
            + Figurkataloge.BEREICHE.map(([bereich, titel]) =>
                `<details class="dialogbereich" data-bereich="${bereich}"`
                + `${Figurwahlbereiche.offen(kennung, quelle, bereich) ? ' open' : ''}>`
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
     * Die Zeilen auf die Bereiche verteilen; `zeile(eintrag)` baut das `li`.
     * Ein leerer Bereich sagt es; ist der ganze Reiter leer, steht der
     * Leertext der Quelle in beiden.
     */
    static verteilen(behaelter, eintraege, zeile, leerText) {
        for (const [bereich] of Figurkataloge.BEREICHE) {
            const liste = Figurwahlbereiche.liste(behaelter, bereich);
            if (!liste) continue;
            liste.innerHTML = '';
            const eigene = eintraege.filter(e => (e.bereich || 'standard') === bereich);
            const zahl = liste.parentElement.querySelector('[data-zahl]');
            if (zahl) zahl.textContent = `(${eigene.length})`;
            if (!eigene.length) {
                liste.innerHTML = `<li class="gedaempft">${Htmltext.t(
                    eintraege.length ? 'Keine Einträge.' : leerText)}</li>`;
                continue;
            }
            for (const eintrag of eigene) liste.appendChild(zeile(eintrag));
        }
    }

    // -- Gedächtnis -----------------------------------------------------------

    static schluessel(kennung, quelle, bereich) {
        return `figurwahl-bereich:${kennung}:${quelle}:${bereich}`;
    }

    static offen(kennung, quelle, bereich) {
        try {
            return localStorage.getItem(Figurwahlbereiche.schluessel(kennung, quelle, bereich)) === '1';
        } catch (_) {
            return false;
        }
    }

    /** Beim `toggle` eines `details`: den Stand merken. */
    static merken(kennung, details) {
        const liste = details.querySelector('ul[data-bereich]');
        if (!liste) return;
        try {
            localStorage.setItem(
                Figurwahlbereiche.schluessel(kennung, liste.dataset.quelle, liste.dataset.bereich),
                details.open ? '1' : '0');
        } catch (_) {
            // stumm gewollt: ohne localStorage bleibt der Bereich beim Vorgabewert
        }
    }
}
