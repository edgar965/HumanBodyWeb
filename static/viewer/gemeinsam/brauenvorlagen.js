/**
 * Brauenvorlagen — fertige Reglersätze für die gezeichnete Braue.
 *
 * Eine Vorlage setzt nur Werte der Detailfelder (`Koerperdetails`, mm-Werte
 * in Metern); gezeichnet wird immer über dieselbe Karte (`Brauenhaut`). Was
 * eine Vorlage nicht nennt, bleibt auf der Vorgabe — „Vorgabe" selbst setzt
 * alles zurück. Ohne Importe (Node-Test `test_js_brauenhaut.py`).
 */
export class Brauenvorlagen {

    static FELDER = ['brauen_staerke', 'brauen_dicke', 'brauen_dichte', 'brauen_bogen_laenge',
                     'brauen_deckkraft', 'brauen_lage', 'brauen_hoehe_innen',
                     'brauen_hoehe_aussen', 'brauen_woelbung'];

    /** @type {Array<[string, string, Object]>} Kennung, Beschriftung, Werte */
    static ALLE = [
        ['', 'Vorgabe', {}],
        ['gerade', 'Gerade', { brauen_woelbung: -0.003, brauen_hoehe_aussen: 0.002 }],
        ['geschwungen', 'Geschwungen', { brauen_woelbung: 0.004, brauen_hoehe_aussen: -0.003,
                                         brauen_bogen_laenge: 1.1 }],
        ['duenn', 'Dünn', { brauen_dicke: 0.6, brauen_dichte: 0.7, brauen_staerke: 0.8 }],
        ['buschig', 'Buschig', { brauen_dicke: 1.5, brauen_dichte: 1.6, brauen_staerke: 1.25 }],
        ['maennlich', 'Männlich', { brauen_dicke: 1.4, brauen_dichte: 1.4, brauen_woelbung: -0.002,
                                    brauen_hoehe_innen: -0.002 }],
    ];

    /** Die Werte einer Vorlage über `details` gelegt (Vorgaben für alles andere). */
    static anwenden(details, kennung, vorgabe) {
        const werte = Brauenvorlagen.ALLE.find(([k]) => k === kennung)?.[2] || {};
        const aus = { ...details };
        for (const feld of Brauenvorlagen.FELDER) aus[feld] = feld in werte ? werte[feld] : vorgabe[feld];
        return aus;
    }

    /** Welche Vorlage die Details gerade treffen — '' wenn keine (eigene Werte). */
    static erkennen(details, vorgabe) {
        for (const [kennung] of Brauenvorlagen.ALLE) {
            const soll = Brauenvorlagen.anwenden({}, kennung, vorgabe);
            if (Brauenvorlagen.FELDER.every(f => Math.abs((details?.[f] ?? vorgabe[f]) - soll[f]) < 1e-6)) {
                return kennung;
            }
        }
        return null;
    }
}
