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
     *
     * PUNKTE GLEICHER LAGE SIND EIN PUNKT (13.09.2026, Nähte): Der Server
     * trennt Nahtpunkte für die Textur in Kopien (`Nahtteilung`), die im
     * Index nicht mehr verbunden sind — der Censor wäre so eine eigene
     * Insel von 173 Punkten und am Bikinirand „geschlossen". Mit `koerper`
     * (Punktlagen) werden Kopien zuerst mit ihrem Original vereint.
     *
     * AUCH NACH FLÄCHE (24.09.2026, Edgar mit Bild: Arabesque Bild 134, Haut
     * unter der rechten Achsel durch das G9 Base Shirt): Die Punktgrenze ist
     * an HumanBody (70.851 Punkte) bemessen. Genesis 9 ist in der Achsel viel
     * feiner — dort war die freie Insel unter dem Ärmel 298 Punkte groß, aber
     * nur 38 cm², blieb offen und kam beim Armheben durch den Stoff. Mit
     * `flaecheMax` (m², braucht `koerper`) wird eine Insel auch geschlossen,
     * wenn ihre freien Dreiecke zusammen höchstens so groß sind.
     */
    static schliessen(maske, dreiecke, hoechstens, koerper = null, flaecheMax = 0) {
        const n = maske.length;
        const wurzel = new Int32Array(n);
        for (let i = 0; i < n; i++) wurzel[i] = i;
        const finde = (i) => { while (wurzel[i] !== i) { wurzel[i] = wurzel[wurzel[i]]; i = wurzel[i]; } return i; };
        const vereine = (a, b) => { const ra = finde(a), rb = finde(b); if (ra !== rb) wurzel[ra] = rb; };
        if (koerper) Maskeninseln.gleicheLage(koerper, n, (a, b) => { if (maske[a] === maske[b]) vereine(a, b); });
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
        const flaeche = (koerper && flaecheMax > 0) ? Maskeninseln.flaechen(koerper, dreiecke, maske, finde) : null;
        let geschlossen = 0;
        for (let i = 0; i < n; i++) {
            if (maske[i]) continue;
            const r = finde(i);
            const g = groesse.get(r);
            const klein = g <= hoechstens || (flaeche !== null && (flaeche.get(r) || 0) <= flaecheMax);
            if (klein && g < groesste && kueste.has(r)) { maske[i] = 1; geschlossen += 1; }
        }
        return geschlossen;
    }

    /** Je freier Gruppe (Wurzel) die Fläche ihrer ganz freien Dreiecke (m²). */
    static flaechen(koerper, dreiecke, maske, finde) {
        const aus = new Map();
        const P = koerper;
        for (let k = 0; k + 2 < dreiecke.length; k += 3) {
            const a = dreiecke[k], b = dreiecke[k + 1], c = dreiecke[k + 2];
            if (maske[a] || maske[b] || maske[c]) continue;
            const ux = P[3 * b] - P[3 * a], uy = P[3 * b + 1] - P[3 * a + 1], uz = P[3 * b + 2] - P[3 * a + 2];
            const vx = P[3 * c] - P[3 * a], vy = P[3 * c + 1] - P[3 * a + 1], vz = P[3 * c + 2] - P[3 * a + 2];
            const x = uy * vz - uz * vy, y = uz * vx - ux * vz, z = ux * vy - uy * vx;
            const r = finde(a);
            aus.set(r, (aus.get(r) || 0) + Math.sqrt(x * x + y * y + z * z) / 2);
        }
        return aus;
    }

    /**
     * Paare von Punkten mit bitgleicher Lage an `paar(a, b)` melden.
     * Zahlenschlüssel aus den Float-Bits statt Zeichenketten — bei 74.000
     * Punkten sind Zeichenketten der teuerste Teil (`kodierung.js`).
     */
    static gleicheLage(koerper, n, paar) {
        const bits = new Uint32Array(koerper.buffer, koerper.byteOffset, n * 3);
        const erste = new Map();
        for (let i = 0; i < n; i++) {
            const schluessel = ((bits[3 * i] * 31 + bits[3 * i + 1]) * 31 + bits[3 * i + 2]) >>> 0;
            const kandidaten = erste.get(schluessel);
            if (!kandidaten) { erste.set(schluessel, [i]); continue; }
            let gefunden = false;
            for (const j of kandidaten) {
                if (bits[3 * j] === bits[3 * i] && bits[3 * j + 1] === bits[3 * i + 1]
                    && bits[3 * j + 2] === bits[3 * i + 2]) { paar(i, j); gefunden = true; break; }
            }
            if (!gefunden) kandidaten.push(i);
        }
    }
}
