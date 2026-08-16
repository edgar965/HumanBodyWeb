/**
 * Zeichnen der Zeitleiste — Lineal, Spuren, Clips, Abspielkopf.
 *
 * Aus timeline.js herausgeloest (Umbau 15.08.2026): 330 Zeilen, die bei jeder
 * Mausbewegung laufen. Getrennt vom Aufbau der Ereignisse, damit man das eine
 * lesen kann, ohne das andere zu durchsuchen.
 */

import { state, TRACK_HEIGHT, HEADER_WIDTH, RULER_HEIGHT } from './state.js';
import { Reihen } from './zeitleiste_reihen.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Zeitleistenspuren } from './zeitleiste_spuren.js';


export function renderTimeline() {
    if (!Zeitleistenflaeche.ctx || !Zeitleistenflaeche.canvas) return;
    // Reihenzahl kann sich seit dem letzten Zeichnen geändert haben (Spur
    // angelegt, Gruppe aufgeklappt). Die Leinwand wächst dann mit — ohne
    // Rekursion, denn wir zeichnen gleich sowieso.
    const _wrap = Zeitleistenflaeche.canvas.parentElement;
    if (_wrap) {
        const soll = Reihen.noetigeHoehe(_wrap);
        if (Zeitleistenflaeche.canvas.height !== soll) Zeitleistenflaeche.canvas.height = soll;
    }
    const w = Zeitleistenflaeche.canvas.width, h = Zeitleistenflaeche.canvas.height;
    const pps = state.timelineZoom;  // pixels per second at current zoom

    Zeitleistenflaeche.ctx.clearRect(0, 0, w, h);

    // Ruler
    Zeitleistenflaeche.ctx.fillStyle = '#1a1a2e';
    Zeitleistenflaeche.ctx.fillRect(0, 0, w, RULER_HEIGHT);
    Zeitleistenflaeche.ctx.strokeStyle = '#334155';
    Zeitleistenflaeche.ctx.lineWidth = 1;
    Zeitleistenflaeche.ctx.beginPath();
    Zeitleistenflaeche.ctx.moveTo(0, RULER_HEIGHT);
    Zeitleistenflaeche.ctx.lineTo(w, RULER_HEIGHT);
    Zeitleistenflaeche.ctx.stroke();

    // Time markers
    Zeitleistenflaeche.ctx.fillStyle = '#64748b';
    Zeitleistenflaeche.ctx.font = '10px monospace';
    const secStep = Math.max(1, Math.floor(50 / pps));
    for (let s = 0; s < state.project.duration + 10; s += secStep) {
        const x = HEADER_WIDTH + s * pps - state.timelineScrollX;
        if (x < HEADER_WIDTH || x > w) continue;
        Zeitleistenflaeche.ctx.fillText(`${s}s`, x + 2, 12);
        Zeitleistenflaeche.ctx.beginPath();
        Zeitleistenflaeche.ctx.moveTo(x, 14);
        Zeitleistenflaeche.ctx.lineTo(x, RULER_HEIGHT);
        Zeitleistenflaeche.ctx.stroke();
    }

    // Tracks + Clips (nach Display-Rows, damit Licht-Gruppen-Header richtig rendert)
    const rows = Reihen.liste();
    for (let ri = 0; ri < rows.length; ri++) {
        const row = rows[ri];
        const y = RULER_HEIGHT + ri * TRACK_HEIGHT;
        if (row.header) {
            const isLight = row.header === 'light';
            Zeitleistenflaeche.ctx.fillStyle = isLight ? 'rgba(255,193,7,0.12)' : 'rgba(124,92,191,0.12)';
            Zeitleistenflaeche.ctx.fillRect(0, y, w, TRACK_HEIGHT);
            Zeitleistenflaeche.ctx.strokeStyle = isLight ? 'rgba(255,193,7,0.4)' : 'rgba(124,92,191,0.4)';
            Zeitleistenflaeche.ctx.beginPath();
            Zeitleistenflaeche.ctx.moveTo(0, y);
            Zeitleistenflaeche.ctx.lineTo(w, y);
            Zeitleistenflaeche.ctx.moveTo(0, y + TRACK_HEIGHT);
            Zeitleistenflaeche.ctx.lineTo(w, y + TRACK_HEIGHT);
            Zeitleistenflaeche.ctx.stroke();
            Zeitleistenflaeche.ctx.fillStyle = isLight ? '#ffc107' : '#b388ff';
            Zeitleistenflaeche.ctx.font = 'bold 11px sans-serif';
            Zeitleistenflaeche.ctx.textBaseline = 'middle';
            const caret = row.collapsed ? '▶' : '▼';
            Zeitleistenflaeche.ctx.fillText(`${caret} ${row.label}`, 8, y + TRACK_HEIGHT / 2 + 1);
            Zeitleistenflaeche.ctx.textBaseline = 'alphabetic';
            continue;
        }
        const ti = row.trackIdx;
        const track = state.project.tracks[ti];

        Zeitleistenspuren.hintergrund(ti, y, w);
        Zeitleistenspuren.balken(track, y, pps, w);
        Zeitleistenspuren.linien(track, y, pps);
        Zeitleistenspuren.klips(track, ti, y, pps);
        Zeitleistenspuren.ueberblendung(track, y, pps, w);
    }

    // Playhead
    const phX = HEADER_WIDTH + (state.playheadFrame / state.project.fps) * pps - state.timelineScrollX;
    if (phX >= HEADER_WIDTH) {
        Zeitleistenflaeche.ctx.strokeStyle = '#ef4444';
        Zeitleistenflaeche.ctx.lineWidth = 2;
        Zeitleistenflaeche.ctx.beginPath();
        Zeitleistenflaeche.ctx.moveTo(phX, 0);
        Zeitleistenflaeche.ctx.lineTo(phX, h);
        Zeitleistenflaeche.ctx.stroke();
        // Playhead handle
        Zeitleistenflaeche.ctx.fillStyle = '#ef4444';
        Zeitleistenflaeche.ctx.beginPath();
        Zeitleistenflaeche.ctx.moveTo(phX - 6, 0);
        Zeitleistenflaeche.ctx.lineTo(phX + 6, 0);
        Zeitleistenflaeche.ctx.lineTo(phX, 10);
        Zeitleistenflaeche.ctx.fill();
    }

    // Update frame info
    const info = document.getElementById('tl-frame-info');
    if (info) info.textContent = `Frame ${state.playheadFrame} / ${Math.round(state.project.duration * state.project.fps)}`;
}

export function updateDuration() {
    // Duration is now auto-computed by Timeline.duration getter.
    // This function is kept for backward compatibility (called from many places).
}

fn.renderTimeline = renderTimeline;
fn.updateDuration = updateDuration;
