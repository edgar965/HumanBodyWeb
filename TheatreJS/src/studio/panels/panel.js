/**
 * Panel — gemeinsame Grundlage der Eigenschaften-Bereiche.
 *
 * Herausgeloest aus main.js (Umbau 16.08.2026). Dort gab es drei Funktionen
 * (Licht, Kleidung, Figur), die alle mit denselben sechs Zeilen begannen:
 * Reiter umschalten, `properties-content` holen, HTML hineinschreiben. Diese
 * sechs Zeilen standen dreimal.
 *
 * Zweiter Grund fuer die Klasse: Die Panels bauten ihr HTML mit Inline-Stilen,
 * dieselbe `style="width:100%;padding:4px;background:…"`-Kette teils
 * sechsmal in einer Funktion. Die Bausteine hier (`zahlfeld`, `dreierblock`,
 * `schieber`) erzeugen Markup mit CSS-Klassen; die Regeln stehen einmal im
 * Stilblock von theatre.html.
 */
export class Panel {

    /** id des Behaelters, in den alle Panels schreiben. */
    static ZIEL = 'properties-content';

    /** Reiter, der beim Oeffnen aktiv wird. */
    static REITER = 'tab-properties';

    /**
     * Reiter umschalten und den Zielbereich zurueckgeben (oder null).
     * Ersetzt die sechs Zeilen, die in jedem Panel wortgleich standen.
     */
    static oeffnen() {
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        const reiter = document.querySelector(`[data-tab="${Panel.REITER}"]`);
        const flaeche = document.getElementById(Panel.REITER);
        if (reiter) reiter.classList.add('active');
        if (flaeche) flaeche.classList.add('active');
        return document.getElementById(Panel.ZIEL);
    }

    /** Zielbereich leeren (Auswahl aufgehoben). */
    static leeren(text = 'Kein Objekt ausgewählt') {
        const ziel = document.getElementById(Panel.ZIEL);
        if (ziel) ziel.innerHTML = `<div class="pnl-leer">${text}</div>`;
    }

    // ------------------------------------------------------- Markup-Bausteine

    static kopf(symbol, titel) {
        return `<h3 class="pnl-kopf"><i class="fas ${symbol}"></i> ${titel}</h3>`;
    }

    static zahlfeld(id, wert, schritt = 0.1) {
        return `<input type="number" id="${id}" class="pnl-zahl" value="${wert}" step="${schritt}">`;
    }

    /** Drei benannte Zahlfelder in einer Reihe — fuer Position und Drehung. */
    static dreierblock(titel, praefix, werte, schritt = 0.1) {
        const achsen = ['x', 'y', 'z'].map((achse, i) => `
            <div><span class="pnl-achse">${achse.toUpperCase()}:</span>
                ${Panel.zahlfeld(`${praefix}-${achse}`, werte[i], schritt)}</div>`).join('');
        return `<div class="pnl-feld"><label class="pnl-label">${titel}</label>
            <div class="pnl-drei">${achsen}</div></div>`;
    }

    static schieber(id, titel, wert, { min = 0, max = 100, step = 1 } = {}) {
        return `<div class="pnl-feld">
            <label class="pnl-label">${titel}: <span id="${id}-wert">${wert}</span></label>
            <input type="range" id="${id}" class="pnl-schieber"
                   min="${min}" max="${max}" step="${step}" value="${wert}">
        </div>`;
    }

    static farbfeld(id, titel, hex) {
        return `<div class="pnl-feld"><label class="pnl-label">${titel}</label>
            <input type="color" id="${id}" class="pnl-farbe" value="${hex}"></div>`;
    }

    static hinweis(text) {
        return `<div class="pnl-hinweis"><i class="fas fa-info-circle"></i> ${text}</div>`;
    }

    /** Mehrere Elemente auf einmal holen; fehlt eines, kommt null zurueck. */
    static felder(...ids) {
        const gefunden = ids.map(id => document.getElementById(id));
        return gefunden.some(e => !e) ? null : gefunden;
    }
}
