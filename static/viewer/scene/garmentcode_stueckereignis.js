/**
 * Stueckereignis — sagt am Dokument, wenn ein GarmentCode-Stück kommt oder
 * geht.
 *
 * WARUM (11.09.2026): Wer wissen will, was eine Figur trägt, sah bis dahin
 * im Takt in `inst.clothMeshes` nach — das Einhängen löste kein Ereignis
 * aus. Ein Absatzschuh ändert aber die Pose der Figur, und die soll
 * genau dann neu geholt werden, wenn er angezogen oder abgelegt wird
 * (`garmentcode_absatz.js`). `GarmentcodeAnziehen.einhaengen` und
 * `entfernen` melden hier; eigenes Modul, weil `garmentcode_anziehen.js`
 * schon über der Zeilengrenze liegt.
 */
export class Stueckereignis {

    static NAME = 'gc-stueck';

    /** `detail`: `{inst, stueck, angezogen}`. */
    static melden(figur, stueck, angezogen) {
        document.dispatchEvent(new CustomEvent(Stueckereignis.NAME, {
            detail: { inst: figur, stueck, angezogen },
        }));
    }

    static hoeren(zuhoerer) {
        document.addEventListener(Stueckereignis.NAME, (e) => zuhoerer(e.detail || {}));
    }
}
