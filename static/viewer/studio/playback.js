/**
 * BVH Studio — Playback controls, audio, apply playhead to tracks.
 */
import { state, HEADER_WIDTH } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { startAudioPlayback, stopAllAudio, stopAudioTrack } from './spur_ton.js';
import { _schedulePreloads } from './vorladen.js';
import { applyAudioTrack } from './spur_ton.js';
import { applyBvhTrack, applyCameraTrack, applyLightTrack, applyModelTrack,
    applySceneObjectTrack } from './spur_anwenden.js';
import { Abspielende } from './abspielende.js';
import { Mimikanwendung } from './mimikanwendung.js';
import { Genesis9gelenke } from '../gemeinsam/genesis9gelenke.js';
import { Endlosschalter } from './endlosschalter.js';
import { Ladehinweis } from './ladehinweis.js';
import { Zeitleistenfolge } from './zeitleiste_folgen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Schluesselpaar } from './schluesselpaar.js';
import { globaleSichtbarkeit } from './globale_sichtbarkeit.js';

export function setupPlayback() {
    document.getElementById('pb-play')?.addEventListener('click', togglePlay);
    Endlosschalter.binden();
    document.getElementById('pb-stop')?.addEventListener('click', stopPlayback);
    document.getElementById('pb-prev')?.addEventListener('click', () => stepFrame(-1));
    document.getElementById('pb-next')?.addEventListener('click', () => stepFrame(1));
    document.getElementById('pb-start')?.addEventListener('click', () => springen(0));
    document.getElementById('pb-end')?.addEventListener('click', () => springen(abspielende()));
    document.getElementById('pb-speed')?.addEventListener('input', (e) => {
        state.playbackSpeed = parseFloat(e.target.value) || 0;
        const anzeige = document.getElementById('pb-speed-val');
        if (anzeige) anzeige.textContent = state.playbackSpeed.toFixed(2) + '×';
    });

    // Ctrl shortcuts registered globally at module top level (index.js)
    // Other keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        const inInput = (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT');
        if (inInput) return;
        if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
        if (e.code === 'ArrowLeft') { e.preventDefault(); stepFrame(-1); }
        if (e.code === 'ArrowRight') { e.preventDefault(); stepFrame(1); }
        if (e.code === 'Home') { e.preventDefault(); springen(0); }
        if (e.code === 'End') { e.preventDefault(); springen(abspielende()); }
        if (e.code === 'Delete' || e.code === 'Backspace') {
            e.preventDefault();
            // Priorität: Clip-Selektion → Library-Selektion → Track-Selektion
            if (state.selectedClipIdx >= 0) {
                fn.deleteSelectedClip();
            } else if (document.querySelector('.lib-item.selected')) {
                fn.deleteSelectedLibItem();
            } else if (state.selectedTrackIdx >= 0) {
                fn.removeTrack(state.selectedTrackIdx);  // pushUndo intern
            }
        }
        if (e.code === 'KeyS' && !e.ctrlKey) {
            e.preventDefault();
            fn.splitClipAtPlayhead();
        }
        if (e.code === 'KeyB' && !e.ctrlKey) {
            e.preventDefault();
            // Nur auf einer Animationsspur — `standbildEinfuegen` prüft das
            // selbst noch einmal (Aufruf auch aus dem Kontextmenü möglich).
            if (state.project.tracks[state.selectedTrackIdx]?.type === 'bvh') {
                fn.standbildEinfuegen();
            }
        }
        if (e.code === 'KeyG' && !e.ctrlKey) {
            e.preventDefault();
            const spur = state.project.tracks[state.selectedTrackIdx];
            if (spur?.type === 'bvh') {
                fn.addSpeedKeyframeAufAnimation(state.selectedTrackIdx);
            } else if (spur?.type === 'effekte') {
                fn.addSpeedKeyframe(state.selectedTrackIdx);
            }
        }
        if (e.code === 'KeyK') {
            e.preventDefault();
            const t = state.project.tracks[state.selectedTrackIdx];
            if (t?.type === 'camera') fn.addCameraKeyframe(state.selectedTrackIdx);
        }
        if (e.code === 'KeyL') {
            e.preventDefault();
            const t = state.project.tracks[state.selectedTrackIdx];
            if (t?.type === 'light') fn.addLightKeyframe(state.selectedTrackIdx);
        }
        // Ctrl shortcuts handled in capture-phase handler above
        if (e.key === 'F2') {
            e.preventDefault();
            const sel = document.querySelector('.lib-item.selected');
            if (sel) fn.renameSelectedLibItem();
        }
        if (e.code === 'KeyA' && !e.ctrlKey) {
            e.preventDefault();
            const sel = document.querySelector('.lib-item.selected');
            if (sel) fn.previewAnimation(sel.dataset.category, sel.dataset.name);
        }
        if (e.code === 'KeyQ') {
            e.preventDefault();
            fn.closePreview();
        }
    });
}

export function togglePlay() {
    // Laedt noch etwas (Figur, Retarget), zeigt ein Popup, was fehlt, und spielt,
    // sobald alles da ist (Edgar, 21.09.2026: 'bei start auf Play tut sich nichts').
    if (!state.playing && Ladehinweis.zeigen(state, togglePlay)) return;
    state.playing = !state.playing;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = state.playing ? 'fas fa-pause' : 'fas fa-play';
    if (state.playing) {
        // Am Ende angehalten (ohne „Endlos"): von vorn, sonst hielte es sofort wieder.
        state.playheadFrame = Abspielende.startbild(state.playheadFrame, abspielende());
        // Diagnose-Snapshot: was ist der Zustand beim Play-Start?
        const summary = state.project.tracks.map((tr, i) => {
            const link = tr.type === 'model' ? `→${tr._linkedAnimIdx}` : '';
            const ctrl = tr.type === 'bvh' ? (tr._modelControlled ? 'mctl' : 'free') : '';
            const has = tr.type === 'bvh' ? `mesh=${!!tr.mesh} mix=${!!tr.mixer} skel=${!!tr.skeleton}` : '';
            const clipsInfo = tr.clips.map(c => {
                const cs = c.startFrame, ce = c.startFrame + Math.ceil(c.duration * state.project.fps);
                const ac = (c.type === 'bvh') ? `ac=${!!c.animClip}` : '';
                const preset = c.data?.preset ? ` p=${c.data.preset}` : '';
                return `${c.name}[${cs}-${ce}${preset}${ac?' '+ac:''}]`;
            }).join(',');
            return `T${i}(${tr.type}/${tr.name}${link} ${ctrl} ${has}): [${clipsInfo}]`;
        }).join(' | ');
        fn.serverLog('play_start',
            `frame=${state.playheadFrame} fps=${state.project.fps} tracks=${state.project.tracks.length} ${summary}`);
        startAudioPlayback();
    } else {
        stopAllAudio();
        state.controls.enabled = true;
    }
}

/** Das Bild, an dem die letzte Animation endet — siehe `Abspielende`. */
export function abspielende() {
    return Abspielende.bild(state.project.tracks, state.project.fps, state.project.duration);
}

/** Anhalten, ohne den Abspielkopf zu bewegen (Ende ohne „Endlos"). */
export function pausePlayback() {
    state.playing = false;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = 'fas fa-play';
    stopAllAudio();
    state.controls.enabled = true;
}

export function stopPlayback() {
    state.playing = false;
    state.playheadFrame = 0;
    const icon = document.getElementById('pb-play-icon');
    if (icon) icon.className = 'fas fa-play';
    stopAllAudio();
    state.controls.enabled = true;  // re-enable OrbitControls
    Zeitleistenfolge.nachziehen(state, Zeitleistenflaeche.breite - HEADER_WIDTH);
    applyPlayhead();
    fn.renderTimeline();
    updatePlaybackUI();
}

export function stepFrame(delta) {
    springen(state.playheadFrame + delta);
}

/**
 * Den Abspielkopf auf ein Bild setzen (Anfang, Ende, Schritt) — Abspielen
 * läuft weiter. Zieht die Zeitleiste mit, wenn der Kopf dabei den sichtbaren
 * Rand verlässt (22.09.2026, Edgar: „mit dem Playhead blättern … hat schon
 * mal funktioniert, warum wieder weg???") — `Zeitleistenfolge` deckte bisher
 * nur Abspielen, Fortschrittsbalken und Ziehen ab (`zeitleiste_ziehen.js`),
 * nicht die Sprungknöpfe (pb-start/-end/-prev/-next) und Pos1/Ende/Pfeiltasten,
 * die alle über diese Funktion laufen.
 */
export function springen(bild) {
    state.playheadFrame = Math.max(0, Math.round(bild) || 0);
    Zeitleistenfolge.nachziehen(state, Zeitleistenflaeche.breite - HEADER_WIDTH);
    applyPlayhead();
    fn.renderTimeline();
    updatePlaybackUI();
}

// Bestimmt den Licht-An/Aus-State am aktuellen Playhead für einen Track.
// Priorität:
//  1. Wenn track.muted=true → immer aus (User-Override via Aus-Button)
//  2. Letzter Keyframe vor/an Playhead mit .data.visible != null → dessen Wert
//  3. Default: an (!track.muted)
//
// Wie bei der Kamera: außerhalb der Keyframes wird auf den NÄCHSTLIEGENDEN
// geklemmt, nicht auf "aus" — sonst geht ein Licht, das an drei Stellen als
// "an" gespeichert wurde, überall SONST im Projekt aus (Edgar, 23.09.2026:
// "Lichter sind dauernd aus ... Events werden ignoriert"). `Schluesselpaar`
// liefert diese Klemmung schon (`vorher` ist vor dem ersten KF der erste,
// nach dem letzten der letzte) — dieselbe Stelle, die auch Kamera und
// Lichtwerte (Position/Farbe/Stärke) benutzen.
function _lightVisibleAtPlayhead(track) {
    if (track.muted) return false;
    const kfs = track.clips.filter(c => c.type === 'light_kf');
    // Ohne Keyframes: Licht im Default-Zustand (an wenn nicht muted).
    // Standard-Keyframes werden NICHT mehr automatisch angelegt — das Licht ist
    // einfach immer aktiv bis der User Keyframes für Animation hinzufügt.
    if (kfs.length === 0) return true;
    const sorted = [...kfs].sort((a, b) => {
        if (a.startFrame !== b.startFrame) return a.startFrame - b.startFrame;
        return (a.data?.trackPosition === 'upper' ? 0 : 1) - (b.data?.trackPosition === 'upper' ? 0 : 1);
    });
    const paar = Schluesselpaar.finden(sorted, state.playheadFrame);
    // `vorher` ist "der letzte Keyframe mit startFrame <= Bild" innerhalb der
    // Spanne, und der geklemmte Rand außerhalb — in beiden Fällen der
    // richtige An/Aus-Zustand für einen Schalter (kein Zwischenwert nötig).
    return !paar || paar.vorher.data?.visible !== false;
}

// Synchronisiert visible state für alle Lichter — wird JEDEN Frame vom
// Render-Loop aufgerufen, damit An/Aus auch ohne Play sofort wirkt.
// Respektiert track.muted UND per-keyframe .data.visible.
export function syncLightVisibility() {
    for (const track of state.project.tracks) {
        if (track.type !== 'light' || !track.light) continue;
        const visible = _lightVisibleAtPlayhead(track);
        track.light.visible = visible;
        // Helper-Group: Lichtkegel (coneVisible) + Helferlinien (lightVisible)
        // unabhängig voneinander steuerbar. Beide bleiben auch sichtbar wenn Licht aus
        // (damit User weiß wo das Licht steht).
        const lh = track.lightHelper;
        if (lh) {
            lh.visible = true;  // Group immer an, Kinder-Visibility entscheidet
            if (lh.spotHelper) lh.spotHelper.visible = !!track.lightVisible;
            if (lh.originCone) lh.originCone.visible = track.coneVisible !== false;
        }
    }
}

export function applyPlayhead() {
    const t = state.playheadFrame / state.project.fps;

    syncLightVisibility();

    _schedulePreloads(t);

    // Bestimme strukturell (nicht per aktivem Clip!), welche BVH-Tracks einen
    // Model-Track verlinkt haben. Nur dort übergibt Model-Track die Visibility.
    for (const track of state.project.tracks) {
        if (track.type === 'bvh') track._modelControlled = false;
    }
    for (const track of state.project.tracks) {
        if (track.type === 'model') {
            const linked = state.project.getLinkedAnimation(track);
            if (linked) linked._modelControlled = true;
        }
    }

    let cameraApplied = false;
    for (const track of state.project.tracks) {
        if (track.muted) continue;
        if (track.type === 'bvh') applyBvhTrack(track, t);
        else if (track.type === 'model') applyModelTrack(track, t);
        else if (track.type === 'camera') {
            // Only the first active camera track drives the camera; later ones
            // would overwrite and make playback look chaotic.
            if (!cameraApplied && track.cameraActive && track.clips?.length) {
                applyCameraTrack(track, t);
                cameraApplied = true;
            }
        }
        else if (track.type === 'light') applyLightTrack(track, t);
        else if (track.type === 'audio') applyAudioTrack(track, t);
        else if (track.type === 'scene_object') applySceneObjectTrack(track, t);
    }
    // Gelenkkorrekturen (18.09.2026 abends): Daz' JCMs der Genesis-9-Figuren
    // aus den Knochenwinkeln dieses Bildes — nach den Bewegungsspuren.
    Genesis9gelenke.alle(state.project.tracks.map(s => s.modell).filter(Boolean));
    // Die Mimik NACH allen Bewegungsspuren: sie überschreibt die Gesichtsknochen,
    // die der Mischer der Körperanimation gerade gesetzt hat (14.09.2026).
    Mimikanwendung.alle(t);
    // Globale Sichtbarkeits-Schalter als letzter Schritt (siehe
    // `globale_sichtbarkeit.js`) — sonst überschreibt die Spur-Anwendung
    // hier drüber ein zuvor ausgeschaltetes Licht/Modell wieder.
    globaleSichtbarkeit.anwenden();
}

export function updatePlaybackUI() {
    const t = state.playheadFrame / state.project.fps;
    const el = document.getElementById('pb-time');
    if (el) el.textContent = formatTime(t);
    const fr = document.getElementById('pb-frame');
    if (fr) fr.textContent = `F: ${state.playheadFrame}`;
    const dur = document.getElementById('pb-duration');
    if (dur) dur.textContent = formatTime(state.project.duration);
}

export function formatTime(s) {
    const m = Math.floor(s / 60);
    const sec = (s % 60).toFixed(2);
    return `${m.toString().padStart(2, '0')}:${sec.padStart(5, '0')}`;
}

// Register functions in registry
fn.applyPlayhead = applyPlayhead;
fn.updatePlaybackUI = updatePlaybackUI;
fn.stopAudioTrack = stopAudioTrack;
// FEHLER bis 16.08.2026: Nicht angemeldet, aber in eigenschaften/licht.js als
// `fn.syncLightVisibility?.()` gerufen — nach einem Wechsel der Lichtart wurde
// die Sichtbarkeit still NICHT nachgezogen (ein stummgeschaltetes Licht konnte
// wieder leuchten). Das `?.` verschluckte den fehlenden Namen.
// Gefunden mit Docu/umbau/registrierungspruefung.py.
fn.syncLightVisibility = syncLightVisibility;
