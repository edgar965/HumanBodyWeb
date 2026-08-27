/**
 * Kopfspalte der Zeitleiste — die Spurnamen links.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026). Die Hoehe folgt der
 * Leinwand, damit die Spalte beim Scrollen mitgeht.
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): `updateTrackHeaders()` hatte 97
 * Zeilen. Die Gruppenzeile steht jetzt in `Gruppenkopf`, die Spurzeile in
 * `Spurkopf`, das Rechtsklickmenue in `Spurkontextmenue`.
 */

import { RULER_HEIGHT } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Reihen } from './zeitleiste_reihen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { Gruppenkopf } from './zeitleiste_gruppenkopf.js';
import { Spurkopf } from './zeitleiste_spurkopf.js';


export function updateTrackHeaders() {
    const behaelter = document.getElementById('track-headers');
    if (!behaelter) return;
    behaelter.innerHTML = '';
    // Genauso hoch wie die Leinwand, damit die Kopfspalte beim Scrollen
    // mitgeht (das CSS hat kein `bottom: 0` mehr — siehe bvh_studio.html).
    if (Zeitleistenflaeche.canvas) {
        behaelter.style.height = Zeitleistenflaeche.canvas.height + 'px';
    }
    const lineal = document.createElement('div');
    lineal.style.cssText =
        `height:${RULER_HEIGHT}px;border-bottom:1px solid var(--border);`;
    behaelter.appendChild(lineal);

    const neuzeichnen = () => { updateTrackHeaders(); renderTimeline(); };
    for (const reihe of Reihen.liste()) {
        behaelter.appendChild(reihe.header
            ? Gruppenkopf.element(reihe, neuzeichnen)
            : Spurkopf.element(reihe));
    }
}

fn.updateTrackHeaders = updateTrackHeaders;
