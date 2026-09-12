/**
 * Schieber — Schieberegler und Zahlenfeld einer Einstellung gleich halten.
 *
 * Edgar, 12.09.2026: „mach für alle Einstellungen slider". Das Markup kommt
 * aus `templates/effekte/_feld.html`: ein `<input type="range">` mit
 * `data-fuer="<id>"` und das Zahlenfeld mit dieser `id`. Das Zahlenfeld ist
 * der Wert (es trägt `name` und `data-parameter`, `Effektformular.lesen()`
 * liest es); der Regler ist die Hand daran. Tippt jemand ins Zahlenfeld,
 * folgt der Regler — geklemmt auf seinen Bereich, der Tippwert bleibt.
 */
export class Schieber {

    /** Alle Regler unter `wurzel` verdrahten. */
    static verdrahten(wurzel) {
        for (const regler of wurzel.querySelectorAll('.effekt-schieber[data-fuer]')) {
            const feld = wurzel.querySelector('#' + regler.dataset.fuer);
            if (feld) new Schieber(regler, feld);
        }
    }

    constructor(regler, feld) {
        this.regler = regler;
        this.feld = feld;
        regler.addEventListener('input', () => {
            feld.value = regler.value;
            feld.dispatchEvent(new Event('change', { bubbles: true }));
        });
        feld.addEventListener('input', () => this.folgen());
        feld.addEventListener('change', () => this.folgen());
        this.folgen();
    }

    /** Der Regler folgt dem Zahlenfeld. */
    folgen() {
        const wert = parseFloat(this.feld.value);
        if (Number.isNaN(wert)) return;
        this.regler.value = String(Math.min(parseFloat(this.regler.max),
                                            Math.max(parseFloat(this.regler.min), wert)));
    }
}
