/**
 * Spurmenue — das Untermenü „Clip hinzufügen" einer Spur.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026), am 16.08.2026 in eine
 * Klasse umgebaut. Vorher: eine Funktion mit 244 Zeilen und einer
 * `if/else if`-Kette ueber sieben Spurtypen. Darin dreimal dasselbe Muster —
 *
 *   * ACHTMAL "Element anlegen, Klasse setzen, innerHTML mit Symbol und
 *     Inline-Stil, Klick-Zuhoerer" -> jetzt `_eintrag()`,
 *   * ZWEIMAL das Positionieren eines Untermenues beim Ueberfahren
 *     (getBoundingClientRect, left/top) -> jetzt `_untermenue()`,
 *   * in jedem Zweig `sub.innerHTML = ''` und eine eigene Leer-Meldung.
 *
 * Die Symbolfarben standen als Inline-Stil in jedem innerHTML; sie sind jetzt
 * benannte Konstanten und gehen ueber eine CSS-Variable in die Vorlage.
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { Clip } from './models.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/** Animationsliste wird gemerkt; Modelle immer frisch geholt (siehe _modell). */
export let _cachedAnimations = null;

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
        this.vorgabebilder = DEFAULT_CLIP_SECONDS * this.fps;
        this.bild = (zielbild != null) ? zielbild : state.playheadFrame;
        this.ziel = null;
    }

    /** Menü aufbauen. Der Verteiler auf die Spurtypen. */
    async fuellen(untermenueId = 'track-ctx-add-submenu') {
        this.ziel = document.getElementById(untermenueId);
        if (!this.ziel) return;
        this._laden();
        const wege = {
            bvh: () => this._bvh(),
            model: () => this._modell(),
            audio: () => this._ton(),
            scene_object: () => this._szenenobjekt(),
            camera: () => this._kamera(),
            light: () => this._licht(),
        };
        const weg = wege[this.spur.type];
        if (!weg) {
            this._hinweis('Nicht verfügbar für diesen Spurtyp');
            return;
        }
        await weg();
    }

    // ------------------------------------------------------------- Bausteine

    _laden() {
        this._hinweis('Lade...');
    }

    _hinweis(text) {
        this.ziel.innerHTML = `<div class="ctx-submenu-empty">${text}</div>`;
    }

    _leeren() {
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
    _eintrag(angaben, beiKlick) {
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
    _spureintrag(text, beiKlick, zusatz = {}) {
        const [symbol, farbe] = Spurmenue.SYMBOLE[this.spur.type] || ['fa-plus', null];
        return this._eintrag({ symbol, farbe, text, ...zusatz }, beiKlick);
    }

    /**
     * Ein Untermenü anhängen, das beim Überfahren neben seinem Elternteil
     * erscheint. `position: fixed` ist noetig, weil das Menue der ersten Ebene
     * `overflow: auto` hat und das Untermenue sonst abgeschnitten wuerde.
     */
    _untermenue(elternteil) {
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

    // --------------------------------------------------------- Spurtyp: BVH

    async _bvh() {
        if (!_cachedAnimations) {
            try {
                _cachedAnimations = await Serverabruf.json(
                    '/api/character/animations/');
            } catch (fehler) {
                this._hinweis('Fehler beim Laden');
                return;
            }
        }
        const kategorien = _cachedAnimations.categories || {};
        const namen = Object.keys(kategorien).sort();
        if (!namen.length) {
            this._hinweis('Keine Animationen verfügbar');
            return;
        }
        this._leeren();
        for (const name of namen) {
            const animationen = kategorien[name] || [];
            const kopf = this._eintrag({
                symbol: 'fa-folder', farbe: Spurmenue.ORDNER_FARBE, text: name,
                rechts: `${animationen.length} <i class="fas fa-caret-right"></i>`,
                klasse: 'has-submenu',
            }, null);
            const unter = this._untermenue(kopf);
            if (!animationen.length) {
                unter.innerHTML = '<div class="ctx-submenu-empty">Leer</div>';
            }
            for (const animation of animationen) {
                unter.appendChild(this._eintrag({
                    symbol: 'fa-running', text: animation.name,
                    rechts: (animation.frames || '?') + 'f',
                }, () => this._animationEinfuegen(name, animation)));
            }
            this.ziel.appendChild(kopf);
        }
    }

    async _animationEinfuegen(kategorie, animation) {
        await fn.addClipToTrack(this.nummer, kategorie, animation.name,
                                animation.frames || 0);
        const spur = state.project.tracks[this.nummer];
        const clip = spur.clips[spur.clips.length - 1];
        if (!clip) return;
        // Vorgabe sind zehn Sekunden — laengere Animationen werden beschnitten,
        // kuerzere bleiben, wie sie sind.
        const grenze = Math.round(DEFAULT_CLIP_SECONDS * clip.fps);
        if (clip.totalFrames > grenze) clip.trimOut = clip.totalFrames - grenze;
        clip.startFrame = this.bild;
        fn.updateDuration();
        fn.renderTimeline();
    }

    // ------------------------------------------------------- Spurtyp: Modell

    async _modell() {
        // Immer frisch holen (kein Zwischenspeicher): So erscheinen neue
        // Dateien in data/models/ sofort im Menue.
        let vorgaben = [];
        try {
            const antwort = await fetch('/api/character/models/');
            if (!antwort.ok) throw new Error('HTTP ' + antwort.status);
            vorgaben = (await antwort.json()).presets || [];
        } catch (fehler) {
            this._hinweis('Fehler beim Laden: ' + fehler.message);
            return;
        }
        if (!vorgaben.length) {
            this._hinweis('Keine Modelle in data/models/');
            return;
        }
        this._leeren();
        for (const vorgabe of vorgaben) {
            this.ziel.appendChild(this._spureintrag(
                vorgabe.label || vorgabe.name,
                () => this._modellEinfuegen(vorgabe)));
        }
    }

    _modellEinfuegen(vorgabe) {
        pushUndo('Modell-Clip hinzufügen');
        const clip = new Clip(null, vorgabe.label || vorgabe.name,
                              this.vorgabebilder, this.fps);
        clip.type = 'model';
        clip.startFrame = this.bild;
        clip.data = { preset: vorgabe.name, bodyType: 'Female_Caucasian' };
        this.spur.clips.push(clip);
        this.spur._currentPreset = null;
        fn.applyPlayhead();
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
    }

    // ---------------------------------------------------------- Spurtyp: Ton

    _ton() {
        this._leeren();
        this.ziel.appendChild(this._spureintrag('Audio-Datei wählen...',
                                                () => this._tonWaehlen()));
    }

    _tonWaehlen() {
        const feld = document.createElement('input');
        feld.type = 'file';
        feld.accept = 'audio/*';
        feld.addEventListener('change', () => this._tonEinfuegen(feld.files[0]));
        feld.click();
    }

    async _tonEinfuegen(datei) {
        if (!datei) return;
        try {
            const puffer = await this.spur.audioCtx.decodeAudioData(
                await datei.arrayBuffer());
            pushUndo('Audio-Clip hinzufügen');
            const clip = new Clip(null, datei.name, this.vorgabebilder, this.fps);
            clip.type = 'audio';
            clip.startFrame = this.bild;
            clip.data = {
                fileName: datei.name,
                audioBuffer: puffer,
                audioDuration: Math.min(DEFAULT_CLIP_SECONDS, puffer.duration),
                volume: 1.0, fadeIn: 0, fadeOut: 0, offset: 0,
            };
            clip.data.audioUrl = await this._tonHochladen(datei);
            this.spur.clips.push(clip);
            fn.updateDuration();
            fn.renderTimeline();
            fn.updateProperties();
        } catch (fehler) {
            console.error('[BVH Studio] Ton nicht lesbar:', fehler);
            alert('Audio laden fehlgeschlagen: ' + fehler.message);
        }
    }

    /**
     * Datei zum Server geben, damit sie beim Videoexport zur Verfuegung steht.
     * Schlaegt das fehl, bleibt der Clip trotzdem — im Browser klingt er.
     */
    async _tonHochladen(datei) {
        try {
            const daten = new FormData();
            daten.append('audio', datei);
            const ergebnis = await Serverabruf.formular(
                '/api/studio/audio-upload/', daten);
            return ergebnis.ok ? ergebnis.url : undefined;
        } catch (fehler) {
            console.warn('Ton nicht hochladbar:', fehler);
            return undefined;
        }
    }

    // -------------------------------------------- Spurtypen mit einem Eintrag

    _szenenobjekt() {
        this._leeren();
        this.ziel.appendChild(this._spureintrag('3D-Datei wählen...',
            () => fn.addSceneObjectClip?.(this.nummer, this.bild)));
    }

    _kamera() {
        this._leeren();
        this.ziel.appendChild(this._spureintrag('Kameraposition',
            () => fn.addCameraKeyframe(this.nummer, this.bild)));
    }

    // -------------------------------------------------------- Spurtyp: Licht

    _licht() {
        this._leeren();
        this.ziel.appendChild(this._spureintrag(
            'Lichteigenschaft (Pair: vor/nach)',
            () => fn.addLightKeyframePair(this.nummer, this.bild),
            { titel: 'Legt zwei Keyframes am gleichen Frame an — einer für das '
                     + 'Segment davor, einer für danach' }));
        this.ziel.appendChild(this._spureintrag('Lichteigenschaft (einzel)',
            () => fn.addLightKeyframe(this.nummer, this.bild)));

        const kopf = this._eintrag({
            symbol: 'fa-star', farbe: Spurmenue.SYMBOLE.light[1],
            text: 'Presets', rechts: '<i class="fas fa-caret-right"></i>',
            klasse: 'has-submenu',
        }, null);
        const unter = this._untermenue(kopf);
        unter.innerHTML = '<div class="ctx-submenu-empty">Lade...</div>';
        this.ziel.appendChild(kopf);
        this._lichtvorgaben(unter);
    }

    /** Vorgaben nachladen — sie FÜGEN Lichter hinzu, ersetzen keine. */
    async _lichtvorgaben(unter) {
        try {
            const vorgaben = await (fn.fetchTheatrePresets?.()
                ?? fetch('/api/studio/theatre-presets/')
                    .then(a => a.json()).then(d => d.presets || []));
            if (!vorgaben?.length) {
                unter.innerHTML = '<div class="ctx-submenu-empty">Keine Presets</div>';
                return;
            }
            unter.innerHTML = '';
            for (const vorgabe of vorgaben) {
                unter.appendChild(this._eintrag({
                    symbol: 'fa-lightbulb', farbe: Spurmenue.SYMBOLE.light[1],
                    text: `<span>${vorgabe.label}</span>`,
                    rechts: vorgabe.lightCount + 'x',
                    titel: (vorgabe.description || '')
                        + '\n\nFügt Preset-Lichter HINZU (existierende bleiben erhalten).',
                }, () => fn.applyTheatrePresetAdditive?.(vorgabe.name, this.bild)));
            }
        } catch (fehler) {
            unter.innerHTML = '<div class="ctx-submenu-empty">Fehler beim Laden</div>';
            console.warn('Licht-Vorgaben nicht ladbar:', fehler);
        }
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
