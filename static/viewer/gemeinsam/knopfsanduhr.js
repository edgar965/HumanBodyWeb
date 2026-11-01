/**
 * Knopfsanduhr — ein Knopf zeigt eine Sanduhr und ist gesperrt, solange sein Vorgang läuft (31.10.2026, Edgar: „beim Button ‚Rendern‘ und den anderen Export-Buttons, wenn der
 * Prozess läuft, eine Sanduhr, deaktiviere den“). Die ursprüngliche Beschriftung merkt sich der Knopf selbst (`data-ohne-sanduhr`) und bekommt sie beim Ausschalten zurück;
 * mehrfaches Ein- oder Ausschalten ändert nichts.
 */
export class Knopfsanduhr {

    /** @param an Sanduhr zeigen und sperren — aus: alte Beschriftung zurück (gesperrt bleibt er, wenn `gesperrt`) @param text Beschriftung neben der Sanduhr */
    static setzen(knopf, an, text = '', gesperrt = false) {
        const hat = knopf.dataset.ohneSanduhr !== undefined;
        if (an && !hat) {
            const alt = knopf.textContent.trim();
            knopf.dataset.ohneSanduhr = knopf.innerHTML;
            knopf.innerHTML = '<i class="fas fa-hourglass-half fa-spin"></i> ';
            knopf.append(text || alt);
        } else if (!an && hat) {
            knopf.innerHTML = knopf.dataset.ohneSanduhr;
            delete knopf.dataset.ohneSanduhr;
        }
        knopf.disabled = an || gesperrt;
        knopf.setAttribute('aria-busy', an ? 'true' : 'false');
    }
}
