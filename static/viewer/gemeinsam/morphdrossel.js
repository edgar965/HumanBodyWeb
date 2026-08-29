/**
 * Morphdrossel — Reglerzüge sammeln und gebündelt an den Server schicken.
 *
 * WARUM (Befund `doppelcode`, 29.08.2026): `sendMorphThrottled` stand
 * zeichengleich in `result_character/websocket.js` und `viewer/websocket.js`
 * (13 Zeilen). Beide Seiten schieben dieselben Regler über dieselbe
 * Verbindung.
 *
 * WAS DIE DROSSEL LEISTET: Ein Reglerzug erzeugt Dutzende `input`-Ereignisse
 * je Sekunde. Ungedrosselt geht jedes einzeln über die Leitung, und der
 * Server rechnet für jedes ein Netz. Gesammelt wird 33 ms lang — rund ein
 * Bild bei 30 Hz.
 *
 * EIN EINZELNER WERT GEHT ALS `morph`, MEHRERE ALS `morph_batch`. Das ist
 * kein Feinschliff, sondern der Grund, warum ein einzelner Reglerzug flüssig
 * bleibt: Der Server hat für die Einzelnachricht einen kürzeren Weg. Wer das
 * vereinheitlicht, macht das Ziehen an EINEM Regler langsamer.
 *
 * Der Zustand (`pendingMorphs`, `morphTimer`) bleibt am Seitenzustand, wo er
 * schon lag — beide Seiten führen ihn in ihrer `state.js`.
 */
export class Morphdrossel {
    /** Sammelfenster in Millisekunden — rund ein Bild bei 30 Hz. */
    static FENSTER_MS = 33;

    /**
     * @param {Object} state Seitenzustand mit `pendingMorphs` und `morphTimer`
     * @param {Function} senden Nachricht an den Server (`wsSend`)
     * @param {string} schluessel Name des Morphs
     * @param {number} wert neuer Wert
     */
    static schieben(state, senden, schluessel, wert) {
        state.pendingMorphs[schluessel] = wert;
        if (state.morphTimer) return;
        state.morphTimer = setTimeout(() => {
            const eintraege = Object.entries(state.pendingMorphs);
            if (eintraege.length === 1) {
                const [k, v] = eintraege[0];
                senden({ type: 'morph', key: k, value: v });
            } else {
                senden({ type: 'morph_batch', morphs: state.pendingMorphs });
            }
            state.pendingMorphs = {};
            state.morphTimer = null;
        }, Morphdrossel.FENSTER_MS);
    }
}
