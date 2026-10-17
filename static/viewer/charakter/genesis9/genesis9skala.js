/**
 * Genesis9skala — die Anzeige eines Reglers in seiner eigenen Einheit (17.10.2026).
 *
 * Die meisten Schieber zeigen „Prozent" (Daz' Kanäle). Der Sammelregler „Lebensalter" (`G9lebensalter`) läuft −1…1, soll aber Jahre zeigen:
 * Er bringt `skala` mit — Stützstellen `[Wert, Anzeige]`, dazwischen linear — und `einheit`. Ohne `skala` bleibt alles wie vorher (`text` gibt `null`).
 */
export class Genesis9skala {
    /** „10 Jahre" für den Wert `wert` des Reglers, oder `null`, wenn er keine eigene Skala hat. */
    static text(wert, regler) {
        const stuetzen = regler?.skala;
        if (!Array.isArray(stuetzen) || stuetzen.length < 2) return null;
        let anzeige = stuetzen[stuetzen.length - 1][1];
        if (wert <= stuetzen[0][0]) anzeige = stuetzen[0][1];
        else {
            for (let i = 1; i < stuetzen.length; i++) {
                const [x0, y0] = stuetzen[i - 1];
                const [x1, y1] = stuetzen[i];
                if (wert <= x1) {
                    anzeige = y0 + (y1 - y0) * (wert - x0) / (x1 - x0);
                    break;
                }
            }
        }
        return `${Math.round(anzeige)} ${regler.einheit || ''}`.trim();
    }
}
