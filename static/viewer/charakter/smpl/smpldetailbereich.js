import { Detailbedienung } from '../detailbedienung.js';

/**
 * Smpldetailbereich — der Bereich Augen · Brauen · Mund · Nägel auch für SMPL-X.
 *
 * WARUM (Edgar, 25.09.2026: „mach auch Augen/Augenbrauen/Mund/Nägel"): Der
 * Bereich (`_szene_details.html`, `Detailbedienung`) ist derselbe wie bei
 * HumanBody — dieselben Felder, dieselben Regler. Verborgen wird, was an
 * HumanBody-Morphs oder -Materialgruppen hängt und bei SMPL-X nichts hätte:
 * die Form-Morphs (Lider, Brauenform, Fingernagellänge), die Fußnagellänge
 * (Punktstreckung der Nagelstücke) und „Haut" (SMPL-X hat einen eigenen
 * Hautbereich mit Fototextur). Verborgen wird nur, was HIER verborgen wurde
 * (`data-smpl-verborgen`), wie `Eigenschaftenbereiche.genesis9Garderobe`.
 */
export class Smpldetailbereich {

    static BEREICH = 'prop-details-section';

    /** Was bei SMPL-X nichts bewirkt (Kennungen bzw. Präfixe von Regler-Kennungen). */
    static NUR_HUMANBODY = ['prop-details-haut', 'prop-detail-naegel-fuss-laenge'];
    static MORPH_PRAEFIX = 'prop-detail-morph-';

    static zeigen(inst) {
        const bereich = document.getElementById(Smpldetailbereich.BEREICH);
        if (!bereich) return;
        bereich.classList.remove('hb-versteckt');
        for (const element of Smpldetailbereich._elemente(bereich)) {
            if (element.classList.contains('hb-versteckt')) continue;
            element.classList.add('hb-versteckt');
            element.dataset.smplVerborgen = '1';
        }
        Detailbedienung.fuellen(inst, null);
    }

    static verbergen() {
        const bereich = document.getElementById(Smpldetailbereich.BEREICH);
        if (!bereich) return;
        for (const element of bereich.querySelectorAll('[data-smpl-verborgen]')) {
            element.classList.remove('hb-versteckt');
            delete element.dataset.smplVerborgen;
        }
    }

    /** Die Zeilen und Unterüberschriften, die bei SMPL-X nicht gelten. */
    static _elemente(bereich) {
        const aus = [];
        for (const kennung of Smpldetailbereich.NUR_HUMANBODY) {
            const element = document.getElementById(kennung);
            if (element) aus.push(element.closest('.slider-row') || element);
        }
        for (const regler of bereich.querySelectorAll(`[id^="${Smpldetailbereich.MORPH_PRAEFIX}"]`)) {
            if (regler.id.endsWith('-val')) continue;
            const zeile = regler.closest('.slider-row');
            if (zeile) aus.push(zeile);
        }
        for (const titel of bereich.querySelectorAll('.unterabschnittstitel')) aus.push(titel);
        return [...new Set(aus)];
    }
}
