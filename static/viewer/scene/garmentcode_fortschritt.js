import { Fortschrittsrechnung } from '../gemeinsam/fortschrittsrechnung.js';

/**
 * Fortschrittsanzeige für den GarmentCode-Reiter.
 *
 * Der Bau läuft in Schritten, die unterschiedlich lange dauern (gemessen am
 * 06.09.2026): Maße nehmen unter einer Sekunde, der Schnitt 3–9 s, die
 * Drapierung 25–190 s, das Anziehen 0,6 s. Ohne Anzeige sieht der Nutzer
 * eine Minute lang nichts und hält den Knopf für kaputt — genau das ist
 * passiert.
 *
 * Echten Fortschritt vom Server gibt es nicht: Die Simulation läuft in einem
 * eigenen Prozess und meldet sich erst am Ende. Der Balken schätzt deshalb
 * aus den gemessenen Dauern (`Fortschrittsrechnung`) und läuft nie voll,
 * bevor der Schritt es wirklich ist. Darunter steht weiter, WAS gerade
 * läuft und wie lange schon — das ist die Angabe, die nicht schätzt.
 */
class GarmentcodeFortschritt {
    constructor() {
        this.schritte = [];
        this.uhr = null;
        this.beginn = 0;
    }

    /** Die Schritte festlegen und die Anzeige aufbauen. */
    starten(schritte) {
        const ziel = document.getElementById('gc-fortschritt');
        if (!ziel) return;
        this.schritte = schritte.map((s) => ({ ...s, stand: 'wartet' }));
        this.beginn = Date.now();
        ziel.classList.remove('hb-versteckt');
        this.zeichnen();
        // Jede halbe Sekunde: Der Balken soll sichtbar kriechen, nicht
        // im Sekundentakt springen.
        this.uhr = setInterval(() => this.zeichnen(), 500);
    }

    /** Einen Schritt als laufend markieren. */
    laeuft(schluessel) {
        for (const schritt of this.schritte) {
            if (schritt.schluessel === schluessel) {
                schritt.stand = 'laeuft';
                schritt.seit = Date.now();
            }
        }
        this.zeichnen();
    }

    /** Einen Schritt abschließen — mit einem kurzen Ergebnistext. */
    fertig(schluessel, text = '') {
        for (const schritt of this.schritte) {
            if (schritt.schluessel === schluessel) {
                schritt.stand = 'fertig';
                schritt.text = text;
                schritt.dauer = schritt.seit
                    ? Math.round((Date.now() - schritt.seit) / 1000) : null;
            }
        }
        this.zeichnen();
    }

    /** Einen Schritt als gescheitert markieren. */
    gescheitert(schluessel, text) {
        for (const schritt of this.schritte) {
            if (schritt.schluessel === schluessel) {
                schritt.stand = 'fehler';
                schritt.text = text;
            }
        }
        this.beenden();
    }

    /** Schritte, die nicht mehr kommen, aus der Anzeige nehmen. */
    entfallen(schluessel) {
        this.schritte = this.schritte.filter((s) => s.schluessel !== schluessel);
        this.zeichnen();
    }

    beenden() {
        if (this.uhr) { clearInterval(this.uhr); this.uhr = null; }
        this.zeichnen();
    }

    // ------------------------------------------------------------- zeichnen

    /** Die Schritte so, wie die Rechnung sie erwartet. */
    stand() {
        const jetzt = Date.now();
        return this.schritte.map((s) => ({
            stand: s.stand,
            erwartet: s.erwartet,
            verstrichen: s.seit ? (jetzt - s.seit) / 1000 : 0,
        }));
    }

    zeichnen() {
        const ziel = document.getElementById('gc-fortschritt');
        if (!ziel) return;
        const stand = this.stand();
        const anteil = Fortschrittsrechnung.gesamt(stand);
        const laufend = this.schritte.find((s) => s.stand === 'laeuft');
        const rest = this.uhr ? Fortschrittsrechnung.rest(stand) : null;
        const gesamt = Math.round((Date.now() - this.beginn) / 1000);

        ziel.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill" style="width:${(anteil * 100).toFixed(1)}%"></div>
            </div>
            <div class="slider-row hb-font-size-0-72rem">
                <label>${laufend ? laufend.titel : (this.uhr ? '…' : 'fertig')}</label>
                <span class="slider-val">${Math.round(anteil * 100)} %${
                    rest !== null ? ` · noch ~${Fortschrittsrechnung.zeit(rest)}` : ''}</span>
            </div>
            ${this.zeilen()}
            <div class="hb-font-size-0-72rem">Gesamt: ${Fortschrittsrechnung.zeit(gesamt)}</div>`;
    }

    zeilen() {
        const zeichen = { wartet: '·', laeuft: '▸', fertig: '✓', fehler: '✕' };
        return this.schritte.map((schritt) => {
            let rechts = schritt.text || '';
            if (schritt.stand === 'laeuft' && schritt.seit) {
                const bisher = Math.round((Date.now() - schritt.seit) / 1000);
                // WENN ES LÄNGER DAUERT, SAGEN WIE VIEL LÄNGER (09.09.2026,
                // Edgar: „danach war das UI nicht mehr bedienbar"). Sein Lauf
                // stand bei 105 s gegen 22 s erwartet: Der Balken war bei
                // seinen 97 % gedeckelt, daneben stand nur „105 s …", und
                // das sieht nach einem Stillstand aus. Es lief noch — der
                // Serverlog zeigt die Simulation bis Sekunde 118.
                rechts = (schritt.erwartet && bisher > 2 * schritt.erwartet)
                    ? `${bisher} s … (erwartet ${schritt.erwartet} s)`
                    : `${bisher} s …`;
            } else if (schritt.stand === 'fertig' && schritt.dauer !== null
                       && !schritt.text) {
                rechts = `${schritt.dauer} s`;
            }
            return `<div class="slider-row"><label>${zeichen[schritt.stand]} `
                + `${schritt.titel}</label>`
                + `<span class="slider-val">${rechts}</span></div>`;
        }).join('');
    }
}

export const garmentcodeFortschritt = new GarmentcodeFortschritt();
