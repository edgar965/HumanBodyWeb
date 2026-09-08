import { Protokoll } from './protokoll.js';

/**
 * Netznachricht — was ueber den Morph-WebSocket hereinkommt, auseinanderhalten.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Derselbe Verteiler stand in
 * `viewer/websocket.js` und `result_character/websocket.js`.
 *
 * ZWEI ARTEN AUF EINEM KANAL: Ein `ArrayBuffer` sind die neuen Punktlagen —
 * das ist der Normalfall und kommt mehrmals je Sekunde. Alles andere ist Text
 * und traegt eine Absicht (`reload_mesh`, `error`).
 *
 * DIE ARTEN SIND DRAHTFORMAT: `type`, `body_type`, `gender`, `message`, `bones`
 * schreibt `core/consumers.py`. Wer hier einen Namen aendert, bekommt eine
 * Nachricht, die ankommt und nichts ausloest.
 *
 * `skelett` (05.09.2026) traegt die Knochen, die dem gemorphten Koerper
 * nachgezogen werden muessen. Sie kommt NACH dem passenden Punktepuffer und
 * darf auch leer sein — leer heisst „alles zurueck in die Ruhelage".
 *
 * `stoff` (08.09.2026) kuendigt ein Binaerpaket an, das NICHT der Koerper
 * ist, sondern ein drapiertes Kleidungsstueck, das den Reglern folgt. Die
 * Ankuendigung gilt fuer genau ein Paket. Wer keinen `zustand` uebergibt,
 * bekommt sie nicht — und damit auch keinen Stoff, statt ihn versehentlich
 * als Koerper einzusetzen.
 *
 * EIN UNLESBARER TEXT IST KEIN ABBRUCH: Der Kanal laeuft weiter, die Zeile
 * geht ins Protokoll. Eine geworfene Ausnahme im `onmessage` beendet nichts,
 * sie landet nur als „Unhandled" in der Konsole — und der naechste Puffer
 * kaeme trotzdem an. Besser eine Spur im Log als eine stille Ausnahme.
 */
export class Netznachricht {
    /**
     * @param {MessageEvent} ereignis
     * @param {Object} behandler {punkte(ArrayBuffer), neuLaden(typ, geschlecht),
     *     fehler(text), skelett(knochen)} — jeder Eintrag darf fehlen
     */
    static verteilen(ereignis, behandler, zustand = null) {
        if (ereignis.data instanceof ArrayBuffer) {
            // Ein angekuendigtes Stoffpaket geht an den Stoff, nicht an den
            // Koerper — siehe `stoff` unten. Die Ankuendigung gilt fuer
            // GENAU EIN Paket und wird sofort verbraucht; bliebe sie
            // stehen, landeten die naechsten Koerperpunkte im Stoffnetz.
            const stueck = zustand && zustand.stoffErwartet;
            if (stueck) {
                zustand.stoffErwartet = null;
                if (behandler.stoff) behandler.stoff(ereignis.data, stueck);
                return;
            }
            if (behandler.punkte) behandler.punkte(ereignis.data);
            return;
        }
        let nachricht;
        try {
            nachricht = JSON.parse(ereignis.data);
        } catch (e) {
            Protokoll.debug('websocket', 'Nachricht nicht verwertbar', e);
            return;
        }
        if (nachricht.type === 'error') {
            if (behandler.fehler) behandler.fehler(nachricht.message);
        } else if (nachricht.type === 'reload_mesh') {
            if (behandler.neuLaden) {
                behandler.neuLaden(nachricht.body_type, nachricht.gender);
            }
        } else if (nachricht.type === 'skelett') {
            if (behandler.skelett) behandler.skelett(nachricht.bones || {});
        } else if (nachricht.type === 'stoff') {
            // Kuendigt das naechste Binaerpaket an. Ohne `zustand` (die
            // alten Aufrufer) wird es schlicht ignoriert — dann kommt das
            // Paket als Koerperpunkte an, und DAS waere falsch. Deshalb
            // merkt sich der Verteiler die Ankuendigung nur, wenn ihm ein
            // Zustand gegeben wurde; wer Stoff empfangen will, muss ihn
            // fuehren.
            if (zustand) {
                zustand.stoffErwartet = nachricht.stueck || 'kleidung';
                if (behandler.stoffStand) behandler.stoffStand(nachricht);
            }
        } else if (nachricht.type === 'stoff_bindung') {
            if (behandler.stoffBindung) behandler.stoffBindung(nachricht);
        }
    }
}
