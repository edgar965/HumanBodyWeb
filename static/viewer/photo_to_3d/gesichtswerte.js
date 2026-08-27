/**
 * Die zehn Ausdruckswerte, die SMPL-X je Bild liefert — benannt und begrenzt.
 *
 * Der Rohvektor kommt als Feld ohne Namen aus dem Netz; wer ihn per Index liest,
 * hat den Fehler eine Umstellung später im Gesicht. Hier steht die Reihenfolge
 * einmal.
 *
 * Aus facial_expression.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`: `applyFacialExpression()` hatte 102 Zeilen).
 */
export class Gesichtswerte {
    /** Reihenfolge im Vektor `smplxExpr`. */
    static NAMEN = ['jawOpen', 'smile', 'browUp', 'browDown', 'lipUp',
                    'lipCorner', 'cheekPuff', 'squint', 'noseWrinkle',
                    'eyeWide'];

    /** Der Kiefer öffnet nur nach unten, die übrigen Werte gehen in beide Richtungen. */
    static GRENZEN = { jawOpen: [0, 1.5] };
    static GRENZE_SONST = [-1.5, 1.5];

    /** Drehung je Ausdruckseinheit im Bogenmaß — dezent über den Morphs. */
    static SCHRITT = 0.03;

    /** @param {number[]} vektor die zehn Rohwerte */
    constructor(vektor) {
        for (let i = 0; i < Gesichtswerte.NAMEN.length; i++) {
            const name = Gesichtswerte.NAMEN[i];
            const [unten, oben] = Gesichtswerte.GRENZEN[name]
                                  || Gesichtswerte.GRENZE_SONST;
            this[name] = Math.max(unten, Math.min(oben, (vektor || [])[i] || 0));
        }
    }

    /** Brauen: Heben minus Senken, schon mit dem Schritt multipliziert. */
    get brauen() {
        return (this.browUp - this.browDown) * Gesichtswerte.SCHRITT;
    }

    /** Oberlid — Zusammenkneifen schließt, Aufreißen öffnet. */
    get oberlid() {
        return (this.squint - this.eyeWide) * Gesichtswerte.SCHRITT;
    }

    /** Unterlid — genau andersherum. */
    get unterlid() {
        return (-this.squint + this.eyeWide) * Gesichtswerte.SCHRITT;
    }

    /** Ein Rohwert mit dem Schritt multipliziert. */
    mal(name) {
        return this[name] * Gesichtswerte.SCHRITT;
    }

    /** Für das Protokoll. */
    alsObjekt() {
        const werte = {};
        for (const name of Gesichtswerte.NAMEN) werte[name] = this[name];
        return werte;
    }
}
