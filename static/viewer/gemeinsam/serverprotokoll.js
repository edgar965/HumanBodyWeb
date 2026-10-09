/**
 * Serverprotokoll — Meldungen aus dem Browser an `/api/log/`, auch wenn der Server gerade nicht da ist (09.10.2026).
 *
 * Anlass (Edgar, 09.10.2026, „Fehler beim Importieren … siehe logs", „Failed to fetch" ca. eine Minute, „warum
 * erscheint das nicht in dem Error log??"): Eine andere Sitzung speicherte eine Python-Datei, Djangos Autoreload
 * startete den Server neu (09:59:22 → 10:00:11). Der Browser sah `Failed to fetch` — und konnte es nirgends melden,
 * denn die Meldung selbst geht an denselben Server und ging ins Leere (`.catch(() => {})`). Im Fehlerlog stand
 * deshalb nichts, im `client.log` auch nicht.
 *
 * Jetzt: Scheitert eine Meldung an der VERBINDUNG, wird sie aufgehoben (höchstens `MAX_WARTEND`, die ältesten fallen
 * zuerst), alle `PRUEFEN_MS` fragt das Modul mit der ältesten wieder an, und sobald der Server antwortet, kommen alle
 * nach — mit der Uhrzeit des Browsers — und danach EINE Zusammenfassung „Server N s nicht erreichbar" auf Stufe
 * `error` (die allein landet auch im Fehlerlog, `error.log`). Eine Antwort mit Fehlerstatus (404, 500) zählt nicht als
 * Ausfall: Dann ist der Server da.
 *
 * Stufen: `info` | `warning` | `error` (der Server kennt auch `warnung` und `fehler`, `Serverabruf` sendet deutsche).
 */
export class Serverprotokoll {

    static ADRESSE = '/api/log/';
    static MAX_WARTEND = 100;
    static PRUEFEN_MS = 3000;
    /** Ab so vielen Sekunden Ausfall ist die Zusammenfassung ein Fehler (darunter eine Warnung). */
    static FEHLER_AB_S = 5;

    static _wartend = [];
    static _verworfen = 0;
    static _seit = null;          // Beginn des Ausfalls (ms), solange einer läuft
    static _uhr = null;
    static _prueft = false;

    /** Eine Meldung abschicken; reißt die Verbindung ab, bleibt sie liegen und kommt später nach. */
    static melden(seite, aktion, detail, stufe = 'info') {
        const eintrag = { page: seite, action: aktion, detail: detail || '', level: stufe || 'info' };
        if (Serverprotokoll._seit !== null) {      // Server weg: nicht noch eine Anfrage in die Leere schicken
            Serverprotokoll._merken(eintrag);
            return Promise.resolve(false);
        }
        return Serverprotokoll._senden(eintrag).then(() => true, () => {
            Serverprotokoll._ausfall(eintrag);
            return false;
        });
    }

    /** Wie viele Meldungen warten gerade auf den Server (Diagnose, Tests). */
    static wartend() {
        return Serverprotokoll._wartend.length;
    }

    static _senden(eintrag) {
        return fetch(Serverprotokoll.ADRESSE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eintrag),
        });
    }

    static _ausfall(eintrag) {
        if (Serverprotokoll._seit === null) Serverprotokoll._seit = Date.now();
        Serverprotokoll._merken(eintrag);
        if (Serverprotokoll._uhr === null) {
            Serverprotokoll._uhr = setInterval(() => Serverprotokoll._pruefen(), Serverprotokoll.PRUEFEN_MS);
        }
    }

    static _merken(eintrag) {
        Serverprotokoll._wartend.push({ ...eintrag, zeit: Date.now() });
        while (Serverprotokoll._wartend.length > Serverprotokoll.MAX_WARTEND) {
            Serverprotokoll._wartend.shift();
            Serverprotokoll._verworfen += 1;
        }
    }

    static _uhrzeit(ms) {
        return new Date(ms).toLocaleTimeString('de-DE', { hour12: false });
    }

    /** Ist der Server wieder da? Mit der ältesten wartenden Meldung fragen; antwortet er, alles nachliefern. */
    static async _pruefen() {
        if (Serverprotokoll._prueft || Serverprotokoll._wartend.length === 0) return;
        Serverprotokoll._prueft = true;
        try {
            const bis = Date.now();
            const nachgeliefert = [];
            while (Serverprotokoll._wartend.length > 0) {
                const eintrag = Serverprotokoll._wartend[0];
                const { zeit, ...rest } = eintrag;
                await Serverprotokoll._senden({
                    ...rest, detail: `${rest.detail} [Browser ${Serverprotokoll._uhrzeit(zeit)}, nachgeliefert]`,
                });
                Serverprotokoll._wartend.shift();
                nachgeliefert.push(eintrag);
            }
            await Serverprotokoll._zusammenfassen(bis, nachgeliefert);
        } catch (fehler) {
            // Immer noch weg (oder wieder weg): liegen lassen, der nächste Takt versucht es erneut.
        } finally {
            Serverprotokoll._prueft = false;
        }
    }

    static async _zusammenfassen(bis, nachgeliefert) {
        const von = Serverprotokoll._seit;
        const sekunden = Math.round((bis - von) / 1000);
        const seite = (nachgeliefert[nachgeliefert.length - 1] || {}).page || '?';
        const verworfen = Serverprotokoll._verworfen;
        clearInterval(Serverprotokoll._uhr);
        Serverprotokoll._uhr = null;
        Serverprotokoll._seit = null;
        Serverprotokoll._verworfen = 0;
        const stufe = sekunden >= Serverprotokoll.FEHLER_AB_S ? 'error' : 'warning';
        const detail = `Server ${sekunden} s nicht erreichbar (${Serverprotokoll._uhrzeit(von)}–${Serverprotokoll._uhrzeit(bis)}), `
            + `${nachgeliefert.length} Meldungen nachgeliefert${verworfen ? `, ${verworfen} verworfen` : ''}. `
            + 'Meist lädt der Server nach einer gespeicherten Python-Datei neu (Autoreload, siehe django.log); '
            + 'Aufträge im Hintergrund (Import, Pipelines) rechnen währenddessen weiter.';
        await Serverprotokoll._senden({ page: seite, action: 'verbindung_unterbrochen', detail, level: stufe });
    }
}
