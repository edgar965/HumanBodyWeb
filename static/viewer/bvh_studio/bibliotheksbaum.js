import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Menueanimationen } from './menue_animationen.js';
import { Bibliothekskanal } from '../gemeinsam/bibliothekskanal.js';
import { Clipfehlt } from './clipfehlt.js';

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
        // Ein anderer Tab hat gelöscht, umbenannt, gespeichert (16.09.2026).
        // Bei einer Umbenennung zusätzlich DIESES Projekts eigene Clips
        // umstellen, statt sie beim nächsten Laden als 404 zu verlieren
        // (Edgar, 24.09.2026: „sofort im UI sichtbar").
        Bibliothekskanal.hoeren((meldung) => {
            if (meldung.aktion === 'rename' && meldung.category
                    && meldung.name && meldung.new_name) {
                Clipfehlt.umbenannt(meldung.category, meldung.name, meldung.new_name, state, fn);
            }
            this.laden();
        });
    }

    /**
     * Einen Eintrag sofort aus dem Baum nehmen — der Server hat das Löschen
     * bestätigt, und das Neuladen kann unter Last Sekunden dauern (gemessen
     * 9 s am 16.09.2026); so lange stand der gelöschte Eintrag noch da.
     */
    eintragEntfernen(kategorie, name) {
        const baum = document.getElementById('lib-tree');
        for (const zeile of baum?.querySelectorAll('.lib-item') || []) {
            if (zeile.dataset.category === kategorie && zeile.dataset.name === name) {
                zeile.remove();
            }
        }
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

    /**
     * Baum neu aufbauen. `nachher` wählt einen Eintrag danach aus.
     *
     * Mit jedem Neubau vergisst auch das Menü „Clip hinzufügen" seine Liste
     * (Edgar, 13.09.2026: „bei jedem Refresh soll der Ordner neu refresht
     * werden, so dass ich nicht auf eine Animation klicken kann die es nicht
     * gibt") — es merkte sie sich seit dem ersten Öffnen für die ganze Sitzung,
     * auch über Umbenennen, Verschieben und Löschen in der Bibliothek hinweg.
     */
    async laden(nachher) {
        if (nachher) this.auswahl = nachher;
        Menueanimationen.vergessen();
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
