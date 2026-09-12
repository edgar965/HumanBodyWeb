import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { _selectedInst } from '../utils.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { MhFigur } from './mhfigur.js';
import { Mheigenschaften } from './mheigenschaften.js';
import { Stueckbedienung } from '../stueckbedienung.js';

/**
 * Mhanwenden — ein Knopf, der das gewählte Stück auf die gewählte Figur bringt.
 *
 * WARUM (Edgar, 07.09.2026): „Die MakeHuman Clothes funktionieren irgendwie
 * nicht. Kannst Du im Tab Assets - MakeHuman ganz oben den Button einfügen,
 * mit dem das ausgewählte Asset auf das ausgewählte Modell angewendet wird?
 * Ich verstehe das UI nicht mehr, das ist zu komplex."
 *
 * ES WAREN ZWEI DINGE, UND DAS ZWEITE WAR EIN ECHTER FEHLER
 * =========================================================
 * 1. Der Knopf „1. Erzeuge (Proxy)" stand UNTER der Liste und sieben Reglern,
 *    daneben ein „2. Push Outside" — zwei nummerierte Schritte für das, was
 *    man mit einem Wort meint: anziehen.
 * 2. Auf einer MakeHuman-Figur ging er in einen Fehler. Er schickt
 *    `body_type` an `/api/character/mh-proxy-fit/`, und der Server rechnet
 *    daraus einen HumanBody-Körper. Mit `body_type=MakeHuman · Basisnetz`
 *    antwortet er **500 „Failed to compute body mesh"** (nachgestellt am
 *    07.09.2026 mit curl). `Mhproxynetz.anpassen` fängt das ab und schreibt
 *    eine Zeile in die Browserkonsole — auf dem Bildschirm passiert nichts.
 *
 * DIESER KNOPF WÄHLT DEN WEG NACH DER FIGUR:
 *
 *     MakeHuman-Figur  ->  `MhFigur.anziehen` — die `.mhclo`-Zuordnung gilt
 *                          unmittelbar, kein Regler, kein Nachschieben. Die
 *                          Haut darunter wird ausgeblendet.
 *     alles andere     ->  der bisherige Proxy-Fit mit seinen Reglern.
 *
 * Und er sagt, was er getan hat. Ein Knopf, der stumm nichts tut, ist der
 * Grund, warum diese Meldung überhaupt nötig war.
 */
export class Mhanwenden {

    static KNOPF = 'mh-anwenden';
    static ABNEHMEN = 'mh-abnehmen';
    static STAND = 'mh-anwenden-stand';

    static verdrahten() {
        document.getElementById(Mhanwenden.KNOPF)
            ?.addEventListener('click', () => Mhanwenden.anwenden());
        document.getElementById(Mhanwenden.ABNEHMEN)
            ?.addEventListener('click', () => Mhanwenden.abnehmen());
        // Die Zeile unter dem Knopf nennt Stück und Figur. Beides ändert sich
        // an anderer Stelle: in der Kleiderliste und in der Charakterliste.
        fn.mhAuswahlGeaendert = () => Mhanwenden.angleichen();
        document.querySelector('.panel-tabs')
            ?.addEventListener('click', () => Mhanwenden.angleichen());
        document.getElementById('character-list')
            ?.addEventListener('click', () => setTimeout(
                () => Mhanwenden.angleichen(), 0));
        Mhanwenden.angleichen();
    }

    // ------------------------------------------------------------- Anzeige

    /** Was gerade gewählt ist — und ob der Knopf etwas tun kann. */
    static angleichen() {
        const knopf = document.getElementById(Mhanwenden.KNOPF);
        if (!knopf) return;
        const figur = _selectedInst();
        const kennung = state._selectedMHId;
        knopf.disabled = !figur || !kennung;
        Mhanwenden._stand(Mhanwenden._lage(figur, kennung));
    }

    static _lage(figur, kennung) {
        if (!figur) return 'Erst einen Charakter wählen.';
        if (!kennung) return 'Erst ein Kleidungsstück in der Liste wählen.';
        const art = figur.quelle === MhFigur.QUELLE
            ? 'sitzt exakt (.mhclo)' : 'Proxy-Fit mit den Reglern unten';
        return `${Mhanwenden._kurz(kennung)} → ${figur.presetName} · ${art}`;
    }

    static _stand(text, fehler = false) {
        const zeile = document.getElementById(Mhanwenden.STAND);
        if (!zeile) {
            (fehler ? Protokoll.fehler : Protokoll.warnung)('mhanwenden', text);
            return;
        }
        zeile.className = fehler ? 'fehlertext' : 'hb-font-size-0-72rem';
        zeile.textContent = text;
    }

    static _kurz(kennung) {
        return String(kennung).split('/').pop().replace(/_/g, ' ');
    }

    // ------------------------------------------------------------ Anwenden

    static async anwenden() {
        const figur = _selectedInst();
        const kennung = state._selectedMHId;
        if (!figur || !kennung) {
            Mhanwenden.angleichen();
            return null;
        }
        const knopf = document.getElementById(Mhanwenden.KNOPF);
        if (knopf) knopf.disabled = true;
        Mhanwenden._stand(`${Mhanwenden._kurz(kennung)} wird angezogen …`);
        try {
            return figur.quelle === MhFigur.QUELLE
                ? await Mhanwenden._aufMakehuman(figur, kennung)
                : await Mhanwenden._aufHumanbody(figur, kennung);
        } catch (fehler) {
            Protokoll.fehler('MhAnwenden', kennung, fehler);
            Mhanwenden._stand(`Nicht möglich: ${fehler.message}`, true);
            return null;
        } finally {
            if (knopf) knopf.disabled = false;
        }
    }

    /** Die exakte Zuordnung — und die Haut darunter fällt weg. */
    static async _aufMakehuman(figur, kennung) {
        await figur.anziehen(kennung);
        await Mheigenschaften.nachKleiderwechsel(figur);
        Mhanwenden._stand(
            `${Mhanwenden._kurz(kennung)} sitzt auf ${figur.presetName} — `
            + 'exakt über die .mhclo-Zuordnung, ohne Nacharbeit.');
        return figur;
    }

    /**
     * Der bisherige Weg mit den Reglern.
     *
     * GEPRÜFT WIRD AM ERGEBNIS, nicht an der Rückgabe: `Mhproxynetz.anpassen`
     * gibt bei einem Serverfehler `null` zurück und protokolliert nur. Ob das
     * Stück wirklich an der Figur hängt, steht in `clothMeshes` — und genau
     * das ist die Frage, die der Benutzer hat.
     */
    static async _aufHumanbody(figur, kennung) {
        await fn._doMHProxyFit();
        if (!figur.clothMeshes[`mh_${kennung}`]) {
            Mhanwenden._stand(
                `${Mhanwenden._kurz(kennung)} ließ sich auf `
                + `„${figur.bodyType}" nicht anpassen — dieser `
                + 'Weg braucht eine HumanBody-Figur.', true);
            return null;
        }
        Mhanwenden._stand(`${Mhanwenden._kurz(kennung)} auf `
                          + `${figur.presetName} angepasst (Proxy-Fit).`);
        return figur;
    }

    // ------------------------------------------------------------ Abnehmen

    /**
     * Alle MakeHuman-Stücke von der gewählten Figur nehmen.
     *
     * ZWEI VORSILBEN, UND DAS WAR DER FEHLER DES ALTEN KNOPFES: Die Stücke
     * einer HumanBody-Figur heißen `mh_<kennung>`, die einer MakeHuman-Figur
     * `mhk_<kennung>` (siehe `Mhkleidstueck.schluessel` — `mh_` schaltet in
     * `properties._updatePropContext` den Fit-Regler-Reiter auf, der hier
     * nichts zu suchen hat). „Alle entfernen" kannte nur `mh_` und tat auf
     * einer MakeHuman-Figur nichts, ohne es zu sagen.
     */
    static async abnehmen() {
        const figur = _selectedInst();
        if (!figur) {
            Mhanwenden._stand('Erst einen Charakter wählen.');
            return 0;
        }
        const anzahl = figur.quelle === MhFigur.QUELLE
            ? await Mhanwenden._alleVonMakehuman(figur)
            : Mhanwenden._alleVonHumanbody(figur);
        Mhanwenden._stand(anzahl
            ? `${anzahl} MakeHuman-Stück${anzahl === 1 ? '' : 'e'} von `
              + `${figur.presetName} abgenommen.`
            : `${figur.presetName} trägt keine MakeHuman-Stücke.`);
        return anzahl;
    }

    static async _alleVonMakehuman(figur) {
        const getragen = figur.getragen();
        for (const kennung of getragen) figur.ausziehen(kennung);
        if (getragen.length) await Mheigenschaften.nachKleiderwechsel(figur);
        return getragen.length;
    }

    static _alleVonHumanbody(figur) {
        const schluessel = Object.keys(figur.clothMeshes || {})
            .filter(name => name.startsWith('mh_'));
        Stueckbedienung.alleMitVorsilbe('mh_');
        return schluessel.length;
    }
}

fn.mhAnwenden = Mhanwenden.anwenden;
fn.mhAnwendenVerdrahten = Mhanwenden.verdrahten;
