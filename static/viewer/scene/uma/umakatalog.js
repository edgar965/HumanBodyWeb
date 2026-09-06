import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { escapeHtml, generateCharacterId } from '../utils.js';
import { markDirty } from '../undo.js';
import { UmaFigur } from './umafigur.js';
import { Figurplatzierung } from '../figurplatzierung.js';

/**
 * Umakatalog — die UMA-Figuren aus `Figuren/uma/` anbieten und in die Szene stellen.
 *
 * Gegenstück zu `addCharacterFromPreset` (HumanBody-Modelle) in
 * `charakterliste.js`; der Dialog „Charakter hinzufügen" zeigt beide Listen.
 */
export class Umakatalog {

    static ADRESSE = '/api/character/uma-figur/';

    static async liste() {
        const daten = await Serverabruf.json(Umakatalog.ADRESSE);
        return daten.figuren || [];
    }

    /**
     * Eine Figur laden, in die Szene stellen und auswählen.
     *
     * `lage` kommt aus dem Dialog (`Charakterdialog.lage`); ohne sie gelten
     * die Vorgaben: 1,5 m rechts neben der vorhandenen Figur und auf deren
     * Höhe. Skaliert wird NACH `load()` — vorher hat die Figur keine Größe,
     * die man messen könnte.
     */
    static async hinzufuegen(datei, lage = null) {
        const id = generateCharacterId();
        const figur = new UmaFigur(id, { datei });
        await figur.load();
        Figurplatzierung.anwenden(figur, lage);
        state.characters.set(id, figur);
        state.scene.add(figur.group);
        fn.updateCharacterListUI();
        fn.updateVertexCount();
        fn.selectCharacter(id);
        markDirty();
        return figur;
    }

    /** Die Liste im Dialog füllen; `beimWaehlen(datei)` bei Klick, Doppelklick lädt sofort. */
    static async fuellen(liste, beimWaehlen, beimLaden) {
        liste.innerHTML = '<li class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade Katalog...</li>';
        let figuren;
        try {
            figuren = await Umakatalog.liste();
        } catch (fehler) {
            liste.innerHTML = `<li class="fehlertext">Fehler: ${escapeHtml(fehler.message)}</li>`;
            return;
        }
        liste.innerHTML = '';
        if (figuren.length === 0) {
            liste.innerHTML = '<li class="gedaempft">Keine UMA-Figur im Katalog (Figuren/uma/).</li>';
            return;
        }
        for (const figur of figuren) {
            const li = document.createElement('li');
            const mb = (figur.bytes / 1048576).toFixed(1);
            const unterzeile = `${escapeHtml(figur.geschlecht)} · ${mb} MB · ${escapeHtml(figur.stand)}`;
            li.innerHTML = `${escapeHtml(figur.name.replace(/\.glb$/i, ''))}`
                + `<span class="preset-sub">${unterzeile}</span>`;
            li.dataset.datei = figur.name;
            li.addEventListener('click', () => {
                liste.querySelectorAll('li').forEach(x => x.classList.remove('selected'));
                li.classList.add('selected');
                beimWaehlen(figur.name);
            });
            li.addEventListener('dblclick', () => beimLaden(figur.name));
            liste.appendChild(li);
        }
    }
}

fn.addUmaFigur = Umakatalog.hinzufuegen;
