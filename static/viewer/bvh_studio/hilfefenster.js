import { HELP_CONTENT } from './hilfetexte.js';

/**
 * Hilfefenster — das Hilfemenü der Werkzeugleiste und das Fenster dahinter.
 *
 * Aus `setupToolbar()` herausgeloest (Umbau 16.08.2026): Die sieben
 * Hilfethemen waren sieben gleichlautende Zeilen
 * (`helpDD?.classList.remove('open'); showHelp('<thema>')`) — jetzt eine Liste,
 * die aus den Kennungen der Menüeinträge die Themen ableitet.
 */
export class Hilfefenster {

    /** Themen in der Reihenfolge des Menüs; Kennung ist `dd-help-<thema>`. */
    static THEMEN = ['tracks', 'camera', 'light', 'audio', 'shortcuts',
                     'animations', 'export'];

    static verdrahten(menue) {
        for (const thema of Hilfefenster.THEMEN) {
            document.getElementById(`dd-help-${thema}`)
                ?.addEventListener('click', () => {
                    menue?.classList.remove('open');
                    Hilfefenster.zeigen(thema);
                });
        }
        document.getElementById('help-modal-close')
            ?.addEventListener('click', () => Hilfefenster.schliessen());
        // Klick auf den Rand schließt — nicht auf den Inhalt.
        document.getElementById('help-modal')?.addEventListener('click', ereignis => {
            if (ereignis.target === ereignis.currentTarget) Hilfefenster.schliessen();
        });
    }

    static zeigen(thema) {
        const text = HELP_CONTENT[thema];
        if (!text) return;
        document.getElementById('help-modal-title').innerHTML =
            `<i class="fas fa-question-circle"></i> ${text.title}`;
        document.getElementById('help-modal-body').innerHTML = text.body;
        document.getElementById('help-modal').style.display = 'flex';
    }

    static schliessen() {
        const fenster = document.getElementById('help-modal');
        if (fenster) fenster.style.display = 'none';
    }
}
