/**
 * Fotogenesisschalterleiste — Knopfgruppen und Schalter einer Bedienleiste der Seite „Foto-Genesis“, aus `Fotogenesissteuerung` herausgelöst (04.11.2026): die feste Leiste oben
 * (`Fotogenesissteuerung`) und die Leisten der Zeilen (`Fotogenesiszeilenleiste`, Edgar: „in jeder Zeile ab Zeile 3 diese ansichten plus die Rig, Kleider Toggle buttons“) bauen ihre
 * Knöpfe gleich. Der Zustand steht als Eigenschaft unter dem Schlüssel jeder Gruppe; Änderungen meldet die Leiste an `geaendert(schluessel)`.
 */
export class Fotogenesisschalterleiste {
    /** @param {HTMLElement} leiste @param {(was: string) => void} geaendert */
    constructor(leiste, geaendert) {
        this.leiste = leiste;
        this.geaendert = geaendert;
    }

    _gruppe(titel, eintraege, schluessel) {
        const gruppe = this.leiste.appendChild(document.createElement('div'));
        gruppe.className = 'fotogenesis-steuergruppe';
        gruppe.append(Object.assign(document.createElement('span'), { className: 'fotogenesis-steuername', textContent: titel }));
        const reihe = gruppe.appendChild(document.createElement('div'));
        reihe.className = 'schalterleiste';
        reihe.setAttribute('role', 'group');
        reihe.setAttribute('aria-label', titel);
        for (const e of eintraege) {
            const knopf = reihe.appendChild(document.createElement('button'));
            knopf.type = 'button';
            knopf.className = 'schaltknopf';
            knopf.title = e.titel ?? '';
            if (e.icon) knopf.append(Object.assign(document.createElement('i'), { className: `fas ${e.icon}` }));
            knopf.append(document.createTextNode(e.text));
            knopf.addEventListener('click', () => this.setzen(schluessel, e.wert));
            knopf._wert = e.wert;
        }
        reihe.dataset.schluessel = schluessel;
        this._markieren(schluessel);
    }

    /** Ein einzelner Schaltknopf für einen Wahrheitswert (gedrückt = an). */
    _schalter(text, schluessel, titel, icon) {
        const reihe = this.leiste.appendChild(document.createElement('div'));
        reihe.className = 'fotogenesis-steuergruppe schalterleiste';
        const knopf = reihe.appendChild(document.createElement('button'));
        knopf.type = 'button';
        knopf.className = 'schaltknopf';
        knopf.title = titel;
        knopf.append(Object.assign(document.createElement('i'), { className: `fas ${icon}` }), document.createTextNode(text));
        knopf.addEventListener('click', () => this.setzen(schluessel, !this[schluessel]));
        knopf._wert = true;
        reihe.dataset.schluessel = schluessel;
        this._markieren(schluessel);
    }

    _markieren(schluessel) {
        const reihe = this.leiste.querySelector(`[data-schluessel="${schluessel}"]`);
        for (const k of reihe?.children ?? []) {
            const an = k._wert === this[schluessel];
            k.classList.toggle('active', an);
            k.setAttribute('aria-pressed', String(an));
        }
    }

    setzen(schluessel, wert) {
        if (this[schluessel] === wert) return;
        this[schluessel] = wert;
        this._markieren(schluessel);
        this.geaendert(schluessel);
    }
}
