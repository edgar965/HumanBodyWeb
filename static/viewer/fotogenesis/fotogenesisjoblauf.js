/**
 * Fotogenesisjoblauf — Knopf „Job rechnen“ der Jobseite: Foto-Mesh (PSHuman) und Mesh-Genesis nacheinander (06.11.2026, `core/dienste/fotogenesisjoblauf.py`; Foto-Kette seit 09.11.2026 heraus).
 * Der Knopf reiht den Job in die Schlange der Rechenläufe. Danach steht neben ihm, welcher Schritt läuft; ist der Mesh-Genesis-Test eingereiht, führt die Anzeige zu dessen Seite.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Fotogenesisjoblauf {
    static TAKT_MS = 5000;

    /** Der Lauf zu `wurzel` — null ohne Knopf im Template. */
    static aufbauen(wurzel) {
        const knopf = wurzel.querySelector('[data-aktion="job-rechnen"]');
        return knopf ? new Fotogenesisjoblauf(knopf, wurzel.querySelector('[data-jobstand]')) : null;
    }

    constructor(knopf, anzeige) {
        this.knopf = knopf;
        this.anzeige = anzeige;
        knopf.addEventListener('click', () => this.starten());
        this.abfragen();
    }

    async starten() {
        if (!confirm('Den ganzen Job rechnen? Foto-Mesh (PSHuman), dann der Mesh-Genesis-Test. Die Karte ist rund 25 Minuten belegt.')) return;
        this.startet = true;
        this.knopf.disabled = true;
        try {
            const { stand } = await Serverabruf.senden(this.knopf.dataset.adresse, {});
            this.startet = false;
            this.zeigen(stand);
            window.setTimeout(() => this.abfragen(), Fotogenesisjoblauf.TAKT_MS);
        } catch (fehler) {
            this.startet = false;
            alert(`Nicht gestartet: ${fehler.message}`);
            this.knopf.disabled = false;
        }
    }

    async abfragen() {
        const { stand } = await Serverabruf.json(this.knopf.dataset.stand);
        this.zeigen(stand);
        if (stand && ['wartet', 'laeuft'].includes(stand.status)) window.setTimeout(() => this.abfragen(), Fotogenesisjoblauf.TAKT_MS);
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
            verweis.href = `/mesh-genesis/test/${stand.test}/`;
            verweis.textContent = `Test ${stand.test} eingereiht`;
            this.anzeige.append(verweis);
        }
    }
}
