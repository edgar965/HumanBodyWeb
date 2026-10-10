/**
 * Recherchemodelleinternet — das Bildfenster der Seite „Hilfe → Recherche → Modelle Internet" (10.10.2026).
 *
 * Edgar: „Vorschau (Icon)" in der Tabelle; ein Klick auf das Bild zeigt es groß (wie bei Human 3D). Das Fenster steht fertig in der Vorlage
 * (`#mi-bildfenster`). Ein Bild, das nicht mehr lädt, wird durch „–" ersetzt, nicht stumm leer gelassen. Keine Serverabrufe, keine fremden Texte als HTML:
 * Titel und Alt-Text gehen nur über `textContent` bzw. Attribute.
 */
export class Recherchemodelleinternet {

    constructor() {
        this.fenster = document.getElementById('mi-bildfenster');
        this.gross = document.getElementById('mi-bildgross');
        this.titel = document.getElementById('mi-bildtitel');
        this.zu = document.getElementById('mi-bildfenster-zu');
    }

    binden() {
        document.addEventListener('click', (e) => {
            const ziel = e.target instanceof Element ? e.target : null;
            const bild = ziel ? ziel.closest('td.mi-bildzelle img.mi-bild') : null;
            if (bild) this.oeffnen(bild);
        });
        // `error` steigt nicht auf, wird aber in der Fangphase gesehen.
        document.addEventListener('error', (e) => Recherchemodelleinternet.bildFehlt(e.target), true);
        this.zu.addEventListener('click', () => this.fenster.close());
        // Klick auf den abgedunkelten Rand schließt (das Ziel ist dann das <dialog> selbst, nicht sein Inhalt).
        this.fenster.addEventListener('click', (e) => { if (e.target === this.fenster) this.fenster.close(); });
    }

    /** Zeigt die Vorschau groß; Titel = Name des Modells und die Herkunft des Bildes (steht im `title` der Kachel). */
    oeffnen(bild) {
        this.gross.alt = bild.alt;
        this.gross.src = bild.currentSrc || bild.src;
        this.titel.textContent = bild.title ? `${bild.alt} — ${bild.title}` : bild.alt;
        this.fenster.showModal();
    }

    static bildFehlt(ziel) {
        if (!(ziel instanceof HTMLImageElement) || !ziel.classList.contains('mi-bild')) return;
        const platz = document.createElement('span');
        platz.className = 'mi-fehlt';
        platz.textContent = '–';
        platz.title = 'Das Bild konnte nicht geladen werden';
        ziel.replaceWith(platz);
    }
}

new Recherchemodelleinternet().binden();
