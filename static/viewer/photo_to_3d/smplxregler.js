import { state } from './state.js';

/**
 * Smplxregler — das Reglerfeld für SMPL-X: Geschlecht, zehn Form- und zehn
 * Ausdruckswerte.
 *
 * Aus photo_to_3d/smplx_panel.js herausgeloest (Umbau 16.08.2026):
 * `buildSmplxPanel()` hatte 126 Zeilen, und die beiden Reglergruppen waren
 * ZWEIMAL derselbe 30-Zeilen-Block — einmal für `betaIdx`, einmal für
 * `exprIdx`, mit denselben Grenzen (-300..300), derselben Umrechnung (/100) und
 * derselben Anzeige (eine Dezimalstelle). Jetzt eine Methode und die Tabelle
 * `GRUPPEN`.
 */
export class Smplxregler {

    /** So viele Werte hat jede Gruppe. */
    static ANZAHL = 10;
    /** Reglergrenzen in Hundertsteln — die Werte selbst gehen von -3 bis 3. */
    static VON = -300;
    static BIS = 300;
    /** Nachkommastellen der Anzeige. */
    static STELLEN = 1;

    static GESCHLECHTER = ['female', 'male', 'neutral'];

    /**
     * Die zwei Gruppen: Titel, `data`-Name des Reglers, Zustandsfeld,
     * Beschriftungen und ob die Gruppe offen beginnt.
     */
    static GRUPPEN = [
        ['Shape (Body)', 'betaIdx', 'smplxBetas', 'SMPLX_BETA_LABELS', true],
        ['Expression (Face)', 'exprIdx', 'smplxExpr', 'SMPLX_EXPR_LABELS', false],
    ];

    /**
     * @param beschriftungen { SMPLX_BETA_LABELS, SMPLX_EXPR_LABELS }
     * @param geaendert      () => Netz neu rechnen
     */
    constructor(beschriftungen, geaendert) {
        this.beschriftungen = beschriftungen;
        this.geaendert = geaendert;
    }

    bauen() {
        this.feld = document.getElementById('smplx-panel');
        if (!this.feld) return null;
        this.feld.appendChild(this._geschlechtswahl());
        for (const gruppe of Smplxregler.GRUPPEN) this._gruppe(...gruppe);
        this._zuruecksetzen();
        return this;
    }

    _geschlechtswahl() {
        const zeile = document.createElement('div');
        zeile.className = 'smplx-zeile';
        const wahl = document.createElement('select');
        wahl.className = 'viewer-select';
        wahl.id = 'smplx-gender';
        for (const geschlecht of Smplxregler.GESCHLECHTER) {
            wahl.appendChild(new Option(
                geschlecht.charAt(0).toUpperCase() + geschlecht.slice(1),
                geschlecht));
        }
        wahl.value = state.smplxGender;
        wahl.addEventListener('change', () => {
            state.smplxGender = wahl.value;
            this.geaendert();
        });
        zeile.appendChild(wahl);
        return zeile;
    }

    /** Eine aufklappbare Gruppe mit zehn Reglern. */
    _gruppe(titel, datenname, feldname, beschriftungsname, offen) {
        const kopf = document.createElement('div');
        kopf.className = 'morph-category-header smplx-kopf';
        kopf.textContent = titel;
        const rumpf = document.createElement('div');
        rumpf.className = 'smplx-rumpf' + (offen ? '' : ' zu');
        kopf.addEventListener('click', () => rumpf.classList.toggle('zu'));

        const namen = this.beschriftungen[beschriftungsname] || [];
        for (let i = 0; i < Smplxregler.ANZAHL; i++) {
            rumpf.appendChild(this._zeile(i, datenname, feldname, namen[i]));
        }
        this.feld.append(kopf, rumpf);
    }

    _zeile(nummer, datenname, feldname, name) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const text = document.createElement('label');
        text.textContent = name || `${datenname} ${nummer}`;
        text.title = `${datenname} ${nummer}`;

        const regler = document.createElement('input');
        Object.assign(regler, { type: 'range', min: Smplxregler.VON,
                                max: Smplxregler.BIS, value: 0, step: 1 });
        regler.dataset[datenname] = nummer;

        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.textContent = (0).toFixed(Smplxregler.STELLEN);

        regler.addEventListener('input', () => {
            const wert = parseInt(regler.value, 10) / 100;
            anzeige.textContent = wert.toFixed(Smplxregler.STELLEN);
            state[feldname][nummer] = wert;
            this.geaendert();
        });

        zeile.append(text, regler, anzeige);
        return zeile;
    }

    _zuruecksetzen() {
        document.getElementById('reset-smplx')?.addEventListener('click', () => {
            state.smplxBetas.fill(0);
            state.smplxExpr.fill(0);
            for (const regler of this.feld.querySelectorAll('input[type="range"]')) {
                regler.value = 0;
                const anzeige = regler.parentElement.querySelector('.slider-val');
                if (anzeige) anzeige.textContent = (0).toFixed(Smplxregler.STELLEN);
            }
            this.geaendert();
        });
    }
}
