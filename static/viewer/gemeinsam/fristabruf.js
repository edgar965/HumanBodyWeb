import { Serverabruf } from './serverabruf.js';

/**
 * Fristabruf — ein POST, der nicht ewig wartet.
 *
 * DER BEFUND (Edgar, 09.09.2026: „gerade Hose erzeugt, danach war das UI
 * nicht mehr bedienbar, nur nach Refresh der ganzen Seite, hose wurde nicht
 * gebaut")
 * =====================================================================
 * Im Serverlog steht die Kette vollständig:
 *
 *     13:57:30  POST /api/garmentcode/erzeugen/   200 [6.56]   <- Schnitt fertig
 *     13:57:31  core: GarmentCode: drapiere hose_female …      <- Drapierung an
 *     13:59:14  core: GarmentCode: Segmentierung female …      <- läuft noch
 *     (kein POST /api/garmentcode/drapieren/ — die Antwort kam NIE)
 *
 * `Serverabruf.formular` sitzt auf `fetch` ohne Frist. Eine Antwort, die nie
 * kommt, lässt das `await` für immer stehen; `GarmentcodeAblauf` erreicht sein
 * `finally` nicht, `reiter.laeuft` bleibt gesetzt, und alle fünf Knöpfe
 * bleiben grau. Von außen: „das UI ist tot". Die `Laufwache` gäbe nach 300 s
 * frei — aber erst beim NÄCHSTEN Klick, und der landet auf einem gesperrten
 * Knopf.
 *
 * WARUM NICHT IN djangoBase: `Serverabruf` liegt dort und hängt in sechs
 * Projekten. Eine Frist ist ein Kandidat für das Paket, aber nicht als
 * Nebenwirkung einer Fehlerbehebung hier — dieselbe Entscheidung wie bei
 * `ui/datenfrische.py` am selben Tag.
 *
 * `Serverabruf.json` nimmt die `fetch`-Optionen durch, also läuft die
 * Prüfung des Statuscodes und die Fehlermeldung weiter über die kanonische
 * Fassung; hier kommen nur `signal` und der CSRF-Kopf dazu.
 */
export class Fristabruf {

    /**
     * Vorgabefrist in Sekunden.
     *
     * Gemessen dauert eine Drapierung 22 bis 66 s (die längste im Log:
     * 66,09 s am 09.09.2026, 12:32). 180 s lassen also reichlich Luft für
     * einen langsamen Lauf und brechen trotzdem ab, bevor jemand aufgibt.
     */
    static FRIST_S = 180;

    /**
     * FormData als POST senden, mit Frist.
     *
     * @param adresse   URL
     * @param daten     FormData
     * @param frist_s   Sekunden bis zum Abbruch (Vorgabe `FRIST_S`)
     * @throws bei Fehlercode wie `Serverabruf`, und bei Ablauf der Frist mit
     *         einer Meldung, die die Frist NENNT — „Failed to fetch" allein
     *         sähe aus wie ein Serverfehler.
     */
    static async formular(adresse, daten, frist_s = Fristabruf.FRIST_S) {
        const steuerung = new AbortController();
        const uhr = setTimeout(
            () => steuerung.abort(new Error(
                `Keine Antwort binnen ${frist_s} s (${adresse})`)),
            frist_s * 1000);
        try {
            return await Serverabruf.json(adresse, {
                method: 'POST',
                headers: Fristabruf.csrfKopf(),
                body: daten,
                signal: steuerung.signal,
            });
        } catch (fehler) {
            // Der Abbruchgrund steht in `signal.reason`; `fehler` ist dann
            // ein DOMException „AbortError" ohne die eigene Meldung.
            if (steuerung.signal.aborted && steuerung.signal.reason) {
                throw steuerung.signal.reason;
            }
            throw fehler;
        } finally {
            clearTimeout(uhr);
        }
    }

    /** Wie `Serverabruf._csrfKopf`, das dort privat ist. */
    static csrfKopf() {
        const token = Serverabruf.csrfToken();
        return token ? { 'X-CSRFToken': token } : {};
    }
}
