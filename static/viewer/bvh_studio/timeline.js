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
import { state, RULER_HEIGHT } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Reihen } from './zeitleiste_reihen.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Zeitleistenziehen } from './zeitleiste_ziehen.js';
import { Zeitleistenmenue } from './zeitleiste_menue.js';
import { Zeitleistenhilfe } from './zeitleiste_hilfe.js';
import { Fortschrittsbalken } from './zeitleiste_fortschritt.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/** Grenzen des Zooms in Bildpunkten je Sekunde. */
const ZOOM_MIN = 10;
const ZOOM_MAX = 500;
const ZOOM_SCHRITT = 10;

export function setupTimeline() {
    const flaeche = document.getElementById('timeline-canvas');
    if (!flaeche) return;
    const lineal = document.getElementById('timeline-lineal');
    Zeitleistenflaeche.setzen(flaeche, lineal);
    Fortschrittsbalken.anbinden(document.getElementById('timeline-fortschritt'));

    const rahmen = Zeitleistenflaeche.canvas.parentElement;
    const anpassen = () => {
        Zeitleistenflaeche.canvas.width = rahmen.clientWidth;
        Zeitleistenflaeche.canvas.height = Reihen.noetigeHoehe(rahmen);
        if (lineal) {
            // Klebt oben und nimmt keinen Platz: die Spurenleinwand behält
            // ihren Lineal-Streifen (RULER_HEIGHT) darunter, alle Reihen-
            // und Treffer-Rechnungen bleiben, wie sie sind.
            lineal.width = rahmen.clientWidth;
            lineal.height = RULER_HEIGHT;
            lineal.style.marginBottom = `-${RULER_HEIGHT}px`;
        }
        // Der Balken liegt unter dem Rahmen und ist so breit wie sein eigener
        // Behälter — der Rahmen verliert beim Rollbalken 15 px, der Balken nicht.
        Fortschrittsbalken.breiteSetzen(Fortschrittsbalken.canvas?.parentElement?.clientWidth
                                        || rahmen.clientWidth);
        renderTimeline();
    };
    anpassen();
    new ResizeObserver(anpassen).observe(rahmen);

    _zoomAnbinden();
    Zeitleistenziehen.anbinden();
    Zeitleistenmenue.anbinden();
    Zeitleistenhilfe.anbinden();
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
            // Die Reihe unter der Maus — mit Gruppen ist `y / TRACK_HEIGHT`
            // nicht mehr die Spurnummer (Kontextmenü: `Zeitleistenmenue._oeffnen`).
            const reihe = Reihen.beiY(e.clientY - leinwand.getBoundingClientRect().top);
            const spurNr = reihe?.trackIdx ?? -1;
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
    // Senkrechtes Blättern braucht kein Neuzeichnen mehr: das Lineal klebt
    // als eigene Leinwand (13.09.2026).
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

