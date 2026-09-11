import { GarmentcodePanels } from './garmentcode_panels.js';
import { GarmentcodeSchnitt } from './garmentcode_schnitt.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * GarmentcodeLive — die Regler formen das 2D-Modell, während man zieht.
 *
 * WARUM (Edgar, 08.09.2026: „nach erzeugung eines 2D Modells sollen die
 * Regler in Echtzeit das 2D Modell anpassen")
 * =====================================================================
 * Möglich wurde das durch `GarmentCode/kurvenzerlegung.py`: Der Schnittbau
 * eines Kleides ging von 866 auf 225 ms zurück (T-Shirt 758 → 169), weil
 * die Bogenlänge einer Kurve jetzt EINMAL tabelliert statt je Punkt
 * integriert wird. Vorher wäre „live" eine Sekunde Verzögerung gewesen.
 *
 * ENTPRELLT, UND NUR EIN LAUF ZUR ZEIT. Ein Schieber feuert beim Ziehen
 * rund 60 `input`-Ereignisse je Sekunde. Ohne Bremse liefen Dutzende
 * Schnittläufe gleichzeitig, und die Antworten kämen in beliebiger
 * Reihenfolge zurück — angezeigt würde am Ende irgendeine, nicht die
 * letzte. Deshalb: warten, bis der Nutzer kurz innehält, und während ein
 * Lauf läuft nur den WUNSCH merken.
 *
 * NUR WENN SCHON EIN 2D-MODELL STEHT. Wer die Regler ansieht, ohne je
 * gebaut zu haben, soll nicht durch bloßes Hinsehen einen Bau auslösen.
 */
export class GarmentcodeLive {

    /** So lange muss der Regler ruhig sein, bevor gebaut wird. */
    static RUHE_MS = 220;

    static _uhr = null;
    static _laeuft = false;
    static _nachholen = false;
    static _reiter = null;

    /**
     * Anmelden. Der Reiter gibt sich selbst mit, weil hier sein Zustand
     * (`spezifikation`, `schnittVon`) gebraucht wird.
     */
    static einhaengen(reiter) {
        GarmentcodeLive._reiter = reiter;
    }

    /** Ein Regler wurde bewegt. */
    static angestossen() {
        const reiter = GarmentcodeLive._reiter;
        if (!reiter || !reiter.spezifikation) return false;   // noch nichts gebaut
        if (reiter.laeuft) return false;                      // echter Bau hat Vorrang
        clearTimeout(GarmentcodeLive._uhr);
        GarmentcodeLive._uhr = setTimeout(
            () => GarmentcodeLive._bauen(), GarmentcodeLive.RUHE_MS);
        return true;
    }

    static async _bauen() {
        const reiter = GarmentcodeLive._reiter;
        if (!reiter || reiter.laeuft) return;
        if (GarmentcodeLive._laeuft) {
            // Während ein Lauf unterwegs ist, wird nur gemerkt, dass danach
            // noch einmal gebaut werden muss — sonst überholen sich die
            // Antworten und es bleibt eine veraltete stehen.
            GarmentcodeLive._nachholen = true;
            return;
        }
        const figur = reiter.figur();
        const vorlage = document.getElementById('gc-vorlage')?.value;
        if (!figur || !vorlage) return;
        // Die Vorlage darf nicht gewechselt worden sein: Sonst zeigte der
        // Schnitt des einen Stücks die Regler des anderen.
        if (reiter.schnittVon && reiter.schnittVon.vorlage !== vorlage) return;

        GarmentcodeLive._laeuft = true;
        const meldung = document.getElementById('gc-meldung');
        try {
            reiter.ohneMorphs = GarmentcodeFigur.ohneMorphs(figur);
            const ergebnis = await GarmentcodeSchnitt.bauen(reiter, figur, meldung);
            // Hat inzwischen ein echter Bau begonnen (Häkchen gesetzt, gleich
            // „Bauen 2D + 3D" gedrückt), bleiben die Panels weg: Der Bau
            // hat sie schon entfernt, und sie kämen sonst als rosa Flächen
            // neben den fertigen Schuh zurück (gesehen 11.09.2026).
            if (ergebnis && !reiter.laeuft) {
                reiter.spezifikation = ergebnis.spezifikation || reiter.spezifikation;
                reiter.schnittVon = { figur: figur.id, vorlage };
                await GarmentcodePanels.zeigen(figur, reiter.spezifikation, vorlage);
            }
        } catch (fehler) {
            // Ein misslungener Live-Bau ist kein Grund, die Bedienung zu
            // unterbrechen — der nächste Reglerzug versucht es erneut.
            Protokoll.debug('GC-Live', String(fehler.message || fehler));
        } finally {
            GarmentcodeLive._laeuft = false;
            if (GarmentcodeLive._nachholen) {
                GarmentcodeLive._nachholen = false;
                GarmentcodeLive.angestossen();
            }
        }
    }
}
