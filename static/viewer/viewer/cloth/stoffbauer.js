/**
 * Stoffbauer — die Bereiche „Bauer" und „Grundformen" der Kleidungs-Erzeugung.
 *
 * Aus viewer/cloth.js herausgeloest (Umbau 16.08.2026), zusammen mit
 * Stoffvorlagen. Beide Bereiche folgen demselben Muster: Auswahlfeld aus der
 * Serverantwort fuellen, Regler binden, Erzeugen-Knopf verdrahten — dreimal
 * ausgeschrieben (Vorlagen, Bauer, Grundformen).
 */
export class Stoffbauer {

    static VORGABE_BEREICH = 'TOP';
    static VORGABE_FORM = 'PRIM_SKIRT';
    /** Nur der Rock hat einen Weite-Regler. */
    static MIT_WEITE = 'PRIM_SKIRT';

    /**
     * @param {Object} daten    Antwort von /api/character/cloth/regions/
     * @param {Object} dienste  { reglerBinden, reglerWert, stoffLaden }
     */
    constructor(daten, dienste) {
        this.daten = daten;
        this.dienste = dienste;
        this.bereichsfeld = document.getElementById('cloth-bld-region');
        this.formfeld = document.getElementById('cloth-prim-type');
    }

    verdrahten() {
        this._bauer();
        this._grundformen();
        return this;
    }

    /** Auswahlfeld aus einer Liste mit key/label füllen. */
    _fuellen(feld, eintraege) {
        if (!feld) return;
        for (const eintrag of (eintraege || [])) {
            feld.appendChild(new Option(eintrag.label, eintrag.key));
        }
    }

    // ------------------------------------------------------------------- Bauer

    _bauer() {
        this._fuellen(this.bereichsfeld, this.daten.builder_regions);
        this.dienste.reglerBinden('cloth-bld-looseness', 'cloth-bld-looseness-val',
                                  wert => (wert / 100).toFixed(2));
        document.getElementById('cloth-bld-create')?.addEventListener('click', () => {
            const bereich = this.bereichsfeld ? this.bereichsfeld.value
                                              : Stoffbauer.VORGABE_BEREICH;
            this.dienste.stoffLaden(`bld_${bereich}`, {
                method: 'builder',
                region: bereich,
                looseness: this.dienste.reglerWert('cloth-bld-looseness') / 100,
            });
        });
    }

    // ------------------------------------------------------------- Grundformen

    _grundformen() {
        this._fuellen(this.formfeld, this.daten.primitives);
        if (this.formfeld) {
            this.formfeld.addEventListener('change', () => this._weiteZeigen());
            this._weiteZeigen();
        }
        for (const [feldId, form] of [
                ['cloth-prim-segments', wert => String(wert)],
                ['cloth-prim-length', wert => (wert / 100).toFixed(2)],
                ['cloth-prim-flare', wert => (wert / 100).toFixed(2)]]) {
            this.dienste.reglerBinden(feldId, feldId + '-val', form);
        }
        document.getElementById('cloth-prim-create')?.addEventListener('click', () => {
            const art = this.formfeld ? this.formfeld.value : Stoffbauer.VORGABE_FORM;
            this.dienste.stoffLaden(`prim_${art}`, {
                method: 'primitive',
                prim_type: art,
                segments: this.dienste.reglerWert('cloth-prim-segments'),
                length: this.dienste.reglerWert('cloth-prim-length') / 100,
                flare: this.dienste.reglerWert('cloth-prim-flare') / 100,
            });
        });
    }

    /** Der Weite-Regler gilt nur für den Rock. */
    _weiteZeigen() {
        const zeile = document.getElementById('cloth-prim-flare-row');
        if (!zeile || !this.formfeld) return;
        zeile.style.display =
            this.formfeld.value === Stoffbauer.MIT_WEITE ? 'flex' : 'none';
    }
}
