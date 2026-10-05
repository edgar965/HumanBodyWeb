import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderBewertung — der Reiter „Bewertung" jeder Auftragsseite (05.10.2026).
 *
 * Edgar: „Versuche, die Rückmeldungen und Vorgaben aus meinen Prompts zusammenzufassen. Schreibe diese Zusammenfassung in einem neuen Tab ‚Bewertung' in allen Jobs."
 * Die Zusammenfassung liegt als `daten/bewertung.json` im Paket `Edgar` (`2d3DIterationen`) und kommt über `GET /api/engine2d3dkleider/bewertung/` — dieselbe für
 * jeden Auftrag. Gezeigt wird sie nur; geändert wird die Datei. Ein eigenes Modulskript (nicht an der Seitenklasse), damit der Reiter auch bei einer
 * hängenden Seite etwas zeigt.
 */
export class Engine2d3dKleiderBewertung {

    static ADRESSE = '/api/engine2d3dkleider/bewertung/';

    static async starten() {
        const feld = new Engine2d3dKleiderBewertung();
        await feld.laden();
        return feld;
    }

    constructor() {
        this.titel = document.getElementById('bewertung-titel');
        this.quelle = document.getElementById('bewertung-quelle');
        this.hinweis = document.getElementById('bewertung-hinweis');
        this.inhalt = document.getElementById('bewertung-inhalt');
    }

    async laden() {
        if (!this.inhalt) {
            console.warn('[2D3D Kleider] Bewertung: Reiter fehlt in der Vorlage');
            return;
        }
        try {
            this.zeigen(await Serverabruf.json(Engine2d3dKleiderBewertung.ADRESSE));
        } catch (fehler) {
            this.quelle.textContent = `Bewertung nicht lesbar: ${fehler.daten?.error || fehler.message}`;
        }
    }

    zeigen(daten) {
        this.titel.textContent = daten.titel || 'Bewertung';
        this.quelle.textContent = `Quelle: ${daten.quelle || '–'} · Stand ${daten.stand || '–'}`;
        this.hinweis.textContent = daten.hinweis || '';
        this.inhalt.replaceChildren(...(daten.abschnitte || []).map(a => this.abschnitt(a)));
    }

    /** Ein Abschnitt: Überschrift mit Kennzeichen („Gilt: alle/Randy", „für den Agenten") und seine Punkte mit Beleg. */
    abschnitt(a) {
        const wurzel = document.createElement('section');
        wurzel.className = 'bewertung-abschnitt';
        const kopf = document.createElement('h3');
        kopf.className = 'engine2d3dkleider-gruppe';
        kopf.textContent = a.titel;
        const marken = document.createElement('span');
        marken.className = 'hb-hinweis bewertung-marken';
        marken.textContent = ` Gilt: ${a.gilt || 'alle'} · ${a.fuer_agent ? 'für den Agenten der Nachbesserung' : 'nicht im Prompt des Agenten'}`;
        kopf.appendChild(marken);
        const liste = document.createElement('ul');
        liste.className = 'bewertung-punkte';
        for (const p of a.punkte || []) {
            const punkt = document.createElement('li');
            punkt.textContent = p.text;
            if (p.beleg) {
                const beleg = document.createElement('span');
                beleg.className = 'hb-hinweis bewertung-beleg';
                beleg.textContent = ` (${p.beleg})`;
                punkt.appendChild(beleg);
            }
            liste.appendChild(punkt);
        }
        wurzel.append(kopf, liste);
        return wurzel;
    }
}
