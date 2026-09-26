/**
 * Detailbereiche — was in den klappbaren Bereichen Haut, Augen, Augenbrauen,
 * Mund und Nägel des Reiters „Modell" steht (`_szene_details.html`).
 *
 * WARUM EINE TABELLE (Edgar, 12.09.2026: „es fehlen noch die Lippen (farbe
 * usw.). wahrscheinlich fehlen noch viele andere Sachen, schau mal nach und
 * füge alle ein bei den Eigenschaften, schön nach Bereich geordnet"): Jeder
 * Bereich hat Farbfelder, Prozentregler (Längen, Stärke, Glanz) und
 * Morphregler — und einen eigenen Reset. Statt fünf Listen je Sorte steht
 * hier je Bereich, was zu ihm gehört; `Detailbedienung` läuft darüber. Die
 * Kennungen sind der Vertrag mit der Vorlage (`test_szene_details`).
 *
 * Felder heißen wie in `Koerperdetails.VORGABE`; `_laenge`/`_staerke`/
 * `_dicke`/`_dichte` sind Faktoren (Regler 25–300 %), `_glanz` liegt in 0..1
 * (Regler 0–100 %), `_lage` in Metern (Regler in mm, `millimeter`), Morphs
 * in −1..1 (Regler −100..100). Kennung eines Morphreglers:
 * `prop-detail-morph-<Name>`.
 */
export class Detailbereiche {

    /** @type {Record<string, {farben: string[][], prozent: string[][], millimeter?: string[][],
     *                          auswahl?: string[][], morphe: string[]}>} */
    static ALLE = {
        haut: {
            farben: [['prop-detail-haut', 'haut']],
            prozent: [['prop-detail-haut-glanz', 'haut_glanz']],
            auswahl: [['prop-detail-haut-textur', 'haut_textur']],
            morphe: [],
        },
        augen: {
            farben: [['prop-detail-iris', 'iris'], ['prop-detail-sklera', 'sklera'],
                     ['prop-detail-wimpern', 'wimpern']],
            prozent: [['prop-detail-wimpern-laenge', 'wimpern_laenge']],
            morphe: ['Eyelids_SizeZ', 'Eyelids_Crease', 'Eyelids_Angle', 'Eyelids_LowerCurve'],
        },
        brauen: {
            farben: [['prop-detail-brauen', 'brauen']],
            prozent: [['prop-detail-brauen-staerke', 'brauen_staerke'], ['prop-detail-brauen-dicke', 'brauen_dicke'],
                      ['prop-detail-brauen-dichte', 'brauen_dichte'],
                      ['prop-detail-brauen-bogen-laenge', 'brauen_bogen_laenge'],
                      ['prop-detail-brauen-deckkraft', 'brauen_deckkraft']],
            millimeter: [['prop-detail-brauen-lage', 'brauen_lage'],
                         ['prop-detail-brauen-hoehe-innen', 'brauen_hoehe_innen'],
                         ['prop-detail-brauen-hoehe-aussen', 'brauen_hoehe_aussen'],
                         ['prop-detail-brauen-woelbung', 'brauen_woelbung']],
            morphe: ['Eyebrows_PosZ', 'Eyebrows_Angle', 'Eyebrows_Ridge', 'Eyebrows_Droop'],
        },
        mund: {
            farben: [['prop-detail-lippen', 'lippen'], ['prop-detail-zaehne', 'zaehne'],
                     ['prop-detail-zunge', 'zunge']],
            prozent: [['prop-detail-lippen-glanz', 'lippen_glanz']],
            morphe: [],
        },
        naegel: {
            farben: [['prop-detail-naegel-hand', 'naegel_hand'], ['prop-detail-naegel-fuss', 'naegel_fuss']],
            prozent: [['prop-detail-naegel-fuss-laenge', 'naegel_fuss_laenge']],
            morphe: ['Hands_NailsLength'],
        },
    };

    static morphKennung(name) {
        return `prop-detail-morph-${name}`;
    }

    /** Die Bereiche, die gemeint sind: einer oder alle. */
    static bereiche(name = null) {
        return name ? [Detailbereiche.ALLE[name]].filter(Boolean) : Object.values(Detailbereiche.ALLE);
    }

    static farben(name = null) {
        return Detailbereiche.bereiche(name).flatMap(b => b.farben);
    }

    static prozent(name = null) {
        return Detailbereiche.bereiche(name).flatMap(b => b.prozent);
    }

    /** Regler in Millimetern (Feld in Metern). */
    static millimeter(name = null) {
        return Detailbereiche.bereiche(name).flatMap(b => b.millimeter || []);
    }

    /** Auswahlfelder (`<select>`, Wert = Text). */
    static auswahl(name = null) {
        return Detailbereiche.bereiche(name).flatMap(b => b.auswahl || []);
    }

    /** Felder, deren Änderung die Brauen neu baut (alles an den Brauen außer der Farbe). */
    static neubau(feld) {
        return feld === null || feld.startsWith('brauen');
    }

    static morphe(name = null) {
        return Detailbereiche.bereiche(name).flatMap(b => b.morphe);
    }

    /** Alle Detailfelder (Farben, Prozente, Millimeter, Auswahl) eines Bereichs — für den Reset. */
    static felder(name = null) {
        return [...Detailbereiche.farben(name), ...Detailbereiche.prozent(name),
                ...Detailbereiche.millimeter(name), ...Detailbereiche.auswahl(name)].map(([, feld]) => feld);
    }
}
