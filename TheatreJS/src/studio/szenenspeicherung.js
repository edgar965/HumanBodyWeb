import { Seitenlisten } from './seitenlisten.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Szenenspeicherung — der Dialog „Szene speichern".
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Gespeichert wird mehr als die
 * Figuren: auch Kamera, Umlaufsteuerung und Lichter — eine Bühne ohne ihre
 * Beleuchtung wieder zu laden wäre wertlos.
 *
 * Der Knopf sperrt sich während des Speicherns; ein zweiter Klick würde sonst
 * eine zweite Datei mit demselben Namen schreiben.
 */
export class Szenenspeicherung {

    static DIALOG = 'modal-scene-save';

    constructor(figurenlader, buehne) {
        this.figurenlader = figurenlader;
        this.buehne = buehne;      // { camera, controls, lights }
        this.knopf = document.getElementById('scene-save-btn');
        this.feld = document.getElementById('scene-save-name');
    }

    verdrahten() {
        document.getElementById('menu-scene-save')
            ?.addEventListener('click', () => this.oeffnen());
        if (!this.knopf || !this.feld) return this;
        this.knopf.addEventListener('click', () => this.speichern());
        this.feld.addEventListener('keydown', ereignis => {
            if (ereignis.key === 'Enter') this.knopf.click();
        });
        return this;
    }

    oeffnen() {
        Seitenlisten.oeffnen(Szenenspeicherung.DIALOG);
        if (!this.feld) return;
        this.feld.value = '';
        this.feld.focus();
    }

    async speichern() {
        const name = this.feld.value.trim();
        if (!name) return;
        this.knopf.disabled = true;
        this.knopf.textContent = 'Speichere …';
        try {
            await this.figurenlader.speichern(name, this.buehne);
            Seitenlisten.schliessen(Szenenspeicherung.DIALOG);
        } catch (fehler) {
            Protokoll.fehler('main', 'Szene speichern fehlgeschlagen', fehler);
            alert('Szene speichern fehlgeschlagen: ' + fehler.message);
        }
        this.knopf.disabled = false;
        this.knopf.textContent = 'Speichern';
    }
}
