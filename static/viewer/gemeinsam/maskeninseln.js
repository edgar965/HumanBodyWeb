/**
 * Maskeninseln — freie Inseln in einer Punktmaske schließen.
 *
 * Aus `hautmaske.js` abgeteilt (11.09.2026, Dateigrenze). Ohne Three.js,
 * ohne DOM; geprüft über `test_js_hautmaske.py` (Fall 6).
 */
export class Maskeninseln {

    /**
     * Freie Inseln im Verdeckten schließen: zusammenhängende Gruppen
     * unverdeckter Punkte, die nur an verdeckte grenzen und höchstens
     * `hoechstens` Punkte haben, gelten als verdeckt.
     *
     * WARUM (11.09.2026, lockeres T-Shirt, Arm gesenkt): In der Achselfalte
     * zeigt die Hautnormale in den Arm; der Strahl trifft dort keinen Stoff,
     * drei Punkte blieben frei, und die 17 Dreiecke um sie herum standen als
     * weißer Splitter aus dem T-Shirt. Eine Insel, die ringsum von
     * verdeckter Haut umgeben ist, liegt unter dem Stoff — sonst wäre sie
     * mit der freien Haut verbunden. 200 Punkte sind bei 70.851 Punkten
     * etwa 2 × 2 cm; ein echter Ausschnitt (Rückenfenster) ist größer.
     */
    static schliessen(maske, dreiecke, hoechstens) {
        const n = maske.length;
        const wurzel = new Int32Array(n);
        for (let i = 0; i < n; i++) wurzel[i] = i;
        const finde = (i) => { while (wurzel[i] !== i) { wurzel[i] = wurzel[wurzel[i]]; i = wurzel[i]; } return i; };
        const vereine = (a, b) => { const ra = finde(a), rb = finde(b); if (ra !== rb) wurzel[ra] = rb; };
        for (let k = 0; k + 2 < dreiecke.length; k += 3) {
            const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
            if (!maske[a] && !maske[b]) vereine(a, b);
            if (!maske[b] && !maske[c]) vereine(b, c);
            if (!maske[c] && !maske[a]) vereine(c, a);
        }
        const groesse = new Map();
        for (let i = 0; i < n; i++) if (!maske[i]) { const r = finde(i); groesse.set(r, (groesse.get(r) || 0) + 1); }
        // Die größte Gruppe ist die freie Haut selbst — nie eine Insel.
        let groesste = 0;
        for (const g of groesse.values()) if (g > groesste) groesste = g;
        let geschlossen = 0;
        for (let i = 0; i < n; i++) {
            if (maske[i]) continue;
            const g = groesse.get(finde(i));
            if (g <= hoechstens && g < groesste) { maske[i] = 1; geschlossen += 1; }
        }
        return geschlossen;
    }
}
