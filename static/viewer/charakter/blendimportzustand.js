/**
 * Blendimportzustand — der EINE Fragesteller für den Stand eines Blender-Imports (08.10.2026).
 *
 * Fragt `/api/character/blendimport/<kennung>/zustand/` alle zwei Sekunden, solange der Import läuft, und meldet jeden
 * Stand als Ereignis `blendimport-zustand` am `document` (`detail` = der Stand samt `kennung`). Zuhörer: die Leiste
 * oben neben „HumanBody" (`Blendimportleiste`) und der Lauf im Dialog (`Blendimportfortschritt`) — beide zeigen
 * dasselbe, ohne dass der Server doppelt gefragt wird.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Blendimportzustand {

    static TAKT_MS = 2000;
    static EREIGNIS = 'blendimport-zustand';
    static TITEL = { export: 'Lesen', umposen: 'Haltung', koerper: 'Körpernetz', figur: 'Genesis-Figur', stuecke: 'Kleider & Haar',
                     haut: 'Haut backen', augen: 'Augen', modell: 'Modell' };

    static _uhr = null;
    static _kennung = null;

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
            zustand = { status: 'unbekannt', detail: `Zustand nicht lesbar: ${fehler.message}` };
        }
        zustand.kennung = kennung;
        if (!Blendimportzustand.laeuft(zustand)) {
            clearInterval(Blendimportzustand._uhr);
            Blendimportzustand._uhr = null;
        }
        document.dispatchEvent(new CustomEvent(Blendimportzustand.EREIGNIS, { detail: zustand }));
        return zustand;
    }

    /** Kennung des Imports, der gerade rechnet (auch nach dem Neuladen der Seite) — sonst `null`. */
    static async laufend() {
        const antwort = await Serverabruf.json('/api/character/blendimport/laufend/');
        return antwort.kennung || null;
    }
}
