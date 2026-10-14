/**
 * Mesh3dkopie — die Knöpfe „Kopie ohne Daten“ und „Kopie mit allen Daten“ (11.10.2026).
 *
 * Edgar: „die Kopie-Möglichkeit für Jobs vergessen“ — wie in der Liste von „2D3D Kleider“: ohne Daten = dieselbe Datei und dieselben Einstellungen, nichts gerechnet; mit allen Daten = der ganze
 * Auftrag samt Netzen, Figur, Haut und dem Auftrag „Mesh to 3D“ (`Mesh3dkopie` im Server). Dieselbe Klasse bedient die Liste (angehakte Zeilen, danach lädt die Seite neu) und die Jobseite (dieser
 * eine Auftrag, danach geht es auf die Seite der Kopie). Die Kopie startet nichts.
 */
import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Mesh3dkopie {
    static ADRESSE = '/api/mesh3d/kopieren/';

    /**
     * @param {() => string[]} kennungen die Aufträge, die kopiert werden
     * @param {{knopf: string|HTMLElement, zaehler?: string|HTMLElement|null, mitDaten: boolean}[]} knoepfe die Knöpfe im Dokument — als Id (Jobseite) oder als Element (die Listen der Reiter,
     *   dort gibt es jeden Knopf je Reiter einmal und also keine eindeutige Id); `zaehler`: die Zahl darin
     * @param {boolean} springen mit genau einer Kopie auf deren Seite wechseln (Jobseite), sonst die Seite neu laden (Liste)
     */
    constructor(kennungen, knoepfe, springen = false) {
        this.kennungen = kennungen;
        this.springen = springen;
        const holen = x => (typeof x === 'string' ? document.getElementById(x) : x || null);
        this.knoepfe = knoepfe.map(k => ({ knopf: holen(k.knopf), zaehler: holen(k.zaehler), mitDaten: k.mitDaten }))
            .filter(k => k.knopf);
        for (const k of this.knoepfe) k.knopf.addEventListener('click', () => this.kopieren(k));
    }

    /** Aufruf, wenn sich die Auswahl ändert: Knöpfe nur mit Auswahl frei. */
    anzeigen(anzahl) {
        for (const k of this.knoepfe) {
            k.knopf.disabled = anzahl === 0;
            if (k.zaehler) k.zaehler.textContent = String(anzahl);
        }
    }

    static frage(anzahl, mitDaten) {
        return mitDaten
            ? `${anzahl} Auftrag/Aufträge mit allen Daten kopieren (Netze, Figur, Haut, Ergebnisse, Auftrag „Mesh to 3D“)? Das kopiert den ganzen Ordner und kann etwas dauern. Das gespeicherte Modell wird nicht kopiert.`
            : `${anzahl} Auftrag/Aufträge ohne Daten kopieren? Es entstehen neue Aufträge mit derselben Datei und denselben Einstellungen — nichts wird gerechnet.`;
    }

    async kopieren(eintrag) {
        const ids = this.kennungen();
        if (!ids.length || !window.confirm(Mesh3dkopie.frage(ids.length, eintrag.mitDaten))) return;
        try {
            // Ohne Ersatztext: `Knopfsperre` schriebe ihn in die äußere Hülle und nähme den Zähler mit.
            await Knopfsperre.waehrend(eintrag.knopf, async () => {
                const antwort = await Serverabruf.senden(Mesh3dkopie.ADRESSE, { ids, mit_daten: eintrag.mitDaten });
                if (antwort.error) throw new Error(antwort.error);
                if (this.springen && antwort.auftraege.length === 1) window.location.href = antwort.auftraege[0].url;
                else window.location.reload();
            });
        } catch (fehler) {
            const teilweise = (fehler.daten?.kopiert || 0) > 0;
            window.alert(`Kopieren fehlgeschlagen: ${fehler.daten?.error || fehler.message}${teilweise ? ` (${fehler.daten.kopiert} Kopie(n) sind schon angelegt)` : ''}`);
            if (teilweise) window.location.reload();
        }
    }
}
