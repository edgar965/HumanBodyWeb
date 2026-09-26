import { Fristabruf } from '../gemeinsam/fristabruf.js';

/**
 * GarmentcodeAbbruch — ein laufender Bau, den der Nutzer beenden kann.
 *
 * WARUM (Edgar, 20.09.2026: „bei 2D+3D bauen soll es einen Abbrechen-Button
 * geben"): Ein Bau dauert 25 bis 65 s, und wer den falschen Knopf oder das
 * falsche Stück erwischt hat, konnte bisher nur warten. Zwei Seiten
 * gehören zum Abbruch, und beide sind nötig:
 *
 *   1. im Browser das `AbortSignal`, das den laufenden `fetch` und das
 *      Nachholen (`Antwortnachholen`) beendet — sonst liefe der Ablauf
 *      weiter bis zur Frist und hängte am Ende noch das Netz ein;
 *   2. auf dem Server der Simulationsprozess (`drapierlauf.py`), der
 *      sonst 30 s weiterrechnete und den Rechner belegte. Er hängt an
 *      der Kennung der Anfrage (`anfrage`, dieselbe wie für die
 *      Antwortablage); `Antwortnachholen.formular` meldet sie über
 *      `merken`, und `/api/garmentcode/abbrechen/` beendet ihn.
 *
 * Ein Objekt je Lauf (`GarmentcodeLauf.beginnen` legt es an, hängt es an
 * `reiter.abbruch`); die Abrufe geben es als `abbruch` an
 * `Antwortnachholen.formular` weiter.
 */
export class GarmentcodeAbbruch {

    static ADRESSE = '/api/garmentcode/abbrechen/';

    constructor() {
        this.steuerung = new AbortController();
        /** Kennungen der Anfragen dieses Laufs — 2D + 3D sind zwei. */
        this.kennungen = [];
        this.abgebrochen = false;
    }

    get signal() {
        return this.steuerung.signal;
    }

    /** `Antwortnachholen` meldet die Kennung jeder Anfrage. */
    merken(kennung) {
        if (kennung) this.kennungen.push(kennung);
    }

    /**
     * Abbrechen: erst das Signal (der Browser hört sofort auf zu warten),
     * dann der Server — dessen Antwort ist nur eine Auskunft.
     *
     * @returns Ergebnis je Kennung (`beendet`, `kein_lauf`, `fremd`,
     *          oder `fehler:<text>`)
     */
    async abbrechen() {
        this.abgebrochen = true;
        this.steuerung.abort(GarmentcodeAbbruch.grund());
        const ergebnisse = [];
        for (const kennung of this.kennungen) {
            ergebnisse.push(await GarmentcodeAbbruch.serverBeenden(kennung));
        }
        return ergebnisse;
    }

    /** Der Fehler, den ein abgebrochener Abruf wirft — erkennbar am Namen. */
    static grund() {
        const fehler = new Error('Abgebrochen');
        fehler.name = 'Abgebrochen';
        return fehler;
    }

    /** War ein Fehler unser eigener Abbruch? */
    static istAbbruch(fehler) {
        return fehler?.name === 'Abgebrochen';
    }

    /** Den Simulationsprozess zur Kennung beenden lassen. */
    static async serverBeenden(kennung) {
        const daten = new FormData();
        daten.append('anfrage', kennung);
        try {
            const antwort = await fetch(GarmentcodeAbbruch.ADRESSE, {
                method: 'POST', headers: Fristabruf.csrfKopf(), body: daten,
            });
            if (!antwort.ok) return `fehler:${antwort.status}`;
            return (await antwort.json()).ergebnis || 'unbekannt';
        } catch (fehler) {
            return `fehler:${fehler.message || fehler}`;
        }
    }
}
