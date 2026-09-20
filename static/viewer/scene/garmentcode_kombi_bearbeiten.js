import { garmentcodeRegler } from './garmentcode_regler.js';
import { garmentcodePreset } from './garmentcode_preset.js';
import { GarmentcodeBauregler } from './garmentcode_bauregler.js';

/**
 * GarmentcodeKombiBearbeiten — einen Eintrag der Kombination in den Reiter
 * laden, damit man ihn nachträglich ändert.
 *
 * Edgar, 20.09.2026: „bei «Mehrere Stücke gemeinsam» kann ich die
 * Eigenschaften des Stücks nicht mehr nachträglich ändern. Fixe."
 *
 * Bis dahin war ein Eintrag ein Abzug ohne Rückweg (Begründung im Kopf von
 * `garmentcode_kombi.js`: zwei Quellen für dieselben Zahlen). Der Rückweg
 * geht deshalb GENAU EINMAL in eine Richtung: Der Eintrag wird in den
 * Reiter geladen, dort geändert, und „Übernehmen" schreibt ihn an seiner
 * Stelle zurück (`Kombiliste.ersetzen`). Der Eintrag selbst folgt keinem
 * Reglerzug — er ist erst wieder aktuell, wenn übernommen wurde; solange
 * ist er in der Liste markiert.
 *
 * WIE DER STAND IN DEN REITER KOMMT: Die Vorlage wird wie von Hand gewählt
 * (das `change`-Ereignis, damit alles mitläuft, was daran hängt), dann
 * wird auf die Regler dieser Vorlage gewartet — `laden` stellt dabei das
 * Gedächtnis der Vorlage her, nicht den Eintrag. Deshalb danach: alle
 * Abweichungen auf die Vorgabe, die Werte des Eintrags darüber
 * (`mehrereSetzen` zieht die Schieber nach, merkt, stößt den Live-Bau an),
 * die Häkchen geprüft, die Bauwerte gestellt. Das Material bleibt, wo es
 * ist: Es hängt am getragenen Stück, und das nimmt „Übernehmen" zuerst.
 */
export class GarmentcodeKombiBearbeiten {

    /**
     * Den Eintrag in den Reiter laden.
     *
     * @param eintrag  {vorlage, titel, regler, bau, material}
     * @returns true, wenn die Regler der Vorlage stehen
     */
    static async laden(eintrag) {
        if (!eintrag?.vorlage) return false;
        const auswahl = document.getElementById('gc-vorlage');
        if (auswahl && auswahl.value !== eintrag.vorlage) {
            auswahl.value = eintrag.vorlage;
            auswahl.dispatchEvent(new Event('change', { bubbles: true }));
        }
        await garmentcodeRegler.laden(eintrag.vorlage);
        if (garmentcodeRegler.fuerVorlage !== eintrag.vorlage) return false;
        GarmentcodeKombiBearbeiten.reglerStellen(eintrag.regler || {});
        GarmentcodeBauregler.stellen(eintrag.bau || {});
        return true;
    }

    /**
     * Die Abweichungen des Reiters durch die des Eintrags ersetzen und die
     * Häkchen daran prüfen — ein Preset, dessen Werte der Eintrag nicht
     * trägt, darf nicht gehakt stehen bleiben.
     */
    static reglerStellen(regler) {
        const vorher = Object.keys(garmentcodeRegler.werte);
        garmentcodeRegler.zuruecksetzen(vorher);
        garmentcodeRegler.mehrereSetzen(regler);
        const liest = (p) => garmentcodeRegler.wertVon(p);
        for (const pfad of new Set([...vorher, ...Object.keys(regler)])) {
            garmentcodePreset.pruefen(pfad, liest);
        }
        return Object.keys(regler).length;
    }
}
