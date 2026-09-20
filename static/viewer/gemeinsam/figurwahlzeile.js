import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { Kontextmenue } from './kontextmenue.js';

/**
 * Figurwahlzeile — eine Zeile in den Listen des Figurwahl-Dialogs.
 *
 * Herausgelöst aus `figurwahldialog.js` (296 Zeilen, 11.09.2026), als der
 * Dialog eine zweite Aufgabe bekam (Modell austauschen). Die Zeile kennt
 * den Dialog nicht: Sie bekommt gesagt, was bei Klick, Doppelklick und den
 * Pflege-Knöpfen geschehen soll.
 *
 * RECHTSKLICK (Edgar, 20.09.2026: „bei den gespeicherten Modellen, mach ein
 * Kontextmenü, mit dem ich das Modell löschen kann, dann wird es von der
 * Platte gelöscht"): Auf einer Zeile mit Pflege öffnet die rechte Maustaste
 * das Menü der Seite (`Kontextmenue`) mit Umbenennen und Löschen — dieselben
 * zwei Werkzeuge wie die Knöpfe rechts in der Zeile, und derselbe Weg dahinter
 * (`pflegen(was)`, in der Szene `Katalogpflege` mit Rückfrage und Löschen der
 * Datei). Eine Zeile ohne Pflege — ein Körpertyp, ein Katalogeintrag — hat
 * kein Menü, sie ist keine Datei.
 */
export class Figurwahlzeile {

    /**
     * @param {Object} eintrag  { name, anzeige, unterzeile } aus Figurkataloge
     * @param {Object} taten    { waehlen(), laden(), pflegen(was) | null }
     *        `pflegen` fehlt → keine Werkzeug-Knöpfe
     */
    static bauen(eintrag, { waehlen, laden, pflegen = null }) {
        const li = document.createElement('li');
        li.dataset.name = eintrag.name;
        li.innerHTML = Figurwahlzeile.markup(eintrag, Boolean(pflegen));
        li.addEventListener('click', (e) => {
            if (e.target.closest('[data-tun]')) return;   // Werkzeug, keine Wahl
            waehlen();
        });
        li.addEventListener('dblclick', (e) => {
            if (e.target.closest('[data-tun]')) return;
            laden();
        });
        for (const was of ['umbenennen', 'loeschen']) {
            li.querySelector(`[data-tun="${was}"]`)
                ?.addEventListener('click', () => pflegen(was));
        }
        if (pflegen) {
            // Der Rechtsklick wählt die Zeile mit — man sieht, wovon das Menü spricht.
            Kontextmenue.binden(li, () => { waehlen(); return Figurwahlzeile.menue(pflegen); });
        }
        return li;
    }

    /** Die Einträge des Rechtsklickmenüs — dieselben zwei Werkzeuge wie die Knöpfe. */
    static menue(pflegen) {
        return [
            { symbol: 'fa-pen', text: 'Umbenennen', tun: () => pflegen('umbenennen') },
            { symbol: 'fa-trash', text: 'Löschen', tun: () => pflegen('loeschen') },
        ];
    }

    static markup(eintrag, mitPflege) {
        return `<span class="eintragsname">${Htmltext.t(eintrag.anzeige)}`
            + (eintrag.unterzeile
                ? `<span class="preset-sub">${Htmltext.t(eintrag.unterzeile)}</span>` : '')
            + '</span>'
            + (mitPflege
                ? '<span class="eintragswerkzeuge">'
                  + '<button class="knopf-schmal" data-tun="umbenennen" title="Umbenennen">'
                  + '<i class="fas fa-pen"></i></button>'
                  + '<button class="knopf-schmal" data-tun="loeschen" title="Löschen">'
                  + '<i class="fas fa-trash"></i></button></span>'
                : '');
    }
}
