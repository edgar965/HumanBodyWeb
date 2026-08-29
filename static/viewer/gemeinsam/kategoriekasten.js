/**
 * Kategoriekasten — eine aufklappbare Gruppe im Baum.
 *
 * WARUM (Befund `doppelcode`, 29.08.2026): Diese Zeilen standen SIEBENMAL —
 *
 *     static/viewer/animation/baum.js            static/viewer/scene/animation.js
 *     static/viewer/scene/garments.js            static/viewer/viewer/animation.js
 *     static/viewer/skelett_test/animationsbaum.js
 *     static/viewer/viewer/kleiderliste.js       static/viewer/viewer/smpl_kleiderliste.js
 *
 * Gemeldet waren davon zwei (`kleiderliste.js` gegen `smpl_kleiderliste.js`,
 * 15 Zeilen); die übrigen fünf unterscheiden sich in Kleinigkeiten und blieben
 * unter der Blockgrösse.
 *
 * UND SIE WAREN AUSEINANDERGELAUFEN: Fünf zeichnen den Pfeil als
 * Font-Awesome-Symbol (`<i class="fas fa-chevron-right">`), zwei als
 * Unicode-Dreieck (`&#9654;`). Das ist kein Geschmack, sondern ein Versehen:
 * `animationsbaum.css` dreht `.cat-chevron` beim Aufklappen um 90° — beide
 * Formen drehen sich, aber sie sehen verschieden aus, und zwar in derselben
 * Seitenleiste untereinander. Hier gilt die Fassung der Mehrheit.
 *
 * Die Beschriftung wird als TEXT gesetzt, nicht als HTML: Kategorienamen
 * kommen aus Verzeichnisnamen auf der Platte. Drei der sieben Stellen liessen
 * sie durch `escapeHtml` laufen, vier nicht — auch das eine Stelle weniger,
 * an der man es vergessen kann.
 */
export class Kategoriekasten {
    /**
     * @param {string} beschriftung Anzeigename der Gruppe (roher Text)
     * @param {number} anzahl Zahl rechts im Kopf
     * @param {Object} [wahl]
     * @param {boolean} [wahl.offen] gleich aufgeklappt zeigen
     * @param {boolean} [wahl.gross] Beschriftung in Grossbuchstaben
     * @returns {{kasten: Element, kopf: Element, koerper: Element}}
     */
    static bauen(beschriftung, anzahl, {offen = false, gross = false} = {}) {
        const kasten = document.createElement('div');
        kasten.className = offen ? 'anim-category open' : 'anim-category';

        const kopf = document.createElement('div');
        kopf.className = 'anim-category-header';
        const pfeil = document.createElement('span');
        pfeil.className = 'cat-chevron';
        pfeil.innerHTML = '<i class="fas fa-chevron-right"></i>';
        const text = document.createElement('span');
        text.textContent = gross ? String(beschriftung).toUpperCase()
                                 : String(beschriftung);
        const zahl = document.createElement('span');
        zahl.className = 'cat-count';
        zahl.textContent = String(anzahl);
        kopf.append(pfeil, text, zahl);
        kopf.addEventListener('click', () => kasten.classList.toggle('open'));
        kasten.appendChild(kopf);

        const koerper = document.createElement('div');
        koerper.className = 'anim-category-body';
        kasten.appendChild(koerper);

        return {kasten, kopf, koerper};
    }
}
