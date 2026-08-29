/**
 * Zeitleiste des BVH-Studios aufbauen: Leinwandgroesse, Zoom, Ablegen, Scrollen.
 *
 * WARUM diese Datei jetzt klein ist (Umbau 16.08.2026): `setupTimeline` war EINE
 * Funktion mit 439 Zeilen — Groessenanpassung, Zoom, Treffersuche, vier
 * Mausbehandler mit sieben Zustandsvariablen, drei Kontextmenues, Ablegen und
 * Scrollen. Aufgeteilt nach Aufgabe:
 *
 *   zeitleiste_treffer.js  was liegt an dieser Stelle?
 *   zeitleiste_ziehen.js   verschieben, kuerzen, scrubben, Ansicht schieben
 *   zeitleiste_menue.js    die drei Kontextmenues
 */
import { state, TRACK_HEIGHT, RULER_HEIGHT } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Reihen } from './zeitleiste_reihen.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Zeitleistenziehen } from './zeitleiste_ziehen.js';
import { Zeitleistenmenue } from './zeitleiste_menue.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/** Grenzen des Zooms in Bildpunkten je Sekunde. */
const ZOOM_MIN = 10;
const ZOOM_MAX = 500;
const ZOOM_SCHRITT = 10;

export function setupTimeline() {
    const flaeche = document.getElementById('timeline-canvas');
    if (!flaeche) return;
    Zeitleistenflaeche.setzen(flaeche);

    const rahmen = Zeitleistenflaeche.canvas.parentElement;
    const anpassen = () => {
        Zeitleistenflaeche.canvas.width = rahmen.clientWidth;
        Zeitleistenflaeche.canvas.height = Reihen.noetigeHoehe(rahmen);
        renderTimeline();
    };
    anpassen();
    new ResizeObserver(anpassen).observe(rahmen);

    _zoomAnbinden();
    Zeitleistenziehen.anbinden();
    Zeitleistenmenue.anbinden();
    _ablegenAnbinden();
    _scrollenAnbinden();
}

/** Zoomstand anzeigen — steht sonst an zwei Stellen doppelt. */
function _zoomAnzeigen() {
    const regler = document.getElementById('tl-zoom');
    if (regler) regler.value = state.timelineZoom;
    const beschriftung = document.getElementById('tl-zoom-label');
    if (beschriftung) beschriftung.textContent = `Zoom: ${state.timelineZoom}%`;
}

function _zoomAnbinden() {
    const regler = document.getElementById('tl-zoom');
    if (!regler) return;
    regler.addEventListener('input', () => {
        state.timelineZoom = parseInt(regler.value);
        _zoomAnzeigen();
        renderTimeline();
    });
}

function _ablegenAnbinden() {
    const leinwand = Zeitleistenflaeche.canvas;
    leinwand.addEventListener('dragover', (e) => e.preventDefault());
    leinwand.addEventListener('drop', (e) => {
        e.preventDefault();
        try {
            const daten = JSON.parse(e.dataTransfer.getData('application/json'));
            const y = e.clientY - leinwand.getBoundingClientRect().top - RULER_HEIGHT;
            const spurNr = Math.floor(y / TRACK_HEIGHT);
            if (spurNr >= 0 && spurNr < state.project.tracks.length) {
                fn.addClipToTrack(spurNr, daten.category, daten.name, daten.frames);
            } else {
                // Unterhalb der letzten Spur abgelegt: neue Spur anlegen.
                fn.addTrack();
                fn.addClipToTrack(state.project.tracks.length - 1,
                                  daten.category, daten.name, daten.frames);
            }
        } catch (err) {
            Protokoll.warnung('timeline', 'Drop failed:', err);
        }
    });
}

function _scrollenAnbinden() {
    Zeitleistenflaeche.canvas.addEventListener('wheel', (e) => {
        if (e.ctrlKey) {
            const schritt = e.deltaY > 0 ? -ZOOM_SCHRITT : ZOOM_SCHRITT;
            state.timelineZoom = Math.max(ZOOM_MIN,
                Math.min(ZOOM_MAX, state.timelineZoom + schritt));
            _zoomAnzeigen();
        } else {
            state.timelineScrollX =
                Math.max(0, state.timelineScrollX + e.deltaX + e.deltaY);
        }
        renderTimeline();
        e.preventDefault();
    });
}

