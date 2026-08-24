import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Menuemodelle — der Modell-Zweig des Menüs „Clip hinzufügen".
 *
 * Herausgelöst aus `zeitleiste_spurmenue.js` (372 Zeilen).
 *
 * **Hier wird bewusst NICHT gemerkt.** Die Liste kommt bei jedem Öffnen frisch
 * vom Server, damit eine gerade gespeicherte Figur sofort im Menü steht — der
 * Weg „Modell speichern, dann in die Zeitleiste ziehen" ist der übliche.
 *
 * `_currentPreset = null` setzt die Spur zurück: Sie merkt sich sonst, welche
 * Figur sie zuletzt gebaut hat, und ignoriert den neuen Clip.
 */
export class Menuemodelle {

    static ERSATZKOERPER = 'Female_Caucasian';

    constructor(menue) {
        this.menue = menue;
    }

    async fuellen() {
        let vorgaben;
        try {
            vorgaben = (await Serverabruf.json('/api/character/models/')).presets
                || [];
        } catch (fehler) {
            this.menue.hinweis('Fehler beim Laden: ' + fehler.message);
            return;
        }
        if (!vorgaben.length) {
            this.menue.hinweis('Keine Modelle in data/models/');
            return;
        }
        this.menue.leeren();
        for (const vorgabe of vorgaben) {
            this.menue.ziel.appendChild(this.menue.spureintrag(
                vorgabe.label || vorgabe.name, () => this._einfuegen(vorgabe)));
        }
    }

    _einfuegen(vorgabe) {
        pushUndo('Modell-Clip hinzufügen');
        const clip = new Clip(null, vorgabe.label || vorgabe.name,
                              this.menue.vorgabebilder, this.menue.fps);
        clip.type = 'model';
        clip.startFrame = this.menue.bild;
        clip.data = { preset: vorgabe.name,
                      bodyType: Menuemodelle.ERSATZKOERPER };
        this.menue.spur.clips.push(clip);
        this.menue.spur._currentPreset = null;
        fn.applyPlayhead();
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
    }
}
