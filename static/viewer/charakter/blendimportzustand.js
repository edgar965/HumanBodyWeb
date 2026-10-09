/**
 * Blendimportzustand — der EINE Fragesteller für den Stand eines Blender-Imports (08.10.2026).
 *
 * Fragt `/api/character/blendimport/<kennung>/zustand/` alle zwei Sekunden, solange der Import läuft, und meldet jeden
 * Stand als Ereignis `blendimport-zustand` am `document` (`detail` = der Stand samt `kennung`). Zuhörer: die Leiste
 * oben neben „HumanBody" (`Blendimportleiste`) und der Lauf im Dialog (`Blendimportfortschritt`) — beide zeigen
 * dasselbe, ohne dass der Server doppelt gefragt wird.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { fn } from '../gemeinsam/registrierung.js';

export class Blendimportzustand {

    static TAKT_MS = 2000;
    static EREIGNIS = 'blendimport-zustand';
    static TITEL = { export: 'Lesen', umposen: 'Haltung', koerper: 'Körpernetz', figur: 'Genesis-Figur', stuecke: 'Kleider & Haar',
                     haut: 'Haut backen', augen: 'Augen', modell: 'Modell' };

    static _uhr = null;
    static _kennung = null;
    static _letzter = null;           // der letzte Stand, der wirklich vom Server kam
    static _getrenntSeit = null;      // ms; gesetzt, solange der Server nicht antwortet

    /** Rechnet der Import noch (oder steht er kurz davor)? */
    static laeuft(zustand) {
        return zustand.status === 'laeuft' || zustand.status === 'neu';
    }

    /** Fortschritt in Prozent: im Schritt „figur" zählt der Lauf von „Mesh to 3D", den der Server auf das Band umrechnet. */
    static prozent(zustand) {
        const lauf = zustand.figur_lauf;
        return Math.max(0, Math.min(100, Math.max(zustand.fortschritt || 0, lauf ? lauf.fortschritt : 0)));
    }

    /** Diesen Import beobachten (einen zugleich); fragt sofort einmal und danach im Takt, bis er nicht mehr läuft. */
    static beobachten(kennung) {
        const gleich = Blendimportzustand._kennung === kennung && Blendimportzustand._uhr !== null;
        if (!gleich) {
            clearInterval(Blendimportzustand._uhr);
            Blendimportzustand._kennung = kennung;
            Blendimportzustand._uhr = setInterval(() => Blendimportzustand.abfragen(), Blendimportzustand.TAKT_MS);
        }
        return Blendimportzustand.abfragen();
    }

    static async abfragen() {
        const kennung = Blendimportzustand._kennung;
        let zustand;
        try {
            zustand = await Serverabruf.json(`/api/character/blendimport/${encodeURIComponent(kennung)}/zustand/`);
        } catch (fehler) {
            // Reißt die VERBINDUNG ab (der Server lädt nach einer gespeicherten Python-Datei neu, 09.10.2026: 50 s),
            // sagt das nichts über den Import: Er läuft als eigener Prozess weiter. Früher wurde daraus „unbekannt" —
            // rot, „Zustand nicht lesbar: Failed to fetch" — und das Fragen hörte auf, die Anzeige blieb stehen.
            if (fehler instanceof TypeError) return Blendimportzustand._getrennt(kennung);
            zustand = { status: 'unbekannt', detail: `Stand nicht lesbar (Server-Antwort: ${fehler.message})` };
        }
        Blendimportzustand._wiederda(kennung);
        zustand.kennung = kennung;
        Blendimportzustand._letzter = zustand;
        if (!Blendimportzustand.laeuft(zustand)) {
            clearInterval(Blendimportzustand._uhr);
            Blendimportzustand._uhr = null;
        }
        document.dispatchEvent(new CustomEvent(Blendimportzustand.EREIGNIS, { detail: zustand }));
        return zustand;
    }

    /** Der Server antwortet nicht: den letzten bekannten Stand weiterzeigen, mit dem Hinweis und den Sekunden. */
    static _getrennt(kennung) {
        const jetzt = Date.now();
        if (Blendimportzustand._getrenntSeit === null) Blendimportzustand._getrenntSeit = jetzt;
        const sekunden = Math.round((jetzt - Blendimportzustand._getrenntSeit) / 1000);
        const bekannt = Blendimportzustand._letzter && Blendimportzustand._letzter.kennung === kennung
            ? Blendimportzustand._letzter : { status: 'laeuft' };
        const zustand = {
            ...bekannt, kennung, verbindung: 'getrennt', getrennt_s: sekunden,
            detail: `Der Server antwortet nicht (seit ${sekunden} s) — er lädt vermutlich nach einer Codeänderung neu. `
                + 'Der Import rechnet im Hintergrund weiter; neuer Versuch alle 2 s.',
        };
        document.dispatchEvent(new CustomEvent(Blendimportzustand.EREIGNIS, { detail: zustand }));
        return zustand;
    }

    /** Die erste Antwort nach einem Ausfall: im Protokoll vermerken (das übrige macht `Serverprotokoll`). */
    static _wiederda(kennung) {
        if (Blendimportzustand._getrenntSeit === null) return;
        const sekunden = Math.round((Date.now() - Blendimportzustand._getrenntSeit) / 1000);
        Blendimportzustand._getrenntSeit = null;
        fn.serverLog?.('blendimport_verbindung_wieder',
            `Import ${kennung}: Server nach ${sekunden} s wieder erreichbar — der Import lief in dieser Zeit weiter`,
            sekunden >= 5 ? 'warning' : 'info');
    }

    /** Kennung des Imports, der gerade rechnet (auch nach dem Neuladen der Seite) — sonst `null`. */
    static async laufend() {
        const antwort = await Serverabruf.json('/api/character/blendimport/laufend/');
        return antwort.kennung || null;
    }
}
