import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Bibliothekablage } from './bibliothekablage.js';

/**
 * Bibliothekmenues — Kontextmenüs und Werkzeugleiste der BVH-Bibliothek.
 *
 * Herausgelöst aus `library.js` (329 Zeilen). Dort war es EINE Funktion mit zwei
 * `if/else if`-Ketten über neun Aktionen; hier ist jede Aktion eine Methode, und
 * die Zuordnung steht als Tabelle (`AKTIONEN`).
 *
 * WARUM NACH JEDER AKTION NEU GELADEN WIRD
 * ========================================
 * Der Baum kommt vom Server. Ihn im Browser „mitzupflegen" hieße, die
 * Ordnerstruktur an zwei Stellen zu führen — und beim ersten Sonderfall
 * (Verschieben in einen Ordner, der noch nicht existiert) laufen sie auseinander.
 * Ein Neuladen kostet einen Aufruf und ist immer richtig.
 */
export class Bibliothekmenues {

    /** Menü-Aktion -> Methode. */
    static AKTIONEN = {
        add: 'hinzufuegen', preview: 'vorschau', copy: 'kopieren',
        rename: 'umbenennen', move: 'verschieben', delete: 'loeschen',
        'rename-folder': 'ordnerUmbenennen', 'new-folder': 'ordnerAnlegen',
        'delete-folder': 'ordnerLoeschen',
    };

    constructor(baum) {
        this.baum = baum;
    }

    /** Alle Menüs und Knöpfe anmelden. */
    binden() {
        document.addEventListener('click', () => {
            document.querySelectorAll('.lib-ctx')
                .forEach(menue => menue.style.display = 'none');
        });
        for (const wahl of ['#lib-ctx-file .lib-ctx-item',
                            '#lib-ctx-folder .lib-ctx-item']) {
            document.querySelectorAll(wahl).forEach(eintrag => {
                eintrag.addEventListener('click',
                                         () => this.ausfuehren(eintrag.dataset.action));
            });
        }
        this.werkzeugleiste();
    }

    werkzeugleiste() {
        this._klick('lib-new-folder', () => this.ordnerAnlegen());
        this._klick('lib-rename', () => this.auswahlUmbenennen());
        this._klick('lib-delete', () => this.auswahlLoeschen());
        this._klick('lib-refresh', () => this.baum.laden());
    }

    _klick(kennung, tun) {
        document.getElementById(kennung)?.addEventListener('click', tun);
    }

    async ausfuehren(aktion) {
        const methode = Bibliothekmenues.AKTIONEN[aktion];
        const ziel = this.baum.menueziel;
        if (!methode || !ziel) return;
        await this[methode](ziel);
    }

    // -------------------------------------------------------------- Dateiaktionen

    hinzufuegen(ziel) {
        fn.addClipToTrack(state.selectedTrackIdx, ziel.category, ziel.name,
                          ziel.frames);
    }

    vorschau(ziel) {
        fn.previewAnimation(ziel.category, ziel.name);
    }

    async kopieren(ziel) {
        const name = prompt('Kopie-Name:', ziel.name + '_copy');
        if (!name || name === ziel.name) return;
        const kategorie = prompt('In welchen Ordner?', ziel.category);
        if (!kategorie) return;
        const antwort = await Bibliothekablage.senden('copy', {
            category: ziel.category, name: ziel.name,
            new_category: kategorie, new_name: name });
        if (!antwort) return;
        fn.serverLog('bvh_copied',
                     `${ziel.category}/${ziel.name} -> ${kategorie}/${name}`);
        this.baum.laden({ category: kategorie, name });
    }

    async umbenennen(ziel) {
        const name = prompt('Neuer Name:', ziel.name);
        if (!name || name === ziel.name) return;
        if (await Bibliothekablage.senden('rename', {
                category: ziel.category, name: ziel.name, new_name: name })) {
            this.baum.laden({ category: ziel.category, name });
        }
    }

    async verschieben(ziel) {
        const kategorie = prompt('In welchen Ordner verschieben?', ziel.category);
        if (!kategorie || kategorie === ziel.category) return;
        if (await Bibliothekablage.senden('move', {
                category: ziel.category, name: ziel.name,
                new_category: kategorie })) {
            this.baum.laden();
        }
    }

    async loeschen(ziel) {
        if (!confirm(`"${ziel.name}" wirklich löschen?`)) return;
        // Den Ordner offen halten und die Auswahl fallen lassen: Der geloeschte
        // Eintrag darf nach dem Neuladen nicht wieder ausgewaehlt werden.
        this.baum.offene.add(ziel.category);
        this.baum.auswahl = null;
        if (await Bibliothekablage.senden('delete', {
                category: ziel.category, name: ziel.name })) {
            Bibliothekablage.clipsEntfernen(ziel.category, ziel.name);
            this.baum.laden();
        }
    }

    // ------------------------------------------------------------ Ordneraktionen

    async ordnerUmbenennen(ziel) {
        const name = prompt('Neuer Ordnername:', ziel.category);
        if (!name || name === ziel.category) return;
        if (await Bibliothekablage.senden('rename_folder', {
                category: ziel.category, new_name: name })) {
            this.baum.laden();
        }
    }

    async ordnerAnlegen() {
        const name = prompt('Name des neuen Ordners:');
        if (!name) return;
        if (await Bibliothekablage.senden('create_folder', { folder_name: name })) {
            this.baum.laden();
        }
    }

    async ordnerLoeschen(ziel) {
        if (!confirm(`Ordner "${ziel.category}" wirklich löschen?\n(Nur wenn leer)`)) {
            return;
        }
        if (await Bibliothekablage.senden('delete_folder',
                                          { category: ziel.category })) {
            this.baum.laden();
        }
    }

    // ------------------------------------------------- Über die Werkzeugleiste

    /** Umbenennen des in der Liste ausgewählten Eintrags. */
    async auswahlUmbenennen() {
        const zeile = document.querySelector('.lib-item.selected');
        if (!zeile) return;
        await this.umbenennen({ category: zeile.dataset.category,
                                name: zeile.dataset.name });
    }

    /** Löschen des in der Liste ausgewählten Eintrags. */
    async auswahlLoeschen() {
        const zeile = document.querySelector('.lib-item.selected');
        if (!zeile) return;
        await this.loeschen({ category: zeile.dataset.category,
                              name: zeile.dataset.name });
    }
}
