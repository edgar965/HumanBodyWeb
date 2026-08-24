/**
 * Projektdatei — Studioprojekte auf dem Server speichern, laden, zuruecksetzen.
 *
 * WARUM diese Datei jetzt klein ist (Umbau 16.08.2026): Sie hatte 904 Zeilen und
 * enthielt fuenf verschiedene Aufgaben — Dateioperationen, das Uebersetzen des
 * Zustands in JSON, das Wiedereinlesen, den Sitzungsspeicher und ein komplettes
 * Vorschaufenster mit eigener Three.js-Szene. Jede davon hat jetzt ihr Modul:
 *
 *   projekt_daten.js              Zustand → speicherbare Struktur
 *   projekt_wiederherstellung.js  Struktur → Zustand
 *   projekt_nachladen.js          3D-Objekte und Ton vom Server nachholen
 *   sitzung.js                    sessionStorage
 *   vorschau.js / vorschau_fenster.js   Vorschaufenster (Taste A)
 *   studioanzeige.js              Namensfeld oben rechts
 */
import { state, SESSION_KEY } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { undoStack, redoStack } from './undo.js';
import { Studioanzeige } from './studioanzeige.js';
import { Projektdaten } from './projekt_daten.js';
import { Projektwiederherstellung } from './projekt_wiederherstellung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/** localStorage-Schluessel des zuletzt benutzten Projektpfads. */
const LETZTES = 'bvhStudio_lastProject';

export class Projektdatei {
    /** In den eingestellten Projektordner schreiben. */
    static async speichern() {
        const ordner = state.project.projectPath;
        if (!ordner) { Projektdatei.speichernUnter(); return; }
        const dateiname = (state.project.name || 'project')
            .replace(/[^a-zA-Z0-9_\-]/g, '_') + '.studio.json';
        const trenner = ordner.includes('\\') ? '\\' : '/';
        const pfad = ordner.replace(/[/\\]$/, '') + trenner + dateiname;
        try {
            const ergebnis = await Serverabruf.senden(
                '/api/studio/project-save/',
                { path: pfad, project: Projektdaten.sammeln() });
            if (!ergebnis.ok) {
                alert('Speichern fehlgeschlagen: '
                      + (ergebnis.error || 'Unbekannter Fehler'));
                return;
            }
            state.project._lastSavePath = ergebnis.path;
            Projektdatei._merken(ergebnis.path);
            Protokoll.info('BVH Studio', `Project saved: ${ergebnis.path}`);
            Studioanzeige.melden(`Gespeichert: ${dateiname}`);
        } catch (e) {
            alert('Speichern fehlgeschlagen: ' + e.message);
        }
    }

    static async speichernUnter() {
        const ordner = state.project.projectPath || '';
        const name = prompt(`Projektname speichern unter:\n`
                            + `(Ordner: ${ordner || 'nicht konfiguriert'})`,
                            state.project.name || 'project');
        if (!name) return;
        state.project.name = name;
        await Projektdatei.speichern();
    }

    /** Projekt aus dem eingestellten Ordner waehlen; sonst Dateiauswahl. */
    static async laden() {
        if (state.project.projectPath
            && await Projektdatei._ausOrdner(state.project.projectPath)) return;
        Projektdatei._dateiauswahl();
    }

    static async _ausOrdner(ordner) {
        try {
            const ergebnis = await Serverabruf.json(
                '/api/studio/project-list/?dir=' + encodeURIComponent(ordner));
            if (!ergebnis.files?.length) {
                alert(`Keine Projekte in ${ordner} gefunden.\nDatei manuell wählen...`);
                return false;
            }
            const namen = ergebnis.files.map(f => f.name);
            const liste = namen.map((n, i) => `${i + 1}. ${n}`).join('\n');
            const wahl = prompt(`Projekte in ${ordner}:\n\n${liste}\n\nNummer eingeben:`, '1');
            if (!wahl) return true;                       // abgebrochen, nicht ausweichen
            const idx = parseInt(wahl) - 1;
            if (idx < 0 || idx >= ergebnis.files.length) {
                alert('Ungueltige Auswahl.');
                return true;
            }
            return await Projektdatei._vomServer(ergebnis.files[idx].path,
                                                 ergebnis.files[idx].name);
        } catch (e) {
            return false;                                 // → Dateiauswahl
        }
    }

    static async _vomServer(pfad, anzeigename) {
        const ergebnis = await Serverabruf.json(
            '/api/studio/project-load/?path=' + encodeURIComponent(pfad));
        if (!ergebnis.ok) {
            alert('Laden fehlgeschlagen: ' + (ergebnis.error || ''));
            return true;
        }
        await Projektwiederherstellung.uebernehmen(ergebnis.project);
        state.project._lastSavePath = ergebnis.path;
        Projektdatei._merken(ergebnis.path);
        Studioanzeige.melden(`Geladen: ${anzeigename}`);
        Studioanzeige.aktualisieren();
        return true;
    }

    static _dateiauswahl() {
        const eingabe = document.createElement('input');
        eingabe.type = 'file';
        eingabe.accept = '.json,.studio.json';
        eingabe.addEventListener('change', async () => {
            const datei = eingabe.files[0];
            if (!datei) return;
            try {
                await Projektwiederherstellung.uebernehmen(JSON.parse(await datei.text()));
            } catch (e) {
                alert('Projekt laden fehlgeschlagen: ' + e.message);
            }
        });
        eingabe.click();
    }

    static async zuletztBenutztes() {
        let pfad = '';
        try {
            pfad = localStorage.getItem(LETZTES) || '';
        } catch (e) {
            Protokoll.debug('projekt', 'letztes Projekt nicht lesbar (Speicher gesperrt)', e);
        }
        if (!pfad) { alert('Kein letztes Projekt gespeichert.'); return; }
        try {
            const name = pfad.split(/[/\\]/).pop().replace('.studio.json', '');
            await Projektdatei._vomServer(pfad, name);
            Protokoll.debug('BVH Studio', `Last project loaded: ${pfad}`);
        } catch (e) {
            alert('Laden fehlgeschlagen: ' + e.message);
        }
    }

    /** Alles leeren: Spuren, Sitzung, Rueckgaengig-Stapel. */
    static zuruecksetzen() {
        state._undoSuppressed = true;
        while (state.project.tracks.length > 0) fn.removeTrack(0);
        state._undoSuppressed = false;

        state.project.name = 'Untitled';
        state.selectedTrackIdx = -1;
        state.selectedClipIdx = -1;
        state.playheadFrame = 0;
        state.playing = false;
        undoStack.length = 0;
        redoStack.length = 0;
        sessionStorage.removeItem(SESSION_KEY);

        fn.updateDuration();
        fn.renderTimeline();
        fn.updateTrackHeaders();
        fn.updatePlaybackUI();
        fn.updateProperties();
        Studioanzeige.aktualisieren();
        fn.serverLog('reset_to_default');
    }

    static _merken(pfad) {
        try {
            localStorage.setItem(LETZTES, pfad);
        } catch (e) {
            Protokoll.debug('projekt', 'letztes Projekt nicht merkbar (Speicher gesperrt)', e);
        }
    }
}

fn.saveProject = Projektdatei.speichern;
fn.saveProjectAs = Projektdatei.speichernUnter;
fn.loadProject = Projektdatei.laden;
fn.loadLastProject = Projektdatei.zuletztBenutztes;
fn.resetToDefault = Projektdatei.zuruecksetzen;
