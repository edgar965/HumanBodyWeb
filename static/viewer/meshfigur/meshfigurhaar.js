/**
 * Meshfigurhaar — die Karte „Haar" der Auftragsseite (Schritt „haar", 27.09.2026).
 *
 * Zeigt, was `Meshfigurhaar` aus dem Netz geschnitten hat: das Netz OHNE Haar und das Haar allein, je von vorn,
 * seitlich und hinten (gleicher Ausschnitt), dazu die Kennzahlen aus `ergebnis.haar` (gemessen, nichts
 * geschätzt). Neu gezeichnet wird nur, wenn sich `ergebnis.haar` geändert hat.
 */
export class Meshfigurhaar {

    static TEILE = { ohne: 'Netz ohne Haar', nur: 'Nur Haar' };
    static ANSICHTEN = { vorn: 'vorn', seite: 'seitlich', hinten: 'hinten' };

    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('haar');
        this._stand = null;
    }

    static zahl(wert, stellen = 1) {
        return wert === null || wert === undefined ? '–' : Number(wert).toFixed(stellen).replace('.', ',');
    }

    zeigen(z) {
        const h = (z.ergebnis || {}).haar;
        const stand = JSON.stringify([h, z.updated_at && h ? h.sekunden : null]);
        if (stand === this._stand) return;
        this._stand = stand;
        this.feld.innerHTML = '';
        if (!h) {
            this.feld.textContent = 'Noch kein Haar geschnitten — kommt im Schritt „Haar" nach der Erkennung.';
            return;
        }
        const text = document.createElement('p');
        text.className = 'hb-hinweis';
        text.textContent = Meshfigurhaar.text(h);
        this.feld.appendChild(text);
        const raster = document.createElement('div');
        raster.className = 'meshfigur-haarraster';
        const marke = encodeURIComponent(JSON.stringify(h.sekunden || {}));
        for (const [teil, titel] of Object.entries(Meshfigurhaar.TEILE)) {
            for (const [ansicht, wort] of Object.entries(Meshfigurhaar.ANSICHTEN)) {
                const name = ((h.bilder || {})[teil] || {})[ansicht];
                if (!name) continue;
                const figur = document.createElement('figure');
                const bild = document.createElement('img');
                bild.loading = 'lazy';
                bild.src = `${this.seite.dateiAdresse('ergebnis', name)}?t=${marke}`;
                bild.alt = `${titel}, ${wort}`;
                const unter = document.createElement('figcaption');
                unter.textContent = `${titel} · ${wort}`;
                figur.append(bild, unter);
                raster.appendChild(figur);
            }
        }
        this.feld.appendChild(raster);
    }

    /** Die Kennzahlen in einem Satz (`Haarteilung.kennzahlen`, Millimeter im Gesichtsrahmen). */
    static text(h) {
        const f = h.farbe || {}, rgb = w => (w ? `(${w.join(', ')})` : '–');
        const z = Meshfigurhaar.zahl;
        // Die Farbe der Frisur ist das BELICHTETE Haar (`farbe.haar`, die hellere Hälfte); ältere Läufe kennen nur den Median.
        const farbe = f.haar
            ? `Farbe ${rgb(f.haar)} (belichtetes Haar; Median ${rgb(f.median)}, p10 ${rgb(f.p10)}, p90 ${rgb(f.p90)})`
            : `Farbe Median ${rgb(f.median)}, p10 ${rgb(f.p10)}, p90 ${rgb(f.p90)}`;
        const b = h.bart;
        const bart = b && b.flaechen
            ? ` Bart: ${z(b.cm2, 0)} cm² ${b.aktiv ? 'gehören zur Haut, nicht zum Haar' : ''}, Farbe ${rgb(b.farbe)} (${b.grund}).`
            : (b && b.grund ? ` Bart: ${b.grund}.` : '');
        return `Aus dem ${h.quelle}: Haar ${z(h.anteil_prozent)} % der Kopffläche (${z(h.haar_cm2, 0)} cm², `
            + `${h.flaechen} von ${h.flaechen_gesamt} Flächen); reicht ${z(h.ueber_haut_mm, 0)} mm über den Scheitel `
            + `der Haut und ${z(h.unter_kinn_mm, 0)} mm unter das Kinn; ${farbe}; Hautton ${z(h.hautton, 0)}`
            + `${h.hauttest ? ` (Haut erkannt über: ${h.hauttest})` : ''}.${bart} `
            + `Rechenzeit Maske ${z((h.sekunden || {}).maske)} s, Bilder ${z((h.sekunden || {}).bilder)} s.`;
    }
}
