/**
 * Auswahlfeld — Optionen an ein `<select>` hängen.
 *
 * BEFUND (30.08.2026): Diese vier Zeilen standen SECHZEHNMAL im Projekt,
 * verteilt auf neun Dateien:
 *
 *     const opt = document.createElement('option');
 *     opt.value = t.key;
 *     opt.textContent = t.label;
 *     feld.appendChild(opt);
 *
 * — in `scene/cloth.js` (dreimal), `scene/hair.js` (viermal),
 * `scene/charmorph_hair.js` (zweimal), `scene/properties.js` (zweimal),
 * `viewer/hair.js` (zweimal), `viewer/kleiderpakete.js`,
 * `bvh_studio/eigenschaften/boden.js`, `gemeinsam/kategoriewahl.js` und
 * `vergleich/vergleichsregler.js`. Fünf davon waren in EINE Zeile gequetscht
 * (bis 240 Zeichen) und darum als lange Zeile gemeldet.
 *
 * Die Kopien liefen auseinander: mal `value`/`textContent`, mal zusätzlich
 * `dataset.name`, mal ohne Prüfung auf ein fehlendes Feld. Ein `<select>`, das
 * es nicht gibt, wirft hier keine Ausnahme mehr, sondern füllt nichts.
 *
 * NICHT umgestellt ist die Farbliste in `scene/charmorph_hair.js`: Dort trägt
 * jeder Eintrag seine eigene Haarfarbe als Inline-Stil — der hängt am Eintrag
 * und lässt sich nicht als Klasse vorhalten.
 */
export class Auswahlfeld {

    /**
     * Optionen anhängen. Vorhandene bleiben stehen — wer ersetzen will, leert
     * das Feld vorher selbst (`feld.innerHTML = ''`).
     *
     * @param feld       das `<select>`; fehlt es, passiert nichts
     * @param eintraege  [{ wert, text, daten, gewaehlt }] — `daten` landet im
     *                   `dataset`, `gewaehlt` setzt `selected`
     * @returns {number} wie viele Optionen angehängt wurden
     */
    static fuellen(feld, eintraege) {
        if (!feld || !eintraege) return 0;
        let gesetzt = 0;
        for (const e of eintraege) {
            const eintrag = document.createElement('option');
            eintrag.value = e.wert;
            eintrag.textContent = e.text;
            if (e.daten) Object.assign(eintrag.dataset, e.daten);
            if (e.gewaehlt) eintrag.selected = true;
            feld.appendChild(eintrag);
            gesetzt += 1;
        }
        return gesetzt;
    }

    /**
     * Kurzform für die häufigste Bauart: eine Serverliste aus `{key, label}`.
     *
     * @param feld   das `<select>`
     * @param liste  [{ key, label }] — `null`/`undefined` ist zulässig
     * @returns {number} wie viele Optionen angehängt wurden
     */
    static ausSchluesseln(feld, liste) {
        return Auswahlfeld.fuellen(feld, (liste || []).map(
            (e) => ({ wert: e.key, text: e.label })));
    }

    /**
     * Kurzform für eine Liste blosser Namen — Wert und Aufschrift sind gleich.
     *
     * @param feld    das `<select>`
     * @param namen   Zeichenketten
     * @param zeigen  wahlweise: wie der Name angezeigt wird
     * @returns {number} wie viele Optionen angehängt wurden
     */
    static ausNamen(feld, namen, zeigen = null) {
        return Auswahlfeld.fuellen(feld, (namen || []).map(
            (n) => ({ wert: n, text: zeigen ? zeigen(n) : n })));
    }
}
