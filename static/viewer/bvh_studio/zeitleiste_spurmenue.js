/**
 * Spurmenue — das Untermenü „Clip hinzufügen" einer Spur.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026), am 16.08.2026 in eine
 * Klasse umgebaut. Vorher: eine Funktion mit 244 Zeilen und einer
 * `if/else if`-Kette ueber sieben Spurtypen. Darin dreimal dasselbe Muster —
 *
 *   * ACHTMAL "Element anlegen, Klasse setzen, innerHTML mit Symbol und
 *     Inline-Stil, Klick-Zuhoerer" -> jetzt `eintrag()`,
 *   * ZWEIMAL das Positionieren eines Untermenues beim Ueberfahren
 *     (getBoundingClientRect, left/top) -> jetzt `untermenue()`,
 *   * in jedem Zweig `sub.innerHTML = ''` und eine eigene Leer-Meldung.
 *
 * Die Symbolfarben standen als Inline-Stil in jedem innerHTML; sie sind jetzt
 * benannte Konstanten und gehen ueber eine CSS-Variable in die Vorlage.
 *
 * UMBAU 18.08.2026: 372 Zeilen. Die drei grossen Zweige stehen jetzt je in
 * einer eigenen Klasse — `menue_animationen.js`, `menue_modelle.js`,
 * `menue_licht.js`. Der Ton-Zweig ist ganz entfallen: Er war eine Kopie von
 * `audiospur.js` (dekodieren, Clip bauen, hochladen) und ruft die jetzt auf.
 * Hier bleiben Aufbau, Bausteine und der Verteiler.
 */

import { state } from './state.js';
import { Menueanimationen } from './menue_animationen.js';
import { Menuemodelle } from './menue_modelle.js';
import { Menuelicht } from './menue_licht.js';
import { Audiospur } from './audiospur.js';
import { fn } from '../gemeinsam/registrierung.js';

export const DEFAULT_CLIP_SECONDS = 10;

export class Spurmenue {

    /** Symbol und Farbe je Spurtyp. */
    static SYMBOLE = {
        bvh: ['fa-running', null],
        model: ['fa-user', '#e91e63'],
        audio: ['fa-music', '#4caf50'],
        scene_object: ['fa-cube', '#7c5cbf'],
        camera: ['fa-video', '#00bcd4'],
        light: ['fa-lightbulb', '#ffc107'],
    };
    static ORDNER_FARBE = 'var(--text-muted)';
    /** Ein Untermenü sitzt fünf Pixel höher als sein Elternteil. */
    static VERSATZ_Y = 5;

    /**
     * @param {Object} spur       die Spur aus dem Projekt
     * @param {number} nummer     ihr Index
     * @param {HTMLElement} ctx   das Kontextmenü (wird beim Klick geschlossen)
     * @param {number} zielbild   Bildnummer, an der der Clip liegen soll
     */
    constructor(spur, nummer, ctx, zielbild) {
        this.spur = spur;
        this.nummer = nummer;
        this.ctx = ctx;
        this.fps = state.project.fps;
        this.vorgabesekunden = DEFAULT_CLIP_SECONDS;
        this.vorgabebilder = DEFAULT_CLIP_SECONDS * this.fps;
        this.bild = (zielbild != null) ? zielbild : state.playheadFrame;
        this.ziel = null;
    }

    /** Menü aufbauen. Der Verteiler auf die Spurtypen. */
    async fuellen(untermenueId = 'track-ctx-add-submenu') {
        this.ziel = document.getElementById(untermenueId);
        if (!this.ziel) return;
        this.hinweis('Lade...');
        const wege = {
            bvh: () => new Menueanimationen(this).fuellen(),
            model: () => new Menuemodelle(this).fuellen(),
            audio: () => this._ton(),
            scene_object: () => this._einzeleintrag('3D-Datei wählen...',
                () => fn.addSceneObjectClip?.(this.nummer, this.bild)),
            camera: () => this._einzeleintrag('Kameraposition',
                () => fn.addCameraKeyframe(this.nummer, this.bild)),
            light: () => new Menuelicht(this).fuellen(),
        };
        const weg = wege[this.spur.type];
        if (!weg) {
            this.hinweis('Nicht verfügbar für diesen Spurtyp');
            return;
        }
        await weg();
    }

    // ------------------------------------------------------------- Bausteine

    hinweis(text) {
        this.ziel.innerHTML = `<div class="ctx-submenu-empty">${text}</div>`;
    }

    leeren() {
        this.ziel.innerHTML = '';
    }

    _schliessen() {
        this.ctx.style.display = 'none';
    }

    /**
     * Ein Menüeintrag. Ersetzt acht gleich gebaute Bloecke.
     * @param {Object} angaben { symbol, farbe, text, rechts, titel, klasse }
     * @param {Function} beiKlick
     */
    eintrag(angaben, beiKlick) {
        const { symbol, farbe, text, rechts, titel, klasse } = angaben;
        const element = document.createElement('div');
        element.className = 'ctx-item' + (klasse ? ' ' + klasse : '');
        const stil = farbe ? ` style="--ctx-symbolfarbe:${farbe};"` : '';
        element.innerHTML = `<i class="fas ${symbol} ctx-symbol"${stil}></i> ${text}`
            + (rechts ? `<span class="ctx-rechts">${rechts}</span>` : '');
        if (titel) element.title = titel;
        if (beiKlick) {
            element.addEventListener('click', async () => {
                this._schliessen();
                await beiKlick();
            });
        }
        return element;
    }

    /** Eintrag mit dem Symbol seines Spurtyps. */
    spureintrag(text, beiKlick, zusatz = {}) {
        const [symbol, farbe] = Spurmenue.SYMBOLE[this.spur.type]
            || ['fa-plus', null];
        return this.eintrag({ symbol, farbe, text, ...zusatz }, beiKlick);
    }

    /**
     * Ein Untermenü anhängen, das beim Überfahren neben seinem Elternteil
     * erscheint. `position: fixed` ist noetig, weil das Menue der ersten Ebene
     * `overflow: auto` hat und das Untermenue sonst abgeschnitten wuerde.
     */
    untermenue(elternteil) {
        const feld = document.createElement('div');
        feld.className = 'ctx-submenu ctx-submenu-fixed';
        elternteil.appendChild(feld);
        elternteil.addEventListener('mouseenter', () => {
            const rahmen = elternteil.getBoundingClientRect();
            feld.style.left = rahmen.right + 'px';
            feld.style.top = (rahmen.top - Spurmenue.VERSATZ_Y) + 'px';
        });
        return feld;
    }

    // ------------------------------------------------- Zweige mit einem Eintrag

    _einzeleintrag(text, beiKlick) {
        this.leeren();
        this.ziel.appendChild(this.spureintrag(text, beiKlick));
    }

    /** Ton: Auswahl öffnen, Clip auf die Vorgabelänge begrenzen. */
    _ton() {
        this._einzeleintrag('Audio-Datei wählen...', () =>
            Audiospur.dateiWaehlen(this.nummer, {
                startbild: this.bild,
                bilder: this.vorgabebilder,
                hoechstdauer: DEFAULT_CLIP_SECONDS,
                undoText: 'Audio-Clip hinzufügen',
            }));
    }
}

/**
 * Bisherige Aufrufform. Die Zeitleiste ruft sie an mehreren Stellen auf,
 * deshalb bleibt sie als Huelle.
 */
export async function _populateTrackAddSubmenu(track, trackIdx, ctx, targetFrame,
                                               submenuId = 'track-ctx-add-submenu') {
    return new Spurmenue(track, trackIdx, ctx, targetFrame).fuellen(submenuId);
}
