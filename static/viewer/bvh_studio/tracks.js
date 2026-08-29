/**
 * BVH Studio — Track management (add, remove, select, clip operations).
 *
 * UMBAU 18.08.2026: 324 Zeilen. Jetzt:
 *
 *     spurerzeugung.js    Spuren anlegen (Animation, Modell, Kamera/Licht/Ton/Objekt)
 *     spurabbau.js        Spuren entfernen und Grafikspeicher freigeben
 *     spurauswahl.js      Auswahl und Verschiebe-Griffe
 *     kameraschluessel.js Kameraposition auf die Zeitleiste legen
 *     audiospur.js        Tondatei einlegen und hochladen
 *
 * Hier bleiben die Namen für die Registrierung. Sechs Importe aus
 * `character_core.js` (base64-Umwandlung, Werkstoffe, Hautgewichte) sind
 * entfallen — sie standen im Kopf, benutzt hat sie niemand.
 *
 * DABEI GEFUNDEN: Die Sperre für Szenen-Elemente („Boden kann nicht gelöscht
 * werden") stand ERST NACH dem Freigeben von Netz und Gruppe. Wer den Boden zu
 * löschen versuchte, bekam die Meldung — und einen verschwundenen Boden mit
 * einer Spur ohne Netz. In `Spurabbau` greift die Sperre jetzt zuerst.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { addClipToTrack, loadClipAnimation, buildClipFromData,
         duplicateSelectedClip, deleteSelectedClip, trimSelectedClip,
         splitClipAtPlayhead } from './spur_clips.js';
import { addLightKeyframePair, addLightKeyframe } from './spur_lichter.js';
import { loadTrackCharacter } from './spur_charakter.js';
import { Spurerzeugung } from './spurerzeugung.js';
import { Spurabbau } from './spurabbau.js';
import { Spurauswahl } from './spurauswahl.js';
import { Kameraschluessel } from './kameraschluessel.js';
import { Audiospur } from './audiospur.js';

export function addTrack(name) { return Spurerzeugung.animation(name); }
export function addModelTrack(name) { return Spurerzeugung.modell(name); }
export function addSpecialTrack(type, name) {
    return Spurerzeugung.besonders(type, name);
}
export function addCameraKeyframe(trackIdx, frame) {
    Kameraschluessel.setzen(trackIdx, frame);
}
export function loadAudioFile(trackIdx) { Audiospur.dateiWaehlen(trackIdx); }
export function removeTrack(idx) { Spurabbau.entfernen(idx); }
export function selectTrack(idx) { Spurauswahl.waehlen(idx); }

// Register functions in registry
fn.addTrack = addTrack;
fn.addModelTrack = addModelTrack;
fn.addSpecialTrack = addSpecialTrack;
fn.addClipToTrack = addClipToTrack;
fn.addCameraKeyframe = addCameraKeyframe;
fn.addLightKeyframe = addLightKeyframe;
fn.addLightKeyframePair = addLightKeyframePair;
fn.loadAudioFile = loadAudioFile;
fn.removeTrack = removeTrack;
fn.selectTrack = selectTrack;
fn.loadClipAnimation = loadClipAnimation;
fn.loadTrackCharacter = loadTrackCharacter;
fn.duplicateSelectedClip = duplicateSelectedClip;
fn.deleteSelectedClip = deleteSelectedClip;
fn.trimSelectedClip = trimSelectedClip;
fn.splitClipAtPlayhead = splitClipAtPlayhead;
