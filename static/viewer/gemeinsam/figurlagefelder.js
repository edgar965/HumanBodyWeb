/**
 * Figurlagefelder — „Position X" und „Größe angleichen" im Figurwahl-Dialog.
 *
 * Herausgelöst aus `figurwahldialog.js` (11.09.2026), als der Dialog eine
 * zweite Aufgabe ohne Lage bekam (Modell austauschen). Die Felder gehören
 * zur Wahl, nicht zum Austausch — also ein eigener Baustein, den der Dialog
 * einhängt oder weglässt.
 *
 * Die Vorgabe der Szene-Seite: `ABSTAND_M` rechts neben der vorhandenen
 * Figur, Größe angeglichen. Der Aufrufer liefert über `vorgaben()` die
 * echte Lage — ohne Angabe gilt diese Vorgabe.
 *
 * `angleichen: false` lässt das Kästchen weg (BVH Studio, 11.09.2026): Dort
 * bestimmt die Bewegung die Größe der Figur, ein Kästchen ohne Wirkung wäre
 * eine Behauptung. `lage()` liefert dann die Vorgabe des Aufrufers.
 */
export class Figurlagefelder {

    /** Vorgabe der Szene-Seite: 1,5 m rechts neben der vorhandenen Figur. */
    static ABSTAND_M = 1.5;

    /**
     * @param {string} kennung   Präfix der IDs (die des Dialogs)
     * @param {Function} vorgaben  () => ({x, angleichen, vorbildHoehe})
     * @param {Object} wahl      { angleichen: false } = ohne das Kästchen
     */
    constructor(kennung, vorgaben = null, { angleichen = true } = {}) {
        this.kennung = kennung;
        this.vorgaben = vorgaben || Figurlagefelder.vorgabe;
        this.mitAngleichen = angleichen;
        this.wurzel = null;
    }

    static vorgabe() {
        return { x: Figurlagefelder.ABSTAND_M, angleichen: true, vorbildHoehe: 0 };
    }

    html() {
        const k = this.kennung;
        const kaestchen = this.mitAngleichen ? `
                <label class="ankreuz" for="${k}-angleichen">
                    <input type="checkbox" id="${k}-angleichen" checked>
                    Größe der vorhandenen Figur angleichen
                </label>` : '';
        return `
            <div class="dialogfelder" id="${k}-lage">
                <label for="${k}-x">Position X</label>
                <input type="number" id="${k}-x" step="0.1" value="${Figurlagefelder.ABSTAND_M}">
                <span class="einheit">m</span>${kaestchen}
            </div>`;
    }

    /** Nach dem Einhängen: das Element, in dem die Felder stehen. */
    anbinden(wurzel) {
        this.wurzel = wurzel;
        return this;
    }

    /** Felder mit der Vorgabe des Aufrufers füllen (beim Öffnen). */
    vorbelegen() {
        const vorgabe = this.vorgaben();
        const x = this._feld('x');
        const angleichen = this._feld('angleichen');
        if (x) x.value = vorgabe.x;
        if (angleichen) {
            angleichen.checked = vorgabe.angleichen;
            // Ohne Vorbild gibt es nichts anzugleichen.
            angleichen.disabled = !vorgabe.angleichen;
        }
    }

    /** Die Lage, wie sie jetzt in den Feldern steht. */
    lage() {
        const vorgabe = this.vorgaben();
        const x = this._feld('x');
        const angleichen = this._feld('angleichen');
        return {
            x: x ? Number(x.value) : vorgabe.x,
            angleichen: angleichen ? angleichen.checked : vorgabe.angleichen,
            vorbildHoehe: vorgabe.vorbildHoehe,
        };
    }

    _feld(name) {
        return this.wurzel?.querySelector(`#${this.kennung}-${name}`) || null;
    }
}
