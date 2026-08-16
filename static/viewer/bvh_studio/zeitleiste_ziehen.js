/**
 * Zeitleistenziehen — Clips verschieben, kuerzen, Abspielkopf scrubben, Ansicht
 * schieben.
 *
 * Aus timeline.js herausgeloest (Umbau 16.08.2026): Die sieben Variablen des
 * Ziehvorgangs (`dragMode`, `draggingClip`, `dragStartX`, `dragOrigFrame`,
 * `dragOrigTrimIn`, `dragOrigTrimOut`, `panStartScrollX`) lagen in der Closure
 * von `setupTimeline` — vier Ereignisbehandler griffen darauf zu. Als
 * Klassenfelder sind sie an einem Ort.
 */
import { state, HEADER_WIDTH, RULER_HEIGHT } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { setLibSelectedItem } from './library.js';
import { Reihen } from './zeitleiste_reihen.js';
import { updateTrackHeaders } from './zeitleiste_kopfspalte.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Zeitleistentreffer } from './zeitleiste_treffer.js';

export class Zeitleistenziehen {
    /** 'none' | 'clip-drag' | 'trim-left' | 'trim-right' | 'scrub' | 'pan' */
    static art = 'none';
    static clip = null;
    static startX = 0;
    static startBild = 0;
    static startTrimVorn = 0;
    static startTrimHinten = 0;
    static startVerschiebung = 0;

    static anbinden() {
        const leinwand = Zeitleistenflaeche.canvas;
        leinwand.addEventListener('mousedown', Zeitleistenziehen._druecken);
        leinwand.addEventListener('mousemove', Zeitleistenziehen._bewegen);
        leinwand.addEventListener('mouseup', Zeitleistenziehen._loslassen);
        leinwand.addEventListener('mouseleave', Zeitleistenziehen._verlassen);
        // Mittelklick soll nicht einfuegen oder automatisch scrollen.
        leinwand.addEventListener('auxclick',
            (e) => { if (e.button === 1) e.preventDefault(); });
    }

    /** Abspielkopf auf die Mausposition setzen. */
    static abspielkopfSetzen(mx) {
        state.playheadFrame = Zeitleistentreffer.bildBei(mx);
        renderTimeline();
        fn.updatePlaybackUI();
        fn.applyPlayhead();
    }

    static _mausX(e) {
        return e.clientX - Zeitleistenflaeche.canvas.getBoundingClientRect().left;
    }

    static _druecken(e) {
        const rect = Zeitleistenflaeche.canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Mittlere Taste oder Alt+Klick schiebt die Ansicht.
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            Zeitleistenziehen.art = 'pan';
            Zeitleistenziehen.startX = e.clientX;
            Zeitleistenziehen.startVerschiebung = state.timelineScrollX;
            e.preventDefault();
            return;
        }
        if (e.button !== 0) return;

        const treffer = Zeitleistentreffer.clipBei(mx, my);
        // Auswahl in der Bibliothek loeschen, sobald in der Leiste geklickt wird.
        document.querySelectorAll('.lib-item.selected')
            .forEach(el => el.classList.remove('selected'));
        setLibSelectedItem(null);

        if (treffer) {
            Zeitleistenziehen._clipGreifen(treffer, mx);
            e.preventDefault();
            return;
        }
        if (mx <= HEADER_WIDTH) return;
        if (my <= RULER_HEIGHT) {
            Zeitleistenziehen.art = 'scrub';
            Zeitleistenziehen.startX = mx;
            Zeitleistenziehen.abspielkopfSetzen(mx);
        } else {
            Zeitleistenziehen._reiheWaehlen(my);
        }
        e.preventDefault();
    }

    static _clipGreifen(treffer, mx) {
        state.selectedTrackIdx = treffer.trackIdx;
        state.selectedClipIdx = treffer.clipIdx;
        fn.updateProperties();
        fn.switchPropsTab?.('props');
        renderTimeline();

        const clip = state.project.tracks[treffer.trackIdx].clips[treffer.clipIdx];
        Zeitleistenziehen.clip = treffer;
        Zeitleistenziehen.startX = mx;
        Zeitleistenziehen.startBild = clip.startFrame;
        Zeitleistenziehen.startTrimVorn = clip.trimIn;
        Zeitleistenziehen.startTrimHinten = clip.trimOut;
        // Am Rand gezogen heisst kuerzen, in der Mitte verschieben.
        if (treffer.edge === 'left') {
            pushUndo('Trim links');
            Zeitleistenziehen.art = 'trim-left';
        } else if (treffer.edge === 'right') {
            pushUndo('Trim rechts');
            Zeitleistenziehen.art = 'trim-right';
        } else {
            pushUndo('Clip verschieben');
            Zeitleistenziehen.art = 'clip-drag';
        }
    }

    static _reiheWaehlen(my) {
        const reihe = Reihen.beiY(my);
        if (reihe?.header) {
            if (reihe.header === 'light') {
                state.lightGroupCollapsed = !state.lightGroupCollapsed;
            } else {
                state.sceneGroupCollapsed = !state.sceneGroupCollapsed;
            }
            updateTrackHeaders();
            renderTimeline();
            return;
        }
        if (!reihe || reihe.trackIdx === undefined) return;
        state.selectedTrackIdx = reihe.trackIdx;
        state.selectedClipIdx = -1;
        fn.updateProperties();
        fn.switchPropsTab?.('props');
        renderTimeline();
    }

    static _bewegen(e) {
        if (Zeitleistenziehen.art === 'none') {
            Zeitleistenziehen._zeigerform(e);
            return;
        }
        const mx = Zeitleistenziehen._mausX(e);
        const art = Zeitleistenziehen.art;
        if (art === 'scrub') {
            if (mx > HEADER_WIDTH) Zeitleistenziehen.abspielkopfSetzen(mx);
        } else if (art === 'pan') {
            const dx = e.clientX - Zeitleistenziehen.startX;
            state.timelineScrollX = Math.max(0, Zeitleistenziehen.startVerschiebung - dx);
            renderTimeline();
        } else if (Zeitleistenziehen.clip) {
            Zeitleistenziehen._clipAendern(art, mx);
        }
    }

    static _zeigerform(e) {
        const rect = Zeitleistenflaeche.canvas.getBoundingClientRect();
        const treffer = Zeitleistentreffer.clipBei(e.clientX - rect.left,
                                                   e.clientY - rect.top);
        Zeitleistenflaeche.canvas.style.cursor =
            treffer?.edge ? 'ew-resize' : (treffer ? 'grab' : 'default');
    }

    static _clipAendern(art, mx) {
        const z = Zeitleistenziehen;
        const versatz = Math.round(((mx - z.startX) / state.timelineZoom)
                                   * state.project.fps);
        const clip = state.project.tracks[z.clip.trackIdx].clips[z.clip.clipIdx];
        if (art === 'clip-drag') {
            clip.startFrame = Math.max(0, z.startBild + versatz);
        } else if (art === 'trim-left') {
            const neu = Math.max(0, Math.min(clip.totalFrames - clip.trimOut - 1,
                                             z.startTrimVorn + versatz));
            clip.trimIn = neu;
            // Anfang mitschieben, damit der sichtbare Teil stehen bleibt.
            clip.startFrame = Math.max(0, z.startBild + (neu - z.startTrimVorn));
        } else if (art === 'trim-right') {
            clip.trimOut = Math.max(0, Math.min(clip.totalFrames - clip.trimIn - 1,
                                                z.startTrimHinten - versatz));
        }
        fn.updateDuration();
        renderTimeline();
        fn.applyPlayhead?.();
    }

    static _loslassen() {
        const art = Zeitleistenziehen.art;
        if (art === 'clip-drag' || art === 'trim-left' || art === 'trim-right') {
            Zeitleistenziehen.clip = null;
            fn.updateProperties();
        }
        Zeitleistenziehen.art = 'none';
        Zeitleistenflaeche.canvas.style.cursor = 'default';
    }

    static _verlassen() {
        if (Zeitleistenziehen.art === 'clip-drag') Zeitleistenziehen.clip = null;
        Zeitleistenziehen.art = 'none';
    }
}
