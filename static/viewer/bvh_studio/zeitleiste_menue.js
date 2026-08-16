/**
 * Zeitleistenmenue — die Kontextmenues der Zeitleiste: Clip und leere Spur.
 *
 * Aus timeline.js herausgeloest (Umbau 16.08.2026). Das Menue der Modellspur
 * liegt in zeitleiste_modellmenue.js — es bringt eine eigene Vorlagenliste samt
 * Zwischenspeicher mit.
 */
import { state, HEADER_WIDTH, RULER_HEIGHT } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Reihen } from './zeitleiste_reihen.js';
import { _populateTrackAddSubmenu } from './zeitleiste_spurmenue.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Zeitleistentreffer } from './zeitleiste_treffer.js';
import { Zeitleistenziehen } from './zeitleiste_ziehen.js';
import { Modellmenue } from './zeitleiste_modellmenue.js';

/** Abstand, den ein Menue zum unteren Fensterrand haelt. */
const RAND = 10;

/** Was die Eintraege des Clipmenues tun. */
const CLIPBEFEHLE = {
    'ctx-split': () => fn.splitClipAtPlayhead(),
    'ctx-delete': () => fn.deleteSelectedClip(),
    'ctx-duplicate': () => fn.duplicateSelectedClip(),
    'ctx-save-bvh': () => fn.saveBvhAs(),
    'ctx-smooth': () => fn.smoothSelectedClip(),
    'ctx-ground': () => fn.groundFixSelectedClip(),
    'ctx-trim-start': () => fn.trimSelectedClip('start', 10),
    'ctx-trim-end': () => fn.trimSelectedClip('end', 10),
    'ctx-trim-reset': () => fn.trimSelectedClip('reset'),
};

export class Zeitleistenmenue {
    /** Maus-X des letzten Rechtsklicks — fuer "Abspielkopf hierher". */
    static mausX = 0;

    static get clipmenue() {
        return document.getElementById('clip-context-menu');
    }

    static get spurmenue() {
        return document.getElementById('track-context-menu');
    }

    static anbinden() {
        Zeitleistenflaeche.canvas.addEventListener(
            'contextmenu', Zeitleistenmenue._oeffnen);
        document.addEventListener('click', Zeitleistenmenue.schliessen);
        Zeitleistenmenue.clipmenue?.querySelectorAll('.ctx-item').forEach(eintrag => {
            eintrag.addEventListener('click', () => {
                Zeitleistenmenue.schliessen();
                const befehl = CLIPBEFEHLE[eintrag.dataset.action];
                if (befehl) befehl();
                else if (eintrag.dataset.action === 'ctx-playhead') {
                    Zeitleistenziehen.abspielkopfSetzen(Zeitleistenmenue.mausX);
                }
            });
        });
    }

    static schliessen() {
        for (const m of [Zeitleistenmenue.clipmenue, Modellmenue.menue]) {
            if (m) m.style.display = 'none';
        }
    }

    static _zeigen(menue, e) {
        menue.style.display = '';
        menue.style.left = e.clientX + 'px';
        const hoehe = menue.offsetHeight || 200;
        menue.style.top =
            Math.min(e.clientY, window.innerHeight - hoehe - RAND) + 'px';
    }

    static _oeffnen(e) {
        e.preventDefault();
        const rect = Zeitleistenflaeche.canvas.getBoundingClientRect();
        Zeitleistenmenue.mausX = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const treffer = Zeitleistentreffer.clipBei(Zeitleistenmenue.mausX, my);
        const reihe = Reihen.beiY(my);
        const spurNr = reihe?.trackIdx ?? -1;
        const spur = spurNr >= 0 ? state.project.tracks[spurNr] : null;

        if (treffer) {
            state.selectedTrackIdx = treffer.trackIdx;
            state.selectedClipIdx = treffer.clipIdx;
            fn.updateProperties();
            renderTimeline();
        }
        const klickbild = Zeitleistentreffer.bildBei(Zeitleistenmenue.mausX);

        if (!treffer && spur && my > RULER_HEIGHT
            && Zeitleistenmenue.mausX > HEADER_WIDTH
            && Zeitleistenmenue._leereSpur(e, spur, spurNr, klickbild)) {
            return;
        }
        if (Zeitleistenmenue.spurmenue) {
            Zeitleistenmenue.spurmenue.style.display = 'none';
        }
        if (spur && spur.type === 'model') {
            Zeitleistenmenue.clipmenue.style.display = 'none';
            Modellmenue.mausX = Zeitleistenmenue.mausX;
            Modellmenue.zeigen(e, spur, spurNr, treffer, klickbild,
                               Zeitleistenmenue._zeigen);
            return;
        }
        Zeitleistenmenue._clipspur(e, spur, spurNr, treffer, klickbild);
    }

    /** Rechtsklick in eine Spur ohne Clip: Menue mit "Hinzufuegen". */
    static _leereSpur(e, spur, spurNr, klickbild) {
        const menue = Zeitleistenmenue.spurmenue;
        if (!menue) return false;
        state.selectedTrackIdx = spurNr;
        state.selectedClipIdx = -1;
        fn.updateProperties();
        renderTimeline();
        Zeitleistenmenue.schliessen();
        _populateTrackAddSubmenu(spur, spurNr, menue, klickbild);
        // Der Verknuepfungsteil gilt nur beim Rechtsklick auf den Spurkopf.
        const verknuepfung = document.getElementById('track-ctx-link-section');
        if (verknuepfung) verknuepfung.style.display = 'none';
        Zeitleistenmenue._zeigen(menue, e);
        return true;
    }

    static _clipspur(e, spur, spurNr, treffer, klickbild) {
        const menue = Zeitleistenmenue.clipmenue;
        Modellmenue.menue.style.display = 'none';
        if (spur) {
            _populateTrackAddSubmenu(spur, spurNr, menue, klickbild,
                                     'clip-ctx-add-submenu');
        }
        const hinzufuegen = document.getElementById('clip-ctx-add');
        if (hinzufuegen) hinzufuegen.style.display = spur ? '' : 'none';
        Zeitleistenmenue._zeigen(menue, e);
        // Ohne Clip unter der Maus bleibt nur "Abspielkopf hierher".
        menue.querySelectorAll('.ctx-item[data-action^="ctx-"]').forEach(eintrag => {
            eintrag.style.display =
                (eintrag.dataset.action === 'ctx-playhead' || treffer) ? '' : 'none';
        });
    }
}
