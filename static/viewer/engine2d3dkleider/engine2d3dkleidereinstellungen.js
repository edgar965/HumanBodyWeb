import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';

/**
 * Engine2d3dKleidereinstellungen — jede Eingabe der Auftragsseite „2D3D Kleider" sofort speichern.
 *
 * Auswahlfelder sofort, Text- und Zahlfelder `WARTEN_MS` nach dem letzten Tastendruck. Alle acht Optionsgruppen (Grundfigur,
 * Vorbereitung, Netz, Mesh, Segmentierung, Körper, Iterationen, Film) gehen an `POST …/einstellungen/`. Während eines Laufs ist alles gesperrt (409, und die Seite sperrt die Felder),
 * die Meldung sagt es.
 */
export class Engine2d3dKleidereinstellungen {

    static WARTEN_MS = 700;
    // `netz`, `mesh` und `koerper` fehlten bis 02.10.2026: Ihre Formulare wurden gebaut, aber nie gespeichert — eine
    // geänderte Auflösung blieb auf dem Server unverändert (an `.14.08.48` gemessen: „mittel" gewählt, „hoch" gespeichert).
    /** Gruppe -> Id des Behälters: jeder Behälter "engine2d3dkleider-optionen-<gruppe>" der Seite (04.10.2026: dazu die Renderregler; die Liste stand vorher fest im Code). */
    static get GRUPPEN() {
        const vorsatz = 'engine2d3dkleider-optionen-';
        return Object.fromEntries([...document.querySelectorAll(`[id^="${vorsatz}"]`)].map(e => [e.id.slice(vorsatz.length), e.id]));
    }

    constructor(seite) {
        this.seite = seite;
        // Die Meldung steht auf beiden Reitern (Auftrag: Figur und Film, Iterationen: die Iterationen).
        this.meldungen = document.querySelectorAll('.einstellungen-meldung');
        this.behaelter = Object.values(Engine2d3dKleidereinstellungen.GRUPPEN).map(id => document.getElementById(id));
        this._uhr = null;
        this._lauf = Promise.resolve();
        for (const feld of this.behaelter) {
            feld?.addEventListener('change', () => this.bald(0));
            feld?.addEventListener('input', ereignis => {
                if (ereignis.target.matches('input[type="text"], input[type="number"], textarea')) this.bald();
            });
        }
    }

    /** Die Werte beider Gruppen, wie sie jetzt im Formular stehen. */
    optionen() {
        const aus = {};
        for (const [gruppe, id] of Object.entries(Engine2d3dKleidereinstellungen.GRUPPEN)) {
            aus[gruppe] = Meshoptionenformular.lesen(document.getElementById(id));
        }
        return aus;
    }

    /** Felder sperren, solange der Lauf rechnet — der Arbeitsprozess hat seine Optionen schon gelesen. */
    sperren(gesperrt) {
        for (const feld of this.behaelter) {
            for (const eingabe of feld?.querySelectorAll('input, select, textarea') || []) eingabe.disabled = gesperrt;
        }
    }

    bald(ms = Engine2d3dKleidereinstellungen.WARTEN_MS) {
        clearTimeout(this._uhr);
        this._uhr = setTimeout(() => { this._lauf = this._lauf.then(() => this.speichern()); }, ms);
    }

    /** Sofort, ohne Warten (vor „Neu berechnen“) — true, wenn gespeichert. */
    async jetzt() {
        clearTimeout(this._uhr);
        await this._lauf;
        return this.speichern();
    }

    _melden(text, fehler = false) {
        for (const feld of this.meldungen) {
            feld.textContent = text;
            feld.classList.toggle('hb-schlecht', fehler);
        }
    }

    async speichern() {
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('einstellungen/'), { optionen: this.optionen() });
            if (antwort.error) throw new Error(antwort.error);
            this.seite.zustand.optionen = antwort.optionen;
            this._melden(`Gespeichert ${new Date().toLocaleTimeString('de-DE')}.`);
            return true;
        } catch (fehler) {
            this._melden(`Nicht gespeichert: ${fehler.daten?.error || fehler.message}`, true);
            return false;
        }
    }
}
