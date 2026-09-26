import { escapeHtml } from '../utils.js';

/**
 * Mhreglerzeile — eine Schieber- oder Farbzeile, im Baum erzeugt.
 *
 * Die Vorlagenmarke `{% regler %}` gibt es nur für Zeilen, die IM HTML stehen.
 * Haut und Kleidung bauen ihre Zeilen erst, wenn eine Figur gewählt ist (und
 * die Kleidung sogar je getragenem Stück), also im JavaScript — und dort stand
 * derselbe Block sonst zweimal.
 *
 * Die Wertanzeige heißt bewusst nicht `<id>-val` wie bei der Vorlagenmarke:
 * Diese Zeilen haben gar keine feste Kennung, weil es sie mehrfach gibt. Wer
 * den Wert braucht, bekommt ihn im Rückruf.
 */
export class Mhreglerzeile {

    /**
     * @param {Object} angabe `{name, titel, wert, min, max, einheit}`
     * @param {Function} beimZiehen (wert) => void — bei jedem Pixel
     * @param {Function} [beimLoslassen] (wert) => void — einmal am Ende
     */
    static schieber(angabe, beimZiehen, beimLoslassen = null) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = `<label title="${escapeHtml(angabe.titel || angabe.name)}">`
            + `${escapeHtml(angabe.name)}</label>`;
        const schieber = document.createElement('input');
        schieber.type = 'range';
        schieber.min = String(angabe.min ?? 0);
        schieber.max = String(angabe.max ?? 100);
        schieber.step = '1';
        schieber.value = String(angabe.wert ?? 0);
        schieber.className = 'hb-dehnt-ohne-abstand';
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        const zeigen = () => {
            anzeige.textContent = `${schieber.value}${angabe.einheit || ''}`;
        };
        zeigen();
        schieber.addEventListener('input', () => {
            zeigen();
            beimZiehen(Number(schieber.value));
        });
        if (beimLoslassen) {
            schieber.addEventListener('change',
                                      () => beimLoslassen(Number(schieber.value)));
        }
        zeile.append(schieber, anzeige);
        return zeile;
    }

    /** Eine Farbzeile — `beimAendern(hexwert)`. */
    static farbe(name, wert, beimAendern) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = `<label>${escapeHtml(name)}</label>`;
        const feld = document.createElement('input');
        feld.type = 'color';
        feld.className = 'hb-farbfeld';
        feld.value = wert;
        feld.addEventListener('input', () => beimAendern(feld.value));
        zeile.appendChild(feld);
        return zeile;
    }
}
