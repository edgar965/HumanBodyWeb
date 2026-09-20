import { Fristabruf } from './fristabruf.js';

/**
 * Antwortnachholen — ein POST, dessen Antwort auch dann ankommt, wenn die
 * Verbindung unterwegs reißt.
 *
 * DER BEFUND (Edgar, 20.09.2026: „von einem Bug zum anderen! Stoff drapieren
 * — Failed to fetch"): Der Dev-Server startet neu, sobald eine importierte
 * Datei sich ändert — 109-mal an diesem Abend, weil nebenan eine zweite
 * Sitzung arbeitet. Der alte Prozess rechnet die Drapierung ZU ENDE und
 * schreibt das Rig (Log: 21:42:31 drapiere, 21:42:46 reloading, 21:43:01
 * angezogen), nur die Antwort erreicht den Browser nicht mehr. `fetch`
 * wirft dann einen `TypeError` „Failed to fetch" — nicht die Frist, nicht
 * ein Fehlercode.
 *
 * DER WEG: Jede Anfrage bekommt eine Kennung (`anfrage`). Der Server legt
 * seine Antwort unter ihr ab (`api/garmentantwort.py`). Reißt die
 * Verbindung, fragt dieser Abruf `/api/garmentcode/antwort/<kennung>/`
 * alle `TAKT_S` Sekunden ab, bis die Antwort da ist oder die Frist um ist —
 * die Meldung sagt derweil, was passiert. Ein Fehlercode des Servers (400,
 * 500) und die abgelaufene Frist werden NICHT nachgeholt: Dort gibt es
 * keine Antwort, die noch käme.
 */
export class Antwortnachholen {

    /** Abstand der Nachfragen in Sekunden. */
    static TAKT_S = 3;
    static ADRESSE = '/api/garmentcode/antwort/';

    /**
     * FormData senden wie `Fristabruf.formular`; bei gerissener Verbindung
     * die Antwort nachholen.
     *
     * @param adresse   URL des POST
     * @param daten     FormData — bekommt das Feld `anfrage`
     * @param frist_s   Sekunden für Lauf UND Nachholen zusammen
     * @param melden    (text) => void — sagt, dass nachgeholt wird
     * @param abbruch   optional `{signal, merken(kennung)}` — der
     *                  Abbrechen-Knopf (`scene/garmentcode_abbruch.js`):
     *                  bekommt die Kennung, damit er den Serverlauf
     *                  beenden kann, und sein Signal bricht Lauf UND
     *                  Nachholen ab
     */
    static async formular(adresse, daten, frist_s = Fristabruf.FRIST_S,
                          melden = null, abbruch = null) {
        const kennung = Antwortnachholen.kennung();
        daten.append('anfrage', kennung);
        abbruch?.merken?.(kennung);
        const signal = abbruch?.signal || null;
        const start = Date.now();
        try {
            return await Fristabruf.formular(adresse, daten, frist_s, signal);
        } catch (fehler) {
            if (!Antwortnachholen.gerissen(fehler)) throw fehler;
            const rest_s = frist_s - (Date.now() - start) / 1000;
            if (melden) {
                melden('Verbindung zum Server gerissen (Neustart?) — '
                       + 'der Lauf geht weiter, ich hole die Antwort nach …');
            }
            return await Antwortnachholen.nachholen(kennung, rest_s, fehler, signal);
        }
    }

    /** Eine Kennung, die als Dateiname taugt (`Garmentantwort.KENNUNG`). */
    static kennung() {
        const roh = (globalThis.crypto?.randomUUID?.()
            || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`);
        return roh.replace(/[^A-Za-z0-9_-]/g, '').slice(0, 64);
    }

    /**
     * War es die Verbindung — nicht der Server, nicht die Frist?
     * `fetch` meldet ein Netzproblem als `TypeError`; die Frist kommt als
     * `Error` mit „Keine Antwort binnen" (`Fristabruf`), ein Fehlercode als
     * `Error` aus `Serverabruf` mit dem Status im Text.
     */
    static gerissen(fehler) {
        return fehler instanceof TypeError
            || /failed to fetch|networkerror|load failed/i.test(
                String(fehler?.message || fehler));
    }

    /**
     * Die Antwort zur Kennung abfragen, bis sie da ist.
     * @throws den ursprünglichen Fehler, wenn die Frist ohne Antwort abläuft
     */
    static async nachholen(kennung, frist_s, ursache, signal = null) {
        const ende = Date.now() + Math.max(frist_s, Antwortnachholen.TAKT_S) * 1000;
        while (Date.now() < ende) {
            await new Promise((weiter) => setTimeout(weiter, Antwortnachholen.TAKT_S * 1000));
            // Abgebrochen (Knopf): nicht weiter nachfragen.
            if (signal?.aborted) throw signal.reason || new Error('Abgebrochen');
            try {
                const antwort = await fetch(`${Antwortnachholen.ADRESSE}${kennung}/`,
                                            { cache: 'no-store' });
                if (antwort.status === 404) continue;      // noch nicht fertig
                if (!antwort.ok) {
                    throw new Error(`${antwort.status} beim Nachholen der Antwort`);
                }
                return await antwort.json();
            } catch (fehler) {
                // Der Server ist gerade weg (Neustart) — weiter warten.
                if (!Antwortnachholen.gerissen(fehler)) throw fehler;
            }
        }
        throw new Error(`${ursache?.message || ursache} — und binnen `
            + `${Math.round(frist_s)} s kam auch keine abgelegte Antwort`);
    }
}
