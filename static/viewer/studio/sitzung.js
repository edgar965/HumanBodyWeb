/**
 * Sitzung — Studiozustand im sessionStorage sichern und beim Neuladen zurueckholen.
 *
 * Aus project.js herausgeloest (Umbau 16.08.2026).
 */
import { state, SESSION_KEY } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Projektdaten } from './projekt_daten.js';
import { Projektwiederherstellung } from './projekt_wiederherstellung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Sitzung {
    static sichern() {
        try {
            if (state.project.tracks.length === 0) {
                sessionStorage.removeItem(SESSION_KEY);
                return;
            }
            sessionStorage.setItem(SESSION_KEY, JSON.stringify({
                project: Projektdaten.sammeln(),
                playheadFrame: state.playheadFrame,
                selectedTrackIdx: state.selectedTrackIdx,
                selectedClipIdx: state.selectedClipIdx,
                timelineZoom: state.timelineZoom,
                timelineScrollX: state.timelineScrollX,
            }));
        } catch (e) { Protokoll.debug('sitzung', 'Sitzung nicht speicherbar', e); }
    }

    /** true, wenn eine Sitzung zurueckgespielt wurde. */
    static async wiederherstellen() {
        try {
            const roh = sessionStorage.getItem(SESSION_KEY);
            if (!roh) return false;
            const sitzung = JSON.parse(roh);
            if (!sitzung.project?.tracks?.length) return false;
            if (await Sitzung._vorrangDefaultprojekt(sitzung)) return false;

            // Nur BVH-Spuren zurueckholen, die tatsaechlich Clips haben.
            const gueltig = sitzung.project.tracks
                .filter(t => t.type !== 'bvh' || t.clips?.length > 0);
            if (gueltig.length === 0) {
                sessionStorage.removeItem(SESSION_KEY);
                return false;
            }
            sitzung.project.tracks = gueltig;
            await Projektwiederherstellung.uebernehmen(sitzung.project);

            Sitzung._kaputteSpurenEntfernen();
            if (state.project.tracks.length === 0) {
                sessionStorage.removeItem(SESSION_KEY);
                return false;
            }
            Sitzung._bedienzustandUebernehmen(sitzung);
            Protokoll.debug('BVH Studio', `Session restored: ${state.project.tracks.length} tracks`);
            return true;
        } catch (e) {
            Protokoll.warnung('BVH Studio', 'Session restore failed, clearing:', e);
            sessionStorage.removeItem(SESSION_KEY);
            Sitzung._halbGeladenesAufraeumen();
            return false;
        }
    }

    /**
     * Vorrang Default-Projekt vor Sitzung.
     *
     * Ist ein Default-Projekt eingestellt UND hat es denselben Namen wie die
     * Sitzung, wird lieber frisch aus der Datei geladen — sonst baut die Sitzung
     * alte Zustaende wieder auf (geloeschte Voreinstellungen, kaputte
     * `_linkedAnimIdx`, stumme Spuren, fehlende Netze nach API-Fehlern).
     * Zurueckgespielt wird nur, wenn der User ein ANDERES Projekt gebaut hat —
     * dann ist die Sitzung die einzige Quelle.
     *
     * Gibt true zurueck, wenn der Aufrufer die Sitzung verwerfen soll.
     */
    static async _vorrangDefaultprojekt(sitzung) {
        try {
            const prefs = await Serverabruf.json('/api/ui-prefs/');
            const vorgabe = prefs.studio_default_project;
            const name = sitzung.project.name || '';
            if (!vorgabe || !name || vorgabe !== name) return false;
            Protokoll.debug('BVH Studio', `Session passt zum Default-Projekt "${vorgabe}" `
                        + '→ frisch aus Datei laden (Session verworfen, UI-State behalten).');
            // Die Spurdaten entfernen, damit der Default-Ladeweg in index.js greift
            // (der prueft tracks.length === 0). Den Bedienzustand (Abspielkopf, Zoom,
            // Auswahl) separat weiterreichen, damit er nach dem Laden angewandt wird.
            sessionStorage.removeItem(SESSION_KEY);
            sessionStorage.setItem(SESSION_KEY + '__ui', JSON.stringify({
                playheadFrame: sitzung.playheadFrame,
                timelineZoom: sitzung.timelineZoom,
                timelineScrollX: sitzung.timelineScrollX,
                selectedTrackIdx: sitzung.selectedTrackIdx,
                selectedClipIdx: sitzung.selectedClipIdx,
            }));
            return true;
        } catch (e) {
            Protokoll.warnung('BVH Studio', 'UI-Prefs-Fetch fehlgeschlagen, '
                         + 'fahre mit Session-Restore fort:', e);
            return false;
        }
    }

    /** Spuren wegwerfen, die nach dem Laden ohne Inhalt dastehen. */
    static _kaputteSpurenEntfernen() {
        const kaputt = [];
        for (let i = state.project.tracks.length - 1; i >= 0; i--) {
            const t = state.project.tracks[i];
            if (t.type === 'bvh' && t.clips.length === 0 && !t.mesh) kaputt.push(i);
            // Eigenes 3D-Objekt mit toter URL (Upload nicht mehr da) → Netz fehlt
            if (t.type === 'scene_object' && t.subtype === 'custom' && !t.mesh) kaputt.push(i);
        }
        if (kaputt.length === 0) return;
        state._undoSuppressed = true;
        for (const idx of kaputt) fn.removeTrack(idx);
        state._undoSuppressed = false;
        Protokoll.warnung('BVH Studio', `Removed ${kaputt.length} broken tracks from session`);
    }

    static _bedienzustandUebernehmen(sitzung) {
        state.playheadFrame = sitzung.playheadFrame || 0;
        state.selectedTrackIdx = sitzung.selectedTrackIdx ?? -1;
        state.selectedClipIdx = sitzung.selectedClipIdx ?? -1;
        state.timelineZoom = sitzung.timelineZoom || 100;
        state.timelineScrollX = sitzung.timelineScrollX || 0;

        const schieber = document.getElementById('tl-zoom');
        if (schieber) schieber.value = state.timelineZoom;
        const beschriftung = document.getElementById('tl-zoom-label');
        if (beschriftung) beschriftung.textContent = `Zoom: ${state.timelineZoom}%`;

        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updatePlaybackUI();
        fn.updateProperties();
    }

    static _halbGeladenesAufraeumen() {
        state._undoSuppressed = true;
        while (state.project.tracks.length > 0) fn.removeTrack(0);
        state._undoSuppressed = false;
    }
}

fn.saveSessionState = Sitzung.sichern;
fn.restoreSessionState = Sitzung.wiederherstellen;
