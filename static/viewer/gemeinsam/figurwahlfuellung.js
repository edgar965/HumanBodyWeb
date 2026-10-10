import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { Figurkataloge } from './figurkataloge.js';
import { Figurwahlbereiche } from './figurwahlbereiche.js';
import { Figurwahlimporte } from './figurwahlimporte.js';

/**
 * Figurwahlfuellung — die Listen eines Reiters des Figurwahl-Dialogs füllen: erst die Modelle, dann die abgebrochenen Importe (10.10.2026).
 *
 * ANLASS (Edgar, 10.10.2026): „warum dauert das Aufbauen des Dialogs so lange?" — der Genesis-9-Reiter stand auf „Lade …", bis AUCH die Liste der
 * verwaisten Importe da war. Gemessen im `client.log` (`/api/character/blendimport/verwaist/`): 1,5 s, 3,6 s, 10,4 s, 12,8 s, 19,4 s, 41,1 s, während
 * die Modelle selbst (`/api/character/genesis9-figur/`) 0,3–1,2 s brauchten (5 s bei belegtem Server). Die Modelle stehen jetzt, sobald sie da sind;
 * die Importe kommen nach und werden dazugestellt. Ein neuer Aufruf für denselben Reiter (Löschen, Umbenennen) macht die späte Antwort des alten
 * wertlos (`stand`).
 *
 * Aus `figurwahldialog.js` herausgelöst (die Datei stand bei 296 Zeilen): hier nur das Holen und Verteilen; was eine Zeile tut, die Wahl und die
 * Pflege bleiben beim Dialog (`dialog._zeile`, `_waehlen`, `_pflegen`).
 */
export class Figurwahlfuellung {

    /** @param dialog  der `Figurwahldialog`, dessen Listen gefüllt werden */
    constructor(dialog) {
        this.dialog = dialog;
        this.stand = {};
    }

    async fuellen(quelle) {
        const behaelter = this.dialog._liste(quelle);
        if (!behaelter) return;
        const lauf = this.stand[quelle] = (this.stand[quelle] || 0) + 1;
        Figurwahlbereiche.meldung(behaelter,
            '<li class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade …</li>');
        let eintraege;
        try {
            eintraege = await Figurkataloge.modelle(quelle);
        } catch (fehler) {
            Figurwahlbereiche.meldung(behaelter,
                `<li class="fehlertext">Fehler: ${Htmltext.t(fehler.message)}</li>`);
            return;
        }
        // Die Importe erst jetzt anfragen: der Server bearbeitet die Anfragen nacheinander, die Modelle gehen vor.
        const importe = Figurwahlimporte.zeilen(quelle);
        this._zeigen(quelle, behaelter, eintraege);
        const verwaiste = await importe;
        if (verwaiste.length && this.stand[quelle] === lauf) {
            this._zeigen(quelle, behaelter, [...eintraege, ...verwaiste]);
        }
    }

    _zeigen(quelle, behaelter, eintraege) {
        const dialog = this.dialog;
        Figurwahlbereiche.verteilen(behaelter, eintraege,
                                    eintrag => dialog._zeile(eintrag, quelle),
                                    Figurkataloge.QUELLEN[quelle].leer);
        Figurwahlimporte.aufraeumen(behaelter, eintraege.filter(e => e.verwaist).length,
                                    () => dialog._pflegen(quelle, null, 'verwaisteLoeschen'));
        // Die Zeilen sind neu gebaut: eine schon getroffene Wahl muss wieder markiert werden.
        if (dialog.gewaehlt) dialog._waehlen(dialog.gewaehlt);
        // Die Listen kommen nebenläufig; vorwählen nur im offenen Reiter.
        else if (quelle === dialog.quelle) dialog._einzelnenVorwaehlen(quelle);
    }
}
