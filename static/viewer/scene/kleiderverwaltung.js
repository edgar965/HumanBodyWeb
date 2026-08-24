import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Kleiderverwaltung — Umbenennen, Verschieben, Kopieren, Löschen im Katalog.
 *
 * Herausgelöst aus `kleider_liste.js` (267 Zeilen). Alle vier Aktionen gehen an
 * denselben Endpunkt (`/api/character/garment/manage/`) mit einem `action`-Feld;
 * vorher standen sie als `if/else if`-Kette in einer Funktion, jede mit eigenem
 * `try/catch` und eigenem `console.error`.
 *
 * WARUM KOPIEREN DEN KATALOG NEU LÄDT
 * ===================================
 * Eine Kopie entsteht auf dem Server (Ordner, Netz, Beschreibung). Ihre Kennung
 * und ihre Werte kennt der Browser nicht — wer sie sich ausdenkt, zeigt einen
 * Eintrag, der beim nächsten Laden anders heißt. Umbenennen und Verschieben
 * dagegen ändern nur ein Feld, das der Browser schon hat.
 *
 * DAS KONTEXTMENÜ WIRD EINMAL GEBAUT
 * ==================================
 * Es hängt an `document.body`, nicht an der Zeile: Ein Menü je Eintrag wären bei
 * 125 Kleidungsstücken 125 Menüs im DOM. Der Klick-Horcher zum Schließen wird
 * deshalb auch nur einmal angemeldet (`capture: true`, damit er vor dem Klick auf
 * einen Menüpunkt liegt).
 */
export class Kleiderverwaltung {

    static ENDPUNKT = '/api/character/garment/manage/';
    static MENUE_ID = 'kld-ctx-menu';

    /** Die Menüpunkte: Aktion -> Beschriftung. */
    static AKTIONEN = [
        ['rename', 'Umbenennen'],
        ['move', 'Verschieben...'],
        ['copy', 'Kopieren...'],
    ];

    constructor(neuzeichnen) {
        //: Aufrufbar — die Liste neu aufbauen, nachdem sich etwas geändert hat.
        this.neuzeichnen = neuzeichnen;
        this.ziel = null;
    }

    // ------------------------------------------------------------ Kontextmenü

    /** Menü an der Mausstelle für dieses Kleidungsstück zeigen. */
    zeigen(x, y, stueck) {
        this.ziel = stueck;
        const menue = document.getElementById(Kleiderverwaltung.MENUE_ID)
            || this._menueBauen();
        menue.style.left = x + 'px';
        menue.style.top = y + 'px';
        menue.style.display = 'block';
    }

    _menueBauen() {
        const menue = document.createElement('div');
        menue.id = Kleiderverwaltung.MENUE_ID;
        menue.className = 'kld-ctx';
        menue.innerHTML = Kleiderverwaltung.AKTIONEN.map(
            ([aktion, text]) =>
                `<div class="ctx-item knopf-klein" data-action="${aktion}">${text}</div>`)
            .join('')
            + '<div class="kld-ctx-trenner"></div>'
            + '<div class="ctx-item kld-ctx-loeschen" data-action="delete">Löschen</div>';
        menue.querySelectorAll('.ctx-item').forEach(eintrag => {
            eintrag.addEventListener('click',
                                     () => this.ausfuehren(eintrag.dataset.action));
        });
        document.body.appendChild(menue);
        document.addEventListener('click', () => { menue.style.display = 'none'; },
                                  { capture: true });
        return menue;
    }

    // ---------------------------------------------------------------- Aktionen

    async ausfuehren(aktion) {
        const stueck = this.ziel;
        if (!stueck) return;
        const menue = document.getElementById(Kleiderverwaltung.MENUE_ID);
        if (menue) menue.style.display = 'none';
        const methode = { rename: 'umbenennen', move: 'verschieben',
                          copy: 'kopieren', delete: 'loeschen' }[aktion];
        if (methode) await this[methode](stueck);
    }

    async umbenennen(stueck) {
        const name = prompt('Neuer Name:', stueck.name || stueck.id);
        if (!name || name === stueck.name) return;
        if (await this._senden('rename', { id: stueck.id, new_name: name },
                               'Umbenennen')) {
            stueck.name = name;
            this.neuzeichnen();
        }
    }

    async verschieben(stueck) {
        const kategorien = [...new Set(state._garmentCatalog.map(x => x._category))];
        const ziel = prompt('Verschieben nach Kategorie:\n' + kategorien.join(', '),
                            stueck._category);
        if (!ziel || ziel === stueck._category) return;
        if (await this._senden('move', { id: stueck.id, target_category: ziel },
                               'Verschieben')) {
            stueck._category = ziel;
            this.neuzeichnen(ziel);
        }
    }

    async kopieren(stueck) {
        const name = prompt('Kopie-Name:', (stueck.name || stueck.id) + '_copy');
        if (!name) return;
        if (!await this._senden('copy', { id: stueck.id, new_name: name },
                               'Kopieren')) {
            return;
        }
        await Kleiderverwaltung.katalogNeuLaden();
        this.neuzeichnen();
    }

    async loeschen(stueck) {
        if (!confirm(`"${stueck.name || stueck.id}" wirklich löschen?`)) return;
        if (!await this._senden('delete', { id: stueck.id }, 'Löschen')) return;
        const stelle = state._garmentCatalog.indexOf(stueck);
        if (stelle >= 0) state._garmentCatalog.splice(stelle, 1);
        if (state._selectedKleiderId === stueck.id) state._selectedKleiderId = '';
        this.neuzeichnen();
    }

    // ------------------------------------------------------------------ Kanal

    async _senden(aktion, daten, wofuer) {
        try {
            await Serverabruf.senden(Kleiderverwaltung.ENDPUNKT,
                                     { action: aktion, ...daten });
            return true;
        } catch (fehler) {
            Protokoll.fehler('kleider', `${wofuer} fehlgeschlagen`, fehler);
            alert(`${wofuer} fehlgeschlagen: ${fehler.message}`);
            return false;
        }
    }

    /**
     * Den Katalog vom Server neu holen (siehe Klassendoku).
     *
     * Der Fänger gehört hierher, nicht zum Aufrufer: Nach „Kopieren" oder
     * „Löschen" ist die Änderung auf dem Server schon passiert. Ein Netzfehler
     * beim Nachladen darf die Liste dann nicht leeren und auch keine stille
     * „Unhandled promise rejection" hinterlassen — der alte Stand bleibt
     * stehen, bis der Katalog wieder erreichbar ist.
     */
    static async katalogNeuLaden() {
        let daten;
        try {
            daten = await Serverabruf.json('/api/character/garment/library/');
        } catch (fehler) {
            Protokoll.fehler('kleider', 'Katalog nicht neu ladbar', fehler);
            return;
        }
        state._garmentCatalog.length = 0;
        for (const kategorie of Object.keys(daten.garments || {})) {
            for (const stueck of daten.garments[kategorie]) {
                stueck._category = kategorie;
                state._garmentCatalog.push(stueck);
            }
        }
    }
}
