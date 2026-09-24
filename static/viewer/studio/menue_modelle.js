import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Figurkataloge } from '../gemeinsam/figurkataloge.js';

/**
 * Menuemodelle — der Modell-Zweig des Menüs „Modell hinzufügen".
 *
 * Herausgelöst aus `zeitleiste_spurmenue.js` (372 Zeilen). Seit 15.09.2026
 * (Edgar: „bei Modell hinzufügen, mach das unterteilt, in HumanBody, UMA,
 * MakeHuman usw") ein Ordner je Figurart — dieselben sechs wie im Dialog
 * „Charakter hinzufügen" der Szene (`Figurkataloge.REIHENFOLGE`) — und darin
 * der Katalog der Art. Ein Klick legt einen Modellclip mit `quelle`; die
 * Figur baut `Spurfigurarten` nach dieser Quelle.
 *
 * **Hier wird bewusst NICHT gemerkt.** Die Listen kommen bei jedem Öffnen
 * frisch vom Server, damit eine gerade gespeicherte Figur sofort im Menü
 * steht — der Weg „Modell speichern, dann in die Zeitleiste ziehen" ist der
 * übliche. Die fünf Abrufe laufen nebeneinander; jeder Ordner füllt sich,
 * sobald seine Liste da ist.
 *
 * `_currentPreset = null` setzt die Spur zurück: Sie merkt sich sonst, welche
 * Figur sie zuletzt gebaut hat, und ignoriert den neuen Clip.
 */
export class Menuemodelle {

    static ERSATZKOERPER = 'Female_Caucasian';
    static SYMBOLE = { modell: 'fa-user', smpl: 'fa-child', makehuman: 'fa-user-alt',
                       uma: 'fa-user-astronaut', umapython: 'fa-user-cog',
                       genesis9: 'fa-user-tie' };

    constructor(menue) {
        this.menue = menue;
    }

    async fuellen() {
        this.menue.leeren();
        const wartend = [];
        for (const quelle of Figurkataloge.REIHENFOLGE) {
            const angaben = Figurkataloge.QUELLEN[quelle];
            const kopf = this.menue.eintrag({
                symbol: Menuemodelle.SYMBOLE[quelle] || 'fa-user',
                farbe: this.menue.constructor.SYMBOLE.model[1],
                text: angaben.titel,
                rechts: '<i class="fas fa-caret-right"></i>',
                klasse: 'has-submenu',
            }, null);
            const unter = this.menue.untermenue(kopf);
            unter.innerHTML = '<div class="ctx-submenu-empty">Lade...</div>';
            this.menue.ziel.appendChild(kopf);
            wartend.push(this._ordnerFuellen(quelle, unter, angaben));
        }
        await Promise.all(wartend);
    }

    async _ordnerFuellen(quelle, unter, angaben) {
        let zeilen;
        try {
            zeilen = await Figurkataloge.liste(quelle);
        } catch (fehler) {
            unter.innerHTML = `<div class="ctx-submenu-empty">Fehler: ${fehler.message}</div>`;
            return;
        }
        if (!zeilen.length) {
            unter.innerHTML = `<div class="ctx-submenu-empty">${angaben.leer}</div>`;
            return;
        }
        unter.innerHTML = '';
        for (const zeile of zeilen) {
            unter.appendChild(this.menue.spureintrag(
                zeile.anzeige, () => this._einfuegen(quelle, zeile), { titel: zeile.unterzeile }));
        }
    }

    _einfuegen(quelle, zeile) {
        pushUndo('Modell-Clip hinzufügen');
        const clip = new Clip(null, zeile.anzeige, this.menue.bilderBisProjektende, this.menue.fps);
        clip.type = 'model';
        clip.startFrame = this.menue.bild;
        clip.data = { preset: zeile.name, quelle,
                      bodyType: Menuemodelle.ERSATZKOERPER };
        this.menue.spur.clips.push(clip);
        this.menue.spur._currentPreset = null;
        fn.applyPlayhead();
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
    }
}
