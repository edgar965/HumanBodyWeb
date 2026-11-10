/**
 * Fotogenesiszeilenleiste — die Bedienleiste über einer Zeile der Jobseite (04.11.2026, Edgar: „in jeder Zeile ab Zeile 3 diese ansichten plus die Rig, Kleider Toggle buttons“, mit der
 * Leiste der PSHuman-Eingabe als Bild): Ansicht Textur · Normale · Netz · Netz farbig · Netz-Normale (`Fotogenesisansichtsart`), dazu die Schalter „Kleider“ und „Rig“ wie in der festen
 * Leiste oben (`Fotogenesissteuerung`, gemeinsame Knöpfe `Fotogenesisschalterleiste`). Die Zeile folgt dann ihrer Leiste, nicht der oben. Behälter im Template: `[data-zeilenleiste]`.
 */
import { Fotogenesisansichtsart } from './fotogenesisansichtsart.js';
import { Fotogenesisschalterleiste } from './fotogenesisschalterleiste.js';

export class Fotogenesiszeilenleiste extends Fotogenesisschalterleiste {

    /** Die Leiste im Behälter `leiste` — null ohne Behälter. `kleider`, `rig`: ob die Zeile etwas hat, das die Schalter umschalten. */
    static aufbauen(leiste, geaendert, optionen = {}) {
        return leiste ? new Fotogenesiszeilenleiste(leiste, geaendert, optionen) : null;
    }

    constructor(leiste, geaendert, { kleider = true, rig = true } = {}) {
        super(leiste, geaendert);
        this.art = 'textur';
        this.kleider = true;
        this.rig = false;
        this._gruppe('Ansicht', Fotogenesisansichtsart.ARTEN.map(a => ({ wert: a.wert, text: a.text, titel: a.titel })), 'art');
        if (kleider) this._schalter('Kleider', 'kleider', 'Kleider und Haar zeigen (aus: nur der Körper)', 'fa-shirt');
        if (rig) this._schalter('Rig', 'rig', 'Das Skelett der Figur in ihrer Haltung über die Ansicht legen (Knochenpunkte, Farbe nach Gruppe)', 'fa-bone');
    }

    /** Die Ansichtsart, mit der die Zeichner der Zeile ihre Felder füllen (`Fotogenesisansichtsart.modus`). */
    get modus() {
        return Fotogenesisansichtsart.modus(this.art);
    }
}
