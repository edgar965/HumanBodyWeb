import { closeDialog, escapeHtml, openDialog } from './utils.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Figurkataloge } from '../gemeinsam/figurkataloge.js';
import { Figurwahlzeile } from '../gemeinsam/figurwahlzeile.js';
import { Katalogpflege } from './katalogpflege.js';
import { Figurplatzierung } from './figurplatzierung.js';
import { Umakatalog } from './uma/umakatalog.js';
import { Smplkatalog } from './smpl/smplkatalog.js';
import { Mhkatalog } from './makehuman/mhkatalog.js';
import { Umapythonkatalog } from './umapython/umapythonkatalog.js';

/**
 * Charakterdialog — „Charakter hinzufügen", ein Reiter je Figurart.
 *
 * WARUM (Edgar, 06.09.2026): „mach zwei Tabs, einmal UMA, einmal HumanBody.
 * Mach auch Möglichkeiten zum Umbenennen und Löschen der Modelle aus dem
 * Dialog." Vorher standen beide Listen untereinander; unter 21 Modellen war
 * die UMA-Liste nicht zu finden, und wer eine Figur loswerden wollte, musste
 * in den Ordner. Aus zwei Reitern sind am selben Tag vier geworden:
 * GarmentCode-Körper und MakeHuman kamen dazu.
 *
 * Was je Reiter anders ist, steht in ZWEI Tabellen — `Figurkataloge.QUELLEN`
 * (Abruf, Zeilen, Leertext, Pflege; seit dem 12.09.2026 mit dem Theatre
 * geteilt, vorher fünf eigene Kopien hier) und `LADER` (wer die Figur in
 * die Szene stellt). `LISTEN` nennt nur noch das Element je Reiter. Der
 * Rest des Dialogs kennt die Figurarten nicht.
 *
 * Dazu Position und Größe der neuen Figur, mit den Vorgaben aus
 * `Figurplatzierung`: 1,5 m rechts neben der vorhandenen und auf deren Höhe.
 */
export class Charakterdialog {

    /** Das Listenelement je Reiter in `_charakter_dialog.html`. */
    static LISTEN = {
        modell: 'preset-list',
        smpl: 'smpl-list',
        makehuman: 'mh-figur-list',
        uma: 'uma-list',
        umapython: 'umapython-list',
    };

    /**
     * Wer eine gewählte Zeile in die Szene stellt.
     *
     * Eine Tabelle statt eines verschachtelten Bedingungsausdrucks: Bei der
     * vierten Quelle war der drei Ebenen tief. `addCharacterFromPreset` kommt
     * aus der Registrierung und wird deshalb erst beim Aufruf geholt.
     */
    static LADER = {
        uma: (name, lage) => Umakatalog.hinzufuegen(name, lage),
        smpl: (name, lage) => Smplkatalog.hinzufuegen(name, lage),
        makehuman: (name, lage) => Mhkatalog.hinzufuegen(name, lage),
        modell: (name, lage) => fn.addCharacterFromPreset(name, lage),
        umapython: (name, lage) => Umapythonkatalog.hinzufuegen(name, lage),
    };

    /** Der Reiter, mit dem der Dialog aufgeht — muss zum `active`-Knopf
     *  in `_charakter_dialog.html` passen (Edgar, 07.09.2026:
     *  HumanBody, SMPL, MakeHuman, UMA). */
    static _quelle = 'modell';
    static _gewaehlt = null;

    static verdrahten() {
        const dialog = document.getElementById('add-char-dialog');
        document.getElementById('add-character-btn')
            ?.addEventListener('click', () => Charakterdialog.oeffnen());
        for (const knopf of document.querySelectorAll('#add-char-reiter .dialogreiter-knopf')) {
            knopf.addEventListener('click', () => Charakterdialog._umschalten(knopf.dataset.quelle));
        }
        document.getElementById('add-char-confirm')?.addEventListener('click', async () => {
            if (!Charakterdialog._gewaehlt) return;
            closeDialog(dialog);
            await Charakterdialog._laden(Charakterdialog._gewaehlt);
        });
    }

    static async oeffnen() {
        const dialog = document.getElementById('add-char-dialog');
        openDialog(dialog);
        Charakterdialog._waehlen(null);
        Charakterdialog._lageVorbelegen();
        await Promise.all(Object.keys(Charakterdialog.LISTEN)
            .map(quelle => Charakterdialog._fuellen(quelle)));
    }

    // -- Reiter ---------------------------------------------------------------

    static _umschalten(quelle) {
        Charakterdialog._quelle = quelle;
        for (const knopf of document.querySelectorAll('#add-char-reiter .dialogreiter-knopf')) {
            knopf.classList.toggle('active', knopf.dataset.quelle === quelle);
        }
        for (const [name, element] of Object.entries(Charakterdialog.LISTEN)) {
            document.getElementById(element)
                ?.classList.toggle('hb-versteckt', name !== quelle);
        }
        // Die Wahl gehört zum Reiter: wer umschaltet, wählt neu.
        Charakterdialog._waehlen(null);
        Charakterdialog._einzelnenVorwaehlen(quelle);
    }

    /**
     * Hat der Reiter genau EINEN Eintrag, ist er gewählt.
     *
     * WARUM (07.09.2026, Edgar: „hinzufügen von MakeHuman funktioniert
     * nicht"): Der MakeHuman-Reiter zeigt eine einzige Zeile — MakeHuman hat
     * genau ein Basisnetz. Sie sah aus wie eine Überschrift, nicht wie eine
     * Auswahl; „Hinzufügen" blieb gesperrt und tat auf den Klick nichts. Im
     * Serverlog stand deshalb der Dialogaufbau (alle vier Listen, 200) und
     * danach KEINE einzige Anfrage — ein Fehler, den man nur am Fehlen von
     * etwas erkennt.
     *
     * Bei mehreren Einträgen wird NICHT vorgewählt: Dort ist die Wahl eine
     * echte Entscheidung, und ein vorgewählter erster Eintrag lädt beim
     * schnellen Klick die falsche Figur.
     */
    static _einzelnenVorwaehlen(quelle) {
        const liste = document.getElementById(Charakterdialog.LISTEN[quelle]);
        const zeilen = liste ? liste.querySelectorAll('li[data-name]') : [];
        if (zeilen.length !== 1) return;
        Charakterdialog._waehlen({ quelle, name: zeilen[0].dataset.name });
    }

    static _waehlen(eintrag) {
        Charakterdialog._gewaehlt = eintrag;
        const knopf = document.getElementById('add-char-confirm');
        if (knopf) knopf.disabled = !eintrag;
        document.getElementById('add-char-hinweis')
            ?.classList.toggle('hb-versteckt', Boolean(eintrag));
        for (const liste of document.querySelectorAll('#add-char-dialog .preset-list')) {
            for (const li of liste.querySelectorAll('li')) {
                li.classList.toggle('selected',
                    Boolean(eintrag) && li.dataset.name === eintrag.name
                    && liste.dataset.quelle === eintrag.quelle);
            }
        }
    }

    // -- Lage der neuen Figur -------------------------------------------------

    static _lageVorbelegen() {
        const vorgabe = Figurplatzierung.vorgaben();
        const x = document.getElementById('add-char-x');
        const angleichen = document.getElementById('add-char-angleichen');
        if (x) x.value = vorgabe.x;
        if (angleichen) {
            angleichen.checked = vorgabe.angleichen;
            angleichen.disabled = !vorgabe.angleichen;
        }
    }

    static lage() {
        const x = document.getElementById('add-char-x');
        const angleichen = document.getElementById('add-char-angleichen');
        const vorgabe = Figurplatzierung.vorgaben();
        return {
            x: x ? Number(x.value) : vorgabe.x,
            angleichen: angleichen ? angleichen.checked : vorgabe.angleichen,
            vorbildHoehe: vorgabe.vorbildHoehe,
        };
    }

    // -- Listen ---------------------------------------------------------------

    static async _fuellen(quelle) {
        const liste = document.getElementById(Charakterdialog.LISTEN[quelle]);
        if (!liste) return;
        liste.innerHTML = '<li class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade …</li>';
        let eintraege;
        try {
            eintraege = await Figurkataloge.liste(quelle);
        } catch (fehler) {
            liste.innerHTML = `<li class="fehlertext">Fehler: ${escapeHtml(fehler.message)}</li>`;
            return;
        }
        liste.innerHTML = '';
        if (!eintraege.length) {
            liste.innerHTML = `<li class="gedaempft">${Figurkataloge.QUELLEN[quelle].leer}</li>`;
            return;
        }
        for (const eintrag of eintraege) {
            liste.appendChild(Charakterdialog._zeile(eintrag, quelle));
        }
        // Die Listen kommen nebenläufig; vorwählen nur für den Reiter, der
        // gerade offen ist.
        if (quelle === Charakterdialog._quelle && !Charakterdialog._gewaehlt) {
            Charakterdialog._einzelnenVorwaehlen(quelle);
        }
    }

    static _zeile(eintrag, quelle) {
        const pflege = Figurkataloge.QUELLEN[quelle].pflege;
        return Figurwahlzeile.bauen(eintrag, {
            waehlen: () => Charakterdialog._waehlen({ quelle, name: eintrag.name }),
            laden: async () => {
                closeDialog(document.getElementById('add-char-dialog'));
                await Charakterdialog._laden({ quelle, name: eintrag.name });
            },
            pflegen: pflege ? (was) => Charakterdialog._pflegen(quelle, eintrag.name, was) : null,
        });
    }

    // -- Umbenennen, Löschen, Laden -------------------------------------------

    static async _pflegen(quelle, name, was) {
        try {
            const geschehen = await Katalogpflege[was](quelle, name);
            if (!geschehen) return;
            Charakterdialog._waehlen(null);
            await Charakterdialog._fuellen(quelle);
        } catch (fehler) {
            alert(`Fehler: ${fehler.message}`);
        }
    }

    static async _laden({ quelle, name }) {
        const lage = Charakterdialog.lage();
        try {
            return await Charakterdialog.LADER[quelle](name, lage);
        } catch (fehler) {
            alert(`Fehler: ${fehler.message}`);
            return null;
        }
    }
}
