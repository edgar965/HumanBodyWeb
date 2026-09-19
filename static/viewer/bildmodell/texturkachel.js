/**
 * Texturkachelpanel — was in EINE Kachel hineinkommt, klar gezeigt.
 *
 * Edgar (20.09.2026): „ich verstehe nicht diese Bilder, mach klare Bilder was in
 * das Bein, Nagel hineinkommt. das ist doch reinstes Chaos!" Ein Klick auf eine
 * Kachel im Bereich „Textur" öffnet darunter dieses Panel: links die Karte der
 * Kachel (`kachelkarte_<k>.png`, `G9kachelkarte`: jede Insel nach Körperteil
 * eingefärbt und beschriftet), daneben die Kachel selbst, und dann je Foto, das
 * in die Kachel liefert, sein Beitragsbild (`beitrag_<nr>_<k>.jpg`, `Texturbeitrag`:
 * die benutzten Pixel in voller Farbe mit Saum in der Kachelfarbe, der Rest
 * abgedunkelt) mit dem Anteil an den Texeln der Kachel, absteigend sortiert.
 * `referenz(z, ft)`: unter den Kacheln die tatsächliche Haut der Referenzfigur.
 */
import { Genesis9texturen } from '../gemeinsam/genesis9texturen.js';

export class Texturkachelpanel {

    static NAMEN = { 1001: 'Kopf', 1002: 'Rumpf', 1003: 'Beine', 1004: 'Arme', 1005: 'Nägel' };
    /** Farbe je Kachel — dieselbe wie `Texturbeitrag.FARBEN` (Saum der Beitragsbilder). */
    static FARBEN = { 1001: 'rgb(240,90,90)', 1002: 'rgb(80,160,240)', 1003: 'rgb(90,200,110)',
                      1004: 'rgb(245,180,50)', 1005: 'rgb(190,100,230)' };

    constructor(auftrag) {
        this.auftrag = auftrag;
        this.feld = document.getElementById('textur-kachelpanel');
        this.kachel = null;
    }

    /** Kachel wählen (nochmal = schließen) und zeichnen. */
    waehlen(kachel, ft) {
        this.kachel = this.kachel === kachel ? null : kachel;
        this.zeigen(ft);
    }

    zeigen(ft) {
        if (!this.feld) return;
        this.feld.innerHTML = '';
        const kachel = this.kachel;
        if (!kachel || !ft || !(ft.kacheln || {})[kachel]) { this.feld.classList.add('hb-versteckt'); return; }
        this.feld.classList.remove('hb-versteckt');
        this.feld.style.borderColor = Texturkachelpanel.FARBEN[kachel] || '';
        const marke = ft.stand || Date.now();
        const kopf = document.createElement('div');
        kopf.className = 'bildmodell-kachelpanelkopf';
        const beitraege = this.beitraege(ft, kachel);
        kopf.innerHTML = `<strong>${kachel} · ${Texturkachelpanel.NAMEN[kachel] || ''}</strong> — was hineinkommt: `
            + `${beitraege.length} ${beitraege.length === 1 ? 'Foto' : 'Fotos'}, `
            + `${Math.round(100 * beitraege.reduce((s, b) => s + b.anteil, 0))} % der Kachel belegt`;
        const schliessen = document.createElement('button');
        schliessen.type = 'button';
        schliessen.className = 'btn btn-secondary btn-sm';
        schliessen.textContent = 'Schließen';
        schliessen.addEventListener('click', () => this.waehlen(kachel, ft));
        kopf.appendChild(schliessen);
        const reihe = document.createElement('div');
        reihe.className = 'bildmodell-kachelpanelreihe';
        const karte = (ft.karten || {})[kachel];
        if (karte) {
            reihe.appendChild(this._figur(this.auftrag.dateiAdresse('ergebnis', karte) + `?t=${marke}`,
                                          'Körperteile in der Kachel', 'Welcher Körperteil wo liegt'));
        }
        reihe.appendChild(this._figur(this.auftrag.dateiAdresse('ergebnis', ft.kacheln[kachel]) + `?t=${marke}`,
                                      'die Kachel', 'Die gebackene Kachel'));
        for (const b of beitraege) {
            const text = `${b.datei} · ${(100 * b.anteil).toFixed(1).replace('.', ',')} % der Kachel`;
            const adresse = b.bild ? this.auftrag.dateiAdresse('ergebnis', b.bild) + `?t=${marke}`
                                   : this.auftrag.dateiAdresse('zuschnitt', b.datei);
            reihe.appendChild(this._figur(adresse, text, `${b.texel.toLocaleString('de-DE')} Texel aus ${b.datei}`));
        }
        if (!beitraege.length) {
            const leer = document.createElement('p');
            leer.className = 'hb-hinweis';
            leer.textContent = 'Kein Foto liefert in diese Kachel — die Kachel zeigt die getönte Grundhaut.';
            reihe.appendChild(leer);
        }
        this.feld.append(kopf, reihe);
    }

    /**
     * Die TATSÄCHLICHE Haut der Referenzfigur eines Testfalls — ohne Testfall die
     * Standard-Genesis-Haut nach Geschlecht — als zweite Reihe unter den gebackenen
     * Kacheln (Edgar, 20.09.2026: „mach einen Bereich mit der tatsächlichen Textur
     * von Ursula darunter, damit ich vergleichen kann"; Damira: Standardhaut).
     * `z.texturreferenz = {name, kacheln: {kachel: Bibliothekspfad}}`, Bilder über
     * den Texturvorrat-Endpunkt.
     */
    referenz(z, ft) {
        const feld = document.getElementById('textur-referenz');
        if (!feld) return;
        feld.innerHTML = '';
        const referenz = z.texturreferenz || {};
        const pfade = referenz.kacheln || {};
        const kacheln = Object.keys(pfade).filter(k => !ft || (ft.kacheln || {})[k]);
        if (!ft || !kacheln.length) { feld.classList.add('hb-versteckt'); return; }
        feld.classList.remove('hb-versteckt');
        const kopf = document.createElement('p');
        kopf.className = 'bildmodell-referenzkopf';
        kopf.textContent = `Zum Vergleich: ${referenz.name || 'Referenz'}`;
        const reihe = document.createElement('div');
        reihe.className = 'bildmodell-texturkacheln';
        for (const kachel of kacheln) {
            const adresse = Genesis9texturen.adresse(pfade[kachel]);
            const fig = document.createElement('figure');
            fig.className = 'bildmodell-texturkachel';
            const a = document.createElement('a');
            a.href = adresse;
            a.target = '_blank';
            a.title = `${kachel} der Referenz in voller Größe öffnen`;
            const img = document.createElement('img');
            img.src = adresse;
            img.alt = `Referenz ${kachel}`;
            a.appendChild(img);
            const text = document.createElement('figcaption');
            text.textContent = `${kachel} · ${Texturkachelpanel.NAMEN[kachel] || ''} · Referenz`;
            fig.append(a, text);
            reihe.appendChild(fig);
        }
        feld.append(kopf, reihe);
    }

    /** `[{datei, anteil, texel, bild}]` der Fotos, die in die Kachel liefern — absteigend nach Anteil. */
    beitraege(ft, kachel) {
        const aus = [];
        for (const e of (ft.je_bild || [])) {
            const b = (e.beitraege || {})[String(kachel)];
            if (!b || !(b.anteil > 0)) continue;
            aus.push({ datei: e.datei, anteil: b.anteil, texel: b.texel || 0, bild: b.datei || null });
        }
        aus.sort((a, b) => b.anteil - a.anteil);
        return aus;
    }

    _figur(adresse, text, titel) {
        const fig = document.createElement('figure');
        fig.className = 'bildmodell-kachelbeitrag';
        const a = document.createElement('a');
        a.href = adresse;
        a.target = '_blank';
        a.title = `${titel} — in voller Größe öffnen`;
        const img = document.createElement('img');
        img.src = adresse;
        img.alt = text;
        a.appendChild(img);
        const unter = document.createElement('figcaption');
        unter.textContent = text;
        fig.append(a, unter);
        return fig;
    }
}
