/**
 * Koerperfrage — die Anfrageparameter für Körpertyp, Morphs und Meta-Werte.
 *
 * WARUM (Umbau 16.08.2026): Genau dieser Aufbau stand DREIMAL im Projekt —
 *
 *   * `loadCharacterFromPreset` in asset-loader.js (34 Zeilen),
 *   * `loadGarmentMesh` ebenda (22 Zeilen), jetzt Kleidungsnetz,
 *   * `reloadCharacterMesh` in main.js, jetzt Figurpanel.
 *
 * Alle drei bauen dieselbe Frage für dieselben Endpunkte, und alle drei mussten
 * dieselben Sonderfaelle kennen: Morphs stehen in `morphs` UND in
 * `user_morphs` (Letztere gewinnen), Meta-Werte entweder verschachtelt in
 * `meta` oder flach als `meta_age`. Wer einen Fall vergisst, bekommt eine Figur
 * mit anderen Massen als die Kleidung, die er ihr anzieht.
 */
export class Koerperfrage {

    static VORGABE_KOERPER = 'Female_Caucasian';
    static META_FELDER = ['age', 'mass', 'tone', 'height'];

    /**
     * @param {Object} vorgabe  Vorgabe oder userData mit body_type/bodyType,
     *        morphs, user_morphs, meta
     */
    constructor(vorgabe = {}) {
        this.vorgabe = vorgabe;
    }

    /** Kurzform: Fragezeichenkette aus einer Vorgabe. */
    static text(vorgabe) {
        return new Koerperfrage(vorgabe).felder().toString();
    }

    felder() {
        const frage = new URLSearchParams();
        const koerper = this.vorgabe.body_type || this.vorgabe.bodyType;
        if (koerper) frage.set('body_type', koerper);
        this._morphs(frage);
        this._meta(frage);
        return frage;
    }

    /** `user_morphs` nach `morphs` setzen: gleiche Schluessel gewinnen dort. */
    _morphs(frage) {
        for (const feld of ['morphs', 'user_morphs']) {
            const werte = this.vorgabe[feld];
            if (!werte || typeof werte !== 'object') continue;
            for (const [name, wert] of Object.entries(werte)) {
                if (wert !== undefined && wert !== null) {
                    frage.set('morph_' + name, String(wert));
                }
            }
        }
    }

    _meta(frage) {
        const meta = this.vorgabe.meta || {};
        for (const name of Koerperfrage.META_FELDER) {
            const wert = meta[name] ?? this.vorgabe['meta_' + name];
            if (wert !== undefined && wert !== null) {
                frage.set('meta_' + name, String(wert));
            }
        }
    }

    /** Die Morph-Werte zusammengefasst — fuer userData nach dem Laden. */
    static morphs(vorgabe) {
        return { ...(vorgabe.morphs || {}), ...(vorgabe.user_morphs || {}) };
    }
}
