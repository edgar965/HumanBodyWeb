import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Bibliothekskanal } from '../gemeinsam/bibliothekskanal.js';
import { Kontextmenue } from '../gemeinsam/kontextmenue.js';
import { Ordnerwahl } from '../gemeinsam/ordnerwahl.js';

/**
 * Kontextmenü auf den Animationen im Szene-Reiter — umbenennen und löschen.
 *
 * Edgar, 08.09.2026: „Ich möchte die Animationen aus dem Tab umbenennen und
 * löschen können, mach mir die Kontextmenüs dazu."
 *
 * ES IST DERSELBE ENDPUNKT WIE IM BVH-STUDIO
 * ==========================================
 * `/api/character/bvh-manage/` kann `rename` und `delete` seit langem; das
 * Studio bedient ihn über `Bibliothekablage`. Hier wird nichts nachgebaut —
 * ein zweiter Weg zum selben Dateisystem würde irgendwann anders prüfen als
 * der erste.
 *
 * GELÖSCHT WIRD EINE DATEI AUF DER PLATTE, nicht ein Eintrag in einer Liste:
 * `3DObjects/animations/bvh/<Kategorie>/<Name>.bvh`. Deshalb steht der Name
 * in der Rückfrage — „Wirklich löschen?" allein sagt nicht, WAS gleich weg
 * ist, und die Zeile unter dem Mauszeiger ist nicht immer die, die man meint.
 */
export class Animationsmenue {

    static ENDPUNKT = '/api/character/bvh-manage/';

    /**
     * Das Menü an eine Baumzeile hängen. `danach(aktion)` läuft nach
     * `rename`, `move` oder `delete` — das Löschen braucht mehr als einen
     * neuen Baum (`Animationsentfernung`).
     */
    static binden(zeile, kategorie, name, danach) {
        zeile.addEventListener('contextmenu', (ereignis) => {
            ereignis.preventDefault();
            // Ohne `stopPropagation` öffnete zusätzlich das Menü des
            // Browsers oder eines äußeren Bereichs — beides zugleich.
            ereignis.stopPropagation();
            Animationsmenue.zeigen(ereignis.clientX, ereignis.clientY,
                                   kategorie, name, danach);
        });
    }

    /** Kasten, Lage im Fenster und Schließen: `gemeinsam/kontextmenue.js`. */
    static zeigen(x, y, kategorie, name, danach) {
        Kontextmenue.zeigen(x, y, [
            { symbol: 'fa-pen', text: 'Umbenennen',
              tun: () => Animationsmenue.umbenennen(kategorie, name, danach) },
            { symbol: 'fa-arrows-alt', text: 'Verschieben nach …',
              tun: () => Animationsmenue.verschieben(kategorie, name, danach) },
            { symbol: 'fa-trash', text: 'Löschen',
              tun: () => Animationsmenue.loeschen(kategorie, name, danach) },
        ]);
    }

    // Kein `verbergen()` vor den Aktionen (17.10.2026): Das Menü schließt
    // `Kontextmenue` beim Klick selbst. Die Klasse hatte die Methode nicht —
    // Umbenennen, Verschieben und Löschen warfen einen TypeError, bevor sie fragten.
    static async umbenennen(kategorie, name, danach) {
        const neu = prompt(`Neuer Name für „${name}":`, name);
        if (!neu || neu === name) return false;
        if (!await Animationsmenue._senden('rename', {
                category: kategorie, name, new_name: neu })) {
            return false;
        }
        if (danach) danach('rename', { category: kategorie, name, new_name: neu });
        return true;
    }

    /**
     * In einen anderen Ordner verschieben.
     *
     * Edgar, 08.09.2026: „mach auch einen Kontextmenü eintrag zum verschieben
     * in einen anderen Ordner (mit Popup in welchen)".
     *
     * Das Popup zeigt die vorhandenen Ordner ZUR AUSWAHL und lässt daneben
     * einen neuen Namen zu. Ein blosses `prompt` wäre hier schlecht: Die
     * Ordner heissen `Bandai 1`, `MixamoDance`, `Bondai Dance` — wer den
     * Namen tippt, tippt ihn falsch, und der Server legt dann stillschweigend
     * einen zweiten Ordner daneben an.
     */
    static async verschieben(kategorie, name, danach) {
        const ziel = await Ordnerwahl.waehlen(`„${name}" liegt in „${kategorie}"`,
            Animationsmenue.ordner().map((o) => ({ wert: o, text: o, aktuell: o === kategorie })));
        if (!ziel || ziel === kategorie) return false;
        if (!await Animationsmenue._senden('move', {
                category: kategorie, name, new_category: ziel })) {
            return false;
        }
        if (danach) danach('move');
        return true;
    }

    static async loeschen(kategorie, name, danach) {
        if (!confirm(`„${name}" aus „${kategorie}" endgültig löschen?\n\n`
                     + 'Die BVH-Datei wird von der Platte entfernt.')) {
            return false;
        }
        if (!await Animationsmenue._senden('delete',
                                           { category: kategorie, name })) {
            return false;
        }
        if (danach) danach('delete');
        return true;
    }

    static async _senden(aktion, daten) {
        try {
            await Serverabruf.senden(Animationsmenue.ENDPUNKT,
                                     { action: aktion, ...daten });
            // Die anderen Tabs (Studio, Animationen) holen ihren Baum neu.
            Bibliothekskanal.melden(aktion, daten);
            return true;
        } catch (fehler) {
            alert(`Fehler: ${fehler.message || fehler}`);
            return false;
        }
    }

    /** Die Ordner, die der Baum gerade führt — in seiner Reihenfolge. */
    static ordner() {
        return Array.from(
            document.querySelectorAll('#anim-tree .anim-category-header'))
            // Die Zahl rechts im Kopf gehört nicht zum Namen.
            .map((kopf) => kopf.querySelector('span:nth-child(2)')?.textContent)
            .map((text) => (text || '').trim())
            .filter(Boolean);
    }

    // Das Auswahlfenster „Verschieben nach …“ steht seit 17.10.2026 in
    // `gemeinsam/ordnerwahl.js` — der Reiter „Posen“ braucht dasselbe.

}
