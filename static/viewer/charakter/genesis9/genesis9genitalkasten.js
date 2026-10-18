/**
 * Genesis9genitalkasten — die Kästen des Bereichs „Genitalien" (`Genesis9genitalien`) von außen nachziehen, OHNE ihn neu zu bauen.
 *
 * Edgar, 18.10.2026: „es sollen doch ALLE Assets umbenannt und gelöscht werden können?" — die Stücke dieses Bereichs sind Stücke der Garderobe.
 * Wird eines dort (oder anderswo, `Genesis9garderobepflege`) umbenannt oder gelöscht, muss sein Kasten hier sofort mitziehen, nicht erst nach
 * dem Neuladen. Ohne Importe, damit `Genesis9garderobepflege` ihn nehmen kann, ohne dass ein Ring entsteht (der Bereich hängt über das Menü
 * an der Pflege).
 */
export class Genesis9genitalkasten {

    /** Der Kasten eines Stücks — null, solange der Bereich nicht gebaut ist oder das Stück keine Anatomie hat. */
    static kastenVon(kennung) {
        return [...document.querySelectorAll('details.g9-genitalstueck')].find(kasten => kasten.dataset.stueck === kennung) || null;
    }

    /** Dem Kasten sein Stück und den Kopftext mitgeben (`titel`: `stueck => Text`), damit `benennen` den Kopf neu setzen kann. */
    static merken(kasten, stueck, titel) {
        kasten._stueck = stueck;
        kasten._titel = titel;
    }

    /** Neuer Anzeigename: im Stück und im Kopf des Kastens. */
    static benennen(kennung, name) {
        const kasten = Genesis9genitalkasten.kastenVon(kennung);
        if (!kasten?._stueck) return;
        kasten._stueck.name = name;
        const text = kasten.querySelector(':scope > summary')?.firstChild;
        if (text?.nodeType === Node.TEXT_NODE) text.textContent = `${kasten._titel(kasten._stueck)} `;
    }

    /** Den Kasten wegnehmen, falls es ihn gibt. */
    static entfernen(kennung) {
        Genesis9genitalkasten.kastenVon(kennung)?.remove();
    }
}
