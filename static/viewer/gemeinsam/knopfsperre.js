/**
 * Knopfsperre — ein Knopf, der einen Lauf startet, ist ab dem Klick gesperrt (27.09.2026).
 *
 * Edgar: „bei den jobs, klick auf ‚Neu Berechnen' soll den Button deaktivieren, um keine
 * 2 Jobs zu starten". Bis hierher wurde der Knopf erst wieder gesperrt, wenn der Server
 * geantwortet hatte und `zeigen()` den Zustand „läuft" gesehen hat — das Anlegen des
 * Prozesses dauert aber, und jeder Klick in dieser Lücke hat einen weiteren Lauf gestartet
 * (der zweite überschreibt dieselben Arbeitsdateien).
 *
 * `waehrend()` sperrt sofort, gibt bei einem Fehlschlag wieder frei und lässt den Knopf
 * nach einem erfolgreichen Start gesperrt — von dort an entscheidet der Zustand der Seite
 * (`disabled = status === 'laeuft'`). Ein Klick auf einen schon gesperrten Knopf tut nichts.
 */
export class Knopfsperre {

    /**
     * @param {HTMLButtonElement|null} knopf Der Knopf, der den Lauf startet.
     * @param {Function} tat Was beim Klick geschehen soll (darf werfen).
     * @param {string} [text] Beschriftung während des Starts (`<span>` im Knopf).
     * @returns Das Ergebnis von `tat()`, oder `undefined`, wenn der Knopf schon gesperrt war.
     */
    static async waehrend(knopf, tat, text = null) {
        if (!knopf) return tat();
        if (knopf.disabled) return undefined;
        const beschriftung = knopf.querySelector('span');
        const vorher = beschriftung ? beschriftung.textContent : null;
        knopf.disabled = true;
        if (text && beschriftung) beschriftung.textContent = text;
        try {
            return await tat();
        } catch (fehler) {
            knopf.disabled = false;
            if (beschriftung && vorher !== null) beschriftung.textContent = vorher;
            throw fehler;
        }
    }
}
