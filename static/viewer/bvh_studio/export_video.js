/**
 * BVH Studio — BVH Export and Video Export (server ffmpeg + browser MediaRecorder).
 *
 * UMBAU 18.08.2026: 236 Zeilen für zwei ganz verschiedene Ausgaben. Jetzt:
 *
 *     bvhausgabe.js    BVH-Text herunterladen (Spur, einzelner Clip, Dialog)
 *     videoausgabe.js  Szene aufnehmen (Kamera aus der Zeitleiste, Rückweg)
 *
 * Hier bleibt die Bedienung: Werte aus dem Formular lesen, Fortschritt zeigen,
 * Knöpfe sperren.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { saveBlobAs } from './video_schreiben.js';
import { Bvhausgabe } from './bvhausgabe.js';
import { Videoausgabe } from './videoausgabe.js';

/** Wird von `video_schreiben.js` gelesen, um den Lauf abzubrechen. */
export let exportCancelled = false;

export async function exportBVH() { return Bvhausgabe.spur(); }
export async function saveBvhAs() { return Bvhausgabe.speichernUnter(); }

export function setupExportPanel() {
    _feld('export-target-dir', feld => {
        if (state.project.videoOutputPath) feld.value = state.project.videoOutputPath;
    });
    document.getElementById('export-start')?.addEventListener('click', startExport);
    document.getElementById('export-cancel')?.addEventListener('click', () => {
        exportCancelled = true;
    });
    // Bildbereich und Zielordner auffrischen, wenn der Reiter „Export" aufgeht:
    // Die Projektdauer ändert sich, während das Formular schon steht.
    document.querySelectorAll('.props-tab').forEach(reiter => {
        reiter.addEventListener('click', () => {
            if (reiter.dataset.tab === 'export') _bereichAuffrischen();
        });
    });
}

function _bereichAuffrischen() {
    const bis = document.getElementById('export-to');
    if (bis && bis.value === '0') {
        bis.value = Math.round(state.project.duration * state.project.fps);
    }
    _feld('export-fps', feld => { feld.value = String(state.project.fps); });
    _feld('export-target-dir', feld => {
        if (!feld.value) feld.value = state.project.videoOutputPath || '';
    });
}

function _feld(kennung, tun) {
    const feld = document.getElementById(kennung);
    if (feld) tun(feld);
}

/** Die Werte des Formulars — `null`, wenn der Bereich leer wäre. */
function _angaben() {
    const zahl = (kennung, vorgabe) =>
        parseInt(document.getElementById(kennung)?.value) || vorgabe;
    const von = zahl('export-from', 0);
    let bis = zahl('export-to', 0);
    if (bis <= von) bis = Math.round(state.project.duration * state.project.fps);
    if (bis <= von) {
        alert('Keine Frames zum Exportieren.');
        return null;
    }
    return {
        von, bis,
        bilder: zahl('export-fps', state.project.fps),
        hoehe: zahl('export-resolution', 1080),
        guete: document.getElementById('export-quality')?.value || '18',
        motor: document.getElementById('export-engine')?.value || 'server',
        dateiname: document.getElementById('export-filename')?.value
            || 'bvh_studio_export.mp4',
    };
}

async function startExport() {
    const angaben = _angaben();
    if (!angaben) return;
    exportCancelled = false;
    const felder = {
        rahmen: document.getElementById('export-progress'),
        status: document.getElementById('export-status-text'),
        balken: document.getElementById('export-progress-bar'),
        start: document.getElementById('export-start'),
        abbruch: document.getElementById('export-cancel'),
    };
    _laufAnzeigen(felder, true);
    try {
        await Videoausgabe.aufnehmen(angaben, felder);
    } finally {
        _laufAnzeigen(felder, false);
    }
}

/**
 * Fortschritt und Knöpfe umschalten.
 *
 * Die Statuszeile bleibt beim Beenden stehen: Bricht der Export ab, ist ihre
 * Meldung das Einzige, was dem Nutzer sagt, warum.
 */
function _laufAnzeigen(felder, laeuft) {
    if (felder.rahmen) felder.rahmen.style.display = laeuft ? '' : 'none';
    if (felder.abbruch) felder.abbruch.style.display = laeuft ? '' : 'none';
    if (!felder.start) return;
    felder.start.disabled = laeuft;
    felder.start.classList.toggle('knopf-gesperrt', laeuft);
}

// Register functions in registry
fn.exportBVH = exportBVH;
fn.saveBvhAs = saveBvhAs;
