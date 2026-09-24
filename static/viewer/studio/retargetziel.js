/**
 * Retargetziel — welches Zielskelett der Server für die Figur einer Spur
 * rechnet, und woran ein fertiger Clip erkennt, dass er noch dazu passt.
 *
 * Edgar, 15.09.2026: Modelle im Studio nach Figurart (HumanBody, SMPL,
 * MakeHuman, UMA, UMA Python). Ein Clip ist auf EIN Skelett gebaut — die
 * Spuren nennen die Knochen beim Namen. Wechselt die Figur die Art, stimmen
 * die Namen nicht mehr; deshalb trägt jeder Clip den `schluessel` seines
 * Ziels, und `Bvhspur` holt ihn neu, wenn der der Figur ein anderer ist.
 *
 * Dieselben Ziele wie in der Szene (`scene/eigenanimation.js`,
 * `scene/uma/umaanimation.js`): HumanBody → DEF (ohne Angabe), UMA → `uma`
 * mit der GLB-Datei, SMPL → `smpl` mit dem Körper, MakeHuman → `makehuman`
 * mit Makros und Reglern (POST — 269 Regler passen in keine Adresse), UMA
 * Python → `umapython` mit der Rasse und den DNA-Reglern, Genesis 9 →
 * `genesis9` mit dem Katalognamen und den Daz-Reglern (17.09.2026).
 *
 * Ohne Importe — `test_js_retargetziel` rechnet in Node.
 */
export class Retargetziel {

    static ZIELE = { uma: 'uma', smpl: 'smpl', makehuman: 'makehuman', umapython: 'umapython',
                     genesis9: 'genesis9' };

    /**
     * Die Wahl für den Retarget aus den Feldern der Figur.
     * @param modell  `{quelle, datei, koerper, modell, rasse, makro, regler, dna}`
     *                (die Felder der jeweiligen Modellklasse); null/HumanBody → DEF
     * @param hoehe   Körperhöhe in Metern (0 = Server-Vorgabe)
     * @returns {{target: string|null, figur: string|null, rumpf: Object|null,
     *            hoehe: number, schluessel: string}}
     */
    static wahl(modell, hoehe = 0) {
        const quelle = modell?.quelle || 'modell';
        const target = Retargetziel.ZIELE[quelle] || null;
        if (!target) return { target: null, figur: null, rumpf: null, hoehe: 0, schluessel: 'def' };
        const figur = Retargetziel.figurname(quelle, modell);
        let rumpf = null;
        if (quelle === 'makehuman') rumpf = { makro: modell.makro || null, regler: modell.regler || null };
        if (quelle === 'umapython') rumpf = { makro: null, regler: modell.dna || {} };
        if (quelle === 'genesis9') rumpf = { makro: null, regler: modell.regler || {} };
        const h = Number(hoehe) > 0 ? Number(hoehe) : 0;
        return { target, figur, rumpf, hoehe: h,
                 schluessel: `${target}:${figur}:${h ? h.toFixed(3) : ''}` };
    }

    /** Der Name, unter dem der Server das Skelett dieser Figur nachbaut. */
    static figurname(quelle, modell) {
        if (quelle === 'uma') return modell.datei || '';
        if (quelle === 'smpl') return modell.koerper || 'mean_all';
        if (quelle === 'umapython') return modell.rasse || '';
        if (quelle === 'genesis9') return modell.figur || 'basis';
        return modell.modell || 'basis';
    }

    /** Die Abfrageteile für die Adresse (ohne category/name). */
    static abfrage(wahl) {
        const teile = [];
        if (wahl.target) teile.push('target=' + encodeURIComponent(wahl.target));
        if (wahl.figur) teile.push('figur=' + encodeURIComponent(wahl.figur));
        if (wahl.hoehe) teile.push('body_height=' + wahl.hoehe.toFixed(4));
        return teile.length ? '&' + teile.join('&') : '';
    }
}
