/**
 * Detailzeilen folgen ihrer Hauptzeile — auch nach dem Sortieren.
 *
 * WARUM ES DIESE DATEI GIBT (28.08.2026, djangoBase-Konformität)
 * ==============================================================
 * `Auftragsliste` hatte eine EIGENE Sortierung: Klick auf `th[data-sort]`,
 * Zeilen umhängen, Detailzeile hinterherziehen. Das ist djangoBases
 * `TabellenSortierung` noch einmal — mit einem Unterschied: Sie kennt
 * Detailzeilen nicht und würde die aufgeklappten Details beim Sortieren beim
 * falschen Auftrag stehen lassen.
 *
 * Statt die Sortierung deshalb doppelt zu führen, hängt sich diese Klasse an
 * das Ereignis, das djangoBase dafür vorsieht: `tabelle:sortiert`. Es wird
 * gerade dafür ausgelöst — „damit Gliederungen, die auf der Reihenfolge
 * beruhen, nachziehen können" (Kommentar in `tabellen_sortierung.js`).
 */
export class Detailzeilen {
    /** Vorsatz der Hauptzeilen-Kennung: `row-<auftrag>`. */
    static ZEILE = 'row-';
    /** Vorsatz der Detailzeile: `detail-<auftrag>`. */
    static DETAIL = 'detail-';

    /**
     * Hängt sich an die Tabelle. Mehrfaches Aufrufen ist harmlos.
     * @param {HTMLTableElement} tabelle
     */
    static binden(tabelle) {
        if (!tabelle || tabelle.dataset.detailzeilen === '1') return;
        tabelle.dataset.detailzeilen = '1';
        tabelle.addEventListener('tabelle:sortiert',
                                 () => Detailzeilen.nachziehen(tabelle));
    }

    /** Jede Detailzeile direkt hinter ihre Hauptzeile hängen. */
    static nachziehen(tabelle) {
        const koerper = tabelle.tBodies[0];
        if (!koerper) return;
        for (const zeile of [...koerper.rows]) {
            if (!zeile.id.startsWith(Detailzeilen.ZEILE)) continue;
            const kennung = zeile.id.slice(Detailzeilen.ZEILE.length);
            const detail = document.getElementById(
                Detailzeilen.DETAIL + kennung);
            // `after` und nicht `appendChild`: Die Detailzeile gehört UNTER
            // ihre Hauptzeile, nicht ans Tabellenende.
            if (detail) zeile.after(detail);
        }
    }
}
