/**
 * Serverabruf — Weiterleitung auf die kanonische Fassung in djangoBase, MIT
 * Protokoll.
 *
 * Umbau 16.08.2026: Die Klasse liegt seit heute in
 * `djangobase/static/djangobase/js/serverabruf.js` und wird von den Umstellern
 * unter `djangobase/umbau/` vorausgesetzt. Hier bleibt eine Unterklasse statt
 * einer blossen Weiterleitung — so behalten die rund 60 Module ihren kurzen
 * relativen Import, UND jeder Server-Aufruf dieses Projekts landet an einer
 * Stelle im Protokoll (Edgar, 24.09.2026: „alle rechtsklick und server
 * aufrufe sollen geloggt werden").
 *
 * djangoBase selbst bleibt unangetastet — es ist in ~6 Projekten eingebunden,
 * und `fn.serverLog`/`/api/log/` sind eine Eigenheit DIESES Projekts
 * (`~/.claude/CLAUDE.md`, „Geteilter Code: djangoBase"). Eine Unterklasse statt
 * `Object.assign` auf die Basis: `json`/`text` sind hier UEBERSCHRIEBEN, nicht
 * ergaenzt — `senden`/`formular` in der Basisklasse rufen intern fest
 * `Serverabruf.json` (der djangoBase-Klasse, nicht `this.json`) auf und wuerden
 * eine geloggte Fassung sonst umgehen; deshalb bekommt hier JEDE der vier
 * oeffentlichen Methoden ihre eigene Protokollzeile, statt sich auf Vererbung
 * zu verlassen.
 */
import { Serverabruf as ServerabrufBasis } from '/static/djangobase/js/serverabruf.js';
import { fn } from './registrierung.js';
import { Netzpaket } from './netzpaket.js';

export class Serverabruf extends ServerabrufBasis {

    /**
     * Eine NETZANTWORT holen — als Binärpaket, wenn der Server es kann.
     *
     * Der `Accept`-Kopf handelt das Format aus (`core/daten/netzausgabe.py`): Wer das
     * Paket annimmt, bekommt die Zahlenfelder als rohe Bytes statt als base64 in JSON —
     * ein Drittel weniger Umfang und auf beiden Seiten keine Umkodierung mehr. Ein
     * Endpunkt, der noch nicht umgestellt ist, antwortet weiter mit JSON; deshalb steht
     * `application/json` mit im Kopf und beide Formen werden gelesen.
     *
     * Das Ergebnis sieht in beiden Fällen gleich aus: ein Objekt, dessen Zahlenfelder
     * `base64ToFloat32` & Co. verstehen (`kodierung.js` reicht fertige Puffer durch).
     */
    static async netz(adresse, wahl = undefined) {
        return Serverabruf._geloggt('GET', adresse,
                                    () => Serverabruf._netzAbruf(adresse, wahl));
    }

    /** Dieselbe Aushandlung für eine Netzanfrage per POST (Regler im Rumpf). */
    static async netzSenden(adresse, nutzlast, kopf = {}) {
        return Serverabruf._geloggt('POST', adresse, () => Serverabruf._netzAbruf(adresse, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json',
                       ...ServerabrufBasis._csrfKopf(), ...kopf },
            body: JSON.stringify(nutzlast),
        }));
    }

    static async _netzAbruf(adresse, wahl = undefined) {
        const gewuenscht = { Accept: `${Netzpaket.TYP}, application/json` };
        const antwort = await fetch(adresse, {
            ...wahl, headers: { ...gewuenscht, ...(wahl?.headers || {}) },
        });
        if (!antwort.ok) throw await ServerabrufBasis._fehler(antwort, adresse);
        if (Netzpaket.erkannt(antwort)) return Netzpaket.lesen(await antwort.arrayBuffer());
        return antwort.json();
    }

    static async json(adresse, wahl = undefined) {
        return Serverabruf._geloggt('GET', adresse, () => super.json(adresse, wahl));
    }

    static async text(adresse, wahl = undefined) {
        return Serverabruf._geloggt('GET', adresse, () => super.text(adresse, wahl));
    }

    static async senden(adresse, nutzlast, kopf = {}) {
        return Serverabruf._geloggt('POST', adresse, () => super.senden(adresse, nutzlast, kopf));
    }

    static async formular(adresse, daten, kopf = {}) {
        return Serverabruf._geloggt('POST(form)', adresse, () => super.formular(adresse, daten, kopf));
    }

    /**
     * `jsonOderNull` NICHT ueberschrieben: Sie ruft in der Basisklasse fest
     * `Serverabruf.json` auf — bei einer Unterklasse bleibt das die BASIS
     * (dieselbe Falle wie bei `senden`/`formular` oben), einer geloggten
     * Fassung wuerde das eine unechte Doppel-Buchung vortaeuschen, ohne den
     * echten Aufruf zu treffen. Wer den geloggten Weg braucht, ruft `json`
     * selbst in einem `try/catch`.
     */

    static async _geloggt(methode, adresse, ausfuehren) {
        const start = performance.now();
        try {
            const ergebnis = await ausfuehren();
            fn.serverLog?.('server_call',
                `${methode} ${adresse} ok ${(performance.now() - start).toFixed(0)}ms`);
            return ergebnis;
        } catch (fehler) {
            fn.serverLog?.('server_call_failed',
                `${methode} ${adresse} status=${fehler.status ?? '?'} `
                + `${(performance.now() - start).toFixed(0)}ms ${fehler.message}`, 'warnung');
            throw fehler;
        }
    }
}
