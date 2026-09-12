import { Figurwahldialog } from '../../viewer/gemeinsam/figurwahldialog.js';

/**
 * Modellwahl — „Modell wählen …" auf der Seite „Effekte".
 *
 * Edgar, 12.09.2026: „… und ein Modell auswahl dialog". Es ist DERSELBE
 * Dialog wie „Charakter hinzufügen" in der Szene und „Modell laden" im
 * Theatre (`gemeinsam/figurwahldialog.js`), nur mit dem Reiter „HumanBody"
 * allein und ohne Lage-Felder: Die Figur-Pipeline nimmt gespeicherte
 * Modelle der Szene (`HumanBody/data/models/<name>.json`), nichts anderes.
 *
 * Was ein Modell mitbringt (Körpertyp, GarmentCode-Stücke, Frisur), steht
 * als JSON in der Seite (`#effektModelle`, aus `Effektquellen.modelle()`)
 * und wird nach der Wahl unter dem Namen gezeigt — der Film nimmt genau
 * das: nur GarmentCode-Stücke, die Frisur starr am Kopf.
 */
export class Modellwahl {

    /**
     * @param {HTMLElement} kasten   `#effektModell` (data-name, Name, Meta)
     * @param {Array} modelle        Einträge aus `Effektquellen.modelle()`
     * @param {Function} beimWaehlen (name) => …
     */
    constructor(kasten, modelle, beimWaehlen) {
        this.kasten = kasten;
        this.modelle = modelle || [];
        this.beimWaehlen = beimWaehlen;
        this.dialog = new Figurwahldialog({
            lader: { modell: async (name) => this.waehlen(name) },
            quellen: ['modell'],
            titel: 'Modell wählen',
            knopf: 'Übernehmen',
            symbol: 'fa-user',
            lage: false,
            kennung: 'effekt-modell-dialog',
        });
    }

    oeffnen() {
        return this.dialog.oeffnen();
    }

    /** Der gewählte Name — '' ohne Wahl. */
    name() {
        return this.kasten.dataset.name || '';
    }

    eintrag(name) {
        return this.modelle.find(m => m.name === name) || null;
    }

    waehlen(name) {
        const modell = this.eintrag(name);
        this.kasten.dataset.name = name;
        this.kasten.querySelector('#effektModellName').textContent = name;
        this.kasten.querySelector('#effektModellMeta').textContent =
            modell ? Modellwahl.beschreibung(modell) : 'Modelldatei ohne lesbare Angaben';
        this.beimWaehlen(name);
        return name;
    }

    /** „Female_Caucasian · 12 Morphs · t-shirt-anliegend, hose · Frisur Ballerina". */
    static beschreibung(modell) {
        const teile = [modell.koerpertyp || '?', `${modell.morphs || 0} Morphs`];
        teile.push((modell.stuecke || []).length
            ? modell.stuecke.join(', ') : 'keine GarmentCode-Stücke (Figur unbekleidet)');
        teile.push(modell.frisur ? `Frisur ${modell.frisur}` : 'ohne Frisur');
        return teile.join(' · ');
    }
}
