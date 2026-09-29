/**
 * Meshfigurkleidung — die Karte „Kleidung" der Auftragsseite (Schritt „kleidung", 29.09.2026).
 *
 * Zeigt, was `Meshfigurkleidung` aus dem Körpernetz geschnitten hat: das Netz OHNE Kleidung und die Kleidung allein,
 * je von vorn, seitlich und hinten (gleicher Ausschnitt), dazu die Kennzahlen aus `ergebnis.kleidung` — Anteil, die
 * Stücke (Oberteil, Hose, Socken, Zubehör) und woher der Hautton kommt. Neu gezeichnet wird nur, wenn sich
 * `ergebnis.kleidung` geändert hat. Die Kleidung selbst sitzt als Objekt auf der Figur (`Meshfigurkleider`).
 */
export class Meshfigurkleidung {

    static TEILE = { ohne: 'Netz ohne Kleidung', nur: 'Nur Kleidung' };
    static ANSICHTEN = { vorn: 'vorn', seite: 'seitlich', hinten: 'hinten' };
    static GRUPPEN = {
        gesicht: 'Gesicht', hand_l: 'Hand links', hand_r: 'Hand rechts', unterarm_l: 'Unterarm links',
        unterarm_r: 'Unterarm rechts', unterschenkel_l: 'Unterschenkel links', unterschenkel_r: 'Unterschenkel rechts',
    };

    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('kleidung');
        this._stand = null;
    }

    static zahl(wert, stellen = 1) {
        return wert === null || wert === undefined ? '–' : Number(wert).toFixed(stellen).replace('.', ',');
    }

    static rgb(w) { return w ? `(${w.join(', ')})` : '–'; }

    zeigen(z) {
        if (!this.feld) return;
        const k = (z.ergebnis || {}).kleidung;
        const stand = JSON.stringify(k || null);
        if (stand === this._stand) return;
        this._stand = stand;
        this.feld.innerHTML = '';
        if (!k) {
            this.feld.textContent = 'Noch keine Kleidung geschnitten — kommt im Schritt „Kleidung" nach dem Haar.';
            return;
        }
        if (k.fehler) {
            this.feld.textContent = `Kleidung nicht erkannt: ${k.fehler}`;
            return;
        }
        const text = document.createElement('p');
        text.className = 'hb-hinweis';
        text.textContent = Meshfigurkleidung.text(k);
        this.feld.appendChild(text);
        this.feld.appendChild(Meshfigurkleidung.stuecke(k));
        this.feld.appendChild(this.raster(k));
    }

    /** Die Kennzahlen in einem Satz (`Kleidungsteilung.kennzahlen`). */
    static text(k) {
        const z = Meshfigurkleidung.zahl, h = k.hautmodell || {};
        const gruppen = Object.entries(h.gruppen || {}).filter(([, g]) => g.angenommen)
            .map(([n]) => Meshfigurkleidung.GRUPPEN[n] || n).join(', ');
        const verworfen = Object.entries(h.gruppen || {}).filter(([, g]) => !g.angenommen)
            .map(([n]) => Meshfigurkleidung.GRUPPEN[n] || n).join(', ');
        return `Kleidung ${z(k.anteil_prozent)} % der Körperfläche (${z(k.cm2, 0)} cm², ${k.flaechen} von `
            + `${k.flaechen_gesamt} Flächen), Farbe Median ${Meshfigurkleidung.rgb(k.farbe)}. Hautton `
            + `${Meshfigurkleidung.rgb(h.hautton)} aus den kahlen Stellen (${gruppen || '–'})`
            + `${verworfen ? `; bedeckt und nicht gezählt: ${verworfen}` : ''} — nicht aus Rumpf und Oberschenkeln, `
            + `dort trägt man meist Stoff. Rechenzeit ${z((k.sekunden || {}).erkennen)} s, `
            + `Bilder ${z((k.sekunden || {}).bilder)} s.`;
    }

    static stuecke(k) {
        const liste = document.createElement('ul');
        liste.className = 'meshfigur-kleidungsstuecke';
        for (const s of k.stuecke || []) {
            const punkt = document.createElement('li');
            const farbe = document.createElement('span');
            farbe.className = 'meshfigur-farbfeld';
            farbe.style.background = `rgb(${(s.farbe || [128, 128, 128]).join(',')})`;
            punkt.append(farbe, `${s.name}: ${Meshfigurkleidung.zahl(s.cm2, 0)} cm² (${s.flaechen} Flächen), `
                + `Höhe ${Meshfigurkleidung.zahl(s.y_von_m, 2)}–${Meshfigurkleidung.zahl(s.y_bis_m, 2)} m`);
            liste.appendChild(punkt);
        }
        return liste;
    }

    raster(k) {
        const raster = document.createElement('div');
        raster.className = 'meshfigur-kleidungsraster';
        const marke = encodeURIComponent(JSON.stringify(k.sekunden || {}));
        for (const [teil, titel] of Object.entries(Meshfigurkleidung.TEILE)) {
            for (const [ansicht, wort] of Object.entries(Meshfigurkleidung.ANSICHTEN)) {
                const name = ((k.bilder || {})[teil] || {})[ansicht];
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
        return raster;
    }
}
