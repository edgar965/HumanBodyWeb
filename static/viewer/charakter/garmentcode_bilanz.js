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
 * SEIT DEM 10.09.2026 SIND ES ZWEI: Der Median allein hat Edgar dreimal
 * „funktioniert immer noch nicht" schreiben lassen — er meldete 9,4 mm,
 * während der Stoff an der Brust auf 2,7 mm anlag, weil Dekolleté, Achsel
 * und frei fallender Saum mitzählen. Das engste Viertel (`hautabstand_eng_mm`)
 * beschreibt, was wirklich am Körper ankommt; der Median, wie weit das Stück
 * insgesamt absteht. Warum ein Quartil und keine Kontaktschwelle, steht in
 * `Assets/GarmentCode/hautabstand.py` — gemessen gibt es kein Tal in der
 * Verteilung, an dem sich eine Schwelle festmachen ließe.
 *
 * `garmentcode_drapieren.js` lag bei 156 Zeilen und wäre mit den zwei
 * Fassungen auf 204 gewachsen — der angefasste Teil wird abgeteilt
 * (`~/.claude/rules/struktur.md`).
 */
export class GarmentcodeBilanz {

    /**
     * Millimeter für deutsche Augen: Komma statt Punkt, und eine
     * Nachkommastelle nur, solange sie etwas sagt.
     *
     * `toFixed` liefert „2.4" und „4" — das erste ist im Deutschen falsch
     * geschrieben, das zweite verschenkt bei einem einstelligen Wert genau
     * die Stelle, um die es hier geht (4 gegen 4,3 mm).
     */
    static mm(wert) {
        const zahl = Number(wert);
        if (!isFinite(zahl)) return '';
        return zahl.toLocaleString('de-DE', {
            minimumFractionDigits: zahl < 10 ? 1 : 0,
            maximumFractionDigits: zahl < 10 ? 1 : 0,
        });
    }

    /**
     * Die Schwelle steht NICHT mehr hier (10.09.2026).
     *
     * Der Server entscheidet über `hautabstand_sitzt`, weil er beide Grenzen
     * kennt — engstes Viertel und Median — und weil eine Zahl, die an zwei
     * Stellen gepflegt wird, irgendwann an einer davon veraltet.
     * `Assets/GarmentCode/hautabstand.Hautabstand` führt sie.
     */

    /**
     * Eine Zeile, die in den Reiter passt.
     *
     * Der Hautabstand bleibt drin: Er ist die eine Zahl, die „liegt an"
     * belegt. Wird daraus ein zweistelliger Wert, drapiert etwas auf dem
     * falschen Körper, ohne dass ein Fehler auftritt — dann sagt sie es
     * ausdrücklich.
     */
    static kurzbilanz(netz, getragen) {
        // Ein ABSTURZ der Simulation zuerst, vor allem anderen (09.09.2026):
        // Vorher kam er als „Fertig, steht aber 166 mm ab — sitzt nicht"
        // heraus, also als schlechtes Ergebnis statt als Fehler. Wer das
        // liest, dreht an den Reglern und sucht an der falschen Stelle.
        if (netz.abgestuerzt) {
            return 'Die Stoffsimulation ist abgestürzt — das gezeigte Netz '
                + 'ist unfertig. Meist liegt es an einem Reglerwert im '
                + 'Bereich „Simulation".';
        }
        if (!getragen) return `Drapiert, aber nicht an der Figur (${netz.dauer_s} s)`;
        const abstand = Number(netz.hautabstand_mm);
        const eng = Number(netz.hautabstand_eng_mm);
        if (netz.hautabstand_sitzt === false) {
            return `Fertig, sitzt aber nicht — ${GarmentcodeBilanz.mm(eng)} mm `
                + `selbst an den engsten Stellen, `
                + `${GarmentcodeBilanz.mm(abstand)} mm im Mittel`;
        }
        // „liegt mit X an" zuerst: Das ist die Frage, die beim Ansehen
        // gestellt wird. Der Median steht daneben, weil ein weit fallender
        // Schnitt dort zweistellig sein DARF (Kreisrock: 8 mm eng, 27 mm
        // Median — beides richtig).
        const haut = isFinite(eng)
            ? `, liegt mit ${GarmentcodeBilanz.mm(eng)} mm an`
                + (isFinite(abstand)
                    ? ` (Median ${GarmentcodeBilanz.mm(abstand)} mm)` : '')
            : (isFinite(abstand)
                ? `, ${GarmentcodeBilanz.mm(abstand)} mm zur Haut` : '');
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
        const eng = Number(netz.hautabstand_eng_mm);
        const sitz = !isFinite(abstand) ? ''
            : (netz.hautabstand_sitzt !== false
                ? `, ${GarmentcodeBilanz.mm(eng)} mm im engsten Viertel der `
                    + `Stoffpunkte (das ist, was am Körper ankommt), `
                    + `${GarmentcodeBilanz.mm(abstand)} mm im Mittel über alle — `
                    + `Dekolleté, Achsel und frei fallender Saum zählen da mit`
                : `, steht ${GarmentcodeBilanz.mm(abstand)} mm ab und selbst das `
                    + `engste Viertel liegt bei ${GarmentcodeBilanz.mm(eng)} mm `
                    + `— sitzt nicht`);
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
