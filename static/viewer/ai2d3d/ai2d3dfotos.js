/**
 * Ai2d3dfotos — Feld 1 „Fotos“ der Seite „2d-3d-AI“ (24.10.2026): das gewählte Foto groß, darunter alle Fotos des Jobs als Leiste; ein Klick auf ein kleines Bild wählt die Perspektive für die ganze Seite.
 * Die Bilder kommen vom Server (`/api/2d3dai/<job>/foto/<nr>/`) und werden je Nummer einmal geladen (`bild` liefert sie für den Vergleich, `Ai2d3dvergleich`).
 */
export class Ai2d3dfotos {
    /**
     * @param {HTMLElement} feld die Fläche für das große Bild @param {HTMLElement} leiste die Leiste der kleinen Bilder
     * @param {{nr: number, name: string, winkel: number|null, adresse: string}[]} fotos @param {(nr: number) => void} beiWahl
     */
    constructor(feld, leiste, fotos, beiWahl) {
        this.feld = feld;
        this.leiste = leiste;
        this.fotos = fotos;
        this._bilder = new Map();
        this.gross = feld.appendChild(document.createElement('img'));
        this.gross.className = 'ai2d3d-foto';
        this.gross.alt = '';
        for (const f of fotos) {
            const knopf = leiste.appendChild(document.createElement('button'));
            knopf.type = 'button';
            knopf.className = 'ai2d3d-daumen';
            knopf.dataset.nr = String(f.nr);
            knopf.title = Ai2d3dfotos.beschriftung(f);
            const klein = knopf.appendChild(document.createElement('img'));
            klein.src = f.adresse;
            klein.alt = knopf.title;
            klein.loading = 'eager';
            const unter = knopf.appendChild(document.createElement('span'));
            unter.textContent = Ai2d3dfotos.kurz(f);
        }
        leiste.addEventListener('click', e => {
            const knopf = e.target.closest('[data-nr]');
            if (knopf) beiWahl(Number(knopf.dataset.nr));
        });
    }

    /** „vorne · 0°“ / „Bild 3 · Winkel unbekannt“ */
    static beschriftung(f) {
        return f.winkel === null ? `${f.name} · Winkel unbekannt` : `${f.name} · ${f.winkel}°`;
    }

    static kurz(f) {
        return f.winkel === null ? `${f.name} (?)` : f.name;
    }

    waehlen(nr) {
        const f = this.fotos[nr];
        this.gross.src = f.adresse;
        this.gross.alt = Ai2d3dfotos.beschriftung(f);
        this.gross.dataset.nr = String(nr);
        for (const k of this.leiste.querySelectorAll('[data-nr]')) k.setAttribute('aria-pressed', String(Number(k.dataset.nr) === nr));
    }

    /** Das Foto als geladenes Bild (für den Vergleich). */
    bild(nr) {
        if (!this._bilder.has(nr)) {
            this._bilder.set(nr, new Promise((fertig, fehler) => {
                const b = new Image();
                b.onload = () => fertig(b);
                b.onerror = () => fehler(new Error(`Foto ${nr} nicht geladen`));
                b.src = this.fotos[nr].adresse;
            }));
        }
        return this._bilder.get(nr);
    }
}
