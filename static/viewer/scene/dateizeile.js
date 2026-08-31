/**
 * Eine Zeile der Dateiliste im Lade-Dialog.
 *
 * ANLASS (31.08.2026): Der Zeilenaufbau stand als EIN Ausdruck mit 226
 * Zeichen im Rumpf von `openLoadDialog` — drei Zellen, zwei
 * Fallunterscheidungen und eine Maskierung hintereinander. Eine lange Zeile
 * versteckt genau das: Wer den Datumsteil ändern will, liest erst den
 * halben Ausdruck.
 *
 * Die Klasse baut dieselben drei Zellen, aber je Zelle eine Methode. Was
 * hier steht, ist Anzeige — die Auswahl-Logik bleibt im Dialog.
 */
import { escapeHtml } from './utils.js';

export class Dateizeile {
    /**
     * @param {object} datei Eintrag aus `/api/character/model-files/`
     *   mit `type`, `label`/`name` und `modified` (Sekunden seit 1970).
     */
    constructor(datei) {
        this.datei = datei;
        this.istSzene = datei.type === 'scene';
    }

    /** @returns {string} die drei `<td>` einer Zeile */
    html() {
        return this._name() + this._art() + this._datum();
    }

    /** Name mit Symbol — Film für eine Szene, Person für ein Modell. */
    _name() {
        const symbol = this.istSzene ? 'fa-film' : 'fa-user';
        const text = escapeHtml(this.datei.label || this.datei.name);
        return `<td class="dateizelle">`
            + `<i class="fas ${symbol} dateisymbol"></i>${text}</td>`;
    }

    /** Die Art als Abzeichen. */
    _art() {
        const klasse = this.istSzene ? 'file-type-scene' : 'file-type-model';
        const wort = this.istSzene ? 'Szene' : 'Modell';
        return `<td class="dateizelle mittig">`
            + `<span class="${klasse}">${wort}</span></td>`;
    }

    /**
     * Datum in deutscher Schreibweise — leer, wenn die Datei keines mitbringt.
     * `modified` zählt Sekunden, `Date` erwartet Millisekunden.
     */
    _datum() {
        const roh = this.datei.modified;
        const text = roh
            ? new Date(roh * 1000).toLocaleDateString('de-DE')
            : '';
        return `<td class="dateizelle datumszelle">${text}</td>`;
    }
}
