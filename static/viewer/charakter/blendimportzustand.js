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
    static VORLAEUFIG = 'blendimport-vorlaeufig';       // der Kurzstand von `laufend`, bevor der erste Zustand da ist — hört nur die Leiste
    static TITEL = { umwandeln: 'Umwandeln', export: 'Lesen', umposen: 'Haltung', koerper: 'Körpernetz', figur: 'Genesis-Figur', finger: 'Finger', stuecke: 'Kleider & Haar',
                     haut: 'Haut backen', augen: 'Augen', modell: 'Modell' };

    static _uhr = null;
    static _kennung = null;
    static FRIST_MS = 30000;          // so lange darf eine Abfrage ausstehen, bevor der Takt eine neue losschickt
    static _unterwegs = null;         // die Abfrage, die gerade aussteht (Promise) — solange sie läuft, fragt der Takt nicht nach
    static _unterwegsSeit = 0;        // ms; seit wann
    static _letzter = null;          // der letzte Stand, der wirklich vom Server kam
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
            // Eine noch ausstehende Abfrage eines ANDEREN Imports blockiert die neue nicht (und ihre späte Antwort verwirft `_holen`).
            if (Blendimportzustand._kennung !== kennung) Blendimportzustand._unterwegs = null;
            Blendimportzustand._kennung = kennung;
            Blendimportzustand._uhr = setInterval(() => Blendimportzustand.abfragen(), Blendimportzustand.TAKT_MS);
        }
        return Blendimportzustand.abfragen();
    }

    /** Nichts mehr beobachten (der Import wurde abgebrochen und gelöscht): sonst fragte der Takt nach einem Stand, den es nicht mehr gibt. */
    static vergessen() {
        clearInterval(Blendimportzustand._uhr);
        Blendimportzustand._uhr = null;
        Blendimportzustand._kennung = null;
        Blendimportzustand._unterwegs = null;
        Blendimportzustand._letzter = null;
        Blendimportzustand._getrenntSeit = null;
    }

    /**
     * Den Stand holen — aber nie zwei Abfragen zugleich (10.10.2026): Der Takt feuert alle 2 s, ein belegter Server (die synchronen Ansichten
     * teilen sich einen Faden) antwortete in 75 s, und so reihten sich ~37 Anfragen hinter die erste, jede eine Last mehr für denselben Faden.
     * Steht eine Abfrage aus, bekommt der Aufrufer sie zurück; der Takt setzt erst nach ihrer Antwort wieder an. Hängt eine Abfrage
     * länger als `FRIST_MS` (`Serverabruf` hat keine Zeitgrenze, im Protokoll standen Antworten nach 296 s und 2.494 s), darf eine neue
     * losgehen — sonst bliebe die Leiste für immer auf dem alten Stand, obwohl der Server längst wieder antwortet.
     */
    static abfragen() {
        const kennung = Blendimportzustand._kennung;
        if (!kennung) return Promise.resolve(null);
        if (Blendimportzustand._unterwegs && Date.now() - Blendimportzustand._unterwegsSeit < Blendimportzustand.FRIST_MS) {
            return Blendimportzustand._unterwegs;
        }
        const lauf = Blendimportzustand._holen(kennung).finally(() => {
            if (Blendimportzustand._unterwegs === lauf) Blendimportzustand._unterwegs = null;
        });
        Blendimportzustand._unterwegs = lauf;
        Blendimportzustand._unterwegsSeit = Date.now();
        return lauf;
    }

    static async _holen(kennung) {
        let zustand;
        try {
            zustand = await Serverabruf.json(`/api/character/blendimport/${encodeURIComponent(kennung)}/zustand/`);
        } catch (fehler) {
            if (Blendimportzustand._kennung !== kennung) return null;           // eine späte Antwort für einen Import, den niemand mehr beobachtet
            // Reißt die VERBINDUNG ab (der Server lädt nach einer gespeicherten Python-Datei neu, 09.10.2026: 50 s),
            // sagt das nichts über den Import: Er läuft als eigener Prozess weiter. Früher wurde daraus „unbekannt" —
            // rot, „Zustand nicht lesbar: Failed to fetch" — und das Fragen hörte auf, die Anzeige blieb stehen.
            // Dasselbe gilt für einen Fehlerstatus ab 500 (10.10.2026: der alte Prozess antwortete beim Beenden mit 500 „cannot schedule
            // new futures after interpreter shutdown", der Dialog zeigte die ganze HTML-Seite und fragte nie wieder) — ein echter
            // Fehler der Ansicht steht im `error.log` des Servers, nicht in der Leiste.
            if (fehler instanceof TypeError || fehler.status >= 500) return Blendimportzustand._getrennt(kennung, fehler.status);
            zustand = { status: 'unbekannt', detail: `Stand nicht lesbar (Server-Antwort: ${fehler.message})` };
        }
        if (Blendimportzustand._kennung !== kennung) return null;               // dito: abgebrochen/gelöscht oder ein anderer Import gewählt
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

    /** Der Server antwortet nicht (oder mit Fehlerstatus `status`): den letzten bekannten Stand weiterzeigen, mit dem Hinweis und den Sekunden. */
    static _getrennt(kennung, status = undefined) {
        const jetzt = Date.now();
        if (Blendimportzustand._getrenntSeit === null) Blendimportzustand._getrenntSeit = jetzt;
        const sekunden = Math.round((jetzt - Blendimportzustand._getrenntSeit) / 1000);
        const bekannt = Blendimportzustand._letzter && Blendimportzustand._letzter.kennung === kennung
            ? Blendimportzustand._letzter : { status: 'laeuft' };
        const zustand = {
            ...bekannt, kennung, verbindung: 'getrennt', getrennt_s: sekunden,
            detail: `Der Server antwortet nicht${status ? ` (Fehler ${status})` : ''} (seit ${sekunden} s) — er lädt vermutlich nach einer Codeänderung neu. `
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

    /** Der Kurzstand des Imports, der gerade rechnet: `{kennung|null, status, schritt, name}` (billig — kein Blick in die Schritte). */
    static laufendStand() {
        return Serverabruf.json('/api/character/blendimport/laufend/');
    }

    /** Kennung des Imports, der gerade rechnet (auch nach dem Neuladen der Seite) — sonst `null`. */
    static async laufend() {
        const antwort = await Blendimportzustand.laufendStand();
        return antwort.kennung || null;
    }

    /**
     * Beim Laden der Seite: rechnet ein Import, sofort den Kurzstand melden (Name, Schritt — nur an die Leiste, Ereignis `VORLAEUFIG`),
     * dann beobachten. Der erste Zustandsabruf wartet auf den einen Faden der synchronen Ansichten: am 10.10.2026 dauerte er beim Laden
     * der Szene 75 s (17:55:52 `laufend` in 1,2 s, 17:57:15 der Zustand) — so lange fehlte die Leiste ganz („ich sehe den job nicht im UI").
     */
    static async aufnehmen() {
        const lauf = await Blendimportzustand.laufendStand();
        if (!lauf.kennung) return null;
        document.dispatchEvent(new CustomEvent(Blendimportzustand.VORLAEUFIG, {
            detail: { kennung: lauf.kennung, status: lauf.status || 'laeuft', schritt: lauf.schritt, quelle: { name: lauf.name }, vorlaeufig: true },
        }));
        return Blendimportzustand.beobachten(lauf.kennung);
    }
}
