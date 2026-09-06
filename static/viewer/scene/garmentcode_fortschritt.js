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
 * eigenen Prozess und meldet sich erst am Ende. Deshalb zeigt diese Anzeige,
 * WAS gerade läuft und WIE LANGE schon — keine erfundene Prozentzahl.
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
        this.uhr = setInterval(() => this.zeichnen(), 1000);
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

    beenden() {
        if (this.uhr) { clearInterval(this.uhr); this.uhr = null; }
        this.zeichnen();
    }

    zeichnen() {
        const ziel = document.getElementById('gc-fortschritt');
        if (!ziel) return;
        const zeichen = { wartet: '·', laeuft: '▸', fertig: '✓', fehler: '✕' };
        const zeilen = this.schritte.map((schritt) => {
            let rechts = schritt.text || '';
            if (schritt.stand === 'laeuft' && schritt.seit) {
                rechts = `${Math.round((Date.now() - schritt.seit) / 1000)} s …`;
            } else if (schritt.stand === 'fertig' && schritt.dauer !== null
                       && !schritt.text) {
                rechts = `${schritt.dauer} s`;
            }
            return `<div class="slider-row"><label>${zeichen[schritt.stand]} `
                + `${schritt.titel}</label>`
                + `<span class="slider-val">${rechts}</span></div>`;
        });
        const gesamt = Math.round((Date.now() - this.beginn) / 1000);
        ziel.innerHTML = zeilen.join('')
            + `<div class="hb-font-size-0-72rem">Gesamt: ${gesamt} s</div>`;
    }
}

export const garmentcodeFortschritt = new GarmentcodeFortschritt();
