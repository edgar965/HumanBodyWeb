import { Panel } from './panel.js';

/**
 * Lichtpanel — Helligkeit, Farbe, Position und Drehung eines Bühnenlichts.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): 162 Zeilen, davon rund 90 nur
 * Inline-Stile in einer HTML-Vorlage. Die Regeln stehen jetzt als `.pnl-*` im
 * Stilblock von theatre.html, hier bleibt die Fachlogik — welche Werte das
 * Licht hat und was beim Verstellen mit dem Symbol in der Szene passiert.
 */
export class Lichtpanel {

    static GRAD = 180 / Math.PI;

    /**
     * @param {Object} lichter  die benannten Lichter aus createScene
     */
    constructor(lichter) {
        this.lichter = lichter;
        //: Das Symbol in der Szene, das zum gewaehlten Licht gehoert. Wird von
        //: aussen gesetzt, weil die Auswahl beim Klick in der Szene entsteht.
        this.symbol = null;
    }

    name(licht) {
        if (licht === this.lichter.spotLeft) return 'Spot Left';
        if (licht === this.lichter.spotRight) return 'Spot Right';
        if (licht === this.lichter.backLight) return 'Back Light';
        return 'Licht';
    }

    zeigen(licht, symbol = null) {
        if (symbol) this.symbol = symbol;
        const ziel = Panel.oeffnen();
        if (!ziel) return;
        const grad = Lichtpanel.GRAD;
        ziel.innerHTML = `<div class="pnl-inhalt">
            ${Panel.kopf('fa-lightbulb', this.name(licht))}
            ${Panel.schieber('light-intensity', 'Intensität',
                             licht.intensity.toFixed(1), { max: 100 })}
            ${Panel.farbfeld('light-color', 'Farbe', '#' + licht.color.getHexString())}
            ${Panel.dreierblock('Position', 'light-pos',
                                [licht.position.x.toFixed(2),
                                 licht.position.y.toFixed(2),
                                 licht.position.z.toFixed(2)])}
            ${Panel.dreierblock('Rotation (Grad)', 'light-rot',
                                [(licht.rotation.x * grad).toFixed(1),
                                 (licht.rotation.y * grad).toFixed(1),
                                 (licht.rotation.z * grad).toFixed(1)], 5)}
            ${Panel.hinweis('Ziehe das Licht-Symbol in der Szene, um Position '
                            + 'und Drehung zu ändern')}
        </div>`;
        this._verdrahten(licht);
    }

    verbergen() {
        Panel.leeren();
        this.symbol = null;
    }

    // ------------------------------------------------------------------ intern

    _verdrahten(licht) {
        this._helligkeit(licht);
        this._farbe(licht);
        this._position(licht);
        this._drehung(licht);
    }

    _helligkeit(licht) {
        const schieber = document.getElementById('light-intensity');
        const anzeige = document.getElementById('light-intensity-wert');
        if (!schieber) return;
        schieber.oninput = (ereignis) => {
            licht.intensity = parseFloat(ereignis.target.value);
            if (anzeige) anzeige.textContent = licht.intensity.toFixed(1);
        };
    }

    _farbe(licht) {
        const waehler = document.getElementById('light-color');
        if (!waehler) return;
        waehler.oninput = (ereignis) => {
            licht.color.setHex(parseInt(ereignis.target.value.substring(1), 16));
            // Das Symbol in der Szene faerbt mit — sonst zeigt es die alte Farbe.
            if (!this.symbol) return;
            this.symbol.children.forEach(kind => {
                if (!kind.material) return;
                kind.material.color.copy(licht.color);
                if (kind.material.emissive) kind.material.emissive.copy(licht.color);
            });
        };
    }

    _position(licht) {
        const felder = Panel.felder('light-pos-x', 'light-pos-y', 'light-pos-z');
        if (!felder) return;
        const setzen = () => {
            licht.position.set(...felder.map(f => parseFloat(f.value)));
            if (!this.symbol) return;
            this.symbol.position.copy(licht.position);
            this.symbol.lookAt(licht.target.position);
        };
        felder.forEach(feld => { feld.oninput = setzen; });
    }

    _drehung(licht) {
        const felder = Panel.felder('light-rot-x', 'light-rot-y', 'light-rot-z');
        if (!felder) return;
        const setzen = () => {
            licht.rotation.set(
                ...felder.map(f => parseFloat(f.value) / Lichtpanel.GRAD));
            if (this.symbol) this.symbol.rotation.copy(licht.rotation);
        };
        felder.forEach(feld => { feld.oninput = setzen; });
    }
}
