import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { Laufwache } from '../gemeinsam/laufwache.js';
import { GarmentcodeAbbruch } from './garmentcode_abbruch.js';

/**
 * GarmentcodeLauf — den Reiter besetzen, die Knöpfe sperren, den Lauf
 * abbrechen.
 *
 * Herausgelöst aus `garmentcode_ablauf.js` (20.09.2026), als der
 * Abbrechen-Knopf dazukam (Edgar: „bei 2D+3D bauen soll es einen
 * Abbrechen-Button geben. Sobald bauen gestartet ist, sollen die
 * Bauen-Buttons deaktiviert sein") — die Datei stand bei 299 Zeilen.
 * Beide Wege, Einzelbau (`GarmentcodeAblauf.bauen`) und gemeinsamer Lauf
 * (`GarmentcodeGemeinsam.bauen`), gehen hier durch: EIN Ort, der weiß,
 * welche Knöpfe während eines Laufs grau sind und welcher aktiv wird.
 *
 * Die Entscheidung „darf ein Lauf starten" trifft `Laufwache` (ohne DOM,
 * deshalb prüfbar); hier steht nur, was der Nutzer davon sieht.
 */
export class GarmentcodeLauf {

    /**
     * Alle Knöpfe, die während eines Laufs grau sind — EINE Liste.
     *
     * `gc-kombi-bauen` gehört dazu (09.09.2026): Der gemeinsame Lauf
     * benutzt dieselbe `Laufwache`, und ein Knopf, der klickbar aussieht,
     * verspricht etwas, das erst die Wache abweist.
     */
    static KNOEPFE = ['gc-vorschau-2d', 'gc-vorschau-3d', 'gc-bauen-2d',
                      'gc-bauen-3d', 'gc-bauen-beides', 'gc-kombi-bauen'];

    /** Der eine Knopf, der NUR während eines Laufs geht. */
    static ABBRECHEN = 'gc-abbrechen';

    static knoepfe() {
        return GarmentcodeLauf.KNOEPFE
            .map((k) => document.getElementById(k)).filter(Boolean);
    }

    /**
     * Ist der Reiter frei — und wenn nicht, sagt er es.
     *
     * @returns den Stand der `Laufwache` (`{darf, grund, seit}`)
     *
     * Früher stand an dieser Stelle `if (reiter.laeuft) return;` — stumm,
     * und damit die Ursache des Befundes vom 08.09.2026.
     */
    static frei(reiter, meldung) {
        const stand = Laufwache.pruefen(reiter);
        if (stand.grund === 'besetzt' && meldung) {
            meldung.textContent = `Es läuft noch ein Bau (seit ${stand.seit} s) `
                + '— „Abbrechen" beendet ihn, sonst kommen die Knöpfe von selbst zurück.';
        } else if (stand.grund === 'verloren' && meldung) {
            meldung.textContent = `Der vorige Bau meldet sich seit ${stand.seit} s `
                + 'nicht mehr — er gilt als verloren, dieser Klick übernimmt.';
        }
        return stand;
    }

    /**
     * Den Reiter besetzen, die Bau-Knöpfe sperren, „Abbrechen" freigeben.
     *
     * @returns die Laufnummer (`Laufwache`), für `beenden`
     */
    static beginnen(reiter, knoepfe = GarmentcodeLauf.knoepfe()) {
        const lauf = Laufwache.beginnen(reiter);
        reiter.abbruch = new GarmentcodeAbbruch();
        knoepfe.forEach((k) => { k.disabled = true; });
        GarmentcodeLauf.abbrechenKnopf(true);
        return lauf;
    }

    /** Freigeben — nur, wenn dieser Lauf noch der aktuelle ist. */
    static beenden(reiter, knoepfe = GarmentcodeLauf.knoepfe(), lauf = undefined) {
        if (!Laufwache.beenden(reiter, lauf)) return false;
        reiter.abbruch = null;
        knoepfe.forEach((k) => { k.disabled = false; });
        GarmentcodeLauf.abbrechenKnopf(false);
        garmentcodeFortschritt.beenden();
        return true;
    }

    /**
     * Der Abbrechen-Knopf: Signal im Browser, Prozess auf dem Server.
     *
     * Die Knöpfe kommen über das `finally` des Laufs zurück, sobald der
     * abgebrochene Abruf wirft — nicht hier, sonst gäbe ein Klick den
     * Reiter frei, während der alte Lauf noch auf seine Antwort wartet.
     */
    static async abbrechen(reiter) {
        const abbruch = reiter.abbruch;
        const meldung = document.getElementById('gc-meldung');
        if (!abbruch) {
            if (meldung) meldung.textContent = 'Es läuft gerade kein Bau.';
            return [];
        }
        GarmentcodeLauf.abbrechenKnopf(false);
        if (meldung) meldung.textContent = 'Breche ab …';
        const ergebnisse = await abbruch.abbrechen();
        if (meldung) {
            meldung.textContent = GarmentcodeLauf.abbruchText(ergebnisse);
        }
        return ergebnisse;
    }

    /** Was der Server zum Abbruch sagt, in einem Satz. */
    static abbruchText(ergebnisse) {
        if (ergebnisse.includes('beendet')) {
            return 'Abgebrochen — die Simulation wurde beendet.';
        }
        if (ergebnisse.some((e) => String(e).startsWith('fehler:'))) {
            return 'Abgebrochen im Browser; der Server war nicht erreichbar '
                + `(${ergebnisse.join(', ')}).`;
        }
        return 'Abgebrochen — auf dem Server lief nichts mehr.';
    }

    /** „Abbrechen" ist nur während eines Laufs klickbar. */
    static abbrechenKnopf(aktiv) {
        const knopf = document.getElementById(GarmentcodeLauf.ABBRECHEN);
        if (knopf) knopf.disabled = !aktiv;
    }
}
