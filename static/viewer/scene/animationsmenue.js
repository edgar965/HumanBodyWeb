import { Serverabruf } from '../gemeinsam/serverabruf.js';

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
    static KENNUNG = 'anim-ctx';

    /** Das Menü an eine Baumzeile hängen. */
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

    static zeigen(x, y, kategorie, name, danach) {
        const menue = Animationsmenue._menue();
        menue.innerHTML = '';
        menue.appendChild(Animationsmenue._eintrag(
            'fa-pen', 'Umbenennen',
            () => Animationsmenue.umbenennen(kategorie, name, danach)));
        menue.appendChild(Animationsmenue._eintrag(
            'fa-arrows-alt', 'Verschieben nach …',
            () => Animationsmenue.verschieben(kategorie, name, danach)));
        menue.appendChild(Animationsmenue._eintrag(
            'fa-trash', 'Löschen',
            () => Animationsmenue.loeschen(kategorie, name, danach)));
        // Erst messen, dann setzen: Am rechten Rand liefe das Menü sonst aus
        // dem Fenster und die Einträge wären nicht erreichbar.
        menue.style.left = '0px';
        menue.style.top = '0px';
        menue.style.display = 'block';
        const breite = menue.offsetWidth;
        const hoehe = menue.offsetHeight;
        menue.style.left = `${Math.min(x, window.innerWidth - breite - 4)}px`;
        menue.style.top = `${Math.min(y, window.innerHeight - hoehe - 4)}px`;
        Animationsmenue._schliessenBeiKlick();
    }

    static verbergen() {
        const menue = document.getElementById(Animationsmenue.KENNUNG);
        if (menue) menue.style.display = 'none';
    }

    static async umbenennen(kategorie, name, danach) {
        Animationsmenue.verbergen();
        const neu = prompt(`Neuer Name für „${name}":`, name);
        if (!neu || neu === name) return false;
        if (!await Animationsmenue._senden('rename', {
                category: kategorie, name, new_name: neu })) {
            return false;
        }
        if (danach) danach();
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
        Animationsmenue.verbergen();
        const ziel = await Animationsmenue._ordnerWaehlen(kategorie, name);
        if (!ziel || ziel === kategorie) return false;
        if (!await Animationsmenue._senden('move', {
                category: kategorie, name, new_category: ziel })) {
            return false;
        }
        if (danach) danach();
        return true;
    }

    static async loeschen(kategorie, name, danach) {
        Animationsmenue.verbergen();
        if (!confirm(`„${name}" aus „${kategorie}" endgültig löschen?\n\n`
                     + 'Die BVH-Datei wird von der Platte entfernt.')) {
            return false;
        }
        if (!await Animationsmenue._senden('delete',
                                           { category: kategorie, name })) {
            return false;
        }
        if (danach) danach();
        return true;
    }

    static async _senden(aktion, daten) {
        try {
            await Serverabruf.senden(Animationsmenue.ENDPUNKT,
                                     { action: aktion, ...daten });
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

    /**
     * Das Auswahlfenster. Liefert den Zielordner oder `null`.
     *
     * Kein `<dialog>`: Die Seite läuft mit einem eigenen Fensterstil, und ein
     * modales `dialog` legt sich über die Szene, während man noch sehen will,
     * welche Figur gewählt ist.
     */
    static _ordnerWaehlen(kategorie, name) {
        return new Promise((fertig) => {
            const hinter = document.createElement('div');
            // Die Klassen der Seite, nicht eigene: `.scene-modal-overlay`
            // und `.scene-modal` sind in `scene_config.html` gestaltet. Ein
            // eigener Kasten hätte kein Aussehen — weisser Text auf weissem
            // Grund, und niemand sieht, warum.
            hinter.className = 'scene-modal-overlay visible';
            hinter.innerHTML = `
                <div class="scene-modal">
                  <div class="scene-modal-header">
                    <h4><i class="fas fa-arrows-alt"></i> Verschieben</h4>
                    <button class="scene-modal-close" data-ab>&times;</button>
                  </div>
                  <div class="scene-modal-body">
                    <div class="dialoghinweis" data-titel></div>
                    <select class="viewer-select hb-dehnt-ohne-abstand"
                            data-liste></select>
                    <input class="scene-name-input hb-versteckt" type="text"
                           data-neu placeholder="Name des neuen Ordners">
                  </div>
                  <div class="scene-modal-footer">
                    <button data-ab>Abbrechen</button>
                    <button class="primary" data-ok>Verschieben</button>
                  </div>
                </div>`;
            const nimm = (was) => hinter.querySelector(`[${was}]`);
            // Der Name kommt aus einem Verzeichnis auf der Platte — als
            // TEXT setzen, nicht als HTML.
            nimm('data-titel').textContent = `„${name}" liegt in „${kategorie}"`;
            const liste = nimm('data-liste');
            const feld = nimm('data-neu');
            for (const ordner of Animationsmenue.ordner()) {
                const eintrag = document.createElement('option');
                eintrag.value = ordner;
                eintrag.textContent = ordner
                    + (ordner === kategorie ? ' (aktuell)' : '');
                eintrag.disabled = ordner === kategorie;
                liste.appendChild(eintrag);
            }
            const neuer = document.createElement('option');
            neuer.value = '__neu__';
            neuer.textContent = 'Neuer Ordner …';
            liste.appendChild(neuer);
            liste.addEventListener('change', () => {
                feld.classList.toggle('hb-versteckt', liste.value !== '__neu__');
                if (liste.value === '__neu__') feld.focus();
            });
            document.body.appendChild(hinter);
            const schliessen = (wert) => { hinter.remove(); fertig(wert); };
            nimm('data-ok').addEventListener('click', () => schliessen(
                liste.value === '__neu__' ? feld.value.trim() : liste.value));
            for (const knopf of hinter.querySelectorAll('[data-ab]')) {
                knopf.addEventListener('click', () => schliessen(null));
            }
            // Ein Klick auf den Hintergrund bricht ab, einer im Kasten nicht.
            hinter.addEventListener('click', (ereignis) => {
                if (ereignis.target === hinter) schliessen(null);
            });
            liste.focus();
        });
    }

    // -- Bausteine ------------------------------------------------------------

    /** Der eine Menükasten dieser Seite — angelegt, wenn es ihn nicht gibt. */
    static _menue() {
        let menue = document.getElementById(Animationsmenue.KENNUNG);
        if (menue) return menue;
        menue = document.createElement('div');
        menue.id = Animationsmenue.KENNUNG;
        menue.className = 'hb-kontextmenue';
        menue.style.display = 'none';
        document.body.appendChild(menue);
        return menue;
    }

    static _eintrag(symbol, text, tun) {
        const zeile = document.createElement('div');
        zeile.className = 'hb-menueeintrag';
        zeile.innerHTML = `<i class="fas ${symbol} hb-symbolspalte"></i> `;
        zeile.appendChild(document.createTextNode(text));
        zeile.addEventListener('click', tun);
        return zeile;
    }

    /**
     * Ein Klick daneben schliesst das Menü.
     *
     * `{ once: true }` und ein Aufschub um einen Zyklus: Ohne ihn fängt
     * derselbe Klick, der das Menü öffnet, den Schliesser gleich mit ab —
     * das Menü blitzt auf und ist weg.
     */
    static _schliessenBeiKlick() {
        setTimeout(() => {
            document.addEventListener('click', () => Animationsmenue.verbergen(),
                                      { once: true });
        }, 0);
    }
}
