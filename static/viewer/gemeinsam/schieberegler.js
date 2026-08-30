/**
 * Schieberegler — einen Regler an seine Wertanzeige hängen, lesen, stellen.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): `scene/utils.js` und
 * `viewer/utils.js` führten dieselben drei Helfer, Zeichen für Zeichen gleich —
 * nur die Namen unterschieden sich (`_bindSlider`/`bindSlider`,
 * `_sliderVal`/`sliderVal`). Die beiden Seiten heißen ihre Helfer weiterhin so,
 * wie sie es gewohnt sind; gerechnet wird nur noch hier.
 *
 * NICHT ZU VERWECHSELN mit `Metaregler`: Der rechnet die vier Körperregler
 * zwischen Anzeigeeinheit (Jahre, Kilogramm) und Serverwert (-1..1) um. Hier
 * geht es um die Bedienung selbst, ohne jede Kenntnis der Bedeutung.
 *
 * FEHLT EIN ELEMENT, passiert nichts — und zwar mit Absicht. Die Seiten
 * verdrahten ihre Regler in Rutschen, und nicht jede Vorlage bringt jeden
 * Regler mit. Eine Ausnahme an dieser Stelle bräche den ganzen Rutsch ab, und
 * die Regler DANACH blieben tot. Das ist der Grund für die stille Rückgabe;
 * wer wissen will, ob ein Regler da ist, fragt vorher `document`.
 *
 * `parseInt` und nicht `parseFloat`: Alle Regler dieser Anwendung arbeiten in
 * ganzen Schritten und rechnen im Format erst herunter (`wert / 1000`). Ein
 * Regler mit Nachkommastellen müsste das hier ändern — und alle Aufrufer mit.
 */
export class Schieberegler {
    /**
     * Regler an seine Anzeige hängen.
     *
     * @param {string} reglerId Kennung des `<input type="range">`
     * @param {string} anzeigeId Kennung des Elements für den Text
     * @param {Function} format Zahl → Text
     */
    static binden(reglerId, anzeigeId, format) {
        const regler = document.getElementById(reglerId);
        const anzeige = document.getElementById(anzeigeId);
        if (!regler || !anzeige) return;
        regler.addEventListener('input', () => {
            anzeige.textContent = format(parseInt(regler.value));
        });
    }

    /** Stellung eines Reglers als ganze Zahl — 0, wenn es ihn nicht gibt. */
    static wert(reglerId) {
        const el = document.getElementById(reglerId);
        return el ? parseInt(el.value) : 0;
    }

    /**
     * Einen Regler stellen und seine Anzeige nachziehen.
     *
     * Farbfelder haben keine Wertanzeige — dort wird nur der Wert gesetzt.
     * Die Anzeige heißt hier fest `<reglerId>-val`; wer einen anderen Namen
     * benutzt, schreibt selbst hinein.
     */
    static setzen(reglerId, wert, format) {
        const el = document.getElementById(reglerId);
        // stumm gewollt: Die Seiten stellen ihre Regler in Rutschen, und nicht
        // jede Vorlage bringt jeden Regler mit. Eine Meldung hier käme bei
        // jedem Seitenaufbau dutzendfach, ohne dass etwas kaputt wäre — und
        // eine Ausnahme bräche den Rutsch ab, sodass die Regler DANACH
        // ungestellt blieben. Wer wissen will, ob es den Regler gibt, fragt
        // vorher `document`.
        if (!el) return;
        el.value = wert;
        if (el.type === 'color') return;
        const anzeige = document.getElementById(reglerId + '-val');
        if (anzeige && format) anzeige.textContent = format(parseInt(wert));
    }
}
