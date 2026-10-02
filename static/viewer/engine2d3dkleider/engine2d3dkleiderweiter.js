import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderweiter — „Weiterrechnen" in der Liste der Aufträge „2D3D Kleider" (Edgar, 02.10.2026: „auch ein fertiger Job
 * kann weitergerechnet werden auf Knopfdruck, mach die Funktion in den Jobs rein").
 *
 * Derselbe Weg wie der Knopf im Reiter „Iterationen" der Auftragsseite: `POST /api/engine2d3dkleider/<id>/begutachtung/` mit
 * `{automatisch: true, runden}` — die Runden setzen beim besten bisherigen Modell an, egal ob der Auftrag „Fertig",
 * „Angehalten" oder „Wartet auf Rezept" ist. Aktiv bei genau EINEM gewählten Auftrag: Die GPU rechnet einen Lauf zur Zeit
 * (`Engine2d3dKleidergpu`), ein zweiter Start würde abgewiesen.
 */
export class Engine2d3dKleiderweiter {
    /** Wie `Begutachtungsrunde.RUNDEN_HOECHSTENS` — mehr kappt der Server stumm. */
    static RUNDEN_HOECHSTENS = 50;


    constructor(wahl, knopfId = 'engine2d3dkleider-weiter', rundenId = 'engine2d3dkleider-weiter-runden',
        meldungId = 'engine2d3dkleider-weiter-meldung') {
        this.wahl = wahl;
        this.knopf = document.getElementById(knopfId);
        this.runden = document.getElementById(rundenId);
        this.meldung = document.getElementById(meldungId);
        if (!this.knopf || !this.runden || !this.meldung) {
            console.warn('[2D3D Kleider] Weiterrechnen: Knopf, Rundenfeld oder Meldung fehlt in der Vorlage');
            return;
        }
        this.knopf.addEventListener('click', () => this.starten());
    }

    anzeigen(anzahl) {
        if (!this.knopf) return;
        this.knopf.disabled = anzahl !== 1;
        this.knopf.title = anzahl === 1 ? 'Den gewählten Auftrag um so viele automatische Runden weiterrechnen'
            : 'Genau einen Auftrag wählen — die GPU rechnet einen Lauf zur Zeit';
    }

    async starten() {
        const ids = this.wahl.kennungen();
        if (ids.length !== 1) return;
        const runden = Math.max(1, Math.min(Engine2d3dKleiderweiter.RUNDEN_HOECHSTENS, Number(this.runden.value) || 1));
        this.knopf.disabled = true;
        this.meldung.textContent = 'Startet …';
        this.meldung.classList.remove('hb-schlecht');
        try {
            const antwort = await Serverabruf.senden(`/api/engine2d3dkleider/${ids[0]}/begutachtung/`,
                { aufrufe: '', kommentar: 'Weiterrechnen aus der Liste', automatisch: true, runden });
            if (antwort.error) throw new Error(antwort.error);
            this.meldung.textContent = `${runden} Runde(n) gestartet`;
        } catch (fehler) {
            this.meldung.textContent = `Nicht gestartet: ${fehler.daten?.error || fehler.message}`;
            this.meldung.classList.add('hb-schlecht');
        } finally {
            this.knopf.disabled = this.wahl.kennungen().length !== 1;
        }
    }
}
