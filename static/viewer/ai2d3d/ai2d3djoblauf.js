/**
 * Ai2d3djoblauf — Knopf „Job rechnen“ der Jobseite: PSHuman, Foto-Kette (mit Häkchen) und Genesis nacheinander (06.11.2026, `core/dienste/ai2d3djoblauf.py`).
 * Der Knopf reiht den Job in die Schlange der Rechenläufe. Danach steht neben ihm, welcher Schritt läuft; ist der Mesh3D-AI-Test eingereiht, führt die Anzeige zu dessen Seite.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3djoblauf {
    static TAKT_MS = 5000;

    /** Der Lauf zu `wurzel` — null ohne Knopf im Template. */
    static aufbauen(wurzel) {
        const knopf = wurzel.querySelector('[data-aktion="job-rechnen"]');
        return knopf ? new Ai2d3djoblauf(knopf, wurzel.querySelector('[data-jobstand]')) : null;
    }

    constructor(knopf, anzeige) {
        this.knopf = knopf;
        this.anzeige = anzeige;
        knopf.addEventListener('click', () => this.starten());
        this.abfragen();
    }

    async starten() {
        if (!confirm('Den ganzen Job rechnen? PSHuman, mit Häkchen die Foto-Kette, dann der Mesh3D-AI-Test. Die Karte ist rund 25 Minuten belegt.')) return;
        this.startet = true;
        this.knopf.disabled = true;
        try {
            const { stand } = await Serverabruf.senden(this.knopf.dataset.adresse, {});
            this.startet = false;
            this.zeigen(stand);
            window.setTimeout(() => this.abfragen(), Ai2d3djoblauf.TAKT_MS);
        } catch (fehler) {
            this.startet = false;
            alert(`Nicht gestartet: ${fehler.message}`);
            this.knopf.disabled = false;
        }
    }

    async abfragen() {
        const { stand } = await Serverabruf.json(this.knopf.dataset.stand);
        this.zeigen(stand);
        if (stand && ['wartet', 'laeuft'].includes(stand.status)) window.setTimeout(() => this.abfragen(), Ai2d3djoblauf.TAKT_MS);
    }

    /** Text neben dem Knopf; der Knopf ist gesperrt, solange der Job rechnet. */
    zeigen(stand) {
        if (!stand) return;
        const laeuft = ['wartet', 'laeuft'].includes(stand.status);
        this.knopf.disabled = laeuft || this.startet;      // die erste Abfrage kann nach dem Klick ankommen und darf den Knopf nicht wieder freigeben
        this.anzeige.textContent = '';
        if (stand.status === 'fehler') this.anzeige.textContent = stand.fehler;
        else if (stand.status === 'wartet') this.anzeige.textContent = 'Wartet in der Schlange';
        else if (laeuft) this.anzeige.textContent = stand.schritte.find(s => s.status === 'laeuft')?.text ?? '';
        else if (stand.test) {
            const verweis = document.createElement('a');
            verweis.href = `/mesh-3D-AI/test/${stand.test}/`;
            verweis.textContent = `Test ${stand.test} eingereiht`;
            this.anzeige.append(verweis);
        }
    }
}
