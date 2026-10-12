/**
 * Serverfehler — aus einem Fehler des Serverabrufs eine Meldung machen, die sagt, was los ist (12.10.2026).
 *
 * Edgar: „zauberer Fehler: Zustand nicht lesbar: 500 Internal Server Error bei /api/mesh3d/…/zustand/ — <html> <head> <title>500 Internal Server Error</title> …“ und „wenn Server nicht erreichbar,
 * soll eine eindeutige Fehlermeldung kommen, keine komische wie bisher“. Zwei Fälle zeigten dem Nutzer Rohtext statt einer Auskunft:
 *
 *  - Der Server ist weg (aus, oder der Autoreload nach einer gespeicherten Python-Datei, etwa eine Minute): `fetch` wirft `TypeError: Failed to fetch` — ohne jeden Hinweis, WAS nicht erreichbar ist.
 *  - Der Server stirbt gerade (die letzten Sekunden vor dem Neustart) oder hängt hinter einem Vorrechner: statt JSON kommt die HTML-Seite eines 500/502/503/504, und die ersten 200 Zeichen davon
 *    (`<html> <head> <title>…`) standen im Fehlerband.
 *
 * `verstaendlich(fehler)` tauscht dafür `fehler.message` gegen einen deutschen Satz; die Klasse des Fehlers (`TypeError`), `status`, `adresse`, `rumpf` und `daten` bleiben, wie sie waren — wer
 * `instanceof TypeError` oder `fehler.status` prüft (`Antwortnachholen`, `Blendimportzustand`), merkt nichts. Der ursprüngliche Text steht in `fehler.technisch` und, in eckigen Klammern, im neuen.
 * Antworten, die der Server mit JSON begründet (`{"error": …}`, 400/404/409 …), bleiben unberührt: Dort sagt der Server selbst, was los ist.
 *
 * Gerufen wird es an EINER Stelle: `Serverabruf._geloggt` (gemeinsam/serverabruf.js) — damit jede Seite, die den Serverabruf des Projekts nutzt, dieselbe Meldung zeigt.
 */
export class Serverfehler {
    /** So melden Browser eine abgerissene Verbindung: Chrome „Failed to fetch“, Firefox „NetworkError …“, Safari „Load failed“. */
    static VERBINDUNG = /failed to fetch|networkerror|load failed|network request failed|fetch failed/i;
    /** Statuscodes, mit denen ein Vorrechner meldet, dass dahinter niemand antwortet. */
    static NICHT_DA = [502, 503, 504];

    /** Der deutsche Satz zu diesem Fehler, oder `null`, wenn der Fehler schon etwas Brauchbares sagt (JSON-Antwort des Servers, Fehler im eigenen Code). */
    static text(fehler) {
        if (!fehler || typeof fehler !== 'object') return null;
        const wo = globalThis.location?.host || 'der Server';
        const status = Number(fehler.status) || 0;
        if (!status && fehler instanceof TypeError && Serverfehler.VERBINDUNG.test(String(fehler.message))) {
            return Serverfehler._nichtDa(wo, `Browser: ${fehler.message}`);
        }
        if (Serverfehler.NICHT_DA.includes(status)) return Serverfehler._nichtDa(wo, `Antwort ${status}`);
        if (status >= 500 && !fehler.daten) {
            return `Server-Fehler ${status} bei ${fehler.adresse || 'einer Server-Adresse'}: der Server nennt keinen Grund. `
                + 'Startet er gerade neu (nach einer Codeänderung etwa eine Minute), geht es von selbst vorbei; '
                + 'sonst steht die Ursache in Hilfe → Logs → Exceptions.';
        }
        return null;
    }

    static _nichtDa(wo, technisch) {
        return `Server nicht erreichbar (${wo}): keine Antwort. Er ist aus, startet gerade neu (nach einer Codeänderung etwa eine Minute) oder die Verbindung ist unterbrochen. [${technisch}]`;
    }

    /** Den Fehler zurückgeben, mit verständlicher Meldung (einmal; ein zweiter Aufruf ändert nichts mehr). */
    static verstaendlich(fehler) {
        if (!fehler || typeof fehler !== 'object' || fehler.verstaendlich) return fehler;
        const text = Serverfehler.text(fehler);
        if (text) {
            fehler.technisch = fehler.message;
            fehler.message = text;
            fehler.verstaendlich = true;
        }
        return fehler;
    }
}
