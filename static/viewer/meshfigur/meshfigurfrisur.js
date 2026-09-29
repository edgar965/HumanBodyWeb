/**
 * Meshfigurfrisur — der Teil „Frisur" der Karte „Haar" (Schritt „frisur", 29.09.2026).
 *
 * Zeigt, was `Meshfigurfrisur` gemessen hat: die gewählte Frisur mit Stil, gestellten Reglern und Farbe, die
 * Reglersuche der besten Frisuren (Hüllenabstand vorher → nachher) und die Rangliste aller gemessenen
 * Frisur-Stil-Paare. Die Zahlen sind der Hüllenabstand zum Netzhaar (`Haar.haarhuelle`, mm, flächengewichtet
 * über alle Richtungen mit Haar) und die Deckung (Anteil der Richtungen mit Netzhaar, die die Frisur auch
 * belegt) — gemessen, nichts geschätzt.
 */
export class Meshfigurfrisur {

    constructor() {
        this.feld = document.getElementById('frisur');
        this._stand = null;
    }

    static zahl(wert, stellen = 1) {
        return wert === null || wert === undefined ? '–' : Number(wert).toFixed(stellen).replace('.', ',');
    }

    zeigen(z) {
        const f = (z.ergebnis || {}).frisur;
        const stand = JSON.stringify(f || null);
        if (!this.feld || stand === this._stand) return;
        this._stand = stand;
        this.feld.innerHTML = '';
        if (!f) {
            this.feld.textContent = 'Noch keine Frisur gewählt — kommt im Schritt „Frisur" nach der Vorschau.';
            return;
        }
        this.feld.append(this._satz(f));
        if ((f.fein || []).length) {
            this.feld.append(this._tabelle(['Frisur', 'Stil', 'vorher mm', 'nachher mm', 'Deckung', 'Regler'],
                f.fein.map(r => [r.name, r.stil || '–', Meshfigurfrisur.zahl(r.vorher?.mm, 2),
                                 Meshfigurfrisur.zahl(r.nachher?.mm, 2), Meshfigurfrisur.zahl(r.nachher?.deckung, 3),
                                 Meshfigurfrisur.regler(r.regler)])));
        }
        if ((f.kandidaten || []).length) {
            const titel = document.createElement('p');
            titel.className = 'hb-hinweis';
            titel.textContent = 'Rangliste ohne Regler (je Frisur und Stil, die besten zuerst):';
            this.feld.append(titel, this._tabelle(['Frisur', 'Stil', 'Abstand mm', 'Deckung', 'fehlt mm', 'zu viel mm'],
                f.kandidaten.map(k => [k.name, k.stil || '–', k.fehler ? k.fehler : Meshfigurfrisur.zahl(k.mm, 2),
                                       Meshfigurfrisur.zahl(k.deckung, 3), Meshfigurfrisur.zahl(k.fehlt_mm, 2),
                                       Meshfigurfrisur.zahl(k.zuviel_mm, 2)])));
        }
    }

    static regler(werte) {
        const paare = Object.entries(werte || {});
        return paare.length ? paare.map(([n, w]) => `${n} ${Meshfigurfrisur.zahl(w, 2)}`).join(', ') : '–';
    }

    _satz(f) {
        const p = document.createElement('p');
        p.className = 'hb-hinweis';
        const w = f.wahl, k = f.karten || {}, s = f.sekunden || {}, z = Meshfigurfrisur.zahl;
        const teile = [];
        if (w) {
            teile.push(`Gewählt: ${w.name}${w.stil ? ` (${w.stil})` : ''}, Hüllenabstand ${z(w.abstand?.mm, 2)} mm, `
                + `Deckung ${z(w.abstand?.deckung, 3)}, Farbe ${w.farbe}.`);
        } else if (f.option === 'aus') {
            teile.push('Keine Frisur (Option „Frisur" steht auf „Keine").');
        }
        if (f.fehler) teile.push(`Frisur: ${f.fehler}.`);
        if (f.eigen_fehler) teile.push(`„Haar Eigen" nicht gebaut: ${f.eigen_fehler}.`);
        if (k.datei) {
            teile.push(`Haarkarten: ${k.straehnen} Strähnen, Länge Median ${z(k.laenge_mm?.median, 0)} mm, `
                + `p90 ${z(k.laenge_mm?.p90, 0)} mm, ${z((k.bytes || 0) / 1048576, 1)} MB.`);
        } else if (k.fehler) {
            teile.push(`Haarkarten: ${k.fehler}.`);
        }
        teile.push(`Rechenzeit Messen ${z(s.messen)} s, Regler ${z(s.regler)} s, Karten ${z(s.karten)} s.`);
        p.textContent = teile.join(' ');
        const farbe = document.createElement('span');
        farbe.className = 'meshfigur-farbfeld';
        if (w) farbe.style.background = w.farbe;
        p.prepend(farbe);
        return p;
    }

    _tabelle(koepfe, zeilen) {
        const tabelle = document.createElement('table');
        tabelle.className = 'doku meshfigur-kettentabelle';
        const kopf = tabelle.createTHead().insertRow();
        for (const k of koepfe) kopf.appendChild(Object.assign(document.createElement('th'), { textContent: k }));
        const rumpf = tabelle.createTBody();
        for (const zeile of zeilen) {
            const tr = rumpf.insertRow();
            for (const wert of zeile) tr.insertCell().textContent = wert;
        }
        return tabelle;
    }
}
