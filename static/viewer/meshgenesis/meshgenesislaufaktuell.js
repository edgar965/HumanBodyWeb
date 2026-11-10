import { Meshgenesislaufaktuellzeichner } from './meshgenesislaufaktuellzeichner.js';
import { Meshgenesiswarteschlangezeichner } from './meshgenesiswarteschlangezeichner.js';

/**
 * Meshgenesislaufaktuell — der Reiter „Lauf Aktuell“ auf /mesh-genesis/ (18.10.2026, Edgar: „mach auch einen neuen Tab: ‚Lauf Aktuell‘, wo du den gerade laufenden Job listest,
 * mit GPU, CPU-Verbrauch und Fortschrittsbalken“).
 *
 * Fragt `GET /api/meshgenesis/lauf-aktuell/` im Takt des Servers (`takt_s`), NUR solange das Feld des Reiters sichtbar und der Tab im Vordergrund ist: Ein verdeckter Reiter
 * stößt keine Messung an (die kostet auf dem Server rund 1 s im Hintergrund — Zählerabfrage, Prozessliste). Der Wechsel des Reiters setzt `hidden` am Feld (`Seitenreiter`);
 * ein `MutationObserver` darauf startet und hält an.
 */
export class Meshgenesislaufaktuell {
    static ADRESSE = '/api/meshgenesis/lauf-aktuell/';

    static binden(feld) {
        if (!feld) return null;
        const reiter = new Meshgenesislaufaktuell(feld);
        reiter.beobachten();
        return reiter;
    }

    constructor(feld) {
        this.feld = feld;
        this.ziel = feld.querySelector('[data-laufaktuell]') || feld;
        this.uhr = null;
        this.takt = 5000;
        this.holt = false;
    }

    beobachten() {
        const pruefen = () => (this.sichtbar() ? this.starten() : this.anhalten());
        new MutationObserver(pruefen).observe(this.feld, { attributes: true, attributeFilter: ['hidden'] });
        document.addEventListener('visibilitychange', pruefen);
        pruefen();
    }

    sichtbar() {
        return !this.feld.hidden && !document.hidden;
    }

    starten() {
        if (this.uhr) return;
        this.holen();
        this.uhr = setInterval(() => this.holen(), this.takt);
    }

    anhalten() {
        clearInterval(this.uhr);
        this.uhr = null;
    }

    async holen() {
        if (this.holt) return;
        this.holt = true;
        try {
            const antwort = await fetch(Meshgenesislaufaktuell.ADRESSE, { headers: { Accept: 'application/json' } });
            if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
            const stand = await antwort.json();
            this.ziel.replaceChildren(...Meshgenesislaufaktuell.karten(stand));
            this.taktSetzen(stand.takt_s);
        } catch (fehler) {
            const meldung = Meshgenesislaufaktuellzeichner.el('p', 'meshgenesis-la-fehler', `Stand nicht abrufbar: ${fehler.message} — nächster Versuch in ${this.takt / 1000} s.`);
            this.ziel.querySelector('.meshgenesis-la-fehler')?.remove();
            this.ziel.prepend(meldung);
        } finally {
            this.holt = false;
        }
    }

    /** Rechner · laufende Jobs · Warteschlange (ersetzt seit 18.10.2026 „Ketten im Hintergrund“) · andere Programme auf der GPU · Fuß. */
    static karten(stand, jetzt = Date.now() / 1000) {
        const z = Meshgenesislaufaktuellzeichner;
        return [z.rechner(stand, jetzt), z.jobs(stand, jetzt), Meshgenesiswarteschlangezeichner.karte(stand, jetzt), z.fremde(stand), z.fuss(stand)].filter(Boolean);
    }

    taktSetzen(sekunden) {
        const ms = Math.max(2, Number(sekunden) || 5) * 1000;
        if (ms === this.takt) return;
        this.takt = ms;
        if (this.uhr) {
            clearInterval(this.uhr);
            this.uhr = setInterval(() => this.holen(), ms);
        }
    }
}
