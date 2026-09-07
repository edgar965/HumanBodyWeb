/**
 * Fortschrittsrechnung — wie voll ist der Balken?
 *
 * WARUM OHNE DOM (Edgar, 06.09.2026: „mach einen Fortschrittsbalken"): Ein
 * Balken, der lügt, ist schlimmer als keiner. Echten Fortschritt meldet der
 * Server nicht — die Simulation läuft in einem eigenen Prozess und schweigt
 * bis zum Ende. Also wird geschätzt, und dann muss die Schätzung nachprüfbar
 * sein statt in einer Zeichenroutine zu verschwinden.
 *
 * DIE KURVE
 * =========
 * Innerhalb eines Schrittes läuft der Balken nach `1 - exp(-k·t/erwartet)`:
 *
 *      t = 0            0 %
 *      t = erwartet    80 %
 *      t = 2×erwartet  96 %
 *      t → ∞        →  DECKEL (97 %)
 *
 * Linear wäre schlechter: Der Balken stünde bei einer Drapierung, die länger
 * dauert als gedacht, am Anschlag und rührte sich nicht mehr — genau das
 * Bild, das „hängt" bedeutet. So kriecht er immer weiter und erreicht die
 * volle Breite trotzdem erst, wenn der Schritt wirklich fertig ist.
 *
 * Die Schritte sind nach ihrer erwarteten Dauer GEWICHTET. Ohne das wäre der
 * Schnitt (rund 3 s) genauso breit wie die Drapierung (rund 40 s), und der
 * Balken spränge sofort auf ein Drittel, um dann eine Minute zu stehen.
 */
export class Fortschrittsrechnung {

    /** So weit kommt ein laufender Schritt höchstens — fertig ist fertig. */
    static DECKEL = 0.97;

    /** Steilheit: bei der erwarteten Dauer sind 80 % erreicht. */
    static STEILE = 1.6;

    /** Erwartete Dauer, wenn ein Schritt keine mitbringt (Sekunden). */
    static VORGABE_S = 5;

    /**
     * Anteil EINES laufenden Schrittes.
     *
     * @param verstrichen  Sekunden seit Beginn des Schrittes
     * @param erwartet     erwartete Dauer in Sekunden
     */
    static anteil(verstrichen, erwartet) {
        const t = Math.max(0, Number(verstrichen) || 0);
        const soll = Number(erwartet) > 0
            ? Number(erwartet) : Fortschrittsrechnung.VORGABE_S;
        const wert = 1 - Math.exp(-Fortschrittsrechnung.STEILE * t / soll);
        return Math.min(Fortschrittsrechnung.DECKEL, wert);
    }

    /**
     * Gesamtfortschritt über alle Schritte, 0…1.
     *
     * Ein Schritt ist `{stand, erwartet, verstrichen}` — `stand` ist
     * 'wartet', 'laeuft', 'fertig' oder 'fehler'. Gescheiterte Schritte
     * zählen wie fertige: Der Balken soll nicht zurückspringen, wenn etwas
     * schiefgeht; das sagt die Zeile daneben.
     */
    static gesamt(schritte) {
        const liste = Array.isArray(schritte) ? schritte : [];
        if (!liste.length) return 0;
        let summe = 0;
        let erreicht = 0;
        for (const schritt of liste) {
            const gewicht = Number(schritt?.erwartet) > 0
                ? Number(schritt.erwartet) : Fortschrittsrechnung.VORGABE_S;
            summe += gewicht;
            if (schritt?.stand === 'fertig' || schritt?.stand === 'fehler') {
                erreicht += gewicht;
            } else if (schritt?.stand === 'laeuft') {
                erreicht += gewicht * Fortschrittsrechnung.anteil(
                    schritt.verstrichen, gewicht);
            }
        }
        return summe > 0 ? erreicht / summe : 0;
    }

    /**
     * Die verbleibende Zeit in Sekunden — oder null, wenn sie nicht zu
     * schätzen ist.
     *
     * Geschätzt wird aus den ERWARTETEN Dauern der noch offenen Schritte,
     * nicht aus dem Balkenstand: Der Balken kriecht asymptotisch, eine
     * Restzeit daraus zurückzurechnen ergäbe absurde Werte.
     */
    static rest(schritte) {
        const liste = Array.isArray(schritte) ? schritte : [];
        let rest = 0;
        let offen = false;
        for (const schritt of liste) {
            if (schritt?.stand === 'fertig' || schritt?.stand === 'fehler') continue;
            const gewicht = Number(schritt?.erwartet) > 0
                ? Number(schritt.erwartet) : Fortschrittsrechnung.VORGABE_S;
            offen = true;
            rest += schritt?.stand === 'laeuft'
                ? Math.max(0, gewicht - (Number(schritt.verstrichen) || 0))
                : gewicht;
        }
        return offen ? Math.round(rest) : null;
    }

    /** „1:05" oder „12 s" — kurz genug für die Zeile über dem Balken. */
    static zeit(sekunden) {
        const s = Math.max(0, Math.round(Number(sekunden) || 0));
        if (s < 60) return `${s} s`;
        return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
    }
}
