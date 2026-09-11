import { Htmltext } from '/static/djangobase/js/htmltext.js';

/**
 * Figurwahlzeile — eine Zeile in den Listen des Figurwahl-Dialogs.
 *
 * Herausgelöst aus `figurwahldialog.js` (296 Zeilen, 11.09.2026), als der
 * Dialog eine zweite Aufgabe bekam (Modell austauschen). Die Zeile kennt
 * den Dialog nicht: Sie bekommt gesagt, was bei Klick, Doppelklick und den
 * Pflege-Knöpfen geschehen soll.
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
        return li;
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
