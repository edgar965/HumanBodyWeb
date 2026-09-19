/**
 * Dialoggroesse — ein vergrößerbares `<dialog>`, dessen Größe gemerkt wird.
 *
 * Edgar (20.09.2026): „das Fenster soll vergrößerbar sein, merke dir die Größe."
 * Das CSS gibt dem Dialog `resize: both`; beim Ziehen an der Ecke setzt der
 * Browser Breite und Höhe als Inline-Stil. Ein `ResizeObserver` schreibt jede
 * Änderung in den `localStorage` (`{b, h}` in Pixeln), beim nächsten Öffnen
 * gilt sie wieder. Unter 480 × 320 gilt der Merker als kaputt und wird ignoriert.
 */
export class Dialoggroesse {

    static MINDESTENS = { b: 480, h: 320 };

    /** @param dialog das `<dialog>`, @param schluessel Name im `localStorage` */
    static merken(dialog, schluessel) {
        if (!dialog) return;
        let g = null;
        try { g = JSON.parse(localStorage.getItem(schluessel) || 'null'); } catch (e) { g = null; }
        const min = Dialoggroesse.MINDESTENS;
        if (g && g.b >= min.b && g.h >= min.h) {
            dialog.style.width = `${Math.min(g.b, window.innerWidth - 16)}px`;
            dialog.style.height = `${Math.min(g.h, window.innerHeight - 16)}px`;
        }
        if (typeof ResizeObserver === 'undefined') return;
        new ResizeObserver(() => {
            if (!dialog.open) return;
            const b = Math.round(dialog.offsetWidth), h = Math.round(dialog.offsetHeight);
            if (b < min.b || h < min.h) return;
            try { localStorage.setItem(schluessel, JSON.stringify({ b, h })); } catch (e) { /* ohne Merker */ }
        }).observe(dialog);
    }
}
