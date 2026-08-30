import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Mhproxystand } from './mhproxy_stand.js';
import { Kleiderverwaltung } from './kleiderverwaltung.js';

/**
 * Das Rechtsklickmenü über einem Kleidungsstück der Proxy-Liste: Umbenennen,
 * Verschieben, Kopieren, Löschen.
 *
 * Aus mhproxy_liste.js herausgelöst (Umbau 27.08.2026). Das Neuzeichnen kommt
 * als Rückruf herein — ein Import von `_renderMHList` wäre ein Ringschluss.
 */
export class Mhproxymenue {
    /** Endpunkt, der alle vier Aktionen ausführt. */
    static ADRESSE = '/api/character/garment/manage/';

    /** Kleidungsstück, auf das zuletzt rechtsgeklickt wurde. */
    static ziel = null;
    /** Rückruf, der die Liste neu aufbaut. */
    static neuzeichnen = () => {};

    /**
     * @param {number} x
     * @param {number} y
     * @param {Object} stueck
     * @param {Function} neuzeichnen
     */
    static zeigen(x, y, stueck, neuzeichnen) {
        Mhproxymenue.ziel = stueck;
        Mhproxymenue.neuzeichnen = neuzeichnen;
        const menue = document.getElementById('mh-ctx-menu')
                      || Mhproxymenue._anlegen();
        menue.style.left = x + 'px';
        menue.style.top = y + 'px';
        menue.style.display = 'block';
    }

    static _anlegen() {
        const menue = document.createElement('div');
        menue.id = 'mh-ctx-menu';
        menue.className = 'ctx-menu';
        menue.classList.add('kontextmenue-schwebend');
        menue.innerHTML = `
            <div class="ctx-item knopf-klein" data-action="rename">Umbenennen</div>
            <div class="ctx-item knopf-klein" data-action="move">Verschieben...</div>
            <div class="ctx-item knopf-klein" data-action="copy">Kopieren...</div>
            <div class="hb-trennlinie"></div>
            <div class="ctx-item ctx-loeschen" data-action="delete">Löschen</div>
        `;
        menue.querySelectorAll('.ctx-item').forEach(eintrag => {
            eintrag.addEventListener('mouseenter',
                () => { eintrag.style.background = 'var(--accent)'; });
            eintrag.addEventListener('mouseleave',
                () => { eintrag.style.background = ''; });
            eintrag.addEventListener('click',
                () => Mhproxymenue._ausfuehren(eintrag.dataset.action));
        });
        document.body.appendChild(menue);
        document.addEventListener('click',
            () => { menue.style.display = 'none'; }, { capture: true });
        return menue;
    }

    static async _ausfuehren(aktion) {
        const stueck = Mhproxymenue.ziel;
        if (!stueck) return;
        const menue = document.getElementById('mh-ctx-menu');
        if (menue) menue.style.display = 'none';
        // Ausgeschrieben statt über eine Zuordnungstabelle: `jsfaenger` prüft,
        // ob ein Serveraufruf gedeckt ist, und findet den Aufrufer über den
        // Namen im Text. Eine Tabelle verbirgt ihn (Befund 27.08.2026).
        try {
            if (aktion === 'rename') await Mhproxymenue._umbenennen(stueck);
            else if (aktion === 'move') await Mhproxymenue._verschieben(stueck);
            else if (aktion === 'copy') await Mhproxymenue._kopieren(stueck);
            else if (aktion === 'delete') await Mhproxymenue._loeschen(stueck);
        } catch (e) {
            Protokoll.fehler('MH-Proxy', `${aktion} fehlgeschlagen:`, e);
        }
    }

    static async _umbenennen(stueck) {
        const name = prompt('Neuer Name:', stueck.name || stueck.id);
        if (!name || name === stueck.name) return;
        await Serverabruf.senden(Mhproxymenue.ADRESSE,
            { action: 'rename', id: stueck.id, new_name: name });
        stueck.name = name;
        Mhproxymenue.neuzeichnen();
    }

    static async _verschieben(stueck) {
        const kategorien = [...new Set(
            state._garmentCatalog.map(x => x._category))];
        const ziel = prompt('Verschieben nach Kategorie:\n'
                            + kategorien.join(', '), stueck._category);
        if (!ziel || ziel === stueck._category) return;
        await Serverabruf.senden(Mhproxymenue.ADRESSE,
            { action: 'move', id: stueck.id, target_category: ziel });
        stueck._category = ziel;
        // Sonst klappt die Liste in die alte Kategorie zurück und das
        // verschobene Stück ist scheinbar verschwunden.
        Mhproxystand.aufklappen(ziel);
        Mhproxymenue.neuzeichnen();
    }

    static async _kopieren(stueck) {
        const name = prompt('Kopie-Name:', (stueck.name || stueck.id) + '_copy');
        if (!name) return;
        await Serverabruf.senden(Mhproxymenue.ADRESSE,
            { action: 'copy', id: stueck.id, new_name: name });
        await Mhproxymenue._katalogNeuLaden();
        Mhproxymenue.neuzeichnen();
    }

    static async _loeschen(stueck) {
        if (!confirm(`"${stueck.name || stueck.id}" wirklich löschen?`)) return;
        await Serverabruf.senden(Mhproxymenue.ADRESSE,
            { action: 'delete', id: stueck.id });
        const stelle = state._garmentCatalog.indexOf(stueck);
        if (stelle >= 0) state._garmentCatalog.splice(stelle, 1);
        if (state._selectedMHId === stueck.id) state._selectedMHId = '';
        Mhproxymenue.neuzeichnen();
    }

    /** Die Kopie liegt nur auf dem Server — der Katalog muss frisch geholt werden. */
    static async _katalogNeuLaden() {
        Kleiderverwaltung.uebernehmen(
            await Serverabruf.json('/api/character/garment/library/'));
    }
}
