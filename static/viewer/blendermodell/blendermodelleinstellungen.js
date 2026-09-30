import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';

/**
 * Blendermodelleinstellungen — jede Eingabe der Auftragsseite „BlenderModel" sofort speichern (29.09.2026).
 *
 * Wie `Meshfigureinstellungen` (Edgar: „bei eingabe in irgend ein feld soll das automatisch gespeichert werden"):
 * Auswahlfelder sofort, Text- und Zahlfelder `WARTEN_MS` nach dem letzten Tastendruck. Alle drei Optionsgruppen
 * (Figur, Kostüm-Kreislauf, Blender) gehen an `POST …/einstellungen/`. Während eines Laufs ist alles gesperrt (409,
 * und die Seite sperrt die Felder), die Meldung sagt es.
 */
export class Blendermodelleinstellungen {

    static WARTEN_MS = 700;
    static GRUPPEN = {
        figur: 'blendermodell-optionen-figur',
        kostuem: 'blendermodell-optionen-kostuem',
        blender: 'blendermodell-optionen-blender',
    };

    constructor(seite) {
        this.seite = seite;
        // Die Meldung steht auf beiden Reitern (Auftrag: Figur und Blender, Iterationen: die Iterationen).
        this.meldungen = document.querySelectorAll('.einstellungen-meldung');
        this.behaelter = Object.values(Blendermodelleinstellungen.GRUPPEN).map(id => document.getElementById(id));
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
        for (const [gruppe, id] of Object.entries(Blendermodelleinstellungen.GRUPPEN)) {
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

    bald(ms = Blendermodelleinstellungen.WARTEN_MS) {
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
