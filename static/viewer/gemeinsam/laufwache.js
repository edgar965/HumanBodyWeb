/**
 * Laufwache — wer den Reiter gerade besetzt, und ab wann er als verloren gilt.
 *
 * WARUM ES SIE GIBT (08.09.2026, Edgar: „Kleid erzeugen funktioniert gerade
 * nicht (nach T-Shirt Erzeugung)")
 * =====================================================================
 * In `garmentcode_ablauf.js` stand als Wache eine einzige Zeile:
 *
 *     if (reiter.laeuft) return;
 *
 * Kein Text, keine Anfrage, nichts. Wer klickte, sah einen Knopf, der nichts
 * tut — und genau so liest sich „funktioniert nicht". Im Serverlog war der
 * Befund eindeutig: Nach dem Wechsel auf das Kleid kam KEIN einziger
 * `/api/garmentcode/erzeugen/` mehr an, der Klick hat den Ablauf nie
 * erreicht.
 *
 * Dazu kommt der Weg, auf dem `laeuft` haengen bleibt: `Serverabruf.formular`
 * sitzt auf `fetch` OHNE Frist (nachgesehen in djangoBase, 08.09.2026). Eine
 * Antwort, die nie kommt — ein Serverneustart mitten im Lauf, wie am
 * 07.09.2026 um 18:57 — laesst das `await` fuer immer stehen. Der Reiter
 * bleibt dann besetzt, und ALLE drei Knoepfe sind dauerhaft tot.
 *
 * OHNE DOM, DAMIT PRUEFBAR — wie `fortschrittsrechnung.js` und
 * `greifrechnung.js`. Der Zustand ist ein schlichtes Objekt
 * (`{laeuft, laeuftSeit, laufnummer}`); wer die Knoepfe sperrt und die
 * Meldung schreibt, entscheidet der Aufrufer.
 *
 * DIE LAUFNUMMER IST KEIN SCHMUCK. Ohne sie gaebe ein verloren geglaubter
 * Lauf, dessen Anfrage doch noch zurueckkommt, die Knoepfe mitten im
 * naechsten Bau frei und ueberschriebe dessen Meldung.
 */
export class Laufwache {

    /** Ab wann ein laufender Bau als verloren gilt (Sekunden). */
    static FRIST_S = 300;

    /**
     * Darf ein neuer Lauf starten?
     *
     * @returns `{darf, grund, seit}` — `grund` ist `'frei'`, `'besetzt'`
     *          oder `'verloren'`, `seit` die Dauer des laufenden Baus in
     *          Sekunden.
     */
    static pruefen(zustand, jetzt = Date.now()) {
        if (!zustand || !zustand.laeuft) {
            return { darf: true, grund: 'frei', seit: 0 };
        }
        const seit = Math.max(0,
            Math.round((jetzt - (zustand.laeuftSeit || 0)) / 1000));
        return seit < Laufwache.FRIST_S
            ? { darf: false, grund: 'besetzt', seit }
            : { darf: true, grund: 'verloren', seit };
    }

    /** Den Reiter besetzen. Gibt die Laufnummer dieses Laufs zurueck. */
    static beginnen(zustand, jetzt = Date.now()) {
        zustand.laeuft = true;
        zustand.laeuftSeit = jetzt;
        zustand.laufnummer = (zustand.laufnummer || 0) + 1;
        return zustand.laufnummer;
    }

    /**
     * Freigeben — aber nur, wenn DIESER Lauf noch der aktuelle ist.
     *
     * @returns `true`, wenn wirklich freigegeben wurde
     */
    static beenden(zustand, lauf) {
        if (!zustand || zustand.laufnummer !== lauf) return false;
        zustand.laeuft = false;
        zustand.laeuftSeit = 0;
        return true;
    }

    /** Gehoert eine Meldung noch zum aktuellen Lauf? */
    static aktuell(zustand, lauf) {
        return Boolean(zustand) && zustand.laufnummer === lauf;
    }
}
