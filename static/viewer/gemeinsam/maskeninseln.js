/**
 * Maskeninseln — freie Inseln in einer Punktmaske schließen.
 *
 * Aus `hautmaske.js` abgeteilt (11.09.2026, Dateigrenze). Ohne Three.js,
 * ohne DOM; geprüft über `test_js_hautmaske.py` (Fall 6 und 7).
 */
export class Maskeninseln {

    /**
     * Freie Inseln im Verdeckten schließen: zusammenhängende Gruppen
     * unverdeckter Punkte, die AN VERDECKTE GRENZEN und höchstens
     * `hoechstens` Punkte haben, gelten als verdeckt.
     *
     * WARUM (11.09.2026, lockeres T-Shirt, Arm gesenkt): In der Achselfalte
     * zeigt die Hautnormale in den Arm; der Strahl trifft dort keinen Stoff,
     * drei Punkte blieben frei, und die 17 Dreiecke um sie herum standen als
     * weißer Splitter aus dem T-Shirt. Eine Insel, die ringsum von
     * verdeckter Haut umgeben ist, liegt unter dem Stoff — sonst wäre sie
     * mit der freien Haut verbunden. 200 Punkte sind bei 70.851 Punkten
     * etwa 2 × 2 cm; ein echter Ausschnitt (Rückenfenster) ist größer.
     *
     * NUR WAS AN VERDECKTES GRENZT (12.09.2026, Edgar: „die
     * Wimperneinstellung funktioniert nicht"): Die erste Fassung schloss
     * JEDE kleine Gruppe außer der größten. Die 136 Wimpernstreifen des
     * HumanBody-Netzes (je 27 Ecken) hängen an keiner Haut — eigene Stücke,
     * 18 cm vom nächsten Stoff — und waren mit T-Shirt und Hose an der Figur
     * alle 3.672 Ecken „verdeckt": Gruppe 2 im Index leer, keine Wimpern
     * mehr am Gesicht, und kein Regler dafür konnte etwas zeigen. Eine
     * Insel im Sinne der Achselfalte hat eine Küste aus verdeckten Punkten;
     * ein Stück ohne jede solche Kante ist keine Insel, sondern ein Teil
     * für sich (Wimpern, Zähne, Zunge, Augäpfel).
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
        // Die Küste: freie Gruppen, die über eine Kante an Verdecktes stoßen.
        const kueste = new Set();
        for (let k = 0; k + 2 < dreiecke.length; k += 3) {
            const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
            if (maske[a] !== maske[b]) kueste.add(finde(maske[a] ? b : a));
            if (maske[b] !== maske[c]) kueste.add(finde(maske[b] ? c : b));
            if (maske[c] !== maske[a]) kueste.add(finde(maske[c] ? a : c));
        }
        const groesse = new Map();
        for (let i = 0; i < n; i++) if (!maske[i]) { const r = finde(i); groesse.set(r, (groesse.get(r) || 0) + 1); }
        // Die größte Gruppe ist die freie Haut selbst — nie eine Insel.
        let groesste = 0;
        for (const g of groesse.values()) if (g > groesste) groesste = g;
        let geschlossen = 0;
        for (let i = 0; i < n; i++) {
            if (maske[i]) continue;
            const r = finde(i);
            const g = groesse.get(r);
            if (g <= hoechstens && g < groesste && kueste.has(r)) { maske[i] = 1; geschlossen += 1; }
        }
        return geschlossen;
    }
}
