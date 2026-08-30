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
 * DIE ARTEN SIND DRAHTFORMAT: `type`, `body_type`, `gender`, `message` schreibt
 * `core/consumers.py`. Wer hier einen Namen aendert, bekommt eine Nachricht,
 * die ankommt und nichts ausloest.
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
     *     fehler(text)} — jeder Eintrag darf fehlen
     */
    static verteilen(ereignis, behandler) {
        if (ereignis.data instanceof ArrayBuffer) {
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
        }
    }
}
