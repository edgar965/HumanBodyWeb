/**
 * Modellchecktabelle — alle Befunde des Modell Checks als Tabelle (02.11.2026 spätabends, Edgar: „mache eine Tabelle mit allen Befunden und wenn ich auf einen
 * Eintrag gehe, dann markiere mir diesen Eintrag rot auf dem View“). Zeilen aus `Modellcheckbefunde.sammeln`, durchgefallene zuerst. Überfahren (Maus oder
 * Tastaturfokus) zeigt nur diesen Befund rot in der 3D-Ansicht (`Modellcheck3d.hervorheben`); Klick hält ihn fest und fährt die Kamera hin, ein zweiter Klick
 * löst ihn. Ohne Wahl zeigt die Ansicht alle durchgefallenen Befunde.
 */
export class Modellchecktabelle {

    static SPALTEN = ['', 'Prüfung', 'Stück', 'Ort', 'Messwert'];

    /** `huelle`: `[data-modellcheck="befunde"]`, `raum`: die `Modellcheck3d` des Dialogs. */
    constructor(huelle, raum) {
        this.huelle = huelle;
        this.raum = raum;
        this.gewaehlt = null;
    }

    leeren() {
        this.huelle.replaceChildren();
        this.gewaehlt = null;
    }

    zeigen(befunde) {
        this.leeren();
        const fehler = befunde.filter((b) => b.fehler).length;
        const kopf = document.createElement('div');
        kopf.className = 'modellcheck-befundkopf';
        kopf.textContent = befunde.length
            ? `Befunde: ${befunde.length}, davon ${fehler} durchgefallen — Zeile überfahren: nur dieser Befund rot im View · Klick: festhalten und hinfahren`
            : 'Keine Befunde.';
        this.huelle.appendChild(kopf);
        if (!befunde.length) return;
        const tabelle = document.createElement('table'), thead = document.createElement('thead'), tbody = document.createElement('tbody');
        tabelle.className = 'modellcheck-befundtabelle';
        const kz = document.createElement('tr');
        for (const s of Modellchecktabelle.SPALTEN) { const th = document.createElement('th'); th.textContent = s; kz.appendChild(th); }
        thead.appendChild(kz);
        for (const b of befunde) tbody.appendChild(this._zeile(b));
        tabelle.append(thead, tbody);
        this.huelle.appendChild(tabelle);
    }

    _zeile(b) {
        const tr = document.createElement('tr');
        tr.className = b.fehler ? 'fehler' : 'unter';
        tr.tabIndex = 0;
        tr.title = b.fehler ? 'durchgefallen' : 'unter der Grenze der Prüfung';
        const zeichen = document.createElement('i');
        zeichen.className = `fas ${b.fehler ? 'fa-times' : 'fa-minus'}`;
        const zellen = [zeichen, b.pruefung, b.stueck, b.ort, b.wert];
        for (const z of zellen) {
            const td = document.createElement('td');
            if (z instanceof Node) td.appendChild(z); else td.textContent = z ?? '';
            tr.appendChild(td);
        }
        tr.addEventListener('mouseenter', () => this.raum.hervorheben(b));
        tr.addEventListener('focus', () => this.raum.hervorheben(b));
        tr.addEventListener('mouseleave', () => this.raum.hervorheben(this.gewaehlt?.b || null));
        tr.addEventListener('blur', () => this.raum.hervorheben(this.gewaehlt?.b || null));
        tr.addEventListener('click', () => this._waehlen(tr, b));
        tr.addEventListener('keydown', (e) => { if (e.key === 'Enter') this._waehlen(tr, b); });
        return tr;
    }

    _waehlen(tr, b) {
        const war = this.gewaehlt?.b === b;
        this.gewaehlt?.tr.classList.remove('gewaehlt');
        this.gewaehlt = war ? null : { tr, b };
        if (war) { this.raum.hervorheben(null); return; }
        tr.classList.add('gewaehlt');
        this.raum.hervorheben(b, true);
    }
}
