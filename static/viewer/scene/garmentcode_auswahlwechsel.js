import { garmentcodePreset } from './garmentcode_preset.js';

/**
 * GarmentcodeAuswahlwechsel — Häkchen und Kleiderbibliothek schließen sich aus.
 *
 * Edgar, 24.09.2026: „Ich verstehe das Garment Code UI nicht, wenn ich eine
 * Schuhart ausgewählt habe UND ein Teil einer Kleiderbibliothek — was wird dann
 * gebaut? Bei Klick auf ein Item oben (z.B. Ballerina) müsste doch die Selektion
 * der Kleiderbibliothek wegmachen? Umgekehrt, wenn ich aus der Kleiderbibliothek
 * etwas auswähle, müssten die Checkboxen oben alle ausgehen."
 *
 * Gebaut wurde immer, was in den Reglern stand, also das zuletzt Geklickte. Die
 * Anzeige log aber: Ballerina blieb angehakt, wenn danach „Crudehighsocks" die
 * Regler stellte, weil `pruefen` ein Häkchen nur an seinem KERN misst
 * (`meta.feet`), und den ließ das Vorbild stehen. Der Name des Stücks kam vom
 * Vorbild (`GarmentcodeTitel`: Vorbild vor Form), das Bild zeigte beides.
 *
 * Jetzt: Ein Häkchen setzen hebt die Wahl in der Bibliothek auf; ein Vorbild
 * wählen nimmt alle Häkchen weg, ohne die Werte anzufassen (das Vorbild hat die
 * Regler schon vollständig gestellt, `GarmentcodeVorbilder._reglerStellen`).
 * Beide Hörer sitzen am Dokument und laufen NACH den eigenen Hörern von Kästchen
 * und Knopf (Bubbling), also wenn deren Werte schon stehen.
 */
export class GarmentcodeAuswahlwechsel {

    static verdrahten() {
        document.addEventListener('change', (ereignis) => {
            const kaestchen = ereignis.target;
            if (kaestchen?.matches?.('input[data-preset]') && kaestchen.checked) {
                GarmentcodeAuswahlwechsel.vorbildAbwaehlen();
            }
        });
        document.addEventListener('click', (ereignis) => {
            const knopf = ereignis.target?.closest?.('#gc-vorbilder .vorbild-knopf');
            if (knopf) garmentcodePreset.alleAbhaken();
        });
    }

    /** Kein Vorbild der Kleiderbibliothek mehr gewählt; gibt zurück, ob eines gewählt war. */
    static vorbildAbwaehlen() {
        const aktive = document.querySelectorAll('#gc-vorbilder .vorbild-knopf.active');
        for (const knopf of aktive) knopf.classList.remove('active');
        return aktive.length > 0;
    }
}

GarmentcodeAuswahlwechsel.verdrahten();
