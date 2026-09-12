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
 * Felder heißen wie in `Koerperdetails.VORGABE`; `_laenge`/`_staerke` sind
 * Faktoren (Regler 50–300 %), `_glanz` liegt in 0..1 (Regler 0–100 %),
 * Morphs in −1..1 (Regler −100..100). Kennung eines Morphreglers:
 * `prop-detail-morph-<Name>`.
 */
export class Detailbereiche {

    /** @type {Record<string, {farben: string[][], prozent: string[][], morphe: string[]}>} */
    static ALLE = {
        haut: {
            farben: [['prop-detail-haut', 'haut']],
            prozent: [['prop-detail-haut-glanz', 'haut_glanz']],
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
            prozent: [['prop-detail-brauen-staerke', 'brauen_staerke']],
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

    static morphe(name = null) {
        return Detailbereiche.bereiche(name).flatMap(b => b.morphe);
    }

    /** Alle Detailfelder (Farben und Prozente) eines Bereichs — für den Reset. */
    static felder(name = null) {
        return [...Detailbereiche.farben(name), ...Detailbereiche.prozent(name)].map(([, feld]) => feld);
    }
}
