/**
 * Hauptfadenwaechter — meldet ins Seitenlog, WÄHREND der Hauptfaden der Seite steht (05.10.2026).
 *
 * Edgar: „warum sind keine Logs sichtbar, wenn ich auf den Tab Iterationen klicke?" — Jede Log-Zeile geht vom Hauptfaden ab; wo er steht, schweigt das Log, und der
 * Beobachter für lange Aufgaben (`PerformanceObserver`, `longtask`) meldet erst nach ihrem Ende. Der Wächter ist ein Web-Worker (`hauptfadenarbeiter.js`, eigener
 * Faden), der den Hauptfaden anfragt und bei ausbleibender Antwort SELBST an die Log-Adresse schreibt: `haenger_live` (steht seit …) und `haenger_ende` (wieder da).
 *
 * Hängt an nichts und wirft nie: Geht der Worker nicht zu starten, bleibt die Seite wie sie ist, und `fehler` bekommt den Grund.
 */
export class Hauptfadenwaechter {

    /**
     * @param {{adresse: string, seite: string, kennung: string, fehler?: (text: string) => void}} optionen `adresse`: `POST`-Ziel des Seitenlogs;
     *   `seite`/`kennung`: Seitenname und Kennung des Tabs, wie sie die Zeilen des Seitenlogs tragen; `fehler`: Rückruf, wenn der Worker nicht startet oder abbricht
     * @returns {Worker|null}
     */
    static starten({ adresse, seite, kennung, fehler = () => {} }) {
        try {
            const arbeiter = new Worker(new URL('./hauptfadenarbeiter.js', import.meta.url).href, { type: 'module' });
            arbeiter.onmessage = ereignis => {
                if (ereignis.data && ereignis.data.typ === 'ping') arbeiter.postMessage({ typ: 'pong' });
            };
            arbeiter.onerror = ereignis => fehler(`Hauptfaden-Wächter: ${ereignis.message || 'Worker abgebrochen'}`);
            arbeiter.postMessage({ typ: 'start', adresse: new URL(adresse, location.href).href, seite, kennung });
            const sichtbarkeit = () => arbeiter.postMessage({ typ: 'sicht', wert: document.visibilityState === 'visible' });
            document.addEventListener('visibilitychange', sichtbarkeit);
            sichtbarkeit();
            return arbeiter;
        } catch (ausnahme) {
            fehler(`Hauptfaden-Wächter nicht gestartet: ${ausnahme && ausnahme.message ? ausnahme.message : ausnahme}`);
            return null;
        }
    }
}
