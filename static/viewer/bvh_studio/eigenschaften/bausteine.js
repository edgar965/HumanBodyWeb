/**
 * Maskenbausteine — die drei HTML-Schnipsel, aus denen jede Eigenschaftsmaske
 * besteht.
 *
 * Aus properties.js herausgeloest (Umbau 16.08.2026): Das `<div class="prop-row">
 * <label>…</label>…</div>`-Muster stand dort ueber hundertmal ausgeschrieben.
 */
export class Maskenbausteine {
    /** Eine Beschriftungszeile mit beliebigem Bedienelement. */
    static zeile(beschriftung, inhalt) {
        return `<div class="prop-row"><label>${beschriftung}:</label>${inhalt}</div>`;
    }

    /** Zahlenfeld. `zusatz` nimmt min/max/step als fertiges Attributstueck. */
    static zahl(id, wert, zusatz = '') {
        return `<input type="number" value="${wert}" id="${id}" ${zusatz}>`;
    }

    /** Abschnitt mit Ueberschrift. */
    static gruppe(titel, inhalt) {
        return `<div class="prop-group">`
             + `<h3 class="abschnittstitel-akzent">${titel}</h3>`
             + `${inhalt}</div>`;
    }

    /** Kurzform fuer addEventListener auf eine Element-Kennung. */
    static an(id, ereignis, hoerer) {
        document.getElementById(id)?.addEventListener(ereignis, hoerer);
    }
}
