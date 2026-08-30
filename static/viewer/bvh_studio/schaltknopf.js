/**
 * Schaltknopf — der An/Aus-Knopf der Eigenschaftsleiste.
 *
 * BEFUND (30.08.2026, `jsbefunde`): Dieses Markup stand VIERMAL im Studio,
 * jedes Mal neu geschrieben und jedes Mal mit demselben achtteiligen
 * Inline-Stil, von dem sieben Teile fest waren:
 *
 *     <button id="${id}" style="padding:5px 16px;background:${an ? '#4caf50'
 *       : '#666'};color:#fff;border:none;border-radius:4px;cursor:pointer;
 *       font-weight:bold;min-width:60px;">${an ? 'An' : 'Aus'}</button>
 *
 * — in `properties.js` (Sichtbarkeit), `eigenschaften/boden.js` (Raster),
 * `eigenschaften/licht.js` (Lichtschalter) und
 * `eigenschaften/klip_schluesselbilder.js` (Licht am Schlüsselbild). Nur die
 * Farbe hing am Zustand; alles andere war Kopie. Die vier Kopien waren dabei
 * auseinandergelaufen: 16px / 14px / 12px Innenabstand und 60px / 50px
 * Mindestbreite — ohne dass ein Unterschied gemeint war.
 *
 * Geblieben sind zwei Grössen: die normale und `schmal` für die enge
 * Schlüsselbild-Leiste. Die Farben stehen in `bvh_studio.html` als
 * `.schaltknopf.an` / `.schaltknopf.aus`.
 */
export class Schaltknopf {

    /**
     * Das Markup eines An/Aus-Knopfs.
     *
     * @param kennung  `id` des Knopfs
     * @param an       Zustand — bestimmt Farbe und Aufschrift
     * @param schmal   engere Bauform (Schlüsselbild- und Lichtleiste)
     * @returns {string} HTML
     */
    static bauen(kennung, an, schmal = false) {
        const klassen = `schaltknopf ${an ? 'an' : 'aus'}${schmal ? ' schmal' : ''}`;
        return `<button id="${kennung}" class="${klassen}">`
            + `${an ? 'An' : 'Aus'}</button>`;
    }
}
