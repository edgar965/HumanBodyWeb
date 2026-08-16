import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { undo, redo, pushUndo } from './undo.js';
import { _gaussSmooth, _updateGaussUI, applyGaussToAllClips,
         reloadAllClipAnimations, smoothSelectedClip,
         saveSmoothedBVH } from './werkzeug_glaettung.js';
import { _fixedPos, applyFixedPositionAll,
         restoreFixedPositionAll } from './werkzeug_position.js';
import { groundFixSelectedClip, saveBvhWithEffects } from './werkzeug_boden.js';
import { Hilfefenster } from './hilfefenster.js';

/**
 * Werkzeugleiste — die obere Leiste des BVH-Studios: Menüs, Knöpfe,
 * Spur-Kontextmenü und die Werkzeuge (Glättung, Boden, feste Position).
 *
 * Aus bvh_studio/tools.js herausgeloest (Umbau 16.08.2026): `setupToolbar()`
 * hatte 155 Zeilen, davon waren die meisten Wiederholungen:
 *
 *  * 17 Menüeinträge, jeder als eigene Zeile mit demselben Rumpf
 *    (`menü.classList.remove('open'); <aufruf>()`) — fünf im Spurmenü, fünf im
 *    Dateimenü, sieben in der Hilfe.
 *  * 4 Menüknöpfe mit `e.stopPropagation(); menü.classList.toggle('open')`.
 *  * 3 Kontextmenü-Einträge mit `menü.style.display = 'none'; if
 *    (state.selectedTrackIdx >= 0) …`.
 *  * 8 einfache Knöpfe.
 *
 * Alles davon steht jetzt in Tabellen. Ein neuer Menüeintrag ist eine Zeile.
 */
export class Werkzeugleiste {

    /** Die drei Menüs: Knopf, Menü und ihre Einträge (Kennung → Aufruf). */
    static MENUES = [
        ['btn-add-track', 'track-dropdown', [
            ['dd-add-bvh', () => fn.addTrack()],
            ['dd-add-camera', () => fn.addSpecialTrack('camera')],
            ['dd-add-light', () => fn.addSpecialTrack('light')],
            ['dd-add-audio', () => fn.addSpecialTrack('audio')],
            ['dd-add-model', () => fn.addModelTrack()],
        ]],
        ['btn-file', 'file-dropdown', [
            ['dd-file-save', () => fn.saveProject()],
            ['dd-file-save-as', () => fn.saveProjectAs()],
            ['dd-file-load', () => fn.loadProject()],
            ['dd-file-load-last', () => fn.loadLastProject()],
            ['dd-file-default', () => fn.resetToDefault()],
        ]],
        ['btn-help', 'help-dropdown', []],   // Einträge kommen aus Hilfefenster
    ];

    /** Das Werkzeugmenü — die Einträge wirken auf die Glättung und den Boden. */
    static WERKZEUGMENUE = ['btn-tools', 'tools-dropdown'];

    /** Einfache Knöpfe der Leiste. */
    static KNOEPFE = [
        ['btn-undo', () => undo()],
        ['btn-redo', () => redo()],
        ['btn-delete-track', () => fn.removeTrack(state.selectedTrackIdx)],
        ['btn-delete-clip', () => fn.deleteSelectedClip()],
        ['btn-split', () => fn.splitClipAtPlayhead()],
        ['btn-export-bvh', () => fn.exportBVH()],
        ['tool-smooth-apply', () => smoothSelectedClip()],
        ['tool-ground-apply', () => groundFixSelectedClip()],
    ];

    /** Grenzen der Glättungsbreite. */
    static SIGMA_MIN = 0.5;
    static SIGMA_MAX = 20;
    static SIGMA_VORGABE = 2;
    /** Wie weit die Glättung über Sigma hinaus reicht. */
    static SIGMA_RADIUS = 3;

    constructor() {
        this.menues = new Map();
    }

    aufbauen() {
        this._menues();
        this._knoepfe();
        this._exportknopf();
        this._werkzeuge();
        this._reiter();
        this._spurkontext();
        Hilfefenster.verdrahten(this.menues.get('help-dropdown'));
        this._menuesSchliessen();
        return this;
    }

    // ------------------------------------------------------------------- Menüs

    _menues() {
        for (const [knopfId, menueId, einträge] of Werkzeugleiste.MENUES) {
            const menue = this._menue(knopfId, menueId);
            for (const [id, tun] of einträge) this._eintrag(id, menue, tun);
        }
        this._menue(...Werkzeugleiste.WERKZEUGMENUE);
    }

    /** Knopf, der ein Menü auf- und zuklappt. */
    _menue(knopfId, menueId) {
        const menue = document.getElementById(menueId);
        this.menues.set(menueId, menue);
        document.getElementById(knopfId)?.addEventListener('click', ereignis => {
            // Ohne stopPropagation schließt der Klick das Menü sofort wieder,
            // weil er beim Dokument ankommt (siehe `_menuesSchliessen`).
            ereignis.stopPropagation();
            menue?.classList.toggle('open');
        });
        return menue;
    }

    /** Menüeintrag: schließt sein Menü und tut dann etwas. */
    _eintrag(id, menue, tun) {
        document.getElementById(id)?.addEventListener('click', () => {
            menue?.classList.remove('open');
            tun();
        });
    }

    /** Ein Klick irgendwohin schließt alle Menüs. */
    _menuesSchliessen() {
        document.addEventListener('click', () => {
            for (const menue of this.menues.values()) {
                menue?.classList.remove('open');
            }
            const kontext = document.getElementById('track-context-menu');
            if (kontext) kontext.style.display = 'none';
        });
    }

    _knoepfe() {
        for (const [id, tun] of Werkzeugleiste.KNOEPFE) {
            document.getElementById(id)?.addEventListener('click', tun);
        }
    }

    /**
     * Video-Export: zum Export-Reiter wechseln und den Bereich auf die ganze
     * Länge stellen, falls dort noch nichts steht.
     */
    _exportknopf() {
        document.getElementById('btn-export-video')?.addEventListener('click', () => {
            fn.switchPropsTab('export');
            const bis = document.getElementById('export-to');
            if (bis && (bis.value === '0' || !bis.value)) {
                bis.value = Math.round(state.project.duration * state.project.fps);
            }
        });
    }

    _reiter() {
        for (const reiter of document.querySelectorAll('.props-tab')) {
            reiter.addEventListener('click', () => fn.switchPropsTab(reiter.dataset.tab));
        }
    }

    // -------------------------------------------------------------- Werkzeuge

    _werkzeuge() {
        const menue = this.menues.get('tools-dropdown');
        this._eintrag('dd-gauss-on', menue, () => this.glaettung(true));
        this._eintrag('dd-gauss-off', menue, () => this.glaettung(false));
        this._eintrag('dd-gauss-save', menue, () => saveSmoothedBVH());
        this._eintrag('dd-ground', menue, () => {
            fn.switchPropsTab('tools');
            groundFixSelectedClip();
        });
        this._eintrag('dd-fixed-pos', menue, () => this.festePosition());
        this._eintrag('dd-save-bvh', menue, () => saveBvhWithEffects());
        this._sigma();
        this._radius();
    }

    glaettung(ein) {
        _gaussSmooth.active = ein;
        _updateGaussUI();
        if (ein) applyGaussToAllClips();
        else reloadAllClipAnimations();
    }

    /** Breite der Glättung. Außerhalb der Grenzen wird zurückgestellt. */
    _sigma() {
        document.getElementById('dd-gauss-sigma-input')
            ?.addEventListener('change', ereignis => {
                const wert = parseFloat(ereignis.target.value)
                             || Werkzeugleiste.SIGMA_VORGABE;
                _gaussSmooth.sigma = Math.max(Werkzeugleiste.SIGMA_MIN,
                    Math.min(Werkzeugleiste.SIGMA_MAX, wert));
                ereignis.target.value = _gaussSmooth.sigma;
                _updateGaussUI();
                if (_gaussSmooth.active) applyGaussToAllClips();
            });
        document.getElementById('tool-smooth-sigma')
            ?.addEventListener('input', ereignis => {
                const sigma = parseFloat(ereignis.target.value)
                              || Werkzeugleiste.SIGMA_VORGABE;
                const anzeige = document.getElementById('tool-smooth-radius');
                if (anzeige) {
                    anzeige.textContent = Math.ceil(sigma * Werkzeugleiste.SIGMA_RADIUS);
                }
            });
    }

    /** Die Figur an einem Ort halten, statt sie laufen zu lassen. */
    festePosition() {
        _fixedPos.active = !_fixedPos.active;
        const anzeige = document.getElementById('fixed-pos-status');
        if (anzeige) {
            anzeige.textContent = _fixedPos.active ? 'An' : 'Aus';
            anzeige.classList.toggle('an', _fixedPos.active);
        }
        if (_fixedPos.active) applyFixedPositionAll();
        else restoreFixedPositionAll();
    }

    _radius() {
        document.getElementById('fixed-pos-radius')
            ?.addEventListener('input', ereignis => {
                // Der Regler liegt im Menü — ohne stopPropagation schließt es.
                ereignis.stopPropagation();
                const zentimeter = parseInt(ereignis.target.value, 10);
                const anzeige = document.getElementById('fixed-pos-radius-val');
                if (anzeige) anzeige.textContent = zentimeter + 'cm';
                _fixedPos.radius = zentimeter / 100;
                if (_fixedPos.active) applyFixedPositionAll();
            });
    }

    // --------------------------------------------------------- Spur-Kontextmenü

    /** Rechtsklick auf eine Spur: löschen, umbenennen, stummschalten. */
    _spurkontext() {
        const menue = document.getElementById('track-context-menu');
        const eintrag = (id, tun) => {
            document.getElementById(id)?.addEventListener('click', () => {
                if (menue) menue.style.display = 'none';
                if (state.selectedTrackIdx < 0) return;
                tun(state.project.tracks[state.selectedTrackIdx]);
            });
        };
        eintrag('track-ctx-delete', () => fn.removeTrack(state.selectedTrackIdx));
        eintrag('track-ctx-rename', spur => this.spurUmbenennen(spur));
        eintrag('track-ctx-mute', spur => this.spurStumm(spur));
    }

    spurUmbenennen(spur) {
        const name = prompt('Neuer Track-Name:', spur.name);
        if (!name || name === spur.name) return;
        pushUndo('Spur umbenennen');
        spur.name = name;
        fn.updateTrackHeaders();
        fn.updateProperties();
    }

    spurStumm(spur) {
        pushUndo('Mute/Unmute');
        spur.muted = !spur.muted;
        // Bei Lichtspuren heißt stumm: das Licht ist aus.
        if (spur.type === 'light' && spur.light) {
            spur.light.visible = !spur.muted;
            if (spur.lightHelper) {
                spur.lightHelper.visible = !spur.muted && spur.lightVisible;
            }
        }
        fn.updateProperties();
    }
}
