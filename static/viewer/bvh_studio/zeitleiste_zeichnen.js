/**
 * Zeichnen der Zeitleiste — Lineal, Spuren, Clips, Abspielkopf.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026): 330 Zeilen, die bei jeder
 * Mausbewegung laufen. Getrennt vom Aufbau der Ereignisse, damit man das eine
 * lesen kann, ohne das andere zu durchsuchen.
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): `renderTimeline()` hatte 95 Zeilen.
 * Lineal, Gruppenzeile und Abspielkopf stehen jetzt in eigenen Klassen; die
 * Gruppenfarben teilt sich die Leinwand seither mit der Kopfspalte.
 */

import { state, TRACK_HEIGHT, RULER_HEIGHT } from './state.js';
import { Reihen } from './zeitleiste_reihen.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Zeitleistenspuren } from './zeitleiste_spuren.js';
import { Zeitleistenlineal } from './zeitleiste_lineal.js';
import { Gruppenzeile } from './zeitleiste_gruppenzeile.js';
import { Abspielkopf } from './zeitleiste_abspielkopf.js';


export function renderTimeline() {
    if (!Zeitleistenflaeche.ctx || !Zeitleistenflaeche.canvas) return;
    // Reihenzahl kann sich seit dem letzten Zeichnen geändert haben (Spur
    // angelegt, Gruppe aufgeklappt). Die Leinwand wächst dann mit — ohne
    // Rekursion, denn wir zeichnen gleich sowieso.
    const rahmen = Zeitleistenflaeche.canvas.parentElement;
    if (rahmen) {
        const soll = Reihen.noetigeHoehe(rahmen);
        if (Zeitleistenflaeche.canvas.height !== soll) {
            Zeitleistenflaeche.canvas.height = soll;
        }
    }
    const breite = Zeitleistenflaeche.canvas.width;
    const hoehe = Zeitleistenflaeche.canvas.height;
    const pps = state.timelineZoom;      // Pixel je Sekunde beim aktuellen Zoom

    Zeitleistenflaeche.ctx.clearRect(0, 0, breite, hoehe);
    Zeitleistenlineal.zeichnen(breite, pps);
    _reihen(breite, pps);
    Abspielkopf.zeichnen(hoehe, pps);
    Abspielkopf.bildanzeige();
}

/** Spuren und Klips — nach Anzeigereihen, damit Gruppenzeilen mitkommen. */
function _reihen(breite, pps) {
    const reihen = Reihen.liste();
    for (let ri = 0; ri < reihen.length; ri++) {
        const reihe = reihen[ri];
        const y = RULER_HEIGHT + ri * TRACK_HEIGHT;
        if (reihe.header) {
            Gruppenzeile.zeichnen(reihe, y, breite);
            continue;
        }
        const ti = reihe.trackIdx;
        const spur = state.project.tracks[ti];
        Zeitleistenspuren.hintergrund(ti, y, breite);
        Zeitleistenspuren.balken(spur, y, pps, breite);
        Zeitleistenspuren.linien(spur, y, pps);
        Zeitleistenspuren.klips(spur, ti, y, pps);
        Zeitleistenspuren.ueberblendung(spur, y, pps, breite);
    }
}

export function updateDuration() {
    // Die Dauer rechnet der `duration`-Getter der Zeitleiste selbst aus. Die
    // Funktion bleibt, weil viele Stellen sie noch rufen.
}

fn.renderTimeline = renderTimeline;
fn.updateDuration = updateDuration;
