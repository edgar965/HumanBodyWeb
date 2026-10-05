import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderVorgabe — der Prompt des Rundenberaters im Reiter „Bewertung", editierbar (05.10.2026).
 *
 * Edgar: „der prompt soll editierbar sein, mach einen Speichern button und wende den neuen Prompt dann an für die nächste Runde."
 * Der Text liegt als Datei `2d3DIterationen/Edgar/vorgaben/abgleich.md` auf dem Server (`GET /api/engine2d3dkleider/vorgabe/`); „Speichern" schickt ihn an
 * `POST …/vorgabe/speichern/`. Der Server liest die Datei bei jedem Bau des Prompts, der neue Text gilt also ab der nächsten Iteration — dafür gibt es hier nichts weiter zu tun.
 * Ein eigenes Modulskript (nicht an der Seitenklasse), damit der Reiter auch bei einer hängenden Seite etwas zeigt.
 */
export class Engine2d3dKleiderVorgabe {

    static ADRESSE = '/api/engine2d3dkleider/vorgabe/';

    static async starten() {
        const feld = new Engine2d3dKleiderVorgabe();
        await feld.laden();
        return feld;
    }

    constructor() {
        this.text = document.getElementById('vorgabe-text');
        this.knopf = document.getElementById('vorgabe-speichern');
        this.status = document.getElementById('vorgabe-status');
        this.gespeichert = '';
        if (this.text && this.knopf) {
            this.text.addEventListener('input', () => this.pruefen());
            this.knopf.addEventListener('click', () => this.speichern());
        }
    }

    /** Knopf nur, wenn sich der Text vom gespeicherten unterscheidet. */
    pruefen() {
        const geaendert = this.text.value !== this.gespeichert;
        this.knopf.disabled = !geaendert;
        if (geaendert) this.status.textContent = 'Nicht gespeichert';
    }

    zeigen(daten, meldung) {
        this.gespeichert = daten.text;
        this.text.value = daten.text;
        this.text.disabled = false;
        this.knopf.disabled = true;
        this.status.textContent = meldung(daten);
    }

    async laden() {
        if (!this.text || !this.knopf) {
            console.warn('[2D3D Kleider] Prompt: Feld fehlt in der Vorlage');
            return;
        }
        try {
            this.zeigen(await Serverabruf.json(Engine2d3dKleiderVorgabe.ADRESSE), d => `Gespeicherter Stand: ${d.gespeichert}`);
        } catch (fehler) {
            this.status.textContent = `Prompt nicht lesbar: ${fehler.daten?.error || fehler.message}`;
        }
    }

    async speichern() {
        this.knopf.disabled = true;
        this.status.textContent = 'Wird gespeichert …';
        try {
            const daten = await Serverabruf.senden(`${Engine2d3dKleiderVorgabe.ADRESSE}speichern/`, { text: this.text.value });
            this.zeigen(daten, d => `Gespeichert (${d.gespeichert}) — gilt ab der nächsten Iteration`);
        } catch (fehler) {
            this.status.textContent = `Nicht gespeichert: ${fehler.daten?.error || fehler.message}`;
            this.knopf.disabled = false;
        }
    }
}
