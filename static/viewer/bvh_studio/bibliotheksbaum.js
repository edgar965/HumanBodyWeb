import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Bibliotheksbaum — der Ordnerbaum der BVH-Bibliothek in der Seitenleiste.
 *
 * Herausgelöst aus `library.js` (329 Zeilen). Der Zustand — welche Ordner offen
 * sind, was ausgewählt ist, worauf das Kontextmenü zeigt — lag dort in drei
 * Modulvariablen (`_libOpenCats`, `_libSelectedItem`, `_libCtxTarget`). Jetzt
 * sind es Felder EINER Instanz (Kriterium 9: geteilter Zustand gehört in eine
 * Klasse).
 *
 * WARUM DER OFFEN-ZUSTAND GEMERKT WIRD
 * ====================================
 * Der Baum wird nach jeder Dateioperation neu gebaut. Ohne das Merken klappten
 * alle Ordner zu, und nach jedem Umbenennen musste man sich neu durchklicken.
 * Gemerkt wird VOR dem Neubau aus dem DOM — so gehen auch Ordner mit, die der
 * Nutzer gerade von Hand geöffnet hat.
 */
export class Bibliotheksbaum {

    static QUELLE = '/api/character/animations/';

    constructor() {
        /** Offene Ordner (Kategorienamen). */
        this.offene = new Set();
        /** Ausgewählter Eintrag: `{category, name}` oder `null`. */
        this.auswahl = null;
        /** Worauf das Kontextmenü zeigt. */
        this.menueziel = null;
    }

    // -------------------------------------------------------------- Kontextmenü

    /** Ein Kontextmenü an der Mausstelle zeigen (alle anderen zu). */
    menueZeigen(menueId, x, y) {
        document.querySelectorAll('.lib-ctx').forEach(m => m.style.display = 'none');
        const menue = document.getElementById(menueId);
        if (!menue) return;
        menue.style.display = 'block';
        menue.style.left = x + 'px';
        menue.style.top = y + 'px';
    }

    // -------------------------------------------------------------------- Laden

    /** Baum neu aufbauen. `nachher` wählt einen Eintrag danach aus. */
    async laden(nachher) {
        if (nachher) this.auswahl = nachher;
        try {
            this.offeneMerken();
            const daten = await Serverabruf.json(Bibliotheksbaum.QUELLE);
            const baum = document.getElementById('lib-tree');
            if (!baum) return;
            baum.innerHTML = '';
            const kategorien = daten.categories || {};
            for (const name of Object.keys(kategorien).sort()) {
                baum.appendChild(this.kategorie(baum, name, kategorien[name]));
            }
        } catch (fehler) {
            Protokoll.fehler('BVH Studio', 'Library load failed', fehler);
        }
    }

    offeneMerken() {
        const baum = document.getElementById('lib-tree');
        if (!baum) return;
        baum.querySelectorAll('.lib-cat.open').forEach(element => {
            if (element.dataset.category) this.offene.add(element.dataset.category);
        });
    }

    // ----------------------------------------------------------------- Aufbau

    kategorie(baum, name, animationen) {
        const kasten = document.createElement('div');
        kasten.className = 'lib-cat';
        kasten.dataset.category = name;
        kasten.appendChild(this.kategoriekopf(kasten, name, animationen.length));
        if (this.offene.has(name)) kasten.classList.add('open');
        // Auch aufklappen, wenn die Auswahl darin liegt.
        if (this.auswahl && this.auswahl.category === name) kasten.classList.add('open');
        const koerper = document.createElement('div');
        koerper.className = 'lib-cat-body';
        for (const animation of animationen) {
            koerper.appendChild(this.eintrag(baum, name, animation));
        }
        kasten.appendChild(koerper);
        return kasten;
    }

    kategoriekopf(kasten, name, anzahl) {
        const kopf = document.createElement('div');
        kopf.className = 'lib-cat-header';
        kopf.innerHTML = '<span class="lib-chevron"><i class="fas fa-chevron-right"></i></span> '
            + `${name} <span class="lib-cat-anzahl">(${anzahl})</span>`;
        kopf.addEventListener('click', () => {
            kasten.classList.toggle('open');
            if (kasten.classList.contains('open')) this.offene.add(name);
            else this.offene.delete(name);
        });
        kopf.addEventListener('contextmenu', ereignis => {
            ereignis.preventDefault();
            this.menueziel = { type: 'folder', category: name };
            this.menueZeigen('lib-ctx-folder', ereignis.clientX, ereignis.clientY);
        });
        return kopf;
    }

    eintrag(baum, kategorie, animation) {
        const zeile = document.createElement('div');
        zeile.className = 'lib-item';
        zeile.dataset.category = kategorie;
        zeile.dataset.name = animation.name;
        zeile.textContent = `${animation.name} (${animation.frames || '?'}f)`;
        zeile.draggable = true;
        this.ziehenBinden(zeile, kategorie, animation);
        this.klickBinden(baum, zeile, kategorie, animation);
        if (this.auswahl && this.auswahl.category === kategorie
                && this.auswahl.name === animation.name) {
            zeile.classList.add('selected');
        }
        return zeile;
    }

    ziehenBinden(zeile, kategorie, animation) {
        zeile.addEventListener('dragstart', ereignis => {
            ereignis.dataTransfer.setData('application/json', JSON.stringify({
                category: kategorie, name: animation.name,
                frames: animation.frames || 0,
            }));
            zeile.classList.add('dragging');
        });
        zeile.addEventListener('dragend', () => zeile.classList.remove('dragging'));
    }

    klickBinden(baum, zeile, kategorie, animation) {
        zeile.addEventListener('dblclick', ereignis => {
            ereignis.preventDefault();
            ereignis.stopPropagation();
            fn.addClipToTrack(state.selectedTrackIdx, kategorie, animation.name,
                              animation.frames || 0);
        });
        zeile.addEventListener('click', () => this.auswaehlen(baum, zeile, kategorie,
                                                             animation));
        zeile.addEventListener('contextmenu', ereignis => {
            ereignis.preventDefault();
            ereignis.stopPropagation();
            this.auswaehlen(baum, zeile, kategorie, animation);
            this.menueziel = { type: 'file', category: kategorie,
                               name: animation.name, frames: animation.frames || 0 };
            this.menueZeigen('lib-ctx-file', ereignis.clientX, ereignis.clientY);
        });
    }

    auswaehlen(baum, zeile, kategorie, animation) {
        baum.querySelectorAll('.lib-item.selected')
            .forEach(element => element.classList.remove('selected'));
        zeile.classList.add('selected');
        this.auswahl = { category: kategorie, name: animation.name };
    }
}
