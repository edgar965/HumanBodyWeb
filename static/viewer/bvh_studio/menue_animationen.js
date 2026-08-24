import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Menueanimationen — der BVH-Zweig des Menüs „Clip hinzufügen".
 *
 * Herausgelöst aus `zeitleiste_spurmenue.js` (372 Zeilen). Zwei Eigenheiten:
 *
 * 1. **Die Animationsliste wird gemerkt** (`_gemerkt`). Sie hat über 7.000
 *    Einträge; jeder Rechtsklick würde sie sonst neu holen.
 * 2. **Ein eingefügter Clip wird auf zehn Sekunden beschnitten** — über
 *    `trimOut`, nicht durch Kürzen der Daten. Ein 40-Sekunden-Clip würde sonst
 *    die halbe Zeitleiste füllen; ziehen kann man ihn danach wieder auf.
 */
export class Menueanimationen {

    /** Einmal geholt, dann gemerkt. */
    static _gemerkt = null;

    static vergessen() {
        Menueanimationen._gemerkt = null;
    }

    constructor(menue) {
        this.menue = menue;
    }

    async fuellen() {
        const kategorien = await this._kategorien();
        if (!kategorien) return;
        const namen = Object.keys(kategorien).sort();
        if (!namen.length) {
            this.menue.hinweis('Keine Animationen verfügbar');
            return;
        }
        this.menue.leeren();
        for (const name of namen) {
            this.menue.ziel.appendChild(
                this._ordner(name, kategorien[name] || []));
        }
    }

    async _kategorien() {
        if (!Menueanimationen._gemerkt) {
            try {
                Menueanimationen._gemerkt = await Serverabruf.json(
                    '/api/character/animations/');
            } catch (fehler) {
                this.menue.hinweis('Fehler beim Laden');
                return null;
            }
        }
        return Menueanimationen._gemerkt.categories || {};
    }

    _ordner(name, animationen) {
        const kopf = this.menue.eintrag({
            symbol: 'fa-folder', farbe: this.menue.constructor.ORDNER_FARBE,
            text: name,
            rechts: `${animationen.length} <i class="fas fa-caret-right"></i>`,
            klasse: 'has-submenu',
        }, null);
        const unter = this.menue.untermenue(kopf);
        if (!animationen.length) {
            unter.innerHTML = '<div class="ctx-submenu-empty">Leer</div>';
        }
        for (const animation of animationen) {
            unter.appendChild(this.menue.eintrag({
                symbol: 'fa-running', text: animation.name,
                rechts: (animation.frames || '?') + 'f',
            }, () => this._einfuegen(name, animation)));
        }
        return kopf;
    }

    async _einfuegen(kategorie, animation) {
        await fn.addClipToTrack(this.menue.nummer, kategorie, animation.name,
                                animation.frames || 0);
        const spur = state.project.tracks[this.menue.nummer];
        const clip = spur.clips[spur.clips.length - 1];
        if (!clip) return;
        // Vorgabe sind zehn Sekunden — laengere Animationen werden beschnitten,
        // kuerzere bleiben, wie sie sind.
        const grenze = Math.round(this.menue.vorgabesekunden * clip.fps);
        if (clip.totalFrames > grenze) clip.trimOut = clip.totalFrames - grenze;
        clip.startFrame = this.menue.bild;
        fn.updateDuration();
        fn.renderTimeline();
    }
}
