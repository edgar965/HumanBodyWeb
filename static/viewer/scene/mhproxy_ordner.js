import { state } from './state.js';
import { Bildnachlader } from '../gemeinsam/bildnachlader.js';
import { Mhproxystand } from './mhproxy_stand.js';

/**
 * Ein Kategorieordner der Proxy-Liste mit seinen Kleidungsstücken.
 *
 * Aus mhproxy_liste.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`:
 * `_renderMHList()` hatte 90 Zeilen).
 */
export class Mhproxyordner {
    static ZU = '▶';
    static AUF = '▼';
    /** Kantenlänge des Vorschaubilds in Pixeln. */
    static BILD_PX = 36;

    /**
     * @param {Array} stuecke
     * @returns {Object<string, Array>} Kategorie -> Kleidungsstücke
     */
    static gruppieren(stuecke) {
        const nach = {};
        for (const stueck of stuecke) {
            if (!nach[stueck._category]) nach[stueck._category] = [];
            nach[stueck._category].push(stueck);
        }
        return nach;
    }

    /**
     * @param {string} kategorie
     * @param {Array} stuecke
     * @param {HTMLElement} liste die umgebende Liste (für die Auswahlmarke)
     * @param {Function} aufKontextmenue (x, y, stueck) => void
     * @returns {HTMLElement}
     */
    static element(kategorie, stuecke, liste, aufKontextmenue) {
        const ordner = document.createElement('div');
        ordner.className = 'anim-folder';
        ordner.innerHTML = '<div class="anim-folder-header">'
            + `<span class="chevron">${Mhproxyordner.AUF}</span> `
            + `${kategorie} (${stuecke.length})</div>`;
        const rumpf = document.createElement('div');
        rumpf.className = 'anim-folder-body';

        // Nur die zuletzt benutzte Kategorie steht offen — bei 125 Stücken
        // wären sonst alle Vorschaubilder auf einmal fällig.
        const offen = Mhproxystand.offeneKategorie === kategorie;
        rumpf.style.display = offen ? '' : 'none';
        ordner.querySelector('.chevron').textContent =
            offen ? Mhproxyordner.AUF : Mhproxyordner.ZU;

        for (const stueck of stuecke) {
            rumpf.appendChild(Mhproxyordner._zeile(stueck, kategorie, liste,
                                                   aufKontextmenue));
        }
        ordner.appendChild(rumpf);
        Mhproxyordner._klappen(ordner, rumpf, kategorie);
        return ordner;
    }

    static _klappen(ordner, rumpf, kategorie) {
        const kopf = ordner.querySelector('.anim-folder-header');
        kopf.addEventListener('click', () => {
            const aufgehen = rumpf.style.display === 'none';
            rumpf.style.display = aufgehen ? '' : 'none';
            kopf.querySelector('.chevron').textContent =
                aufgehen ? Mhproxyordner.AUF : Mhproxyordner.ZU;
            if (aufgehen) Mhproxystand.aufklappen(kategorie);
        });
    }

    static _zeile(stueck, kategorie, liste, aufKontextmenue) {
        const zeile = document.createElement('div');
        zeile.className = 'anim-item';
        zeile.dataset.garmentId = stueck.id;
        zeile.style.cssText = 'display:flex;align-items:center;gap:6px;'
            + 'padding:4px 8px;cursor:pointer;';
        if (state._selectedMHId === stueck.id) zeile.classList.add('selected');
        if (stueck.has_thumb) zeile.appendChild(Mhproxyordner._bild(stueck));
        zeile.appendChild(Mhproxyordner._name(stueck));
        zeile.addEventListener('click', () => {
            Mhproxyordner._waehlen(stueck, liste, zeile);
            Mhproxystand.aufklappen(kategorie);
        });
        zeile.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            Mhproxyordner._waehlen(stueck, liste, zeile);
            aufKontextmenue(e.clientX, e.clientY, stueck);
        });
        return zeile;
    }

    static _bild(stueck) {
        const bild = document.createElement('img');
        // Erst beim Aufklappen laden — 4,77 MB und 125 Anfragen weniger je
        // Seitenaufruf (siehe Bildnachlader).
        Bildnachlader.vormerken(bild,
                                `/api/character/garment/thumb/${stueck.id}/`);
        bild.style.cssText = `width:${Mhproxyordner.BILD_PX}px;`
            + `height:${Mhproxyordner.BILD_PX}px;border-radius:3px;`
            + 'object-fit:cover;flex-shrink:0;';
        return bild;
    }

    static _name(stueck) {
        const name = document.createElement('span');
        name.textContent = stueck.name || stueck.id;
        name.style.cssText = 'font-size:0.8rem;overflow:hidden;'
            + 'text-overflow:ellipsis;white-space:nowrap;';
        return name;
    }

    static _waehlen(stueck, liste, zeile) {
        state._selectedMHId = stueck.id;
        liste.querySelectorAll('.anim-item')
             .forEach(el => el.classList.remove('selected'));
        zeile.classList.add('selected');
    }
}
