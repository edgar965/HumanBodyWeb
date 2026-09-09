import { Fristabruf } from '../gemeinsam/fristabruf.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { garmentcodeRegler } from './garmentcode_regler.js';

/**
 * GarmentcodeSchnitt — der 2D-Teil: aus Maßen und Reglern ein Schnittmuster.
 *
 * EIGENER SCHRITT, EIGENER KNOPF (Edgar, 07.09.2026: „Mach einen zusatz
 * Button bei Garment Code: „2D" in dem erst das 2D Modell erstellt wird als
 * separater Schritt, das sollte ja relativ schnell gehen, oder?").
 *
 * Ja — gemessen am Server-Log: `/api/garmentcode/erzeugen/` braucht **6,12 s**,
 * die Drapierung danach rund 22 s und das Anziehen 3 s. Wer am Schnitt
 * schraubt (71 Regler beim T-Shirt), sieht das Ergebnis damit in einem
 * Fünftel der Zeit; der lange Teil kommt erst, wenn der Schnitt sitzt.
 *
 * WARUM ALS EIGENES MODUL: `garmentcode.js` stand bei 290 Zeilen, und die
 * Regel ist, dass eine Datei beim Anfassen nicht über ihre Grenze wächst
 * (`~/.claude/rules/struktur.md`). Der Schnittteil war der geschlossenste
 * Block darin — Anfrage, Vorschaubild, Meldungstext — und steht jetzt hier.
 * `bauen()` im Reiter ruft ihn und hängt die Drapierung an; `nurSchnitt()`
 * hört danach auf.
 */
export class GarmentcodeSchnitt {

    /**
     * Den Schnitt konstruieren und anzeigen.
     *
     * @param reiter    der `GarmentcodeReiter` (für `figurdaten`/`ohneMorphs`)
     * @param figur     die gewählte Figur
     * @param meldung   das Meldungsfeld
     * @returns das Ergebnis des Servers, oder `null` bei einem Fehler
     *          (die Meldung steht dann schon im Feld)
     */
    static async bauen(reiter, figur, meldung) {
        garmentcodeFortschritt.laeuft('schnitt');

        const daten = reiter.figurdaten(figur);
        daten.append('vorlage', document.getElementById('gc-vorlage').value);
        daten.append('regler', garmentcodeRegler.alsJson());
        // Gemessen 0,2 bis 14 s; 60 s sind reichlich. Ohne Frist bliebe
        // der Reiter besetzt, wenn die Antwort ausbleibt (09.09.2026).
        const ergebnis = await Fristabruf.formular(
            '/api/garmentcode/erzeugen/', daten, 60);

        if (ergebnis.fehler) {
            garmentcodeFortschritt.gescheitert('schnitt', 'Fehler');
            meldung.textContent = `Fehlgeschlagen: ${ergebnis.fehler}`;
            return null;
        }
        garmentcodeFortschritt.fertig('schnitt', ergebnis.name || 'fertig');
        meldung.textContent = GarmentcodeSchnitt.text(ergebnis, reiter);
        return ergebnis;
    }

    /**
     * Was unter dem Balken steht.
     *
     * Die beiden Warnungen sind keine Zierde: „durchdringt sich selbst"
     * heißt, dass die Simulation danach unbrauchbar wird, und „ohne Morphs"
     * sagt, dass der GRUNDkörper vermessen wurde — ein Bau aus dem Browser
     * ohne geladene Figur hat am 06.09.2026 eine Stunde Messläufe
     * verdorben, weil der Ergebnisordner still einen Grundkörper-Schnitt
     * trug.
     */
    static text(ergebnis, reiter) {
        const warnung = ergebnis.selbstdurchdringend
            ? ' — Achtung: Schnitt durchdringt sich selbst' : '';
        const eigene = garmentcodeRegler.anzahl;
        const zusatz = eigene ? ` (${eigene} eigene Einstellungen)` : '';
        const grundkoerper = reiter.ohneMorphs
            ? ' — Achtung: Figur ohne Morphs, vermessen wurde der Grundkörper'
            : '';
        return `Schnitt fertig: ${ergebnis.name}${zusatz}${warnung}${grundkoerper}`;
    }

}
