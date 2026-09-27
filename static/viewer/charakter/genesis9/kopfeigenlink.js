import { escapeHtml } from '../utils.js';

/**
 * Kopfeigenlink — im Reglerabschnitt „Kopf-Eigen" der Weg zur Seite „Gesichtsform".
 *
 * Edgar, 27.09.2026: „diese neuen Morphs sollen in einem neuen Abschnitt ‚Kopf-Eigen' erscheinen."
 * Die Morphe selbst sind Regler wie alle anderen (`G9schnittmorph.bereich`); gemalt und gerechnet
 * werden sie auf `/gesichtsform/?modell=<Name>` (Schnitte und Konturen, `core/api/gesichtsform.py`).
 * Der Abschnitt steht immer da — auch ohne Morph, sonst gäbe es keinen Weg dorthin.
 */
export class Kopfeigenlink {

    static SCHLUESSEL = 'kopf_eigen';

    /** Unter die Regler des Abschnitts „Kopf-Eigen" den Link für die geladene Figur hängen. */
    static anhaengen(kasten, bereich, inst) {
        if (bereich.schluessel !== Kopfeigenlink.SCHLUESSEL) return;
        const zeile = document.createElement('div');
        zeile.className = 'gedaempft kopfeigen-link';
        const name = inst?.presetName || '';
        const adresse = `/gesichtsform/?modell=${encodeURIComponent(name)}`;
        zeile.innerHTML = `<a href="${adresse}" target="_blank" rel="noopener">`
            + `<i class="fas fa-draw-polygon"></i> Gesichtsform von „${escapeHtml(name)}" malen …</a>`
            + (bereich.regler.length ? '' : '<br>Noch kein Kopf-Eigen-Morph — dort wird er gerechnet.');
        kasten.appendChild(zeile);
    }
}
