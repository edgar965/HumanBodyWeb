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
     * Die Werkzeuge einer Zeile (Knopf rechts und Eintrag im Rechtsklickmenü). `importloeschen` (10.10.2026, Edgar: „Button zum Löschen
     * eines Imports oder verwaisten Imports"): ein Modell aus einem Blender-Import samt Import, oder ein abgebrochener Import allein.
     */
    static WERKZEUGE = {
        umbenennen: { symbol: 'fa-pen', text: 'Umbenennen', titel: 'Umbenennen' },
        loeschen: { symbol: 'fa-trash', text: 'Löschen', titel: 'Löschen' },
        importloeschen: { symbol: 'fa-eraser', text: 'Import löschen …',
                          titel: 'Import löschen: Ordner, Auftrag „Mesh to 3D", Stücke und Modell' },
    };

    static STANDARD = ['umbenennen', 'loeschen'];

    /**
     * @param {Object} eintrag  { name, anzeige, unterzeile, warnung? } aus Figurkataloge — `warnung` setzt ein rotes Zeichen vor den Namen
     * @param {Object} taten    { waehlen(), laden(), pflegen(was) | null, werkzeuge }
     *        `pflegen` fehlt → keine Werkzeug-Knöpfe; `werkzeuge` nennt, welche (Vorgabe Umbenennen und Löschen)
     */
    static bauen(eintrag, { waehlen, laden, pflegen = null, werkzeuge = Figurwahlzeile.STANDARD }) {
        const li = document.createElement('li');
        li.dataset.name = eintrag.name;
        if (eintrag.warnung) li.classList.add('mit-warnung');
        li.innerHTML = Figurwahlzeile.markup(eintrag, pflegen ? werkzeuge : false);
        li.addEventListener('click', (e) => {
            if (e.target.closest('[data-tun]')) return;   // Werkzeug, keine Wahl
            waehlen();
        });
        li.addEventListener('dblclick', (e) => {
            if (e.target.closest('[data-tun]')) return;
            laden();
        });
        for (const was of Object.keys(Figurwahlzeile.WERKZEUGE)) {
            li.querySelector(`[data-tun="${was}"]`)
                ?.addEventListener('click', () => pflegen(was));
        }
        if (pflegen) {
            // Der Rechtsklick wählt die Zeile mit — man sieht, wovon das Menü spricht.
            Kontextmenue.binden(li, () => { waehlen(); return Figurwahlzeile.menue(pflegen, werkzeuge); });
        }
        return li;
    }

    /** Die Einträge des Rechtsklickmenüs — dieselben Werkzeuge wie die Knöpfe. */
    static menue(pflegen, werkzeuge = Figurwahlzeile.STANDARD) {
        return werkzeuge.map(was => ({
            symbol: Figurwahlzeile.WERKZEUGE[was].symbol, text: Figurwahlzeile.WERKZEUGE[was].text, tun: () => pflegen(was),
        }));
    }

    /** `mitPflege`: `true` (Umbenennen und Löschen), eine Liste von Werkzeugen oder `false`. */
    static markup(eintrag, mitPflege) {
        const werkzeuge = mitPflege === true ? Figurwahlzeile.STANDARD : (mitPflege || []);
        const warnung = eintrag.warnung
            ? `<i class="fas fa-triangle-exclamation eintrag-warnung" title="${Htmltext.t(eintrag.warnung)}"></i>` : '';
        return `<span class="eintragsname">${warnung}${Htmltext.t(eintrag.anzeige)}`
            + (eintrag.unterzeile
                ? `<span class="preset-sub">${Htmltext.t(eintrag.unterzeile)}</span>` : '')
            + '</span>'
            + (werkzeuge.length
                ? '<span class="eintragswerkzeuge">'
                  + werkzeuge.map(was => `<button class="knopf-schmal" data-tun="${was}" title="${Htmltext.t(Figurwahlzeile.WERKZEUGE[was].titel)}">`
                                         + `<i class="fas ${Figurwahlzeile.WERKZEUGE[was].symbol}"></i></button>`).join('')
                  + '</span>'
                : '');
    }
}
