/**
 * Seitenabbruch — die lesenden Abrufe einer Seite enden, sobald sie verlassen wird (30.10.2026, Edgar: „wenn ich /studio/ öffne, und schnell eine
 * andere Seite klicke, dauert es ewig, bis du auf den Klick reagierst, die seite lädt weiter").
 *
 * Gemessen (Chrome, Studio mit TechnoDance, 2,5 s nach dem Öffnen „Alle Jobs" geklickt): Das Studio stellt Dutzende Abrufe auf einmal; Chrome schickt
 * je Host sechs, der Rest wartet in Chromes Schlange und ging nach dem Klick noch 16 s lang zum Server (`django.log` 14:07:24–40: Retargets, Netze,
 * Texturen). Die neue Seite teilte sich den Server mit ihnen — `GET /mesh-3D-AI/` 12,9 s, bei Edgar 32,05 s (13:42:16–48, 204 Anfragen mit 64,9 s
 * Serverzeit daneben).
 *
 * Ab dem Ereignis `navigate` der Navigation API (ein anderes Dokument, kein Download, von keinem Zuhörer abgesagt) bricht `signal` ab, und Chrome
 * schickt die wartenden Abrufe nicht mehr. Ein abgebrochener Abruf meldet KEINEN Fehler (kein Hinweis im Augenblick des Wechsels, keine Zeile im
 * Protokoll): `mit` wartet, bis die Seite verschwindet — oder holt ihn neu, wenn sie nach `FRIST_MS` noch da ist (Abbruch im Dialog von
 * `beforeunload`, Antwort 204). Nur LESENDE Abrufe und reine Rechnungen machen mit (GET, Netzanfragen, Retarget, Texturbündel): ein Schreiben, das
 * noch in Chromes Schlange steht, ginge sonst verloren.
 */
import { fn } from './registrierung.js';

export class Seitenabbruch {
    static FRIST_MS = 10000;
    static _steuerung = new AbortController();
    static _geblieben = null;           // Promise, solange die Seite verlassen wird

    /** Das Signal für den nächsten Abruf (nach einem Abbruch, der die Seite nicht verließ, ein neues). */
    static get signal() {
        return Seitenabbruch._steuerung.signal;
    }

    static get verlassen() {
        return Seitenabbruch._geblieben !== null;
    }

    /** Wartet, solange die Seite verlassen wird — endet nur, wenn sie doch bleibt. */
    static async geblieben() {
        while (Seitenabbruch._geblieben) await Seitenabbruch._geblieben;
    }

    /** Das Signal des Aufrufers und das der Seite zusammen. */
    static verbunden(eigen, seite = Seitenabbruch.signal) {
        return eigen ? AbortSignal.any([eigen, seite]) : seite;
    }

    /** `ausfuehren(signal)` mit dem Signal der Seite; hat der Wechsel sie abgebrochen: warten und, wenn die Seite bleibt, noch einmal. */
    static async mit(ausfuehren) {
        for (;;) {
            await Seitenabbruch.geblieben();
            const signal = Seitenabbruch.signal;
            try {
                return await ausfuehren(signal);
            } catch (fehler) {
                if (!signal.aborted || fehler?.name !== 'AbortError') throw fehler;
            }
        }
    }

    static beobachten() {
        globalThis.navigation?.addEventListener('navigate', ereignis => {        // `globalThis`: die Node-Tests der Module kennen kein `window`
            if (ereignis.destination.sameDocument || ereignis.downloadRequest !== null) return;
            queueMicrotask(() => {          // erst nach allen Zuhörern: hat einer abgesagt, bleibt die Seite
                if (ereignis.defaultPrevented || Seitenabbruch._geblieben) return;
                Seitenabbruch._geblieben = new Promise(weiter => setTimeout(() => {
                    Seitenabbruch._steuerung = new AbortController();
                    Seitenabbruch._geblieben = null;
                    fn.serverLog?.('abrufe_fortgesetzt', 'Seite nach dem Verlassen geblieben — abgebrochene Abrufe laufen neu', 'warnung');
                    weiter();
                }, Seitenabbruch.FRIST_MS));
                Seitenabbruch._steuerung.abort();
            });
        });
    }
}

Seitenabbruch.beobachten();
