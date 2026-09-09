import { GarmentcodeBauregler } from './garmentcode_bauregler.js';

/**
 * Was die Figur nach einem Bau wirklich trägt — als Text.
 *
 * WARUM EIGENES MODUL (08.09.2026): Edgar: „mach die vielen Texte aus dem
 * Garment Code weg … «Fertig: 11878 Punkte, 23629 Dreiecke in 21.2 s, 12 mm
 * zur Haut, 113 Punkte aus der Haut geholt, aber unbeweglich»". Die Zeile war
 * vollständig und unlesbar. Jetzt gibt es zwei: eine kurze für den Reiter und
 * die ausführliche als Tooltip.
 *
 * Die Zahlen bleiben, weil der Hautabstand die einzige Größe ist, die „liegt
 * an" BELEGT — auf dem falschen Körper lag er bei 27 mm Median mit 31 % der
 * Punkte über 5 cm, auf der Figur bei 13 mm. Verschwiegen wäre er ein Fehler,
 * der beim nächsten Mal wieder eine Stunde kostet.
 *
 * `garmentcode_drapieren.js` lag bei 156 Zeilen und wäre mit den zwei
 * Fassungen auf 204 gewachsen — der angefasste Teil wird abgeteilt
 * (`~/.claude/rules/struktur.md`).
 */
export class GarmentcodeBilanz {

    /**
     * Ab hier sitzt ein Stück nicht mehr — dann sagt es die Meldung.
     *
     * 40 mm, nicht enger: Eine weite Hose kommt auf 21 mm und ist völlig
     * in Ordnung (06.09.2026 gemessen, Bundweite 1,0 und Ausstellung 1,0);
     * mit einer engeren Schwelle liest sich jeder weite Schnitt wie ein
     * Fehler. Auf dem falschen Körper lag der Wert bei 27 mm MEDIAN mit
     * 31 % der Punkte über 50 mm — das trifft diese Schwelle sicher.
     */
    static ABSTAND_WARNUNG_MM = 40;

    /**
     * Eine Zeile, die in den Reiter passt.
     *
     * Der Hautabstand bleibt drin: Er ist die eine Zahl, die „liegt an"
     * belegt. Wird daraus ein zweistelliger Wert, drapiert etwas auf dem
     * falschen Körper, ohne dass ein Fehler auftritt — dann sagt sie es
     * ausdrücklich.
     */
    static kurzbilanz(netz, getragen) {
        if (!getragen) return `Drapiert, aber nicht an der Figur (${netz.dauer_s} s)`;
        const abstand = Number(netz.hautabstand_mm);
        if (isFinite(abstand)
                && abstand > GarmentcodeBilanz.ABSTAND_WARNUNG_MM) {
            return `Fertig, steht aber ${abstand.toFixed(0)} mm ab — sitzt nicht`;
        }
        const haut = isFinite(abstand) ? `, ${abstand.toFixed(0)} mm zur Haut` : '';
        const starr = (netz.auf_figur !== false && !getragen.angezogen)
            ? ' — unbeweglich' : '';
        // Abweichende Reglerstellung nennen (09.09.2026): Ohne sie liesse
        // sich ein Ergebnis später nicht mehr der Einstellung zuordnen, mit
        // der es entstanden ist. Steht alles auf Vorgabe, bleibt es leer.
        const fein = GarmentcodeBauregler.zusatz(netz.feineinstellung);
        return `Fertig in ${netz.dauer_s} s${haut}${fein}${starr}`;
    }

    /**
     * Was die Figur JETZT trägt — nicht, was gerechnet wurde.
     *
     * Der Hautabstand steht mit drin, weil er die einzige Zahl ist, die
     * „liegt an" belegt. Ein T-Shirt kommt auf wenige Millimeter; wird
     * daraus eine zweistellige Zahl, drapiert etwas auf dem falschen
     * Körper, ohne dass ein Fehler auftritt.
     */
    static bilanz(netz, getragen) {
        if (!getragen) {
            return `Drapiert (${netz.punkte} Punkte, ${netz.dauer_s} s), `
                + `aber NICHT an der Figur`;
        }
        const abstand = Number(netz.hautabstand_mm);
        const sitz = !isFinite(abstand) ? ''
            : (abstand <= GarmentcodeBilanz.ABSTAND_WARNUNG_MM
                ? `, ${abstand.toFixed(0)} mm zur Haut`
                : `, steht ${abstand.toFixed(0)} mm ab — sitzt nicht`);
        // Auf einem SMPL-Referenzkörper (06.09.2026) gibt es weder Skelett
        // noch Korrektur — das ist der Weg des Online-Tools, und so heißt
        // es auch. „Unbeweglich" wäre dort keine Einschränkung, sondern
        // die Messlatte.
        const beweglich = netz.auf_figur === false
            ? `, auf dem Referenzkörper ${netz.drapierkoerper || ''} wie das Online-Tool`
            : (getragen.angezogen
                ? `, beweglich über ${getragen.zugeordnet} Knochen`
                // Nach dem Skelettbau oben bleibt dieser Fall nur noch
                // für Figuren ohne DEF-Rig (erzeugte Modelle) — und dann
                // ist es keine Eigenschaft der Figur, sondern ihrer Bauart.
                : ', unbeweglich: diese Bauart hat kein DEF-Rig');
        // Wie viele Punkte in der Haut steckten und herausgeholt wurden.
        // Ohne die Zahl bliebe unsichtbar, dass dieser Schritt überhaupt
        // stattfindet — und wie viel er zu tun hatte.
        const geholt = Number(netz.aus_der_haut) > 0
            ? `, ${netz.aus_der_haut} Punkte aus der Haut geholt` : '';
        return `Fertig: ${netz.punkte} Punkte, ${netz.dreiecke} Dreiecke `
            + `in ${netz.dauer_s} s${sitz}${geholt}${beweglich}`;
    }
}
