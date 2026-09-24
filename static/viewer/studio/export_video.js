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
export async function saveBvhToLibrary() { return Bvhausgabe.inBibliothekSpeichern(); }

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
    _aufloesungsfeld();
    _cropfeld();
    _crfregler();
}

/** „Benutzerdefiniert" in der Aufloesungs-Auswahl blendet die Breite/Hoehe-Felder ein. */
function _aufloesungsfeld() {
    const auswahl = document.getElementById('export-resolution');
    const feld = document.getElementById('export-custom-res');
    if (!auswahl || !feld) return;
    const auffrischen = () => feld.classList.toggle('an', auswahl.value === 'custom');
    auswahl.addEventListener('change', auffrischen);
    auffrischen();
}

/** Die Checkbox „Bildausschnitt" blendet die Crop-Felder ein. */
function _cropfeld() {
    const schalter = document.getElementById('export-crop-an');
    const feld = document.getElementById('export-crop-felder');
    if (!schalter || !feld) return;
    const auffrischen = () => feld.classList.toggle('an', schalter.checked);
    schalter.addEventListener('change', auffrischen);
    auffrischen();
}

/** Der CRF-Regler zeigt seinen Wert direkt daneben (wie Theatre). */
function _crfregler() {
    const regler = document.getElementById('export-crf');
    const anzeige = document.getElementById('export-crf-val');
    if (!regler || !anzeige) return;
    regler.addEventListener('input', () => { anzeige.textContent = regler.value; });
}

/** Feste Aufloesungen der Auswahlliste (Vorbild: Theatre `Bildexport.AUFLOESUNGEN`). */
const AUFLOESUNGEN = {
    '720': [1280, 720], '1080': [1920, 1080],
    '1440': [2560, 1440], '2160': [3840, 2160],
};

/** Breite/Hoehe aus der Aufloesungs-Auswahl. */
function _masse() {
    const wahl = document.getElementById('export-resolution')?.value || '1080';
    if (wahl === 'viewport') {
        const leinwand = state.renderer?.domElement;
        if (leinwand) return [leinwand.clientWidth || leinwand.width, leinwand.clientHeight || leinwand.height];
        return [1920, 1080];
    }
    if (wahl === 'custom') {
        const zahl = (kennung, vorgabe) => parseInt(document.getElementById(kennung)?.value) || vorgabe;
        return [zahl('export-width', 1920), zahl('export-height', 1080)];
    }
    return AUFLOESUNGEN[wahl] || [1920, 1080];
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
    const [breite, hoehe] = _masse();
    const ausschnittAn = document.getElementById('export-crop-an')?.checked || false;
    const format = document.getElementById('export-format')?.value || 'mp4';
    const dateiname = document.getElementById('export-filename')?.value
        || 'bvh_studio_export.mp4';
    return {
        von, bis,
        bilder: zahl('export-fps', state.project.fps),
        breite, hoehe,
        format,
        guete: zahl('export-crf', 18),
        hintergrund: document.getElementById('export-bg')?.value || 'scene',
        ausschnitt: ausschnittAn ? {
            x: zahl('export-crop-x', 0), y: zahl('export-crop-y', 0),
            breite: zahl('export-crop-w', 0), hoehe: zahl('export-crop-h', 0),
        } : null,
        motor: document.getElementById('export-engine')?.value || 'server',
        // Endung folgt dem gewählten Format — sonst hieße eine WebM-Datei
        // nach der Wahl noch ".mp4" (Dateiname-Feld ändert sich nicht mit).
        dateiname: _mitEndung(dateiname, format),
    };
}

const FORMAT_ENDUNG = { mp4: 'mp4', webm: 'webm', png: 'zip' };

function _mitEndung(dateiname, format) {
    const endung = FORMAT_ENDUNG[format] || 'mp4';
    return dateiname.replace(/\.[^.]+$/, '') + '.' + endung;
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
    // 'block'/'inline-block', nicht '': #export-progress und #export-cancel
    // stehen per ID-Regel auf display:none — mit '' erschien seit dem
    // 17.08.2026 weder Balken noch Abbrechen (11.09.2026).
    if (felder.rahmen) felder.rahmen.style.display = laeuft ? 'block' : 'none';
    if (felder.abbruch) felder.abbruch.style.display = laeuft ? 'inline-block' : 'none';
    if (!felder.start) return;
    felder.start.disabled = laeuft;
    felder.start.classList.toggle('knopf-gesperrt', laeuft);
}

// Register functions in registry
fn.exportBVH = exportBVH;
fn.saveBvhAs = saveBvhAs;
fn.saveBvhToLibrary = saveBvhToLibrary;
