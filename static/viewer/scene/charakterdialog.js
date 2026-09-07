import { closeDialog, escapeHtml, openDialog } from './utils.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Katalogpflege } from './katalogpflege.js';
import { Figurplatzierung } from './figurplatzierung.js';
import { Umakatalog } from './uma/umakatalog.js';
import { Smplkatalog } from './smpl/smplkatalog.js';
import { Mhkatalog } from './makehuman/mhkatalog.js';

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
 * Was je Reiter anders ist, steht in ZWEI Tabellen — `QUELLEN` (Liste,
 * Leertext, Pflege) und `LADER` (wer die Figur in die Szene stellt). Der Rest
 * des Dialogs kennt die Figurarten nicht.
 *
 * Dazu Position und Größe der neuen Figur, mit den Vorgaben aus
 * `Figurplatzierung`: 1,5 m rechts neben der vorhandenen und auf deren Höhe.
 */
export class Charakterdialog {

    static QUELLEN = {
        uma: { liste: 'uma-list', leer: 'Keine UMA-Figur im Katalog (Figuren/uma/).' },
        modell: { liste: 'preset-list', leer: 'Keine Modelle vorhanden.' },
        // SMPL-Referenzkörper von GarmentCode (06.09.2026): Upstream-Dateien,
        // deshalb ohne Umbenennen und Löschen.
        smpl: { liste: 'smpl-list', leer: 'Keine SMPL-Körper im GarmentCode-Klon.', pflege: false },
        // MakeHuman-Basiskörper (06.09.2026): eine Datei des Projekts, deshalb
        // ebenfalls ohne Umbenennen und Löschen.
        makehuman: { liste: 'mh-figur-list', leer: 'MakeHuman/base.obj fehlt.', pflege: false },
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
    };

    static _quelle = 'uma';
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
        await Promise.all([Charakterdialog._umaFuellen(), Charakterdialog._modelleFuellen(),
                           Charakterdialog._smplFuellen(), Charakterdialog._mhFuellen()]);
    }

    // -- Reiter ---------------------------------------------------------------

    static _umschalten(quelle) {
        Charakterdialog._quelle = quelle;
        for (const knopf of document.querySelectorAll('#add-char-reiter .dialogreiter-knopf')) {
            knopf.classList.toggle('active', knopf.dataset.quelle === quelle);
        }
        for (const [name, angaben] of Object.entries(Charakterdialog.QUELLEN)) {
            document.getElementById(angaben.liste)
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
        const liste = document.getElementById(
            Charakterdialog.QUELLEN[quelle]?.liste);
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

    static async _umaFuellen() {
        const liste = document.getElementById('uma-list');
        if (!liste) return;
        await Charakterdialog._fuellen(liste, 'uma', async () => {
            const figuren = await Umakatalog.liste();
            return figuren.map(f => ({
                name: f.name,
                anzeige: f.name.replace(/\.glb$/i, ''),
                unterzeile: `${f.geschlecht} · ${(f.bytes / 1048576).toFixed(1)} MB · ${f.stand}`,
            }));
        });
    }

    static async _modelleFuellen() {
        const liste = document.getElementById('preset-list');
        if (!liste) return;
        await Charakterdialog._fuellen(liste, 'modell', async () => {
            const daten = await Serverabruf.json('/api/character/models/');
            return (daten.presets || []).map(p => ({
                name: p.name, anzeige: p.label || p.name, unterzeile: '',
            }));
        });
    }

    static async _smplFuellen() {
        const liste = document.getElementById('smpl-list');
        if (!liste) return;
        await Charakterdialog._fuellen(liste, 'smpl', async () => {
            const figuren = await Smplkatalog.liste();
            return figuren.map(f => ({
                name: f.name,
                anzeige: f.anzeige || f.name,
                unterzeile: `${f.geschlecht} · ${f.smpl ? 'SMPL' : 'GarmentCode-Modell'} · `
                    + (f.masse_vorhanden ? 'Maße vorgegeben' : 'ohne Maße'),
            }));
        });
    }

    static async _mhFuellen() {
        const liste = document.getElementById('mh-figur-list');
        if (!liste) return;
        await Charakterdialog._fuellen(liste, 'makehuman', async () => {
            const figuren = await Mhkatalog.liste();
            return figuren.map(f => ({
                name: f.name,
                anzeige: f.anzeige || f.name,
                unterzeile: `${f.punkte.toLocaleString()} Punkte · `
                    + `${(f.hoehe * 100).toFixed(1)} cm · `
                    + 'Kleidung sitzt ohne Nacharbeit',
            }));
        });
    }

    static async _fuellen(liste, quelle, holen) {
        liste.innerHTML = '<li class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade …</li>';
        let eintraege;
        try {
            eintraege = await holen();
        } catch (fehler) {
            liste.innerHTML = `<li class="fehlertext">Fehler: ${escapeHtml(fehler.message)}</li>`;
            return;
        }
        liste.innerHTML = '';
        if (!eintraege.length) {
            liste.innerHTML = `<li class="gedaempft">${Charakterdialog.QUELLEN[quelle].leer}</li>`;
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
        const li = document.createElement('li');
        li.dataset.name = eintrag.name;
        const pflege = Charakterdialog.QUELLEN[quelle]?.pflege !== false;
        li.innerHTML = `<span class="eintragsname">${escapeHtml(eintrag.anzeige)}`
            + (eintrag.unterzeile
                ? `<span class="preset-sub">${escapeHtml(eintrag.unterzeile)}</span>` : '')
            + '</span>'
            + (pflege
                ? '<span class="eintragswerkzeuge">'
                  + '<button class="knopf-schmal" data-tun="umbenennen" title="Umbenennen">'
                  + '<i class="fas fa-pen"></i></button>'
                  + '<button class="knopf-schmal" data-tun="loeschen" title="Löschen">'
                  + '<i class="fas fa-trash"></i></button></span>'
                : '');
        li.addEventListener('click', (ereignis) => {
            if (ereignis.target.closest('[data-tun]')) return;   // Werkzeug, keine Wahl
            Charakterdialog._waehlen({ quelle, name: eintrag.name });
        });
        li.addEventListener('dblclick', async (ereignis) => {
            if (ereignis.target.closest('[data-tun]')) return;
            closeDialog(document.getElementById('add-char-dialog'));
            await Charakterdialog._laden({ quelle, name: eintrag.name });
        });
        li.querySelector('[data-tun="umbenennen"]')?.addEventListener(
            'click', () => Charakterdialog._pflegen(quelle, eintrag.name, 'umbenennen'));
        li.querySelector('[data-tun="loeschen"]')?.addEventListener(
            'click', () => Charakterdialog._pflegen(quelle, eintrag.name, 'loeschen'));
        return li;
    }

    // -- Umbenennen, Löschen, Laden -------------------------------------------

    static async _pflegen(quelle, name, was) {
        try {
            const geschehen = await Katalogpflege[was](quelle, name);
            if (!geschehen) return;
            Charakterdialog._waehlen(null);
            await (quelle === 'uma'
                ? Charakterdialog._umaFuellen() : Charakterdialog._modelleFuellen());
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
