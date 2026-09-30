/**
 * Sortenanteile — die Aufteilung von „Haar – Generisch" nach einem Reglerzug.
 *
 * Edgar, 30.09.2026: „wenn ich einen anteil eines neuen haares hinzumische, soll der
 * anteil der anderen proportional sinken, so dass die Summe aller Anteile immer 100% ist".
 *
 * Der gezogene Regler bekommt seinen Wert; der Rest (1 − Wert) wird auf die ANDEREN
 * verteilt, im Verhältnis ihrer bisherigen Anteile. Kin 100 % → Toulouse auf 30 % → Kin
 * 70 %. Pixie dazu auf 20 % → Kin 56 %, Toulouse 24 % (Verhältnis 70 : 30 bleibt). Pixie
 * zurück auf 0 → Kin 70 %, Toulouse 30 % — das alte Verhältnis kehrt zurück, weil nur
 * skaliert wird, nie umverteilt.
 *
 * DIE EINZIGE SORTE BLEIBT BEI 100 %. Steht nur eine Sorte über 0 und wird sie
 * heruntergezogen, gibt es niemanden, der den Rest aufnehmen könnte. Die Summe muss 100 %
 * sein — also springt der Regler zurück. Wer mischen will, zieht eine ANDERE Sorte hoch.
 *
 * Ohne DOM und ohne Three: Die Rechnung läuft so auch im Node-Test
 * (`test_js_sortenanteile.py`); das Setzen der Schieber macht `Genesis9stueckregler`.
 */
export class Sortenanteile {

    static VORSATZ = 'sorte.';

    /** Ist das ein Sortenregler (Anteil einer Frisur)? */
    static ist(name) {
        return String(name || '').startsWith(Sortenanteile.VORSATZ);
    }

    /**
     * Die neue Aufteilung.
     * @param {Object<string, number>} aktuell Wert JEDES Sortenreglers (auch der auf Vorgabe)
     * @param {string} name der gezogene Regler
     * @param {number} wert sein neuer Wert (0…1)
     * @returns {Object<string, number>} alle Sortenregler, Summe 1
     */
    static ziehen(aktuell, name, wert) {
        const gezogen = Math.min(1, Math.max(0, Number(wert) || 0));
        const andere = Object.keys(aktuell).filter(k => k !== name);
        const summe = andere.reduce((s, k) => s + Math.max(0, Number(aktuell[k]) || 0), 0);
        const aus = {};
        if (summe <= 1e-9) {
            for (const k of andere) aus[k] = 0;
            aus[name] = 1;
            return aus;
        }
        const rest = 1 - gezogen;
        for (const k of andere) aus[k] = Math.max(0, Number(aktuell[k]) || 0) * rest / summe;
        aus[name] = gezogen;
        return aus;
    }

    /**
     * Die Werte, die in `inst.kleidung[…].regler` gehören: nur die, die von ihrer Vorgabe
     * abweichen — wie bei jedem anderen Regler (`Genesis9stueckregler`).
     *
     * Die Grundsorte hat die Vorgabe 1,0. Steht sie nach einem Zug auf 70 %, MUSS der Wert
     * mit: Fehlte er, nähme der Server wieder 1,0 an, und aus 70 : 30 würde 100 : 30.
     */
    static eintragen(regler, aufteilung, vorgaben) {
        for (const [name, wert] of Object.entries(aufteilung)) {
            const vorgabe = vorgaben[name] ?? 0;
            if (Math.abs(wert - vorgabe) < 1e-6) delete regler[name];
            else regler[name] = wert;
        }
        return regler;
    }
}
