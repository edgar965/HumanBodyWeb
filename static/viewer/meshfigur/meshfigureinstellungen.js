import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';

/**
 * Meshfigureinstellungen — jede Eingabe der Auftragsseite „Mesh to 3D" sofort speichern (29.09.2026).
 *
 * Edgar: „bei eingabe in irgend ein feld soll das automatisch gespeichert werden". Optionen, beide Pfade und
 * der Schalter „Kopfnetz verwenden" gehen an `POST …/einstellungen/` — Auswahlfelder und Schalter sofort,
 * Text- und Zahlfelder `WARTEN_MS` nach dem letzten Tastendruck (ein Pfad wird dabei kopiert; halbe Pfade
 * nach jedem Buchstaben wären lauter Fehlermeldungen). Ein falscher Pfad kommt als Meldung unter die Felder,
 * die Optionen sind dann trotzdem gespeichert. Während eines Laufs ist alles gesperrt (409), die Meldung
 * sagt es.
 */
export class Meshfigureinstellungen {

    static WARTEN_MS = 700;

    constructor(seite) {
        this.seite = seite;
        this.optionen = document.getElementById('meshfigur-optionen');
        this._uhr = null;
        this._lauf = Promise.resolve();
        for (const feld of [this.optionen, document.getElementById('eingangspfade')]) {
            feld?.addEventListener('change', () => this.bald(0));
            feld?.addEventListener('input', ereignis => {
                if (ereignis.target.matches('input[type="text"], input[type="number"], textarea')) this.bald();
            });
        }
    }

    bald(ms = Meshfigureinstellungen.WARTEN_MS) {
        clearTimeout(this._uhr);
        this._uhr = setTimeout(() => { this._lauf = this._lauf.then(() => this.speichern()); }, ms);
    }

    /** Sofort, ohne Warten (vor „Neu berechnen“) — true, wenn gespeichert. */
    async jetzt() {
        clearTimeout(this._uhr);
        await this._lauf;
        return this.speichern();
    }

    async speichern() {
        const pfade = this.seite.pfade;
        const rumpf = {
            optionen: Meshoptionenformular.lesen(this.optionen),
            pfade: pfade.lesen(),
            kopf_an: pfade.kopfVerwenden(),
        };
        try {
            const antwort = await Serverabruf.senden(this.seite.adresse('einstellungen/'), rumpf);
            if (antwort.error) throw new Error(antwort.error);
            this.seite.zustand.eingang = antwort.eingang;
            const zeit = new Date().toLocaleTimeString('de-DE');
            pfade.melden(antwort.neu_eingelesen || antwort.eingang?.neu_eingelesen
                ? `Gespeichert ${zeit} — Netz neu eingelesen, „Neu berechnen“ beginnt bei der Erkennung.`
                : `Gespeichert ${zeit}.`);
            return true;
        } catch (fehler) {
            pfade.melden(`Nicht gespeichert: ${fehler.daten?.error || fehler.message}`, true);
            return false;
        }
    }
}
