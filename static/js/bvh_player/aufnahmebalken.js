/**
 * Aufnahmebalken — der Fortschritt über der 3D-Ansicht während der Aufnahme.
 *
 * Aus `job_result.html` und `standalone_result.html` herausgelöst (Umbau
 * 28.08.2026, Befund `doppelcode`): Der Balken wurde in beiden Vorlagen mit
 * fünf `style.cssText`-Zeilen von Hand gebaut — dieselben fünf, zweimal.
 *
 * Die Stile stehen jetzt in `stilhelfer.css` (`.aufnahmebalken*`); hier bleibt
 * nur der Aufbau und das Nachziehen des Fortschritts.
 */
export class Aufnahmebalken {
    /** So oft wie das Bild — der Fortschritt hängt an `video.currentTime`. */
    static _kennung = null;

    /**
     * @param {HTMLElement} ansicht Element, über das der Balken gelegt wird
     */
    constructor(ansicht) {
        this.ansicht = ansicht;
        this.balken = document.createElement('div');
        this.balken.className = 'aufnahmebalken';

        this.punkt = document.createElement('span');
        this.punkt.className = 'aufnahmepunkt';

        this.bahn = document.createElement('div');
        this.bahn.className = 'aufnahmebahn';
        this.fuellung = document.createElement('div');
        this.fuellung.className = 'aufnahmefuellung';
        this.bahn.appendChild(this.fuellung);

        this.beschriftung = document.createElement('span');
        this.beschriftung.className = 'aufnahmeanteil';
        this.beschriftung.textContent = '0%';

        this.balken.append(this.punkt, this.bahn, this.beschriftung);
        // `position: relative` am Rahmen, sonst liegt der Balken am Fenster
        // statt an der Ansicht.
        this.ansicht.style.position = 'relative';
        this.ansicht.appendChild(this.balken);
    }

    /** Den Fortschritt aus dem Video nachziehen, bis `anhalten()` kommt. */
    verfolgen(video) {
        const takt = () => {
            if (video.duration > 0) {
                this.setzen(Math.min(
                    100, (video.currentTime / video.duration) * 100));
            }
            this._kennung = requestAnimationFrame(takt);
        };
        this._kennung = requestAnimationFrame(takt);
    }

    anhalten() {
        if (this._kennung !== null) cancelAnimationFrame(this._kennung);
        this._kennung = null;
    }

    setzen(anteil) {
        this.fuellung.style.width = anteil + '%';
        this.beschriftung.textContent = Math.round(anteil) + '%';
    }

    melden(text) {
        this.beschriftung.textContent = text;
    }

    fertig() {
        this.anhalten();
        this.setzen(100);
    }

    weg() {
        this.anhalten();
        this.balken.remove();
    }
}
